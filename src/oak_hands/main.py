import argparse
import time

import depthai as dai
from depthai_nodes.node import FrameCropper, GatherData, ParsingNeuralNetwork

from oak_hands.annotator import HandAnnotator
from oak_hands.crop_configs import CropConfigBuilder

PALM_DETECTION_MODEL = "luxonis/mediapipe-palm-detection:192x192"
HAND_LANDMARKER_MODEL = "luxonis/mediapipe-hand-landmarker:224x224"
CAMERA_SIZE = (768, 768)
CROP_PADDING = 0.1
MIN_HAND_SCORE = 0.5
VISUALIZER_PORT = 8082
QUIT_KEY = ord("q")
RVC2_FPS = 8
DEFAULT_FPS = 30
KEEP_ALIVE_POLL_SECONDS = 0.1


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Detect hand landmarks on the camera")
    parser.add_argument(
        "--live-feed",
        action="store_true",
        help=f"Stream the video with the hand landmarks to http://localhost:{VISUALIZER_PORT}",
    )
    return parser.parse_args(argv)


def load_model(model: str, platform: str) -> dai.NNArchive:
    return dai.NNArchive(dai.getModelFromZoo(dai.NNModelDescription(model, platform=platform)))


def frame_type_for(platform: str) -> dai.ImgFrame.Type:
    return dai.ImgFrame.Type.BGR888p if platform == "RVC2" else dai.ImgFrame.Type.BGR888i


def fps_for(platform: str) -> int:
    """RVC2 cannot run two chained models at full rate."""
    return RVC2_FPS if platform == "RVC2" else DEFAULT_FPS


def resize_to_model_input(
    pipeline: dai.Pipeline, frames: dai.Node.Output, archive: dai.NNArchive, frame_type: dai.ImgFrame.Type
) -> dai.Node.Output:
    width, height = archive.getInputWidth(), archive.getInputHeight()
    resize = pipeline.create(dai.node.ImageManip)
    resize.setMaxOutputFrameSize(width * height * 3)
    resize.initialConfig.setOutputSize(width, height, mode=dai.ImageManipConfig.ResizeMode.STRETCH)
    resize.initialConfig.setFrameType(frame_type)
    frames.link(resize.inputImage)
    return resize.out


def encode_for_visualizer(
    pipeline: dai.Pipeline, frames: dai.Node.Output, fps: int
) -> dai.Node.Output:
    width, height = CAMERA_SIZE
    convert = pipeline.create(dai.node.ImageManip)
    convert.setMaxOutputFrameSize(width * height * 3)
    convert.initialConfig.setOutputSize(width, height)
    convert.initialConfig.setFrameType(dai.ImgFrame.Type.NV12)
    frames.link(convert.inputImage)

    encoder = pipeline.create(dai.node.VideoEncoder)
    encoder.setMaxOutputFrameSize(width * height * 3)
    encoder.setDefaultProfilePreset(fps, dai.VideoEncoderProperties.Profile.H264_MAIN)
    convert.out.link(encoder.input)
    return encoder.out


def build_hand_pipeline(pipeline: dai.Pipeline, platform: str) -> tuple[dai.Node.Output, dai.Node.Output]:
    """Palm detection -> crop each palm -> hand landmarks. Returns (raw video, annotations)."""
    frame_type = frame_type_for(platform)
    fps = fps_for(platform)
    palm_archive = load_model(PALM_DETECTION_MODEL, platform)
    landmarker_archive = load_model(HAND_LANDMARKER_MODEL, platform)

    camera = pipeline.create(dai.node.Camera).build()
    video = camera.requestOutput(CAMERA_SIZE, frame_type, fps=fps)

    palm_detector = pipeline.create(ParsingNeuralNetwork).build(
        resize_to_model_input(pipeline, video, palm_archive, frame_type), palm_archive
    )

    crop_size = (landmarker_archive.getInputWidth(), landmarker_archive.getInputHeight())
    crop_configs = pipeline.create(CropConfigBuilder).build(palm_detector.out, CROP_PADDING, crop_size)
    hand_crops = (
        pipeline.create(FrameCropper)
        .fromManipConfigs(
            inputManipConfigs=crop_configs.config_output,
            maxOutputFrameSize=crop_size[0] * crop_size[1] * 3,
            waitForConfig=True,
        )
        .build(palm_detector.passthrough)
    )
    landmarker = pipeline.create(ParsingNeuralNetwork).build(hand_crops.out, landmarker_archive)

    # Pairs each palm with the landmarks computed from its crop.
    hands = pipeline.create(GatherData).build(
        cameraFps=fps, inputData=landmarker.outputs, inputReference=palm_detector.out
    )
    skeleton_edges = landmarker_archive.getConfig().model.heads[0].metadata.extraParams["skeleton_edges"]
    annotator = pipeline.create(HandAnnotator).build(hands.out, CROP_PADDING, MIN_HAND_SCORE, skeleton_edges)
    return video, annotator.annotations_output


def attach_live_feed(
    pipeline: dai.Pipeline, platform: str, video: dai.Node.Output, annotations: dai.Node.Output
) -> dai.RemoteConnection:
    """Only called with --live-feed: nothing is encoded or streamed to the host otherwise."""
    visualizer = dai.RemoteConnection(httpPort=VISUALIZER_PORT)
    visualizer.addTopic("Video", encode_for_visualizer(pipeline, video, fps_for(platform)), "images")
    visualizer.addTopic("Hands", annotations, "images")
    return visualizer


def wait_until_stopped(pipeline: dai.Pipeline, visualizer: dai.RemoteConnection | None) -> None:
    try:
        while pipeline.isRunning():
            if visualizer is not None and visualizer.waitKey(1) == QUIT_KEY:
                break
            if visualizer is None:
                time.sleep(KEEP_ALIVE_POLL_SECONDS)
    except KeyboardInterrupt:
        print("Stopping hand landmarker.")


def main() -> None:
    live_feed = parse_arguments().live_feed
    with dai.Device() as device, dai.Pipeline(device) as pipeline:
        platform = device.getPlatform().name
        print(f"Platform: {platform}")
        video, annotations = build_hand_pipeline(pipeline, platform)
        visualizer = attach_live_feed(pipeline, platform, video, annotations) if live_feed else None

        pipeline.start()
        if visualizer is None:
            print("Hand landmarker is running on the camera without a live feed (use --live-feed to see it). Press Ctrl+C to stop.")
        else:
            visualizer.registerPipeline(pipeline)
            print(f"Open http://localhost:{VISUALIZER_PORT} to see the feed. Press '{chr(QUIT_KEY)}' there or Ctrl+C to stop.")
        wait_until_stopped(pipeline, visualizer)


if __name__ == "__main__":
    main()

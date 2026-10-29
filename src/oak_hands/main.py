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
    """Palm detection -> crop each palm -> hand landmarks. Returns (video, annotations)."""
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
    return encode_for_visualizer(pipeline, video, fps), annotator.out


def main() -> None:
    visualizer = dai.RemoteConnection(httpPort=VISUALIZER_PORT)
    with dai.Device() as device, dai.Pipeline(device) as pipeline:
        platform = device.getPlatform().name
        print(f"Platform: {platform}")
        video, annotations = build_hand_pipeline(pipeline, platform)
        visualizer.addTopic("Video", video, "images")
        visualizer.addTopic("Hands", annotations, "images")

        pipeline.start()
        visualizer.registerPipeline(pipeline)
        print(f"Open http://localhost:{VISUALIZER_PORT} to see the feed. Press '{chr(QUIT_KEY)}' there or Ctrl+C to stop.")
        try:
            while pipeline.isRunning():
                if visualizer.waitKey(1) == QUIT_KEY:
                    break
        except KeyboardInterrupt:
            print("Stopping hand landmarker.")


if __name__ == "__main__":
    main()

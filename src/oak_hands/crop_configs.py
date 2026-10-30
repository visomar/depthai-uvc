import depthai as dai

from oak_hands.landmarks import padded_size


class CropConfigBuilder(dai.node.HostNode):
    """Turns each palm detection into an ImageManip crop config for the landmarker stage.

    The configs of one detections message are sent together as a MessageGroup.
    """

    def __init__(self) -> None:
        super().__init__()
        self.detections_input = self.createInput()
        self.config_output = self.createOutput()
        self._padding = 0.0
        self._crop_size = (0, 0)

    def build(
        self,
        detections: dai.Node.Output,
        padding: float,
        crop_size: tuple[int, int],
    ) -> "CropConfigBuilder":
        self._padding = padding
        self._crop_size = crop_size
        self.link_args(detections)
        return self

    def process(self, img_detections: dai.Buffer) -> None:
        assert isinstance(img_detections, dai.ImgDetections)
        configs = dai.MessageGroup()
        for index, detection in enumerate(img_detections.detections):
            configs[f"cfg_{index}"] = self._build_crop_config(detection, img_detections)
        configs.setTimestamp(img_detections.getTimestamp())
        configs.setSequenceNum(img_detections.getSequenceNum())
        self.config_output.send(configs)

    def _build_crop_config(
        self, detection: dai.ImgDetection, source: dai.ImgDetections
    ) -> dai.ImageManipConfig:
        box = detection.getBoundingBox()
        width, height = padded_size((box.size.width, box.size.height), self._padding)
        crop = dai.RotatedRect()
        crop.center.x = box.center.x
        crop.center.y = box.center.y
        crop.size.width = width
        crop.size.height = height
        crop.angle = 0

        config = dai.ImageManipConfig()
        config.addCropRotatedRect(crop, normalizedCoords=True)
        config.setOutputSize(*self._crop_size, dai.ImageManipConfig.ResizeMode.STRETCH)
        config.setReusePreviousImage(False)
        config.setTimestamp(source.getTimestamp())
        config.setSequenceNum(source.getSequenceNum())
        return config

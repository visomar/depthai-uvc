import depthai as dai
from depthai_nodes import SECONDARY_COLOR, GatheredData
from depthai_nodes.utils import AnnotationHelper

from oak_hands.gestures import recognize_gesture
from oak_hands.landmarks import crop_to_image_coordinates, hand_label, handedness_label, padded_size

KEYPOINTS_HEAD = "0"
SCORE_HEAD = "1"
HANDEDNESS_HEAD = "2"
LABEL_TEXT_SIZE = 32
LABEL_OFFSET_ABOVE_BOX = 0.1
LABEL_OFFSET_LEFT = 0.05


class HandAnnotator(dai.node.HostNode):
    """Draws the skeleton and handedness of every detected hand as image annotations."""

    def __init__(self) -> None:
        super().__init__()
        self.gathered_data = self.createInput()
        self.annotations_output = self.createOutput(
            possibleDatatypes=[dai.Node.DatatypeHierarchy(dai.DatatypeEnum.ImgAnnotations, True)]
        )
        self._padding = 0.0
        self._min_score = 0.0
        self._skeleton_edges: list[list[int]] = []

    def build(
        self,
        gathered_data: dai.Node.Output,
        padding: float,
        min_score: float,
        skeleton_edges: list[list[int]],
    ) -> "HandAnnotator":
        self._padding = padding
        self._min_score = min_score
        self._skeleton_edges = skeleton_edges
        self.link_args(gathered_data)
        return self

    def process(self, gathered_data: dai.Buffer) -> None:
        assert isinstance(gathered_data, GatheredData)
        detections: dai.ImgDetections = gathered_data.reference_data
        annotations = AnnotationHelper()
        for index, detection in enumerate(detections.detections):
            hand_results = gathered_data.items[index]
            if hand_results[SCORE_HEAD].getFirstPrediction() >= self._min_score:
                self._annotate_hand(annotations, detection, hand_results)
        self.annotations_output.send(
            annotations.build(
                timestamp=detections.getTimestamp(),
                sequence_num=detections.getSequenceNum(),
            )
        )

    def _annotate_hand(
        self, annotations: AnnotationHelper, detection: dai.ImgDetection, hand_results: dict
    ) -> None:
        box = detection.getBoundingBox()
        center = (box.center.x, box.center.y)
        crop_size = padded_size((box.size.width, box.size.height), self._padding)
        crop_points = [
            (keypoint.imageCoordinates.x, keypoint.imageCoordinates.y)
            for keypoint in hand_results[KEYPOINTS_HEAD].getKeypoints()
        ]
        points = crop_to_image_coordinates(crop_points, center, crop_size)

        for start, end in self._skeleton_edges:
            annotations.draw_line(pt1=points[start], pt2=points[end])
        annotations.draw_points(points=[list(point) for point in points], color=SECONDARY_COLOR, thickness=2)

        handedness = handedness_label(hand_results[HANDEDNESS_HEAD].getFirstPrediction())
        gesture = recognize_gesture(points)
        label = hand_label(handedness, gesture.name if gesture else None)
        annotations.draw_text(
            text=label,
            position=(center[0] - LABEL_OFFSET_LEFT, center[1] - box.size.height / 2 - LABEL_OFFSET_ABOVE_BOX),
            color=SECONDARY_COLOR,
            size=LABEL_TEXT_SIZE,
        )

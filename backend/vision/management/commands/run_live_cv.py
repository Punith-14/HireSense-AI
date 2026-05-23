import cv2
from django.core.management.base import BaseCommand, CommandError

from vision.services import VisionFrameProcessor


class Command(BaseCommand):
    help = "Run local webcam emotion and attention processing for VS Code demos."

    def add_arguments(self, parser):
        parser.add_argument("--camera", type=int, default=0)
        parser.add_argument("--width", type=int, default=960)
        parser.add_argument("--height", type=int, default=540)

    def handle(self, *args, **options):
        capture = cv2.VideoCapture(options["camera"])
        if not capture.isOpened():
            raise CommandError("Webcam unavailable. Check camera permissions and device index.")

        capture.set(cv2.CAP_PROP_FRAME_WIDTH, options["width"])
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, options["height"])
        processor = VisionFrameProcessor()
        self.stdout.write("Live CV started. Press q in the preview window to stop.")

        try:
            while True:
                ok, frame = capture.read()
                if not ok:
                    raise CommandError("Failed to read frame from webcam.")

                result = processor.process_frame(frame)
                annotated = processor.annotate_frame(frame, result)
                cv2.imshow("HireSenseAI Live CV", annotated)

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        finally:
            capture.release()
            cv2.destroyAllWindows()

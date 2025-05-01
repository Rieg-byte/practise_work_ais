from ultralytics import YOLO
import cv2


class SheepDetector:
    def __init__(self):
        self.model = YOLO('yolo11n.pt')
        self.class_name = "sheep"  # Имя класса

    '''
    Детектирование на изображении
    '''
    def detect_on_image(self, image):
        results = self.model.predict(source=image, conf=0.25)
        result_img = results[0].plot()
        sheep_count = sum(1 for box in results[0].boxes if self.model.names[int(box.cls)] == self.class_name)
        return result_img, sheep_count

    '''
        Детектирование на видео
    '''
    def detect_on_video(self, input_video, output_video):
        cap = cv2.VideoCapture(input_video)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        out = cv2.VideoWriter(
            output_video,
            fourcc,
            fps,
            (width, height)
        )

        count = 0

        while True:
            success, frame = cap.read()

            if not success:
                break

            results = self.model.predict(frame)
            annotated_frame = results[0].plot()
            out.write(annotated_frame)
            current = len(results[0].boxes)
            count = max(count, current)

        cap.release()
        out.release()

        return count

    '''
        Детектирование в реальном времени
    '''
    def detect_on_camera(self, frame):
        results = self.model(frame)

        return [
            {
                'x_min': box.xyxyn[0][0].item(),
                'y_min': box.xyxyn[0][1].item(),
                'x_max': box.xyxyn[0][2].item(),
                'y_max': box.xyxyn[0][3].item(),
                'confidence': box.conf.item() * 100
            }
            for box in results[0].boxes if self.model.names[int(box.cls)] == self.class_name
        ]

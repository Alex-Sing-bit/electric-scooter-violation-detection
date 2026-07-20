import os

import cv2

from utils.bbox_utils import detect_scooters
from visualisation.visualizer import ResultVisualizer, visualize_violation, visualize_warning, print_violations


class ViolationProcessor:
    def __init__(self, models_engine, minio_client):
        self.engine = models_engine
        self.minio = minio_client

        self.VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        self.IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}

    def process(self, violation_id, object_name, file_extension):
        local_path = f"tmp_{violation_id}{file_extension}"
        self.minio.fget_object("scooter-violations", object_name, local_path)

        print(f"Downloaded file: {object_name} (extension: {file_extension})")

        fps, duration = 0, 0
        if file_extension in self.VIDEO_EXTENSIONS:
            print("Processing as video...")
            fps, duration, results = self._process_video(local_path, violation_id)
        elif file_extension in self.IMAGE_EXTENSIONS:
            print("Processing as image...")
            fps, duration, results = self._process_image(local_path, violation_id)
        else:
            raise Exception(f"Unsupported file format: {file_extension}")

        for r in results:
            result_path = r['minio_path']
            local_output = result_path.split("/")[-1]
            self.minio.fput_object("scooter-violations", result_path, local_output)

        os.remove(local_path)
        return fps, duration, results

    def _process_image(self, local_path, violation_id):
        image = cv2.imread(local_path)
        if image is None:
            return None

        # 1. Детекция
        result = self.engine.detector.detect(image)
        scooters = detect_scooters(result["detections"])

        if not scooters:
            return []

        print(f"Detected {len(scooters) if scooters is not None else '-'} scooters")

        # 2. Сегментация поверхности
        scooters, _ = self.engine.segmenter.categorize_escooter_surface(image, scooters)

        # 3. Предсказание поз
        self.engine.predictor.scooters = scooters
        predictions = self.engine.predictor.predict_image(image)

        print(f"Predicting {len(predictions) if predictions is not None else '-'} predictions")

        # 4. Анализ нарушений
        self.engine.analyzer.analyze(predictions, scooters)

        # 5. Сбор результатов
        found_violations = []
        if predictions:
            for p in predictions:
                if p.get('violations'):
                    found_violations.extend(p['violations'])
                    image = visualize_violation(image, p)

        for s in scooters:
            if s.get('warning'):
                found_violations.extend(s['warning'])
                image = visualize_warning(image, s)

        visualizer = ResultVisualizer()
        image = print_violations(image, found_violations)
        image = visualizer.visualize_predictions(image, predictions)

        output_filename = f"result_{violation_id}.jpg"

        cv2.imwrite(output_filename, image)

        result = [{
            "timestamp": 0,
            "duration": 0,
            "frame": 0,
            "violations": list(set(found_violations)),
            "minio_path": f"processed/{violation_id}/{output_filename}"
        }]
        print(result)

        return 0, 0, result

    def _process_video(self, local_path, violation_id):
        print(f"Attempting to open video file: {local_path}")
        print(f"File exists: {os.path.exists(local_path)}")
        print(f"File size: {os.path.getsize(local_path) if os.path.exists(local_path) else 'N/A'} bytes")

        cap = cv2.VideoCapture(local_path)
        fps_count = cap.get(cv2.CAP_PROP_FPS)
        analyze_speed = int(fps_count / 3)
        seg_speed = int(fps_count)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration_seconds = total_frames / fps_count

        frame_id = 0
        results = []

        seg_results = [None]

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break

            if frame_id % analyze_speed == 0:
                result = self.engine.detector.track(frame)
                scooters = detect_scooters(result["detections"])

                if scooters:
                    scooters, seg_results[0] = (self.engine.segmenter.categorize_escooter_surface(
                            frame,
                            scooters,
                            None if frame_id % seg_speed == 0 else seg_results[0]
                        )
                    )

                    self.engine.predictor.scooters = scooters

                    predictions = self.engine.predictor.predict_image(frame)

                    self.engine.analyzer.analyze(predictions, scooters)

                    current_frame_violations = []

                    if predictions:
                        for p in predictions:
                            if p.get('violations'):
                                current_frame_violations.extend(p['violations'])
                                frame = visualize_violation(frame, p)

                    for s in scooters:
                        if s.get('warning'):
                            current_frame_violations.extend(s['warning'])
                            frame = visualize_warning(frame, s)

                    if current_frame_violations:
                        found_violations = tuple(sorted(set(current_frame_violations)))
                        output_filename = f"violation_{violation_id}_f{frame_id}.jpg"

                        visualizer = ResultVisualizer()
                        annotated_frame = print_violations(frame, found_violations)
                        annotated_frame = visualizer.visualize_predictions(annotated_frame, predictions)

                        if hasattr(annotated_frame, 'close'):
                            annotated_frame.close()

                        res = {
                            "timestamp": int(frame_id / fps_count),
                            "duration": 0,
                            "frame": frame_id,
                            "violations": list(found_violations),
                            "minio_path": f"processed/{violation_id}/{output_filename}"
                        }
                        prev = [results[-1] if len(results) > 0 else None]
                        is_same_as_prev = False if prev[0] is None else \
                            (res["violations"] == prev[0]["violations"]
                             and res["frame"] - prev[0]["frame"] < 40)
                        if not is_same_as_prev:
                            results.append(res)
                            cv2.imwrite(output_filename, annotated_frame)
                            prev[0] = res
                        elif prev[0] is not None and is_same_as_prev:
                            prev[0]["duration"] = int(frame_id / fps_count) - prev[0]["timestamp"]
                            results[-1] = prev[0]

            frame_id += 1

        cap.release()

        print(results)
        return fps_count, duration_seconds, results
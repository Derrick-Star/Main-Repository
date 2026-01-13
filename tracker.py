import cv2
import mediapipe as mp
import numpy as np
import time

# Initialize MediaPipe Objectron for 3D object detection
mp_objectron = mp.solutions.objectron
mp_drawing = mp.solutions.drawing_utils

# Open camera
cap = cv2.VideoCapture(0)  # Change to video path if using a file

# Initialize Objectron for detecting a box-like object (e.g., shoe, book)
with mp_objectron.Objectron(static_image_mode=False,
                            max_num_objects=2,
                            min_detection_confidence=0.5,
                            min_tracking_confidence=0.5,
                            model_name='Shoe') as objectron:

    prev_time = time.time()
    prev_positions = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = objectron.process(frame_rgb)

        if results.detected_objects:
            for obj in results.detected_objects:
                # Draw 3D bounding box
                mp_drawing.draw_landmarks(frame, obj.landmarks_2d, mp_objectron.BOX_CONNECTIONS)
                
                # Get object dimensions in real-world units (approximation)
                keypoints = obj.landmarks_3d.landmark
                width = np.linalg.norm(np.array([keypoints[1].x, keypoints[1].y, keypoints[1].z]) -
                                       np.array([keypoints[0].x, keypoints[0].y, keypoints[0].z]))
                height = np.linalg.norm(np.array([keypoints[3].x, keypoints[3].y, keypoints[3].z]) -
                                        np.array([keypoints[0].x, keypoints[0].y, keypoints[0].z]))
                depth = np.linalg.norm(np.array([keypoints[4].x, keypoints[4].y, keypoints[4].z]) -
                                       np.array([keypoints[0].x, keypoints[0].y, keypoints[0].z]))

                # Scale dimensions (assume a reference object for proper scaling)
                scaling_factor = 100  # Adjust based on real-world calibration
                width *= scaling_factor
                height *= scaling_factor
                depth *= scaling_factor

                # Calculate speed (if object is being tracked)
                obj_id = hash(tuple(obj.landmarks_3d.landmark[0]))  # Generate a simple ID
                cur_time = time.time()

                if obj_id in prev_positions:
                    prev_pos, prev_t = prev_positions[obj_id]
                    distance_moved = np.linalg.norm(np.array([keypoints[0].x, keypoints[0].y, keypoints[0].z]) - np.array(prev_pos))
                    time_elapsed = cur_time - prev_t
                    speed = (distance_moved * scaling_factor) / time_elapsed  # Speed in units/sec
                else:
                    speed = 0  # First frame, no previous data

                prev_positions[obj_id] = ([keypoints[0].x, keypoints[0].y, keypoints[0].z], cur_time)

                # Display measurements
                cv2.putText(frame, f"Width: {width:.2f} cm", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f"Height: {height:.2f} cm", (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f"Depth: {depth:.2f} cm", (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                cv2.putText(frame, f"Speed: {speed:.2f} cm/s", (50, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

        cv2.imshow("Object Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
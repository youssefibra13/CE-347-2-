import cv2
import mediapipe as mp
import math
import time

cap = None

def pose_estimation():
    global cap
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils
    start_time = time.time()
    last_print_time = time.time()  # Track the last time the wrist position was printed

    while True:
        if cap is not None:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert the frame to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Perform pose estimation on the frame
            results = pose.process(frame_rgb)

            # Annotate the frame with pose estimation
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                          mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                          )
                
                right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
                right_wrist_position = (int(right_wrist.x * frame.shape[1]), int(right_wrist.y * frame.shape[0]))

                # Print the right wrist position every second
                current_time = time.time()
                if current_time - last_print_time >= 1:
                    print(f"Right Wrist Position: {right_wrist_position}")
                    last_print_time = current_time

                cv2.circle(frame, right_wrist_position, 5, (0, 255, 0), -1)

            # Display the annotated frame
            cv2.imshow('Pose Estimation', frame)

            # Break the loop if 'q' is pressed or 15 seconds have passed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if current_time - start_time > 15:
                break

    cap.release()
    cv2.destroyAllWindows()

def start_video():
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(1)  # Use 0 for the default camera

def stop_video():
    global cap
    if cap is not None:
        cap.release()
        cap = None

if __name__ == '__main__':
    start_video()
    pose_estimation()
    stop_video()
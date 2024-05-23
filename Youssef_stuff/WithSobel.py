import cv2
import mediapipe as mp
import numpy as np
import math
import time

cap = None
calculated_values = {}
height = 0

def apply_sobel(frame, mask):
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Apply Sobel operator to get the gradients
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)
    
    # Convert gradients to absolute values
    abs_sobelx = cv2.convertScaleAbs(sobelx)
    abs_sobely = cv2.convertScaleAbs(sobely)
    
    # Combine the gradients
    sobel_combined = cv2.addWeighted(abs_sobelx, 0.5, abs_sobely, 0.5, 0)
    
    # Apply the mask to the Sobel output
    sobel_masked = cv2.bitwise_and(sobel_combined, sobel_combined, mask=mask)
    
    return sobel_masked

def pose_estimation():
    global cap
    mp_pose = mp.solutions.pose
    mp_selfie_segmentation = mp.solutions.selfie_segmentation
    pose = mp_pose.Pose()
    segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
    mp_drawing = mp.solutions.drawing_utils
    start_time = time.time()

    while True:
        if cap is not None:
            ret, frame = cap.read()
            if not ret:
                break

            # Convert the frame to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Perform segmentation to create a mask
            segmentation_results = segmentation.process(frame_rgb)
            mask = segmentation_results.segmentation_mask
            condition = mask > 0.5
            mask = np.uint8(condition) * 255  # Convert to binary mask

            # Create a white background image
            white_background = np.ones_like(frame, dtype=np.uint8) * 255
            
            # Extract the segmented person
            person = cv2.bitwise_and(frame, frame, mask=mask)
            
            # Create the inverse mask
            inverse_mask = cv2.bitwise_not(mask)
            
            # Extract the background from the white background image using the inverse mask
            background = cv2.bitwise_and(white_background, white_background, mask=inverse_mask)
            
            # Combine the person and the white background
            frame_with_white_bg = cv2.add(person, background)

            # Perform pose estimation on the frame
            results = pose.process(frame_rgb)

            # Apply Sobel operator to the masked region
            sobel_frame = apply_sobel(frame_with_white_bg, mask)

            # Annotate the frame with pose estimation
            frame_with_white_bg = cv2.cvtColor(frame_with_white_bg, cv2.COLOR_RGB2BGR)
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                mp_drawing.draw_landmarks(frame_with_white_bg, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                          mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                          mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2)
                                          )
                def dist_bw_two_points(a, b, frame):
                    a_marks = landmarks[a]
                    b_marks = landmarks[b]

                    a_x, a_y = int(a_marks.x * frame.shape[1]), int(a_marks.y * frame.shape[0])
                    b_x, b_y = int(b_marks.x * frame.shape[1]), int(b_marks.y * frame.shape[0])

                    distance = math.sqrt((b_x - a_x) ** 2 + (b_y - a_y) ** 2)
                    cv2.circle(frame, (a_x, a_y), 5, (0, 255, 0), -1)
                    cv2.circle(frame, (b_x, b_y), 5, (0, 255, 0), -1)
                    
                    return distance

                # Relative Positioning of LEFT_WRIST AND RIGHT_WRIST
                fixed_distance = 80 / dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_WRIST, mp_pose.PoseLandmark.LEFT_WRIST, frame)

                # LEFT ARM LENGTH
                left_arm_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_WRIST, frame)
                
                # RIGHT ARM LENGTH
                right_arm_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_WRIST, frame)

                # LEFT LEG LENGTH
                #left_thigh_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE, frame)
                #left_knee_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.LEFT_FOOT_INDEX, mp_pose.PoseLandmark.LEFT_KNEE, frame)
                
                # RIGHT LEG LENGTH
                #right_thigh_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE, frame)
                #right_knee_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_FOOT_INDEX, mp_pose.PoseLandmark.RIGHT_KNEE, frame)
                
                # SHOULDER LENGTH
                shoulder_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.LEFT_SHOULDER, frame)
                chest_circumference = 3.14 * shoulder_length
                
                # WAIST CIRCUMFERENCE
                waist_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.LEFT_HIP, frame)
                waist_circumference = 3.14 * waist_length
                
                # HEIGHT
                height = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.NOSE, mp_pose.PoseLandmark.LEFT_HEEL,
                                                            frame) + 2 * fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.NOSE,
                                                                                                             mp_pose.PoseLandmark.LEFT_EYE_INNER, frame)
                # SITTING HEIGHT
                #sitting_height = height - (left_thigh_length + right_thigh_length) / 2
                
                # FOOT LENGTH
                #foot_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.LEFT_FOOT_INDEX, mp_pose.PoseLandmark.LEFT_HEEL, frame)

                calculated_values['fixed_distance'] = str(round(216, 2)) + " cm"
                calculated_values['height'] = str(round(height, 2)) + " cm"
                calculated_values['left_arm_length'] = str(round(left_arm_length, 2)) + " cm"
                #calculated_values['left_thigh_length'] = str.round(left_thigh_length, 2)) + " cm"
                #calculated_values['left_knee_length'] = str.round(left_knee_length, 2)) + " cm"
                calculated_values['right_arm_length'] = str(round(right_arm_length, 2)) + " cm"
                #calculated_values['right_thigh_length'] = str.round(right_thigh_length, 2)) + " cm"
                #calculated_values['right_knee_length'] = str.round(right_knee_length, 2)) + " cm"
                calculated_values['shoulder_length'] = str(round(shoulder_length, 2)) + " cm"
                calculated_values['chest_circumference'] = str(round(chest_circumference, 2)) + " cm"
                calculated_values['waist_length'] = str(round(waist_length, 2)) + " cm"
                calculated_values['waist_circumference'] = str(round(waist_circumference, 2)) + " cm"
                #calculated_values['sitting_height'] = str.round(sitting_height, 2)) + " cm"
                #calculated_values['foot_length'] = str.round(foot_length, 2)) + " cm"

            # Display the annotated frame and the Sobel frame
            cv2.imshow('Pose Estimation', frame_with_white_bg)
            cv2.imshow('Sobel Edge Detection', sobel_frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if time.time() - start_time > 15:
                break

    cap.release()
    cv2.destroyAllWindows()
    print(calculated_values)

def start_video():
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(1)

def stop_video():
    global cap
    if cap is not None:
        cap.release()
        cap = None
        print(calculated_values)

if __name__ == '__main__':
    start_video()
    pose_estimation()
    stop_video()

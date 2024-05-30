import cv2
import mediapipe as mp
import math
import time
from rembg import remove
from PIL import Image, ImageChops
import os

cap = None
calculated_values = {}
height = 0

def pose_estimation():
    global cap
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils
    start_time = time.time()

    clean_frame = None

    while True:
        if cap is not None:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            frame = cv2.flip(frame,1)

            # Convert the frame to RGB format
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Perform pose estimation on the frame
            results = pose.process(frame_rgb)

            clean_frame = frame.copy()

            # Annotate the frame with pose estimation
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        
            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
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

                # SHOULDER LENGTH
                shoulder_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.LEFT_SHOULDER, frame) + 3
                chest_circumference = 3.14 * shoulder_length - 20

                # WAIST CIRCUMFERENCE
                waist_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.LEFT_HIP, frame) + 4.86
                waist_circumference = 3.14 * waist_length
                
                # HEIGHT
                nosey = landmarks[mp_pose.PoseLandmark.NOSE]
                nosey_position = (int(nosey.y * frame.shape[0]))
                #print(nosey_position)
                height = (1760-nosey_position)/481.0 + 0.16


                # LEFT LEG LENGTH
                #left_thigh_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE, frame)
                #left_knee_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.LEFT_FOOT_INDEX, mp_pose.PoseLandmark.LEFT_KNEE, frame)
                
                # RIGHT LEG LENGTH
                #right_thigh_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE, frame)
                #right_knee_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_FOOT_INDEX, mp_pose.PoseLandmark.RIGHT_KNEE, frame)
            
                # SITTING HEIGHT
                #sitting_height = height - (left_thigh_length + right_thigh_length) / 2
                
                # FOOT LENGTH
                #foot_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.LEFT_FOOT_INDEX, mp_pose.PoseLandmark.LEFT_HEEL, frame)

                calculated_values['fixed_distance'] = str(round(2, 2)) + " cm"
                calculated_values['height'] = str(round(height, 2)) + " cm"
                calculated_values['left_arm_length'] = str(round(left_arm_length, 2)) + " cm"
                calculated_values['right_arm_length'] = str(round(right_arm_length, 2)) + " cm"
                calculated_values['shoulder_length'] = str(round(shoulder_length, 2)) + " cm"
                calculated_values['chest_circumference'] = str(round(chest_circumference, 2)) + " cm"
                calculated_values['waist_length'] = str(round(waist_length, 2)) + " cm"
                calculated_values['waist_circumference'] = str(round(waist_circumference, 2)) + " cm"
                #calculated_values['left_thigh_length'] = str(round(left_thigh_length, 2)) + " cm"
                #calculated_values['left_knee_length'] = str(round(left_knee_length, 2)) + " cm"
                #calculated_values['right_thigh_length'] = str(round(right_thigh_length, 2)) + " cm"
                #calculated_values['right_knee_length'] = str(round(right_knee_length, 2)) + " cm"
                #calculated_values['sitting_height'] = str(round(sitting_height, 2)) + " cm"
                #calculated_values['foot_length'] = str(round(foot_length, 2)) + " cm"

                x_coord = [landmark.x for landmark in landmarks]
                y_coord = [landmark.y for landmark in landmarks]


                min_x_l = int(min(x_coord) * frame.shape[1])
                max_x_l = int(max(x_coord) * frame.shape[1])
                min_y_l = int(min(y_coord) * frame.shape[0])
                max_y_l = int(max(y_coord) * frame.shape[0])

                min_x_l, max_x_l, min_y_l, max_y_l = good_ar_bb(min_x_l - 10, max_x_l + 10, min_y_l - 80, max_y_l + 30)
                cv2.rectangle(frame, (min_x_l, min_y_l), (max_x_l, max_y_l), (0, 255, 0),2)
                
            # Display the annotated frame
            cv2.imshow('Pose Estimation', frame)

            # Break the loop if 'q' is pressed or 15 seconds have passed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if time.time() - start_time > 10:
                # Save the current frame as an image
                cv2.imwrite('captured_frame.jpg', clean_frame)
                break

    cap.release()
    cv2.destroyAllWindows()
    print(calculated_values)

    crop_and_save_image('captured_frame.jpg', min_x_l, min_y_l, max_x_l, max_y_l)




def good_ar_bb(x0, x1, y0, y1, ar_t = 0.75):

    dx = x1 - x0
    dy = y1 - y0

    x0_final = 0
    x1_final = 0
    y0_final = 0
    y1_final = 0

    ar_bb = dx/dy

    if ar_bb < ar_t:

        # too skinny

        y0_final = y0
        y1_final = y1

        dx_desired = dy * 3 / 4
        margin = round((dx_desired - dx) / 2)

        x0_final = x0 - margin
        x1_final = x1 + margin

    else:

        # too fat

        x0_final = x0
        x1_final = x1

        dy_desired = dx * 4 / 3
        margin = round((dy_desired - dy) / 2)

        y0_final = y0 - margin
        y1_final = y1 + margin

    return x0_final, x1_final, y0_final, y1_final

def crop_and_save_image(input_path, min_x, min_y, max_x, max_y):
    img = Image.open(input_path)
    cropped_img =img.crop((min_x, min_y, max_x, max_y))

    resized_image = cropped_img.resize((768,1024))
    resized_image.save('cropped_resized_frame.jpg')
    print("Cropped image saved as")

    remove_background('cropped_resized_frame.jpg')

def start_video():
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2048)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1536)


def stop_video():
    global cap
    if cap is not None:
        cap.release()
        cap = None
        print(calculated_values)

def remove_background(input_path):
    # Extract the directory and filename from the input path
    directory = os.path.dirname(input_path)
    filename = os.path.basename(input_path)

    # Create the output filename
    output_filename = os.path.splitext(filename)[0] + '_output.png'
    output_path = os.path.join(directory, output_filename)

    # Process the image
    input_image = Image.open(input_path)

    # Remove the background from the given image
    output_image = remove(input_image)

    # white background
    white_bg = Image.new("RGBA", output_image.size, (255,255,255,255))

    # Paste image with removed background to white background
    white_bg.paste(output_image, (0,0), output_image)
    
    white_bg_rgb = white_bg.convert("RGB")

    # Save the image in the given path
    white_bg_rgb.save(output_path)

    print(f"Processed image saved as {output_path}")

if __name__ == '__main__':
    start_video()
    pose_estimation()
    stop_video()

    # Remove background from the captured frame
    #remove_background('captured_frame.jpg')

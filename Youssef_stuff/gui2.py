import cv2
import mediapipe as mp
import time
from rembg import remove
from PIL import Image, ImageTk
import os
import tkinter as tk

cap = None
calculated_values = {}
height = 0
pose_running = False

def pose_estimation():
    global cap, calculated_values, pose_running
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, model_complexity=1, smooth_landmarks=True, enable_segmentation=False, smooth_segmentation=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils
    start_time = time.time()
    picture_taken = False

    clean_frame = None

    while pose_running:
        if cap is not None:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            frame = cv2.flip(frame, 1)

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
                def dist_bw_two_points(a, b):
                    a_marks = landmarks[a]
                    b_marks = landmarks[b]

                    a_x, a_y = int(a_marks.x * frame.shape[1]), int(a_marks.y * frame.shape[0])
                    b_x, b_y = int(b_marks.x * frame.shape[1]), int(b_marks.y * frame.shape[0])

                    distance = math.sqrt((b_x - a_x) ** 2 + (b_y - a_y) ** 2)
                    return distance

                if time.time() - start_time <= 8:
                    # Relative Positioning of LEFT_WRIST AND RIGHT_WRIST
                    fixed_distance = 80 / dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_WRIST, mp_pose.PoseLandmark.LEFT_WRIST)
                
                    # LEFT ARM LENGTH
                    left_arm_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_WRIST)
                    
                    # RIGHT ARM LENGTH
                    right_arm_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_WRIST)

                    # SHOULDER LENGTH
                    shoulder_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.LEFT_SHOULDER) + 3
                    chest_circumference = 3.14 * shoulder_length - 20

                    # WAIST CIRCUMFERENCE
                    waist_length = fixed_distance * dist_bw_two_points(mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.LEFT_HIP) + 4.86
                    waist_circumference = 3.14 * waist_length
                    
                    # HEIGHT
                    nosey = landmarks[mp_pose.PoseLandmark.NOSE]
                    nosey_position = (int(nosey.y * frame.shape[0]))
                    height = (1760 - nosey_position) / 481.0 + 0.16

                    calculated_values['Fixed Distance'] = str(round(fixed_distance, 2)) + " cm"
                    calculated_values['Height'] = str(round(height, 2)) + " cm"
                    calculated_values['Left Arm Length'] = str(round(left_arm_length, 2)) + " cm"
                    calculated_values['Right Arm Length'] = str(round(right_arm_length, 2)) + " cm"
                    calculated_values['Shoulder Length'] = str(round(shoulder_length, 2)) + " cm"
                    calculated_values['Chest Circumference'] = str(round(chest_circumference, 2)) + " cm"
                    calculated_values['Waist Length'] = str(round(waist_length, 2)) + " cm"
                    calculated_values['Waist Circumference'] = str(round(waist_circumference, 2)) + " cm"

                x_coord = [landmark.x for landmark in landmarks]
                y_coord = [landmark.y for landmark in landmarks]

                min_x_l = int(min(x_coord) * frame.shape[1])
                max_x_l = int(max(x_coord) * frame.shape[1])
                min_y_l = int(min(y_coord) * frame.shape[0])
                max_y_l = int(max(y_coord) * frame.shape[0])

                min_x_l, max_x_l, min_y_l, max_y_l = good_ar_bb(min_x_l - 10, max_x_l + 10, min_y_l - 80, max_y_l + 30)
                cv2.rectangle(frame, (min_x_l, min_y_l), (max_x_l, max_y_l), (0, 255, 0), 2)

                # Display measurements on the frame
                y_offset = 30
                for key, value in calculated_values.items():
                    cv2.putText(frame, f"{key}: {value}", (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    y_offset += 30
                
            # Convert the frame to an image that can be displayed in Tkinter
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            live_stream_label.imgtk = imgtk
            live_stream_label.configure(image=imgtk)
                
            # Display the annotated frame
            #cv2.imshow('Pose Estimation', frame)

            if not picture_taken and time.time() - start_time > 15:
                cv2.imwrite('captured_frame.jpg', clean_frame)
                picture_taken = True

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
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

    ar_bb = dx / dy

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
    cropped_img = img.crop((min_x, min_y, max_x, max_y))

    resized_image = cropped_img.resize((768, 1024))
    resized_image.save('cropped_resized_frame.jpg')
    print("Cropped image saved as")

    remove_background('cropped_resized_frame.jpg')

def start_video():
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(1)  # Change to 0 if the webcam is at index 0
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Reduce the frame size
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)  # Reduce the frame size

def stop_video():
    global cap, pose_running
    if cap is not None:
        pose_running = False
        cap.release()
        cap = None
        print(calculated_values)

def remove_background(input_path):
    directory = os.path.dirname(input_path)
    filename = os.path.basename(input_path)
    output_filename = os.path.splitext(filename)[0] + '_output.png'
    output_path = os.path.join(directory, output_filename)

    input_image = Image.open(input_path)
    output_image = remove(input_image)

    white_bg = Image.new("RGBA", output_image.size, (255, 255, 255, 255))
    white_bg.paste(output_image, (0, 0), output_image)
    
    white_bg_rgb = white_bg.convert("RGB")
    white_bg_rgb.save(output_path)

    print(f"Processed image saved as {output_path}")

def start_pose_estimation():
    global root, main_frame, live_stream_label

    main_frame.destroy()  # Destroy the initial frame

    # Create new frame for video and measurements
    new_frame = tk.Frame(root)
    new_frame.pack(fill=tk.BOTH, expand=True)

    # Left column for images
    left_frame = tk.Frame(new_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.Y)

    # Load and display images in the left column
    for i in range(1, 6):
        img_path = os.path.join(os.getcwd(), f'image{i}.jpg')  # Assuming image files are named image1.jpg, image2.jpg, etc.
        img = Image.open(img_path)
        img = img.resize((150, 150))
        imgtk = ImageTk.PhotoImage(img)
        img_label = tk.Label(left_frame, image=imgtk)
        img_label.image = imgtk  # Keep a reference to avoid garbage collection
        img_label.pack(pady=10)

    # Center frame for live stream
    center_frame = tk.Frame(new_frame)
    center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    live_stream_label = tk.Label(center_frame)
    live_stream_label.pack(fill=tk.BOTH, expand=True)

    # Right column for images
    right_frame = tk.Frame(new_frame)
    right_frame.pack(side=tk.LEFT, fill=tk.Y)

    # Load and display images in the right column
    for i in range(6, 11):
        img_path = os.path.join(os.getcwd(), f'image{i}.jpg')  # Assuming image files are named image6.jpg, image7.jpg, etc.
        img = Image.open(img_path)
        img = img.resize((150, 150))
        imgtk = ImageTk.PhotoImage(img)
        img_label = tk.Label(right_frame, image=imgtk)
        img_label.image = imgtk  # Keep a reference to avoid garbage collection
        img_label.pack(pady=10)

    start_video()
    global pose_running
    pose_running = True

    pose_estimation()
    stop_video()

def show_notification():
    notification = tk.Toplevel(root)
    notification_label = tk.Label(notification, text="We will take your measurements first. Please stand in front of the TV", font=('Helvetica', 16))
    notification_label.pack(pady=40)
    root.after(8000, lambda: notification.destroy())
    root.after(8000, start_pose_estimation)

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Virtual Try-on")

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    message_label = tk.Label(main_frame, text="Wanna Try some outfits before shopping? Try Our Virtual Try-on Today.", font=('Helvetica', 20))
    message_label.pack(pady=40)

    start_button = tk.Button(main_frame, text="Start", command=show_notification, font=('Helvetica', 18))
    start_button.pack(pady=20)

    root.mainloop()

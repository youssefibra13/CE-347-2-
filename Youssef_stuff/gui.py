import cv2
import mediapipe as mp
import math
import time
from rembg import remove
from PIL import Image, ImageChops, ImageTk
import os
import tkinter as tk
import requests

cap = None
calculated_values = {}
height = 0
pose_running = False
selected_top = None
selected_bottom = None

# Create a dictionary that maps image numbers to their links
image_links = {
    1: 'https://m.media-amazon.com/images/I/51ei4ovZkML._AC_SL1500_.jpg',
    2: 'https://m.media-amazon.com/images/I/81LQKqWP-SL._AC_SL1240_.jpg',
    3: 'https://m.media-amazon.com/images/I/51fXZywiqJL._AC_SL1500_.jpg',
    4: 'https://m.media-amazon.com/images/I/61ghRCrF+zL._AC_SL1500_.jpg',
    5: 'https://m.media-amazon.com/images/I/91vGZV0B7cL._AC_SL1500_.jpg',
    6: 'https://m.media-amazon.com/images/I/51iejFS+YjL._AC_SL1500_.jpg',
    7: 'https://m.media-amazon.com/images/I/61PW2AjZDEL._AC_SL1000_.jpg',
    8: 'https://m.media-amazon.com/images/I/71+8pg5EZvL._AC_SL1500_.jpg',
    9: 'https://m.media-amazon.com/images/I/81LOWvyXYvL._AC_SL1500_.jpg',
    10: 'https://m.media-amazon.com/images/I/814kdMWIe2L._AC_SL1500_.jpg',
    11: 'https://m.media-amazon.com/images/I/61KFJ-d4BhL._AC_SL1500_.jpg',
    12: 'https://m.media-amazon.com/images/I/81eS7FlxHwL._AC_SL1500_.jpg'
}

def send_data_to_server(top_link, bottom_link):
    url = 'https://agents.socratics.ai:8080/ootd'
    data = {
        'lower_body': bottom_link,
        'upper_body': top_link
    }

    files = {
        'body': ('cropped_resized_frame_output.png', open('cropped_resized_frame_output.png', 'rb'), 'image/png')
    }
    response = requests.post(url, data=data, files=files)
    if response.status_code == 200:
        print('Data sent successfully!')
        return response.content
    else:
        print('Failed to send data.')
        return None

def pose_estimation():
    global cap, calculated_values, pose_running
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
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
                def dist_bw_two_points(a, b, frame):
                    a_marks = landmarks[a]
                    b_marks = landmarks[b]

                    a_x, a_y = int(a_marks.x * frame.shape[1]), int(a_marks.y * frame.shape[0])
                    b_x, b_y = int(b_marks.x * frame.shape[1]), int(b_marks.y * frame.shape[0])

                    distance = math.sqrt((b_x - a_x) ** 2 + (b_y - a_y) ** 2)
                    cv2.circle(frame, (a_x, a_y), 5, (0, 255, 0), -1)
                    cv2.circle(frame, (b_x, b_y), 5, (0, 255, 0), -1)
                    
                    return distance

                if time.time() - start_time <= 8:
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
                    height = (1760-nosey_position)/481.0 + 0.16

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
                
            # Display the annotated frame
            cv2.imshow('Pose Estimation', frame)

            if not picture_taken and time.time() - start_time > 15:
                cv2.imwrite('captured_frame.jpg', clean_frame)
                picture_taken = True
                crop_and_save_image('captured_frame.jpg', min_x_l, min_y_l, max_x_l, max_y_l)
                send_to_server_and_display()

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    print(calculated_values)

    

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
    cropped_img = img.crop((min_x, min_y, max_x, max_y))

    resized_image = cropped_img.resize((768, 1024))
    resized_image.save('cropped_resized_frame_output.png')
    print("Cropped image saved as cropped_resized_frame_output.png")

    remove_background('cropped_resized_frame_output.png')

def start_video():
    global cap
    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2048)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1536)

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
    global root, main_frame
    main_frame.destroy()  # Destroy the initial frame

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

def show_images():
    global root, main_frame

    main_frame.destroy()  # Destroy the initial frame

    image_frame = tk.Frame(root)
    image_frame.pack(fill=tk.BOTH, expand=True)

    top_label = tk.Label(image_frame, text="Enter the number for the top:", font=('Helvetica', 16))
    top_label.grid(row=0, column=0, pady=10, sticky=tk.E)
    top_entry = tk.Entry(image_frame, font=('Helvetica', 16))
    top_entry.grid(row=0, column=1, pady=10, sticky=tk.W)

    bottom_label = tk.Label(image_frame, text="Enter the number for the bottom/pants:", font=('Helvetica', 16))
    bottom_label.grid(row=1, column=0, pady=10, sticky=tk.E)
    bottom_entry = tk.Entry(image_frame, font=('Helvetica', 16))
    bottom_entry.grid(row=1, column=1, pady=10, sticky=tk.W)

    image_paths = [f'image{i}.jpg' for i in range(1, 13)]  # Update to 12 images
    images = []
    
    for image_path in image_paths:
        img = Image.open(image_path)
        img = img.resize((200, 200))  # Resize the images if needed
        img = ImageTk.PhotoImage(img)
        images.append(img)

    for i in range(3):  # 3 rows
        for j in range(4):  # 4 images per row
            image_index = i * 4 + j
            if image_index < len(images):
                label = tk.Label(image_frame, image=images[image_index])
                label.grid(row=i + 2, column=j, padx=10, pady=10)
                label.image = images[image_index]  # Keep a reference to avoid garbage collection
                label_text = tk.Label(image_frame, text=f"{image_index + 1}", font=('Helvetica', 16))
                label_text.grid(row=i + 2, column=j, sticky=tk.S, pady=10)

    submit_button = tk.Button(image_frame, text="Submit", command=lambda: submit_selection(top_entry.get(), bottom_entry.get()), font=('Helvetica', 16))
    submit_button.grid(row=5, column=0, columnspan=4, pady=20)

def submit_selection(top, bottom):
    global selected_top, selected_bottom, main_frame
    selected_top = top
    selected_bottom = bottom
    print(f"Selected Top: {selected_top}, Selected Bottom: {selected_bottom}")

    show_notification()

def send_to_server_and_display():
    global selected_top, selected_bottom
    top_link = image_links[int(selected_top)]
    bottom_link = image_links[int(selected_bottom)]
    received_image_data = send_data_to_server(top_link, bottom_link)
    
    if received_image_data:
        display_received_image(received_image_data)

def display_received_image(image_data):
    global root
    image = Image.open(BytesIO(image_data))
    image = ImageTk.PhotoImage(image)
    
    result_frame = tk.Frame(root)
    result_frame.pack(fill=tk.BOTH, expand=True)

    result_label = tk.Label(result_frame, image=image)
    result_label.pack(pady=20)
    result_label.image = image  # Keep a reference to avoid garbage collection

    stop_video()

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Virtual Try-on")

    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)

    message_label = tk.Label(main_frame, text="Wanna Try some outfits before shopping? Try Our Virtual Try-on Today.", font=('Helvetica', 20))
    message_label.pack(pady=40)

    start_button = tk.Button(main_frame, text="Start", command=show_images, font=('Helvetica', 18))
    start_button.pack(pady=20)

    root.mainloop()

import mediapipe as mp

from mediapipe import solutions

import math

import cv2

import keyboard

from mediapipe.framework.formats import landmark_pb2
import numpy as np

import pyautogui

import time

from system_wrapper import SystemWrapper

MARGIN = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54) # vibrant green

DISPLAY_RES = [2560, 1440]
MOUSE_OUTER_DEADZONE = 0.1
POLL_RATE = 30 #Hz

def draw_landmarks_on_image(rgb_image, detection_result):
  hand_landmarks_list = detection_result.hand_landmarks
  handedness_list = detection_result.handedness
  annotated_image = np.copy(rgb_image)

  # Loop through the detected hands to visualize.
  for idx in range(len(hand_landmarks_list)):
    hand_landmarks = hand_landmarks_list[idx]
    handedness = handedness_list[idx]

    # Draw the hand landmarks.
    hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
    hand_landmarks_proto.landmark.extend([
      landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
    ])
    solutions.drawing_utils.draw_landmarks(
      annotated_image,
      hand_landmarks_proto,
      solutions.hands.HAND_CONNECTIONS,
      solutions.drawing_styles.get_default_hand_landmarks_style(),
      solutions.drawing_styles.get_default_hand_connections_style())

    # Get the top left corner of the detected hand's bounding box.
    height, width, _ = annotated_image.shape
    x_coordinates = [landmark.x for landmark in hand_landmarks]
    y_coordinates = [landmark.y for landmark in hand_landmarks]
    text_x = int(min(x_coordinates) * width)
    text_y = int(min(y_coordinates) * height) - MARGIN

    # Draw handedness (left or right hand) on the image.
    cv2.putText(annotated_image, f"{handedness[0].category_name}",
                (text_x, text_y), cv2.FONT_HERSHEY_DUPLEX,
                FONT_SIZE, HANDEDNESS_TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

  return annotated_image

model_path = 'C:\\Users\\ohjui\\Desktop\\northwestern tings\\Spring 2024\\347-2\\not_racist.task'
         
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# def print_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):

#     try:

#         # print("Distance is " + "{:.4f}".format(distance_index_thumb(result)), end = "\r")

#         print_index(result)

#         posx = int(result.hand_landmarks[0][8].x * DISPLAY_RES[0])
#         posy = int(result.hand_landmarks[0][8].y * DISPLAY_RES[1])
        
#         posx = DISPLAY_RES[0] - posx

#         # pyautogui.moveTo(posx, posy)

#         if (distance_index_thumb(result) < 0.05) : pyautogui.mouseDown(x = posx, y = posy)

#         else: pyautogui.mouseUp(x = posx, y = posy)

#     except:
       
#        print("Hand not found\t\t\t\t\t\t\t\t\t\t\t\t\t", end='\r')

sys = SystemWrapper(screen_res=[3440,1440], ratio=0.35)

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=sys.mouse_update)

vid = cv2.VideoCapture(0)

count = 0

print("starting loop")

x1 = 0
y1 = 0
z1 = 0

x2 = 0
y2 = 0
z2 = 0

RATIO = 0.2

with HandLandmarker.create_from_options(options) as landmarker:
        
    while True:

        if keyboard.is_pressed('q'): break
        
        ret, frame = vid.read()
        count += 1
    
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    
        landmarker.detect_async(mp_image, count)

        time.sleep(1/POLL_RATE)

vid.release()
    
cv2.destroyAllWindows() 

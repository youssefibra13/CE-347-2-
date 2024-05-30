# # # # import the opencv library 
# # # import cv2 


# # # # define a video capture object 
# # # vid = cv2.VideoCapture(0) 

# # # while(True): 
	
# # # 	# Capture the video frame 
# # # 	# by frame 
# # # 	ret, frame = vid.read() 

# # # 	# Display the resulting frame 
# # # 	cv2.imshow('frame', frame) 
	
# # # 	# the 'q' button is set as the 
# # # 	# quitting button you may use any 
# # # 	# desired button of your choice 
# # # 	if cv2.waitKey(1) & 0xFF == ord('q'): 
# # # 		break

# # # # After the loop release the cap object 
# # # vid.release() 
# # # # Destroy all the windows 
# # # cv2.destroyAllWindows() 


# # import cv2

# # def gstreamer_pipeline(capture_width=1280, capture_height=720, display_width=1280, display_height=720, framerate=60, flip_method=0):
# #     return (
# #         f"nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int){capture_width}, height=(int){capture_height}, format=(string)NV12, framerate=(fraction){framerate}/1 ! "
# #         f"nvvidconv flip-method={flip_method} ! video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! "
# #         "videoconvert ! video/x-raw, format=(string)BGR ! appsink"
# #     )

# # cap = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
# # if not cap.isOpened():
# #     print("Failed to open camera.")
# # else:
# #     while True:
# #         ret, frame = cap.read()
# #         if not ret:
# #             print("Failed to get frame.")
# #             break
       
# #         cv2.imshow("CSI Camera", frame)
# #         keyCode = cv2.waitKey(30) & 0xFF
# #         # Stop the program on the ESC key
# #         if keyCode == 27:
# #             break

# # cap.release()
# # cv2.destroyAllWindows()

# import sys
# import cv2

# def read_cam():
#     cap = cv2.VideoCapture("nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080,format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert !  appsink")
#     if cap.isOpened():
#         cv2.namedWindow("demo", cv2.WINDOW_AUTOSIZE)
#         while True:
#             ret_val, img = cap.read();
#             cv2.imshow('demo',img)
#             cv2.waitKey(10)
#     else:
#      print ("camera open failed")

#     cv2.destroyAllWindows()


# if __name__ == '__main__':
#     read_cam()

import sys
import cv2

def read_cam():
    cap = cv2.VideoCapture("nvarguscamerasrc ! video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080,format=(string)NV12, framerate=(fraction)30/1 ! nvvidconv ! video/x-raw, format=(string)I420 ! appsink")
    if cap.isOpened():
        cv2.namedWindow("demo", cv2.WINDOW_AUTOSIZE)
        while True:
            ret_val, img = cap.read();
            img2 = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_I420);
            cv2.imshow('demo',img2)
            cv2.waitKey(10)
    else:
     print ("camera open failed")

    cv2.destroyAllWindows()


if __name__ == '__main__':
    read_cam()
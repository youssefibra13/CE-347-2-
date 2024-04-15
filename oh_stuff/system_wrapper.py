import math
import pyautogui

class SystemWrapper:

    def __init__(self, screen_res = [], ratio = 0.5, pinch_threshold = 0.05, ptr_ratio = 5):

        if screen_res == []:
            
            self.screen_res = [1920, 1080]

        else:

            self.screen_res = screen_res

        self.mouse_x = 0
        self.mouse_y = 0

        self.ratio = ratio

        self.mouse_state = 0 # 0 is depresssed

        self.pinch_threshold = pinch_threshold

        self.pinch_distance = pinch_threshold + 1

        self.ptr_ratio = ptr_ratio

        self.refresh_count = 0

    def distance_index_thumb(self, result):
   
        dx = result.hand_landmarks[0][8].x - result.hand_landmarks[0][4].x
        dy = result.hand_landmarks[0][8].y - result.hand_landmarks[0][4].y
        dz = result.hand_landmarks[0][8].z - result.hand_landmarks[0][4].z

        return math.sqrt(dx * dx + dy * dy + dz * dz)
    
    def print_data(self, result, dist):
   
        print("Index finger at\t" + \
                "{:.4f}".format(result.hand_landmarks[0][8].x) + "\t" +\
                "{:.4f}".format(result.hand_landmarks[0][8].y) + "\t" +\
                "{:.4f}".format(result.hand_landmarks[0][8].z) + "\t" +\
                "{:.4f}".format(dist), end = "\r" )

    def mouse_update(self, result, output_image, timestamp_ms):

        if result.hand_landmarks != []:

            self.mouse_x        = self.ratio * result.hand_landmarks[0][8].x     + (1 - self.ratio) * self.mouse_x
            self.mouse_y        = self.ratio * result.hand_landmarks[0][8].y     + (1 - self.ratio) * self.mouse_y
            self.pinch_distance = self.ratio * self.distance_index_thumb(result) + (1 - self.ratio) * self.pinch_distance

            self.print_data(result, self.pinch_distance)

            # screen_x = (1 - self.mouse_x) * self.screen_res[0]
            # screen_y =      self.mouse_y   * self.screen_res[1]

            # if (self.refresh_count == self.ptr_ratio):

            #     self.refresh_count = 0

            #     if (self.pinch_distance < self.pinch_threshold and self.mouse_state == 0):
            #         pyautogui.mouseDown(x = screen_x, y = screen_y)
            #         self.mouse_state = 1

            #     elif (self.pinch_distance > self.pinch_threshold and self.mouse_state == 1):
            #         pyautogui.mouseUp(x = screen_x, y = screen_y)
            #         self.mouse_state = 0

            #     else:
            #         pyautogui.moveTo(x = screen_x, y = screen_y)

            # else:

            #     self.refresh_count = self.refresh_count + 1

        else:

            print("Hand not found\t\t\t\t\t\t\t\t\t\t\t\t\t", end='\r')





        
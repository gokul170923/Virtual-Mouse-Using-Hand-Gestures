# include the libraries opencv to capture frames 
import cv2
# include mediapipe so we can use its hand landmaarking
import mediapipe as mp
# include pyautogui which lets you control mouse via python
import pyautogui

import time

# Initialize the last click time
last_click_time = 0
click_cooldown = 1  # Cooldown period in seconds

# getting screen dimensions for moving pointer
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()


# mediapipe pre -built solution for working with hands is imported
mp_hands = mp.solutions.hands

# Hands(): Initializes the hand detection model.
# 0.7 telles my model if you are >= 70 percent confident then do stuff
# By default, it looks for hands in the frame and detects 21 landmarks
hands = mp_hands.Hands(min_detection_confidence=0.7)

# this includes a utility for drawing landmarks and their connections 
# on images or video frames becuase we need to display it back to user
mp_drawing = mp.solutions.drawing_utils

# Initialize webcam using the opencv library
cap = cv2.VideoCapture(0)

# Get webcam dimensions ,  no screem res != webcam res
# The screen res. is generally much larger than the webcam resolution.
CAM_WIDTH = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
CAM_HEIGHT = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

# Initialize previous position for smoothing

prev_screen_x, prev_screen_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2


# this function acts as a gateway to map landmarks position to screen
def handle_gesture(hand_landmarks):
        global prev_screen_x , prev_screen_y , clicked , last_click_time

        # Get  finger tip coordinates 
        index_tip = hand_landmarks.landmark[8]

        #  .X and .Y tells position of landmark in the frame 
        # example 0.5 tells taht is at 50 % frame width 

        # since they are at normal form ( 0 to 1 ) 
        # find the actual pizel position with respect to camera or screen 
        # multiply the offsets 
        

        #  ----------------- 1 . to draw circle in pointer finger --------
        x = int(index_tip.x * CAM_WIDTH)
        y = int(index_tip.y * CAM_HEIGHT)

        # Draw a circle at index finger tip
        cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)
        #                       radius,(R G B),-1 makes the circle filled.


        # ------------------ 2 . to move the pointer on screen -----------

        # Map webcam coordinates to screen coordinates
        screen_x = int(index_tip.x * SCREEN_WIDTH)
        screen_y = int(index_tip.y * SCREEN_HEIGHT)

        # Smooth the movement by averaging the previous and current positions
        smooth_x = int((prev_screen_x + screen_x )//2)
        smooth_y = int((prev_screen_y + screen_y )//2)

        # Move the mouse to the smoothed coordinates
        pyautogui.moveTo(smooth_x, smooth_y, duration=0.1)
        # Update the previous position for the next iteration
        prev_screen_x, prev_screen_y = smooth_x, smooth_y

        current_time = time.time()


        # ----------------- 3 . to left click ----------------------------

        if  ( abs(hand_landmarks.landmark[4].x - hand_landmarks.landmark[16].x) < 0.1
              and abs(hand_landmarks.landmark[4].y - hand_landmarks.landmark[16].y) < 0.1
             and current_time - last_click_time > click_cooldown):
                print("left click")
                pyautogui.click()
                last_click_time = current_time


        # ----------------- 4 . to right click ----------------------------

        if ( abs(hand_landmarks.landmark[4].x - hand_landmarks.landmark[20].x) < 0.1
           and abs(hand_landmarks.landmark[4].y - hand_landmarks.landmark[20].y) < 0.1
                and current_time - last_click_time > click_cooldown):
                pyautogui.rightClick()
                print("right click")
                last_click_time = current_time


        # ----------------- 5 . to double click ----------------------------

        if ( abs(hand_landmarks.landmark[12].x - hand_landmarks.landmark[16].x) < 0.05
           and abs(hand_landmarks.landmark[12].y - hand_landmarks.landmark[16].y) < 0.05
                and current_time - last_click_time > click_cooldown):
                pyautogui.doubleClick()
                print("double click")
                last_click_time = current_time


        # ----------------- 6 . to zoom in ----------------------------

        if ( abs(hand_landmarks.landmark[4].x - hand_landmarks.landmark[8].x) < 0.05
           and abs(hand_landmarks.landmark[4].y - hand_landmarks.landmark[8].y) < 0.05
                and current_time - last_click_time > click_cooldown):
                pyautogui.hotkey('ctrl', '+')
                print("zoom in")
                last_click_time = current_time


        # ----------------- 7 . to zoom out ----------------------------
        
        if ( abs(hand_landmarks.landmark[4].x - hand_landmarks.landmark[12].x) < 0.05
           and abs(hand_landmarks.landmark[4].y - hand_landmarks.landmark[12].y) < 0.05
                and current_time - last_click_time > click_cooldown):
                pyautogui.hotkey('ctrl', '-')
                print("zoom out")
                last_click_time = current_time


        # ----------------- 8 . scroll up ----------------------------
        
        if ( abs(hand_landmarks.landmark[8].x - hand_landmarks.landmark[12].x) < 0.05
           and abs(hand_landmarks.landmark[8].y - hand_landmarks.landmark[12].y) < 0.05):
                pyautogui.scroll(-50)
                print("scroll up")


        # ----------------- 8 . scroll down ----------------------------
        
        if ( abs(hand_landmarks.landmark[8].x - hand_landmarks.landmark[5].x) < 0.05
           and abs(hand_landmarks.landmark[8].y - hand_landmarks.landmark[5].y) < 0.05):
                pyautogui.scroll(50)
                print("scroll down")



while True:
        # Capture frame from the live video
        #  .read() returns a boolean value and the actual frame
        returnBoolean, frame = cap.read() 

        # Flip the frame horizontally for a later selfie-view display
        frame = cv2.flip(frame, 1)

        # for some reason OpenCV captures frames in BGR (Blue-Green-Red) fromat
        # but MediaPipe requires RGB (Red-Green-Blue) format.
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame with MediaPipe hands model
        results = hands.process(frame_rgb)

        # If hands are detected .multi_hand_landmarks has the boolean status 
        # and list of the landmarks and coodinates detected 
        if results.multi_hand_landmarks:
            # for all the landmarks in  list  Draw landmarks on the frame using 
                for hand_landmarks in results.multi_hand_landmarks:
                        # drwaing tool draws the result to the original frame
                        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                        # Call the gesture handling function to check for gestures
                        handle_gesture(hand_landmarks)


        # Display the original frame with now landmarks added 
        cv2.imshow("Hand Tracking", frame)      
        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break

# Release webcam and close windows
cap.release()
cv2.destroyAllWindows()

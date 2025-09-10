# File: sports_analyzer/visualize_landmarks.py
import cv2
import mediapipe as mp
import os

# --- Configuration ---
# Update this to the video you want to process. Use 0 for webcam.
INPUT_VIDEO_PATH = "sprint.mp4" 

print("--- Starting Real-Time Landmark Visualization ---")
print("Press 'q' to quit the video window.")

# --- MediaPipe Setup ---
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# --- Video Processing ---
# Use 0 for webcam, or a file path for a video file.
cap_source = 0 if INPUT_VIDEO_PATH.lower() == "webcam" else INPUT_VIDEO_PATH
if cap_source != 0 and not os.path.exists(cap_source):
    print(f"[ERROR] Input video not found at '{cap_source}'")
    exit()

cap = cv2.VideoCapture(cap_source)
if not cap.isOpened():
    print(f"[ERROR] Could not open video source: {cap_source}")
    exit()

# Initialize the Pose model
with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Video stream ended or file could not be read. Exiting.")
            break

        # Flip the image horizontally for a later selfie-view display
        # and convert the BGR image to RGB.
        image = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = pose.process(image)

        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(
                image,
                results.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
            )
        
        # Display the resulting frame
        cv2.imshow('Real-Time MediaPipe Pose', image)

        # Exit logic: press 'q' to close the window
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# --- Cleanup ---
print("\nClosing visualization.")
cap.release()
cv2.destroyAllWindows()


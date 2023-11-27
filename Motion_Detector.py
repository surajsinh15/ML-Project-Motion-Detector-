import cv2
import numpy as np
from IPython.display import display, Image

# Function to get live video feed from webcam
def get_live_video_feed():
    cap = cv2.VideoCapture(0)
    return cap

# Function to read the first frame, convert to Grayscale, and store it as the reference background image
def initialize_reference_background(cap):
    ret, first_frame = cap.read()
    if ret:
        reference_background = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
        reference_background = cv2.resize(reference_background, (500, 500))
        return reference_background
    else:
        return None
    
# Function to compute the absolute difference between the current and first frame
def compute_absolute_difference(prev_frame, cur_frame, next_frame):
    if prev_frame is not None and cur_frame is not None and next_frame is not None:
        cur_frame = cv2.resize(cur_frame, (prev_frame.shape[1], prev_frame.shape[0]))
        next_frame = cv2.resize(next_frame, (prev_frame.shape[1], prev_frame.shape[0]))

        diff1 = cv2.absdiff(next_frame, cur_frame)
        diff2 = cv2.absdiff(cur_frame, prev_frame)

        return cv2.bitwise_and(diff1, diff2)
    else:
        return None
    
# Function to apply threshold to the frame
def apply_threshold(frame_diff_result):
    _, threshold_diff = cv2.threshold(frame_diff_result, 30, 255, cv2.THRESH_BINARY)
    threshold_diff = cv2.dilate(threshold_diff, None, iterations=2)
    return threshold_diff

# Function to find contours in the thresholded frame
def find_contours(threshold_diff):
    contours, _ = cv2.findContours(threshold_diff, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

# Function to check if contourArea is large and draw a rectangle around the object,
# output "UNSAFE" text in red color
def check_and_draw_contours(contours, frame):
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    if len(contours) > 0:
        cv2.putText(frame, "UNSAFE", (frame.shape[1] - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        return True
    else:
        return False
    
# Function to display images
def display_images(frame):
    cv2.imshow('Motion Detector', frame)

# Function to release objects
def release_objects(cap):
    cap.release()
    cv2.destroyAllWindows()

def main():
    # Get live video feed from webcam
    cap = get_live_video_feed()

    # Get video dimensions from the first frame
    _, first_frame = cap.read()
    height, width, _ = first_frame.shape

    # Define the codec and create a VideoWriter object to save the video locally
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # You can change the codec as needed
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (width, height))

    # Initialize reference background
    reference_background = initialize_reference_background(cap)

    # Initialize previous, current, and next frames
    prev_frame = None
    cur_frame = None
    next_frame = None

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Error: Could not read frame")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (500, 500))

        prev_frame = cur_frame
        cur_frame = gray
        next_frame = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2GRAY)

        # Compute absolute difference between frames
        frame_diff_result = compute_absolute_difference(prev_frame, cur_frame, next_frame)

        if frame_diff_result is not None:
            # Apply threshold
            threshold_diff_result = apply_threshold(frame_diff_result)

            # Find contours
            contours = find_contours(threshold_diff_result)

            # Check if contourArea is large and draw rectangle around the object,
            # output "UNSAFE" text in red color
            if check_and_draw_contours(contours, frame):
                print("Motion Detected - UNSAFE")
            else:
                print("No Motion Detected - SAFE")

            # Display images
            display_images(frame)

            # Write the frame to the output video
            out.write(frame)

        # Exit when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release video writer object, video capture object, and close the window
    out.release()
    release_objects(cap)

# Run the main function
main()
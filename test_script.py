import requests
import json

# --- Configuration ---
# Make sure your FastAPI server is running before you execute this script.
API_URL = "http://127.0.0.1:8000/api/v1/analysis/"

# IMPORTANT: Download a test video and place it in the root of the sports_analyzer directory.
# Rename the video to "test_video.mp4" or update the filename below.
# Sample video link: https://www.pexels.com/video/a-man-sprinting-on-a-running-track-5893899/
VIDEO_PATH = "sprint2.mp4"

# --- Athlete Data ---
# These values are sent along with the video, just like in the app.
payload = {
    "sport": "sprint",
    "athlete_height_m": 1.8  # Height in meters (e.g., 1.8m is ~5'11")
}

def run_test():
    """
    Sends a video to the analysis API and prints the response.
    """
    print(f"--- Starting Sprint Analysis Test ---")
    print(f"Target API: {API_URL}")
    print(f"Video File: {VIDEO_PATH}")
    print(f"Payload: {payload}")

    try:
        # Open the video file in binary read mode
        with open(VIDEO_PATH, "rb") as video_file:
            # The 'files' dictionary tells 'requests' how to structure the multipart/form-data
            files_to_upload = {
                'video_file': (VIDEO_PATH, video_file, 'video/mp4')
            }

            print("\nUploading video and sending request... (This may take a moment)")
            
            # Make the POST request
            response = requests.post(API_URL, files=files_to_upload, data=payload)

            # Check the server's response
            print(f"\nServer responded with status code: {response.status_code}")

            if response.status_code == 200:
                print("--- Analysis Successful! ---")
                # Pretty-print the JSON response
                analysis_data = response.json()
                print(json.dumps(analysis_data, indent=4))
            else:
                print("--- Analysis Failed! ---")
                # Print the error details from the server
                print("Error Response:")
                print(response.text)

    except FileNotFoundError:
        print(f"\n[ERROR] Test video not found at '{VIDEO_PATH}'.")
        print("Please download a video, place it in the project's root directory, and name it 'test_video.mp4'.")
    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Connection failed. Is the FastAPI server running?")
        print("Please run 'uvicorn main:app --reload' in a separate terminal before running this test.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    run_test()

import requests
import json

API_URL = "http://127.0.0.1:8000/api/v1/analysis/"

VIDEO_PATH = "high_jump.mp4"

payload = {
    "sport": "high_jump",
    "athlete_height_m": 1.9
}

def run_test():
    print(f"--- Starting Sprint Analysis Test ---")
    print(f"Target API: {API_URL}")
    print(f"Video File: {VIDEO_PATH}")
    print(f"Payload: {payload}")

    try:
        with open(VIDEO_PATH, "rb") as video_file:
            files_to_upload = {
                'video_file': (VIDEO_PATH, video_file, 'video/mp4')
            }

            print("\nUploading video and sending request... (This may take a moment)")
            
            response = requests.post(API_URL, files=files_to_upload, data=payload)

            print(f"\nServer responded with status code: {response.status_code}")

            if response.status_code == 200:
                print("--- Analysis Successful! ---")
                analysis_data = response.json()
                print(json.dumps(analysis_data, indent=4))
            else:
                print("--- Analysis Failed! ---")
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

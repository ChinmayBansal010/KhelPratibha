import time
import os
import argparse
import pandas as pd
from utils.exercise_classifier import ExerciseClassifier
import absl.logging
absl.logging.set_verbosity(absl.logging.ERROR)

def test_single_video(video_path, classifier):
    """
    Runs classification on a single video file.
    
    Args:
        video_path (str): Path to the video file.
        classifier (ExerciseClassifier): The initialized classifier object.
    
    Returns:
        dict: Results with filename, prediction, and processing time.
    """
    print(f"\n▶ Processing: {os.path.basename(video_path)}")

    start_time = time.time()
    try:
        predicted_exercise = classifier.classify(video_path)
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return {
            "video": os.path.basename(video_path),
            "prediction": "error",
            "time_sec": None
        }
    end_time = time.time()

    processing_time = round(end_time - start_time, 2)

    print(f"   ✅ Prediction: {predicted_exercise.upper()}")
    print(f"   ⏱ Processing Time: {processing_time:.2f} sec")

    return {
        "video": os.path.basename(video_path),
        "prediction": predicted_exercise,
        "time_sec": processing_time
    }


def run_tests(video_paths, save_csv=False, output_csv="results.csv"):
    """
    Runs the classifier on one or multiple videos.
    
    Args:
        video_paths (list[str]): List of video file paths.
        save_csv (bool): Whether to save results as CSV.
        output_csv (str): File path for saving CSV.
    """
    print("\n--- Testing Rule-Based Exercise Classifier ---")
    classifier = ExerciseClassifier()

    results = []
    for path in video_paths:
        if not os.path.exists(path):
            print(f"\n❌ Skipping (file not found): {path}")
            continue
        results.append(test_single_video(path, classifier))

    # Save to CSV if requested
    if save_csv and results:
        df = pd.DataFrame(results)
        df.to_csv(output_csv, index=False)
        print(f"\n📁 Results saved to '{output_csv}'")


def collect_videos(input_path):
    """
    Collects video paths from a single file or directory.
    """
    if os.path.isdir(input_path):
        return [
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.lower().endswith((".mp4", ".avi", ".mov"))
        ]
    elif os.path.isfile(input_path):
        return [input_path]
    return []


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Test Exercise Classifier on video(s).")
    parser.add_argument("input", help="Path to a video file or a folder containing videos.")
    parser.add_argument("--csv", action="store_true", help="Save results to CSV.")
    parser.add_argument("--output", default="results.csv", help="CSV output filename.")
    args = parser.parse_args()

    videos = collect_videos(args.input)
    if not videos:
        print(f"\n❌ No valid video files found in: {args.input}")
    else:
        run_tests(videos, save_csv=args.csv, output_csv=args.output)

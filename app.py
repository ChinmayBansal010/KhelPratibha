import os
import cv2
import mediapipe as mp
import pandas as pd
import traceback
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from utils.exercise_classifier import ExerciseClassifier
# Import all counters, including the new ones
from exercises.pushups import PushupCounter
from exercises.squats import SquatCounter
from exercises.situps import SitupCounter
from exercises.pullups import PullupCounter
from exercises.jumping_jacks import JumpingJackCounter
from exercises.lunges import LungeCounter
from exercises.bicep_curls import BicepCurlCounter

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

classifier = ExerciseClassifier()

def process_video_for_reps(filepath, exercise_type):
    """Processes a video file to count repetitions for a specific exercise."""
    cap = cv2.VideoCapture(filepath)
    # Add the new counters to the dictionary
    counters = {
        'pushups': PushupCounter(), 'squats': SquatCounter(),
        'situps': SitupCounter(), 'pullups': PullupCounter(),
        'jumpingjacks': JumpingJackCounter(), 'lunges': LungeCounter(),
        'bicepcurls': BicepCurlCounter()
    }
    counter = counters.get(exercise_type.lower())
    
    if not counter:
        raise ValueError(f"Invalid exercise type provided: {exercise_type}")

    with mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret: break
            
            results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                h, w, _ = frame.shape
                landmarks = {name: (lm[mark.value].x*w, lm[mark.value].y*h, lm[mark.value].z) for name, mark in mp.solutions.pose.PoseLandmark.__members__.items()}
                counter.update(landmarks)
    cap.release()

    total_reps = counter.good_reps + counter.bad_reps
    score = int(round(total_reps * (counter.good_reps / total_reps))) if total_reps > 0 else 0
    
    return {
        "good_reps": counter.good_reps, "bad_reps": counter.bad_reps,
        "feedback_log": counter.feedback_log, "score": score
    }

@app.route('/process_video', methods=['POST'])
def handle_video_upload():
    """Main API endpoint for video processing."""
    if 'video' not in request.files or 'exercise_type' not in request.form:
        return jsonify({'error': 'Missing video or exercise_type'}), 400

    video = request.files['video']
    user_exercise = request.form['exercise_type'].lower()
    
    if video.filename == '':
        return jsonify({'error': 'No video file selected'}), 400

    filename = secure_filename(video.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        video.save(filepath)
        detected_exercise = classifier.classify(filepath)
        
        if detected_exercise != "unknown" and detected_exercise != user_exercise:
            msg = f"It looks like you're doing {detected_exercise}, but you selected {user_exercise}."
            return jsonify({'error': msg, 'verified': False}), 400

        results = process_video_for_reps(filepath, user_exercise)
        return jsonify({'verified': True, 'exercise': user_exercise, **results}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'An internal error occurred: {e}'}), 500
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


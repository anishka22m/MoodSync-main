from flask import Flask, jsonify, request
import cv2
import numpy as np
from keras.models import load_model
import mediapipe as mp
from streamlit_webrtc import VideoProcessorBase, webrtc_streamer
import av
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

# Load the model and other required components
model = load_model("Model and labels/model.keras")
label = np.load("Model and labels/labels.npy")
holistic = mp.solutions.holistic
hands = mp.solutions.hands
holis = holistic.Holistic()
drawing = mp.solutions.drawing_utils

# Custom Video Processor for Emotion Processing
class EmotionProcessor(VideoProcessorBase):
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        frm = frame.to_ndarray(format="bgr24")

        frm = cv2.flip(frm, 1)

        res = holis.process(cv2.cvtColor(frm, cv2.COLOR_BGR2RGB))

        lst = []

        if res.face_landmarks:
            for i in res.face_landmarks.landmark:
                lst.append(i.x - res.face_landmarks.landmark[1].x)
                lst.append(i.y - res.face_landmarks.landmark[1].y)

            if res.left_hand_landmarks:
                for i in res.left_hand_landmarks.landmark:
                    lst.append(i.x - res.left_hand_landmarks.landmark[8].x)
                    lst.append(i.y - res.left_hand_landmarks.landmark[8].y)
            else:
                for i in range(42):
                    lst.append(0.0)

            if res.right_hand_landmarks:
                for i in res.right_hand_landmarks.landmark:
                    lst.append(i.x - res.right_hand_landmarks.landmark[8].x)
                    lst.append(i.y - res.right_hand_landmarks.landmark[8].y)
            else:
                for i in range(42):
                    lst.append(0.0)

            lst = np.array(lst).reshape(1, -1)

            # Log frame data before processing
            print("Before Processing - Frame Data:", lst)

            pred = label[np.argmax(model.predict(lst))]

            print(pred)
            cv2.putText(frm, pred, (50, 50), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)

            np.save("emotion.npy", np.array([pred]))

        # Log frame data after processing
        print("After Processing - Frame Data:", lst)

        drawing.draw_landmarks(
            frm,
            res.face_landmarks,
            holistic.FACEMESH_TESSELATION,
            landmark_drawing_spec=drawing.DrawingSpec(
                color=(0, 0, 255), thickness=-1, circle_radius=1
            ),
            connection_drawing_spec=drawing.DrawingSpec(thickness=1),
        )
        drawing.draw_landmarks(frm, res.left_hand_landmarks, hands.HAND_CONNECTIONS)
        drawing.draw_landmarks(frm, res.right_hand_landmarks, hands.HAND_CONNECTIONS)

        return av.VideoFrame.from_ndarray(frm, format="bgr24")


# @app.route("/get_emotion", methods=["POST"])
# def get_emotion():
#     data = request.json
#     frame_data = data.get("frame")
#     frame = av.VideoFrame.from_ndarray(np.array(frame_data), format="bgr24")

#     # Use the EmotionProcessor to process the frame
#     processor = EmotionProcessor()
#     processed_frame = processor.recv(frame)

#     return jsonify({"processed_frame": processed_frame.to_ndarray().tolist()})
@app.route("/get_emotion", methods=["GET", "POST"])
def get_emotion():
    try:
        if request.method == "GET":
            frame_data = request.args.get("frame")
        elif request.method == "POST":
            data = request.get_json()
            frame_data = data.get("frame")

        # Log received frame data
        print("Received Frame Data:", frame_data)

        frame = av.VideoFrame.from_ndarray(np.array(json.loads(frame_data)), format="bgr24")

        # Use the EmotionProcessor to process the frame
        processor = EmotionProcessor()
        processed_frame = processor.recv(frame)

        return jsonify({"processed_frame": processed_frame.to_ndarray().tolist()})

    except Exception as e:
        # Log the exception for debugging
        print(f"Error in get_emotion endpoint: {e}")
        return jsonify({"error": "Internal Server Error"}), 500



if __name__ == "__main__":
    app.run(debug=True, port=5500)


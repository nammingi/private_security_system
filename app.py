from flask import Flask, render_template, Response
import cv2
import imutils
import datetime

app = Flask(__name__)
video_capture = cv2.VideoCapture(0)  # 카메라 장치 설정

def detect_motion():
    first_frame = None
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        
        # 회색조 변환 및 가우시안 블러 적용
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if first_frame is None:
            first_frame = gray
            continue

        # 움직임 감지: 현재 프레임과 초기 프레임의 차이 계산
        frame_delta = cv2.absdiff(first_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        motion_detected = False
        for c in cnts:
            if cv2.contourArea(c) < 500:  # 작은 움직임은 무시
                continue
            motion_detected = True
            break

        # 움직임이 감지되면 영상을 저장합니다.
        if motion_detected:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            cv2.imwrite(f"motion_{timestamp}.jpg", frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame.tobytes() + b'\r\n')
        
        # 실시간 영상 스트리밍을 위한 프레임 전송
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            break
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')


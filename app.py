from flask import Flask, render_template, Response
import cv2
from multiprocessing import Process, Queue
import time

app = Flask(__name__)
frame_queue = Queue()  # 프레임을 저장할 큐 생성

def capture_frames(queue):
    """카메라 프레임을 캡처하고 큐에 저장하는 함수"""
    video_capture = cv2.VideoCapture(0)
    while True:
        ret, frame = video_capture.read()
        if not ret:
            continue
        # 프레임을 큐에 넣음
        if queue.qsize() < 10:  # 큐 크기를 제한하여 메모리 과부하 방지
            queue.put(frame)

def generate_frames():
    """큐에서 프레임을 읽어와 HTTP 스트림으로 변환"""
    while True:
        if not frame_queue.empty():
            frame = frame_queue.get()
            ret, jpeg = cv2.imencode('.jpg', frame)
            if ret:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
        else:
            time.sleep(0.1)  # 큐가 비었을 때 잠시 대기

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # 멀티프로세스 설정
    p = Process(target=capture_frames, args=(frame_queue,))
    p.start()
    # Flask 서버 시작
    app.run(host='0.0.0.0', port=5000, debug=True)
    p.join()  # Flask 서버가 종료되면 프로세스도 종료

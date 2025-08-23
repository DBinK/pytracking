# client.py
import zmq
import cv2

class RemoteTracker:
    def __init__(self, address="tcp://127.0.0.1:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(address)
        self.initialized = False

    def _encode_frame(self, frame):
        """编码图像为JPEG，并转hex字符串"""
        _, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        return buf.tobytes().hex()

    def init(self, frame, bbox):
        msg = {
            "cmd": "init",
            "frame": self._encode_frame(frame),
            "bbox": bbox
        }
        self.socket.send_json(msg)
        reply = self.socket.recv_json()
        if reply["status"] == "ok":
            self.initialized = True
            return True
        return False

    def update(self, frame):
        if not self.initialized:
            raise RuntimeError("Tracker not initialized. Call init() first.")

        msg = {
            "cmd": "update",
            "frame": self._encode_frame(frame),
        }
        self.socket.send_json(msg)
        reply = self.socket.recv_json()

        if reply["status"] == "ok":
            return True, tuple(reply["bbox"])
        else:
            return False, None

if __name__ == "__main__":
    tracker = RemoteTracker()
    cap = cv2.VideoCapture("tmp/1.mp4")
    print(f"视频帧数: {cap.get(cv2.CAP_PROP_FRAME_COUNT)}")
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if not tracker.initialized:
            tracker.init(frame, (100, 100, 400, 400))

        # 记录开始时间（时钟周期数）
        start_tick = cv2.getTickCount()

        success, bbox = tracker.update(frame)

        # 记录结束时间（时钟周期数），并计算用时（秒）
        end_tick = cv2.getTickCount()
        elapsed_time = (end_tick - start_tick) / cv2.getTickFrequency() * 1000

        print("追踪结果:", success, bbox)
        print(f"tracker.update() 执行时间: {elapsed_time:.6f} ms")
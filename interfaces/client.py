import zmq
import cv2
import json

class RemoteTracker:
    def __init__(self, address="tcp://127.0.0.1:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(address)
        self.initialized = False

    def _encode_frame(self, frame):
        """编码图像为JPEG（二进制）"""
        _, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        return buf.tobytes()

    def init(self, frame, bbox):
        meta = {"cmd": "init", "bbox": bbox}
        frame_bytes = self._encode_frame(frame)
        # multipart: [json, binary]
        self.socket.send_multipart([json.dumps(meta).encode("utf-8"), frame_bytes])
        reply = self.socket.recv_json()
        if reply["status"] == "ok":
            self.initialized = True
            return True
        return False

    def update(self, frame):
        if not self.initialized:
            raise RuntimeError("Tracker not initialized. Call init() first.")

        meta = {"cmd": "update"}
        frame_bytes = self._encode_frame(frame)
        self.socket.send_multipart([json.dumps(meta).encode("utf-8"), frame_bytes])
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

        start_tick = cv2.getTickCount()
        success, bbox = tracker.update(frame)
        end_tick = cv2.getTickCount()
        elapsed_time = (end_tick - start_tick) / cv2.getTickFrequency() * 1000

        print("追踪结果:", success, bbox)
        print(f"tracker.update() 执行时间: {elapsed_time:.6f} ms")

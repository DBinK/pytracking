import zmq
import cv2
import json

class RemoteTracker:
    def __init__(self, address="tcp://127.0.0.1:5555"):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect(address)
        self.initialized = False
        self.session_id = None

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
        # 确保reply是字典类型
        if isinstance(reply, dict) and reply.get("status") == "ok":
            self.initialized = True
            self.session_id = reply.get("session_id")
            return True
        return False

    def update(self, frame):
        if not self.initialized:
            raise RuntimeError("Tracker not initialized. Call init() first.")
        
        if not self.session_id:
            raise RuntimeError("No session ID available.")

        meta = {"cmd": "update", "session_id": self.session_id}
        frame_bytes = self._encode_frame(frame)
        self.socket.send_multipart([json.dumps(meta).encode("utf-8"), frame_bytes])
        reply = self.socket.recv_json()
        
        # 确保reply是字典类型
        if isinstance(reply, dict) and reply.get("status") == "ok":
            bbox = reply["bbox"]  # 确保bbox可以转换为tuple类型
            if isinstance(bbox, (list, tuple)) and len(bbox) == 4:
                return True, tuple(bbox)  
            else:                 # 如果bbox不是期望的格式，则返回错误
                return False, None
        else:
            return False, None

    def release(self):
        """
        释放远程跟踪器资源
        """
        if not self.session_id:
            return False
            
        meta = {"cmd": "release", "session_id": self.session_id}
        self.socket.send_json(meta)
        reply = self.socket.recv_json()
        
        if isinstance(reply, dict) and reply.get("status") == "ok":
            self.session_id = None
            self.initialized = False
            return True
        return False


if __name__ == "__main__":
    tracker = RemoteTracker()
    cap = cv2.VideoCapture("tmp/2.mp4")

    print(f"视频帧数: {cap.get(cv2.CAP_PROP_FRAME_COUNT)}")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if not tracker.initialized:
            tracker.init(frame, (651, 259, 114, 90))

        start_tick = cv2.getTickCount()
        success, bbox = tracker.update(frame)
        end_tick = cv2.getTickCount()
        elapsed_time = (end_tick - start_tick) / cv2.getTickFrequency() * 1000

        print("追踪结果:", success, bbox)
        print(f"tracker.update() 执行时间: {elapsed_time:.6f} ms")
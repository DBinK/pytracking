import zmq
import cv2
import numpy as np
import json

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from interfaces.cv_wrapper import TrackerDiMP_create


class TrackerServer:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5555")
        
        self.tracker_initialized = False
        self.init_bbox = None
        self.tracker = None
        
        print("服务端启动...")

    def decode_frame(self, buf):
        """解码JPEG为numpy图像"""
        np_arr = np.frombuffer(buf, dtype=np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    def init_tracker(self, frame, bbox):
        """
        初始化追踪器
        TODO: 在这里实现具体的追踪器初始化逻辑
        """
        self.init_bbox = tuple(bbox)

        # 这里应该初始化实际的追踪器
        self.tracker = TrackerDiMP_create()
        self.tracker.init(frame, self.init_bbox)

        self.tracker_initialized = True
        return True

    def update_tracker(self, frame):
        """
        更新追踪器
        TODO: 在这里实现具体的追踪更新逻辑
        """
        if self.tracker_initialized:
            # 这里应该调用实际的追踪器更新方法
            success, bbox = self.tracker.update(frame)

            if success and bbox is not None:
                # 绘制边界框
                x, y, w, h = [int(v) for v in bbox]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "DiMP", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "追踪失败", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

            # 临时模拟追踪区域更新
            # bbox = [x+1 for x in self.init_bbox]
            return bbox
        return None

    def handle_init_command(self, frame, msg):
        if frame is None:
            return {"status": "error", "msg": "failed to decode frame"}
        
        success = self.init_tracker(frame, msg["bbox"])
        if success:
            return {"status": "ok"}
        else:
            return {"status": "error", "msg": "failed to initialize tracker"}

    def handle_update_command(self, frame):
        if frame is None:
            return {"status": "error", "msg": "failed to decode frame"}
        
        bbox = self.update_tracker(frame)
        if bbox is not None:
            return {"status": "ok", "bbox": bbox}
        else:
            return {"status": "error", "msg": "tracker not initialized"}

    def run(self):
        
        while True:
            # multipart 接收: [json字符串, 图像二进制]
            meta_str, frame_buf = self.socket.recv_multipart()
            msg = json.loads(meta_str.decode("utf-8"))
            cmd = msg["cmd"]

            if cmd == "init":
                frame = self.decode_frame(frame_buf)
                response = self.handle_init_command(frame, msg)
                self.socket.send_json(response)

            elif cmd == "update":
                frame = self.decode_frame(frame_buf)
                response = self.handle_update_command(frame)
                self.socket.send_json(response)

                if frame is not None:
                    cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
                    cv2.imshow("frame", frame)
                    cv2.waitKey(1)

            else:
                self.socket.send_json({"status": "error", "msg": "unknown command"})


if __name__ == "__main__":
    server = TrackerServer()
    server.run()
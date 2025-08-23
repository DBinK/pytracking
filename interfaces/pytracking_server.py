import zmq
import cv2
import numpy as np
import json
import uuid

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from interfaces.cv_wrapper import TrackerDiMP_create


class TrackerServer:
    def __init__(self):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:5555")
        
        # 存储多个跟踪器实例，以会话ID为键
        self.trackers = {}
        
        print("服务端启动...")

    def decode_frame(self, buf):
        """解码JPEG为numpy图像"""
        np_arr = np.frombuffer(buf, dtype=np.uint8)
        return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    def create_session(self):
        """
        创建新的会话ID
        """
        session_id = str(uuid.uuid4())
        self.trackers[session_id] = {
            'tracker': None,
            'initialized': False,
            'bbox': None
        }
        return session_id

    def init_tracker(self, session_id, frame, bbox):
        """
        初始化追踪器
        """
        # 如果会话不存在，创建新会话
        if session_id not in self.trackers:
            self.trackers[session_id] = {
                'tracker': None,
                'initialized': False,
                'bbox': None
            }

        try:
            # 初始化实际的追踪器
            tracker = TrackerDiMP_create()
            tracker.init(frame, tuple(bbox))
            
            # 保存跟踪器状态
            self.trackers[session_id]['tracker'] = tracker
            self.trackers[session_id]['initialized'] = True
            self.trackers[session_id]['bbox'] = tuple(bbox)
            
            return True
        except Exception as e:
            print(f"初始化跟踪器失败: {e}")
            return False

    def update_tracker(self, session_id, frame):
        """
        更新追踪器
        """
        if session_id not in self.trackers or not self.trackers[session_id]['initialized']:
            return None

        try:
            # 调用实际的追踪器更新方法
            success, bbox = self.trackers[session_id]['tracker'].update(frame)

            cv2.namedWindow(session_id, cv2.WINDOW_NORMAL)
            if success and bbox is not None:
                # 绘制边界框（仅用于调试）
                x, y, w, h = [int(v) for v in bbox]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "DiMP", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
                cv2.imshow(session_id, frame)
                cv2.waitKey(1)

                # 更新保存的边界框
                self.trackers[session_id]['bbox'] = bbox
                return bbox
            else:
                cv2.putText(frame, "追踪失败", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

                # 显示帧（仅用于调试）
                cv2.imshow(session_id, frame)
                cv2.waitKey(1)

                return None
            

        except Exception as e:
            print(f"更新跟踪器失败: {e}")
            return None

    def release_tracker(self, session_id):
        """
        释放指定会话的跟踪器
        """
        if session_id in self.trackers:
            del self.trackers[session_id]
            return True
        return False

    def handle_init_command(self, frame, msg):
        if frame is None:
            return {"status": "error", "msg": "failed to decode frame"}
        
        session_id = msg.get("session_id")
        if not session_id:
            # 创建新的会话
            session_id = self.create_session()
        
        success = self.init_tracker(session_id, frame, msg["bbox"])
        if success:
            return {"status": "ok", "session_id": session_id}
        else:
            return {"status": "error", "msg": "failed to initialize tracker"}

    def handle_update_command(self, frame, msg):
        if frame is None:
            return {"status": "error", "msg": "failed to decode frame"}
        
        session_id = msg.get("session_id")
        if not session_id:
            return {"status": "error", "msg": "session_id is required"}
            
        bbox = self.update_tracker(session_id, frame)
        if bbox is not None:
            return {"status": "ok", "bbox": bbox}
        else:
            return {"status": "error", "msg": "tracker update failed"}

    def handle_release_command(self, msg):
        session_id = msg.get("session_id")
        if not session_id:
            return {"status": "error", "msg": "session_id is required"}
            
        success = self.release_tracker(session_id)
        if success:
            return {"status": "ok"}
        else:
            return {"status": "error", "msg": "failed to release tracker"}

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
                response = self.handle_update_command(frame, msg)
                self.socket.send_json(response)


            elif cmd == "release":
                response = self.handle_release_command(msg)
                self.socket.send_json(response)

            else:
                self.socket.send_json({"status": "error", "msg": "unknown command"})


if __name__ == "__main__":
    server = TrackerServer()
    server.run()
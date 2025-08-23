# server.py
import zmq
import cv2
import numpy as np
import pickle

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

print("服务端启动...")

tracker_initialized = False
init_bbox = None

while True:
    msg = socket.recv_json()
    cmd = msg["cmd"]

    if cmd == "init":
        # 初始化目标跟踪
        frame_data = bytes.fromhex(msg["frame"])
        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
        init_bbox = tuple(msg["bbox"])
        tracker_initialized = True

        # TODO: 在这里初始化你的真正 tracker
        
        socket.send_json({"status": "ok"})

    elif cmd == "update" and tracker_initialized:
        frame_data = bytes.fromhex(msg["frame"])
        frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
        # TODO: 在这里调用你的 tracker.update(frame)

        # 模拟一个返回 bbox
        h, w, _ = frame.shape
        bbox = (w//4, h//4, w//2, h//2)
        socket.send_json({"status": "ok", "bbox": bbox})

    else:
        socket.send_json({"status": "error", "msg": "tracker not initialized"})
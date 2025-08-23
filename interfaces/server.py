import zmq
import cv2
import numpy as np
import json

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

print("服务端启动...")

tracker_initialized = False
init_bbox = None

def decode_frame(buf):
    """解码JPEG为numpy图像"""
    np_arr = np.frombuffer(buf, dtype=np.uint8)
    return cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

cv2.namedWindow("追踪", cv2.WINDOW_NORMAL)

while True:
    # multipart 接收: [json字符串, 图像二进制]
    meta_str, frame_buf = socket.recv_multipart()
    msg = json.loads(meta_str.decode("utf-8"))
    cmd = msg["cmd"]

    if cmd == "init":
        frame = decode_frame(frame_buf)
        if frame is None:
            socket.send_json({"status": "error", "msg": "failed to decode frame"})
            continue
        init_bbox = tuple(msg["bbox"])
        bbox = init_bbox
        tracker_initialized = True

        # TODO: 初始化你的 tracker

        socket.send_json({"status": "ok"})

    elif cmd == "update" and tracker_initialized:
        frame = decode_frame(frame_buf)
        if frame is None:
            socket.send_json({"status": "error", "msg": "failed to decode frame"})
            continue

        # TODO: 调用 tracker.update(frame)

        bbox = [x+1 for x in bbox] # 模拟追踪区域更新, 每个数加1

        socket.send_json({"status": "ok", "bbox": bbox})

        # cv2.imshow("追踪", frame)
        # cv2.waitKey(1)

    else:
        socket.send_json({"status": "error", "msg": "tracker not initialized"})

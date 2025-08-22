
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cv2

from interfaces.cv_wrapper import TrackerDiMP_create

# 示例用法，类似于OpenCV的使用方式

# source="tmp/1.mp4"
source="tmp/2.mp4"
cap = cv2.VideoCapture(source)  # 或 0 表示摄像头

# 读取第一帧
ret, frame = cap.read()

if not ret:
    print("无法读取视频源")
    sys.exit(1)

# 手动选择跟踪目标区域 (x, y, w, h) - 与你的cvtracker.py保持一致
bbox_pytk = cv2.selectROI("Frame", frame, False)

# 创建追踪器
tracker_pytk = TrackerDiMP_create()
success = tracker_pytk.init(frame, bbox_pytk)

tracker_cv2 = cv2.TrackerCSRT_create()  # type: ignore
tracker_cv2.init(frame, bbox_pytk)

if not success:
    print("追踪器初始化失败")
    sys.exit(1)

cv2.namedWindow("tracker", cv2.WINDOW_NORMAL)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 更新追踪器
    success, bbox_pytk = tracker_pytk.update(frame)
    success, bbox_cv2 = tracker_cv2.update(frame)

    print(f"pytk: {bbox_pytk}, cv2: {bbox_cv2}")
    
    disp = frame.copy()

    if success and bbox_pytk is not None:
        # 绘制边界框
        x, y, w, h = [int(v) for v in bbox_pytk]
        cv2.rectangle(disp, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(disp, "DiMP", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)
    else:
        cv2.putText(disp, "追踪失败", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
    
    if success and bbox_cv2 is not None:
        # 绘制边界框
        x, y, w, h = [int(v) for v in bbox_cv2]
        cv2.rectangle(disp, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(disp, "cv2", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)
    else:
        cv2.putText(disp, "追踪失败", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 0, 0), 2)

    cv2.imshow("tracker", disp)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC键退出
        break

cap.release()
cv2.destroyAllWindows()
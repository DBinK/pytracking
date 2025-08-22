
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import cv2

from interfaces.cv_wrapper import TrackerDiMP_create

if __name__ == "__main__":
    # 示例用法，类似于OpenCV的使用方式
    
    source="tmp/1.mp4"
    cap = cv2.VideoCapture(source)  # 或 0 表示摄像头

    # 读取第一帧
    ret, frame = cap.read()

    if not ret:
        print("无法读取视频源")
        sys.exit(1)

    # 手动选择跟踪目标区域 (x, y, w, h) - 与你的cvtracker.py保持一致
    bbox = cv2.selectROI("Frame", frame, False)
    
    # 创建追踪器
    tracker = TrackerDiMP_create()
    success = tracker.init(frame, bbox)
    
    if not success:
        print("追踪器初始化失败")
        sys.exit(1)
    
    # cv2.namedWindow("追踪", cv2.WINDOW_NORMAL)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # 更新追踪器
        success, bbox = tracker.update(frame)
        print("追踪结果:", success, bbox)
        
        disp = frame.copy()
        if success and bbox is not None:
            # 绘制边界框
            x, y, w, h = [int(v) for v in bbox]
            cv2.rectangle(disp, (x, y), (x + w, y + h), (0, 255, 0), 2)
        else:
            cv2.putText(disp, "追踪失败", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        
        cv2.imshow("追踪", disp)

        if cv2.waitKey(1) & 0xFF == 27:  # ESC键退出
            break
    
    cap.release()
    cv2.destroyAllWindows()
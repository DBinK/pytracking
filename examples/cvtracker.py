import cv2

tracker = cv2.TrackerCSRT_create()
source="tmp/1.mp4"
cap = cv2.VideoCapture(source)  # 或 0 表示摄像头

# 读取第一帧
ret, frame = cap.read()

# 手动选择跟踪目标区域 (x, y, w, h)
bbox = cv2.selectROI("Frame", frame, False)
tracker.init(frame, bbox)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 更新追踪器
    success, bbox = tracker.update(frame)

    if success:
        # 画出追踪框
        x, y, w, h = map(int, bbox)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    else:
        cv2.putText(frame, "Tracking failed!", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,255),2)

    cv2.imshow("Tracking", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # 按 ESC 键退出
        break

cap.release()
cv2.destroyAllWindows()

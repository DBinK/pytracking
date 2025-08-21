import cv2 as cv  
import sys  
import os  
  
# 添加pytracking路径  
env_path = os.path.join(os.path.dirname(__file__), '..')  
if env_path not in sys.path:  
    sys.path.append(env_path)  
  
from pytracking.evaluation import Tracker  
  
def minimal_tracking_demo(video_path, initial_bbox, tracker_name="dimp", tracker_param="dimp50"):  
    """  
    最小跟踪演示  
    Args:  
        video_path: 视频文件路径  
        initial_bbox: 初始边界框 [x, y, width, height]  
        tracker_name: 跟踪器名称  
        tracker_param: 跟踪器参数  
    """  
    # 创建跟踪器  
    tracker = Tracker(tracker_name, tracker_param)  
      
    # 打开视频  
    cap = cv.VideoCapture(video_path)  
    ret, frame = cap.read()  
      
    if not ret:  
        print("无法读取视频")  
        return  
      
    # 初始化跟踪器  
    tracker_instance = tracker.create_tracker(tracker.get_parameters())  
    tracker_instance.initialize_features()  
      
    # 使用预定义的bbox初始化  
    init_info = {'init_bbox': initial_bbox}  
    tracker_instance.initialize(frame, init_info)  
      
    frame_idx = 0  
    while True:  
        ret, frame = cap.read()  
        if not ret:  
            break  
              
        # 跟踪  
        if frame_idx > 0:  
            out = tracker_instance.track(frame, {})  
            bbox = out['target_bbox']  
              
            # 绘制边界框  
            x, y, w, h = [int(v) for v in bbox]  
            cv.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  
        else:  
            # 绘制初始边界框  
            x, y, w, h = initial_bbox  
            cv.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  
          
        # 显示结果  
        cv.imshow('Tracking', frame)  
        if cv.waitKey(1) & 0xFF == ord('q'):  
            break  
              
        frame_idx += 1  
      
    cap.release()  
    cv.destroyAllWindows()  
  
# 使用示例  
if __name__ == "__main__":  
    # 预定义的边界框 [x, y, width, height]  
    predefined_bbox = [100, 100, 50, 50]  # 根据您的需求修改  
    camera_id = "http://192.168.50.244:4747/video"
    minimal_tracking_demo(camera_id, predefined_bbox)
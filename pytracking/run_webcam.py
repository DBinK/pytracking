import os
import sys
import argparse

env_path = os.path.join(os.path.dirname(__file__), '..')
if env_path not in sys.path:
    sys.path.append(env_path)

from pytracking.evaluation import Tracker


def run_webcam(tracker_name, tracker_param, debug=None, visdom_info=None, camera_id=0):
    """Run the tracker on your webcam.
    args:
        tracker_name: Name of tracking method.
        tracker_param: Name of parameter file.
        debug: Debug level.
        visdom_info: Dict optionally containing 'use_visdom', 'server' and 'port' for Visdom visualization.
        camera_id: ID of the camera to use (default is 0)
    """
    visdom_info = {} if visdom_info is None else visdom_info
    tracker = Tracker(tracker_name, tracker_param)
    # Pass camera_id to run_video_generic
    tracker.run_video_generic(debug=debug, visdom_info=visdom_info, camera_id=camera_id)


def main():
    parser = argparse.ArgumentParser(description='Run the tracker on your webcam.')
    parser.add_argument('tracker_name', type=str, help='Name of tracking method.')
    parser.add_argument('tracker_param', type=str, help='Name of parameter file.')
    parser.add_argument('--debug', type=int, default=0, help='Debug level.')
    parser.add_argument('--use_visdom', type=bool, default=True, help='Flag to enable visdom')
    parser.add_argument('--visdom_server', type=str, default='127.0.0.1', help='Server for visdom')
    parser.add_argument('--visdom_port', type=int, default=8097, help='Port for visdom')
    parser.add_argument('--camera_id', type=int, default=0, help='ID of the camera to use (default is 0)')

    args = parser.parse_args()

    visdom_info = {'use_visdom': args.use_visdom, 'server': args.visdom_server, 'port': args.visdom_port}
    # run_webcam(args.tracker_name, args.tracker_param, args.debug, visdom_info, args.camera_id)
    camera_id = "http://192.168.50.244:4747/video"
    run_webcam(args.tracker_name, args.tracker_param, args.debug, visdom_info, camera_id)


if __name__ == '__main__':
    main()
import cv2
import argparse
import os
import sys


def parse_args(input, output):
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Process pic')
    parser.add_argument('--input', help='video to process', dest='input', default=None, type=str)
    parser.add_argument('--output', help='pic to store', dest='output', default=None, type=str)
    # default为间隔多少帧截取一张图片
    parser.add_argument('--skip_frame', dest='skip_frame', help='skip number of video', default=1, type=int)
    # input为输入视频的路径 ，output为输出存放图片的路径
    args = parser.parse_args(['--input', input, '--output', output])
    return args


def process_video(i_video, o_video, num):
    cap = cv2.VideoCapture(i_video)
    num_frame = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    expand_name = '.jpg'
    if not cap.isOpened():
        print("Please check the path.")
    cnt = 0
    count = 0
    while 1:
        ret, frame = cap.read()
        cnt += 1
        #  how
        # many
        # frame
        # to
        # cut
        if (cnt % num == 0) and frame is not None:
            count += 1
            # resize
            #frame = cv2.resize(frame, dsize=(0, 0), dst=None, fx=0.7, fy=0.7, interpolation=cv2.INTER_LINEAR)
            cv2.imwrite(os.path.join(o_video, str(count).zfill(4) + expand_name), frame)

        if not ret:
            break


if __name__ == '__main__':
    args = parse_args(sys.argv[1], sys.argv[2])
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    print('Called with args:')
    print(args)
    process_video(args.input, args.output, args.skip_frame)

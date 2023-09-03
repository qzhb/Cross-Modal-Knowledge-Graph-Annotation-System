import re
import math
import os
import cv2
import json
import zmq
import numpy 
from PIL import Image, ImageFont, ImageDraw

import progressbar
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

img_prefix = ['png', 'jpg', 'jpeg']
webvtt_prefix = ['webvtt']


def ImgAddText(img,text,left,top,textColor,textSize):
    if(isinstance(img,numpy.ndarray)):
        img=Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontStyle = ImageFont.truetype('simsun.ttc',textSize,encoding='utf-8')
    draw.text((left,top),text,textColor,font=fontStyle)
    return cv2.cvtColor(numpy.asarray(img),cv2.COLOR_RGB2BGR)

def read_images(img_path,data_path,json_path,save_path):

    files = os.listdir(img_path)
    portion = 0
    total = len(files)
    files.sort(key= lambda x: int(x[:-4]))

    ProgressBar = progressbar.ProgressBar(portion, total)
    ProgressBar.setModal(True)
    ProgressBar.setWindowModality(Qt.ApplicationModal)
    ProgressBar.show()

    webvtt = read_webvtt(data_path)
    res = parse_webvtt(os.path.join(data_path, webvtt))
    # txt_object_file = save_data(os.path.join(data_path, "object_data.txt"))

    for file in files:
        index = file.find(".")
        prefix = file[index + 1:]
        if prefix in img_prefix:
            # draw_images(img_path, file[:index], txt_object_file, json_path, save_path,res)
            draw_images(img_path, file[:index], json_path, save_path, res)
            portion += 1
            ProgressBar.setValue(portion)  # 更新进度条的值
            QApplication.processEvents()  # 实时显示

#def draw_images(path, img_name, txt_object_file, data_path,save_path,res):
def draw_images(path, img_name, data_path, save_path, res):

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")

    img_number = int(img_name)
    img_path = os.path.join(path, img_name + ".jpg")
    img_save_path = os.path.join(save_path, img_name + ".jpg")

    img = cv2.imread(img_path)

    # line_object = txt_object_file[int(img_name)]

    # objects_list = line_object.rstrip().split(",")

    # 假如没有标注信息就利用前面的关键帧的标注
    if not os.path.exists(data_path+img_name+'.json'):
        key = str(img_number-(img_number-1)%6).zfill(4)
    else:
        key = img_name

    # f = open(data_path+img_name+'.json','r')
    f = open(data_path + key + '.json', 'r')
    data = json.load(f)
    f.close()
    # for j in range(len(data['shapes'])):
    #     if data['shapes'][j]['shape_type'] != 'rectangle':
    #         data['shapes'][j]['shape_type'] = 'rectangle'
    #         points = data['shapes'][j]['points']
    #         x1 = data['imageWidth']
    #         y1 = data['imageHeight']
    #         x2 = 0
    #         y2 = 0
    #         for tmp in points:
    #             if x1>int(tmp[0]):
    #                 x1 = int(tmp[0])
    #             if y1>int(tmp[1]):
    #                 y1 = int(tmp[1])
    #             if x2<int(tmp[0]):
    #                 x2 = int(tmp[0])
    #             if y2<int(tmp[1]):
    #                 y2 = int(tmp[1])
    #         points = [[x1,y1],[x2,y2]]
    #     else:
    #         x1 = int(data['shapes'][j]['points'][0][0])
    #         y1 = int(data['shapes'][j]['points'][0][1])
    #         x2 = int(data['shapes'][j]['points'][1][0])
    #         y2 = int(data['shapes'][j]['points'][1][1])
    #         x3 = min(x1, x2)
    #         x4 = max(x1, x2)
    #         y3 = min(y1, y2)
    #         y4 = max(y1, y2)
    #         points = [[x3,y3],[x4,y4]]
    #     if points[0][0]<0:
    #         points[0][0]=0
    #     if points[0][1]<0:
    #         points[0][1]=0
    #     if points[1][0]>data['imageWidth']:
    #         points[1][0]=data['imageWidth']
    #     if points[1][1]>data['imageHeight']:
    #         points[1][1]=data['imageHeight']
    #     data['shapes'][j]['points'] = points
    # f = open(data_path+img_name+'.json','w')
    # json.dump(data,f,indent=2)
    # f.close()
    # f = open(data_path + img_name + '.json', 'r')
    # data = json.load(f)
    shapes = data['shapes']
    if os.path.exists(data_path+key+'.txt'):
        f = open(data_path+key+'.txt','r')
        emotions = f.readlines()
        f.close()
        for j in range(len(shapes)):
            x1 = int(shapes[j]['points'][0][0])
            y1 = int(shapes[j]['points'][0][1])
            x2 = int(shapes[j]['points'][1][0])
            y2 = int(shapes[j]['points'][1][1])
            label = shapes[j]['label']
            if x1>x2:
                x1,x2 = x2,x1
            if y1>y2:
                y1,y2 = y2,y1
            emotion = emotions[j].split('\n')[0]
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
            img = ImgAddText(img,label,x1-20,y1-20,(255,0,0),35)
            img = ImgAddText(img,emotion,x1-20,y1-40,(0,255,0),25)
            #cv2.putText(img, label, (x1, y1 - 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            #cv2.putText(img, emotion, (x1, y1 - 33), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        f2 = open(data_path+key+'.txt','w')
        for j in range(len(shapes)):
            x1 = int(shapes[j]['points'][0][0])
            y1 = int(shapes[j]['points'][0][1])
            x2 = int(shapes[j]['points'][1][0])
            y2 = int(shapes[j]['points'][1][1])
            label = shapes[j]['label']
            # 截取人脸
            if x1>x2:
                x1,x2 = x2,x1
            if y1>y2:
                y1,y2 = y2,y1
            cropped = img[y1:y2, x1:x2]
            cv2.imwrite('Face/CROPPED_FACE.jpg', cropped)
            # 表情识别
            command = 'Start'
            socket.send(command.encode())
            message = socket.recv()
            STR = repr(message)
            emotion = STR.split('\'')[1]
            if j != len(shapes)-1 :
                f2.write(emotion+'\n')
            else:
                f2.write(emotion)

            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
            img = ImgAddText(img,label,x1-20,y1-20,(255,0,0),35)
            img = ImgAddText(img,emotion,x1-20,y1-40,(0,255,0),25)
            #cv2.putText(img, label, (x1, y1-2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            #cv2.putText(img, emotion, (x1, y1 - 33), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        f2.close()

        # i = 0
        # while i <= len(objects_list) - 5:
        #     x1 = int(objects_list[i])
        #     y1 = int(objects_list[i + 1])
        #     x2 = int(objects_list[i + 2])
        #     y2 = int(objects_list[i + 3])
        #     if objects_list[i + 4] != "person":
        #         cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 3)
        #         cv2.putText(img, objects_list[i + 4], (x1, y1-2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
        #     i = i + 5

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imwrite(img_save_path, img)

    for i in range(len(res)):
        t1 = math.floor(res[i][0] / 1000 * 23)
        t2 = math.ceil(res[i][1] / 1000 * 23)

        if img_number in range(t1, t2):
            img = Image.open(img_save_path)
            draw = ImageDraw.Draw(img)
            ttfont = ImageFont.truetype('simsun.ttc', size=50)
            width = img.size[0]
            height = img.size[1]
            x1 = int(width * 0.01);
            y1 = int(height * 0.7);
            j = 2
            while j < len(res[i]):
                line = res[i][j]
                offsetx, offsety = ttfont.getoffset(line)
                width, height = ttfont.getsize(line)
                draw.rectangle((offsetx + x1, offsety + y1, offsetx + x1 + width, offsety + y1 + height+3), fill='black')
                draw.text((x1 + 10, y1 + 5), line, fill=(255, 255, 255), font=ttfont)
                y1 += height
                j += 1
            img.save(img_save_path)

def save_data(data_path):
    txt_file = {}

    with open(data_path, "r") as fin:
        count = 1
        for line in fin:
            txt_file[count] = line
            count += 1

    return txt_file

def time_stamp2time(x):
    time_list = [str(i) for i in x.split(' --> ')]
    time_list1_1 = [x for x in time_list[0].split(':')]
    time_list1_2 = [int(x) for x in time_list1_1[2].split('.')]
    time_list1_1.pop()

    time_list2_1 = [x for x in time_list[1].split(':')]
    time_list2_2 = [int(x) for x in time_list2_1[2].split('.')]
    time_list2_1.pop()

    # 解析出对应的时间戳（相对于时间0)
    t1 = int(time_list1_1[0]) * 60 * 60 * 1000 + int(time_list1_1[1]) * 60 * 1000 + time_list1_2[0] * 1000 + \
         time_list1_2[1]
    t2 = int(time_list2_1[0]) * 60 * 60 * 1000 + int(time_list2_1[1]) * 60 * 1000 + time_list2_2[0] * 1000 + \
         time_list2_2[1]
    return t1, t2


def parse_webvtt(file_path):
    # 打开字幕文件
    count = -1;
    res = []
    with open(file_path, 'r') as f1:
        for line in f1:
            if line != '\n':
                if re.match(r'\d{1,2}:\d{1,2}:\d{1,2}.\d{1,3} --> \d{1,2}:\d{1,2}:\d{1,2}.\d{3}', line):
                    count += 1
                    line = line.strip()
                    time_stamp1 = line
                    t1, t2 = time_stamp2time(time_stamp1)
                    res = res + [[t1, t2]]
                else:
                    # TODO 去掉更多的标签 maybe <b></b>...?
                    line = line.replace('<i>', '');
                    line = line.replace('</i>', '');
                    line.replace('\n', '')
                    if count >= 0:
                        res[count] += [line]

    return res


def read_webvtt(webvtt_path):
    files = os.listdir(webvtt_path)
    for file in files:
        if re.match(r'.*webvtt', file):
            return file


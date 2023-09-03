import sys
import argparse
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow

from example import Ui_Form
from PyQt5.QtCore import *
import os
import time
import zmq

class myWidget(Ui_Form,QWidget):

    def __init__(self,pic_dir):
        super(Ui_Form,self).__init__()
        self.setupUi(self)

        self.pic_dir = pic_dir    # 存放人脸底库的文件夹
        while not os.path.exists(self.pic_dir):
            time.sleep(0.5)
        character_list_ori = os.listdir(self.pic_dir)
        self.character_list = sorted(character_list_ori)
        for i in self.character_list:
            self.label_list.addItem(i.split('.jpg')[0])
        self.label_list.setCurrentIndex(-1)

        self.label_list.currentIndexChanged.connect(self.showpic)
        self.delete_button.clicked.connect(self.delete_pic)

        self.timer = QTimer()
        self.timer.start(1000)
        self.timer.timeout.connect(self.operate)

    def update_list(self):
        character_list_ori = os.listdir(self.pic_dir)
        character_list_new = sorted(character_list_ori)
        if self.character_list == character_list_new:
            return
        self.label_list.clear()
        self.character_list = character_list_new
        for i in self.character_list:
            self.label_list.addItem(i.split('.jpg')[0])
        self.label_list.setCurrentIndex(0)

    def operate(self):
        path = os.getcwd()+'/show_example/update_Y.txt'
        path_new = os.getcwd() + '/show_example/update_N.txt'
        if not os.path.exists(path):
            return
        f = open(path)
        list = f.readlines()
        filename = self.pic_dir+'/'+list[0].split('\n')[0] +'.jpg'
        self.label1.setText(list[0].split('\n')[0].split('%')[0])
        self.show_image(filename,self.pic1)
        filename = self.pic_dir+'/'+list[1].split('\n')[0] + '.jpg'
        self.label2.setText(list[1].split('\n')[0].split('%')[0])
        self.show_image(filename, self.pic2)
        filename = self.pic_dir+'/'+list[2].split('\n')[0] + '.jpg'
        self.label3.setText(list[2].split('\n')[0].split('%')[0])
        self.show_image(filename, self.pic3)
        filename = self.pic_dir+'/'+list[3].split('\n')[0] + '.jpg'
        self.label4.setText(list[3].split('\n')[0].split('%')[0])
        self.show_image(filename, self.pic4)
        filename = self.pic_dir+'/'+list[4].split('\n')[0] + '.jpg'
        self.label5.setText(list[4].split('\n')[0].split('%')[0])
        self.show_image(filename, self.pic5)
        os.rename(path,path_new)
        self.update_list()

    def showpic(self):
        path = self.pic_dir+'/'+self.label_list.currentText()+'.jpg'
        self.show_image(path,self.pic_list)

    def show_image(self,path,label):
        if not os.path.exists(path):
            return
        image = QImage(path)
        width = label.width()
        height = label.height()
        w = image.width()
        h = image.height()
        if width/height < w/h:
            w_new = width
            h_new = h/w * w_new
        else:
            h_new = height
            w_new = w/h * h_new
        pixmap = QPixmap.fromImage(image).scaled(w_new,h_new, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(pixmap)
        #label.setScaledContents(True)

    def delete_pic(self):
        # 通信
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5558")
        path = self.pic_dir + '/' + self.label_list.currentText() + '.jpg'
        os.remove(path)
        command = 'a '+ self.pic_dir + '/' +' 2 '
        socket.send(command.encode())
        self.update_list()

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pic', help='show the dir of the pictures')
    args = parser.parse_args()
    pic_dir = args.pic
    app = QApplication(sys.argv)
    m = myWidget(pic_dir=pic_dir)
    m.show()
    sys.exit(app.exec_())

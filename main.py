#_*_encoding:utf-8_*_
import sys
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

import draw
import warning
from gui import Ui_MainWindow
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import *
import os
import split
from data_management import DataManagement
from multiprocessing import Process
from visualize import visualize
import time

class myMainWindow(Ui_MainWindow, QMainWindow):

    def __init__(self):

        super(Ui_MainWindow, self).__init__()
        self.setupUi(self)

        # 全局变量地址
        self.annotation_global_path = None

        # 性别
        # self.sex_box.addItems(['male','female','其它'])
        self.sex_box.addItems(['男', '女', '其它'])
        self.sex_box.setCurrentIndex(-1)

        # 年龄
        # self.age_box.addItems(['baby','schoolchild','teenager','adult','middle-aged','old'])
        self.age_box.addItems(['婴儿', '儿童', '青少年', '成年', '中年', '老年'])
        self.age_box.setCurrentIndex(-1)

        self.pic_num = 0
        self.max_pic_num = 0
        self.ahead_or_back = True
        self.timer = QTimer()
        self.timer_save = QTimer()
        self.timer.timeout.connect(self.operate)
        self.timer_save.timeout.connect(self.save_all)
        self.button_start.clicked.connect(self.start)
        self.button_stop.clicked.connect(self.stop)
        self.button_ahead.clicked.connect(self.ahead)
        self.button_back.clicked.connect(self.back)
        self.button_loadvideo.clicked.connect(self.openfile)
        self.button_relabel.clicked.connect(self.label)
        self.Slider.valueChanged.connect(self.slider)
        self.button_save.clicked.connect(self.save_all)
        self.button_next.clicked.connect(self.nextvideo)

        self.story_input.setDisabled(True)
        self.story_reference.setDisabled(True)

        self.data_signals()

    # 进度条拖动
    def slider(self):
        self.pic_num = self.Slider.value()
        self.time.setText(str(self.pic_num))
        self.show_img(str(self.pic_num))

    # 显示图片
    def operate(self):
        if self.ahead_or_back:
            self.pic_num = self.pic_num + 1
        else:
            self.pic_num = self.pic_num - 1
        if self.pic_num < 1 or self.pic_num > self.max_pic_num:
            self.timer.stop()
            return
        self.time.setText(str(self.pic_num))
        self.show_img(str(self.pic_num))
        self.Slider.setValue(self.pic_num)

    def graph_show(self):
        # self.data.graph_data_visualization(self.annotation_path)
        self.graph_path = self.annotation_path + 'graph_data_visualization.png'
        visualize(self.data, self.graph_path)
        img = QtGui.QImage(self.graph_path)
        png = QtGui.QPixmap.fromImage(img).scaled(self.graph.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.graph.setPixmap(png)

    def show_img(self, img_name):
        # 调用QtGui.QPixmap方法，打开一个图片，存放在变量png中
        img = QtGui.QImage(os.path.join(self.drawpath, img_name.zfill(4)))
        png = QtGui.QPixmap.fromImage(img).scaled(self.display.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        # 在l1里面，调用setPixmap命令，建立一个图像存放框，并将之前的图像png存放在这个框框里。
        self.display.setPixmap(png)
        #self.display.setScaledContents(True)
        # ui.pic.setPixmap(QPixmap(""))
        # 显示整个窗口
        # self.display.show()

    def start(self):
        self.ahead_or_back = True
        self.timer.start(43.48)

    def stop(self):
        self.timer.stop()

    def ahead(self):
        self.ahead_or_back = True
        self.timer.start(21.74)

    def back(self):
        self.ahead_or_back = False
        self.timer.start(21.74)

    def openfile(self):

        self.timer_save.stop()

        file_name, file_type = QFileDialog.getOpenFileName(self, "选取文件", "./",
                                                           "All Files (*);;Video Files (*.mkv)")  # 设置文件扩展名过滤,注意用双分号间隔
        if not file_name:
            return
        self.file_path = os.path.dirname(file_name)
        self.video_name = self.file_path.split('/')[-1]  #clip名
        self.movie_name = self.file_path.split('/')[-2]  #电影名
        self.db = os.getcwd() + '/annotation_results/Face_data/' + self.movie_name + '_DB'

        gui.setWindowTitle('annotation system:  '+self.movie_name+'  '+self.video_name)

        self.annotation_global_path = './annotation_results/global_data/'
        if not os.path.exists(self.annotation_global_path):
            if not os.path.exists('./annotation_results'):
                os.mkdir('./annotation_results')
            os.system('cp -r data/global_data annotation_results/global_data')

        self.annotation_path = './annotation_results/annotation_data/'+self.movie_name+'/'+self.video_name+'/'
        self.json_path = self.annotation_path+'json/'

        if os.path.exists(self.annotation_global_path):
            self.data = DataManagement(self.annotation_global_path)
        else:
            self.data = DataManagement()

        if os.path.exists(self.annotation_path):
            self.data.load_nodes_and_links(self.annotation_path)
        else:
            os.makedirs(self.annotation_path)
            self.data.save_nodes_and_links(self.annotation_path)

        # create directory
        if self.video_name is not None:
            self.path = './annotation_results/movie_clip_frames/' + self.movie_name + '/'+self.video_name + '/ori/'
            self.labelme_path = './annotation_results/movie_clip_frames/' + self.movie_name + '/'+self.video_name + '/key/'
            self.drawpath = './annotation_results/movie_clip_frames/' + self.movie_name + '/'+self.video_name + '/processed/'

        if not os.path.exists(self.path):
            os.makedirs(self.path)
            os.makedirs(self.labelme_path)
            os.makedirs(self.drawpath)
            # process video
            args = split.parse_args(file_name, self.path)
            split.process_video(args.input, args.output, args.skip_frame)

            # 选取视频的关键帧
            pictures = os.listdir(self.path)
            pictures = sorted(pictures)
            for i in range(len(pictures)):
                if i % 6 == 0:
                    os.system('cp '+self.path+pictures[i] + ' '+self.labelme_path+pictures[i])

            self.label()

            img_prefix = ['png', 'jpg', 'jpeg']
            files = os.listdir(self.path)
            self.pic_num = 0
            self.max_pic_num = 0
            for file in files:
                index = file.find(".")
                prefix = file[index + 1:]
                if prefix in img_prefix:
                    self.max_pic_num = self.max_pic_num + 1
            # print(self.path)
        else:
            self.pic_num = 0
            self.max_pic_num = len(os.listdir(self.path))

        self.data_IO()

        self.Slider.setMaximum(self.max_pic_num-1)
        self.Slider.setMinimum(1)
        self.Slider.setValue(1)
        self.show_img(str(1))

        self.scene_display.setText(self.data.scene)

        self.event_box.setCurrentIndex(-1)
        self.event_box.setCurrentText(self.data.event)
        if self.event_box.currentIndex()==-1:
            self.event_box.setCurrentText('其它')
            self.event_input.setEnabled(True)
            self.event_input.setText(self.data.event)

        self.story_input.setPlainText(self.data.plot)

        self.timer_save.start(60000)

    # 调用labelme软件修正bounding box及其标签
    def label(self):
        if self.annotation_global_path == None:
            return
        command1 = 'python3 labelme.py ' + self.labelme_path + ' --output ' + os.getcwd() +'/annotation_results/annotation_data/'+self.movie_name+'/'+self.video_name+'/json/ ' + '--autosave --labels ' + self.file_path + '/character_list.txt'
        p1 = Process(target=self.run_sh, args=(command1,))
        command2 = 'python3 show_example/show_example.py --pic ' + self.db
        p2 = Process(target=self.run_sh, args=(command2,))
        p1.start()
        p2.start()
        Warning_dialog = warning.myDialog()
        Warning_dialog.setWindowModality(Qt.ApplicationModal)
        Warning_dialog.show()
        while p1.is_alive() == True:
            while p2.is_alive() == True:
                Warning_dialog.confirm.setDisabled(True)
                QApplication.processEvents()
                time.sleep(0.1)
        Warning_dialog.close()
        os.system('rm -rf '+self.drawpath)
        os.mkdir(self.drawpath)
        draw.read_images(self.path, self.file_path,self.json_path, self.drawpath)

    def run_sh(self,command):
        os.system(command)

    # 各种信号
    def data_signals(self):
        self.scene_box.currentIndexChanged.connect(self.scene_set)

        self.event_box.currentIndexChanged.connect(self.event_set)

        self.characters_save.clicked.connect(self.characterssave)
        self.characters_delete.clicked.connect(self.charactersdelete)

        # self.objects_box.currentIndexChanged.connect(self.objects_set)
        # self.objects_save.clicked.connect(self.objectssave)
        # self.objects_delete.clicked.connect(self.objectsdelete)

        self.actions_save.clicked.connect(self.actionssave)
        self.actions_box.currentIndexChanged.connect(self.actions_set)
        self.actions_delete.clicked.connect(self.actionsdelete)
        self.actions_list_human_box.currentIndexChanged.connect(self.actions_update)

        self.expressions_save.clicked.connect(self.expressionssave)
        self.expressions_box.currentIndexChanged.connect(self.expressions_set)
        self.expressions_delete.clicked.connect(self.expressionsdelete)
        self.expressions_list_human_box.currentIndexChanged.connect(self.expressions_update)

        self.relation_HH_box.currentIndexChanged.connect(self.relationHHset)
        self.relation_HH_save.clicked.connect(self.relationHHsave)
        self.relation_HH_delete.clicked.connect(self.relationHHdelete)

        # self.relation_HO_box.currentIndexChanged.connect(self.relationHOset)
        # self.relation_HO_save.clicked.connect(self.relationHOsave)
        # self.relation_HO_delete.clicked.connect(self.relationHOdelete)

        self.interaction_box.currentIndexChanged.connect(self.interactionset)
        self.interaction_save.clicked.connect(self.interactionsave)
        self.interaction_delete.clicked.connect(self.interactiondelete)

        self.scene_input.textEdited['QString'].connect(self.scene_display.setText)

    # 数据的输入输出
    def data_IO(self):
        # 场景
        self.scene_box.clear()
        f = open(self.file_path + '/scene_list.txt')
        scene_list = f.readlines()
        scene_list = sorted(scene_list)
        for i in range(len(scene_list)):
            item = scene_list[i].split('\n')[0]
            if item != '':
                self.scene_box.addItem(item)
        f.close()
        self.scene_box.addItem("其它")
        self.scene_box.setCurrentIndex(-1)
        self.scene_input.setDisabled(True)

        # 事件
        self.event_box.clear()
        self.event_input.setDisabled(True)
        f = open(self.file_path+ '/event_list.txt')
        event_list = f.readlines()
        event_list = sorted(event_list)
        for i in range(len(event_list)):
            item = event_list[i].split('\n')[0]
            self.event_box.addItem(item)
        f.close()
        self.event_box.addItem('其它')
        self.event_box.setCurrentIndex(-1)

        # 剧情
        self.story_reference.clear()
        f = open(self.file_path + '/story_reference.txt')
        story_reference = f.readlines()[0]
        f.close()
        self.story_reference.setDisabled(True)
        self.story_reference.setPlainText(story_reference)
        self.story_input.clear()
        self.story_input.setEnabled(True)

        # 角色
        self.character_update()
        character_list_ori = os.listdir(self.db)
        character_list = []
        for i in character_list_ori:
            character_list.append(i.split('.jpg')[0].split('%')[0])
        character_list.append('Passerby')
        character_list_sorted = sorted(list(set(character_list)))
        self.name_input.addItems(character_list_sorted)
        self.name_input.setCurrentIndex(-1)

        # 物体
        # self.objects_update()
        # self.objects_box.clear()
        # f = open(self.file_path + '/object_list.txt')
        # objects_list = f.readlines()
        # objects_list_sorted = sorted(objects_list)
        # for i in range(len(objects_list_sorted)):
        #     item = objects_list_sorted[i].split('\n')[0]
        #     if item != 'person':
        #         self.objects_box.addItem(item)
        # f.close()
        # self.objects_box.addItem('其它')
        # self.objects_box.setCurrentIndex(-1)
        # self.objects_input.setDisabled(True)

        # 动作
        self.actions_box.clear()
        f = open(self.file_path + '/action_list.txt')
        actions_list = f.readlines()
        actions_list = sorted(list(set(actions_list)))
        for i in range(len(actions_list)):
            item = actions_list[i].split('\n')[0]
            self.actions_box.addItem(item)
        f.close()
        self.actions_box.addItem('其它')
        self.actions_box.setCurrentIndex(-1)

        # 表情
        self.expressions_box.clear()
        f = open(self.file_path + '/expression_list.txt')
        expressions_list = f.readlines()
        expressions_list = sorted(list(set(expressions_list)))
        for i in range(len(expressions_list)):
            item = expressions_list[i].split('\n')[0]
            self.expressions_box.addItem(item)
        f.close()
        self.expressions_box.addItem('其它')
        self.expressions_box.setCurrentIndex(-1)

        # 人人关系
        self.relationHH_update()
        self.relationHH_list_update()

        # 人物关系
        # self.relationHO_update()
        # self.relationHO_list_update()

        # 人人交互
        self.interaction_update()
        self.interaction_list_update()

    # 场景设置
    def scene_set(self):
        if self.scene_box.currentText() == '其它':
            self.scene_display.clear()
            self.scene_input.setEnabled(True)
        else:
            self.scene_input.clear()
            self.scene_input.setDisabled(True)
            self.scene_display.setText(self.scene_box.currentText())

    # 场景存储
    def scenesave(self):
        self.data.scene = self.scene_display.text()

    # 事件设置
    def event_set(self):
        if self.event_box.currentText() == '其它':
            self.event_input.setEnabled(True)
        else:
            self.event_input.clear()
            self.event_input.setDisabled(True)

    # 事件存储
    def eventsave(self):
        if self.event_box.currentText() == '其它':
            self.data.event = self.event_input.text()
        else:
            self.data.event = self.event_box.currentText()

    # 剧情存储
    def storysave(self):
        self.data.plot = self.story_input.toPlainText()

    # 角色存储
    def characterssave(self):
        if self.name_input.currentText() == 'Passerby':
            i = 1
            name = 'Passerby'+str(i)
            while self.data.get_characters().__contains__(name):
                i += 1
                name = 'Passerby' + str(i)
        else:
            name = self.name_input.currentText()
        self.data.add_character_node(name, self.sex_box.currentText(),self.age_box.currentText())
        self.name_input.setCurrentIndex(-1)
        self.age_box.setCurrentIndex(-1)
        self.sex_box.setCurrentIndex(-1)
        self.character_update()
        self.save_all()

    # 角色list更新
    def character_update(self):
        self.characters_box.clear()
        self.characters_box.addItems(self.data.get_characters())
        self.characters_box.setCurrentIndex(-1)
        self.actions_human_box.clear()
        self.actions_human_box.addItems(self.data.get_characters())
        self.actions_human_box.setCurrentIndex(-1)
        self.expressions_human_box.clear()
        self.expressions_human_box.addItems(self.data.get_characters())
        self.expressions_human_box.setCurrentIndex(-1)
        self.human1_box.clear()
        self.human1_box.addItems(self.data.get_characters())
        self.human1_box.setCurrentIndex(-1)
        self.human2_box.clear()
        self.human2_box.addItems(self.data.get_characters())
        self.human2_box.setCurrentIndex(-1)
        # self.human_box.clear()
        # self.human_box.addItems(self.data.get_characters())
        # self.human_box.setCurrentIndex(-1)
        self.human3_box.clear()
        self.human3_box.addItems(self.data.get_characters())
        self.human3_box.setCurrentIndex(-1)
        self.human4_box.clear()
        self.human4_box.addItems(self.data.get_characters())
        self.human4_box.setCurrentIndex(-1)
        self.actions_list_human_box.clear()
        self.actions_list_human_box.addItems(self.data.get_characters())
        self.actions_list_human_box.setCurrentIndex(-1)
        self.expressions_list_human_box.clear()
        self.expressions_list_human_box.addItems(self.data.get_characters())
        self.expressions_list_human_box.setCurrentIndex(-1)
        self.relationHH_list_update()
        # self.relationHO_list_update()
        self.interaction_list_update()

    # 角色删除
    def charactersdelete(self):
        self.data.delete_character_node(self.characters_box.currentText())
        self.character_update()
        self.save_all()

    # 物体设置
    # def objects_set(self):
    #     if self.objects_box.currentText() == '其它':
    #         self.objects_input.setEnabled(True)
    #     else:
    #         self.objects_input.setDisabled(True)

    # 物体存储
    # def objectssave(self):
    #     if self.objects_box.currentText() == '其它':
    #         category = self.objects_input.text()
    #     else:
    #         category = self.objects_box.currentText()
    #     self.data.add_object_node(category)
    #     self.objects_input.clear()
    #     self.objects_input.setDisabled(True)
    #     self.objects_box.setCurrentIndex(-1)
    #     self.objects_update()
    #     self.save_all()

    # 物体list更新
    # def objects_update(self):
    #     self.objects_list.clear()
    #     self.objects_list.addItems(self.data.get_objects())
    #     self.objects_list.setCurrentIndex(-1)
    #     self.object_box.clear()
    #     self.object_box.addItems(self.data.get_objects())
    #     self.object_box.setCurrentIndex(-1)
    #     self.relationHO_list_update()

    # 物体删除
    # def objectsdelete(self):
    #     self.data.delete_object_node(self.objects_list.currentText())
    #     self.objects_update()
    #     self.save_all()

    # 动作设置
    def actions_set(self):
        if self.actions_box.currentText() == '其它':
            self.action_input.setEnabled(True)
        else:
            self.action_input.clear()
            self.action_input.setDisabled(True)

    # 动作存储
    def actionssave(self):
        if self.actions_box.currentText() == '其它':
            action = self.action_input.text()
        else:
            action = self.actions_box.currentText()
        time_interval = (int(self.time_start_actions_input.text()),int(self.time_end_actions_input.text()))
        self.data.add_action(self.actions_human_box.currentText(),action,time_interval)
        self.actions_box.setCurrentIndex(-1)
        self.action_input.clear()
        self.actions_human_box.setCurrentIndex(-1)
        self.time_start_actions_input.clear()
        self.time_end_actions_input.clear()
        self.actions_update()
        self.save_all()

    # 动作list更新
    def actions_update(self):
        self.actions_list.clear()
        if self.actions_list_human_box.currentIndex() != -1 :
            actionlist = self.data.get_actions(self.actions_list_human_box.currentText())
            action_list = []
            for i in range(len(actionlist)):
                tmp = str(actionlist[i][0])+','+str(actionlist[i][1])+','+str(actionlist[i][2])
                action_list.append(tmp)
            self.actions_list.addItems(action_list)

    # 动作删除
    def actionsdelete(self):
        name = self.actions_list_human_box.currentText()
        act = self.actions_list.currentText().split(',')
        act_tuple = (act[0],int(act[1]),int(act[2]))
        self.data.delete_actions(name,act_tuple)
        self.actions_update()
        self.save_all()

    # 表情设置
    def expressions_set(self):
        if self.expressions_box.currentText() == '其它':
            self.expression_input.setEnabled(True)
        else:
            self.expression_input.clear()
            self.expression_input.setDisabled(True)

    # 表情存储
    def expressionssave(self):
        if self.expressions_box.currentText() == '其它':
            expression = self.expression_input.text()
        else:
            expression = self.expressions_box.currentText()
        time_interval = (int(self.time_start_expressions_input.text()),int(self.time_end_expressions_input.text()))
        self.data.add_expression(self.expressions_human_box.currentText(),expression,time_interval)
        self.expressions_box.setCurrentIndex(-1)
        self.expressions_human_box.setCurrentIndex(-1)
        self.expression_input.clear()
        self.time_start_expressions_input.clear()
        self.time_end_expressions_input.clear()
        self.expressions_update()
        self.save_all()

    # 表情list更新
    def expressions_update(self):
        self.expressions_list.clear()
        if self.expressions_list_human_box.currentIndex() != -1 :
            expressionlist = self.data.get_expressions(self.expressions_list_human_box.currentText())
            expression_list = []
            for i in range(len(expressionlist)):
                tmp = str(expressionlist[i][0])+','+str(expressionlist[i][1])+','+str(expressionlist[i][2])
                expression_list.append(tmp)
            self.expressions_list.addItems(expression_list)

    # 表情删除
    def expressionsdelete(self):
        name = self.expressions_list_human_box.currentText()
        exp = self.expressions_list.currentText().split(',')
        exp_tuple = (exp[0], int(exp[1]), int(exp[2]))
        self.data.delete_expression(name, exp_tuple)
        self.expressions_update()
        self.save_all()

    # 人人关系设置
    def relationHHset(self):
        if self.relation_HH_box.currentText() == "其它":
            self.relation_HH_input.setEnabled(True)
        else:
            self.relation_HH_input.clear()
            self.relation_HH_input.setDisabled(True)

    # 人人关系存储
    def relationHHsave(self):
        if self.relation_HH_box.currentText() == "其它":
            self.data.add_c2c_relation_node(self.relation_HH_box.currentText(),self.relation_HH_input.text(),
                                            self.human1_box.currentText(),self.human2_box.currentText())
        else:
            self.data.add_c2c_relation_node(self.relation_HH_box.currentText(), None,
                                            self.human1_box.currentText(), self.human2_box.currentText())
        self.human1_box.setCurrentIndex(-1)
        self.human2_box.setCurrentIndex(-1)
        self.relationHH_update()
        self.relation_HH_input.clear()
        self.relationHH_list_update()
        self.save_all()

    # 人人关系category更新
    def relationHH_update(self):
        self.relation_HH_box.clear()
        self.relation_HH_box.addItems(sorted(self.data.get_c2c_relation_category()))
        self.relation_HH_box.addItem("其它")
        self.relation_HH_box.setCurrentIndex(-1)

    # 人人关系list更新
    def relationHH_list_update(self):
        self.relation_HH_list.clear()
        c2c_relations = self.data.get_c2c_relations()
        tmplist = []
        for tmp in c2c_relations:
            ans = tmp[0] + ',' + tmp[1] + ',' + tmp[2]
            tmplist.append(ans)
        self.relation_HH_list.addItems(tmplist)
        self.relation_HH_list.setCurrentIndex(-1)

    # 人人关系删除
    def relationHHdelete(self):
        if self.relation_HH_list.currentIndex() == -1:
            return
        else:
            tmp = self.relation_HH_list.currentText().split(',')
            ans = (tmp[0],tmp[1],tmp[2])
            self.data.delete_c2c_relation_node(ans)
            self.relationHH_list_update()
        self.save_all()

    # 人物关系设置
    # def relationHOset(self):
    #     if self.relation_HO_box.currentText() == "其它":
    #         self.relation_HO_input.setEnabled(True)
    #     else:
    #         self.relation_HO_input.clear()
    #         self.relation_HO_input.setDisabled(True)

    # 人物关系category更新
    # def relationHO_update(self):
    #     self.relation_HO_box.clear()
    #     self.relation_HO_box.addItems(sorted(self.data.get_c2o_relation_category()))
    #     self.relation_HO_box.addItem("其它")
    #     self.relation_HO_box.setCurrentIndex(-1)

    # 人物关系list更新
    # def relationHO_list_update(self):
    #     self.relation_HO_list.clear()
    #     c2o_relations = self.data.get_c2o_relations()
    #     tmplist = []
    #     for tmp in c2o_relations:
    #         ans = tmp[0] + ',' + tmp[1] + ',' + tmp[2]
    #         tmplist.append(ans)
    #     self.relation_HO_list.addItems(tmplist)
    #     self.relation_HO_list.setCurrentIndex(-1)

    # 人物关系存储
    # def relationHOsave(self):
    #     if self.relation_HO_box.currentText() == "其它":
    #         self.data.add_c2o_relation_node(self.relation_HO_box.currentText(),self.relation_HO_input.text(),
    #                                         self.human_box.currentText(),self.object_box.currentText())
    #     else:
    #         self.data.add_c2o_relation_node(self.relation_HO_box.currentText(), None,
    #                                         self.human_box.currentText(), self.object_box.currentText())
    #     self.human_box.setCurrentIndex(-1)
    #     self.object_box.setCurrentIndex(-1)
    #     self.relationHO_update()
    #     self.relation_HO_input.clear()
    #     self.relationHO_list_update()
    #     self.save_all()

    # 人物关系删除
    # def relationHOdelete(self):
    #     if self.relation_HO_list.currentIndex() == -1:
    #         return
    #     else:
    #         tmp = self.relation_HO_list.currentText().split(',')
    #         ans = (tmp[0], tmp[1], tmp[2])
    #         self.data.delete_c2o_relation_node(ans)
    #         self.relationHO_list_update()
    #     self.save_all()

    # 人人交互设置
    def interactionset(self):
        if self.interaction_box.currentText() == "其它":
            self.interaction_input.setEnabled(True)
        else:
            self.interaction_input.clear()
            self.interaction_input.setDisabled(True)

    # 人人交互category更新
    def interaction_update(self):
        self.interaction_box.clear()
        self.interaction_box.addItems(sorted(self.data.get_c2c_interaction_category()))
        self.interaction_box.addItem("其它")
        self.interaction_box.setCurrentIndex(-1)

    # 人人交互list更新
    def interaction_list_update(self):
        self.interaction_list.clear()
        interactions = self.data.get_c2c_interactions()
        tmplist = []
        for tmp in interactions:
            if len(tmp)==3:
                node = self.data.c2c_interaction_nodes[tmp]
                interaction_time = node.when
                interaction_reason = node.why
                self.data.delete_c2c_interaction_node(tmp)
                self.data.add_c2c_interaction_node(tmp[1],None,interaction_reason,interaction_time,tmp[0],tmp[2])
                ans = tmp[0] + ',' + tmp[1] + ',' + tmp[2]+',('+str(interaction_time[0])+','+str(interaction_time[1])+')'
            else:
                ans = tmp[0] + ',' + tmp[1] + ',' + tmp[2]+',('+str(tmp[3][0])+','+str(tmp[3][1])+')'
            tmplist.append(ans)
        self.interaction_list.addItems(tmplist)
        self.interaction_list.setCurrentIndex(-1)

    # 人人交互存储
    def interactionsave(self):
        time_interval = (int(self.time_start_interaction_input.text()),int(self.time_end_interaction_input.text()))
        if self.interaction_box.currentText() == "其它":
            self.data.add_c2c_interaction_node(self.interaction_box.currentText(),self.interaction_input.text(),
                                               self.reason_input.text(),time_interval,self.human3_box.currentText(),
                                               self.human4_box.currentText())
        else:
            self.data.add_c2c_interaction_node(self.interaction_box.currentText(), None,
                                               self.reason_input.text(), time_interval, self.human3_box.currentText(),
                                               self.human4_box.currentText())
        self.human3_box.setCurrentIndex(-1)
        self.human4_box.setCurrentIndex(-1)
        self.interaction_update()
        self.interaction_input.clear()
        self.reason_input.clear()
        self.time_start_interaction_input.clear()
        self.time_end_interaction_input.clear()
        self.interaction_list_update()
        self.save_all()

    # 人人交互删除
    def interactiondelete(self):
        if self.interaction_list.currentIndex() == -1:
            return
        else:
            tmp = self.interaction_list.currentText().split(',')
            ans = (tmp[0], tmp[1], tmp[2],(int(tmp[3].split('(')[1]),int(tmp[4].split(')')[0])))
            self.data.delete_c2c_interaction_node(ans)
            self.interaction_list_update()
        self.save_all()

    # 保存全局变量和局部变量
    def save_all(self):
        if self.annotation_global_path == None:
            return
        self.scenesave()
        self.eventsave()
        self.storysave()
        self.data.save_nodes_and_links(self.annotation_path)
        self.data.save_indexes(self.annotation_global_path)
        #self.graph_show()

    # 打开下一个视频
    def nextvideo(self):
        self.save_all()
        self.openfile()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = myMainWindow()
    gui.show()
    # 退出整个app
    # app.exit(app.exec_())
    sys.exit(app.exec_())

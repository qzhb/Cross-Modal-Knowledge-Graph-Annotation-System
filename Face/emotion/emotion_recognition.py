"""
visualize results for test image
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
import os
from torch.autograd import Variable

import transforms as transforms
from skimage import io
from skimage.transform import resize
from models import *

from os import path

import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")


cut_size = 44

transform_test = transforms.Compose([
    transforms.TenCrop(cut_size),
    transforms.Lambda(lambda crops: torch.stack([transforms.ToTensor()(crop) for crop in crops])),
])

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.299, 0.587, 0.114])
class_names = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

net = VGG('VGG19')
# checkpoint = torch.load(os.path.join('FER2013_VGG19', 'PrivateTest_model.t7'))
checkpoint = torch.load(os.path.join('FER2013_VGG19', 'PrivateTest_model.t7'),map_location=torch.device('cpu'))
net.load_state_dict(checkpoint['net'])
# net.cuda()
net.eval()
while True:
    message = socket.recv()
    print("Received request: %s" % message)

    
    #raw_img = io.imread('../../CROPPED_FACE.jpg')
    raw_img = io.imread('../CROPPED_FACE.jpg')
    gray = rgb2gray(raw_img)
    gray = resize(gray, (48,48), mode='symmetric').astype(np.uint8)
    
    img = gray[:, :, np.newaxis]
    
    img = np.concatenate((img, img, img), axis=2)
    img = Image.fromarray(img)
    inputs = transform_test(img)
    
    
    ncrops, c, h, w = np.shape(inputs)
    
    inputs = inputs.view(-1, c, h, w)
    # inputs = inputs.cuda()
    inputs = Variable(inputs, volatile=True)
    outputs = net(inputs)
    
    outputs_avg = outputs.view(ncrops, -1).mean(0)  # avg over crops
    
    score = F.softmax(outputs_avg)
    _, predicted = torch.max(outputs_avg.data, 0)
    
    # socket.send(class_names[int(predicted.cpu().numpy())])
    socket.send_string(str(class_names[int(predicted.cpu().numpy())]))
        

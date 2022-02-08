import pyautogui
import time
import pandas as pd
import numpy as np
from PIL import ImageGrab
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
from textblob import TextBlob
import time
import datetime
import csv
import cv2
from ctypes import *
from Levenshtein import distance as lev
import discord
import os
import pytesseract
import pygetwindow
import win32con
import win32gui
import win32ui
import win32api
import numpy as np
import pandas as pd
import winsound
import time
import re
import random
import pyautogui
from threading import Thread
from requests import get
from getpass import getpass
from sqlalchemy import create_engine
from PIL import Image
from pynput import keyboard
from pynput.keyboard import Key

mode = 1 #0map1run

def remove_isolated_pixels(image):
    connectivity = 8

    output = cv2.connectedComponentsWithStats(image, connectivity=connectivity, ltype=cv2.CV_32S)

    num_stats = output[0]
    labels = output[1]
    stats = output[2]

    new_image = image.copy()

    for label in range(num_stats):
        if stats[label,cv2.CC_STAT_AREA] <= 10:
            new_image[labels == label] = 0

    return new_image

def on_press(key):
    #handle pressed keys
    pass

def process(x,y):
    screen =  ImageGrab.grab(bbox=(420,1,2140,1280))
    pyautogui.keyDown('y')
    time.sleep(0.1)
    screenY =  ImageGrab.grab(bbox=(420,1,2140,1280))
    pyautogui.keyUp('y')
    time.sleep(0.1)
    screen2 =  ImageGrab.grab(bbox=(420,1,2140,1280))
    pyautogui.keyDown('y')
    time.sleep(0.1)
    screenY2 =  ImageGrab.grab(bbox=(420,1,2140,1280))
    pyautogui.keyUp('y')
    
    screen = np.array(screen) 
    screen = screen[:, :, ::-1].copy() 
    lower = np.array([170,170,170])
    upper= np.array([240,240,240])
    mask = cv2.inRange(screen, lower, upper)
    screen = cv2.bitwise_and(screen, screen, mask=mask)
    #cv2.imwrite(f'test/screen.jpg', screen)

    screenY = np.array(screenY) 
    screenY = screenY[:, :, ::-1].copy() 
    lower = np.array([170,170,170])
    upper= np.array([240,240,240])
    mask = cv2.inRange(screenY, lower, upper)
    screenY = cv2.bitwise_and(screenY, screenY, mask=mask)
    #cv2.imwrite(f'test/screenY.jpg', screenY)
    screen2 = np.array(screen2) 
    screen2 = screen2[:, :, ::-1].copy() 
    lower = np.array([170,170,170])
    upper= np.array([240,240,240])
    mask = cv2.inRange(screen2, lower, upper)
    screen2 = cv2.bitwise_and(screen2, screen2, mask=mask)
    #cv2.imwrite(f'test/screen2.jpg', screen2)
    screenY2 = np.array(screenY2) 
    screenY2 = screenY2[:, :, ::-1].copy() 
    lower = np.array([170,170,170])
    upper= np.array([240,240,240])
    mask = cv2.inRange(screenY2, lower, upper)
    screenY2 = cv2.bitwise_and(screenY2, screenY2, mask=mask)
    #cv2.imwrite(f'test/screenY2.jpg', screenY2)
    
    diffY = cv2.subtract(screenY,screen)
    diffY = cv2.cvtColor(diffY, cv2.COLOR_BGR2GRAY)
    (thresh, diffY) = cv2.threshold(diffY, 50, 255, cv2.THRESH_BINARY)
    #cv2.imwrite(f'test/diffY.jpg', diffY) #isoler les surlignage + bruit

    diffY2 = cv2.subtract(screenY2,screen2)
    diffY2 = cv2.cvtColor(diffY2, cv2.COLOR_BGR2GRAY)
    (thresh, diffY2) = cv2.threshold(diffY2, 50, 255, cv2.THRESH_BINARY)
    #cv2.imwrite(f'test/diffY2.jpg', diffY2) #isoler les surlignage + bruit

    diffYY1 = cv2.subtract(diffY,diffY2)
    #cv2.imwrite(f'test/diffYY1.jpg', diffYY1) #isoler les bruits

    diffYY2 = cv2.subtract(diffY2,diffY)
    #cv2.imwrite(f'test/diffYY2.jpg', diffYY2) #isoler les bruits

    diffYY= cv2.add(diffYY1,diffYY2)
    #cv2.imwrite(f'test/diffYY.jpg', diffYY) #isoler les bruits

    difSubY = cv2.subtract(diffY,diffYY)
    #cv2.imwrite(f'test/difSubY.jpg', difSubY)
 
    image_X_Y = remove_isolated_pixels(difSubY)
    if mode == 0:
        cv2.imwrite(f'Map/{x}_{y}.jpg', image_X_Y)
    else:
        im_source = cv2.imread(f'Map/{x}_{y}.jpg',0)
        diffsource = cv2.subtract(difSubY,im_source) 
        diffsource = remove_isolated_pixels(diffsource)  
        cv2.imwrite(f'test/{x}_{y}.jpg', diffsource)
    print(x,y)
     

x = int(input("x:"))
y = int(input("y:"))

def on_release(key):
    #handle released keys

    global x
    global y
    
    if(key==Key.down):
        y = y + 1
        process(x,y)
    if(key==Key.up):
        y = y - 1
        process(x,y)
    if(key==Key.left):
        x = x - 1
        process(x,y)
    if(key==Key.right):
        x = x + 1
        process(x,y)

time.sleep(1)
with keyboard.Listener(on_press=on_press,on_release=on_release) as listener:
    listener.join()
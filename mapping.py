import pyautogui
import time
import numpy as np
import cv2
import re
import pytesseract
import Levenshtein as lev
from PIL import ImageGrab
from PIL import Image
from pynput import keyboard
from pynput.keyboard import Key

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

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
    screen =  ImageGrab.grab(bbox=(410,1,2240,1280))
    pyautogui.keyDown('y')
    time.sleep(0.1)
    screenY =  ImageGrab.grab(bbox=(410,1,2240,1280))
    pyautogui.keyUp('y')
    time.sleep(0.1)
    screen2 =  ImageGrab.grab(bbox=(410,1,2240,1280))
    pyautogui.keyDown('y')
    time.sleep(0.1)
    screenY2 =  ImageGrab.grab(bbox=(410,1,2240,1280))
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
        kernel = np.ones((5,5),np.uint8)
        diffsource = cv2.dilate(diffsource,kernel,iterations = 7)
 
        blur = cv2.GaussianBlur(diffsource, (5, 5),cv2.BORDER_DEFAULT)
        ret, thresh = cv2.threshold(blur, 200, 255,cv2.THRESH_BINARY_INV)
        cv2.imwrite("test/thresh.png",thresh)
        contours, hierarchies = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        blank = np.zeros(thresh.shape[:2],
				dtype='uint8')

        cv2.drawContours(blank, contours, -1,
        				(255, 0, 0), 1)

        cv2.imwrite("test/contours.png", blank)
        list_click = []

        for i in contours:
            M = cv2.moments(i)
            if M['m00'] != 0:
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                cv2.drawContours(diffsource, [i], -1, (0, 255, 0), 2)
                cv2.circle(diffsource, (cx, cy), 7, (0, 0, 255), -1)
                cv2.putText(diffsource, "center", (cx - 20, cy - 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            if cx != 859 and cy != 639:
                list_click.append((cx+420,cy+1))

        print(list_click)

        for coord in list_click:
            test_click(coord)
            time.sleep(0.2)
            
        pyautogui.keyUp('shift')

        
        cv2.imwrite("test/center.png", diffsource)

    print(x,y)

x = int(input("x:"))
y = int(input("y:"))

def test_click(coord):
    x_click,y_click = coord
    average_coord = []
    for x_test in range(x_click-20,x_click+20,10):
        for y_test in range(y_click-20,y_click+20,10):
            pyautogui.moveTo(x_test, y_test)
            ressource_grab =  ImageGrab.grab(bbox=(x_click-20,y_click-200,x_click+450,y_click-20))
            ressource_grab = np.array(ressource_grab) 
            ressource_grab = ressource_grab[:, :, ::-1].copy() 
            ressource_grab = cv2.cvtColor(ressource_grab, cv2.COLOR_BGR2HLS)
            average = ressource_grab.mean(axis=0).mean(axis=0)
            if len(average_coord)>0:
                if average[1]<average_coord[0][0][0] and average[2]<average_coord[0][0][1]:
                    pyautogui.keyDown('shift')
                    pyautogui.click(x_test,y_test)
                    pyautogui.keyUp('shift') 
                    return True

                elif average[1]==average_coord[0][0][0] and average[2]==average_coord[0][0][1]:
                    pass
                else:
                    pyautogui.keyDown('shift')
                    pyautogui.click(average_coord[0][1],average_coord[0][2])
                    pyautogui.keyUp('shift') 
                    return True
            else:
                average_coord.append((average[1:3],x_test,y_test))
    pyautogui.keyDown('shift')
    pyautogui.click(average_coord[0][1],average_coord[0][2])
    pyautogui.keyUp('shift') 

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
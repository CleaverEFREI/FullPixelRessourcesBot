import pyautogui
import time
import numpy as np
import cv2
from PIL import ImageGrab
from pynput import keyboard
from pynput.keyboard import Key
import pygetwindow
import win32gui
import random


mode = int(input("Mode map 0 / run 1:"))


def hook():
    # Scan des fenetres ouvertes
    screen_name = "Not found"
    print("Waiting for dofus ...")
    while screen_name == "Not found":

        screen_tiles_name = pygetwindow.getAllTitles()
        for i in screen_tiles_name:
            if "Dofus 2." in i:
                # Si on trouve dofus
                print("Hooked on : " + i)
                screen_name = i
                break

    hwnd = win32gui.FindWindow(None, screen_name)
    return hwnd


def windows_size(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    return x, y, w, h


hwnd = hook()
x, y, w, h = windows_size(hwnd)

x = int(input("x:"))
y = int(input("y:"))
if mode:
    NomFile = input("Nom du path à utiliser:")
else:
    NomFile = None


def remove_isolated_pixels(image):
    connectivity = 8

    output = cv2.connectedComponentsWithStats(
        image, connectivity=connectivity, ltype=cv2.CV_32S)

    num_stats = output[0]
    labels = output[1]
    stats = output[2]

    new_image = image.copy()

    for label in range(num_stats):
        if stats[label, cv2.CC_STAT_AREA] <= 10:
            new_image[labels == label] = 0

    return new_image


def on_press(key):
    # handle pressed keys
    pass


def process(x, y):
    screen = ImageGrab.grab(
        bbox=(int(410/2560*w), 1, int(2240/2560*w), int(1280/1440*h)))
    pyautogui.keyDown('y')
    time.sleep(0.1)
    screenY = ImageGrab.grab(
        bbox=(int(410/2560*w), 1, int(2240/2560*w), int(1280/1440*h)))
    pyautogui.keyUp('y')
    time.sleep(0.1)
    screen2 = ImageGrab.grab(
        bbox=(int(410/2560*w), 1, int(2240/2560*w), int(1280/1440*h)))
    pyautogui.keyDown('y')
    time.sleep(0.1)
    screenY2 = ImageGrab.grab(
        bbox=(int(410/2560*w), 1, int(2240/2560*w), int(1280/1440*h)))
    pyautogui.keyUp('y')

    screen = np.array(screen)
    screen = screen[:, :, ::-1].copy()
    lower = np.array([170, 170, 170])
    upper = np.array([240, 240, 240])
    mask = cv2.inRange(screen, lower, upper)
    screen = cv2.bitwise_and(screen, screen, mask=mask)
    #cv2.imwrite(f'test/screen.jpg', screen)

    screenY = np.array(screenY)
    screenY = screenY[:, :, ::-1].copy()
    lower = np.array([170, 170, 170])
    upper = np.array([240, 240, 240])
    mask = cv2.inRange(screenY, lower, upper)
    screenY = cv2.bitwise_and(screenY, screenY, mask=mask)
    #cv2.imwrite(f'test/screenY.jpg', screenY)
    screen2 = np.array(screen2)
    screen2 = screen2[:, :, ::-1].copy()
    lower = np.array([170, 170, 170])
    upper = np.array([240, 240, 240])
    mask = cv2.inRange(screen2, lower, upper)
    screen2 = cv2.bitwise_and(screen2, screen2, mask=mask)
    #cv2.imwrite(f'test/screen2.jpg', screen2)
    screenY2 = np.array(screenY2)
    screenY2 = screenY2[:, :, ::-1].copy()
    lower = np.array([170, 170, 170])
    upper = np.array([240, 240, 240])
    mask = cv2.inRange(screenY2, lower, upper)
    screenY2 = cv2.bitwise_and(screenY2, screenY2, mask=mask)
    #cv2.imwrite(f'test/screenY2.jpg', screenY2)

    diffY = cv2.subtract(screenY, screen)
    diffY = cv2.cvtColor(diffY, cv2.COLOR_BGR2GRAY)
    (thresh, diffY) = cv2.threshold(diffY, 50, 255, cv2.THRESH_BINARY)
    # cv2.imwrite(f'test/diffY.jpg', diffY) #isoler les surlignage + bruit

    diffY2 = cv2.subtract(screenY2, screen2)
    diffY2 = cv2.cvtColor(diffY2, cv2.COLOR_BGR2GRAY)
    (thresh, diffY2) = cv2.threshold(diffY2, 50, 255, cv2.THRESH_BINARY)
    # cv2.imwrite(f'test/diffY2.jpg', diffY2) #isoler les surlignage + bruit

    diffYY1 = cv2.subtract(diffY, diffY2)
    # cv2.imwrite(f'test/diffYY1.jpg', diffYY1) #isoler les bruits

    diffYY2 = cv2.subtract(diffY2, diffY)
    # cv2.imwrite(f'test/diffYY2.jpg', diffYY2) #isoler les bruits

    diffYY = cv2.add(diffYY1, diffYY2)
    # cv2.imwrite(f'test/diffYY.jpg', diffYY) #isoler les bruits

    difSubY = cv2.subtract(diffY, diffYY)
    #cv2.imwrite(f'test/difSubY.jpg', difSubY)

    image_X_Y = remove_isolated_pixels(difSubY)
    if mode == 0:
        cv2.imwrite(f'Map/{x}_{y}.jpg', image_X_Y)
    else:
        im_source = cv2.imread(f'Map/{x}_{y}.jpg', 0)
        diffsource = cv2.subtract(difSubY, im_source)
        diffsource = remove_isolated_pixels(diffsource)
        cv2.imwrite(f'test/{x}_{y}.jpg', diffsource)
        kernel = np.ones((5, 5), np.uint8)
        diffsource = cv2.dilate(diffsource, kernel, iterations=7)

        blur = cv2.GaussianBlur(diffsource, (5, 5), cv2.BORDER_DEFAULT)
        ret, thresh = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY_INV)
        cv2.imwrite("test/thresh.png", thresh)
        contours, hierarchies = cv2.findContours(
            thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
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
            if cx != int(859/2560*w) and cy != int(639/1440*h):
                list_click.append((cx+int(420/2560*w), cy+int(1/1440*h)))

        for coord in list_click:
            test_click(coord)
            time.sleep(0.2)

        pyautogui.keyUp('shift')
        time.sleep(len(list_click)*4)

        cv2.imwrite("test/center.png", diffsource)

    print(x, y)


def test_click(coord):
    x_click, y_click = coord
    average_coord = []
    for x_test in range(x_click-20, x_click+20, 5):
        for y_test in range(y_click-20, y_click+20, 5):
            pyautogui.moveTo(x_test, y_test)
            ressource_grab = ImageGrab.grab(bbox=(x_click-int(20/2560*w), y_click-int(
                200/1440*h), x_click+int(450/2560*w), y_click-int(20/1440*h)))
            ressource_grab = np.array(ressource_grab)
            ressource_grab = ressource_grab[:, :, ::-1].copy()
            ressource_grab = cv2.cvtColor(ressource_grab, cv2.COLOR_BGR2HLS)
            average = ressource_grab.mean(axis=0).mean(axis=0)
            if len(average_coord) > 0:
                if average[1] < average_coord[0][0][0] and average[2] < average_coord[0][0][1]:
                    pyautogui.keyDown('shift')
                    pyautogui.click(x_test, y_test)
                    pyautogui.keyUp('shift')
                    return True

                elif average[1] == average_coord[0][0][0] and average[2] == average_coord[0][0][1]:
                    pass
                else:
                    pyautogui.keyDown('shift')
                    pyautogui.click(average_coord[0][1], average_coord[0][2])
                    pyautogui.keyUp('shift')
                    return True
            else:
                average_coord.append((average[1:3], x_test, y_test))
    pyautogui.keyDown('shift')
    pyautogui.click(average_coord[0][1], average_coord[0][2])
    pyautogui.keyUp('shift')


def on_release(key):
    # handle released keys

    global x
    global y

    if(key == Key.down):
        y = y + 1
        process(x, y)
    if(key == Key.up):
        y = y - 1
        process(x, y)
    if(key == Key.left):
        x = x - 1
        process(x, y)
    if(key == Key.right):
        x = x + 1
        process(x, y)
    if(key == Key.f10):
        exit()


def moove_right():

    pyautogui.click(int(random.randint(950, 1000)/1000*w),
                    int(random.randint(400, 600)/1000*h))


def moove_left():

    pyautogui.click(int(random.randint(0, 500)/1000*w),
                    int(random.randint(400, 600)/1000*h))


def moove_up():

    pyautogui.click(int(random.randint(400, 600)/1000*w),
                    int(random.randint(0, 500)/1000*h))


def moove_down():

    pyautogui.click(int(random.randint(400, 600)/1000*w),
                    int(random.randint(950, 1000)/1000*h))


def readpath():
    path = []
    with open(f'C:/Users/louis/ressourcesBot/path/{NomFile}.txt') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line:
                line = line.split(":")
                path.append((line[0], line[1]))
    return path


def waiting_map():
    change_map = ImageGrab.grab(
        bbox=(int(0.4*w), int(0.4*h), int(0.6*w), int(0.6*h)))
    screen = np.array(change_map)
    screen = screen[:, :, ::-1].copy()
    while cv2.countNonZero(screen) != 0:
        change_map = ImageGrab.grab(
            bbox=(int(0.4*w), int(0.4*h), int(0.6*w), int(0.6*h)))
        screen = np.array(change_map)
        screen = screen[:, :, ::-1].copy()
    while cv2.countNonZero(screen) == 0:
        change_map = ImageGrab.grab(
            bbox=(int(0.4*w), int(0.4*h), int(0.6*w), int(0.6*h)))
        screen = np.array(change_map)
        screen = screen[:, :, ::-1].copy()
    time.sleep(1)
    return True


def moove_in_path(path_list, x, y):    
    process(x, y)
    if path_list[0] == path_list[-1]:
        while True:
            for cord in path_list:
                cord[0] = int(cord[0])
                cord[1] = int(cord[1])
                while cord[0] != x and cord[1] != y:
                    if cord[0] < x:
                        moove_right()
                        x = x + 1
                    if cord[0] > x:
                        moove_left()
                        x = x - 1
                    if cord[1] < y:
                        moove_up()
                        y = y + 1
                    if cord[1] > y:
                        moove_down()
                        y = y - 1
                    waiting_map()
                    process(x, y)
    else:

        for cord in path_list:
            while cord[0] != x and cord[1] != y:
                if cord[0] < x:
                    moove_right()
                    x = x + 1
                if cord[0] > x:
                    moove_left()
                    x = x - 1
                if cord[1] < y:
                    moove_up()
                    y = y + 1
                if cord[1] > y:
                    moove_down()
                    y = y - 1
                waiting_map()
                process(x, y)


time.sleep(4)
if mode == 0:
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()
else:
    path_list = readpath()
    moove_in_path(path_list,x,y)

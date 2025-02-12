# All screen and windows related functions
DEBUG = False
import win32gui
import time
from ctypes import windll
import psutil
import cv2
import numpy as np
import win32api
import threading
from threading import Thread, Event
from datetime import datetime
import os
import random
import string
import dxcam

# Make program aware of DPI scaling, otherwise values from GetWindowRect will be incorrect
user32 = windll.user32
user32.SetProcessDPIAware()

def getHandleByTitle(title):
    '''Get window handle by exact match of window title'''
    toplist, winlist = [], []
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(enum_cb, toplist)
    win = [(hwnd, t) for hwnd, t in winlist if title == t]
    if len(win) == 0:
        raise RuntimeError('window with title "%s" not detected.'%title)
    return win[0][0]

def moveWindow(handle, x, y, width = None, height = None):
    if width is None and height is None:
        rect = win32gui.GetWindowRect(handle)
        width = rect[2] - rect[0]
        height = rect[3] - rect[1]
    win32gui.MoveWindow(handle, x, y, width, height, True)

def captureWindow(DXCam: dxcam.DXCamera, handle, convert = None, save=None):
    '''bring forth a windpywintypes.errorow and capture'''
    bbox_window = win32gui.GetWindowRect(handle)
    bbox_client = win32gui.GetClientRect(handle)
    border_size = int((bbox_window[2] - bbox_window[0] - bbox_client[2]) / 2)
    header_size = int(bbox_window[3] - bbox_window[1] - bbox_client[3] - border_size*2)
    region = [bbox_window[0] + border_size,
              bbox_window[1] + header_size + border_size,
              bbox_window[2] - border_size,
              bbox_window[3] - border_size]
    while True:
        img = DXCam.grab(region)
        if img is not None:
            break
    if save:
        # new thread to save time
        thread = threading.Thread(target=img.save, args=(save,) )
        thread.start()
        print('saved an streaming image...')
    img = np.array(img)
    if convert == 'GBR':
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif convert == None:
        pass
    else:
        raise ValueError('Unsupported conversion type %s'%convert)
    return img

def killImageWindow(name='Microsoft.Photos.exe'):
    '''Kill a image window by process name '''
    for proc in psutil.process_iter():
        if proc.name() == name:
            proc.kill()


class CaptureStream:
    event = Event()
    '''Background process to capture roblox window as stream of images '''
    def __init__(self, title, scale = 0.5, stride = 32, saveInterval = 2):
        '''
            title: title of window to be captured
            scale: resize factor when returning the image
            stride: final image size will be a multiple of stride
            saveInternal: Intervals in seconds to save a streaming image (for training, etc)
        '''
        # save file info
        if saveInterval > 0:
            randomID = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
            foldername = r'images\\' + datetime.now().strftime("%m-%d-%Y_%H-%M-%S")
            os.mkdir(foldername)
            self.filename = foldername + r'\\'+ randomID+'_img_%04d.png'
        else:
            self.filename = None

        self.h = getHandleByTitle(title)
        moveWindow(self.h, 0, 0, 100, 100)  # put roblex window to left top corner and minimize the window size.
        thread = Thread(target=self.update, args=[self.h, self.filename, saveInterval], daemon=True)
        thread.start()
        self.img = None
        self.scale = scale
        self.stride = int(stride)



    def update(self, handle, filename, saveInterval):
        '''
             handle: window handle
             filename: file name template used for saving images. String must contain %d for indexing
             saveInterval: duration between save images in sec
        :return:
        '''
        lastSaveTime = -100
        i = 0
        DXCam = dxcam.create()
        while True:
            if time.time() - lastSaveTime < saveInterval or not filename:
                save = None
            else:
                save = filename%i
                i+=1
                lastSaveTime = time.time()
            self.img0 = captureWindow(DXCam, handle, convert=None, save=save)
            w = int(self.img0.shape[1] *self.scale)
            h = int(self.img0.shape[0] *self.scale)
            w -= w % self.stride
            h -= h % self.stride
            self.img = cv2.resize(self.img0, (640,640))
            self.event.set()



    def __iter__(self):
        self.count = -1
        return self

    def __next__(self):
        self.count += 1
        while self.img is None:
            self.event.wait()
            self.event.clear()
        cpy = self.img
        self.img = None
        return cpy, self.img0.copy()


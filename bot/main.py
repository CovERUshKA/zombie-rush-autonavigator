import sys
sys.path.append("../")  # root folder
sys.path.append("../yolo/yolov5")  # yolov5 folder, needed for pretrained model to work

from roblox import screen
import os
import cv2
import time
import keyboard
import yolo.utils
from roblox.utils import FrameCounter
from bot_utils import opt
from bot_utils import AnnotedImage
import win32api
import win32con
import numpy as np
import torch
import threading
from ultralytics.nn.autobackend import AutoBackend
from ultralytics.utils.torch_utils import select_device
import sys
import win32gui
from ultralytics.utils import ops

import pathlib
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

saveStream = opt.save_stream
simulationMode = opt.simulation_mode
weights = opt.weights
device = opt.device
augment = opt.augment
saveImg = opt.save_annote_img

# get the Screen resolution.
scalex = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
scaley = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

# get the scale(a screen has 65535*65535 mickey value)
scalex = int(65535 / scalex)
scaley = int(65535 / scaley)

def set_cur_pos(rx, ry):
    global scalex
    global scaley
    hWindow = screen.getHandleByTitle("Roblox")

    bbox_window = win32gui.GetWindowRect(hWindow)
    bbox_client = win32gui.GetClientRect(hWindow)
    border_size = int((bbox_window[2] - bbox_window[0] - bbox_client[2]) / 2)
    header_size = int(bbox_window[3] - bbox_window[1] - bbox_client[3] - border_size*2)
    region = [bbox_window[0] + border_size,
              bbox_window[1] + header_size + border_size,
              bbox_window[2] - border_size,
              bbox_window[3] - border_size]

    # This is needed, because if you decide to hold right mouse button to rotate - it won't shake your screen
    # I tried several other methods to make rotation possible when autonavigation enabled - nothing worked
    # Ser cursor position
    win32api.SetCursorPos((region[0] + round(rx*bbox_client[2]), region[1] + round(ry*bbox_client[3])))
    # Move mouse on one pixel to make mouse teleport.
    win32api.mouse_event(0x0001, 0, 1, 0, 0)

event = threading.Event()
anno_event = threading.Event()
main_lock = threading.Lock()
anno_lock = threading.Lock()
imgs = []
preds = []
inferred = 0
save_key = False
paused = False
last_poses = None
last_sizes = None

destroy_program = False

def process_data(args):
    global event
    global main_lock
    global device
    global destroy_program
    global paused
    global last_poses
    global last_sizes
    profilers = (
                ops.Profile(device=device),
            )
    while True:
        event.wait()
        if destroy_program:
            break
        main_lock.acquire(True, -1)
        event.clear()
        if len(preds) == 0:
            main_lock.release()
            continue
        pred = preds.pop(0)
        main_lock.release()

        with profilers[0]:
            pred = ops.non_max_suppression(pred, 0.25, 0.45, max_time_img=0.001)

        pos, sizes = yolo.utils.processPrediction(pred, args[0], args[1], ['amethyst', 'combustion', 'diamond',
                                                                           'diamond_skeleton', 'emerald', 'gold',
                                                                           'gold_skeleton', 'normal', 'obsidian', 
                                                                           'phantom', 'phantom_skeleton', 'ruby', 
                                                                           'sapphire', 'silver', 'skeleton', 'slime_zombie', 
                                                                           'speedy', 'super_phantom', 'wraith', 'zombie_king'])

        anno_lock.acquire(True, -1)
        last_poses = pos.copy()
        last_sizes = sizes.copy()
        anno_lock.release()

        if keyboard.is_pressed("p")  and not paused:
            print("Paused...")
            paused = True

        if keyboard.is_pressed("r") and paused:
            print("Resumed.")
            paused = False
        
        closest = None
        largest = None
        if not paused:
            closest_dist = 3
            largest_size = 0
            largest_sizes = None
            # for x, y in pos[0]:
            #     dist = math.dist((0.5, 0.5), (x, y))
            #     if dist < closest_dist:
            #         closest_dist = dist
            #         closest = (x, y)
            for n, n_list in enumerate(pos):
                for j, size in enumerate(sizes[n]):
                    size_square = size[0] * size[1]
                    if size_square > largest_size:
                        largest_sizes = size
                        largest_size = size_square
                        largest = pos[n][j]
            if largest != None:
                set_cur_pos(largest[0]+largest_sizes[0]/2, largest[1]+largest_sizes[1]/2)

def run():
    global device
    global model
    global save_key
    global destroy_program
    global paused
    global last_poses
    global last_sizes
    # load pretrained model
    device = select_device(device, verbose=False)
    model = AutoBackend(weights, device=device, verbose=True, fp16=True) # fp16=True
    print(type(model))
    print("MODEEELLLL DEVICE ____ ", model.device, torch.cuda.is_available())
    
    # background process to capture roblox window
    stream = screen.CaptureStream('Roblox', scale=1., saveInterval = saveStream) # stride = 32

    # initialize
    frame_counter = FrameCounter(interval=5)
    anno_image = AnnotedImage(saveImg)

    process_thread = threading.Thread(target=process_data, args=(([1, 3, 640, 640], (640, 640, 3)),))
    process_thread.start()
    try:
        profilers = (
                ops.Profile(device=device),
                ops.Profile(device=device),
                ops.Profile(device=device),
            )
        for img, img0 in stream:
            if save_key:
                print("Saving screenshot...")
                sv = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                rect = win32gui.GetClientRect(stream.h)
                try:
                    os.mkdir(f"images")
                except FileExistsError:
                    pass
                cv2.imwrite(f"images/Screenshot_{rect[2]}x{rect[3]}_{int(time.time())}.png", sv)
                print("Screenshot saved.")
                save_key = False
            im = img.copy()
            
            im = im.transpose((2, 0, 1))[::-1]
            im = np.ascontiguousarray(im)
            im = torch.from_numpy(im).to(device)
            im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
            im /= 255.0  # 0 - 255 to 0.0 - 1.0
            if im.ndimension() == 3:
                im = im.unsqueeze(0)
            
            with profilers[1]:
                pred = model(im)
            
            main_lock.acquire(True, -1)
            event.set()
            preds.clear()
            preds.append(pred.copy())
            main_lock.release()
            
            saved_poses = None
            saved_sizes = None

            anno_lock.acquire(True, -1)
            if last_poses != None and last_sizes != None:
                saved_poses = last_poses.copy()
                saved_sizes = last_sizes.copy()
            anno_lock.release()

            # draw bounding boxes
            anno_image.show(img, paused, saved_poses, saved_sizes)

            # count frames
            frame_counter.log()
    except KeyboardInterrupt:
        print("KeyboardInterrupt exception detected")
        destroy_program = True
        event.set()

def save_key_callback(key):
    global save_key
    save_key = True

keyboard.on_release_key("f", save_key_callback)
if __name__ == '__main__':
    run()
from bot_utils import opt
import torch
from ultralytics import YOLO
from ultralytics.utils.torch_utils import select_device
from PIL import Image

import pathlib
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath
import os
import time
import shutil

saveStream = opt.save_stream
simulationMode = opt.simulation_mode
weights = opt.weights
device = opt.device
augment = opt.augment
saveImg = opt.save_annote_img


def run():
    global device
    global model
    # load pretrained model
    device = select_device(device, verbose=False)
    model = YOLO(weights, task="detect")
    print(type(model))
    print("MODEEELLLL DEVICE ____ ", model.device, torch.cuda.is_available())
    dir = round(time.time() * 1000)
    os.mkdir(f"images/labeled/{dir}")
    os.mkdir(f"images/labeled/{dir}/labels")
    os.mkdir(f"images/labeled/{dir}/images")
    for filename in os.listdir("images"):
        print(filename)
        if filename.endswith('.jpg') or filename.endswith('.png'):
            img = Image.open(f"images/{filename}")
            results = model(img, verbose=False, conf = 0.5, iou=0.7, agnostic_nms=True)
            with open(f"images/labeled/{dir}/labels/{filename[:-4]}.txt", 'w') as file:
                for n, prediction in enumerate(results[0].boxes.xywhn):
                    file.write(f"{int(list(results[0].boxes.cls.cpu().numpy())[n])} {prediction[0].item()} {prediction[1].item()} {prediction[2].item()} {prediction[3].item()}\n")
                shutil.move(f"images/{filename}",f"images/labeled/{dir}/images/{filename}")
    shutil.copy("labels.txt",f"images/labeled/{dir}")

if __name__ == '__main__':
    run()

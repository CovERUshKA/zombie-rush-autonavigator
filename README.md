# Autonavigator for Zombie Rush

This autonavigator automatically set's cursor on position of detected zombies and then you can click to shoot.

Dataset - https://universe.roboflow.com/test-o0ilg/zombie-rush

# Autolabeling
You can use `autolabel.py` to autolabel images at the `images` folder and then upload them to roboflow, with the `labels.txt` file copied there.

# Keys
P - Pause\
R - Resume\
F - Save screenshot to `images` folder for dataset

# Installation on Windows using Conda
Follow this command order in conda in order to install everything as I did
1) Create conda environment
```
conda create -n autonavigator python=3.10
conda activate autonavigator
```
2) Install cudatoolkit and cudnn
```
conda install -c conda-forge cudatoolkit=11.2 cudnn=8.1.0
```
3) Install [pytorch](https://pytorch.org/get-started/locally/) with cuda
```
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
```
4) Open project folder
```
cd /d /path/to/folder
```
4) Install packages from `requirements.txt`
```
pip install -r requirements.txt
```
5) Open bot folder
```
cd bot
```
6) Start bot using raw command or using `start.bat` if you are on Windows
```
python.exe .\main.py --device=0 --weights .\weights\yolov8_zombie_m_v3.pt
```
  Windows
```
start.bat
```

# Enhancements that you can make
1) You can tune DXCam to wait for last frame available, and not spam grab. Or maybe use BetterCam or some other libraries
2) Export yolo model using TensorRT to optimize it's execution on GPU

# Preview
![Preview-ezgif com-cut](https://github.com/user-attachments/assets/5745341b-e7fb-448e-ba9f-a289b229d475)

# Credits
Andrew Wong for [RobloxBot](https://github.com/andrewssdd/RobloxBot) - bot that collects coins in Murder Mystery 2, used as a base, check it out

# Autonavigator for Zombie Rush

This autonavigator automatically set's cursor on position of detected zombies and then you can click to shoot.

Dataset - https://universe.roboflow.com/test-o0ilg/zombie-rush

# Autolabeling
You can use `autolabel.py` to autolabel images at the `images` folder and then upload them to roboflow, with the `labels.txt` file copied there.

# Keys
P - Pause\
R - Resume\
F - Save screenshot to `images` folder for dataset

# Enhancements that you can make
1) Tune DXCam to wait for last frame available, and not spam grab. Maybe use BetterCam or some other libraries
2) Export yolo model using TensorRT to optimize it's execution on GPU

# Preview
![Preview-ezgif com-cut](https://github.com/user-attachments/assets/5745341b-e7fb-448e-ba9f-a289b229d475)

# Credits
Andrew Wong for [RobloxBot](https://github.com/andrewssdd/RobloxBot) - bot that collects coins in Murder Mystery 2, used as a base, check it out

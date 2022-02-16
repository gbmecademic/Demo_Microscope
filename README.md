This repo is for the microscope and microhandling demo of SLAS 2022

# Demo Description
The robot picks a random sample from the 3D printed rack with the gripper. It then shows it in front of the USB microscope where it can move around using the joystick.

## UI
The UI displays the camera feed from the microscope and lets the user pick a random sample, return it to the rack, or start the automode.

## Joystick
The joystick interface is built on the windows dll *windmm.dll* therefore it will only work on a windows machine.

# Work left
While it is functionnal, there is still a lot of work left especially on the error handling. I would also modify the automode to be able to move using the joystick while the automode is on and showing the sample to the microscope. There couls also be a slider to change the speed of the joystick.


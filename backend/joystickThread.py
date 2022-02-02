from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from . import joystick
from time import sleep



class JoystickThread(QThread):
    def __init__(self, robot, lcd_list, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.robot = robot
        self.robotInitPos = self.robot.GetPose()
        self.runFlag = True
        self.joystick = joystick.MecaJoy()
        self.maxOffset = (5,5)
        self.lcdList = lcd_list

    def run(self) -> None:
        commandToSend = [0,0,0,0,0,0]
        while self.runFlag:
            joyData = self.joystick.getinfo()
            joyData[1] = -joyData[1]
            robotPose = self.robot.GetPose()
            poseOffset = [x1 - x2 for (x1, x2) in zip(robotPose, self.robotInitPos)]
            self.lcdList[0].display(poseOffset[0])
            self.lcdList[1].display(poseOffset[1])
            for i in range(2):
                if joyData[i] == 0:
                    commandToSend[i] = joyData[i]
                elif joyData[i] > 0:
                    if poseOffset[i] <= 0:
                        commandToSend[i] = joyData[i]
                    elif poseOffset[i] > 0:
                        if abs(poseOffset[i]) > self.maxOffset[i]:
                            commandToSend[i] = 0
                        else:
                            commandToSend[i] = joyData[i]
                elif joyData[i] < 0:
                    if poseOffset[i] >= 0:
                        commandToSend[i] = joyData[i]
                    elif poseOffset[i] < 0:
                        if abs(poseOffset[i]) > self.maxOffset[i]:
                            commandToSend[i] = 0
                        else:
                            commandToSend[i] = joyData[i]
                    

            self.robot.MoveLinVelWRF(*commandToSend)
            sleep(0.01)
        
        self.lcdList[0].display(0)
        self.lcdList[1].display(0)

    def stop_running(self):
        self.runFlag = False
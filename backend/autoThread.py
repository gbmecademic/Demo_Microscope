from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from time import sleep
from random import randint


class AutoThread(QThread):
    finished = pyqtSignal()
    def __init__(self, robot, tray, wrf, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.robot = robot
        self.tray = tray
        self.goFlag = True
        self.wrf = wrf

    def run(self):
        self.robot.SetJointVel(20)
        self.robot.SetCartLinVel(15)
        self.robot.SetGripperForce(20)
        self.robot.SetGripperVel(20)
        while self.goFlag:
            sampleIndex = randint(0, 24)
            self._move_to_rack()
            self.robot.SetWRF(*self.wrf)
            self._pick_action(self.tray.positions_wrf[sampleIndex])
            self.robot.SetWRF(0,0,0,0,0,0)
            sleep(0.5)
            rackPose = self.robot.GetPose()
            self._move_from_rack()
            self._move_to_micro()
            sleep(5)
            self._move_from_micro()
            self._move_to_rack()
            self._place_action(rackPose)
            self._move_from_rack()

        self.robot.StartOfflineProgram(42)
        self.finished.emit()

    def toggle_off(self):
        self.goFlag = False

    def _pick_action(self, position):
        self.robot.MovePose(*position)
        self.robot.MoveLinRelTRF(9,0,0,0,0,0)
        self.robot.GripperClose()
        self.robot.Delay(0.5)
        self.robot.MoveLinRelTRF(-30,0,0,0,0,0)
        self.robot.MoveLinRelTRF(0,0,-30,0,0,0)
        cp5 = self.robot.SetCheckpoint(5)
        cp5.wait()

    def _place_action(self, position):
        self.robot.MovePose(*position)
        self.robot.MoveLinRelTRF(0,0,30,0,0,0)
        self.robot.MoveLinRelTRF(25,0,0,0,0,0)
        self.robot.GripperOpen()
        self.robot.Delay(0.5)
        self.robot.MoveLinRelTRF(-10,0,0,0,0,0)
        cp3 = self.robot.SetCheckpoint(3)
        cp3.wait()

    def _move_to_micro(self):
        self.robot.MovePose(34.25, -232.218, 197.534, 90, 0, 0)
        self.robot.MovePose(34.25, -210.168, 63.534, 90, 0, 0)
        self.robot.MovePose(34.25, -205.518, 39.334, 90, 0, 0)
        self.robot.MoveLin(121.8, -205.518, 39.334, 90, 0, 0)
        self.robot.MoveLin(121.8, -205.518, 42.199, 90, 0, 0)
        cp2 = self.robot.SetCheckpoint(2)
        cp2.wait()
    
    def _move_from_micro(self):
        self.robot.MoveLin(121.8, -205.518, 39.334, 90, 0, 0)
        self.robot.MoveLin(34.25, -205.518, 39.334, 90, 0, 0)
        self.robot.MovePose(34.25, -210.168, 63.534, 90, 0, 0)
        self.robot.MovePose(34.25, -232.218, 197.534, 90, 0, 0)
        cp6 = self.robot.SetCheckpoint(6)
        cp6.wait()


    def _move_to_rack(self):
        self.robot.MoveJoints(-90, 10, 0, 0, -10, 0)
        self.robot.MoveJoints(-90, -1.431, 68.895, 0, -67.465, 0)
        cp1 = self.robot.SetCheckpoint(1)
        cp1.wait()
    
    def _move_from_rack(self):
        self.robot.MoveJoints(-90, -1.431, 68.895, 0, -67.465, 0)
        self.robot.MoveJoints(-90, 10, 0, 0, -10, -6)
        cp4 = self.robot.SetCheckpoint(4)
        cp4.wait()
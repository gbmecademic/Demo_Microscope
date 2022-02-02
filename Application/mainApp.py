from time import sleep
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QLCDNumber
from PyQt5.QtGui import QPixmap
from frontend import ApplicationWindow
from backend import sampletray, joystickThread, autoThread
from mecademicpy.robot import Robot
import sys
import os
from random import randint

class Application(QtWidgets.QMainWindow, ApplicationWindow.Ui_ApplicationWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.showMaximized()

        # Frontend setup
        self.buttonRetSample.setEnabled(False)
        self.labelJoystick.setStyleSheet("background-color: gray")
        
        current_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        pixmap_logo = QPixmap(os.path.join(parent_dir, 'frontend/images/logoM.png'))
        pixmap_logo = pixmap_logo.scaledToWidth(281)
        self.labelLogo.setPixmap(pixmap_logo)

        self.lcdNumberX.setSegmentStyle(QLCDNumber.Flat)
        self.lcdNumberX.setStyleSheet('background: white; color: black')

        self.lcdNumberY.setSegmentStyle(QLCDNumber.Flat)
        self.lcdNumberY.setStyleSheet('background: white; color: black')
        

        # Backend setup
        self.joystick_status = False
        self.sampleTray = sampletray.SampleTray()
        self.rack_position = [-32.25, -262.478, 87.574, 0, 0, 0]
        self.currentSampleIndex = None
        self.currentSamplePosition = None
        self.robot = Robot()
        self.robot.Connect()
        self.robot.ActivateAndHome()
        self.robot.WaitHomed()
        self.robot.GripperOpen()
        self.robot.SetTRF(37,0,14,0,0,0)
        self.robot.SetJointVel(20)
        self.robot.SetCartLinVel(15)
        self.robot.SetGripperForce(20)
        self.robot.SetGripperVel(20)
        self.joystickThread = None
        self.autoThread = None
        self.autoFlag = True

        # Button connections
        self.comboCameraSelect.currentIndexChanged.connect(self.change_camera)
        self.buttonPickSample.clicked.connect(self.pick_random_sample)
        self.buttonRetSample.clicked.connect(self.place_back_sample)
        self.autoButton.clicked.connect(self._toggle_auto_mode)

        # Testing stuff

    def toggle_joystick(self):
        self.joystick_status = True if not self.joystick_status else False

        if self.joystick_status:
            self.labelJoystick.setStyleSheet("background-color: green")
            self.labelJoystick.setText("Joystick Active")
        else:
            self.labelJoystick.setStyleSheet("background-color: gray")
            self.labelJoystick.setText("Joystick not Active")

    def change_camera(self):
        camera_index = self.comboCameraSelect.currentIndex()
        if self.videoPlayer.cameraIndex == camera_index:
            return
        else:
            self.videoPlayer.change_capture(camera_index)

    def pick_random_sample(self):
        if self.currentSampleIndex is not None:
            return
        else:
            self.buttonPickSample.setEnabled(False)
            self.autoButton.setEnabled(False)
            self.currentSampleIndex = randint(0, 24)
            self._move_to_rack()
            self.robot.SetWRF(*self.rack_position)
            self._pick_action(self.sampleTray.positions_wrf[self.currentSampleIndex])
            self.robot.SetWRF(0,0,0,0,0,0)
            self._move_from_rack()
            self._move_to_micro()
            self.toggle_joystick()
            self.buttonRetSample.setEnabled(True)
            self.joystickThread = joystickThread.JoystickThread(self.robot, [self.lcdNumberX, self.lcdNumberY])
            self.joystickThread.start()

    def place_back_sample(self):
        if self.currentSampleIndex is None:
            return
        else:
            self.buttonRetSample.setEnabled(False)
            self.toggle_joystick()
            self._move_from_micro()
            self._move_to_rack()
            self.robot.SetWRF(*self.rack_position)
            self._place_action()
            self.robot.SetWRF(0,0,0,0,0,0)
            self._move_from_rack()
            self.autoButton.setEnabled(True)
            self.buttonPickSample.setEnabled(True)
            self.currentSampleIndex = None
            self.joystickThread.stop_running()
    
    def _pick_action(self, position):
        self.robot.MovePose(*position)
        self.robot.MoveLinRelTRF(9,0,0,0,0,0)
        self.robot.GripperClose()
        self.robot.Delay(0.5)
        self.robot.MoveLinRelTRF(-30,0,0,0,0,0)
        self.robot.MoveLinRelTRF(0,0,-30,0,0,0)
        cp5 = self.robot.SetCheckpoint(5)
        cp5.wait()
        self.currentSamplePosition = self.robot.GetPose()

    def _place_action(self):
        self.robot.MovePose(*self.currentSamplePosition)
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

    def _toggle_auto_mode(self):
        if self.autoButton.isChecked():
            self.autoFlag = True
            self.buttonPickSample.setEnabled(False)
            self.buttonRetSample.setEnabled(False)
            self.autoThread = autoThread.AutoThread(self.robot, self.sampleTray, self.rack_position)
            self.autoThread.finished.connect(self.wait_finished)
            self.autoThread.start()
        else:
            self.autoThread.toggle_off()
            cp_ext = self.robot.ExpectExternalCheckpoint(42)
            cp_ext.wait()
            self.buttonPickSample.setEnabled(True)
            self.buttonRetSample.setEnabled(True)
    
    def wait_finished(self):
        self.autoFlag = False

if __name__=="__main__":
    app = QApplication(sys.argv)
    a = Application()
    a.show()
    sys.exit(app.exec_())
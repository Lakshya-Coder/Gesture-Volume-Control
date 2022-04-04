import cv2
import numpy as np

import Colors
from HandTrackingModule import HandDetector
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

detector = HandDetector(detectionCon=0.8, maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
volPer = 0
volBar = 400
vol = 0
area = 0

colorVol = Colors.blue

smoothness = 5


def set_color_vol(color=Colors.blue):
    global colorVol
    colorVol = color


def set_volume():
    volume.SetMasterVolumeLevelScalar(volPer / 100, None)
    cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, Colors.green, cv2.FILLED)


def do_all_drawing():
    draw_volume_bar_percentage(img)
    draw_current_volume(img)


def draw_volume_bar_percentage(image):
    cv2.rectangle(image, (50, 150), (85, 400), Colors.green, 3)
    cv2.rectangle(image, (50, int(volBar)), (85, 400), Colors.green, cv2.FILLED)
    cv2.putText(image, f'{int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, Colors.green, 3)


def draw_current_volume(image):
    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(image, f'Vol set : {int(cVol)}', (400, 50), cv2.FONT_HERSHEY_COMPLEX, 1, colorVol, 3)


while True:
    success, img = cap.read()

    # Find Hand
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=True)

    if len(lmList) != 0:
        # Filter based on size
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100

        if 250 < area < 1000:

            # Find distance between index and thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)

            # Convert Volume
            volBar = np.interp(length, [50, 200], [400, 150])
            volPer = np.interp(length, [50, 200], [0, 100])

            # Reduce Resolution to make it smoother
            volPer = smoothness * round(volPer / smoothness)

            # Check finger up
            fingers = detector.fingersUp()

            # If middle finger is down set the volume
            if not fingers[2]:
                set_volume()
                set_color_vol(Colors.green)
            else:
                set_color_vol()

    do_all_drawing()

    cv2.imshow("Image", img)
    cv2.waitKey(1)

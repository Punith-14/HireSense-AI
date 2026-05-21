import cv2
import mediapipe as mp
import pandas as pd
from fer import FER

detector = FER()

print("OpenCV:", cv2.__version__)
print("MediaPipe Working")
print("Pandas Working")
print("FER Working")
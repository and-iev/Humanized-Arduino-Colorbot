import cv2
import numpy as np
import json
from mss import mss


class Screengrabber:
    def __init__(self):
        with open('config.json', 'r') as f:
            cfg = json.load(f)["detection"]

        self.fov = cfg["fov"]
        self.lower = np.array(cfg["lower_color"])
        self.upper = np.array(cfg["upper_color"])
        self.min_size = cfg["min_target_size"]
        self.sct = mss()
        self.monitor = self.sct.monitors[1]
        self.center = (self.monitor['width'] // 2, self.monitor['height'] // 2)

    def get_frame(self):
        region = {
            'left': self.center[0] - self.fov // 2,
            'top': self.center[1] - self.fov // 2,
            'width': self.fov,
            'height': self.fov
        }
        return np.array(self.sct.grab(region))

    def process_frame(self, frame): # using different tactics to isolate colors we need in our captured frame
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None

        valid = []
        for cnt in contours:
            if cv2.contourArea(cnt) > self.min_size:
                M = cv2.moments(cnt) # using moments to calculate center of mass of our contours
                if M['m00'] > 0: # avoiding division by 0 for when mass of contour is 0
                    cx, cy = M['m10'] / M['m00'], M['m01'] / M['m00'] #cx is X-bar where m10 is My and m00 is mass, naturally m01 is Mx and cy is Y-bar
                    score = self._get_score(cnt, cx, cy)
                    valid.append((cnt, cx, cy, score))  # Store score with target

        return max(valid, key=lambda x: x[3])[0:3] if valid else None

    def _get_score(self, cnt, cx, cy):  # this function helps us determine the best next target using size and difference from middle of screen
        dist = np.hypot(cx - self.fov // 2, cy - self.fov // 2) #Euclidian distance formula
        area = cv2.contourArea(cnt)
        return area / (dist ** 1.5 + 1)
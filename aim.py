import time
import math
import json
import serial


class Aimbot:
    def __init__(self, fov):
        # load configuration once at initialization
        with open('config.json', 'r') as f:
            config = json.load(f)
            cfg = config["aim"]
            hw_cfg = config["hardware"]

        # aim control parameters
        self.p_gain = cfg["p_gain"]  # proportional gain Kp
        self.d_gain = cfg["d_gain"]  # derivative gain Kn
        self.max_speed = cfg["max_speed"]  # maximum movement speed (pixels/frame)
        self.stickiness = cfg["stickiness"]  # how strongly we stick to previous target position
        self.deadzone = cfg["deadzone"]  # radius where we consider ourselves "on target" (pixels)


        self.fov_half = fov // 2


        self.serial = serial.Serial(
            hw_cfg["com_port"],
            hw_cfg["baud_rate"]
        )

        # target tracking state
        self.target = None  # current target position (x,y relative to screen center)
        self.prev_err = (0, 0)  # previous error (for D-term calculation)
        self.last_time = 0  # timestamp of last target update

    def update(self, target): # update loop; called every frame
        now = time.time()
        if target:
            self._update_target(target, now)
            self._move()
        elif now - self.last_time < 0.1:
            # target lost recently; continue moving toward last known position
            self._move()
        else:
            # target lost for too long; reset
            self.target = None

    def _update_target(self, target, timestamp):
        cnt, cx, cy = target  # cnt is the contour, (cx,cy) is centroid

        if self.target:
            # apply stickiness by blending new position with previous position
            # stickiness reduces over time since last update (more responsive to new targets)
            stick = self.stickiness * min(1, (timestamp - self.last_time) * 2)
            self.target = (
                cx * (1 - stick) + self.target[0] * stick,  # X-axis blending
                cy * (1 - stick) + self.target[1] * stick  # Y-axis blending
            )
        else:
            # acquiring new target
            self.target = (cx, cy)

        self.last_time = timestamp

    def _move(self):
        if not self.target:
            return
        # calculate error (distance from crosshair to target)
        # err_x: horizontal error (positive = target is right of crosshair)
        # err_y: vertical error (positive = target is below crosshair)
        err_x = self.target[0] - self.fov_half
        err_y = self.target[1] - self.fov_half

        # Check for if we are within the deadzone (close enough to target)
        if abs(err_x) < self.deadzone and abs(err_y) < self.deadzone:
            return  # No need to move

        # PD control Calculation:
        # this creates smooth, controlled movement toward target
        dx = self.p_gain * err_x + self.d_gain * (err_x - self.prev_err[0])
        dy = self.p_gain * err_y + self.d_gain * (err_y - self.prev_err[1])

        # speed limiting (normalize if exceeding max speed)
        speed = math.hypot(dx, dy)
        if speed > self.max_speed:
            ratio = self.max_speed / speed
            dx *= ratio
            dy *= ratio

        self._send(dx, dy)

        # store current error for next frame's D-term calculation
        self.prev_err = (err_x, err_y)

    def _send(self, dx, dy):
        # clamp values to Arduino's expected range (-127 to 127)
        dx = max(-127, min(127, int(dx)))
        dy = max(-127, min(127, int(dy)))

        self.serial.write(bytes([dx & 0xFF, dy & 0xFF]))
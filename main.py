import win32api
import time
from screengrab import Screengrabber
from aim import Aimbot


def main():
    grabber = Screengrabber()
    aimbot = Aimbot(grabber.fov)

    try:
        print("Aimbot active, Hold RMB to aim")
        while True:
            if win32api.GetAsyncKeyState(0x02) < 0:  # right mouse
                frame = grabber.get_frame()
                target = grabber.process_frame(frame)
                aimbot.update(target)

            if win32api.GetAsyncKeyState(0x7B) < 0:  # F12 to exit
                break

            time.sleep(1 / 200)  # 200Hz loop

    finally:
        aimbot.serial.close()


if __name__ == "__main__":
    main()
# DISCLAIMER
**This was never meant to be undetected, and I do not condone any use for gaining an unfair advantage in video games.**

# Goal
Trying to create a more human-like color-based guided aim tool, with overshooting/undershooting, oscillation, and human like target prioritization with a completely external, hardware-based mouse movement method. Attempts at humanization were achieved through different mathematical and physical applications some of which include moments of centers of mass, PD control system (proportional gain and derivative gain), and exponential smoothing.

 ## Pre-Setup intstructions
 - You will need an Arduino Leonardo as well as a USB hostshield
 - Once you have procured the aforementioned items you will need to solder 1 3.3V pad and 2 5V pads on the hostshield.

   ## Steup instructions
   **Install necessary files**
   - Install the necessary requirements by running:
     ```bash
     pip install -r requirements.txt
     ```
   - Download arduino_mouse.ino and upload it to your arduino leonardo, make sure you are able to move your mouse around when it is plugged into the hostshield
   - Make sure to import "USB Host Shield Library 2.0" in your Arduino IDE

   **Configure**
   - Configure config.json depending on your in game sensitivity and other parameters like color target (Default is purple). Editing the values of parameters like stickiness, p_gain, d_gain, and max_speed can help improve speed at the exepsnse of humanization. 
   **Run the colorbot**
     - run the colorbot by running
       ```bash
       python main.py
       ```

     **Demo video**
   https://youtu.be/p9eITEym5O0






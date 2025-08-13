Air-Typing Virtual Keyboard (Prototype)

I made this Python-based virtual keyboard that lets you type in the air using hand gestures via OpenCV (no Mediapipe).  
Finger pointing moves the cursor, palm open hovers/selects, and a fist presses keys.  
Still under training  this is just a prototype, so expect more upgrades soon.

How it Works

- **virtual_keyboard.py** → The main logic for webcam capture, hand detection, gesture recognition, and virtual keyboard rendering.
- **config.py** → Change this if you want to adjust camera index, detection thresholds, keyboard size, debounce timing, etc.

---

  Gestures

- Finger Pointing → Move cursor over virtual keys.
- Palm Open → Hover/select mode.
- Fist (Palm Closed) → Press the selected key.
- Both Palms Up → Exit the program.

---

 Notes
- This is a **prototype**, so detection accuracy and gesture recognition are still under development.
- Works best in well-lit environments with clear hand visibility.

 Project Structure

VIRTUAL-KEYBOARD/
│
├── virtual_keyboard.py  
├── config.py            
├── requirements.txt     
└── README.md            

 Requirements & Dependencies

Before running, make sure you have **Python 3.8+** installed.

Install dependencies using:
```
pip install -r requirements.txt
```
`requirements.txt` should contain:

opencv-python
numpy
cvzone


## 🎯 How to Run

1. Clone the repository

git clone https://github.com/Satishhhh989/Aerotype.git
cd Aerotype


2. **Install dependencies**
```bash
pip install -r requirements.txt
```

Run the program**
bash
python virtual_keyboard.py

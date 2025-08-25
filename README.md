# AEROTYPE (Enhanced Prototype)

This project is a Python-based virtual keyboard that allows you to type in the air using hand gestures.  
It uses a combination of OpenCV-based skin segmentation and Mediapipe hand-tracking for gesture recognition.  
The camera captures your hand movements, and those movements are mapped to a virtual keyboard displayed on the screen.

This is still a prototype version and under active development. Expect upgrades in detection accuracy, gesture recognition, and typing responsiveness in the future.

---

## Features

- Point your finger to move over the virtual keyboard.
- Close your palm (make a fist) to press keys. A double-press system is used to reduce false positives.
- Keep your palm open to enable hover or selection mode.
- Typed text is displayed on-screen, with an option to save it to a file after you exit.
- The keyboard layout, colors, debounce timing, and other settings can be fully customized in the configuration file.
- Works directly with your computer’s webcam.

---

## Project Structure
AEROTYPE
├── virtual_keyboard.py # Main program containing logic for camera input, hand detection, and keyboard rendering
├── enhanced_config.py # Configuration file for adjusting camera index, thresholds, keyboard layout, colors, etc.
├── requirements.txt # List of dependencies
└── README.md # Documentation

---

## Requirements

1. Python version must be **3.8 – 3.10**  
   (Mediapipe does not support Python 3.11 or higher yet).

2. Required Python libraries are listed in `requirements.txt`:


---

## Setting Up Python and Virtual Environment

If you already have Python 3.8 – 3.10 installed, you can skip step 1.

### Step 1. Install Python 3.10  
Download Python 3.10 from the official [Python website](https://www.python.org/downloads/).  
During installation, make sure to select the option "Add to PATH".

### Step 2. Create a Virtual Environment  
It is recommended to use a virtual environment so that dependencies do not conflict with your system Python.
```
# Create a virtual environment named .venv
python -m venv .venv

# Activate on Windows
.venv\Scripts\activate

# Activate on Linux/Mac
source .venv/bin/activate
```
Step 3. Install Dependencies
After activating the virtual environment, install all required libraries:
```pip install -r requirements.txt```



How to Run
1.Clone the repository
```git clone https://github.com/Satishhhh989/Aerotype.git```
```cd Aerotype```
2.Activate the virtual environment
```# Windows
.venv\Scripts\activate
```
```# Linux/Mac
source .venv/bin/activate```

Run the program
python virtual_keyboard.py




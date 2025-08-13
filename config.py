# config.py

VIDEO_SOURCE = "http://192.168.29.146:8080/video"  # Replace with your phone's IP Webcam URL or use integer for webcam index

KEYBOARD_ROWS = [
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Backspace'],
    ['Z', 'X', 'C', 'V', 'B', 'N', 'M', 'Space', 'Enter']
]

KEY_SIZE = (70, 70)
KEY_SPACING = 10
KEYBOARD_TOP_LEFT = (50, 320)

DEBOUNCE_FRAMES = 15
SMOOTHING_FRAMES = 6

SKIN_YCRCB_MIN = (0, 133, 77)
SKIN_YCRCB_MAX = (255, 173, 127)

CONTOUR_MIN_AREA = 1800
FINGER_DEFECT_DEPTH = 18000

HAND_DETECTION_PAD = 0.4  # Ignore upper 40% of frame to avoid face detection

# Colors for UI
COLOR_KEY_BG = (200, 200, 200)
COLOR_KEY_HOVER = (0, 180, 255)
COLOR_KEY_PRESS = (0, 130, 200)
COLOR_TEXT = (0, 0, 0)
COLOR_TEXT_HOVER = (255, 255, 255)

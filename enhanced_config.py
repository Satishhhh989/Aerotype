# enhanced_config.py


# Camera Settings
VIDEO_SOURCE = 0  

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
FLIP_CAMERA = True  

# MediaPipe Hand Detection Settings
HAND_DETECTION_CONFIDENCE = 0.7  
HAND_TRACKING_CONFIDENCE = 0.5   
MAX_HANDS = 1                    

# Gesture Recognition Settings
GESTURE_STABILITY_FRAMES = 3    
CURSOR_SMOOTHING_FRAMES = 5      

# Keyboard Layout Settings
KEYBOARD_LAYOUT = [
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'BACKSPACE'],
    ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
    ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'ENTER'],
    ['SHIFT', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '?'],
    ['SPACE', 'CAPS', 'CLEAR']
]

# Key Sizing (in pixels)
KEY_WIDTH = 60
KEY_HEIGHT = 60
KEY_SPACING = 8
KEYBOARD_START_X = 50
KEYBOARD_START_Y = 300

# Special Key Widths (multiplier of standard key width)
SPECIAL_KEY_WIDTHS = {
    'SPACE': 4.0,
    'BACKSPACE': 1.5,
    'ENTER': 1.5,
    'SHIFT': 1.5,
    'CAPS': 1.2,
    'CLEAR': 1.2
}

# Text Area Settings
TEXT_AREA_HEIGHT = 100
TEXT_AREA_BACKGROUND = (245, 245, 245)
TEXT_AREA_BORDER = (200, 200, 200)
TEXT_COLOR = (50, 50, 50)
MAX_DISPLAY_LINES = 3
MAX_LINE_LENGTH = 60

# Interaction Settings
CLICK_COOLDOWN_FRAMES = 10       
HOVER_DURATION_SECONDS = 1.5     
HOVER_ACTIVATION_DELAY = 0.3     

# Color Themes
COLORS = {
    'key_default': (220, 220, 220),     
    'key_hover': (0, 180, 255),          
    'key_press': (0, 130, 200),          
    'key_active': (100, 200, 100),       
    'text_default': (0, 0, 0),           
    'text_hover': (255, 255, 255),       
    'cursor': (0, 255, 0),               
    'cursor_border': (255, 255, 255),    
    'progress_bar': (0, 255, 0),         
    'progress_bg': (200, 200, 200),      
    'gesture_text': (255, 0, 0),         
        'fps_text': (255, 0, 0),             
        'status_text': (255, 0, 0)
    }

# Gesture Sensitivity Settings
FINGER_DETECTION_THRESHOLD = 0.8     
FIST_DETECTION_THRESHOLD = 0.2       

# File Output Settings
AUTO_SAVE_INTERVAL = 300             
OUTPUT_FILENAME_PREFIX = "virtual_keyboard_text"
OUTPUT_ENCODING = "utf-8"

# Advanced Features
ENABLE_WORD_SUGGESTIONS = False      
ENABLE_SWIPE_GESTURES = False        
ENABLE_VOICE_COMMANDS = False       
ENABLE_AUTO_CORRECT = False          

# Debug Settings
SHOW_HAND_LANDMARKS = True           
SHOW_FPS_COUNTER = True              
SHOW_GESTURE_INFO = True             
VERBOSE_LOGGING = False              

# Performance Settings
TARGET_FPS = 30                      
ENABLE_GPU_ACCELERATION = False      

# Keyboard Shortcuts
SHORTCUTS = {
    's': 'save_text',              
    'c': 'clear_text',               
    'esc': 'exit'                    
}

# Calibration Settings (for different users/setups)
HAND_SIZE_CALIBRATION = 1.0          
DISTANCE_CALIBRATION = 1.0           
LIGHTING_COMPENSATION = 1.0         

# Multi-language Support (Future feature)
SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de']
DEFAULT_LANGUAGE = 'en'

# Accessibility Features
HIGH_CONTRAST_MODE = False           
LARGE_KEY_MODE = False              
AUDIO_FEEDBACK = False               

def get_keyboard_layout():
    """Return the current keyboard layout."""
    return KEYBOARD_LAYOUT

def get_colors():
    """Return the color scheme."""
    return COLORS

def get_special_key_width(key):
    """Get the width multiplier for special keys."""
    return SPECIAL_KEY_WIDTHS.get(key, 1.0)

# Validation functions
def validate_config():
    """Validate configuration values."""
    issues = []
    
    if not (0.0 <= HAND_DETECTION_CONFIDENCE <= 1.0):
        issues.append("HAND_DETECTION_CONFIDENCE must be between 0.0 and 1.0")
    
    if not (0.0 <= HAND_TRACKING_CONFIDENCE <= 1.0):
        issues.append("HAND_TRACKING_CONFIDENCE must be between 0.0 and 1.0")
    
    if HOVER_DURATION_SECONDS < 0.5:
        issues.append("HOVER_DURATION_SECONDS should be at least 0.5 seconds")
    
    if KEY_WIDTH < 30 or KEY_HEIGHT < 30:
        issues.append("Key dimensions should be at least 30 pixels")
    
    return issues

# Auto-validate on import
_validation_issues = validate_config()
if _validation_issues:
    print("Configuration Issues Found:")
    for issue in _validation_issues:
        print(f"  - {issue}")
    print("Please fix these issues for optimal performance.")

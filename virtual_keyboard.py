import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import threading
import time
import datetime
import sys
import math

class CameraStream:
    """Threaded capture for smooth frame retrieval."""
    def __init__(self, source):
        try:
            source = int(source)
        except ValueError:
            pass
        self.cap = cv2.VideoCapture(source)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.frame = None
        self.stopped = False
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame

    def read(self):
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        self.stopped = True
        if self.cap:
            self.cap.release()


class HandTracker:
    """MediaPipe hand tracking with gesture recognition."""
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
    def detect_gesture(self, landmarks):
        """Detect gesture based on hand landmarks."""
       
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_tip = landmarks[8]
        index_pip = landmarks[6]
        index_mcp = landmarks[5]
        middle_tip = landmarks[12]
        middle_pip = landmarks[10]
        ring_tip = landmarks[16]
        ring_pip = landmarks[14]
        pinky_tip = landmarks[20]
        pinky_pip = landmarks[18]
        wrist = landmarks[0]
        
        # Calculate if fingers are extended
        fingers_up = []
        
        
        if thumb_tip.x > thumb_ip.x:  
            fingers_up.append(thumb_tip.x > thumb_ip.x)
        else:  # Left hand
            fingers_up.append(thumb_tip.x < thumb_ip.x)
            
        # Other fingers (check if tip is above pip)
        finger_tips = [index_tip, middle_tip, ring_tip, pinky_tip]
        finger_pips = [index_pip, middle_pip, ring_pip, pinky_pip]
        
        for tip, pip in zip(finger_tips, finger_pips):
            fingers_up.append(tip.y < pip.y)
            
        # Gesture recognition
        total_fingers = sum(fingers_up)
        
        if total_fingers == 0:
            return "FIST", index_tip
        elif total_fingers == 1 and fingers_up[1]:  # Only index finger
            return "POINT", index_tip
        elif total_fingers == 2 and fingers_up[1] and fingers_up[2]:  # Index and middle
            return "PEACE", index_tip
        elif total_fingers >= 4:
            return "OPEN_PALM", index_tip
        else:
            return "PARTIAL", index_tip
    
    def process_frame(self, frame):
        """Process frame and return hand landmarks and gesture."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Draw landmarks
            self.mp_draw.draw_landmarks(
                frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
            
            
            gesture, cursor_landmark = self.detect_gesture(hand_landmarks.landmark)
            
            # Convert normalized coordinates to pixel coordinates
            h, w = frame.shape[:2]
            cursor_pos = (int(cursor_landmark.x * w), int(cursor_landmark.y * h))
            
            return gesture, cursor_pos, hand_landmarks
        
        return None, None, None


class AdvancedVirtualKeyboard:
    
    def __init__(self):
        self.text = ""
        self.cursor_pos = 0
        self.hovered_key = None
        self.pressed_key = None
        self.keyboard_rects = []
        self.special_keys = {}
        self.shift_active = False
        self.caps_lock = False
        self.build_keyboard()
        
        # Hover timing for click-less typing
        self.hover_start_time = 0
        self.hover_duration_threshold = 1.5  # seconds
        self.hover_key = None
        
    def build_keyboard(self):
        """Build keyboard layout with special keys."""
        self.keyboard_rects = []
        self.special_keys = {}
        
        # Keyboard rows with special key indicators
        rows = [
            ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'BACKSPACE'],
            ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'ENTER'],
            ['SHIFT', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '?'],
            ['SPACE', 'CAPS', 'CLEAR']
        ]
        
        key_width = 60
        key_height = 60
        key_spacing = 8
        start_x = 50
        start_y = 300
        
        y = start_y
        for row in rows:
            x = start_x
            for key in row:
                # Special key sizing
                if key == 'SPACE':
                    width = key_width * 4
                elif key in ['BACKSPACE', 'ENTER', 'SHIFT']:
                    width = key_width * 1.5
                elif key == 'CAPS':
                    width = key_width * 1.2
                elif key == 'CLEAR':
                    width = key_width * 1.2
                else:
                    width = key_width
                    
                rect = (int(x), int(y), int(width), key_height, key)
                self.keyboard_rects.append(rect)
                
                # Store special keys for easy access
                if key in ['SHIFT', 'CAPS', 'BACKSPACE', 'ENTER', 'SPACE', 'CLEAR']:
                    self.special_keys[key] = rect
                
                x += width + key_spacing
            y += key_height + key_spacing
    
    def draw(self, frame):
        """Draw keyboard and text area."""
        # Text area background
        cv2.rectangle(frame, (0, 0), (1280, 100), (245, 245, 245), -1)
        cv2.rectangle(frame, (0, 0), (1280, 100), (200, 200, 200), 2)
        
        # Display text with cursor
        display_text = self.text if self.text else "Start typing with gestures..."
        text_with_cursor = display_text[:self.cursor_pos] + "|" + display_text[self.cursor_pos:]
        
        # Handle text wrapping
        lines = text_with_cursor.split('\n')
        y_offset = 30
        for line in lines[:3]:  # Show max 3 lines
            if len(line) > 60:  # Wrap long lines
                line = line[:57] + "..."
            cv2.putText(frame, line, (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (50, 50, 50), 2)
            y_offset += 25
        
        # Status indicators
        status_text = []
        if self.caps_lock:
            status_text.append("CAPS")
        if self.shift_active:
            status_text.append("SHIFT")
        
        if status_text:
            cv2.putText(frame, " | ".join(status_text), (1000, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
        
        # Draw keyboard
        for (x, y, w, h, label) in self.keyboard_rects:
            # Determine colors
            if self.pressed_key == label:
                bg_color = (0, 130, 200)  # Blue when pressed
                text_color = (255, 255, 255)
            elif self.hovered_key == label:
                bg_color = (0, 180, 255)  # Light blue when hovered
                text_color = (255, 255, 255)
            elif label == 'SHIFT' and self.shift_active:
                bg_color = (100, 200, 100)  # Green when active
                text_color = (0, 0, 0)
            elif label == 'CAPS' and self.caps_lock:
                bg_color = (100, 200, 100)  # Green when active
                text_color = (0, 0, 0)
            else:
                bg_color = (220, 220, 220)  # Default gray
                text_color = (0, 0, 0)
            
            # Draw key
            cv2.rectangle(frame, (x, y), (x + w, y + h), bg_color, -1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 2)
            
            # Draw text
            display_label = self.get_key_display_text(label)
            text_size = cv2.getTextSize(display_label, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)[0]
            text_x = x + (w - text_size[0]) // 2
            text_y = y + (h + text_size[1]) // 2
            cv2.putText(frame, display_label, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, text_color, 2)
        
        # Draw hover progress bar if hovering
        if self.hover_key and time.time() - self.hover_start_time > 0.3:
            progress = min((time.time() - self.hover_start_time) / self.hover_duration_threshold, 1.0)
            bar_width = 300
            bar_height = 10
            bar_x = (1280 - bar_width) // 2
            bar_y = 250
            
            # Progress bar background
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (200, 200, 200), -1)
            # Progress bar fill
            cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_width * progress), bar_y + bar_height), (0, 255, 0), -1)
            # Progress bar text
            cv2.putText(frame, f"Hovering: {self.hover_key}", (bar_x, bar_y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    def get_key_display_text(self, key):
        """Get display text for key considering shift/caps state."""
        if key in ['BACKSPACE', 'ENTER', 'SHIFT', 'CAPS', 'SPACE', 'CLEAR']:
            return key
        elif key.isalpha():
            if self.caps_lock or self.shift_active:
                return key.upper()
            else:
                return key.lower()
        else:
            return key
    
    def key_at_position(self, x, y):
        """Find which key is at the given position."""
        for (kx, ky, kw, kh, label) in self.keyboard_rects:
            if kx <= x <= kx + kw and ky <= y <= ky + kh:
                return label
        return None
    
    def type_key(self, key_label):
        """Handle key press with special key logic."""
        if key_label == "BACKSPACE":
            if self.cursor_pos > 0:
                self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                self.cursor_pos -= 1
        elif key_label == "SPACE":
            self.text = self.text[:self.cursor_pos] + " " + self.text[self.cursor_pos:]
            self.cursor_pos += 1
        elif key_label == "ENTER":
            self.text = self.text[:self.cursor_pos] + "\n" + self.text[self.cursor_pos:]
            self.cursor_pos += 1
        elif key_label == "SHIFT":
            self.shift_active = not self.shift_active
        elif key_label == "CAPS":
            self.caps_lock = not self.caps_lock
        elif key_label == "CLEAR":
            self.text = ""
            self.cursor_pos = 0
        else:
            # Regular character
            char = self.get_key_display_text(key_label)
            if char and len(char) == 1:
                self.text = self.text[:self.cursor_pos] + char + self.text[self.cursor_pos:]
                self.cursor_pos += 1
                
                # Reset shift after typing a character
                if self.shift_active:
                    self.shift_active = False
    
    def update_hover(self, key):
        """Update hover state for click-less typing."""
        current_time = time.time()
        
        if key != self.hover_key:
            self.hover_key = key
            self.hover_start_time = current_time
        elif key and (current_time - self.hover_start_time) >= self.hover_duration_threshold:
            # Auto-type after hovering
            self.type_key(key)
            self.hover_start_time = current_time + 1  # Prevent immediate re-trigger


def save_text_to_file(text):
    """Save typed text to file."""
    if len(text.strip()) == 0:
        print("No text to save.")
        return
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"virtual_keyboard_text_{timestamp}.txt"
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Text saved to {filename}")
    except Exception as e:
        print(f"Error saving file: {e}")


def main():
    # Configuration
    VIDEO_SOURCE = 0  # Change this to your  camera source
    # VIDEO_SOURCE = 0  # Use this for webcam
    
    # Initialize components
    stream = CameraStream(VIDEO_SOURCE)
    hand_tracker = HandTracker()
    keyboard = AdvancedVirtualKeyboard()
    
    # Smoothing for cursor
    cursor_history = deque(maxlen=5)
    
    # Control variables
    last_gesture = None
    gesture_stable_count = 0
    gesture_stability_threshold = 3
    
    # Click detection
    click_cooldown = 0
    click_cooldown_frames = 10
    
    print("Enhanced Virtual Keyboard with MediaPipe")
    print("Gestures:")
    print("- POINT: Move cursor")
    print("- FIST: Click key")
    print("- PEACE: Right-click menu (future feature)")
    print("- OPEN_PALM: Hover mode (auto-type)")
    print("- Press ESC to exit")
    
    frame_count = 0
    fps_counter = deque(maxlen=30)
    
    try:
        while True:
            start_time = time.time()
            frame = stream.read()
            if frame is None:
                continue
            
            frame = cv2.flip(frame, 1)  # Mirror for natural interaction
            frame_height, frame_width = frame.shape[:2]
            
            # Process hand tracking
            gesture, cursor_pos, hand_landmarks = hand_tracker.process_frame(frame)
            
            # Smooth cursor movement
            if cursor_pos:
                cursor_history.append(cursor_pos)
                if len(cursor_history) >= 3:
                    smooth_x = int(np.mean([pos[0] for pos in cursor_history]))
                    smooth_y = int(np.mean([pos[1] for pos in cursor_history]))
                    cursor_pos = (smooth_x, smooth_y)
                
                # Draw cursor
                cv2.circle(frame, cursor_pos, 12, (0, 255, 0), -1)
                cv2.circle(frame, cursor_pos, 15, (255, 255, 255), 2)
            
            # Gesture stability check
            if gesture == last_gesture:
                gesture_stable_count += 1
            else:
                gesture_stable_count = 0
                last_gesture = gesture
            
            # Handle interactions
            keyboard.hovered_key = None
            keyboard.pressed_key = None
            
            if cursor_pos and gesture_stable_count >= gesture_stability_threshold:
                hovered_key = keyboard.key_at_position(*cursor_pos)
                keyboard.hovered_key = hovered_key
                
                if gesture == "FIST" and click_cooldown <= 0:
                    if hovered_key:
                        keyboard.type_key(hovered_key)
                        keyboard.pressed_key = hovered_key
                        click_cooldown = click_cooldown_frames
                        print(f"Typed: {hovered_key}")
                
                elif gesture == "OPEN_PALM":
                    # Hover mode for hands-free typing
                    if hovered_key:
                        keyboard.update_hover(hovered_key)
                else:
                    keyboard.hover_key = None
            
            # Update cooldowns
            if click_cooldown > 0:
                click_cooldown -= 1
            
            # Draw UI
            keyboard.draw(frame)
            
            # Display gesture and FPS info
            info_y = 120
            if gesture:
                cv2.putText(frame, f"Gesture: {gesture}", (10, info_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # Calculate and display FPS
            end_time = time.time()
            fps = 1.0 / (end_time - start_time) if (end_time - start_time) > 0 else 0
            fps_counter.append(fps)
            avg_fps = np.mean(fps_counter)
            
            cv2.putText(frame, f'FPS: {avg_fps:.1f}', (1100, 120), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
            
            # Show frame
            cv2.imshow("Enhanced Virtual Keyboard", frame)
            
            # Handle exit
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC key
                break
            elif key == ord('s'):  # Save text
                save_text_to_file(keyboard.text)
            
            frame_count += 1
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Cleanup
        stream.stop()
        cv2.destroyAllWindows()
        
        # Ask to save text
        if keyboard.text.strip():
            while True:
                try:
                    choice = input("Save typed text to file? (y/n): ").strip().lower()
                    if choice == 'y':
                        save_text_to_file(keyboard.text)
                        break
                    elif choice == 'n':
                        print("Text not saved.")
                        break
                    else:
                        print("Please enter 'y' or 'n'.")
                except (EOFError, KeyboardInterrupt):
                    print("\nGoodbye!")
                    break
        
        print("Virtual keyboard session ended.")


if __name__ == "__main__":
    main()

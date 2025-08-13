import cv2
import numpy as np
from collections import deque
import threading
import config
import imutils
import sys
import time
import datetime

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


def detect_hand(frame):
    ycrcb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCrCb)
    mask = cv2.inRange(ycrcb, config.SKIN_YCRCB_MIN, config.SKIN_YCRCB_MAX)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mask = cv2.erode(mask, kernel, iterations=1)
    mask = cv2.dilate(mask, kernel, iterations=2)
    mask = cv2.GaussianBlur(mask, (7, 7), 0)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest) > config.CONTOUR_MIN_AREA:
            bbox = cv2.boundingRect(largest)
            return mask, largest, bbox
    return mask, None, None


def get_gesture_and_fingertip(contour, frame):
    hull_indices = cv2.convexHull(contour, returnPoints=False)
    gesture = "Unknown"
    fingertip = None

    if hull_indices is not None and len(hull_indices) > 3:
        defects = cv2.convexityDefects(contour, hull_indices)
        fingertip_candidates = []
        cnt_defects = 0

        if defects is not None:
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])

                if d > config.FINGER_DEFECT_DEPTH:
                    cnt_defects += 1
                    fingertip_candidates.extend([start, end])

            if cnt_defects >= 4:
                gesture = "Palm Open"
            elif cnt_defects in [1, 2]:
                gesture = "Finger Pointing"
            else:
                gesture = "Palm Closed"

            if fingertip_candidates:
                fingertip = min(fingertip_candidates, key=lambda p: p[1])

            cv2.drawContours(frame, [cv2.convexHull(contour)], -1, (0, 255, 255), 2)
            if fingertip:
                cv2.circle(frame, fingertip, 15, (0, 255, 0), 3)
        else:
            gesture = "Palm Closed"

    return gesture, fingertip


class KeyDebounce:
    def __init__(self, debounce_frames):
        self.last_pressed_frame = -debounce_frames
        self.debounce_frames = debounce_frames

    def ready(self, frame_index):
        return (frame_index - self.last_pressed_frame) > self.debounce_frames

    def update(self, frame_index):
        self.last_pressed_frame = frame_index


class VirtualKeyboard:
    def __init__(self):
        self.text = ""
        self.hovered_key = None
        self.pressed_key = None
        self.keyboard_rects = []
        self.build_keyboard()

    def build_keyboard(self):
        self.keyboard_rects = []
        y = config.KEYBOARD_TOP_LEFT[1]
        for row in config.KEYBOARD_ROWS:
            x = config.KEYBOARD_TOP_LEFT[0]
            for key in row:
                w, h = config.KEY_SIZE
                if key == "Space":
                    key_size = (w * 3 + config.KEY_SPACING * 2, h)
                elif key == "Backspace":
                    key_size = (int(w * 1.6), h)
                elif key == "Enter":
                    key_size = (int(w * 1.8), h)
                else:
                    key_size = (w, h)

                self.keyboard_rects.append((x, y, int(key_size[0]), int(key_size[1]), key))
                x += key_size[0] + config.KEY_SPACING
            y += config.KEY_SIZE[1] + config.KEY_SPACING

    def draw(self, frame):
        cv2.rectangle(frame, (0, 0), (1280, 70), (245, 245, 245), -1)
        display_text = self.text if self.text else "Typing area..."
        cv2.putText(frame, display_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (50, 50, 50), 3)

        for (x, y, w, h, label) in self.keyboard_rects:
            if self.pressed_key == label:
                bg_color = config.COLOR_KEY_PRESS
                text_color = config.COLOR_TEXT_HOVER
            elif self.hovered_key == label:
                bg_color = config.COLOR_KEY_HOVER
                text_color = config.COLOR_TEXT_HOVER
            else:
                bg_color = config.COLOR_KEY_BG
                text_color = config.COLOR_TEXT

            cv2.rectangle(frame, (x, y), (x + w, y + h), bg_color, -1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 100, 100), 2)

            text_pos = (x + int(w / 8), y + int(h * 0.65))
            cv2.putText(frame, label, text_pos, cv2.FONT_HERSHEY_SIMPLEX, 1.3, text_color, 2)

    def key_at_position(self, x, y):
        for (kx, ky, kw, kh, label) in self.keyboard_rects:
            if kx <= x <= kx + kw and ky <= y <= ky + kh:
                return label
        return None

    def type_key(self, key_label):
        if key_label == "Backspace":
            self.text = self.text[:-1]
        elif key_label == "Space":
            self.text += " "
        elif key_label == "Enter":
            self.text += "\n"
        else:
            self.text += key_label

def ask_save_text(text):
    if len(text.strip()) == 0:
        print("No text typed; nothing to save.")
        return
    while True:
        choice = input("Do you want to save the typed text to a file? (y/n): ").strip().lower()
        if choice == 'y':
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"typed_text_{timestamp}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Text saved to {filename}")
            break
        elif choice == 'n':
            print("Text not saved.")
            break
        else:
            print("Please enter 'y' or 'n'.")

def scan_for_pointer(stream, min_frames=30):
    fingertip_history = deque(maxlen=config.SMOOTHING_FRAMES)
    valid_count = 0

    print("Show your pointing finger to start typing...")

    while True:
        frame = stream.read()
        if frame is None:
            continue
        frame = imutils.resize(frame, width=1280)
        crop_top = int(config.HAND_DETECTION_PAD * frame.shape[0])
        roi_frame = frame[crop_top:, :]

        mask, contour, bbox = detect_hand(roi_frame)

        if contour is not None:
            gesture, fingertip = get_gesture_and_fingertip(contour, roi_frame)
            if gesture == "Finger Pointing" and fingertip is not None:
                fingertip_pos = (fingertip[0], fingertip[1] + crop_top)
                fingertip_history.append(fingertip_pos)
                if len(fingertip_history) == config.SMOOTHING_FRAMES:
                    valid_count += 1
                else:
                    valid_count = 0
            else:
                valid_count = 0
        else:
            valid_count = 0

        cv2.putText(frame, "Show your pointing finger to start typing...", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Pointer Scan", frame)

        if valid_count >= min_frames:
            cv2.destroyWindow("Pointer Scan")
            print("Pointer verified! Starting virtual keyboard...")
            break

        if cv2.waitKey(1) & 0xFF == 27:
            print("Exit requested during pointer scan.")
            stream.stop()
            cv2.destroyAllWindows()
            sys.exit(0)

def main():
    stream = CameraStream(config.VIDEO_SOURCE)
    scan_for_pointer(stream)

    keyboard = VirtualKeyboard()
    debounce = KeyDebounce(config.DEBOUNCE_FRAMES)

    frame_index = 0
    fingertip_history = deque(maxlen=config.SMOOTHING_FRAMES)
    running = True

    DOUBLE_PRESS_TIMEOUT_FRAMES = 15  # About 0.5 sec for double press
    last_pressed_key = None
    last_pressed_frame = -DOUBLE_PRESS_TIMEOUT_FRAMES - 1

    stable_pos = None
    stable_counter = 0
    stable_threshold = 5

    while running:
        frame = stream.read()
        if frame is None:
            continue
        frame = imutils.resize(frame, width=1280)

        crop_top = int(config.HAND_DETECTION_PAD * frame.shape[0])
        roi_frame = frame[crop_top:, :]

        mask, contour, bbox = detect_hand(roi_frame)

        gesture = None
        fingertip_pos = None

        if contour is not None:
            gesture, fingertip = get_gesture_and_fingertip(contour, roi_frame)
            if fingertip:
                fingertip_pos = (fingertip[0], fingertip[1] + crop_top)
                fingertip_history.append(fingertip_pos)
                smooth_pos = np.mean(fingertip_history, axis=0).astype(int)
            else:
                x, y, w, h = bbox
                fingertip_pos = (x + w // 2, y + h // 2 + crop_top)
                fingertip_history.append(fingertip_pos)
                smooth_pos = np.mean(fingertip_history, axis=0).astype(int)

            cv2.rectangle(frame,
                          (bbox[0], bbox[1] + crop_top),
                          (bbox[0] + bbox[2], bbox[1] + bbox[3] + crop_top),
                          (0, 255, 0), 2)
        else:
            gesture = None
            fingertip_pos = None
            fingertip_history.clear()
            smooth_pos = None

        keyboard.hovered_key = None
        keyboard.pressed_key = None

        if smooth_pos is not None:
            hovered = keyboard.key_at_position(*smooth_pos)
            keyboard.hovered_key = hovered

            # Cursor stability logic
            if hovered is not None:
                if stable_pos is None or np.linalg.norm(np.array(stable_pos) - smooth_pos) > 15:
                    stable_pos = smooth_pos
                    stable_counter = 0
                else:
                    stable_counter += 1

                final_cursor_pos = stable_pos if stable_counter >= stable_threshold else smooth_pos
            else:
                stable_pos = None
                stable_counter = 0
                final_cursor_pos = smooth_pos

            cv2.circle(frame, tuple(final_cursor_pos), 14, (0, 120, 255), 3)

            # Double press detection logic:
            key_pressed_now = False
            if hovered and gesture == "Palm Closed":
                if (hovered == last_pressed_key) and ((frame_index - last_pressed_frame) <= DOUBLE_PRESS_TIMEOUT_FRAMES):
                    # Double press detected -> type the key
                    keyboard.type_key(hovered)
                    keyboard.pressed_key = hovered
                    key_pressed_now = True
                    last_pressed_key = None  # Reset to wait for next double press
                    last_pressed_frame = -DOUBLE_PRESS_TIMEOUT_FRAMES - 1
                else:
                    # Mark this as first press candidate
                    last_pressed_key = hovered
                    last_pressed_frame = frame_index
            elif (frame_index - last_pressed_frame) > DOUBLE_PRESS_TIMEOUT_FRAMES:
                last_pressed_key = None  # Reset if timeout passed without second press

        else:
            stable_pos = None
            stable_counter = 0
            last_pressed_key = None

        fps = int(cv2.getTickFrequency() / (cv2.getTickCount() % cv2.getTickFrequency()) + 1)
        cv2.putText(frame, f'FPS: {fps}', (1100, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

        keyboard.draw(frame)

        cv2.imshow("Virtual Keyboard", frame)
        cv2.imshow("Skin Mask", mask)

        key = cv2.waitKey(1) & 0xFF
        if key == 27 or cv2.getWindowProperty("Virtual Keyboard", cv2.WND_PROP_VISIBLE) < 1:
            running = False

        frame_index += 1

    stream.stop()
    cv2.destroyAllWindows()

    # After exit, ask if user wants to save the text
    ask_save_text(keyboard.text)

    sys.exit(0)


if __name__ == "__main__":
    main()
#it uses my mobile camera for tthe live preview 
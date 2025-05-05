import numpy as np
import cv2
import skimage
from skimage import img_as_ubyte, morphology
import time

def detect_parking_spots(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 104, 255, cv2.THRESH_BINARY)
    morphology.closing(binary, morphology.disk(10))
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    parking_spots = {}
    spot_label = ord('A')
    for i, contour in enumerate(contours):
        approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
        if len(approx) == 4:
            (x, y, w, h) = cv2.boundingRect(approx)
            aspect_ratio = w / float(h)
            if aspect_ratio > 1 and aspect_ratio < 3:
                if i % 2 == 0:
                    parking_spots[chr(spot_label)] = [x, y, w, h]
                    spot_label += 1
    print(f"Detected {len(parking_spots)} parking spots")
    return parking_spots

def is_inside(spot, point):
    x, y, w, h = spot
    px, py = point
    return x <= px <= x + w and y <= py <= y + h

def detect_car_on_spot(keypoints, parking_data, parking_status, spot_timers, registration_plates):
    for keypoint in keypoints:
        kp_x, kp_y = int(keypoint.pt[0]), int(keypoint.pt[1])
        for spot_label, spot in parking_data.items():
            if is_inside(spot, (kp_x, kp_y)):
                if parking_status[spot_label] is None:
                    parking_status[spot_label] = registration_plates.pop(0) if registration_plates else "Unknown"
                    spot_timers[spot_label] = time.time()
                    print(f"Miejsce {spot_label} zostało zajęte")
                else:
                    spot_timers[spot_label] = time.time()

def update_parking_status(parking_status, spot_timers, timeout=1.7):
    current_time = time.time()
    for spot_label in parking_status:
        if parking_status[spot_label] is not None and spot_timers[spot_label] and current_time - spot_timers[spot_label] > timeout:
            print(f"Miejsce {spot_label} stało się wolne")
            parking_status[spot_label] = None
            spot_timers[spot_label] = None

def threshold(img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 95, 255, cv2.THRESH_BINARY)
    return cv2.bitwise_not(binary)

def entry_gate(frame, keypoints, gate_open, gate_open_time):
    gate_color = (0, 255, 0) if gate_open else (0, 0, 255)
    if gate_open:
        cv2.line(frame, (90, 470), (90, 390), gate_color, 5)
    else:
        cv2.line(frame, (90, 470), (170, 470), gate_color, 5)

    for keypoint in keypoints:
        x, y = keypoint.pt
        if abs(x - 90) < 50 and abs(y - 470) < 80:
            gate_open = True
            gate_open_time = time.time()

    if gate_open and time.time() - gate_open_time > 4:
        gate_open = False
    
    return gate_open, gate_open_time

def exit_gate(frame, keypoints, gate_open, gate_open_time):
    gate_color = (0, 255, 0) if gate_open else (0, 0, 255)
    if gate_open:
        cv2.line(frame, (420, 580), (420, 500), gate_color, 5)
    else:
        cv2.line(frame, (340, 580), (420, 580), gate_color, 5)

    for keypoint in keypoints:
        x, y = keypoint.pt
        if abs(x - 340) < 50 and abs(y - 580) < 100:
            gate_open = True
            gate_open_time = time.time()

    if gate_open and time.time() - gate_open_time > 4:
        gate_open = False
    
    return gate_open, gate_open_time

def detect_collision(keypoints):
    global collision_events
    sizes = [kp.size for kp in keypoints]
    if sizes:
        max_size = max(sizes)
        mean_size = np.mean(sizes)
        if max_size > 1.3 * mean_size:
            largest_kp = max(keypoints, key=lambda kp: kp.size)
            x, y = int(largest_kp.pt[0]), int(largest_kp.pt[1])
            if all(abs(cx - x) > 15 or abs(cy - y) > 15 for cx, cy in collision_events):
                collision_events.append((x, y))
                print(f"Wykryto możliwą stłuczkę na pozycji: ({x}, {y})")

# Video path
video_path = "C:/Users/KOMP/Desktop/studia/5 SEMESTR/PSIO - przetwarzanie obrazow/projekt_parking/autka4.mp4"
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Cannot open video")
    exit()

ret, frame = cap.read()
if not ret:
    print("Cannot read frame from video")
    exit()

frame = cv2.resize(frame, (480, 640))
parking_data = detect_parking_spots(frame)

params = cv2.SimpleBlobDetector_Params()
params.filterByArea = True
params.minArea = 2000
params.maxArea = 20000
params.filterByCircularity = True
params.minCircularity = 0.2
params.filterByConvexity = True
params.minConvexity = 0.5
params.filterByInertia = True
params.minInertiaRatio = 0.01

detector = cv2.SimpleBlobDetector_create(params)

collision_events = []

registration_plates = ["EL 1111S", "EL 2222S", "EL 5555S", "EL 6666S"]
parking_status = {spot: None for spot in parking_data}
spot_timers = {spot: None for spot in parking_data}

entry_gate_open = False
entry_gate_open_time = 0
exit_gate_open = False
exit_gate_open_time = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_resized = cv2.resize(frame, (480, 640))
    binary = threshold(frame_resized)
    binary_processed = morphology.remove_small_objects(
        morphology.dilation(morphology.erosion(binary, morphology.disk(2)), morphology.disk(3))
    )

    keypoints = detector.detect(binary_processed)
    
    entry_gate_open, entry_gate_open_time = entry_gate(frame_resized, keypoints, entry_gate_open, entry_gate_open_time)

    detect_car_on_spot(keypoints, parking_data, parking_status, spot_timers, registration_plates)

    update_parking_status(parking_status, spot_timers)

    detect_collision(keypoints)
    
    exit_gate_open, exit_gate_open_time = exit_gate(frame_resized, keypoints, exit_gate_open, exit_gate_open_time)

    for spot_label, spot in parking_data.items():
        x, y, w, h = spot
        color = (0, 0, 255) if parking_status[spot_label] else (0, 255, 0)
        cv2.rectangle(frame_resized, (x, y), (x + w, y + h), color, 2)

    im_with_keypoints = cv2.drawKeypoints(
        frame_resized, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    )
    cv2.imshow("Frame", im_with_keypoints)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

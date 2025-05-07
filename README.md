# Parking Monitoring System

## 📌 Project Description

This project monitors a small parking lot with a capacity of up to 8 vehicles (up to 4 simultaneously in use). The system performs:

- Entry and exit logging
- Collision detection
- Parking space tracking
- Timestamp recording for each parking event

Only authorized vehicles are allowed to enter. Unauthorized access attempts are also recorded in the database.

---
## Program showcase

- Car enters the parking lot
  
![image](https://github.com/user-attachments/assets/53ca9a4b-a756-4e9a-b3c8-aa5451f93483)

![image](https://github.com/user-attachments/assets/dcf310de-9fd9-4a6c-99e2-d26a9195924d)

- Car takes a spot
  
![image](https://github.com/user-attachments/assets/a58bf6ac-3a22-4832-a7b6-22111bbd7cec)

![image](https://github.com/user-attachments/assets/dd4966fe-6c36-448f-ade6-6dc46412c1b3)

- Unsuccessful entry attempt
  
![image](https://github.com/user-attachments/assets/ca792f90-9895-420a-9cee-fbb0883fa5ef)

![image](https://github.com/user-attachments/assets/ea32b44a-1d4a-4de7-845d-d64172f59e54)

- Collision

![image](https://github.com/user-attachments/assets/632dbb6d-ab1e-4d9b-ac4b-5b1b9ba232ce)

![image](https://github.com/user-attachments/assets/700837de-d722-4518-ba1b-fb61d604c921)


- Car leaves the parking lot

![image](https://github.com/user-attachments/assets/4020535b-76cf-4e00-a371-e69543e84a02)

![image](https://github.com/user-attachments/assets/ab12c186-0609-42bc-96fb-bed92edcb187)


---
## 🧰 Technologies Used

- **Language**: Python
- **Database**: SQLite
- **Libraries**:
  - `OpenCV` – image processing, vehicle detection
  - `NumPy` – matrix operations
  - `scikit-image` – image enhancement and morphology
- **OCR Tools**:
  - `Template Matching` (final choice)
  - Previously tested: `EasyOCR`, `pytesseract`

---

## 🧱 Architecture

A **monolithic** system with two main modules:

- **Image Processing Module**  
  Detects vehicles, license plates, parking spots, collisions, and controls entry/exit gates.

- **Database Module** (`db.py`)  
  Handles vehicle authorization, event logging, and parking status updates.

---

## 🗃️ Database Schema

- **`car_permission`**
  - `registration_number` – vehicle plate number
  - `permission` – boolean (authorized or not)
  - `image_path` – reference photo of vehicle

- **`parking_status`**
  - `parking_spot` – spot label (A–H)
  - `registration_number` – vehicle occupying the spot (NULL if free)

- **`events`**
  - Logs all events: entries, exits, unauthorized attempts, collisions

---

## ⚙️ Key Methods

- **`detect_parking_spots(image)`**  
  Identifies parking spaces using image thresholding and contour detection.

- **`detect_car_on_spot()`**  
  Associates vehicles with specific spots using keypoint matching.

- **`update_parking_status()`**  
  Updates spot status based on timers.

- **`match_plate(screenshot_path, plates_dict)`**  
  Matches license plates with stored templates.

- **`entry_gate()` / `exit_gate()`**  
  Manages gate control logic and triggers screenshots.

- **`detect_collision()`**  
  Detects unusual blob activity indicating potential collisions.

---

## ⚠️ Limitations

- **Single vehicle tracking**: Only one vehicle can be moving in the parking lot at a time.
- **Template dependency**: Matching requires predefined plate templates, which limits scalability.
- **OCR Inefficiency**: Poor results from OCR libraries due to image quality and vertical plate orientation.

---

## ✅ Conclusions

The system fulfills its original functional goals, such as tracking vehicle movements and logging parking events. Due to limitations with OCR accuracy, template matching was used instead. While effective for demonstrations, real-world deployment would require more robust multi-vehicle tracking and advanced OCR solutions.


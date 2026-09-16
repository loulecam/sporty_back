# AI Sport Coach

Real-time sport coaching application using **computer vision** to detect and count physical exercises from camera frames.

The project uses **MediaPipe Pose** to detect human body landmarks and analyzes their positions and angles to recognize exercises such as **biceps curls** and **squats**.

A Flask backend communicates with the frontend in real time using **Socket.IO**, allowing exercise counters to be updated as movements are detected.

---

## Overview

The application analyzes images captured by a user's camera and determines whether a complete exercise movement has been performed.

Currently supported exercises:

* 💪 Biceps curls
* 🦵 Squats

The main processing pipeline is:

```text
Camera
   │
   ▼
Frontend
   │
   │ WebSocket / Socket.IO
   ▼
Flask Backend
   │
   ▼
OpenCV
   │
   ▼
MediaPipe Pose
   │
   ▼
Body Landmarks
   │
   ▼
Geometric Analysis
   │
   ├── Joint angles
   ├── Distances
   └── Body proportions
   │
   ▼
Exercise State Machine
   │
   ▼
Exercise detected
   │
   │ Socket.IO
   ▼
Frontend counter update
```

---

## Features

### Real-time pose estimation

The system uses **MediaPipe Pose** to detect body landmarks from camera frames.

Detected landmarks include:

* Nose
* Eyes
* Ears
* Shoulders
* Elbows
* Wrists
* Hips
* Knees
* Ankles
* Feet

The detected landmarks are converted into pixel coordinates and stored as a dictionary for subsequent analysis.

### Exercise recognition

Exercise detection is based on geometric relationships between body landmarks rather than a trained classification model.

For example, joint angles are calculated using three body points:

```text
        P1
       /
      /
     P2
      \
       \
        P3
```

The angle at `P2` is calculated from the vectors `P2 → P1` and `P2 → P3`.

### Real-time communication

The backend uses **Flask-SocketIO** to receive frames and send exercise updates to the frontend.

The following Socket.IO events are currently used:

| Event           | Direction          | Purpose                          |
| --------------- | ------------------ | -------------------------------- |
| `connect`       | Frontend → Backend | Establish connection             |
| `disconnect`    | Frontend → Backend | Close connection                 |
| `frame`         | Frontend → Backend | Send a frame for biceps analysis |
| `squat_frame`   | Frontend → Backend | Send a frame for squat analysis  |
| `biceps_update` | Backend → Frontend | Update biceps counter            |
| `squat_update`  | Backend → Frontend | Update squat counter             |

---

## Biceps Curl Detection

Biceps curls are detected using the angle formed by:

```text
Wrist → Elbow → Shoulder
```

The system analyzes both arms:

```python
angle_droit = calculate_angle(
    wrist_right,
    elbow_right,
    shoulder_right
)

angle_gauche = calculate_angle(
    wrist_left,
    elbow_left,
    shoulder_left
)
```

A state machine is used to identify a complete movement.

### Movement states

```text
        Arms extended
             │
             ▼
         State 0
             │
       angle < 30°
             │
             ▼
         State 1
             │
       angle > 150°
             │
             ▼
     Complete curl detected
```

The movement must also last longer than the configured time threshold before being counted.

## The current implementation uses an interval of approximately **200 ms between analyzed frames** and requires the movement to exceed **1.5 seconds** before validating the repetition.

## Squat Detection

Squat detection uses the right leg landmarks:

```text
Hip
 │
 ▼
Knee
 │
 ▼
Ankle
```

The system first initializes a reference body height when the user is standing upright.

It then compares the current hip-knee-ankle segment length against this initial reference.

### Movement states

```text
             Standing
                │
                ▼
          Reference height
                │
                ▼
            State: DOWN
                │
        height < 65%
                │
                ▼
            State: UP
                │
        height > 95%
                │
                ▼
         Complete squat
                │
                └──────────► DOWN
```

A squat is counted when the user returns to a position exceeding **95% of the initial reference height**, provided the movement has lasted longer than the configured threshold.

---

## Architecture

The project is divided into two main components.

### Backend

The Flask backend is responsible for:

1. Receiving camera frames.
2. Temporarily storing the images.
3. Running pose estimation.
4. Extracting body landmarks.
5. Analyzing exercise movements.
6. Maintaining exercise counters.
7. Sending updates to the frontend through Socket.IO.
8. Removing temporary image files.

### Computer Vision

The computer vision pipeline is implemented in `curl_analysis.py`.

Its main components are:

```text
load_image()
      │
      ▼
detect_pose()
      │
      ▼
extract_landmarks()
      │
      ▼
calculate_angle()
      │
      ├───────────────┐
      ▼               ▼
check_curl_biceps()  check_squat()
```

The pose processing functions can also annotate detected landmarks on images for visualization and debugging.

---

## Technologies

### Backend

* **Python**
* **Flask**
* **Flask-CORS**
* **Flask-SocketIO**

### Computer Vision

* **MediaPipe Pose**
* **OpenCV**
* **NumPy**

### Communication

* **WebSockets**
* **Socket.IO**

---

## Installation

### Requirements

Python 3.x is required.

Install the dependencies:

```bash
pip install -r requirements.txt
```

Depending on the frontend implementation, additional dependencies may be required.

---

## Project structure

A possible project structure is:

```text
.
├── app.py
├── curl_analysis.py
├── admin.json
├── received_frames/
└── README.md
```

Where:

* `app.py` — Flask API and Socket.IO server.
* `curl_analysis.py` — pose estimation and exercise detection.
* `admin.json` — local user credentials used by the login endpoint.
* `received_frames/` — temporary storage for received camera frames.

---

## Running the application

Start the Flask-SocketIO server with:

```bash
python app.py
```

The server runs on:

```text
http://localhost:5000
```

It is configured to listen on all network interfaces:

```python
socketio.run(
    app,
    debug=True,
    host='0.0.0.0',
    port=5000
)
```

The frontend can then establish a Socket.IO connection to the backend.

---

## Socket.IO API

### Send a biceps frame

The frontend emits:

```text
frame
```

with the binary image data.

The backend:

1. Saves the frame temporarily.
2. Runs `check_curl_biceps()`.
3. Updates the repetition counter if a curl is detected.
4. Emits a `biceps_update` event.
5. Deletes the temporary frame.

### Send a squat frame

The frontend emits:

```text
squat_frame
```

with the binary image data.

The backend follows the same process using `check_squat()`.

When a squat is detected, the backend emits:

```text
squat_update
```

with the current number of repetitions.

---

## Authentication

The backend exposes a simple login endpoint:

```http
POST /login
```

Expected JSON:

```json
{
  "email": "user@example.com",
  "password": "password"
}
```

A successful authentication returns:

```json
{
  "message": "Login successful"
}
```

Invalid credentials return HTTP `401`.

> **Security note:** the current implementation stores and compares passwords directly from `admin.json`. This approach is suitable for a prototype but should not be used for production authentication. Password hashing, secure sessions or token-based authentication should be implemented for a production application.

---

## Exercise detection approach

This project does not rely on a conventional supervised classification model for exercise recognition.

Instead, movements are identified through **pose estimation + geometric rules + state machines**.

This makes it possible to define an exercise using interpretable physical constraints.

For example:

```text
Pose landmarks
      ↓
Joint geometry
      ↓
Angle / distance
      ↓
Threshold
      ↓
Movement state
      ↓
Repetition
```

This approach can be extended by defining additional landmark relationships and movement states.

---

## Adding a new exercise

A new exercise can be implemented following the same general pattern:

### 1. Identify relevant landmarks

For example:

```python
[
    "Epaule droite",
    "Hanche droite",
    "Genou droit"
]
```

### 2. Define geometric features

Possible features include:

* Joint angles
* Distances between landmarks
* Relative segment lengths
* Movement speed
* Temporal duration

### 3. Define movement states

For example:

```text
REST → MOVEMENT → REST
```

### 4. Validate the movement

Use thresholds and temporal constraints to determine when a complete repetition has occurred.

### 5. Expose the exercise through Socket.IO

Add a new event for receiving frames and another event for sending repetition updates to the frontend.

---

## Limitations

The current prototype has several limitations:

* Exercise recognition relies on manually defined geometric thresholds.
* Detection accuracy may depend on camera angle and user positioning.
* The squat detector currently relies on the **right leg**.
* Missing pose landmarks can cause the analysis to fail.
* Frames are temporarily written to disk for processing.
* Exercise counters are stored in global variables and therefore are not designed for multiple independent users/sessions.
* The authentication mechanism is intended for a prototype rather than production use.
* No persistent database is currently used for exercise statistics.

---

## Future Improvements

Possible improvements include:

* [ ] Support additional exercises.
* [ ] Improve robustness to different camera angles.
* [ ] Use normalized landmark coordinates instead of image pixel coordinates.
* [ ] Add movement-quality analysis, not only repetition counting.
* [ ] Provide real-time feedback on exercise form.
* [ ] Replace hard-coded thresholds with configurable parameters.
* [ ] Add user/session-specific exercise counters.
* [ ] Avoid writing every frame to disk.
* [ ] Add persistent workout statistics.
* [ ] Improve authentication and session management.
* [ ] Investigate machine-learning-based exercise classification.
* [ ] Add a calibration phase for individual users.
* [ ] Add confidence thresholds for pose landmarks.

---

## Context

This project explores the use of **computer vision and pose estimation for interactive sports coaching**.

Rather than simply analyzing recorded videos, the architecture is designed around **real-time interaction between a camera-based frontend and a computer-vision backend**, with exercise detection results immediately transmitted back to the user interface.

**Python · Flask · Flask-SocketIO · MediaPipe Pose · OpenCV · NumPy · Computer Vision · Pose Estimation · Real-Time Processing**

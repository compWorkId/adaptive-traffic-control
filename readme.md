# Adaptive Traffic Signal Management System (ATMS)

An intelligent traffic simulation and control system using Python, Pygame, and YOLOv11 to optimize intersection flow and prioritize emergency vehicles.

##  Key Features
- **Density-Based Adaptive Selection**: Dynamically selects the next lane to turn green based on vehicle count (heavier queues get priority).
- **Emergency Priority Override**: Immediate signal preemption for ambulances with synchronized siren audio.
- **Gap-Out Detection**: Switches phases early if the current road is clear, minimizing wasted green time.
- **YOLOv11 Integration**: Ready for real-time vehicle counting via computer vision.
- **Smooth Scaling**: Automatic window scaling (default 1080p width) for full-view visibility on any screen.

---

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- `pip` (Python package manager)

### 1. Clone & Navigate
```bash
git clone repo_url
cd Adaptive-Traffic-Signal-Timer/Code/YOLO/darkflow
```

### 2. Prepare Environment

#### **macOS / Linux**
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required libraries
pip install -r requirements.txt
```

#### **Windows**
```bash
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install required libraries
pip install -r requirements.txt
```

---

## How to Run

Ensure your virtual environment is active (see above), then run:

```bash
python simulation.py
```

*Note: The simulation automatically resolves asset paths relative to the script location, so it can be executed from any directory as long as the relative internal structure is preserved.*

---

## System Logic

### 1. Adaptive Cycle Management
Replaces traditional fixed-time cycles with a **Weighted Priority Selector**. After every phase, the controller identifies the most congested lane and schedules it next.

### 2. Emergency Preemption
A real-time monitor scans for `ambulance` classes. If one enters the intersection's approach:
1. The current active green signal is immediately terminated.
2. A safety all-red buffer (0.5s) is applied.
3. The ambulance's lane turns green until it clears the intersection.

### 3. Actuated "Gap-Out" Logic
If a lane becomes empty before its green timer expires, the system detects the "gap" and terminates the phase early to serve waiting traffic in other directions.

---

## Project Structure
- `simulation.py`: Core engine (GUI, Physics, Adaptive Logic).
- `detector.py`: YOLOv11 integration module.
- `images/`: High-resolution sprites and background assets.
- `yolov8n.pt`: Pre-trained YOLO weights for vehicle detection.

---

## License
MIT License.

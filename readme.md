# Adaptive Traffic Signal Management System (ATMS)

An intelligent traffic simulation and control system using Python, Pygame, and YOLOv11 to optimize intersection flow, reduce congestion, and prioritize emergency vehicles.

##  Key Features
- **Density-Based Adaptive Selection**: Dynamically selects the next lane to turn green based on vehicle count (heaviest queue first).
- **Emergency Priority Override**: Immediate signal preemption for ambulances with synchronized siren audio.
- **Gap-Out Detection**: Switches phases early if the current road is clear, minimizing "wasted" green time.
- **YOLO Integration**: Real-time vehicle counting via YOLOv11 (Mode 1 in `detector.py`).
- **All-Red Safety Buffer**: Implements a safety interval between phase changes to prevent mid-intersection collisions.
- **Automatic Multi-Resolution Scaling**: Simulation runs at a virtual resolution of 1400x922 but scales smoothly to any window size (default: 1080px width).

---

## Installation & Setup

### Prerequisites
- Python 3.8+
- [Optional] CUDA-enabled GPU for faster YOLO inference.

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

Ensure your virtual environment is active, then execute:

```bash
python simulation.py
```

---

## System Logic

### 1. Cycle Management
The system replaces traditional "Fixed Round Robin" with a **Weighted Priority Selection**. After every green phase, the controller scans all waiting lanes and picks the one with the highest vehicle density.

### 2. Emergency Preemption
A background thread continuously scans for `ambulance` sprites. If detected within the intersection boundary:
1. The current green signal is immediately terminated.
2. A 0.5s all-red safety buffer is applied.
3. The ambulance's lane is switched to Green immediately.

### 3. Gap-Out Logic
To maximize efficiency, the system implements **Actuated Signal Logic**. If a lane becomes empty while the timer is still green (and a minimum green time has passed), the phase "gaps out" and switches to the next priority lane.

### 4. Vehicle Physics
- **Lane Disciplines**: Vehicles follow specific lanes (Slow/Main/Turning).
- **Collision Avoidance**: Physics-based queuing with dynamic gaps ensures vehicles don't overlap while waiting.
- **Rotation**: Smooth 90-degree turning transitions using Pygame surfaces.

---

## Project Structure
- `simulation.py`: The main engine containing the GUI, physics, and priority logic.
- `detector.py`: YOLOv11 wrapper for real-time traffic density analysis.
- `images/`: High-resolution assets for vehicles and intersection backgrounds.

---

## License
MIT License. Free to use for research and educational purposes.

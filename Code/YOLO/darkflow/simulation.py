import random
import math
import time
import threading
import pygame
import sys
import os
from detector import VehicleDetector

# Default values of signal times
defaultRed = 150
defaultYellow = 5
defaultGreen = 20
defaultMinimum = 10
defaultMaximum = 60

signals = []
noOfSignals = 4
simTime = 300       # change this to change time of simulation
timeElapsed = 0

currentGreen = 0   # Indicates which signal is green
nextGreen = (currentGreen+1)%noOfSignals
currentYellow = 0   # Indicates whether yellow signal is on or off 

carTime = 2
bikeTime = 1
busTime = 2.5
truckTime = 2.5

noOfCars = 0
noOfBikes = 0
noOfBuses =0
noOfTrucks = 0
noOfLanes = 2

detectionTime = 5
global_detector = None

speeds = {'car':2, 'bus':1.8, 'truck':1.8, 'bike':2, 'taxi':2, 'ambulance': 2.5}  # average speeds of vehicles

# Realistic sizes (Length, Width) for each class
vehicle_sizes = {
    'car': (54, 22),
    'taxi': (54, 22),
    'bike': (34, 18),
    'bus': (80, 26),
    'truck': (80, 26),
    'ambulance': (68, 24)
}

# --- COORDINATE SYSTEM (Reverted to Stable Initial Set) ---
x = {'right':[0,0,0],      'down':[755,727,697], 'left':[1400,1400,1400], 'up':[602,627,657]}
y = {'right':[348,370,398],'down':[0,0,0],       'left':[498,466,436],    'up':[800,800,800]}

vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'crossed':0}}
vehicleTypes = {0:'car', 1:'bus', 2:'truck', 3:'bike', 4:'taxi', 5:'ambulance'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

# Signal coords
signalCoods     = [(530,230),(810,230),(810,570),(530,570)]
signalTimerCoods= [(530,210),(810,210),(810,550),(530,550)]
vehicleCountCoods=[(480,210),(880,210),(880,550),(480,550)]
vehicleCountTexts = ["0", "0", "0", "0"]

# Stop lines
stopLines    = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop  = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
stops = {'right': [580,580,580], 'down': [320,320,320], 'left': [810,810,810], 'up': [545,545,545]}

mid = {'right': {'x':705, 'y':445}, 'down': {'x':695, 'y':450}, 'left': {'x':695, 'y':425}, 'up': {'x':695, 'y':400}}
rotationAngle = 3

# Gap between vehicles
gap  = 15   # stopping gap
gap2 = 15   # moving gap

pygame.init()
pygame.mixer.init()
simulation = pygame.sprite.Group()

class TrafficSignal:
    def __init__(self, red, yellow, green, minimum, maximum):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = "30"
        self.totalGreenTime = 0
        
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        # self.stop = stops[direction][lane]
        self.index = len(vehicles[direction][lane]) - 1
        # Robust relative pathing for cross-platform execution (any CWD)
        script_dir = os.path.dirname(__file__)
        path = os.path.join(script_dir, "images", direction, vehicleClass + ".png")
        if not os.path.exists(path):
            path = os.path.join(script_dir, "images", direction, "car.png")
        
        # Standardize size with class-based dimensions and auto-cropping
        base_size = vehicle_sizes.get(vehicleClass, (54, 22))
        if direction in ['right', 'left']:
            target_size = (base_size[0], base_size[1])
        else:
            target_size = (base_size[1], base_size[0]) # Rotate for vertical lanes
            
        img = pygame.image.load(path)
        # Auto-crop transparent margins
        mask_rect = img.get_bounding_rect()
        if mask_rect.width > 0 and mask_rect.height > 0:
            img = img.subsurface(mask_rect)
            
        self.originalImage = pygame.transform.smoothscale(img, target_size)
        self.currentImage = self.originalImage

    
        if(direction=='right'):
            if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().width - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap    
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif(direction=='left'):
            if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().width + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] += temp
            stops[direction][lane] += temp
        elif(direction=='down'):
            if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().height - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif(direction=='up'):
            if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().height + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] += temp
            stops[direction][lane] += temp
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.currentImage, (self.x, self.y))

    def move(self):
        tspeed = self.speed
        speed_factor = 1.0
        if(self.vehicleClass == 'ambulance'):
            speed_factor = 1.25 # Ambulances up to 1.25x faster
        elif(self.crossed == 1):
            speed_factor = 1.25 # Clear intersection slightly faster
        elif(currentGreen == self.direction_number):
            if(currentYellow == 0):
                speed_factor = 1.75
            else:
                speed_factor = 0.75
        tspeed *= speed_factor

        if(self.direction=='right'):
            if(self.crossed==0 and self.x+self.currentImage.get_rect().width>stopLines[self.direction]):   # if the image has crossed stop line now
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.x+self.currentImage.get_rect().width<mid[self.direction]['x']):
                    if((self.x+self.currentImage.get_rect().width<=self.stop or (currentGreen==0) or self.crossed==1) and (self.index==0 or self.x+self.currentImage.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - gap2) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                        self.x += tspeed
                else:   
                    if(self.turned==0):
                        self.rotateAngle += rotationAngle * speed_factor
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 2 * speed_factor
                        self.y += 1.8 * speed_factor
                        if(self.rotateAngle>=90):
                            self.rotateAngle = 90
                            self.turned = 1
                            # path = "images/" + directionNumbers[((self.direction_number+1)%noOfSignals)] + "/" + self.vehicleClass + ".png"
                            # self.x = mid[self.direction]['x']
                            # self.y = mid[self.direction]['y']
                            # self.image = pygame.image.load(path)
                    else:
                        if(self.index==0 or self.y+self.currentImage.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - gap2) or self.x+self.currentImage.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - gap2)):
                            self.y += tspeed
            else: 
                if((self.x+self.currentImage.get_rect().width<=self.stop or self.crossed == 1 or (currentGreen==0)) and (self.index==0 or self.x+self.currentImage.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - gap2) or (vehicles[self.direction][self.lane][self.index-1].turned==1))):                
                    self.x += tspeed



        elif(self.direction=='down'):
            if(self.crossed==0 and self.y+self.currentImage.get_rect().height>stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.y+self.currentImage.get_rect().height<mid[self.direction]['y']):
                    if((self.y+self.currentImage.get_rect().height<=self.stop or (currentGreen==1) or self.crossed==1) and (self.index==0 or self.y+self.currentImage.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - gap2) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                        self.y += tspeed
                else:   
                    if(self.turned==0):
                        self.rotateAngle += rotationAngle * speed_factor
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 2.5 * speed_factor
                        self.y += 2 * speed_factor
                        if(self.rotateAngle>=90):
                            self.rotateAngle = 90
                            self.turned = 1
                    else:
                        if(self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or self.y<(vehicles[self.direction][self.lane][self.index-1].y - gap2)):
                            self.x -= tspeed
            else: 
                if((self.y+self.currentImage.get_rect().height<=self.stop or self.crossed == 1 or (currentGreen==1)) and (self.index==0 or self.y+self.currentImage.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - gap2) or (vehicles[self.direction][self.lane][self.index-1].turned==1))):                
                    self.y += tspeed
            
        elif(self.direction=='left'):
            if(self.crossed==0 and self.x<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.x>mid[self.direction]['x']):
                    if((self.x>=self.stop or (currentGreen==2) or self.crossed==1) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                        self.x -= tspeed
                else: 
                    if(self.turned==0):
                        self.rotateAngle += rotationAngle * speed_factor
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 1.8 * speed_factor
                        self.y -= 2.5 * speed_factor
                        if(self.rotateAngle>=90):
                            self.rotateAngle = 90
                            self.turned = 1
                            # path = "images/" + directionNumbers[((self.direction_number+1)%noOfSignals)] + "/" + self.vehicleClass + ".png"
                            # self.x = mid[self.direction]['x']
                            # self.y = mid[self.direction]['y']
                            # self.currentImage = pygame.image.load(path)
                    else:
                        if(self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height +  gap2) or self.x>(vehicles[self.direction][self.lane][self.index-1].x + gap2)):
                            self.y -= tspeed
            else: 
                if((self.x>=self.stop or self.crossed == 1 or (currentGreen==2)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or (vehicles[self.direction][self.lane][self.index-1].turned==1))):                
                    self.x -= tspeed
            # if((self.x>=self.stop or self.crossed == 1 or (currentGreen==2 and currentYellow==0)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2))):                
            #     self.x -= self.speed
        elif(self.direction=='up'):
            if(self.crossed==0 and self.y<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.y>mid[self.direction]['y']):
                    if((self.y>=self.stop or (currentGreen==3) or self.crossed == 1) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height +  gap2) or vehicles[self.direction][self.lane][self.index-1].turned==1)):
                        self.y -= tspeed
                else:   
                    if(self.turned==0):
                        self.rotateAngle += rotationAngle * speed_factor
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 1 * speed_factor
                        self.y -= 1 * speed_factor
                        if(self.rotateAngle>=90):
                            self.rotateAngle = 90
                            self.turned = 1
                    else:
                        if(self.index==0 or self.x<(vehicles[self.direction][self.lane][self.index-1].x - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width - gap2) or self.y>(vehicles[self.direction][self.lane][self.index-1].y + gap2)):
                            self.x += tspeed
            else: 
                if((self.y>=self.stop or self.crossed == 1 or (currentGreen==3)) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height + gap2) or (vehicles[self.direction][self.lane][self.index-1].turned==1))):                
                    self.y -= tspeed

# Initialization of signals with default values
def initialize():
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red+ts1.yellow+ts1.green, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts4)
    repeat()

# Set time according to formula
def setTime():
    global noOfCars, noOfBikes, noOfBuses, noOfTrucks, noOfLanes
    global carTime, busTime, truckTime, bikeTime, global_detector
    
    if sys.platform == 'darwin':
        os.system("say 'detecting vehicles, " + directionNumbers[(currentGreen+1)%noOfSignals] + "' &")
    
    # Mode 1: AI/YOLO Detection (Uncomment for folder-based testing)
    # counts = global_detector.detect_and_count("images/detection_input.jpg")
    # noOfCars = counts['car']
    # noOfBuses = counts['bus']
    # noOfTrucks = counts['truck']
    # noOfBikes = counts['bike']

    # Mode 2: Simulator State Counting (Internal Ground Truth)
    noOfCars, noOfBuses, noOfTrucks, noOfBikes = 0,0,0,0
    for j in range(len(vehicles[directionNumbers[nextGreen]][0])):
        vehicle = vehicles[directionNumbers[nextGreen]][0][j]
        if(vehicle.crossed==0):
            vclass = vehicle.vehicleClass
            # print(vclass)
            noOfBikes += 1
    for i in range(1,3):
        for j in range(len(vehicles[directionNumbers[nextGreen]][i])):
            vehicle = vehicles[directionNumbers[nextGreen]][i][j]
            if(vehicle.crossed==0):
                vclass = vehicle.vehicleClass
                # print(vclass)
                if(vclass=='car'):
                    noOfCars += 1
                elif(vclass=='bus'):
                    noOfBuses += 1
                elif(vclass=='truck'):
                    noOfTrucks += 1
    # print(noOfCars)
    greenTime = math.ceil(((noOfCars*carTime) + (noOfBuses*busTime) + (noOfTrucks*truckTime)+ (noOfBikes*bikeTime))/(noOfLanes+1))
    # greenTime = math.ceil((noOfVehicles)/noOfLanes) 
    print('Green Time: ',greenTime)
    if(greenTime<defaultMinimum):
        greenTime = defaultMinimum
    elif(greenTime>defaultMaximum):
        greenTime = defaultMaximum
    # greenTime = random.randint(15,50)
    signals[(currentGreen+1)%(noOfSignals)].green = greenTime
   
# Returns the index of signal with an ambulance, or -1
def checkAmbulance():
    for i in range(noOfSignals):
        direction = directionNumbers[i]
        for lane in range(3):
            for vehicle in vehicles[direction][lane]:
                # Only trigger priority and siren if the ambulance is on camera (e.g., x > -200 and < 1600)
                if vehicle.vehicleClass == 'ambulance' and vehicle.crossed == 0:
                    if -100 < vehicle.x < 1500 and -100 < vehicle.y < 900:
                        return i
    return -1

def repeat():
    global currentGreen, currentYellow, nextGreen
    
    # Actuated Phase: Monitor flow and ambulances
    is_emergency = False
    while(signals[currentGreen].green > 0):
        printStatus()
        updateValues()
        
        # 1. Ambulance Priority Monitoring
        p_lane = checkAmbulance()
        if p_lane != -1:
            if p_lane == currentGreen:
                # Extension: keep light green if ambulance is still in this lane
                pass 
            else:
                # Override: Turn current light red ASAP if ambulance is elsewhere
                signals[currentGreen].green = 0
                is_emergency = True
                break
        
        # 2. Gap-Out Logic (Smart Switching)
        # Check if current direction is clear. If so, switch early after a minimum green time.
        if signals[currentGreen].totalGreenTime >= defaultMinimum:
            pending_vehicles = 0
            for i in range(3):
                # Count vehicles that have not yet crossed mid-point or stop line in current green direction
                for v in vehicles[directionNumbers[currentGreen]][i]:
                    if v.crossed == 0:
                        pending_vehicles += 1
            if pending_vehicles == 0:
                print(f"Gap-Out detected for Lane {currentGreen+1}. Switching early.")
                signals[currentGreen].green = 0
                break

        # detection check
        if signals[(currentGreen+1)%noOfSignals].red == detectionTime:
            thread = threading.Thread(name="detection", target=setTime, args=())
            thread.daemon = True
            thread.start()
            
        time.sleep(1)

    # --- Transition to Yellow ---
    currentYellow = 1
    vehicleCountTexts[currentGreen] = "0"
    
    for i in range(0,3):
        stops[directionNumbers[currentGreen]][i] = defaultStop[directionNumbers[currentGreen]]
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]

    # Emergency Speed-up: Use 3s for yellow during an ambulance override
    if is_emergency:
        signals[currentGreen].yellow = 3
            
    while(signals[currentGreen].yellow > 0):
        printStatus()
        updateValues()
        time.sleep(1)
        
    currentYellow = 0
    
    # Reset signal timers to default
    signals[currentGreen].green = defaultGreen
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed

    # --- All-Red Interval / Buffer ---
    currentGreen = -1
    if is_emergency:
        # 0.5s buffer even during ambulance - enough to prevent mid-intersection collisions
        printStatus()
        updateValues()
        time.sleep(0.5)
    else:
        # 1.5s buffer for normal transitions
        printStatus()
        updateValues()
        time.sleep(1.5)
       
    # --- Select Next Lane (Density-Based Adaptive) ---
    p_lane = checkAmbulance()
    if p_lane != -1:
        currentGreen = p_lane
        print(f"[AMBULANCE OVERRIDE] → Lane {p_lane + 1}")
    else:
        # Count uncrossed vehicles in each waiting lane (exclude the lane that just ran)
        prev_green = nextGreen  # was set before the green phase
        densities = []
        for i in range(noOfSignals):
            if i == prev_green:
                # The lane that just ran gets lowest priority
                count = -1
            else:
                count = 0
                dir_name = directionNumbers[i]
                for lane_idx in range(3):
                    for v in vehicles[dir_name][lane_idx]:
                        if v.crossed == 0:
                            count += 1
            densities.append(count)
        
        best_lane = densities.index(max(densities))
        # If all non-served lanes are empty, fall back to round-robin
        if max(densities) <= 0:
            best_lane = (prev_green + 1) % noOfSignals
        
        currentGreen = best_lane
        print(f"[DENSITY SELECT] Lane densities: {densities} → Lane {currentGreen + 1} selected")
    
    nextGreen = currentGreen  # track which lane just ran
    signals[currentGreen].green = defaultGreen  # will be updated by setTime thread
    repeat()

# Print the signal timers on cmd
def printStatus():                                                                                           
    for i in range(0, noOfSignals):
        # Display --- in logs if timer is in the all-red clearance interval
        r_val = signals[i].red if signals[i].red >= 0 else "---"
        if(i==currentGreen):
            if(currentYellow==0):
                print(" GREEN TS",i+1,"-> r:",r_val," y:",signals[i].yellow," g:",signals[i].green)
            else:
                print("YELLOW TS",i+1,"-> r:",r_val," y:",signals[i].yellow," g:",signals[i].green)
        else:
            print("   RED TS",i+1,"-> r:",r_val," y:",signals[i].yellow," g:",signals[i].green)
    print()

# Update values of the signal timers after every second
def updateValues():
    for i in range(0, noOfSignals):
        if(i==currentGreen):
            if(currentYellow==0):
                signals[i].green-=1
                signals[i].totalGreenTime+=1
            else:
                signals[i].yellow-=1
        else:
            signals[i].red-=1

# Generating vehicles in the simulation
def generateVehicles():
    import time
    last_ambulance_time = time.time()
    while(True):
        current_time = time.time()
        if (current_time - last_ambulance_time) > 30: # 30s interval for ambulance
            vehicle_type = 5
            last_ambulance_time = current_time
        else:
            vehicle_type = random.randint(0,4)
        
        if(vehicle_type==3): # Bike stays in lane 0 typically
            lane_number = 0
        else:
            lane_number = random.randint(0,1) + 1
        will_turn = 0
        if(lane_number==2):
            temp = random.randint(0,4)
            if(temp<=2):
                will_turn = 1
            elif(temp>2):
                will_turn = 0
        temp = random.randint(0,999)
        direction_number = 0
        a = [250,500,750,1000]
        if(temp<a[0]):
            direction_number = 0
        elif(temp<a[1]):
            direction_number = 1
        elif(temp<a[2]):
            direction_number = 2
        elif(temp<a[3]):
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
        time.sleep(0.75)

def simulationTime():
    global timeElapsed, simTime
    while(True):
        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed==simTime):
            totalVehicles = 0
            print('Lane-wise Vehicle Counts')
            for i in range(noOfSignals):
                print('Lane',i+1,':',vehicles[directionNumbers[i]]['crossed'])
                totalVehicles += vehicles[directionNumbers[i]]['crossed']
            print('Total vehicles passed: ',totalVehicles)
            print('Total time passed: ',timeElapsed)
            print('No. of vehicles passed per unit time: ',(float(totalVehicles)/float(timeElapsed)))
            os._exit(1)
    

class Main:
    thread4 = threading.Thread(name="simulationTime",target=simulationTime, args=()) 
    thread4.daemon = True
    thread4.start()

    thread2 = threading.Thread(name="initialization",target=initialize, args=())
    thread2.daemon = True
    thread2.start()

    # Colours 
    black = (0, 0, 0)
    white = (255, 255, 255)

    script_dir = os.path.dirname(__file__)
    
    # Setting background image
    background_path = os.path.join(script_dir, 'images', 'mod_int.png')
    background = pygame.image.load(background_path)

    # Resolve screen size
    screenWidth, screenHeight = background.get_size()
    
    # Target window dimensions (1080px width)
    targetWidth = 1080
    targetHeight = int(screenHeight * (targetWidth / screenWidth))
    
    # Surfaces
    virtual_screen = pygame.Surface((screenWidth, screenHeight))
    screen = pygame.display.set_mode((targetWidth, targetHeight))
    pygame.display.set_caption("SMART TRAFFIC SIMULATION")

    # Image Assets
    redSignal = pygame.image.load(os.path.join(script_dir, 'images', 'signals', 'red.png'))
    yellowSignal = pygame.image.load(os.path.join(script_dir, 'images', 'signals', 'yellow.png'))
    greenSignal = pygame.image.load(os.path.join(script_dir, 'images', 'signals', 'green.png'))
    font = pygame.font.Font(None, 30)

    # YOLO Model Path
    model_path = os.path.join(script_dir, 'yolov8n.pt')
    
    # YOLO Detector Setup
    global global_detector
    try:
        global_detector = VehicleDetector(model_name=model_path)
    except:
        global_detector = None

    # Siren Sound Setup
    siren_sound = None
    try:
        siren_mp3 = os.path.join(script_dir, 'images', 'siren.mp3')
        siren_wav = os.path.join(script_dir, 'images', 'siren.wav')
        if os.path.exists(siren_mp3):
            siren_sound = pygame.mixer.Sound(siren_mp3)
        elif os.path.exists(siren_wav):
            siren_sound = pygame.mixer.Sound(siren_wav)
    except:
        pass
    siren_playing = False

    thread3 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())    # Generating vehicles
    thread3.daemon = True
    thread3.start()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        virtual_screen.blit(background,(0,0))
        for i in range(0,noOfSignals):
            if(i==currentGreen):
                if(currentYellow==1):
                    if(signals[i].yellow==0):
                        signals[i].signalText = "STOP"
                    else:
                        signals[i].signalText = signals[i].yellow
                    virtual_screen.blit(yellowSignal, signalCoods[i])
                else:
                    if(signals[i].green==0):
                        signals[i].signalText = "SLOW"
                    else:
                        signals[i].signalText = signals[i].green
                    virtual_screen.blit(greenSignal, signalCoods[i])
            else:
                if(signals[i].red<=10 and signals[i].red>=0):
                    if(signals[i].red==0):
                        signals[i].signalText = "GO"
                    else:
                        signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                virtual_screen.blit(redSignal, signalCoods[i])
        signalTexts = ["","","",""]

        # display signal timer only (vehicle count hidden for cleaner UI)
        for i in range(0,noOfSignals):  
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            virtual_screen.blit(signalTexts[i],signalTimerCoods[i]) 
            # vehicleCountTexts[i] hidden intentionally

        if checkAmbulance() != -1:
            if not siren_playing:
                if siren_sound:
                    siren_sound.play(-1)
                if sys.platform == 'darwin':
                    os.system("say 'Ambulance Priority' &") # Vocal hooter (Mac only)
                siren_playing = True
        else:
            if siren_playing:
                if siren_sound:
                    siren_sound.stop()
                siren_playing = False

        for vehicle in simulation:  
            virtual_screen.blit(vehicle.currentImage, [vehicle.x, vehicle.y])
            vehicle.move()
            
        # Scale the virtual surface down to the window size for a crisp, full view
        screen.blit(pygame.transform.smoothscale(virtual_screen, (targetWidth, targetHeight)), (0, 0))
        pygame.display.update()

Main()

  

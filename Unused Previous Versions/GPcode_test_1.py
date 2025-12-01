from machine import Pin, PWM, ADC
from time import sleep
from math import acos, asin, atan2, sqrt, degrees, sin

#----------------DEFINE ALL GLOBAL VARS---------------
x_potentiometer = None
y_potentiometer = None

shoulder_servo = None
elbow_servo = None
pen_servo = None

pen_button = None
pen_state = None
previous_button = None
#----------------------------------------------------

#----------------DEFINE POTENTIOMETERS---------------
def setup_potentiometers():
    global x_potentiometer, y_potentiometer
    x_potentiometer = ADC(26)
    y_potentiometer = ADC(27)
#----------------------------------------------------

def read_x_pot():
    return x_potentiometer.read_u16()

def read_y_pot():
    return y_potentiometer.read_u16()

#----------------CONVERT ANGLE TO SERVO DUTY---------
def angle_to_duty(angle: float) -> int:
	"""
	Converts an angle in degrees to the corresponding input
	for the duty_u16 method of the servo class
	"""

	MIN = 1638 # 0 degrees
	MAX = 8192 # 180 degrees
	DEG = (MAX - MIN) / 180 # value per degree

	# clamp angle to be between 0 and 180
	angle = max(0, min(180, angle))

	return int(angle * DEG + MIN)
#----------------------------------------------------

#----------------SETUP SERVOS-------------------------
def setup_servos():
    global shoulder_servo, elbow_servo, pen_servo
    shoulder_servo = PWM(Pin(0))
    elbow_servo = PWM(Pin(1))
    pen_servo = PWM(Pin(2))

    shoulder_servo.freq(50)
    elbow_servo.freq(50)
    pen_servo.freq(50)
#----------------------------------------------------

#----------------SETUP BUTTON-------------------------
def setup_button():
    global pen_button, pen_state, previous_button
    pen_button = Pin(10, Pin.IN, Pin.PULL_DOWN)
    pen_state = 0
    previous_button = 1
#----------------------------------------------------

#----------------ARM LENGTH SETTINGS-----------------
#Component lengths in cm
L_a = 15.5   # upper arm (A->B)
L_b = 15.5   # forearm (B->C)
#----------------------------------------------------

#----------------BASE OFFSET--------------------------
A_base_x = 0
A_base_y = 1
#----------------------------------------------------

#----------------PRE-MAIN LOOP SETUP-----------------------
setup_servos()
setup_button()
setup_potentiometers()
#----------------MAIN LOOP----------------------------
while True:
    #TODO: Break up main loop into some smaller functions
    raw_x = read_x_pot()
    raw_y = read_y_pot()
    
    shoulder_servo.duty_u16(raw_x//2)
    elbow_servo.duty_u16(raw_y//2)

    

    # Pen button toggle
    current_button = pen_button.value()
    if previous_button == 1 and current_button == 0:
        if pen_state == 0:
            pen_servo.duty_u16(angle_to_duty(35))
            pen_state = 1
        else:
            pen_servo.duty_u16(angle_to_duty(20))
            pen_state = 0
        sleep(0.2)
    previous_button = current_button

    sleep(0.05)

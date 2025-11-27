from machine import Pin, PWM, ADC
from time import sleep
from math import acos, asin, sqrt, degrees, sin, atan

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

def x_pot_to_angle():
    return duty_to_angle(read_x_pot())

def read_y_pot():
    return y_potentiometer.read_u16()

def y_pot_to_angle():
    return duty_to_angle(read_y_pot())

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

#----------------CONVERT DUTY TO ANGLE---------
def duty_to_angle(raw_value: int) -> float:
    """
    Converts a 0–65535 potentiometer reading into the corresponding
    servo angle in degrees, using dynamic scaling to the servo’s
    duty range (MIN–MAX).
    """

    MIN = 1638      # 0 Degrees
    MAX = 8192      # 180 Degrees
    DEG = (MAX - MIN) / 180  # Duty per degree

    # Clamp raw potentiometer reading
    raw_value = max(0, min(65535, raw_value))

    duty = MIN + (raw_value / 65535.0) * (MAX - MIN) # Map from 0-65535 -> 1638-8192

    angle = (duty - MIN) / DEG
    return angle
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
    #Get raw duty values from potentiometers
    raw_x = read_x_pot()
    raw_y = read_y_pot()

    '''
    Include toggle to use potentiometers for angles directly.

    If we set direct_angle_input to False, potentiometers give endpoint coordinate on page
    
    If we set direct_angle input to True, potentiometers directly give shoulder and elbow angles
    '''
    direct_angle_input = False
    shoulder_angle = 0
    elbow_angle = 0

    if not direct_angle_input:
        # Convert pots to 8.5x11 inch paper workspace
        #Paper paramaters:
        PAPER_WIDTH_CM  = 27.94
        PAPER_HEIGHT_CM = 21.59
        EDGE = 1.0

        DRAW_MIN_X = EDGE
        DRAW_MAX_Y = PAPER_WIDTH_CM  - EDGE
        DRAW_MIN_Y = EDGE
        DRAW_MAX_X = PAPER_HEIGHT_CM - EDGE

        # duty 0 corresponds to X coordinate 1
        # duty 65535 (MAX) corresponds to X coordinate 20.59 (1 cm from the top)
        c_x = DRAW_MIN_X + (raw_x / 65535) * (DRAW_MAX_X - DRAW_MIN_X)
        c_y = DRAW_MIN_Y + (raw_y / 65535) * (DRAW_MAX_Y - DRAW_MIN_Y)

        length_AB=15.5
        length_BC=15.5
        s_offset = #TODO: measure shoulder offset
        e_offset = #TODO: measure elbow offset


        # Step 1 (Equation 1)
        angle_AC = atan(c_y/c_x)

        length_AC = sqrt(c_y**2+c_x**2)

        angle_BAC = acos((length_AB**2+length_AC**2-length_BC**2)/(2*length_AB*length_BC))

        angle_ABC = acos((length_AB**2+length_BC**2-length_AC**2)/(2*length_AB*length_BC))

        theta_AB = angle_AC-angle_BAC

        #Finally, calculate angles for arms from given params
        shoulder_angle = s_offset + theta_AB
        elbow_angle = angle_ABC - e_offset
        print(f"Target=({Cx:.2f},{Cy:.2f}), Using Angles({shoulder_angle:.2f},{elbow_angle:.2f})")
    else:
        shoulder_angle = x_pot_to_angle()
        elbow_angle = y_pot_to_angle()
        print(f"Using Direct Potentiometer Input with Angles({shoulder_angle:.2f},{elbow_angle:.2f})")
    
    # Send to servos
    shoulder_servo.duty_u16(angle_to_duty(shoulder_angle))
    elbow_servo.duty_u16(angle_to_duty(elbow_angle))

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

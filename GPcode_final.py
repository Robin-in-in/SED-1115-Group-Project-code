from machine import Pin, PWM, ADC
from time import sleep
from math import acos, asin, sqrt, degrees, sin, atan


#----------------READ POTENTIOMETERS-----------------
#Defined by Rafael Robin
#Small helper functions for interacting with potentiometers.
def read_x_pot():
    return x_potentiometer.read_u16()

def x_pot_to_angle():
    return duty_to_angle(read_x_pot())

def read_y_pot():
    return y_potentiometer.read_u16()

def y_pot_to_angle():
    return duty_to_angle(read_y_pot())
#----------------------------------------------------

#----------------CONVERT ANGLE TO SERVO DUTY---------
# Defined by Mohammed Urbani
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
# Defined by Rafael Robin
def duty_to_angle(raw_value: int) -> float:
    """
    Serves to convert potentiometer reading to angle for direct potentiometer input mode. Instead of calculating angles from coordinates, using
    trigonometric functions, we can directly read the angles from the potentiometers, before passing them to the servos.

    Converts a 0–65535 potentiometer reading into the corresponding
    servo angle in degrees.
    """

    MIN = 0
    MAX = 65535
    deg = (MAX - MIN) / 180  # Duty per degree
    # Clamp raw potentiometer reading
    raw_value = max(0, min(65535, raw_value))

    angle = raw_value / deg

    # One last clamp for safety
    angle = max(0,min(180,angle))
    return angle
#----------------------------------------------------

#----------------SETUP SERVOS-------------------------
# Defined by Mohammed Urbani.
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
# Defined by Owen Barnacle. 
def setup_button():
    global pen_button, pen_state, previous_button
    pen_button = Pin(10, Pin.IN, Pin.PULL_DOWN)
    pen_state = 0
    previous_button = 1
#----------------------------------------------------

#----------------SETUP POTENTIOMETERS---------------
#Defined by Mohammed Urbani
def setup_potentiometers():
    global x_potentiometer, y_potentiometer
    x_potentiometer = ADC(26)
    y_potentiometer = ADC(27)
#----------------------------------------------------

#----------------DEFINE ARM PARAMATERS-------------------
# Defined and measured by Mohammed Urbani and Rafael Robin
def setup_arm_paramaters():
    global length_AB, length_BC, s_offset, e_offset
    length_AB = 15.5 # upper arm (A->B)
    length_BC = 15.5 # forearm (B->C)

    #Our group did not manage to find time to measure offsets properly
    s_offset = 0 #TODO: measure shoulder offset
    e_offset = 0 #TODO: measure elbow offset
#----------------------------------------------------

#----------------INVERSE KINEMATICS EQUATIONS--------------
#Originally transcribed by Mohammed Urbani- equations updated by Rafael Robin
def calculate_angles_from_paramaters(c_x, c_y, length_AB, length_BC, s_offset, e_offset):

    angle_AC = atan(c_y/c_x)

    length_AC = sqrt(c_y**2+c_x**2)

    angle_BAC = acos((length_AB**2+length_AC**2-length_BC**2)/(2*length_AB*length_BC))

    angle_ABC = acos((length_AB**2+length_BC**2-length_AC**2)/(2*length_AB*length_BC))

    theta_AB = angle_AC-angle_BAC

    shoulder_angle = s_offset + theta_AB
    elbow_angle = angle_ABC - e_offset

    return shoulder_angle, elbow_angle
#----------------------------------------------------------

#-------------------WRIST TOGGLE---------------------------
#Defined by Owen Barnacle.
def wrist_toggle():
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
#----------------------------------------------------------


#----------------PRE-MAIN LOOP SETUP------------------
setup_servos()
setup_button()
setup_potentiometers()
setup_arm_paramaters()
#-----------------------------------------------------

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

    # GET ANGLES TO SEND TO SERVO, DEPENDING ON INPUT MODE
    if not direct_angle_input:
        # Define paramaters for coordinate space- done by Mohammed Urbani
        PAPER_WIDTH_CM  = 27.94
        PAPER_HEIGHT_CM = 21.59
        EDGE = 1.0

        draw_min_y = EDGE
        draw_max_y = PAPER_WIDTH_CM  - EDGE
        draw_min_x = EDGE
        draw_max_x = PAPER_HEIGHT_CM - EDGE

        # duty 0 corresponds to X coordinate 1
        # duty 65535 (MAX) corresponds to X coordinate 20.59 (1 cm from the top)
        c_x = draw_min_x + (raw_x / 65535) * (draw_max_x - draw_min_x)
        c_y = draw_min_y + (raw_y / 65535) * (draw_max_y - draw_min_y)

        #Finally, calculate angles for arms from given params
        shoulder_angle, elbow_angle = calculate_angles_from_paramaters(c_x, c_y, length_AB, length_BC)
        print(f"Using Cooridnate Potentiometer Input with Angles({shoulder_angle:.2f},{elbow_angle:.2f}), with coordinates({c_x:.2f},{c_y:.2f})")
    else:
        # Get angles from pots directly- done by Rafael Robin
        shoulder_angle, elbow_angle = x_pot_to_angle(), y_pot_to_angle()
        print(f"Using Direct Potentiometer Input with Angles({shoulder_angle:.2f},{elbow_angle:.2f})")
    
    # Send to servos
    shoulder_servo.duty_u16(angle_to_duty(shoulder_angle))
    elbow_servo.duty_u16(angle_to_duty(elbow_angle))
    print(f"Succesfully moved servos.")

    # Pen button toggle. Checks on button edge on every iteration to determine whether or not the wrist should toggle. 
    wrist_toggle()

    # Include a sleep to ensure enough physical time for the servo to execute.
    sleep(0.05)

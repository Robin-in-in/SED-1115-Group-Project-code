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
    x_potentiometer = ADC(26)
    y_potentiometer = ADC(27)
#----------------------------------------------------

def read_x_pot():
    return x_potentiometer.read_u16()

def read_y_pot():
    return y_potentiometer.read_u16()

#----------------CONVERT ANGLE TO SERVO DUTY---------
def angle_to_duty(angle_deg):
    if angle_deg < 0:
        angle_deg = 0
    elif angle_deg > 180:
        angle_deg = 180
    pulse_width = 500 + (2000 * angle_deg / 180)
    return int((pulse_width / 20000) * 65535)
#----------------------------------------------------

#----------------SETUP SERVOS-------------------------
def setup_servos():
    shoulder_servo = PWM(Pin(0))
    elbow_servo = PWM(Pin(1))
    pen_servo = PWM(Pin(2))

    shoulder_servo.freq(50)
    elbow_servo.freq(50)
    pen_servo.freq(50)
#----------------------------------------------------

#----------------SETUP BUTTON-------------------------
def setup_button():
    pen_button = Pin(10, Pin.IN, Pin.PULL_UP)
    pen_state = 0
    previous_button = 1
#----------------------------------------------------

#----------------ARM LENGTH SETTINGS-----------------
#TODO: Specify cm or inches in a comment
L_a = 14.0   # upper arm (A->B)
L_b = 14.0   # forearm (B->C)
#----------------------------------------------------

#----------------BASE OFFSET--------------------------
A_base_x = 0
A_base_y = 0
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

    # Convert pots to 8.5x11 inch paper workspace
    PAPER_WIDTH_CM  = 21.59
    PAPER_HEIGHT_CM = 27.94
    EDGE = 1.0

    DRAW_MIN_X = EDGE
    DRAW_MAX_X = PAPER_WIDTH_CM  - EDGE
    DRAW_MIN_Y = EDGE
    DRAW_MAX_Y = PAPER_HEIGHT_CM - EDGE

    Cx = DRAW_MIN_X + (raw_x / 65535) * (DRAW_MAX_X - DRAW_MIN_X)
    Cy = DRAW_MIN_Y + (raw_y / 65535) * (DRAW_MAX_Y - DRAW_MIN_Y)

    # Step 1 (Equation 1)
    AC = sqrt((A_base_x - Cx)**2 + (A_base_y - Cy)**2)

    # Step 2 (Equation 2) – base-to-target vertical distance
    A_baseC = sqrt((A_base_x - Cx)**2 + (A_base_y - Cy)**2)

    # Step 3 (Equation 3) – ∠BAC
    angle_BAC = acos((L_a**2 + AC**2 - L_b**2) / (2 * L_a * AC))

    # Step 4 (Equation 4) – ∠ACB
    angle_ACB = asin((L_a * sin(angle_BAC)) / L_b)

    # Step 5 (Equation 5) – ∠YAC
    angle_YAC = acos((Cy**2 + AC**2 - A_baseC**2) / (2 * Cy * AC))

    # Step 6 (Equation 6) – α = ∠BAC + ∠YAC
    alpha = angle_BAC + angle_YAC

    # Step 7 (Equation 7) – β = ∠BAC + ∠ACB
    beta = angle_BAC + angle_ACB

    # Convert radians → degrees
    alpha_deg = degrees(alpha)
    beta_deg  = degrees(beta)

    # Apply professor's servo offset equations:
    # (Equation 8) servoA = α - 75°
    # (Equation 9) servoB = 150° - β
    shoulder_angle = alpha_deg - 75
    elbow_angle    = 150 - beta_deg

    # Send to servos
    shoulder_servo.duty_u16(angle_to_duty(shoulder_angle))
    elbow_servo.duty_u16(angle_to_duty(elbow_angle))

    print(f"Target=({Cx:.2f},{Cy:.2f}) AC={AC:.2f} α={alpha_deg:.1f} β={beta_deg:.1f}")

    # Pen button toggle
    current_button = pen_button.value()
    if previous_button == 1 and current_button == 0:
        if pen_state == 0:
            pen_servo.duty_u16(angle_to_duty(45))
            pen_state = 1
        else:
            pen_servo.duty_u16(angle_to_duty(0))
            pen_state = 0
        sleep(0.2)
    previous_button = current_button

    sleep(0.05)

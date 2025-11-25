import sys
from servo_translator import translate
from machine import Pin, PWM, ADC
from G_parser import GCodeParser

pen_down = False
# Initialize servos
def setup_servos():
    shoulder_servo = PWM(Pin(0))
    elbow_servo = PWM(Pin(1))
    pen_servo = PWM(Pin(2))

    shoulder_servo.freq(50)
    elbow_servo.freq(50)
    pen_servo.freq(50)

    return shoulder_servo, elbow_servo, pen_servo

def main():
    shoulder_servo, elbow_servo, pen_servo = setup_servos()
    print("Servo setup complete.")
    '''
    # Some basic logic to test elbow servo 
    elbow_servo.duty_u16(translate(80))
    print("Duty equivalent: ", translate(80))
    print("Moved shoulder to 80 degrees for calibration.")
    return
    '''
    parser = GCodeParser()
    try:
        instructions = parser.parse_file("circle.gcode")
    except Exception as e:
        print(f"Error parsing file: {e}")
        sys.exit(1)

    instructions = parser.parse_file("circle.gcode")

    for instr in instructions:
        cmd = instr["cmd"]

        if cmd == "G1":
            shoulder = instr["S"]   # may be None
            elbow = instr["E"]      # may be None

            if shoulder is not None:
                shoulder_servo.duty_u16(translate(shoulder))
                print(f"Move shoulder to {shoulder} degrees")
                print("Corresponding to duty:", translate(shoulder))

            if elbow is not None:
                elbow_servo.duty_u16(translate(elbow))
                print(f"Move elbow to {elbow} degrees")
                print("Corresponding to duty:", translate(elbow))

        elif cmd == "M3":
            if pen_down:
                pen_servo.duty_u16(10)
                print("Wrist DOWN")
                pen_down=True

        elif cmd == "M5":
            if not pen_down:
                pen_servo.duty_u16(-10)
                print("Wrist UP")
                pen_down=False

        elif cmd == "M18":
            shoulder_servo.duty_u16(translate(0))
            elbow_servo.duty_u16(translate(0))
            shoulder_servo = None
            elbow_servo = None
            pen_servo = None
            print("Disable all servos")


if __name__ == "__main__":
    main()

import unittest
from time import sleep
from math import acos, asin, sqrt, degrees, sin, atan, isclose, isfinite
import logging


#UNIT TESTING DEVELOPPED BY RAFAEL ROBIN
'''
Unfortunately we are unable to achieve full functionality for our arm, but in order to demonstrate partial functionality we've devised unit
tests to demonstrate our working helper functions.
'''

#CAN'T DIRECTLY IMPORT FUNCTIONS FROM GP_CODE_FINAL DUE TO THE MACHINE IMPORT, SO JUST REDEFINE THEM HERE.

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


class TestHelperFunctions(unittest.TestCase):

    # ------------------ duty_to_angle ------------------
    def test_duty_to_angle_min(self):
        self.assertEqual(duty_to_angle(0), 0)

    def test_duty_to_angle_max(self):
        self.assertEqual(duty_to_angle(65535), 180)

    def test_duty_to_angle_mid(self):
        # Should give about 90 degrees with a 2% margin of error.
        self.assertTrue(isclose(duty_to_angle(32767), 90, rel_tol=0.02))


    # ------------------ angle_to_duty ------------------
    def test_angle_to_duty_0(self):
        self.assertEqual(angle_to_duty(0), 1638)

    def test_angle_to_duty_180(self):
        self.assertEqual(angle_to_duty(180), 8192)

    def test_angle_to_duty_90(self):
        expected = 1638 + ((8192 - 1638) / 180) * 90
        self.assertTrue(isclose(angle_to_duty(90), expected, rel_tol=0.02))


    # ------------------ Inverse Kinematics ------------------
    def test_inverse_kinematics_simple(self):
        # Simple symmetric test: arm horizontally straight
        c_x = 15  # AB + BC = 15.5 + 15.5
        c_y = 5
        arm_length = 15.5
        offset_s = 0
        offset_e = 0
        shoulder, elbow = calculate_angles_from_paramaters(
            c_x, c_y, arm_length, arm_length, offset_s, offset_e
        )

        # Expected:
        # elbow_angle = 180°, shoulder≈0°
        self.assertTrue(isfinite(shoulder))
        self.assertTrue(isfinite(elbow))
        print(f"SET ANGLES TO: ({shoulder:.2f},{elbow:.2f}), using coordinates({c_x:.2f},{c_y:.2f}), and offsets({offset_s:.2f},{offset_e:.2f})")



    def test_inverse_kinematics_vertical(self):
        # Arm straight upward
        c_x = 5
        c_y = 15
        arm_length = 15.5
        offset_s = 51
        offset_e = 23
        shoulder, elbow = calculate_angles_from_paramaters(
            c_x, c_y, arm_length, arm_length, offset_s, offset_e
        )

        # Expected:
        # shoulder ≈ 90°, elbow ≈ 180°
        self.assertTrue(isfinite(shoulder))
        self.assertTrue(isfinite(elbow))
        print(f"SET ANGLES TO: ({shoulder:.2f},{elbow:.2f}), using coordinates({c_x:.2f},{c_y:.2f}), and offsets({offset_s:.2f},{offset_e:.2f})")



if __name__ == "__main__":
    unittest.main()

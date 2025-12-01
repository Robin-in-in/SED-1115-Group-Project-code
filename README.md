This document serves as a minimal explanation of everything needed to begin working on the servodraw project.

WHAT WE'RE TRYING TO DO:
- Using the two potentiometers on the pico board we're going to move a "shoulder" and "elbow" that will move a pen. 
- One more servo will control a "wrist" which will put the pen down onto paper or lift it just off the paper- I plan to use a button for this since we only care about the wrist being up or down


RELEVANT TEACHINGS FROM LAB 6 (Servo Input):
(If you don't understand any of this, plug it into ai for help)
- We're using the PICO board to control a servo (a mechanism that rotates, which we will use to control arms that will move a pen)
- The PWM (Pulse-Width-Modulation) refers to a mechanism the PICO provides to generate a wave which can be either "high" or "low"
- By controlling the length of time per cycle the wave is set to high/low, and reading it, we can perform certain functions
- We set the PWM to 50hz (50 cycles per second), Servos (or at least this servo) uses 50hz.
eg.
" We know that a pulse width of 500 microseconds corresponds to a position of 0 degrees, and
we also know that a pulse width of 2500 microseconds corresponds to a position of 180
degrees. " -> This only applies to a frequency of 50hz
- The ratio between the amount of time the PWM is "up" vs "down" is known as the duty cycle
- IMPORTANT: For this particular servo we can't work with the full duty-cycle range- The time of one cycle is 20 000 microseconds, but the "safe" range for this servo is 500-2500 microseconds; that corresponds to the servo being "high" between 2.5-12.5% of the cycle.
- Considering this, we perform some math to take the range read from the potentiometer 0-65535 and map it to that "safe range" (roughly 1639-8190) then further mapping that to 500-2500us

RELEVANT TEACHINGS FROM LAB 7 (Drawing):
- I don't believe we will actually be reading a Gcode file for our project implementation.
- There is useful logic in here for passing angles to the servos and drawing with them. 

RELEVANT TEACHINGS FROM LAB 8 (Arm Movement):
INVERSE KINEMATICS:
- We only want to be able to draw in the range of a given box or "Page", the question is, how are we meant to know the angles we should be able to move our shoulder/elbow such that we can only cover the range of that "box"- not more and not less
- For the shoulder and elbow, their ranges are 0 to 180 degrees- we will need to derive what angles are needed to arrive at any particular coordinate on our page.
- The process of deriving these angles is known as kinematics
- Forward kinematics would be manually moving across the entire range of motion of both and trying to figure out the limits we need to impose that way.
- Inverse kinematics is the more complex approach of starting from the endpoint (the bounds of the box) and using math to calculate the limits we would need to impose. 
- The lab contains a series of equations which will approximate the correct angle ranges for the servos- but these are just guidelines, we'll need to expirement and program some corrections
CALIBRATION:
- Because the servos are economy, the inputs we give them may not produce a consistent output- this means that for each particular servo we need to perform a test to calibrate it.
- We're going to need to give the servo an angle and see how much it actually moves, compared to how much we expect it to move- then account for that offset in our program.

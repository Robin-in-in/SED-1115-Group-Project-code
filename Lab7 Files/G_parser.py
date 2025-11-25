# CREATED USING CHATGPT, returns an instruction dictuonary for each command
# Entire file is pretty self explanitory, but for G1 commands we use regex to search for S and E values.
# Regex acts as a standard to define the pattern of the S and E values we will be searching for.
# (r"S...) look for the letter 'S' > (r"S(...)) everything in the parentheses is a capturing group; what will be returned
# [0-9.+-]+ One or more (+) characters that can be: digits 0–9, period ., plus +, or minus -
#(r"S([0-9.+-]+)")
# We then convert the values found in the capturing group to float for further processing.

import re

class GCodeParser:
    def __init__(self):
        self.instructions = []

    def parse_line(self, line):
        line = line.strip()

        # Skip empty lines or comments
        if not line or line.startswith(";"):
            return

        # --- Parse G1 --------------------------------------------------------
        if line.startswith("G1"):
            # Extract S and E values if they exist
            s_match = re.search(r"S([0-9.+-]+)", line) 
            e_match = re.search(r"E([0-9.+-]+)", line)

            s_val = float(s_match.group(1)) if s_match else None
            e_val = float(e_match.group(1)) if e_match else None

            self.instructions.append({
                "cmd": "G1",
                "S": s_val,
                "E": e_val
            })
            return

        # --- Parse M commands ------------------------------------------------
        if line == "M3":
            self.instructions.append({"cmd": "M3"})
            return

        if line == "M5":
            self.instructions.append({"cmd": "M5"})
            return

        if line == "M18":
            self.instructions.append({"cmd": "M18"})
            return

        # Unknown command
        raise ValueError(f"Unknown G-Code command: {line}")

    def parse_file(self, path):
        with open(path, "r") as f:
            for line in f:
                self.parse_line(line)
        return self.instructions


# Example usage:
if __name__ == "__main__":
    parser = GCodeParser()
    gcode = parser.parse_file("circle.gcode")

    for instr in gcode:
        print(instr)
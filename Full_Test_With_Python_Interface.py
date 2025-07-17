import serial
import time
import kociemba

# PHYSICAL COLORS:
# ===========================
# Up     = White (w)
# Down   = Yellow (y)
# Front  = Red (r)
# Right  = Blue (b)
# Left   = Green (g)
# Back   = Orange (o)
#
# Kociemba solutions:
# U = White
# D = Yellow
# F = Green
# R = Red
# L = Orange
# B = Blue
#
# Remapped Location:
#  - White stays U
#  - Yellow stays D
#  - Red (your F) must be mapped to G (Kociemba F)
#  - Blue (your R) must be mapped to R (Kociemba R)
#  - Green (your L) must be mapped to O (Kociemba L)
#  - Orange (your B) must be mapped to B (Kociemba B)
# ===========================

VALID_COLORS = ['w', 'y', 'r', 'b', 'g', 'o']
FACE_NAMES = ['U (top)', 'R (right)', 'F (front)', 'D (bottom)', 'L (left)', 'B (back)']

def input_colors():
    print("👉 Enter colors for each face (9 stickers per face, use w/y/r/b/g/o):")
    cube = ""
    for face in FACE_NAMES:
        print(f"--- {face} ---")
        count = 0
        while count < 9:
            c = input(f"Sticker {count+1}: ").strip().lower()
            if c in VALID_COLORS:
                cube += c
                count += 1
            else:
                print(f"Invalid color. Use one of {VALID_COLORS}")
    return cube

def remap_and_order(cube_str):
    U = cube_str[0:9]
    R = cube_str[9:18]
    F = cube_str[18:27]
    D = cube_str[27:36]
    L = cube_str[36:45]
    B = cube_str[45:54]

    # Map physical sticker colors to standard Kociemba faces:
    color_map = {
        'w': 'U',
        'y': 'D',
        'r': 'F',  # Red    = Front -> Kociemba = Green
        'b': 'R',  # Blue   = Right -> Kociemba = Red
        'g': 'L',  # Green  = Left  -> Kociemba = Orange
        'o': 'B',  # Orange = Back  -> Kociemba = Blue
    }

    raw_order = U + R + F + D + L + B
    final = ''.join(color_map[c] for c in raw_order)
    return final

def expand_moves(solution):
    parts = solution.split()
    expanded = []
    for m in parts:
        if m.endswith("2"):
            expanded.append(m[0])
            expanded.append(m[0])
        elif m.endswith("'"):
            expanded.append(m[0].lower())
        else:
            expanded.append(m)
    return " ".join(expanded)

# =============== Settings ===============
serial_port = 'COM5'  # Change this to your actual Arduino port
baud_rate = 9600
# ========================================

def main():
    raw_cube_string = input_colors()
    print(f"✅ Raw cube string length: {len(raw_cube_string)}")
    print(f"✅ Raw cube string: {raw_cube_string}")

    if len(raw_cube_string) != 54:
        print("❌ Cube string must be exactly 54 stickers. Exiting.")
        return

    final_cube = remap_and_order(raw_cube_string).upper()
    print(f"✅ Remapped + Ordered for Kociemba: {final_cube}")

    ser = serial.Serial(serial_port, baud_rate, timeout=10)
    time.sleep(2)  # Give Arduino time to reset

    print("🔗 Sending raw cube string to Arduino...")
    ser.write((raw_cube_string + '\n').encode())
    ser.flush()
    time.sleep(1)

    while True:
        line = ser.readline().decode(errors='ignore').strip()
        if line:
            print("Arduino:", line)
            if "Waiting for moves" in line:
                break

    # Solve using Kociemba
    try:
        solution = kociemba.solve(final_cube)
        print(f"✅ Kociemba solution: {solution}")
    except Exception as e:
        print(f"❌ Kociemba error: {e}")
        ser.close()
        return

    moves = expand_moves(solution)
    print(f"🔗 Expanded moves to Arduino: {moves}")

    ser.write((moves + '\n').encode())
    ser.flush()
    time.sleep(0.5)

    while True:
        line = ser.readline().decode(errors='ignore').strip()
        if line:
            print("Arduino:", line)
            if "Cube solved!" in line:
                break

    ser.close()

if __name__ == "__main__":
    main()

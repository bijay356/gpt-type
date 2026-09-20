import sys
import time
import os

# Enable ANSI colors on Windows terminal
os.system("")
sys.stdout.reconfigure(encoding="utf-8")

# Vibrant glowing colors for each word
COLORS = [
    "\033[93m",  # Bright Yellow
    "\033[96m",  # Bright Cyan
    "\033[95m",  # Bright Magenta
    "\033[92m",  # Bright Green
    "\033[94m",  # Bright Blue
    "\033[91m",  # Bright Red
    "\033[97m",  # Bright White
    "\033[33m",  # Warm Gold
    "\033[36m",  # Teal Cyan
    "\033[35m",  # Purple
]

BOLD = "\033[1m"
RESET = "\033[0m"

# Calibrated for ~30 seconds video
lines = [
    ("Tum jab aaogi toh khoya hua paogi mujhe", 0.45, 1.2, False),
    ("Mere tanhaion mein khwabon ke siwa kuch bhi nahin", 0.45, 2.2, True),

    ("Mere kamre ko sajane ki tamanna hain tumhe", 0.45, 1.2, False),
    ("Mere kamre ko sajane ki tamanna hain tumhe", 0.45, 1.5, False),
    ("Mere kamre mein kitabon ke siwa kuch bhi nahin", 0.48, 3.5, False),
]

color_idx = 0

print("\n")
for text, word_delay, line_pause, is_couplet_end in lines:
    words = text.split(" ")
    for i, word in enumerate(words):
        color = COLORS[color_idx % len(COLORS)]
        color_idx += 1
        sys.stdout.write(f"{color}{BOLD}{word}{RESET}")
        if i < len(words) - 1:
            sys.stdout.write(" ")
        sys.stdout.flush()
        time.sleep(word_delay)
    sys.stdout.write("\n")
    if is_couplet_end:
        print()  # Stanza spacing
    time.sleep(line_pause)

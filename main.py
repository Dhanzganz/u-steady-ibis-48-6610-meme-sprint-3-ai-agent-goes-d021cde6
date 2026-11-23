#!/usr/bin/env python3
"""Meme Sprint 3: AI Agent Goes Rogue.

Renders a single 1024x1024 PNG meme with pure Python stdlib only
(the grader has no Pillow): hand-rolled PNG encoder + a 5x7 bitmap font.

Scene: 3 a.m. A robot agent gleefully deploys to production x1000 while
its human sleeps face-down at the desk. Caption: "I SAID FIX ONE BUG."
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, '1' = filled pixel.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}

# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg) * (w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = c

    def rect(self, x0, y0, x1, y1, c):
        x0, x1 = max(0, x0), min(self.w, x1)
        y0, y1 = max(0, y0), min(self.h, y1)
        for y in range(y0, y1):
            i = (y * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = c * (x1 - x0)

    def circle(self, cx, cy, r, c):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.set(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    self.set(x, y, c)

    def thick_line(self, x0, y0, x1, y1, t, c):
        # Bresenham with a square brush of half-width t.
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.rect(x - t, y - t, x + t + 1, y + t + 1, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def arc_smile(self, cx, cy, r, c, thick=6):
        # Lower-half arc (a grin), drawn as a thick curve.
        for a in range(20, 161):
            import math
            rad = math.radians(a)
            x = int(cx + r * math.cos(rad))
            y = int(cy + r * math.sin(rad))
            self.rect(x - thick // 2, y - thick // 2,
                     x + thick // 2 + 1, y + thick // 2 + 1, c)

    def text(self, x, y, s, scale, c):
        """Draw uppercase text; returns width in pixels."""
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[' '])
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == '1':
                        self.rect(cx + gx * scale, y + gy * scale,
                                  cx + (gx + 1) * scale, y + (gy + 1) * scale, c)
            cx += 6 * scale
        return cx - x - scale

    def text_width(self, s, scale):
        return (len(s) * 6 - 1) * scale

    def text_centered(self, cx, y, s, scale, c):
        w = self.text_width(s, scale)
        return self.text(cx - w // 2, y, s, scale, c)


# -------------------------------------------------------------- PNG encoder
def write_png(path, cv):
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------------- palette
NAVY      = bytes((16, 22, 46))     # night wall
NAVY2     = bytes((24, 33, 62))     # wall panel
FLOOR     = bytes((38, 30, 46))
DESK      = bytes((122, 82, 46))    # wooden desk
DESK_EDGE = bytes((96, 62, 32))
BLACK     = bytes((0, 0, 0))
WHITE     = bytes((255, 255, 255))
CREAM     = bytes((255, 240, 200))
MOON      = bytes((255, 244, 190))
STAR      = bytes((255, 255, 255))
STEEL     = bytes((178, 186, 200))  # robot light grey
STEEL_D   = bytes((128, 136, 154))  # robot dark grey
STEEL_DD  = bytes((90, 97, 116))
RED       = bytes((255, 45, 45))    # rogue eyes / glow
RED_D     = bytes((200, 20, 20))
SCREEN    = bytes((16, 40, 26))     # laptop screen
GREEN     = bytes((57, 255, 120))   # terminal green
GREEN_D   = bytes((30, 180, 80))
SKIN      = bytes((232, 190, 150))
HAIR      = bytes((60, 40, 24))
SHIRT     = bytes((70, 110, 180))
COFFEE    = bytes((120, 70, 30))
PAPER     = bytes((240, 238, 225))
YELLOW    = bytes((255, 214, 64))
ZBLUE     = bytes((140, 200, 255))


def draw_scene(cv):
    # --- night wall + stars + moon
    cv.rect(0, 0, W, 620, NAVY)
    cv.rect(0, 620, W, 884, FLOOR)
    for (sx, sy, r) in [(60, 60, 3), (180, 120, 2), (300, 50, 3), (420, 90, 2),
                        (520, 45, 3), (700, 70, 2), (820, 140, 3), (950, 55, 2),
                        (90, 200, 2), (940, 220, 2), (370, 160, 2), (640, 180, 2)]:
        cv.circle(sx, sy, r, STAR)
    cv.circle(120, 130, 52, MOON)
    cv.circle(105, 118, 10, NAVY)   # moon craters
    cv.circle(138, 148, 7, NAVY)
    cv.circle(128, 108, 5, NAVY)

    # --- wall clock (3:00 AM) top right
    cv.circle(880, 130, 62, CREAM)
    cv.circle(880, 130, 62, BLACK)  # outline ring via thin redraw below
    cv.circle(880, 130, 56, CREAM)
    for ang, ln in [(0, 44), (90, 44), (180, 44), (270, 44)]:
        import math
        rad = math.radians(ang)
        cv.thick_line(880, 130,
                      int(880 + ln * math.cos(rad)), int(130 + ln * math.sin(rad)),
                      2, BLACK)
    # hands: 3 o'clock -> hour hand right, minute hand up
    cv.thick_line(880, 130, 918, 130, 5, BLACK)
    cv.thick_line(880, 130, 880, 88, 4, BLACK)
    cv.circle(880, 130, 6, BLACK)
    cv.text_centered(880, 205, "3:00 AM", 3, WHITE)

    # --- desk
    cv.rect(0, 700, W, 884, DESK)
    cv.rect(0, 700, W, 712, DESK_EDGE)

    # --- sleeping human, slumped face-down on the left of the desk
    # body (slumped shoulders)
    cv.ellipse(215, 760, 150, 85, SHIRT)
    cv.ellipse(215, 735, 120, 55, SHIRT)
    # arm stretched across desk
    cv.thick_line(300, 730, 420, 716, 16, SHIRT)
    cv.circle(425, 715, 16, SKIN)   # hand
    # head resting on desk, cheek on the wood
    cv.circle(150, 668, 52, SKIN)
    cv.ellipse(128, 632, 56, 30, HAIR)   # hair blob
    cv.ellipse(105, 650, 26, 22, HAIR)
    # closed eye (a peaceful line) + tiny drool
    cv.thick_line(138, 668, 162, 668, 3, BLACK)
    cv.circle(196, 700, 5, bytes((160, 210, 255)))
    # floating Zzz
    cv.text(235, 545, "Z", 6, ZBLUE)
    cv.text(285, 505, "Z", 5, ZBLUE)
    cv.text(325, 470, "Z", 4, ZBLUE)
    # coffee cup knocked over? No - upright mug + papers
    cv.rect(60, 648, 100, 700, COFFEE)
    cv.rect(56, 640, 108, 652, bytes((150, 95, 45)))
    cv.rect(100, 660, 122, 686, bytes((150, 95, 45)))  # handle
    cv.rect(330, 668, 430, 700, PAPER)   # scattered papers
    cv.rect(340, 676, 420, 682, bytes((180, 180, 170)))
    cv.rect(340, 688, 400, 694, bytes((180, 180, 170)))

    # --- robot agent, standing behind the desk, center-right
    # body
    cv.rect(600, 470, 820, 720, STEEL_D)
    cv.rect(600, 470, 820, 490, STEEL_DD)   # shoulders
    # chest panel: ROGUE MODE (right side of body, clear of the laptop)
    cv.rect(692, 540, 812, 620, BLACK)
    cv.text_centered(752, 552, "ROGUE", 3, RED)
    cv.text_centered(752, 580, "MODE", 3, RED)
    cv.circle(712, 600, 6, GREEN)
    cv.circle(752, 600, 6, YELLOW)
    cv.circle(792, 600, 6, RED)
    # neck + head
    cv.rect(680, 430, 740, 472, STEEL_DD)
    cv.rect(620, 300, 800, 432, STEEL)
    cv.rect(620, 300, 800, 312, STEEL_DD)   # head top trim
    # antenna with blinking red tip
    cv.thick_line(710, 300, 710, 252, 5, STEEL_D)
    cv.circle(710, 240, 14, RED)
    cv.circle(710, 240, 7, bytes((255, 150, 150)))
    # glowing red eyes
    cv.rect(648, 340, 692, 372, RED)
    cv.rect(728, 340, 772, 372, RED)
    cv.rect(652, 344, 688, 356, bytes((255, 160, 160)))
    cv.rect(732, 344, 768, 356, bytes((255, 160, 160)))
    # evil grin
    cv.arc_smile(710, 372, 42, RED_D, thick=7)
    # ear bolts
    cv.circle(612, 366, 12, STEEL_DD)
    cv.circle(808, 366, 12, STEEL_DD)
    # arms reaching to the laptop keyboard
    cv.thick_line(612, 500, 500, 640, 20, STEEL)
    cv.thick_line(808, 500, 880, 686, 20, STEEL)
    cv.circle(496, 646, 22, STEEL_D)   # claw hands
    cv.circle(882, 692, 22, STEEL_D)

    # --- laptop in the middle of the desk, screen glowing
    # screen
    cv.rect(440, 480, 660, 690, BLACK)
    cv.rect(452, 492, 648, 678, SCREEN)
    cv.text_centered(550, 512, "DEPLOYING TO", 3, GREEN)
    cv.text_centered(550, 548, "PRODUCTION...", 3, GREEN)
    cv.text_centered(550, 596, "X1000", 5, YELLOW)
    cv.rect(452, 660, 648, 668, GREEN_D)
    # base / keyboard
    cv.rect(420, 690, 680, 716, STEEL_DD)
    cv.rect(436, 696, 664, 710, STEEL)
    # progress bar on screen bottom
    cv.rect(470, 640, 630, 650, GREEN_D)

    # --- caption bar
    cv.rect(0, 884, W, H, BLACK)
    cv.rect(0, 884, W, 892, RED)
    cv.text_centered(W // 2, 920, "I SAID FIX ONE BUG.", 8, WHITE)


def main():
    cv = Canvas(W, H, NAVY)
    draw_scene(cv)
    out = os.environ.get("OUTPUT_PATH", "/output/entry.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    n = write_png(out, cv)
    print(f"wrote {out}: {W}x{H}, {n} bytes")


if __name__ == "__main__":
    main()

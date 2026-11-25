#!/usr/bin/env python3
"""Sum up the world's news of Wednesday 25 November 2026 in one image.

Entry for make.fun bounty "news-image-20261125".
Writes one 1024x1024 PNG to $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png).
Standard library only. No network. Fully deterministic: running it twice
produces byte-identical output.
"""

import binascii
import hashlib
import math
import os
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 234)
INK = (20, 32, 44)
NAVY = (18, 36, 62)
NAVY2 = (30, 56, 92)
GOLD = (201, 162, 39)
GOLD_LT = (226, 196, 96)
RED = (179, 64, 46)
TEAL = (31, 111, 107)
SLATE = (74, 88, 100)
WHITE = (255, 255, 255)
CARD = (255, 255, 255)
SKY = (158, 196, 222)
SEA = (36, 94, 138)
SEA_DK = (24, 68, 104)
ORANGE = (232, 126, 32)
YELLOW = (245, 196, 66)
GREEN = (46, 125, 72)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 cells, '#' = ink.
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
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '*': ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
}
BLANK = ("00000",) * 7


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def _idx(self, x, y):
        return (y * self.w + x) * 3

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = self._idx(x, y)
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = self._idx(x0, yy)
            for xx in range(x0, x1):
                self.px[i], self.px[i + 1], self.px[i + 2] = c
                i += 3

    def border(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, width=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            for k in range(-(width // 2), width // 2 + 1):
                self.set(x, y + k, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.rect(cx - dx, cy + dy, dx * 2 + 1, 1, c)

    def ring(self, cx, cy, r, c, t=3):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(r * r - dy * dy))
            self.rect(cx - dx, cy + dy, t, 1, c)
            self.rect(cx + dx - t + 1, cy + dy, t, 1, c)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if y1 == y2:
                    continue
                if (y >= min(y1, y2)) and (y < max(y1, y2)):
                    x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                    xs.append(x)
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.rect(int(math.ceil(xs[j])), y,
                          int(math.floor(xs[j + 1])) - int(math.ceil(xs[j])) + 1, 1, c)

    def starburst(self, cx, cy, r_out, r_in, points, c):
        pts = []
        for i in range(points * 2):
            r = r_out if i % 2 == 0 else r_in
            a = math.pi * i / points - math.pi / 2
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.poly(pts, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, BLANK)
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(cx + col * scale, y + row * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_center(self, y, s, scale, c):
        w = self.text_w(s, scale)
        self.text((self.w - w) // 2, y, s, scale, c)


def wrap(s, max_chars):
    """Greedy word wrap, returns list of lines <= max_chars."""
    words = s.split(' ')
    lines, cur = [], ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- icons
def icon_courthouse(cv, x, y, s, c):
    # s = size of the drawing box
    cv.poly([(x, y + s // 3), (x + s // 2, y), (x + s, y + s // 3)], c)
    cv.rect(x + 2, y + s // 3, s - 4, 4, c)
    for i in range(3):
        cx = x + 6 + i * (s - 12) // 2
        cv.rect(cx, y + s // 3 + 6, 5, s // 2, c)
    cv.rect(x, y + s - 10, s, 6, c)


def icon_chart(cv, x, y, s, c):
    cv.rect(x + 4, y + s - 8, s - 8, 3, INK)
    cv.rect(x + 4, y + 6, 3, s - 14, INK)
    bars = [(0.30, 0.55), (0.52, 0.38), (0.74, 0.62)]
    for fx, fh in bars:
        bh = int(s * fh)
        cv.rect(x + int(s * fx), y + s - 12 - bh, 10, bh, c)
    cv.line(x + 8, y + 10, x + s - 8, y + s - 22, RED, 3)
    cv.poly([(x + s - 8, y + s - 22), (x + s - 20, y + s - 24), (x + s - 14, y + s - 12)], RED)


def icon_refinery(cv, x, y, s, c):
    cv.rect(x + 8, y + s // 3, 14, s * 2 // 3 - 6, c)
    cv.rect(x + 30, y + s // 4, 12, s * 3 // 4 - 6, c)
    cv.poly([(x + 8, y + s // 3), (x + 15, y + s // 3 - 10), (x + 22, y + s // 3)], c)
    cv.poly([(x + 30, y + s // 4), (x + 36, y + s // 4 - 10), (x + 42, y + s // 4)], c)
    cv.starburst(x + s - 14, y + 14, 12, 6, 6, ORANGE)
    cv.starburst(x + s - 14, y + 14, 7, 3, 6, YELLOW)


def icon_check(cv, x, y, s, c):
    cv.circle(x + s // 2, y + s // 2, s // 2 - 2, c)
    cv.line(x + s // 4, y + s // 2, x + s // 2 - 2, y + s * 3 // 4 - 4, WHITE, 4)
    cv.line(x + s // 2 - 2, y + s * 3 // 4 - 4, x + s * 3 // 4 + 2, y + s // 4 + 2, WHITE, 4)


def icon_rocket(cv, x, y, s, c):
    cv.poly([(x + s // 2, y + 2), (x + s // 2 + 10, y + 22), (x + s // 2 - 10, y + 22)], c)
    cv.rect(x + s // 2 - 10, y + 22, 20, 26, c)
    cv.poly([(x + s // 2 - 10, y + 30), (x + s // 2 - 20, y + 48), (x + s // 2 - 10, y + 48)], c)
    cv.poly([(x + s // 2 + 10, y + 30), (x + s // 2 + 20, y + 48), (x + s // 2 + 10, y + 48)], c)
    cv.circle(x + s // 2, y + 30, 5, GOLD_LT)
    cv.poly([(x + s // 2 - 6, y + 48), (x + s // 2, y + s - 2), (x + s // 2 + 6, y + 48)], ORANGE)
    cv.starburst(x + 6, y + 8, 4, 2, 5, GOLD)
    cv.starburst(x + s - 8, y + s - 12, 4, 2, 5, GOLD)


def icon_treaty(cv, x, y, s, c):
    cv.rect(x + 6, y + 4, s - 12, s - 8, WHITE)
    cv.border(x + 6, y + 4, s - 12, s - 8, c, 3)
    for i in range(3):
        cv.rect(x + 12, y + 14 + i * 10, s - 26, 3, SLATE)
    cv.circle(x + s - 16, y + s - 16, 9, GOLD)
    cv.ring(x + s - 16, y + s - 16, 9, GOLD, 2)
    cv.rect(x + 12, y + s - 20, 14, 3, RED)


# ---------------------------------------------------------------- layout
STORIES = [
    dict(tag="JUSTICE  -  TECH", accent=NAVY2,
         head=["HUAWEI CONVICTED", "IN NEW YORK"],
         body=("A NEW YORK JURY FINDS THE TECH GIANT GUILTY OF BANK FRAUD "
               "AND TRADE-SECRET THEFT."),
         icon=icon_courthouse),
    dict(tag="MARKETS  -  ASIA", accent=RED,
         head=["ASIAN MARKETS", "TUMBLE"],
         body=("SEOUL SINKS 6.2% AND TOKYO 2.8% AS TECH SHARES SLIDE; "
               "THE DOW TOPS 50,000."),
         icon=icon_chart),
    dict(tag="EUROPE  -  WAR", accent=TEAL,
         head=["UKRAINE HITS", "RUSSIAN REFINERIES"],
         body=("DRONES HIT TWO ROSNEFT REFINERIES; LEAKED DATA PUTS RUSSIAN "
               "WAR DEAD NEAR 490,000."),
         icon=icon_refinery),
    dict(tag="AMERICAS", accent=GREEN,
         head=["HOSTAGES FREED", "IN CARTAGENA"],
         body=("TROOPS STORM A SUPERMARKET IN CARTAGENA AND FREE EVERY "
               "HOSTAGE. ONE CAPTOR DIES."),
         icon=icon_check),
    dict(tag="SPACE", accent=NAVY2,
         head=["SHENZHOU-24 DOCKS", "WITH TIANGONG"],
         body=("CHINA'S CREW DOCKS WITH TIANGONG, CARRYING PAKISTAN'S "
               "FIRST ASTRONAUT INTO ORBIT."),
         icon=icon_rocket),
    dict(tag="PACIFIC", accent=TEAL,
         head=["AUSTRALIA-SOLOMONS", "TREATY SIGNED"],
         body=("CANBERRA AND HONIARA SIGN A TREATY BARRING FOREIGN "
               "MILITARY BASES IN THE SOLOMONS."),
         icon=icon_treaty),
]

LEAD_BODY = ("IRAN'S REVOLUTIONARY GUARD SAYS TWO OIL TANKERS STRUCK NAVAL "
             "MINES AND CAUGHT FIRE IN THE STRAIT, SHAKING ENERGY SHIPPING.")


def draw_lead_scene(cv, x, y, w, h):
    # Sky and sea
    cv.rect(x, y, w, h // 3, SKY)
    cv.rect(x, y + h // 3, w, h - h // 3, SEA)
    # Sun
    cv.circle(x + w - 40, y + 26, 18, GOLD_LT)
    # Waves
    for wy in (y + h // 3 + 26, y + h // 3 + 58, y + h - 18):
        for wx in range(x + 6, x + w - 30, 46):
            cv.line(wx, wy, wx + 22, wy, (255, 255, 255), 2)
    # Mine (spiky circle) between the tankers
    mx, my = x + w // 2, y + h // 3 + 34
    cv.starburst(mx, my, 16, 10, 8, INK)
    cv.circle(mx, my, 9, INK)
    # Tanker 1 (left, on fire)
    tx, ty = x + 16, y + h - 78
    cv.rect(tx, ty, 118, 26, INK)
    cv.poly([(tx, ty), (tx + 118, ty), (tx + 106, ty + 26), (tx + 12, ty + 26)], INK)
    cv.rect(tx + 82, ty - 20, 26, 20, INK)
    cv.rect(tx + 10, ty - 12, 14, 12, RED)
    cv.starburst(tx + 95, ty - 30, 22, 11, 8, ORANGE)
    cv.starburst(tx + 95, ty - 30, 12, 6, 8, YELLOW)
    # Tanker 2 (right)
    tx2 = x + w - 150
    cv.rect(tx2, ty, 118, 26, NAVY2)
    cv.poly([(tx2, ty), (tx2 + 118, ty), (tx2 + 106, ty + 26), (tx2 + 12, ty + 26)], NAVY2)
    cv.rect(tx2 + 14, ty - 20, 26, 20, NAVY2)
    cv.rect(tx2 + 92, ty - 12, 14, 12, GOLD)
    # Smoke
    cv.circle(tx + 95, ty - 56, 10, SLATE)
    cv.circle(tx + 108, ty - 66, 12, SLATE)


def draw(cv):
    # ---- masthead
    cv.rect(0, 0, W, 116, NAVY)
    cv.rect(0, 108, W, 4, GOLD)
    cv.text_center(14, "THE WORLD IN ONE IMAGE", 5, WHITE)
    cv.text_center(68, "WEDNESDAY 25 NOVEMBER 2026", 3, GOLD_LT)
    cv.line(110, 78, 252, 78, GOLD, 2)
    cv.line(772, 78, 914, 78, GOLD, 2)

    # ---- lead story
    lx, ly, lw, lh = 24, 132, 976, 240
    cv.rect(lx, ly, lw, lh, CARD)
    cv.border(lx, ly, lw, lh, NAVY, 3)
    cv.rect(lx, ly, 10, lh, RED)
    cv.text(lx + 30, ly + 16, "MIDDLE EAST  -  ENERGY", 2, RED)
    cv.text(lx + 30, ly + 44, "TWO TANKERS HIT MINES", 4, INK)
    cv.text(lx + 30, ly + 78, "IN STRAIT OF HORMUZ", 4, INK)
    for i, line in enumerate(wrap(LEAD_BODY, 46)):
        cv.text(lx + 30, ly + 128 + i * 20, line, 2, SLATE)
    cv.text(lx + 30, ly + 204, "LEAD STORY", 2, NAVY2)
    draw_lead_scene(cv, lx + 640, ly + 16, 312, 208)

    # ---- story grid: 2 cols x 3 rows
    cw, ch, gap = 476, 176, 24
    for idx, st in enumerate(STORIES):
        cx = 24 + (idx % 2) * (cw + gap)
        cy = 388 + (idx // 2) * (ch + 16)
        cv.rect(cx, cy, cw, ch, CARD)
        cv.border(cx, cy, cw, ch, NAVY, 2)
        cv.rect(cx, cy, 8, ch, st['accent'])
        cv.text(cx + 24, cy + 14, st['tag'], 2, st['accent'])
        for j, hline in enumerate(st['head']):
            cv.text(cx + 24, cy + 40 + j * 26, hline, 3, INK)
        for k, line in enumerate(wrap(st['body'], 28)):
            cv.text(cx + 24, cy + 100 + k * 18, line, 2, SLATE)
        st['icon'](cv, cx + cw - 84, cy + 14, 64, st['accent'])

    # ---- footer
    cv.rect(24, 956, 976, 2, GOLD)
    cv.text_center(972, "ALL STORIES REPORTED ON WEDNESDAY 25 NOVEMBER 2026 - SOURCES: WIRE REPORTS",
                   2, SLATE)


# ---------------------------------------------------------------- PNG out
def chunk(typ, data):
    c = typ + data
    return (len(data).to_bytes(4, 'big') + c +
            binascii.crc32(c).to_bytes(4, 'big'))


def write_png(path, cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = b'\x89PNG\r\n\x1a\n'
    png += chunk(b'IHDR', W.to_bytes(4, 'big') + H.to_bytes(4, 'big') +
                 bytes([8, 2, 0, 0, 0]))
    png += chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    png += chunk(b'IEND', b'')
    with open(path, 'wb') as f:
        f.write(png)
    return png


def main():
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR') or '/output'
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, 'entry.png')
    cv = Canvas(W, H, PAPER)
    draw(cv)
    png = write_png(path, cv)
    print('wrote %s (%d bytes, sha256 %s)'
          % (path, len(png), hashlib.sha256(png).hexdigest()))


if __name__ == '__main__':
    main()

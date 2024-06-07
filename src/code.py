from connected_variables import ConnectedVariables
import time
import board
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis

# connected variables
cv = ConnectedVariables()
cv.define("cur_color", [16, 0, 0])
cv.define("cur_x", 0)
cv.define("cur_y", 0)
cv.define("clear", False)
last_clear = False
# tile set up

i2c = busio.I2C(board.SCL, board.SDA)
trelli = [  # adjust these to match your jumper settings if needed
     [NeoTrellis(i2c, False, addr=0x2E), NeoTrellis(i2c, False, addr=0x2F)],
     [NeoTrellis(i2c, False, addr=0x30), NeoTrellis(i2c, False, addr=0x31)]
]
trellis = MultiTrellis(trelli)

OFF = 0x000000
RED = 0x100000
YELLOW = 0x100c00
GREEN = 0x000c00
CYAN = 0x000303
BLUE = 0x000010
PURPLE = 0x130010

colors = [OFF, RED, YELLOW, GREEN, CYAN, BLUE, PURPLE]
        
color_table = [  # you can make custom color sections for clarity
  1, 1, 1, 1, 5, 5, 5, 5,
  1, 1, 1, 1, 5, 5, 5, 5,
  1, 1, 1, 1, 5, 5, 5, 5,
  1, 1, 1, 1, 5, 5, 5, 5,
  4, 4, 4, 4, 6, 6, 6, 6,
  4, 4, 4, 4, 6, 6, 6, 6,
  4, 4, 4, 4, 6, 6, 6, 6,
  4, 4, 4, 4, 6, 6, 6, 6
]

def rgb2hex(color):
    return (color[0] * 256 + color[1]) * 256 + color[2]

# convert an x,y (0-7,0-7) to 0-63
def xy_to_pos(x,y):
    return x+(y*8)

# convert 0-63 to x,y
def pos_to_xy(pos):
    return (pos%8, pos//8)
    
def init_pad():
    for x in range(8):
        for y in range(8):
            pos = xy_to_pos(x,y)
            trellis.color(x,y, colors[color_table[pos]])
            time.sleep(0.01)
            
    for x in range(8):
        for y in range(8):
            pos = xy_to_pos(x,y)
            trellis.color(x,y, 0)
            time.sleep(0.01)
        
def paint (x, y, edge):
    if edge == NeoTrellis.EDGE_RISING:
        cv.write('cur_x', x)
        cv.write('cur_y', y)
        trellis.color(
            x,
            y,
            rgb2hex(cv.read('cur_color'))
        )
        
for y_pad in range(8):
    for x_pad in range(8):
        trellis.activate_key(x_pad, y_pad, NeoTrellis.EDGE_RISING)
        trellis.activate_key(x_pad, y_pad, NeoTrellis.EDGE_FALLING)
        trellis.set_callback(x_pad, y_pad, paint)
        time.sleep(0.005)

def handle_clear():
    cur_clear = cv.read('clear')
    if not last_clear and cur_clear:
        init_pad()
        
init_pad()
while True:
    cv.heart_beat()
    handle_clear()
    trellis.sync()
import sys
import importlib
import sdl2.ext
from asm import *
from cpu import CPU, from_bits

SCREEN_W = 276
SCREEN_H = 276

P_PRINT = 0
P_SETCOLOR = 1
P_SETPIXEL = 2
P_FLIP = 3


class Ports:
    def __init__(self, window):
        self.color = sdl2.ext.Color(255, 255, 255)
        self.window = window
        surface = self.window.get_surface()
        sdl2.ext.fill(surface, sdl2.ext.Color(0, 0, 0))
        self.screen = sdl2.ext.PixelView(surface)

    def read(self, port):
        return 0
    
    def write(self, port, val):
        if port == P_PRINT:
            print(from_bits(val, 32))
        elif port == P_SETCOLOR:
            r = (val >> 16) & 0xff
            g = (val >> 8) & 0xff
            b = val & 0xff
            self.color = sdl2.ext.Color(r, g, b)
        elif port == P_SETPIXEL:
            x = val >> 16
            y = val & 0xffff
            self.screen[y][x] = self.color
        elif port == P_FLIP:
            self.window.refresh()


def sim(mod):
    sdl2.ext.init()
    window = sdl2.ext.Window("sdlsim", size=(SCREEN_W, SCREEN_H))
    window.show()
    cpu = CPU(Ports(window))
    code = asm(mod.main)
    cpu.cmem[:len(code)] = code
    if 'data' in dir(mod):
        cpu.dmem[:len(mod.data)] = mod.data
    while True:
        cpu.step()
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                sys.exit()


if len(sys.argv) == 2:
    sim(importlib.import_module(sys.argv[1].replace('.py', '')))

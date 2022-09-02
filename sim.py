import sys
import importlib
from asm import *
from cpu import CPU, from_bits

P_PRINT = 0


class Ports:
    def read(self, port):
        return 0
    
    def write(self, port, val):
        if port == P_PRINT:
            print(from_bits(val, 32))


def sim(mod, n):
    cpu = CPU(Ports())
    code = asm(mod.main)
    cpu.cmem[:len(code)] = code
    if 'data' in dir(mod):
        cpu.dmem[:len(mod.data)] = mod.data
    for _ in range(n):
        cpu.step()


if len(sys.argv) == 3:
    sim(importlib.import_module(sys.argv[1].replace('.py', '')),
        int(sys.argv[2]))

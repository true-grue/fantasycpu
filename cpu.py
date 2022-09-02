THREADS = 8

FMT = [
    '''
    setlocal setglobal setpc setsp setgp jz jnz call thread read write
    '''.split(),
    16,
    'add sub and or xor shl shr shra lt ult lit mul'.split(),
    'imm simm local global'.split(),
    16,
    'imm simm local sp'.split(),
    16
]


def get_bitfield(x, start, size):
    mask = (1 << size) - 1
    return (x >> start) & mask


def to_bits(x, bits):
    return x & (2 ** bits - 1)


def from_bits(x, bits):
    return (-1 << bits) | x if x >> (bits - 1) else x


def decode(fmt, cmd):
    vals = []
    offs = 0
    for field in reversed(fmt):
        if isinstance(field, list):
            size = len(field).bit_length()
            vals.append(field[get_bitfield(cmd, offs, size)])
        else:
            size = field
            vals.append(get_bitfield(cmd, offs, size))
        offs += size
    return tuple(reversed(vals))


def encode(fmt, *vals):
    cmd = 0
    offs = 0
    for field, val in reversed(list(zip(fmt, vals))):
        if isinstance(field, list):
            size = len(field).bit_length()
            val = field.index(val)
        else:
            size = field
        cmd |= to_bits(val, size) << offs
        offs += size
    return cmd


def sign_extend(x):
    return x | 0xffff0000 if x >> 15 else x


def load(mem, addr):
    return mem[to_bits(addr, 16)]


def store(mem, addr, val):
    mem[to_bits(addr, 16)] = val


class Thread:
    def __init__(self):
        self.pc = 0
        self.sp = 65535
        self.gp = 0
        self.active = 0


class CPU:
    def __init__(self, ports):
        self.cmem = [0] * 65536
        self.dmem = [0] * 65536
        self.threads = [Thread() for _ in range(THREADS)]
        self.thread_idx = 0
        self.thread = self.threads[self.thread_idx]
        self.thread.active = 1
        self.ports = ports

    def mem_flow(self, op, dest, y):
        if op == 'setlocal':
            store(self.dmem, self.thread.sp + dest, y)
        elif op == 'setglobal':
            store(self.dmem, self.thread.gp + dest, y)
        elif op == 'setpc':
            if dest:
                self.threads[(y >> 16) % THREADS].pc = to_bits(y, 16)
            else:
                self.thread.pc = to_bits(y, 16)
        elif op == 'setsp':
            self.thread.sp = to_bits(y, 16)
        elif op == 'setgp':
            self.thread.gp = to_bits(y, 16)
        elif op == 'jz':
            if not y:
                self.thread.pc = dest
        elif op == 'jnz':
            if y:
                self.thread.pc = dest
        elif op == 'call':
            store(self.dmem, self.thread.sp + dest, self.thread.pc)
            self.thread.pc = to_bits(y, 16)
        elif op == 'thread':
            self.threads[y % THREADS].active = dest & 1
        elif op == 'read':
            store(self.dmem, y, self.ports.read(dest))
        elif op == 'write':
            self.ports.write(dest, y)

    def alu(self, op, x1, x2):
        if op == 'add':
            return x1 + x2
        if op == 'sub':
            return x1 - x2
        if op == 'and':
            return x1 & x2
        if op == 'or':
            return x1 | x2
        if op == 'xor':
            return x1 ^ x2
        if op == 'shl':
            return x1 << x2
        if op == 'shr':
            return x1 >> x2
        if op == 'shra':
            return from_bits(x1, 32) >> x2
        if op == 'lt':
            return int(from_bits(x1, 32) < from_bits(x2, 32))
        if op == 'ult':
            return int(x1 < x2)
        if op == 'lit':
            return (x1 << 16) | x2
        elif op == 'mul':
            return x1 * x2
            
    def load_x1(self, op, x_src):
        if op == 'imm':
            return x_src
        if op == 'simm':
            return sign_extend(x_src)
        if op == 'local':
            return load(self.dmem, self.thread.sp + x_src)
        if op == 'global':
            return load(self.dmem, self.thread.gp + x_src)

    def load_x2(self, op, x_src):
        if op == 'imm':
            return x_src
        if op == 'simm':
            return sign_extend(x_src)
        if op == 'local':
            return load(self.dmem, self.thread.sp + x_src)
        if op == 'sp':
            return self.thread.sp

    def thread_step(self):
        cmd = load(self.cmem, self.thread.pc)
        self.thread.pc = to_bits(self.thread.pc + 1, 16)
        mem_flow_op, dest, alu_op, x1_op, x1_src, x2_op, x2_src = decode(
            FMT, cmd)
        x1 = self.load_x1(x1_op, x1_src)
        x2 = self.load_x2(x2_op, x2_src)
        y = to_bits(self.alu(alu_op, x1, x2), 32)
        self.mem_flow(mem_flow_op, dest, y)

    def step(self):
        for _ in range(THREADS):
            self.thread = self.threads[self.thread_idx]
            self.thread_idx = (self.thread_idx + 1) % THREADS
            if self.thread.active:
                self.thread_step()
                break

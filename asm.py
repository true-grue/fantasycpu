from cpu import encode, FMT


def imm(x):
    return ('imm', x)


def simm(x):
    return ('simm', x)


sp = ('sp', 0)


def loc(x):
    return ('local', x)


def glob(x):
    return ('global', x)


def alu(op, x1, x2):
    return (op, *x1, *x2)


def add(x1, x2):
    return alu('add', x1, x2)


def sub(x1, x2):
    return alu('sub', x1, x2)


def band(x1, x2):
    return alu('and', x1, x2)


def bor(x1, x2):
    return alu('or', x1, x2)


def bxor(x1, x2):
    return alu('xor', x1, x2)


def shl(x1, x2):
    return alu('shl', x1, x2)


def shr(x1, x2):
    return alu('shr', x1, x2)


def sha(x1, x2):
    return alu('shra', x1, x2)


def lt(x1, x2):
    return alu('lt', x1, x2)


def ult(x1, x2):
    return alu('ult', x1, x2)


def lit(x):
    return alu('lit', imm(x >> 16), imm(x & 0xffff))


def mul(x1, x2):
    return alu('mul', x1, x2)


def getloc(x):
    return alu('add', loc(x), imm(0))


def getglob(x):
    return alu('add', glob(x), imm(0))


def setloc(dest, alu):
    return ('setlocal', dest, *alu)


def setglob(dest, alu):
    return ('setglobal', dest, *alu)


def setsp(alu):
    return ('setsp', 0, *alu)


def setgp(alu):
    return ('setgp', 0, *alu)


def jz(dest, alu):
    return ('jz', dest, *alu)


def jnz(dest, alu):
    return ('jnz', dest, *alu)


def jmp(dest):
    return ('jz', dest, *lit(0))


ret = ('setpc', 0, *add(loc(0), imm(0)))


def call(dest):
    return ('call', 0, *alu('lit', imm(0), imm(dest)))


def read(port, alu):
    return ('read', port, *alu)


def write(port, alu):
    return ('write', port, *alu)


def flatten(lst):
    result = []
    for x in lst:
        result += flatten(x) if isinstance(x, list) else [x]        
    return result


def extract_labels(labels, block):
    result = []
    for cmd in block:
        if isinstance(cmd, str):
            labels[cmd] = len(result)
        else:
            result.append(cmd)
    return result


def resolve_names(names, block):
    result = []
    for cmd in block:
        if isinstance(cmd, tuple):
            result.append(tuple(names.get(val, val) for val in cmd))
        else:
            result.append(cmd)
    return result


def rename_labels(prefix, block):
    result = []
    labels = {}
    for cmd in block:
        if isinstance(cmd, str):
            labels[cmd] = f'{prefix}.{cmd}'
            result.append(labels[cmd])
        else:
            result.append(cmd)
    return resolve_names(labels, result)


def parse_loc(loc):
    loc, *sz = loc.split(':')
    return (loc, int(sz[0]) if sz else 1)


def parse_locs(locs):
    return [parse_loc(loc) for loc in locs.split()]


def proc(name, args, locs, body):
    locs = parse_locs(args) + parse_locs(locs)
    names = {}
    offs = 1
    for v, i in reversed(locs):
        names[v] = offs
        offs += i
    size = len(locs) + 1
    return [
        name,
        setsp(add(imm(-size), sp)),
        *resolve_names(names, rename_labels(name, body)),
        setsp(add(imm(size), sp)),
        ret
    ]


def encode_all(block):
    return [encode(FMT, *vals) for vals in block]


def asm(block):
    names = {}
    block = extract_labels(names, flatten(block))
    return encode_all(resolve_names(names, block))

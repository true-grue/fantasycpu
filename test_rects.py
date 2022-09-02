from asm import *

SEED = 0
P_SETCOLOR = 1
P_SETPIXEL = 2
P_FLIP = 3

fillrect = proc('fillrect', 'x y w h', 'x_end y_end i j', [
    setloc('x_end', add(loc('x'), loc('w'))),
    setloc('y_end', add(loc('y'), loc('h'))),
    setloc('j', getloc('y')),
'fillrect_h',
    setloc('i', getloc('x')),
'fillrect_w',
    write(P_SETPIXEL, alu('lit', loc('i'), loc('j'))),
    setloc('i', add(loc('i'), imm(1))),
    jnz('fillrect_w', lt(loc('i'), loc('x_end'))),
    setloc('j', add(loc('j'), imm(1))),
    jnz('fillrect_h', lt(loc('j'), loc('y_end')))
])    

xorshift = proc('xorshift', '', 'x y', [
    setloc('x', getglob(SEED)),
    setloc('y', shl(loc('x'), imm(13))),
    setloc('x', bxor(loc('x'), loc('y'))),
    setloc('y', shr(loc('x'), imm(17))),
    setloc('x', bxor(loc('x'), loc('y'))),
    setloc('y', shl(loc('x'), imm(5))),
    setloc('x', bxor(loc('x'), loc('y'))),
    setglob(SEED, getloc('x'))
])

main = [
    setsp(add(imm(-2), sp)),
'next_rect',
    call('xorshift'),
    setloc(1, band(glob(SEED), imm(0xff))),
    call('xorshift'),
    setloc(2, band(glob(SEED), imm(0xff))),
    call('xorshift'),
    write(P_SETCOLOR, getglob(SEED)),
    setloc(-1, getloc(1)),
    setloc(-2, getloc(2)),
    setloc(-3, lit(20)),
    setloc(-4, lit(20)),
    call('fillrect'),
    write(P_FLIP, lit(0)),
    jmp('next_rect'),
    fillrect,
    xorshift
]

data = [
    1
]

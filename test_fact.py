from asm import *

P_PRINT = 0

fact = proc('fact', 'n', 'i', [
    setloc('i', lit(1)),
'next',
    jz('end', getloc('n')),
    setloc('i', mul(loc('i'), loc('n'))),
    setloc('n', sub(loc('n'), imm(1))),
    jmp('next'),
'end',
    setloc('n', getloc('i')),
])

main = [
    setloc(-1, lit(5)),
    call('fact'),
    write(P_PRINT, getloc(-1)),
    setloc(-1, lit(6)),
    call('fact'),
    write(P_PRINT, getloc(-1)),
'end',
    jmp('end'),
    fact
]

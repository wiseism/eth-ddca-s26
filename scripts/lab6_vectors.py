"""Independent Python arithmetic oracle, following Lab5 Table1 precisely."""
from pathlib import Path
import random

root = Path('lab6')
mask = (1 << 32) - 1


def expected(op, a, b):
    if op == 0: return (a + b) & mask
    if op == 2: return (a - b) & mask
    if op == 4: return a & b
    if op == 5: return a | b
    if op == 6: return a ^ b
    if op == 7: return ~(a | b) & mask
    if op == 10: return ((a - b) & mask) >> 31
    raise ValueError(op)


rows = []
for line in (root/'reference/testvectors_hex.txt').read_text().splitlines():
    if not line or line.startswith('//'):
        continue
    compact = line.replace('_', '')
    op, a, b = int(compact[0], 16), int(compact[1:9], 16), int(compact[9:17], 16)
    rows.append((op, a, b))
assert len(rows) == 12
for op in (0, 2, 4, 5, 6, 7, 10):
    for a in (0, 1, 0x7fffffff, 0x80000000, mask):
        for b in (0, 1, 0x7fffffff, 0x80000000, mask):
            rows.append((op, a, b))
rng = random.Random(202606)
rows += [(rng.choice((0, 2, 4, 5, 6, 7, 10)), rng.getrandbits(32), rng.getrandbits(32))
         for _ in range(1000)]
(root/'testvectors_hex.txt').write_text('// Completed original 12 inputs + boundaries + independent random oracle\n'+
    '\n'.join(f'{op:X}_{a:08X}_{b:08X}_{expected(op,a,b):08X}' for op,a,b in rows)+'\n')
print('Prepared', len(rows), 'vectors; SLT follows wrapped subtraction sign, as specified in Table1')

"""Execute the pinned MARS simulator in Actions; never run this lab locally."""
from pathlib import Path
import hashlib
import json
import random
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT / 'lab7'
OUT = LAB / 'results'
OUT.mkdir(exist_ok=True)
JAR = LAB / 'Mars.jar'
REGISTERS = ['t2', 'sp', *[f's{i}' for i in range(8)], 'fp', 'gp', 't8', 't9']
EXIT = '\n    addi $v0, $zero, 10\n    syscall\n'
NOP = '    sll $zero, $zero, 0\n'


def halt_copy(source):
    # Replace only the handout's intentional terminal spin, never its computation.
    changed, count = re.subn(r'(?m)^end:\s*\n\s*j\s+end[^\n]*\n(?:\s*(?:sll|add)\s+\$zero[^\n]*\n)?',
                             'end:' + EXIT, source)
    assert count == 1
    return changed


def run(name, source, delayed=False, regions=()):
    source_file = OUT / f'{name}-{int(delayed)}.asm'
    source_file.write_text(source)
    command = ['java', '-Djava.awt.headless=true', '-jar', str(JAR), 'nc', 'np',
               'ae2', 'se3', 'mc', 'CompactDataAtZero', '1000000', 'dec', *REGISTERS]
    if delayed:
        command.append('db')
    files = []
    for i, (start, words) in enumerate(regions):
        dump = OUT / f'{name}-{int(delayed)}-{i}.hex'
        command += ['dump', f'0x{start:x}-0x{start+4*(words-1):x}', 'HexText', str(dump)]
        files.append(dump)
    command.append(str(source_file))
    result = subprocess.run(command, capture_output=True, text=True, timeout=30)
    log = result.stdout + result.stderr
    (OUT / f'{name}-{int(delayed)}.log').write_text(log)
    assert result.returncode == 0, log
    assert not re.search(r'error|exception|maximum.*steps', log, re.I), log
    registers = {m[1].lstrip('$'): int(m[2]) for m in
                 re.finditer(r'(?m)^\s*(\$?(?:t2|sp|s[0-8]|fp|gp|t8|t9))\s+(-?[0-9]+)\s*$', log)}
    # MARS may print the architectural alias s8 instead of fp.
    if 's8' in registers:
        registers['fp'] = registers['s8']
    assert all(r in registers for r in REGISTERS), log
    memory = []
    for dump, (_, count) in zip(files, regions):
        words = [int(line, 16) for line in dump.read_text().splitlines()]
        assert len(words) == count, (dump, len(words), count)
        memory.append([v if v < 2**31 else v-2**32 for v in words])
    return registers, memory


def opcode_check(source, allowed):
    for line in source.splitlines():
        line = line.split('#', 1)[0].rsplit(':', 1)[-1].strip()
        if line and not line.startswith('.'):
            assert line.split()[0].lower() in allowed, line


simple = (LAB / 'lab7.asm').read_text()
sad = (LAB / 'lab7_sad.asm').read_text()
color = (LAB / 'abs_diff_color.asm').read_text()
allowed = {'add', 'sub', 'slt', 'xor', 'and', 'or', 'nor', 'j', 'addi', 'beq'}
opcode_check(simple, allowed)
rng = random.Random(20261103)
summary = dict(mars_sha256=hashlib.sha256(JAR.read_bytes()).hexdigest(),
               memory_configuration='CompactDataAtZero', instruction_subset_checked=True,
               delayed_branch_modes=[False, True])

# Original empty starter must not accidentally satisfy the same result check.
reference, _ = run('original-sum', halt_copy((LAB / 'reference/lab7.asm').read_text()))
assert reference['t2'] != 45
summary['original_starter_rejected'] = True

ranges = [(1, 1), (5, 10), (1, 32767), (32767, 32767), (0, 0)]
for _ in range(35):
    a = rng.randint(1, 32767)
    ranges.append((a, rng.randint(a, 32767)))
for delayed in (False, True):
    for i, (a, b) in enumerate(ranges):
        program = re.sub(r'addi\s+\$t0,\s*\$zero,\s*5\b', f'addi $t0, $zero, {a}', simple, count=1)
        program = re.sub(r'addi\s+\$t1,\s*\$zero,\s*10\b', f'addi $t1, $zero, {b}', program, count=1)
        registers, _ = run(f'range-{i}', halt_copy(program), delayed)
        assert registers['t2'] == (a+b)*(b-a+1)//2
summary['range_cases'] = len(ranges)*2

left = [5, 16, 7, 1, 1, 13, 2, 8, 10]
right = [4, 15, 8, 0, 2, 12, 3, 7, 11]
images = [(left, right), ([0]*9, [16]*9), ([16]*9, [0]*9), (left, left)]
images += [([rng.randrange(17) for _ in range(9)], [rng.randrange(17) for _ in range(9)]) for _ in range(26)]
for delayed in (False, True):
    for i, (a, b) in enumerate(images):
        initialization = ''.join(f'    addi $t0, $zero, {v}\n    sw $t0, {4*j}($s0)\n' for j, v in enumerate(a+b))
        program = re.sub(r'(?s)# INPUTS_BEGIN.*?# INPUTS_END', '# INPUTS_BEGIN\n'+initialization+'# INPUTS_END', sad)
        registers, memory = run(f'sad-{i}', halt_copy(program), delayed, [(0, 27)])
        differences = [abs(x-y) for x, y in zip(a, b)]
        assert memory[0] == a+b+differences
        assert registers['t2'] == sum(differences)
        assert [registers[r] for r in ['sp', 's0', 's1', 's2', 's3']] == [12280, 0, 9, 9, 72]
summary['sad_cases'] = len(images)*2
summary['official_sad'] = dict(left=left, right=right, differences=[1]*9, t2=9,
                             addresses=dict(left=0, right=36, sad=72), final_sp=12280)

functions = 'abs_diff:\n' + sad.split('abs_diff:\n', 1)[1] + '\n' + color
sentinels = ''.join(f'    addi $s{i}, $zero, {101+i}\n' for i in range(8)) + '    addi $fp, $zero, 109\n'
prologue = '.text\n.globl main\nmain:\n    addi $sp, $zero, 12280\n' + sentinels
prologue += '    addi $sp, $sp, -32\n    addi $t0, $zero, 777\n    sw $t0, 24($sp)\n    addi $t0, $zero, 888\n    sw $t0, 28($sp)\n'
epilogue = '    lw $t8, 24($sp)\n    lw $t9, 28($sp)\n    addi $sp, $sp, 32\n' + EXIT


def abi(registers):
    assert registers['sp'] == 12280
    assert [registers[f's{i}'] for i in range(8)] == list(range(101, 109))
    assert registers['fp'] == 109 and registers['gp'] == 6144
    assert registers['t8'] == 777 and registers['t9'] == 888


def batch(name, inputs, routine, delayed):
    size = len(inputs[0])
    flat = [v for case in inputs for v in case]
    assert len(flat)*4 < 4096
    program = '.data\n.word ' + ','.join(map(str, flat)) + '\n' + prologue
    program += '    sw $zero, 6144($zero)\nbatch_loop:\n    lw $t0, 6144($zero)\n'
    program += f'    slti $t1, $t0, {len(inputs)}\n    beq $t1, $zero, batch_done\n' + NOP
    if size == 2:
        program += '    sll $t1, $t0, 3\n'
    else:
        program += '    sll $t1, $t0, 4\n    sll $t2, $t0, 3\n    add $t1, $t1, $t2\n'
    for i in range(min(size, 4)):
        program += f'    lw $a{i}, {4*i}($t1)\n'
    for i in range(4, size):
        program += f'    lw $t3, {4*i}($t1)\n    sw $t3, {4*i}($sp)\n'
    program += f'    jal {routine}\n' + NOP
    program += '    lw $t0, 6144($zero)\n    sll $t1, $t0, 2\n    addi $t1, $t1, 4096\n    sw $v0, 0($t1)\n'
    program += '    addi $t0, $t0, 1\n    sw $t0, 6144($zero)\n    j batch_loop\n' + NOP
    program += 'batch_done:\n' + epilogue + functions
    registers, memory = run(name, program, delayed, [(0, len(flat)), (4096, len(inputs))])
    abi(registers)
    assert memory[0] == flat
    return memory[1]


pairs = [(a, b) for a in range(17) for b in range(17)]
colors = [(0, 0, 0, 255, 255, 255), (255, 255, 255, 0, 0, 0), (4, 8, 12, 4, 8, 12)]
colors += [tuple(rng.randrange(256) for _ in range(6)) for _ in range(97)]
for delayed in (False, True):
    assert batch('abs-diff', pairs, 'abs_diff', delayed) == [abs(a-b) for a, b in pairs]
    assert batch('color', colors, 'abs_diff_color', delayed) == [sum(abs(c[i]-c[i+3]) for i in range(3)) for c in colors]
summary['scalar_cases'] = len(pairs)*2
summary['color_cases'] = len(colors)*2

vectors = [[], [0], [-7], list(range(9)), [1]*96]
vectors += [[rng.randint(-1000, 1000) for _ in range(rng.randrange(49))] for _ in range(20)]
for delayed in (False, True):
    for i, values in enumerate(vectors):
        data = '.data\n.word ' + ','.join(map(str, values or [0])) + '\n'
        program = data + prologue + '    add $a0, $zero, $zero\n'
        program += f'    addi $a1, $zero, {len(values)}\n    jal recursive_sum\n' + NOP
        program += '    add $t2, $v0, $zero\n' + epilogue + functions
        registers, memory = run(f'recursive-{i}', program, delayed, [(0, max(1, len(values)))])
        abi(registers)
        assert registers['t2'] == sum(values)
        assert memory[0] == (values or [0])
summary['recursive_cases'] = len(vectors)*2
summary['logical_cases'] = sum(summary[k] for k in ['range_cases', 'sad_cases', 'scalar_cases', 'color_cases', 'recursive_cases'])
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
print(json.dumps(summary, indent=2))

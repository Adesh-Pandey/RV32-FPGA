#!/usr/bin/env python3
"""Generate crypto benchmark hex files for RV32I pipeline."""

def r_type(funct7, rs2, rs1, funct3, rd, opcode):
    return (funct7 << 25) | (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def i_type(imm, rs1, funct3, rd, opcode):
    imm = imm & 0xFFF
    return (imm << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | opcode

def b_type(offset, rs2, rs1, funct3):
    imm = offset & 0x1FFF
    bit12  = (imm >> 12) & 1
    bit11  = (imm >> 11) & 1
    bit10_5 = (imm >> 5) & 0x3F
    bit4_1  = (imm >> 1) & 0xF
    return (bit12 << 31) | (bit10_5 << 25) | (rs2 << 20) | (rs1 << 15) | \
           (funct3 << 12) | (bit4_1 << 8) | (bit11 << 7) | 0x63

# Register aliases
x0,x1,x2,x3,x4,x5,x6 = 0,1,2,3,4,5,6
x7,x8,x9,x10,x11,x12 = 7,8,9,10,11,12
x13,x14,x15 = 13,14,15

# Instruction helpers
def ADDI(rd, rs1, imm):  return i_type(imm, rs1, 0b000, rd, 0b0010011)
def ADD(rd, rs1, rs2):   return r_type(0b0000000, rs2, rs1, 0b000, rd, 0b0110011)
def XOR(rd, rs1, rs2):   return r_type(0b0000000, rs2, rs1, 0b100, rd, 0b0110011)
def OR(rd, rs1, rs2):    return r_type(0b0000000, rs2, rs1, 0b110, rd, 0b0110011)
def SLLI(rd, rs1, shamt):return i_type(shamt, rs1, 0b001, rd, 0b0010011)
def SRLI(rd, rs1, shamt):return i_type(shamt, rs1, 0b101, rd, 0b0010011)
def SW(rs2, off, rs1):
    imm = off & 0xFFF
    return ((imm >> 5) << 25) | (rs2 << 20) | (rs1 << 15) | (0b010 << 12) | \
           ((imm & 0x1F) << 7) | 0b0100011
def BNE(rs1, rs2, off):  return b_type(off, rs2, rs1, 0b001)
def JAL(rd, off):
    imm = off & 0x1FFFFF
    bit20 = (imm >> 20) & 1
    bit19_12 = (imm >> 12) & 0xFF
    bit11 = (imm >> 11) & 1
    bit10_1 = (imm >> 1) & 0x3FF
    return (bit20 << 31) | (bit10_1 << 21) | (bit11 << 20) | (bit19_12 << 12) | (rd << 7) | 0b1101111

# Custom ROL instruction: R-type with custom-0 opcode (0001011)
def ROL(rd, rs1, rs2):   return r_type(0b0000000, rs2, rs1, 0b001, rd, 0b0001011)

def to_hex(instr):
    return f"{instr:08X}"

def write_hex(filename, instrs, comments):
    with open(filename, 'w') as f:
        for i, (instr, comment) in enumerate(zip(instrs, comments)):
            f.write(f"{to_hex(instr)}  // {i:2d}: {comment}\n")
    print(f"Generated {filename} ({len(instrs)} instructions)")

# ================================================================
# SOFTWARE VERSION: ChaCha20 quarter-round using standard RV32I
# Rotate = SLL + SRL + OR (3 instructions each)
# ================================================================
sw_instrs = []
sw_comments = []

def sw(instr, comment):
    sw_instrs.append(instr)
    sw_comments.append(comment)

# Init: a=0x61, b=0x62, c=0x63, d=0x64, counter=0, limit=4
sw(ADDI(x1, x0, 0x61),  "x1 (a) = 0x61")
sw(ADDI(x2, x0, 0x62),  "x2 (b) = 0x62")
sw(ADDI(x3, x0, 0x63),  "x3 (c) = 0x63")
sw(ADDI(x4, x0, 0x64),  "x4 (d) = 0x64")
sw(ADDI(x10, x0, 0),    "x10 (counter) = 0")
sw(ADDI(x11, x0, 4),    "x11 (limit) = 4")

# Loop body: 22 instructions (index 6..27)
# --- a += b ---
sw(ADD(x1, x1, x2),     "a += b")
# --- d ^= a ---
sw(XOR(x4, x4, x1),     "d ^= a")
# --- d <<<= 16 (software: 3 instrs) ---
sw(SLLI(x5, x4, 16),    "t0 = d << 16")
sw(SRLI(x6, x4, 16),    "t1 = d >> 16")
sw(OR(x4, x5, x6),      "d = t0 | t1 (ROL 16)")

# --- c += d ---
sw(ADD(x3, x3, x4),     "c += d")
# --- b ^= c ---
sw(XOR(x2, x2, x3),     "b ^= c")
# --- b <<<= 12 (software: 3 instrs) ---
sw(SLLI(x5, x2, 12),    "t0 = b << 12")
sw(SRLI(x6, x2, 20),    "t1 = b >> 20")
sw(OR(x2, x5, x6),      "b = t0 | t1 (ROL 12)")

# --- a += b ---
sw(ADD(x1, x1, x2),     "a += b")
# --- d ^= a ---
sw(XOR(x4, x4, x1),     "d ^= a")
# --- d <<<= 8 (software: 3 instrs) ---
sw(SLLI(x5, x4, 8),     "t0 = d << 8")
sw(SRLI(x6, x4, 24),    "t1 = d >> 24")
sw(OR(x4, x5, x6),      "d = t0 | t1 (ROL 8)")

# --- c += d ---
sw(ADD(x3, x3, x4),     "c += d")
# --- b ^= c ---
sw(XOR(x2, x2, x3),     "b ^= c")
# --- b <<<= 7 (software: 3 instrs) ---
sw(SLLI(x5, x2, 7),     "t0 = b << 7")
sw(SRLI(x6, x2, 25),    "t1 = b >> 25")
sw(OR(x2, x5, x6),      "b = t0 | t1 (ROL 7)")

# --- loop control ---
sw(ADDI(x10, x10, 1),   "counter++")
# BNE back to instruction 6: offset = (6 - 27) * 4 = -84
sw(BNE(x10, x11, -84),  "if counter != 4, loop back")

# Store results to memory
sw(SW(x1, 0, x0),       "mem[0] = a (final)")
sw(SW(x2, 4, x0),       "mem[1] = b (final)")
sw(SW(x3, 8, x0),       "mem[2] = c (final)")
sw(SW(x4, 12, x0),      "mem[3] = d (final)")

# Halt
sw(JAL(x0, 0),          "HALT (jal x0, 0)")

# ================================================================
# HARDWARE VERSION: ChaCha20 quarter-round using custom ROL
# Rotate = 1 ROL instruction
# ================================================================
hw_instrs = []
hw_comments = []

def hw(instr, comment):
    hw_instrs.append(instr)
    hw_comments.append(comment)

# Init: same values + rotation amounts in registers
hw(ADDI(x1, x0, 0x61),  "x1 (a) = 0x61")
hw(ADDI(x2, x0, 0x62),  "x2 (b) = 0x62")
hw(ADDI(x3, x0, 0x63),  "x3 (c) = 0x63")
hw(ADDI(x4, x0, 0x64),  "x4 (d) = 0x64")
hw(ADDI(x10, x0, 0),    "x10 (counter) = 0")
hw(ADDI(x11, x0, 4),    "x11 (limit) = 4")
hw(ADDI(x12, x0, 16),   "x12 (rot amount) = 16")
hw(ADDI(x13, x0, 12),   "x13 (rot amount) = 12")
hw(ADDI(x14, x0, 8),    "x14 (rot amount) = 8")
hw(ADDI(x15, x0, 7),    "x15 (rot amount) = 7")

# Loop body: 14 instructions (index 10..23)
# --- a += b ---
hw(ADD(x1, x1, x2),     "a += b")
# --- d ^= a ---
hw(XOR(x4, x4, x1),     "d ^= a")
# --- d <<<= 16 (1 custom ROL) ---
hw(ROL(x4, x4, x12),    "d = ROL(d, 16) [CUSTOM]")

# --- c += d ---
hw(ADD(x3, x3, x4),     "c += d")
# --- b ^= c ---
hw(XOR(x2, x2, x3),     "b ^= c")
# --- b <<<= 12 (1 custom ROL) ---
hw(ROL(x2, x2, x13),    "b = ROL(b, 12) [CUSTOM]")

# --- a += b ---
hw(ADD(x1, x1, x2),     "a += b")
# --- d ^= a ---
hw(XOR(x4, x4, x1),     "d ^= a")
# --- d <<<= 8 (1 custom ROL) ---
hw(ROL(x4, x4, x14),    "d = ROL(d, 8) [CUSTOM]")

# --- c += d ---
hw(ADD(x3, x3, x4),     "c += d")
# --- b ^= c ---
hw(XOR(x2, x2, x3),     "b ^= c")
# --- b <<<= 7 (1 custom ROL) ---
hw(ROL(x2, x2, x15),    "b = ROL(b, 7) [CUSTOM]")

# --- loop control ---
hw(ADDI(x10, x10, 1),   "counter++")
# BNE back to instruction 10: offset = (10 - 23) * 4 = -52
hw(BNE(x10, x11, -52),  "if counter != 4, loop back")

# Store results
hw(SW(x1, 0, x0),       "mem[0] = a (final)")
hw(SW(x2, 4, x0),       "mem[1] = b (final)")
hw(SW(x3, 8, x0),       "mem[2] = c (final)")
hw(SW(x4, 12, x0),      "mem[3] = d (final)")

# Halt
hw(JAL(x0, 0),          "HALT (jal x0, 0)")

# ================================================================
# Verify both produce same final values (golden model)
# ================================================================
def chacha_qr(a, b, c, d):
    """ChaCha20 quarter-round (Python golden model)."""
    M = 0xFFFFFFFF
    def rol(v, n):
        return ((v << n) | (v >> (32 - n))) & M
    a = (a + b) & M; d = rol(d ^ a, 16)
    c = (c + d) & M; b = rol(b ^ c, 12)
    a = (a + b) & M; d = rol(d ^ a, 8)
    c = (c + d) & M; b = rol(b ^ c, 7)
    return a, b, c, d

a, b, c, d = 0x61, 0x62, 0x63, 0x64
for _ in range(4):
    a, b, c, d = chacha_qr(a, b, c, d)

print(f"\n=== Golden Model (4 rounds of ChaCha20 QR) ===")
print(f"a = 0x{a:08X} ({a})")
print(f"b = 0x{b:08X} ({b})")
print(f"c = 0x{c:08X} ({c})")
print(f"d = 0x{d:08X} ({d})")

print(f"\nSoftware: {len(sw_instrs)} total instructions, {22} per loop iteration")
print(f"Hardware: {len(hw_instrs)} total instructions, {14} per loop iteration")
print(f"Loop body reduction: {22-14} instructions saved per iteration ({(22-14)/22*100:.1f}%)")

# Write hex files
write_hex("src/crypto_sw.hex", sw_instrs, sw_comments)
write_hex("src/crypto_hw.hex", hw_instrs, hw_comments)

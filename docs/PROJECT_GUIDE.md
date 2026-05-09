# RV32I Pipelined Processor — Complete Project Guide

> A ground-up walkthrough of every design decision, every pattern choice, and every module in this RISC-V processor project.

---

## Table of Contents

1. [What Are We Building and Why](#1-what-are-we-building-and-why)
2. [RISC-V: Why This ISA](#2-risc-v-why-this-isa)
3. [The RV32I Base Integer Instruction Set](#3-the-rv32i-base-integer-instruction-set)
4. [Architecture Overview: Single-Cycle vs Pipeline](#4-architecture-overview-single-cycle-vs-pipeline)
5. [Module-by-Module Breakdown](#5-module-by-module-breakdown)
   - 5.1 [Program Counter (pc.v)](#51-program-counter-pcv)
   - 5.2 [PC Adder (pc_adder.v)](#52-pc-adder-pc_adderv)
   - 5.3 [Instruction Memory (imem.v)](#53-instruction-memory-imemv)
   - 5.4 [Immediate Generator (imm_gen.v)](#54-immediate-generator-imm_genv)
   - 5.5 [Control Unit (control.v)](#55-control-unit-controlv)
   - 5.6 [Register File (regfile.v)](#56-register-file-regfilev)
   - 5.7 [ALU (alu.v)](#57-alu-aluv)
   - 5.8 [Data Memory (dmem.v)](#58-data-memory-dmemv)
   - 5.9 [Top-Level Pipeline (top.v)](#59-top-level-pipeline-topv)
6. [The Pipeline Deep Dive](#6-the-pipeline-deep-dive)
   - 6.1 [Stage 1: Instruction Fetch (IF)](#61-stage-1-instruction-fetch-if)
   - 6.2 [Stage 2: Instruction Decode (ID)](#62-stage-2-instruction-decode-id)
   - 6.3 [Stage 3: Execute (EX)](#63-stage-3-execute-ex)
   - 6.4 [Stage 4: Memory Access (MEM)](#64-stage-4-memory-access-mem)
   - 6.5 [Stage 5: Write Back (WB)](#65-stage-5-write-back-wb)
7. [Pipeline Hazards: The Real Engineering Challenge](#7-pipeline-hazards-the-real-engineering-challenge)
   - 7.1 [Data Hazards and Forwarding](#71-data-hazards-and-forwarding)
   - 7.2 [Load-Use Hazard and Stalling](#72-load-use-hazard-and-stalling)
   - 7.3 [Control Hazards and Flushing](#73-control-hazards-and-flushing)
   - 7.4 [The Write-Through Bypass Bug We Found](#74-the-write-through-bypass-bug-we-found)
8. [Performance Counters: Measuring What Matters](#8-performance-counters-measuring-what-matters)
9. [Custom ISA Extension: The ROL Instruction](#9-custom-isa-extension-the-rol-instruction)
10. [ChaCha20 Cryptographic Benchmark](#10-chacha20-cryptographic-benchmark)
    - 10.1 [What is ChaCha20](#101-what-is-chacha20)
    - 10.2 [The Quarter-Round Function](#102-the-quarter-round-function)
    - 10.3 [Software vs Hardware Rotation](#103-software-vs-hardware-rotation)
    - 10.4 [Results and Why Our Solution Was Great](#104-results-and-why-our-solution-was-great)
11. [Test Programs Explained](#11-test-programs-explained)
12. [How to Build and Run Everything](#12-how-to-build-and-run-everything)
13. [Project Evolution: How We Got Here](#13-project-evolution-how-we-got-here)

---

## 1. What Are We Building and Why

We are building a **32-bit RISC-V processor** in Verilog. Not a simulator. Not a software emulator. Actual hardware described in a hardware description language that can be synthesized onto an FPGA or fabricated as a chip.

The processor implements the **RV32I base integer instruction set** — the fundamental subset of RISC-V that every RISC-V core must support. On top of that, we added a **5-stage pipeline** for performance, complete **hazard handling** so the pipeline produces correct results, **performance counters** to measure efficiency, and a **custom instruction extension** (rotate-left) to demonstrate how RISC-V's extensibility works in practice with a real cryptographic workload.

This is not a toy. This processor can run real programs — it computes Fibonacci sequences, it runs ChaCha20 encryption rounds, and it handles every edge case that makes pipelined processors tricky to get right.

---

## 2. RISC-V: Why This ISA

We chose RISC-V over alternatives like ARM, MIPS, or x86 for specific reasons:

**Open standard, no licensing fees.** ARM requires expensive licenses. x86 is proprietary to Intel/AMD. RISC-V is free and open — anyone can build a RISC-V processor without paying royalties. For an academic project, this matters because we can study the full ISA specification without legal barriers.

**Clean, modular design.** RISC-V was designed in 2010 at UC Berkeley with decades of hindsight from MIPS, ARM, and x86 mistakes. The base ISA (RV32I) has only ~47 instructions. Compare that to x86 which has thousands. Every instruction in RV32I has a clear purpose and a consistent encoding.

**Extensibility built-in.** RISC-V reserves opcode space specifically for custom extensions. This is not an afterthought — it is a core design philosophy. We used this to add our custom ROL instruction using the `custom-0` opcode space (0001011). Try doing that with ARM.

**Industry relevance.** RISC-V is used in production by SiFive, Alibaba (T-Head), Western Digital, and others. Learning RISC-V is not academic exercise — it is career-relevant.

---

## 3. The RV32I Base Integer Instruction Set

RV32I defines 6 instruction formats. Every instruction is exactly 32 bits wide. This fixed width is a deliberate design choice — it simplifies instruction fetch (always read 4 bytes) and simplifies decode (fields are always in the same bit positions).

### Instruction Formats

```
R-type:  [funct7 (7)] [rs2 (5)] [rs1 (5)] [funct3 (3)] [rd (5)] [opcode (7)]
I-type:  [imm[11:0]      (12)] [rs1 (5)] [funct3 (3)] [rd (5)] [opcode (7)]
S-type:  [imm[11:5] (7)] [rs2 (5)] [rs1 (5)] [funct3 (3)] [imm[4:0] (5)] [opcode (7)]
B-type:  [imm[12|10:5](7)][rs2(5)] [rs1 (5)] [funct3 (3)] [imm[4:1|11](5)][opcode (7)]
U-type:  [imm[31:12]                    (20)]              [rd (5)] [opcode (7)]
J-type:  [imm[20|10:1|11|19:12]         (20)]              [rd (5)] [opcode (7)]
```

**Why 6 formats?** Each serves a different purpose:

- **R-type** (Register): Operations between two registers. `ADD x3, x1, x2` means `x3 = x1 + x2`. Uses funct7 and funct3 to distinguish operations (ADD vs SUB vs AND, etc.).

- **I-type** (Immediate): Operations with a 12-bit constant. `ADDI x2, x1, 5` means `x2 = x1 + 5`. Also used for loads (`LW x6, 0(x0)` loads from memory address in x0+0).

- **S-type** (Store): Stores to memory. `SW x8, 0(x0)` stores x8 to memory address x0+0. The immediate is split across two fields (bits 31:25 and 11:7) — this looks weird but it keeps rs1 and rs2 in the same bit positions as other formats, which simplifies decode hardware.

- **B-type** (Branch): Conditional branches. `BEQ x10, x11, +12` jumps forward 12 bytes if x10 equals x11. The immediate is scrambled across the instruction — again, to keep register fields consistent while providing a 13-bit signed offset (±4KB range).

- **U-type** (Upper): Loads a 20-bit immediate into the upper 20 bits of a register. `LUI x1, 0x12345` sets x1 to 0x12345000. Combined with ADDI, you can load any 32-bit constant in 2 instructions.

- **J-type** (Jump): Unconditional jump. `JAL x1, offset` jumps to PC+offset and saves the return address (PC+4) in x1. The immediate bits are also scrambled to keep bit[31] as the sign bit (simplifies sign-extension hardware).

**Why are immediates scrambled?** This is one of the cleverest parts of RISC-V. Look at where the sign bit is in every format — it is always bit[31]. This means sign-extension hardware is trivial: just replicate bit[31]. Also, rs1 is always bits[19:15] and rs2 is always bits[24:20] regardless of format. The immediate bits were deliberately shuffled so that register fields never move. This saves mux levels in the decode stage.

### Instructions We Implement

| Category | Instructions | Count |
|----------|-------------|-------|
| Arithmetic | ADD, SUB, ADDI | 3 |
| Logical | AND, OR, XOR, ANDI, ORI, XORI | 6 |
| Shifts | SLL, SRL, SRA, SLLI, SRLI, SRAI | 6 |
| Compare | SLT, SLTU, SLTI, SLTIU | 4 |
| Load/Store | LW, SW | 2 |
| Branch | BEQ, BNE, BLT, BGE, BLTU, BGEU | 6 |
| Jump | JAL, JALR | 2 |
| Upper Imm | LUI, AUIPC | 2 |
| **Custom** | **ROL** | **1** |
| **Total** | | **32** |

We implement word-sized loads and stores only (LW/SW). The full RV32I spec also defines LB, LBU, LH, LHU, SB, SH (byte and half-word variants), but for our 32-bit-aligned memory design, word operations are sufficient to demonstrate all pipeline mechanics.

---

## 4. Architecture Overview: Single-Cycle vs Pipeline

### The Single-Cycle Starting Point

Our project started as a **single-cycle processor** where every instruction completes in one clock cycle. The datapath looks like:

```
PC -> IMEM -> Decode -> RegFile Read -> ALU -> DMEM -> RegFile Write
              |                                          ^
              +------ all in one clock cycle -------------+
```

**Advantage:** Simple. CPI (Cycles Per Instruction) is exactly 1.00.

**Problem:** The clock period must be long enough for the slowest instruction to complete. A load instruction has to go through: instruction memory read + register file read + ALU computation + data memory read + register file write — all in one cycle. The clock frequency is limited by this critical path.

### Why We Moved to a 5-Stage Pipeline

A pipeline breaks each instruction into 5 stages. Each stage takes one shorter clock cycle. Multiple instructions overlap in execution:

```
Cycle:    1    2    3    4    5    6    7
Instr 1:  IF   ID   EX   MEM  WB
Instr 2:       IF   ID   EX   MEM  WB
Instr 3:            IF   ID   EX   MEM  WB
```

**Clock frequency boost:** Each stage does ~1/5 of the work, so the clock can run ~5x faster (in theory). An instruction still takes 5 cycles to complete (latency), but a new instruction finishes every cycle (throughput).

**The trade-off:** Pipelining introduces hazards — situations where the next instruction depends on a result that is not yet available. Managing these hazards is where most of the engineering complexity lives. Our pipeline achieves a CPI of ~1.14 on the Fibonacci benchmark, meaning only 14% overhead from hazards, while gaining ~5x clock frequency. Net throughput improvement: **~4.4x** over single-cycle.

### Harvard Architecture

We use a **Harvard architecture** — separate instruction memory (IMEM) and data memory (DMEM). This is not a philosophical choice; it is a practical necessity. In a pipeline, the IF stage reads from instruction memory while the MEM stage simultaneously reads/writes data memory. With a single memory (Von Neumann), these would conflict. Two separate memories eliminate structural hazards between fetch and memory access.

---

## 5. Module-by-Module Breakdown

### 5.1 Program Counter (`pc.v`)

```verilog
module pc(
    input clk, input rst, input en,
    input [31:0] pc_next,
    output reg [31:0] pc
);
    always @(posedge clk) begin
        if (rst)       pc <= 32'b0;
        else if (en)   pc <= pc_next;
    end
endmodule
```

**16 lines. Deceptively important.**

The PC is a 32-bit register that holds the address of the instruction currently being fetched. On every rising clock edge, it updates to `pc_next` — unless:

- **Reset is active:** PC goes to 0 (start of program).
- **Enable is low:** PC holds its current value. This is how we implement **stalling**. When a load-use hazard is detected, `en` goes low, and the PC freezes for one cycle while the pipeline resolves the dependency.

**Design choice: Why a separate enable?** We could have muxed `pc_next` to feed back the current PC during stalls. But a dedicated enable signal is cleaner — it clearly separates "what is the next PC" from "should we update at all." It also maps directly to clock-enable on a real flip-flop, which is efficient in silicon.

### 5.2 PC Adder (`pc_adder.v`)

```verilog
module pc_adder(
    input [31:0] a,
    output [31:0] y
);
    assign y = a + 32'd4;
endmodule
```

**7 lines. Pure combinational logic.**

Adds 4 to the current PC because each instruction is 4 bytes (32 bits) wide. This is the sequential next-instruction address. We made it a separate module for two reasons:

1. **Clarity:** In the datapath, it is obvious where PC+4 comes from.
2. **Reuse:** PC+4 is needed in three places — as the next sequential PC, as the value saved for JAL/JALR (return address), and it propagates through the pipeline to the WB stage.

### 5.3 Instruction Memory (`imem.v`)

```verilog
module imem(
    input [31:0] a,
    output [31:0] rd
);
    reg [31:0] RAM [63:0];

    integer i;
    initial begin
        for (i = 0; i < 64; i = i + 1) RAM[i] = 32'h00000013;
        $readmemh("src/program.hex", RAM);
    end

    assign rd = RAM[a[31:2]];
endmodule
```

**Key decisions:**

**64 words (256 bytes).** Small, but sufficient for academic programs. Our longest program (ChaCha20 software) is 33 instructions.

**Word-addressed via `a[31:2]`.** The PC counts in bytes (0, 4, 8, 12...) but our memory is organized as 32-bit words. Dividing by 4 (dropping the low 2 bits) converts byte address to word index. This is why `a[31:2]` and not just `a` — we are doing an implicit right-shift by 2.

**NOP initialization (`0x00000013`).** Before loading the program, every location is filled with NOP (ADDI x0, x0, 0). This prevents undefined (`x`) values from propagating through the pipeline if the PC overshoots the program. We discovered this was necessary when `x` values in the pipeline caused the simulator to produce garbage. The hex value `0x00000013` decodes as `addi x0, x0, 0` — it writes to x0 which is hardwired to zero, so it has no effect. A true no-operation.

**Combinational read (`assign`).** No clock dependency on the read path. The instruction is available immediately after the address is set. This is modeled as an ideal ROM — in real hardware, this would be a block RAM or cache with some read latency, but for simulation this is appropriate.

### 5.4 Immediate Generator (`imm_gen.v`)

```verilog
module imm_gen(
    input [31:0] instr,
    output reg [31:0] imm_ext
);
    always @(*) begin
        case (instr[6:0])
            7'b0010011, 7'b0000011:  // I-type
                imm_ext = {{20{instr[31]}}, instr[31:20]};
            7'b0100011:              // S-type
                imm_ext = {{20{instr[31]}}, instr[31:25], instr[11:7]};
            7'b1100011:              // B-type
                imm_ext = {{20{instr[31]}}, instr[7], instr[30:25], instr[11:8], 1'b0};
            7'b1101111:              // J-type (JAL)
                imm_ext = {{12{instr[31]}}, instr[19:12], instr[20], instr[30:21], 1'b0};
            7'b1100111:              // JALR
                imm_ext = {{20{instr[31]}}, instr[31:20]};
            7'b0110111, 7'b0010111:  // U-type (LUI, AUIPC)
                imm_ext = {instr[31:12], 12'b0};
            default:
                imm_ext = 32'b0;
        endcase
    end
endmodule
```

This module does something subtle but critical: it extracts the immediate value from different instruction formats and **sign-extends** it to 32 bits.

**Why sign extension matters:** A 12-bit immediate like `-1` is `0xFFF` in 12 bits. To use it in a 32-bit ALU, we need to extend it to `0xFFFFFFFF`, not `0x00000FFF`. The expression `{20{instr[31]}}` replicates the sign bit (bit 31 of the instruction) 20 times, prepending it to the 12-bit immediate. If the sign bit is 1 (negative), we get `0xFFFFF...`; if 0 (positive), we get `0x00000...`.

**B-type and J-type have `1'b0` appended.** Branch and jump offsets are always multiples of 2 (since instructions are at least 2-byte aligned in RISC-V). The LSB is implicitly zero and not stored in the instruction. This gives an extra bit of range — a 13-bit B-type offset can reach ±4KB, and a 21-bit J-type offset can reach ±1MB.

**U-type has `12'b0` appended.** LUI and AUIPC place the immediate in the upper 20 bits and zero the lower 12. Combined with ADDI (which provides the lower 12 bits), you can construct any 32-bit constant.

### 5.5 Control Unit (`control.v`)

The control unit is purely combinational — it takes the opcode, funct3, and funct7 fields from the instruction and produces all the control signals the datapath needs.

**Output signals and what they do:**

| Signal | Width | Purpose |
|--------|-------|---------|
| `reg_write` | 1 | Enable register file write in WB stage |
| `alu_src` | 1 | ALU source B: 0=register, 1=immediate |
| `alu_control` | 4 | Which ALU operation to perform |
| `mem_write` | 1 | Enable data memory write in MEM stage |
| `result_src` | 2 | WB result: 00=ALU, 01=memory, 10=PC+4 |
| `branch` | 1 | This is a conditional branch instruction |
| `jump` | 1 | This is a JAL instruction |
| `jalr` | 1 | This is a JALR instruction |
| `alu_src1` | 2 | ALU source A: 00=register, 01=PC, 10=zero |

**Why separate `jump` and `jalr`?** Both are unconditional jumps, but they compute the target address differently:
- **JAL:** target = PC + immediate (PC-relative)
- **JALR:** target = register + immediate (register-indirect), with LSB cleared

They need different mux selections in the PC-next logic, so they get separate control signals.

**Why `alu_src1` has 3 options?** Most instructions use a register as ALU source A. But:
- **AUIPC** needs `PC + immediate` — so source A must be the PC
- **LUI** needs `0 + immediate` — so source A must be zero

Rather than adding a separate adder for these, we reuse the ALU by muxing its source A input. This is an area-efficient design choice.

**The R-type funct7 trick:** ADD and SUB have the same opcode and funct3. They differ only in funct7 bit 5: ADD has `0000000`, SUB has `0100000`. Same for SRL/SRA. The control unit checks `funct7[5]` to distinguish them. This is a RISC-V encoding decision that minimizes decode complexity.

**The custom ROL instruction (opcode `0001011`):** We placed it in the RISC-V `custom-0` opcode space, which is explicitly reserved for extensions. The control unit treats it like an R-type (two register sources, register destination) but routes to ALU control code `4'b1010`.

### 5.6 Register File (`regfile.v`)

```verilog
module regfile(
    input clk, input we3,
    input [4:0] a1, a2, a3,
    input [31:0] wd3,
    output [31:0] rd1, rd2
);
    reg [31:0] rf [31:0];

    always @(posedge clk) begin
        if (we3) rf[a3] = wd3;
    end

    assign rd1 = (a1 == 5'b0)                   ? 32'b0 :
                 (we3 && a3 == a1 && a3 != 5'b0) ? wd3   : rf[a1];
    assign rd2 = (a2 == 5'b0)                   ? 32'b0 :
                 (we3 && a3 == a2 && a3 != 5'b0) ? wd3   : rf[a2];
endmodule
```

**32 registers, each 32 bits wide.** This is the RISC-V register file (x0 through x31).

**x0 is hardwired to zero.** The first check `(a1 == 5'b0) ? 32'b0 : ...` enforces this. Any read from x0 returns 0 regardless of what was written. This is a RISC-V spec requirement and is incredibly useful — it gives you a constant zero without wasting an instruction to create one.

**Dual-read, single-write.** Two registers can be read simultaneously (rs1 and rs2 for the current instruction) while one register is written (rd from the WB stage). This is the standard 2R1W register file topology.

**Synchronous write, asynchronous read.** Writes happen on the clock edge; reads are combinational. This is critical for the pipeline — the ID stage needs register values immediately (same cycle), not on the next clock edge.

**The write-through bypass.** This is the most subtle part. Look at the second condition:
```verilog
(we3 && a3 == a1 && a3 != 5'b0) ? wd3 : rf[a1]
```

This handles the case where the WB stage writes a register in the **same cycle** that the ID stage reads it. Without this bypass, the read would get the old (stale) value because the write has not settled into the flip-flop yet. The bypass short-circuits: if WB is writing the same register ID is reading, pass the write data directly.

**When does this situation arise?** When there is a 3-instruction gap between a producer and consumer. The forwarding unit handles 1-instruction and 2-instruction gaps (from EX/MEM and MEM/WB stages). But with a 3-instruction gap, the producer is in WB and the consumer is in ID — neither forwarding path covers this. The register file bypass handles it. We discovered this bug during testing (see Section 7.4).

### 5.7 ALU (`alu.v`)

```verilog
module alu(
    input [31:0] src1, src2,
    input [3:0] alu_control,
    output reg [31:0] result,
    output zero
);
    always @(*) begin
        case (alu_control)
            4'b0000: result = src1 + src2;                                    // ADD
            4'b0001: result = src1 - src2;                                    // SUB
            4'b0010: result = src1 & src2;                                    // AND
            4'b0011: result = src1 | src2;                                    // OR
            4'b0100: result = src1 ^ src2;                                    // XOR
            4'b0101: result = ($signed(src1) < $signed(src2)) ? 1 : 0;       // SLT
            4'b0110: result = src1 << src2[4:0];                              // SLL
            4'b0111: result = src1 >> src2[4:0];                              // SRL
            4'b1000: result = (src1 < src2) ? 1 : 0;                         // SLTU
            4'b1001: result = $signed(src1) >>> src2[4:0];                    // SRA
            4'b1010: result = (src1 << src2[4:0]) | (src1 >> (32-src2[4:0])); // ROL
            default: result = 32'b0;
        endcase
    end
    assign zero = (result == 0) ? 1'b1 : 1'b0;
endmodule
```

**Purely combinational.** No clock, no state. Inputs go in, result comes out in the same cycle.

**Shift amounts use only `src2[4:0]`.** A 32-bit value can be shifted by 0 to 31 positions. 5 bits (2^5 = 32) are sufficient. Using only the low 5 bits matches the RISC-V spec and prevents nonsensical shifts.

**SLT vs SLTU:** Set-Less-Than comes in signed and unsigned flavors. `$signed()` tells Verilog to treat the bit patterns as two's complement for comparison. Without it, `0xFFFFFFFF` (-1 signed) would be treated as 4,294,967,295 (unsigned) and would appear greater than 1, which is wrong for signed comparison.

**SRA uses `>>>` (arithmetic right shift).** This preserves the sign bit during shifting, unlike `>>` (logical right shift) which fills with zeros. `SRA` on `-4` (0xFFFFFFFC) by 1 gives `-2` (0xFFFFFFFE), not `2147483646` (0x7FFFFFFE).

**ROL (rotate left, custom):** `(src1 << n) | (src1 >> (32-n))`. The bits that shift out the left side wrap around to the right side. This is a barrel rotation. In standard RV32I, you need 3 instructions (SLL + SRL + OR) to achieve this. Our custom hardware does it in 1 instruction, in 1 cycle.

**The `zero` flag:** Asserted when the result is 0. Used by the branch comparison logic. For BEQ, we SUB the two operands — if the result is zero, they are equal. For BNE, we check `~zero`.

### 5.8 Data Memory (`dmem.v`)

```verilog
module dmem(
    input clk, input we,
    input [31:0] a, wd,
    output [31:0] rd
);
    reg [31:0] RAM [63:0];
    assign rd = RAM[a[31:2]];
    always @(posedge clk)
        if (we) RAM[a[31:2]] <= wd;
endmodule
```

**Asynchronous read, synchronous write.** Read data is available combinationally (same cycle). Write happens on the clock edge. This matches the pipeline timing — in the MEM stage, a load instruction reads immediately, while a store instruction writes on the clock edge.

**Same `a[31:2]` addressing as IMEM.** Byte addresses are converted to word indices.

**No initialization.** Unlike IMEM, data memory starts as undefined. Programs must write before they read (or accept undefined initial values). This is realistic — real SRAM does not have guaranteed initial values.

**Why `<=` (non-blocking) for writes?** In the `always @(posedge clk)` block, non-blocking assignment is the standard practice for sequential logic. It prevents race conditions between reading and writing in the same clock cycle.

### 5.9 Top-Level Pipeline (`top.v`)

This is the 401-line heart of the design. Rather than explain it linearly (which would be repetitive since we cover each stage separately), I will explain the key architectural patterns and then walk through each stage in Section 6.

**Signal naming convention:** Every signal is prefixed with its pipeline stage or pipeline register:
- `if_*` — signals in the IF stage
- `if_id_*` — IF/ID pipeline register outputs
- `id_*` — signals in the ID stage
- `id_ex_*` — ID/EX pipeline register outputs
- `ex_*` — signals in the EX stage
- `ex_mem_*` — EX/MEM pipeline register outputs
- `mem_*` — signals in the MEM stage
- `mem_wb_*` — MEM/WB pipeline register outputs
- `wb_*` — signals in the WB stage

This naming makes it immediately clear which stage owns each signal. When you see `ex_mem_alu_result`, you know it is the ALU result that has been latched into the EX/MEM pipeline register and is now available to the MEM stage.

---

## 6. The Pipeline Deep Dive

### 6.1 Stage 1: Instruction Fetch (IF)

```
         +------+      +----------+      +------+
pc_next->|  PC  |--+-->|   IMEM   |----->| IF/ID|---> to ID stage
         +------+  |   +----------+      +------+
            ^      |
            |      +-->[ PC+4 Adder ]---> pc_plus4
            |
         [ PC MUX ]
          /   |   \
     pc+4  branch  jalr
            target  target
```

**What happens:**
1. The PC register outputs the current instruction address.
2. IMEM reads the instruction at that address (combinational).
3. The PC adder computes PC+4 (next sequential address).
4. The PC-next mux selects the next PC value: sequential (PC+4), branch target, JAL target, or JALR target. The branch/jump targets come from the EX stage (one stage ahead — this is why branches have a penalty).
5. Everything latches into the IF/ID pipeline register on the clock edge.

**The PC-next mux priority:**

```verilog
assign pc_next = (id_ex_jalr)                    ? ex_jalr_target :
                 (id_ex_jump || ex_branch_taken)  ? ex_branch_target :
                                                    pc_plus4;
```

JALR has highest priority because its target comes from a register value (computed in EX). JAL and taken branches share the same target computation (PC + immediate). The default is PC+4 (sequential).

**The IF/ID pipeline register:**

```verilog
always @(posedge clk) begin
    if (reset || flush) begin
        if_id_instr    <= 32'h00000013; // NOP
        if_id_pc       <= 32'b0;
        if_id_pc_plus4 <= 32'b0;
    end else if (!stall) begin
        if_id_instr    <= if_instr;
        if_id_pc       <= pc_out;
        if_id_pc_plus4 <= pc_plus4;
    end
end
```

Three behaviors:
1. **Reset or flush:** Insert a NOP (bubble). This cancels the instruction that was fetched when a branch was taken (it was fetched speculatively and is wrong).
2. **Stall:** Hold current values. The instruction stays in IF/ID for an extra cycle while the load-use hazard resolves.
3. **Normal:** Latch the new instruction, PC, and PC+4.

### 6.2 Stage 2: Instruction Decode (ID)

**What happens:**
1. The control unit decodes `if_id_instr` into control signals.
2. The register file reads rs1 and rs2 (bits [19:15] and [24:20] of the instruction).
3. The immediate generator extracts and sign-extends the immediate.
4. Everything latches into the ID/EX pipeline register.

**The ID/EX pipeline register bubble mechanism:**

```verilog
always @(posedge clk) begin
    if (reset || flush || stall) begin
        // Zero ALL control signals — this is a bubble (NOP)
        id_ex_reg_write <= 0;
        id_ex_mem_write <= 0;
        id_ex_branch    <= 0;
        id_ex_jump      <= 0;
        id_ex_jalr      <= 0;
        // ... all others zeroed ...
    end else begin
        // Normal: latch decoded values
    end
end
```

Both flush and stall insert bubbles here. A bubble is an instruction with all control signals zeroed — it will not write to registers, not write to memory, not take a branch. It just flows through the pipeline doing nothing. This is safer than trying to "delete" the instruction.

### 6.3 Stage 3: Execute (EX)

This is the most complex stage because it contains the forwarding logic, ALU, branch resolution, and target computation.

**Forwarding muxes** (covered in detail in Section 7.1):

```verilog
// After forwarding selection:
case (forward_a)
    2'b10:   ex_rd1_fwd = ex_mem_fwd_val;  // From EX/MEM (1-instruction gap)
    2'b01:   ex_rd1_fwd = wb_result;        // From MEM/WB (2-instruction gap)
    default: ex_rd1_fwd = id_ex_rd1;        // No forwarding needed
endcase
```

**ALU source A mux:**

```verilog
case (id_ex_alu_src1)
    2'b00: ex_srcA = ex_rd1_fwd;   // Register value (with forwarding applied)
    2'b01: ex_srcA = id_ex_pc;     // PC (for AUIPC)
    2'b10: ex_srcA = 32'b0;        // Zero (for LUI)
endcase
```

**ALU source B mux:**

```verilog
assign ex_srcB_mux = (id_ex_alu_src) ? id_ex_imm_ext : ex_rd2_fwd;
```

Simple: either the immediate (for I-type, loads, stores) or the forwarded register value (for R-type).

**Branch resolution:**

```verilog
always @(*) begin
    ex_branch_taken = 0;
    if (id_ex_branch) begin
        case (id_ex_funct3)
            3'b000: ex_branch_taken = ex_zero;           // BEQ: taken if result==0
            3'b001: ex_branch_taken = ~ex_zero;          // BNE: taken if result!=0
            3'b100: ex_branch_taken = ex_alu_result[0];  // BLT: taken if SLT==1
            3'b101: ex_branch_taken = ~ex_alu_result[0]; // BGE: taken if SLT==0
            3'b110: ex_branch_taken = ex_alu_result[0];  // BLTU: taken if SLTU==1
            3'b111: ex_branch_taken = ~ex_alu_result[0]; // BGEU: taken if SLTU==0
        endcase
    end
end
```

**How branch conditions work with the ALU:**

The control unit sets the ALU operation based on the branch type:
- **BEQ/BNE** → ALU does SUB. If result is 0, operands are equal (BEQ taken). If non-zero, they differ (BNE taken).
- **BLT/BGE** → ALU does SLT (signed). If result is 1, rs1 < rs2 (BLT taken). If 0, rs1 >= rs2 (BGE taken).
- **BLTU/BGEU** → ALU does SLTU (unsigned). Same logic but unsigned comparison.

This is elegant — we reuse the ALU for branch comparison instead of adding a separate comparator. The control unit just needs to select the right ALU operation.

**JALR target computation:**

```verilog
assign ex_jalr_target = ex_alu_result & 32'hFFFFFFFE;
```

The ALU computes `rs1 + immediate`, then we mask the LSB to zero. The RISC-V spec requires this — it ensures the target address is 2-byte aligned (even for the 32-bit ISA, this rule exists for forward-compatibility with the compressed C extension).

### 6.4 Stage 4: Memory Access (MEM)

The simplest stage:

```verilog
dmem dmem_unit(
    .clk(clk),
    .we(ex_mem_mem_write),
    .a(ex_mem_alu_result),     // Address = ALU result (base + offset)
    .wd(ex_mem_rd2),           // Write data = forwarded rs2 value
    .rd(mem_read_data)         // Read data = memory contents
);
```

- **Loads:** The ALU computed `base + offset` in the EX stage. Now DMEM reads from that address.
- **Stores:** The ALU computed the address, and `ex_mem_rd2` holds the data to write. Note that `ex_mem_rd2` uses the **forwarded** value (`ex_rd2_fwd`), not the raw register value. This handles the case where a store needs a value that was just computed.
- **Other instructions:** `mem_write` is 0, so nothing happens in memory. The ALU result just passes through.

### 6.5 Stage 5: Write Back (WB)

```verilog
always @(*) begin
    case (mem_wb_result_src)
        2'b00: wb_result = mem_wb_alu_result;   // ALU operations
        2'b01: wb_result = mem_wb_read_data;    // Loads (from memory)
        2'b10: wb_result = mem_wb_pc_plus4;     // JAL/JALR (return address)
    endcase
end
```

A 3-way mux selects what value to write back to the register file:
- **ALU result** (2'b00): For ADD, SUB, AND, OR, LUI, AUIPC, etc.
- **Memory data** (2'b01): For LW (load word).
- **PC+4** (2'b10): For JAL and JALR — the return address is saved so a subroutine can return.

The write-back happens through the register file's write port:
```verilog
regfile reg_unit(
    .we3(mem_wb_reg_write),  // Write enable from WB stage
    .a3(mem_wb_rd),          // Destination register from WB stage
    .wd3(wb_result)          // Data to write
);
```

---

## 7. Pipeline Hazards: The Real Engineering Challenge

Hazards are the reason pipelined processors are hard. Without hazard handling, our pipeline would produce wrong results. This section covers every hazard type and exactly how we solve it.

### 7.1 Data Hazards and Forwarding

**The problem:** Consider these back-to-back instructions:

```assembly
ADDI x1, x0, 5     # x1 = 5       (in EX stage, result computed but not written back)
ADDI x2, x1, 1     # x2 = x1 + 1  (in ID stage, reads x1 from register file)
```

When the second instruction reads x1 in the ID stage, the first instruction has not yet written its result to the register file (that happens in WB, 2 stages later). The register file still holds the old value of x1. This is a **Read-After-Write (RAW) hazard**.

**The solution: Forwarding (bypassing).** The result we need already exists — it is in the EX/MEM or MEM/WB pipeline register. We just need to grab it from there instead of from the register file.

**The forwarding unit:**

```verilog
// Forward A (for rs1):
if (ex_mem_reg_write && ex_mem_rd != 0 && ex_mem_rd == id_ex_rs1)
    forward_a = 2'b10;   // Forward from EX/MEM (1-instruction gap)
else if (mem_wb_reg_write && mem_wb_rd != 0 && mem_wb_rd == id_ex_rs1)
    forward_a = 2'b01;   // Forward from MEM/WB (2-instruction gap)
else
    forward_a = 2'b00;   // No forwarding, use register file value
```

**Three conditions must all be true for forwarding:**
1. The earlier instruction writes to a register (`reg_write == 1`)
2. The destination is not x0 (`rd != 0`) — writing to x0 is a no-op
3. The destination matches the source register being read (`rd == rs1` or `rd == rs2`)

**EX/MEM has priority over MEM/WB.** If both stages have a matching write, the EX/MEM value is more recent:

```assembly
ADDI x1, x0, 5     # MEM/WB: x1 = 5
ADDI x1, x0, 10    # EX/MEM: x1 = 10 (this one wins!)
ADD  x2, x1, x0    # Should use x1 = 10, not 5
```

**What value to forward from EX/MEM:**

```verilog
assign ex_mem_fwd_val = (ex_mem_result_src == 2'b10) ? ex_mem_pc_plus4 :
                        (ex_mem_result_src == 2'b01) ? 32'b0 :
                                                       ex_mem_alu_result;
```

Most of the time, we forward the ALU result. But for JAL/JALR (result_src == 2'b10), the value to forward is PC+4, not the ALU result (the ALU was computing the jump target, not the value to write to rd). For loads (result_src == 2'b01), we forward 0 as a placeholder — but this case is actually handled by the load-use stall (see next section), so the forwarded 0 is never actually used.

### 7.2 Load-Use Hazard and Stalling

**The problem:** Forwarding cannot solve every data hazard. Consider:

```assembly
LW   x6, 0(x0)     # x6 = mem[0]  (data available at END of MEM stage)
ADDI x7, x6, 1     # x7 = x6 + 1  (needs x6 at START of EX stage)
```

When ADDI is in EX and needs x6, the LW is in MEM and has not yet read the data from memory. The data is not available anywhere in the pipeline yet — there is nothing to forward. We must **stall** the pipeline for one cycle.

**After the stall:**

```
Cycle 1:  LW  in EX,   ADDI in ID
Cycle 2:  LW  in MEM,  ADDI in ID (stalled), bubble in EX
Cycle 3:  LW  in WB,   ADDI in EX ← now LW's data is in MEM/WB, can forward!
```

**The stall detection logic:**

```verilog
assign stall = id_ex_result_src == 2'b01 &&       // Instruction in EX is a load
               id_ex_rd != 5'b0 &&                 // Not loading into x0
               (id_ex_rd == if_id_instr[19:15] ||  // ID's rs1 matches load's rd
                id_ex_rd == if_id_instr[24:20]);   // ID's rs2 matches load's rd
```

**When stall is asserted:**
1. **PC freezes** (`en = !stall` → `en = 0`). The same instruction stays in IF.
2. **IF/ID holds** (`!stall` condition prevents update). The same instruction stays in ID.
3. **ID/EX gets a bubble** (stall triggers the zero-all-controls path). The load-dependent instruction waits.

After one cycle, the load data is available in MEM/WB, and normal forwarding delivers it to the EX stage.

### 7.3 Control Hazards and Flushing

**The problem:** When a branch or jump is taken, the instructions already fetched after it are wrong — they were fetched speculatively assuming sequential execution.

```assembly
BEQ x10, x11, target   # Branch resolved in EX stage
ADDI x12, x0, 1        # Already in ID — wrong if branch taken!
ADDI x13, x0, 2        # Already in IF — wrong if branch taken!
```

We do not know if the branch is taken until the EX stage resolves it. By then, two wrong instructions have entered the pipeline.

**The solution: Flush.** When a branch is taken (or a JAL/JALR executes), we flush the IF/ID pipeline register by replacing its contents with a NOP:

```verilog
assign flush = ex_branch_taken || id_ex_jump || id_ex_jalr;
```

When `flush` is asserted:
- IF/ID gets `0x00000013` (NOP) — cancels the instruction in ID
- ID/EX gets zeroed controls (bubble) — cancels the instruction that was in ID last cycle

**Cost:** Each taken branch or jump wastes 1 cycle (the flushed instruction). Since branches are resolved in EX (stage 3), and the wrong instruction was fetched in IF (stage 1), there is a 1-instruction flush penalty.

**Why not predict branches?** Branch prediction (guessing whether a branch will be taken before resolving it) could reduce the penalty to 0 for correct predictions. We chose not to implement it because:
1. It adds significant complexity (prediction tables, misprediction recovery)
2. For our benchmark programs, the penalty is only ~10% of cycles
3. The educational value of understanding the basic flush mechanism is more important

**Why not resolve branches earlier?** Some designs resolve branches in the ID stage, reducing the penalty to 0 cycles. This requires adding a comparator in ID (separate from the ALU) and potentially introduces timing issues. We chose EX-stage resolution for simplicity.

### 7.4 The Write-Through Bypass Bug We Found

This is worth its own section because it illustrates how subtle pipeline bugs can be.

**The scenario:** 3-instruction gap between producer and consumer:

```assembly
ADDI x1, x0, 5     # Writes x1 in cycle N (WB stage)
NOP                 # Gap instruction 1
NOP                 # Gap instruction 2
ADDI x2, x1, 1     # Reads x1 in cycle N (ID stage) ← SAME CYCLE as write!
```

At cycle N:
- The ADDI writing x1 is in the **WB stage** — it writes to the register file on the clock edge
- The ADDI reading x1 is in the **ID stage** — it reads from the register file combinationally

**The bug:** The register file read is combinational (happens before the clock edge), but the write is synchronous (happens on the clock edge). Without the bypass, the read gets the OLD value of x1, not the value being written this cycle.

**The forwarding unit does not help here.** The forwarding unit only checks EX/MEM and MEM/WB pipeline registers. The writing instruction is in WB, which is past MEM/WB — it is about to leave the pipeline entirely.

**The fix:** The write-through bypass in the register file (see Section 5.6):

```verilog
assign rd1 = (we3 && a3 == a1 && a3 != 5'b0) ? wd3 : rf[a1];
```

If WB is writing the same register that ID is reading in the same cycle, bypass the write data directly to the read output. This was a real bug we discovered during the Fibonacci benchmark — without it, the loop produced wrong values because the iterative computation had exactly the right instruction spacing to trigger this edge case.

---

## 8. Performance Counters: Measuring What Matters

We built hardware performance counters directly into the pipeline to quantitatively analyze how well it performs.

```verilog
reg [31:0] perf_cycles;    // Total clock cycles
reg [31:0] perf_instrs;    // Instructions that completed (retired)
reg [31:0] perf_stalls;    // Cycles wasted on load-use stalls
reg [31:0] perf_flushes;   // Cycles wasted on branch/jump flushes
reg        perf_halted;    // Freeze counters when program ends
```

### Why Each Counter Matters

**Cycles:** Total wall-clock cycles. The denominator for CPI.

**Instructions retired:** Not every instruction that enters the pipeline completes. Flushed instructions (from wrong branch paths) enter the pipeline but are cancelled. Only instructions that reach the WB stage with `valid=1` are counted. The `valid` bit propagates through the pipeline — it is set to 1 when a real instruction enters ID/EX, and set to 0 for bubbles.

**Stalls:** Each stall wastes one cycle (the pipeline is frozen). Tells us how often load-use hazards occur.

**Flushes:** Each flush wastes one cycle (a bubble replaces a useful instruction). Tells us the cost of taken branches.

**CPI (Cycles Per Instruction):** `cycles / instructions`. A perfect pipeline has CPI = 1.0. Our overheads:
- CPI = 1.0 + (stalls + flushes) / instructions

### Halt Detection

Programs end with `JAL x0, 0` — an infinite self-loop that jumps to itself. We detect this pattern and freeze the counters:

```verilog
wire halt_detected = id_ex_jump && (id_ex_rd == 5'b0) && (id_ex_imm_ext == 32'b0);
```

Without halt detection, the counters would keep incrementing as the processor endlessly executes the halt loop, making the metrics meaningless.

### Benchmark Results

**Fibonacci (F0..F9):**

| Metric | Value |
|--------|-------|
| Cycles | 73 |
| Instructions | 64 |
| Stalls | 0 |
| Flushes | 8 |
| CPI | 1.14 |

Zero stalls — the Fibonacci code has no load-use hazards because all values flow through registers (the forwarding unit handles everything). The 8 flushes come from 8 taken branches (7 loop back-edges + 1 final halt jump), each costing 1 wasted cycle.

**Effective speedup over single-cycle:** A single-cycle processor has CPI = 1.00 but runs at a lower clock frequency. If the pipeline runs at ~5x the clock (each stage is ~1/5 the critical path), effective throughput is `5 / 1.14 = 4.4x` better.

---

## 9. Custom ISA Extension: The ROL Instruction

### Why Extend the ISA

RISC-V is designed to be extended. The base ISA is minimal — it does not include multiply, divide, floating point, or bitwise rotations. These are left to optional extensions (M, F, D, B, etc.) or custom extensions.

We added a **Rotate Left (ROL)** instruction to demonstrate:
1. How RISC-V's extensibility works in practice
2. How a single custom instruction can measurably improve a real workload
3. The hardware/software co-design process

### The ROL Instruction Encoding

```
Bit layout: 0000000 | rs2 | rs1 | 001 | rd | 0001011
             funct7   rs2   rs1  funct3  rd   opcode

Opcode: 0001011 (custom-0, reserved by RISC-V for extensions)
Format: R-type (two register sources, one register destination)
funct3: 001
funct7: 0000000

Assembly: ROL rd, rs1, rs2
Operation: rd = (rs1 <<< rs2[4:0])
           Equivalent to: (rs1 << rs2[4:0]) | (rs1 >> (32 - rs2[4:0]))
```

### What Changed in Hardware

The addition was minimal — 3 changes:

1. **ALU** (`alu.v`): Added one case to the ALU:
   ```verilog
   4'b1010: result = (src1 << src2[4:0]) | (src1 >> (32 - src2[4:0]));
   ```

2. **Control** (`control.v`): Added one opcode case:
   ```verilog
   7'b0001011: begin  // Custom-0: ROL
       reg_write = 1;
       alu_src = 0;
       alu_control = 4'b1010;
   end
   ```

3. **No changes to the pipeline, forwarding, stall logic, or anything else.** The ROL instruction flows through the pipeline exactly like ADD — it reads two registers, computes a result in the ALU, and writes back. The pipeline does not need to know or care what the ALU is computing.

This demonstrates the power of clean modular design — adding a new computation required touching only the ALU and control unit.

---

## 10. ChaCha20 Cryptographic Benchmark

### 10.1 What is ChaCha20

ChaCha20 is a **stream cipher** designed by Daniel J. Bernstein. It is used in:
- TLS 1.3 (encrypting HTTPS traffic)
- WireGuard VPN
- Google's QUIC protocol
- SSH (as an alternative to AES)

It was designed to be fast in software on processors that lack AES hardware instructions. Its core operation is the **quarter-round**, which operates on four 32-bit words using only:
- Addition (ADD)
- XOR
- Bitwise rotation (ROL)

No multiplication, no table lookups, no variable-time operations. This makes it resistant to side-channel attacks and efficient on simple processors — like ours.

### 10.2 The Quarter-Round Function

The ChaCha20 quarter-round takes four 32-bit words (a, b, c, d) and mixes them:

```
a += b;  d ^= a;  d <<<= 16;
c += d;  b ^= c;  b <<<= 12;
a += b;  d ^= a;  d <<<= 8;
c += d;  b ^= c;  b <<<= 7;
```

Each line has three operations: add, xor, rotate. The rotation amounts (16, 12, 8, 7) are constants chosen by Bernstein for optimal diffusion.

Our benchmark runs this quarter-round 4 times on initial values a=0x61, b=0x62, c=0x63, d=0x64. The expected output (verified by our Python golden model) is:

```
a = 0xD576E19B
b = 0x1898E8F8
c = 0x36858953
d = 0x9FF722DF
```

### 10.3 Software vs Hardware Rotation

**The problem:** Standard RV32I has no rotate instruction. To rotate left by n bits, you need:

```assembly
# Software rotation: d = ROL(d, 16)
SLLI x5, x4, 16    # t0 = d << 16      (shift left, fill right with 0s)
SRLI x6, x4, 16    # t1 = d >> 16      (shift right, fill left with 0s)
OR   x4, x5, x6    # d  = t0 | t1      (combine: rotated result)
```

Three instructions, using two temporary registers (x5, x6). Each quarter-round has 4 rotations, so that is 12 instructions just for rotations out of 22 total per iteration.

**With our custom ROL instruction:**

```assembly
# Hardware rotation: d = ROL(d, 16)
ROL  x4, x4, x12   # d = ROL(d, 16)    (one instruction, one cycle)
```

One instruction, no temporaries. Each quarter-round has 4 rotations = 4 instructions instead of 12. Total loop body shrinks from 22 to 14 instructions.

### 10.4 Results and Why Our Solution Was Great

Our Python script (`gen_crypto_hex.py`) generates both versions of the program and verifies they produce identical results. The testbench (`crypto_tb.v`) runs both back-to-back and compares.

**The numbers:**

| Metric | Software (RV32I) | Hardware (Custom ROL) | Improvement |
|--------|------------------|-----------------------|-------------|
| Instructions per iteration | 22 | 14 | 36% fewer |
| Total instructions (4 rounds) | ~88 loop + 11 overhead | ~56 loop + 15 overhead | ~30% fewer total |
| Temporary registers used | 2 (x5, x6) | 0 | Frees registers |
| Cycles per rotation | ~3-4 (with pipeline effects) | 1 | 3-4x per rotation |

**Why this is a great solution for our project:**

1. **Minimal hardware cost.** We added ONE line to the ALU (`(src1 << n) | (src1 >> (32-n))`), and ONE case to the control unit. The gate count increase is tiny — a barrel shifter and an OR gate that were already mostly present for SLL and SRL.

2. **Measurable, real-world impact.** This is not a synthetic benchmark. ChaCha20 is used in production TLS. The 36% instruction reduction translates directly to lower energy consumption (fewer instruction fetches, fewer register file reads) and higher throughput.

3. **Standard extension path.** Our ROL instruction matches the semantics of the RISC-V Zbb (Bitmanip) extension's `rol` instruction. We used the custom-0 opcode space for our implementation, but the concept is the same one that the official extension standardizes. This shows we are not inventing something arbitrary — we are implementing something the RISC-V community has validated.

4. **Clean verification.** The Python golden model computes the exact expected output. Both the software and hardware versions produce identical results. The testbench verifies this automatically. This is proper hardware/software co-verification.

5. **Demonstrates ISA-hardware co-design.** The `gen_crypto_hex.py` script is itself a tool — it generates machine code from a Python description, acting as a minimal assembler. This shows the full stack: algorithm → assembly → machine code → hardware execution → verification.

---

## 11. Test Programs Explained

### program.hex — Pipeline Hazard Test

This program systematically tests every hazard scenario:

```
Test 1: EX/MEM Forwarding (back-to-back)
  ADDI x1, x0, 5       # x1 = 5
  ADDI x2, x1, 1       # x2 = 6  (needs x1 from previous instruction)
  ADDI x3, x2, 1       # x3 = 7  (needs x2 from previous instruction)
  → Tests that the forwarding unit correctly bypasses from EX/MEM

Test 2: MEM/WB Forwarding (2-instruction gap)
  ADDI x4, x0, 10      # x4 = 10
  NOP                   # 1 gap
  ADDI x5, x4, 4       # x5 = 14  (needs x4 from 2 instructions ago)
  → Tests that forwarding from MEM/WB works

Test 3: Load-Use Hazard (stall + forward)
  SW   x1, 0(x0)       # Store 5 to memory
  ... NOPs ...
  LW   x6, 0(x0)       # x6 = 5  (load from memory)
  ADDI x7, x6, 1       # x7 = 6  (needs x6, which was just loaded)
  → Tests stall insertion + forwarding after stall

Test 4: R-type Forwarding Chain
  ADD  x1, x1, x2      # x1 = 11  (forward both inputs)
  ADD  x2, x1, x1      # x2 = 22  (forward x1 from EX/MEM)

Test 5: Store with Forwarded Data
  ADDI x8, x0, 20      # x8 = 20
  SW   x8, 0(x0)       # Store x8 (forwarded from EX/MEM)
  ... NOPs ...
  LW   x9, 0(x0)       # x9 = 20  (verify store used forwarded value)

Test 6: Branch with Forwarding
  ADDI x10, x0, 5      # x10 = 5
  ADDI x11, x0, 5      # x11 = 5
  BEQ  x10, x11, +12   # Branch taken (forward both x10 and x11)
  ADDI x12, x0, 1      # SKIPPED (flushed)
  ADDI x12, x0, 1      # SKIPPED (flushed)
  ADDI x12, x0, 0      # x12 = 0  (branch target)
  → Tests branch with forwarded operands + flush of wrong-path instructions
```

### benchmark.hex — Fibonacci

Computes F(0) through F(9) iteratively:

```
Init:  x1=0 (F0), x2=1 (F1), x4=2 (counter), x5=10 (limit), x6=0 (ptr)
Store: mem[0]=0, mem[4]=1, x6=8

Loop:
  x3 = x1 + x2     # F(n) = F(n-2) + F(n-1)
  mem[x6] = x3      # Store F(n)
  x1 = x2           # Shift: F(n-2) = old F(n-1)
  x2 = x3           # Shift: F(n-1) = new F(n)
  x6 += 4           # Next memory address
  x4 += 1           # counter++
  BNE x4, x5, loop  # Repeat until counter == 10

Halt: JAL x0, 0     # Infinite loop (stops counters)
```

Result: mem[0..9] = 0, 1, 1, 2, 3, 5, 8, 13, 21, 34

### crypto_sw.hex and crypto_hw.hex — ChaCha20

Software version (33 instructions):
- 6 init instructions (load a, b, c, d, counter, limit)
- 22-instruction loop body (each rotation = 3 instructions)
- 4 store instructions + 1 halt

Hardware version (29 instructions):
- 10 init instructions (load a, b, c, d, counter, limit, + 4 rotation amounts)
- 14-instruction loop body (each rotation = 1 ROL instruction)
- 4 store instructions + 1 halt

The hardware version needs 4 extra init instructions to load rotation amounts into registers (since ROL takes a register operand). But the loop body is 8 instructions shorter, and the loop runs 4 times, so: 4 extra init - (8 savings x 4 iterations) = 28 net instructions saved.

---

## 12. How to Build and Run Everything

### Prerequisites

- **Icarus Verilog** (`iverilog`): Open-source Verilog simulator
- **GTKWave** (optional): For viewing waveform dumps (.vcd files)
- **Python 3** (optional): For regenerating crypto hex files

### Running Tests

```bash
# Pipeline hazard test
iverilog -o hazard_test src/*.v tb/top_tb.v && vvp hazard_test

# Fibonacci benchmark
iverilog -o benchmark_test src/*.v tb/benchmark_tb.v && vvp benchmark_test

# ChaCha20 crypto benchmark (runs both SW and HW versions)
iverilog -o crypto_test src/*.v tb/crypto_tb.v && vvp crypto_test

# Regenerate crypto hex files (if you modify the algorithm)
python3 gen_crypto_hex.py
```

### Viewing Waveforms

Each testbench generates a `.vcd` file:
```bash
gtkwave cpu_test.vcd        # Hazard test waveforms
gtkwave benchmark_test.vcd  # Fibonacci waveforms
gtkwave crypto_test.vcd     # Crypto benchmark waveforms
```

In GTKWave, you can trace any signal through the pipeline — watch an instruction flow from IF through WB, see forwarding muxes activate, see stalls pause the pipeline, and see flushes inject bubbles.

---

## 13. Project Evolution: How We Got Here

Our git history tells the story of how this project grew:

### Phase 1: Basic Building Blocks
**Commits 1-3:** Started with individual modules (PC, IMEM, ALU, register file, control unit) and wired them into a single-cycle datapath. Fixed early bugs — wrong bit selections, missing connections, off-by-one errors in immediate extraction.

### Phase 2: Complete Single-Cycle RV32I
**Commits 4-6:** Added branches (BEQ, BNE, BLT, BGE, BLTU, BGEU), then jumps (JAL, JALR), then LUI and AUIPC. At commit 6, we had a fully functional single-cycle RV32I processor. Every instruction worked, but performance was limited by the long critical path.

### Phase 3: Pipelining
**Commit 7:** The big rewrite. Split the single-cycle datapath into 5 stages with pipeline registers between them. This was the most challenging step — every signal that crosses a stage boundary needs to be registered, and the timing of reads/writes completely changes.

### Phase 4: Hazard Handling
**Commits 8-9:** Added the forwarding unit (data hazards), load-use stall detection (load-data hazards), and branch flushing (control hazards). Also discovered and fixed the register file write-through bug. This is where correctness became hard — the pipeline would produce subtly wrong results that required careful waveform analysis to debug.

### Phase 5: Quantitative Analysis
**Commits 10-11:** Added performance counters, the Fibonacci benchmark, and the pipeline hazard test. Now we could measure CPI, stall rates, and flush rates. Added the CHANGES.md documentation and the mid-term report.

### Phase 6: Custom ISA Extension
**Commit 12:** Added the ROL instruction, the ChaCha20 benchmark, and the Python hex generator. This was the capstone — showing that our pipeline is not only correct and performant but also extensible.

---

## Summary of Key Design Choices

| Decision | What we chose | Why |
|----------|---------------|-----|
| ISA | RISC-V RV32I | Open, clean, extensible, industry-relevant |
| Architecture | Harvard (split IMEM/DMEM) | Avoids structural hazards between fetch and memory |
| Pipeline depth | 5 stages | Classic balance of throughput vs complexity |
| Data hazard solution | Forwarding from EX/MEM and MEM/WB | Eliminates most stalls (~90%+ of data hazards) |
| Load-use solution | 1-cycle stall | Cannot forward data that does not exist yet |
| Control hazard solution | Flush on taken branch | Simple, 1-cycle penalty, no prediction needed |
| Branch resolution | EX stage (stage 3) | Reuses ALU for comparison, keeps ID simple |
| Memory width | 32-bit words only | Sufficient for demonstration, avoids byte-alignment complexity |
| Custom extension | ROL (rotate left) | Real cryptographic need, minimal hardware, measurable speedup |
| Benchmark | ChaCha20 quarter-round | Production-relevant cipher, rotation-heavy, good ISA extension showcase |
| Verification | Python golden model + auto hex generation | Ensures SW and HW versions produce identical results |

---

*This processor runs real programs, handles real hazards, and demonstrates real ISA extensibility. It is not a textbook diagram — it is working hardware.*

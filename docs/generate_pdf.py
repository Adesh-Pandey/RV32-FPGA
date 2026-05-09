#!/usr/bin/env python3
"""Generate a well-formatted PDF guide for the RV32I pipeline project."""

from fpdf import FPDF, XPos, YPos
import os

# ── Colours ──────────────────────────────────────────────────────────
DARK   = (30, 30, 30)
ACCENT = (0, 90, 156)
GREY   = (100, 100, 100)
LIGHT_BG = (245, 245, 250)
CODE_BG  = (240, 240, 245)
WHITE  = (255, 255, 255)
TABLE_HEAD = (0, 90, 156)
TABLE_ALT  = (235, 242, 250)

FONT_DIR = "/usr/share/fonts/noto"

class PDF(FPDF):
    chapter_title = ""

    def __init__(self):
        super().__init__()
        # Register Unicode fonts
        self.add_font("NotoSans", "", f"{FONT_DIR}/NotoSans-Regular.ttf")
        self.add_font("NotoSans", "B", f"{FONT_DIR}/NotoSans-Bold.ttf")
        self.add_font("NotoSans", "I", f"{FONT_DIR}/NotoSans-Italic.ttf")
        self.add_font("NotoSans", "BI", f"{FONT_DIR}/NotoSans-BoldItalic.ttf")
        self.add_font("NotoMono", "", f"{FONT_DIR}/NotoSansMono-Regular.ttf")
        # Use Adwaita for italic mono fallback
        self.add_font("AdwMono", "", "/usr/share/fonts/Adwaita/AdwaitaMono-Regular.ttf")
        self.add_font("AdwMono", "B", "/usr/share/fonts/Adwaita/AdwaitaMono-Bold.ttf")

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("NotoSans", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 8, "RV32I Pipelined Processor -- Complete Project Guide", align="L")
        self.cell(0, 8, self.chapter_title, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*ACCENT)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font("NotoSans", "I", 8)
        self.set_text_color(*GREY)
        self.cell(0, 10, f"Page {self.page_no() - 1}", align="C")

    # ── Helpers ──────────────────────────────────────────────────────
    def cover_page(self):
        self.add_page()
        self.ln(50)
        self.set_font("NotoSans", "B", 36)
        self.set_text_color(*ACCENT)
        self.cell(0, 16, "RV32I Pipelined Processor", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(4)
        self.set_font("NotoSans", "", 18)
        self.set_text_color(*DARK)
        self.cell(0, 12, "Complete Project Guide", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(12)
        self.set_draw_color(*ACCENT)
        self.line(60, self.get_y(), 150, self.get_y())
        self.ln(12)
        self.set_font("NotoSans", "", 12)
        self.set_text_color(*GREY)
        self.cell(0, 8, "A ground-up walkthrough of every design decision,", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 8, "every pattern choice, and every module.", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(30)
        self.set_font("NotoSans", "", 11)
        self.set_text_color(*DARK)
        self.cell(0, 8, "Aayush Gelal  |  Adesh Pandey  |  Bishesh Paudel", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.cell(0, 8, "Tribhuvan University --Electronics Minor Project 2026", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    def section(self, num, title):
        self.chapter_title = f"{num}. {title}"
        self.add_page()
        self.set_font("NotoSans", "B", 22)
        self.set_text_color(*ACCENT)
        self.cell(0, 14, f"{num}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("NotoSans", "B", 18)
        self.set_text_color(*DARK)
        self.cell(0, 12, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(*ACCENT)
        self.line(10, self.get_y() + 1, 200, self.get_y() + 1)
        self.ln(8)

    def sub(self, title):
        self.ln(4)
        self.set_font("NotoSans", "B", 13)
        self.set_text_color(*ACCENT)
        self.cell(0, 9, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(2)

    def sub2(self, title):
        self.ln(2)
        self.set_font("NotoSans", "B", 11)
        self.set_text_color(60, 60, 60)
        self.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(1)

    def body(self, text):
        self.set_font("NotoSans", "", 10)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bold_body(self, text):
        self.set_font("NotoSans", "B", 10)
        self.set_text_color(*DARK)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text):
        self.set_font("NotoSans", "", 10)
        self.set_text_color(*DARK)
        x = self.get_x()
        self.cell(6, 5.5, "- ")
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def code(self, text):
        self.ln(2)
        self.set_fill_color(*CODE_BG)
        self.set_font("NotoMono", "", 8.5)
        self.set_text_color(40, 40, 40)
        lines = text.strip().split("\n")
        # calculate height
        for line in lines:
            self.cell(0, 4.8, "  " + line, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.ln(3)

    def make_table(self, headers, rows, col_widths=None):
        self.ln(2)
        if col_widths is None:
            w = 190 / len(headers)
            col_widths = [w] * len(headers)
        # header
        self.set_font("NotoSans", "B", 9)
        self.set_fill_color(*TABLE_HEAD)
        self.set_text_color(*WHITE)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, " " + h, border=1, fill=True)
        self.ln()
        # rows
        self.set_font("NotoSans", "", 9)
        self.set_text_color(*DARK)
        for ri, row in enumerate(rows):
            if ri % 2 == 1:
                self.set_fill_color(*TABLE_ALT)
                fill = True
            else:
                self.set_fill_color(*WHITE)
                fill = True
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6.5, " " + str(cell), border=1, fill=fill)
            self.ln()
        self.ln(3)


def build():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ━━ Cover ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.cover_page()

    # ━━ Table of Contents ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.add_page()
    pdf.set_font("NotoSans", "B", 20)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 14, "Table of Contents", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)
    toc = [
        ("1", "What Are We Building and Why"),
        ("2", "RISC-V: Why This ISA"),
        ("3", "The RV32I Base Integer Instruction Set"),
        ("4", "Architecture: Single-Cycle vs Pipeline"),
        ("5", "Module-by-Module Breakdown"),
        ("6", "The Pipeline Deep Dive"),
        ("7", "Pipeline Hazards: The Real Engineering Challenge"),
        ("8", "Performance Counters: Measuring What Matters"),
        ("9", "Custom ISA Extension: The ROL Instruction"),
        ("10", "ChaCha20 Cryptographic Benchmark"),
        ("11", "Test Programs Explained"),
        ("12", "How to Build and Run Everything"),
        ("13", "Project Evolution"),
    ]
    for num, title in toc:
        pdf.set_font("NotoSans", "", 11)
        pdf.set_text_color(*DARK)
        pdf.cell(12, 8, num + ".")
        pdf.set_text_color(*ACCENT)
        pdf.cell(0, 8, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(6)

    # ━━ Section 1 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.section("1", "What Are We Building and Why")
    pdf.body(
        "We are building a 32-bit RISC-V processor in Verilog. Not a simulator. Not a software "
        "emulator. Actual hardware described in a hardware description language that can be "
        "synthesized onto an FPGA or fabricated as a chip."
    )
    pdf.body(
        "The processor implements the RV32I base integer instruction set --the fundamental "
        "subset of RISC-V that every RISC-V core must support. On top of that, we added a "
        "5-stage pipeline for performance, complete hazard handling so the pipeline produces "
        "correct results, performance counters to measure efficiency, and a custom instruction "
        "extension (rotate-left) to demonstrate how RISC-V's extensibility works in practice "
        "with a real cryptographic workload (ChaCha20)."
    )
    pdf.body(
        "This is not a toy. This processor can run real programs --it computes Fibonacci "
        "sequences, it runs ChaCha20 encryption rounds, and it handles every edge case that "
        "makes pipelined processors tricky to get right."
    )

    pdf.sub("Project File Structure")
    pdf.code(
        "RV32/\n"
        "  src/\n"
        "    top.v           # Top-level: 5-stage pipeline integration (401 lines)\n"
        "    control.v       # Control unit / instruction decoder (140 lines)\n"
        "    alu.v           # Arithmetic Logic Unit (28 lines)\n"
        "    regfile.v       # 32x32-bit register file (25 lines)\n"
        "    pc.v            # Program counter with enable (16 lines)\n"
        "    pc_adder.v      # PC+4 adder (7 lines)\n"
        "    imem.v          # Instruction memory, 64 words (15 lines)\n"
        "    dmem.v          # Data memory, 64 words (19 lines)\n"
        "    imm_gen.v       # Immediate value extractor (33 lines)\n"
        "    program.hex     # Hazard test program\n"
        "    benchmark.hex   # Fibonacci benchmark\n"
        "    crypto_sw.hex   # ChaCha20 (software rotations)\n"
        "    crypto_hw.hex   # ChaCha20 (hardware ROL instruction)\n"
        "  tb/\n"
        "    top_tb.v        # Pipeline hazard testbench\n"
        "    benchmark_tb.v  # Fibonacci benchmark testbench\n"
        "    crypto_tb.v     # ChaCha20 SW vs HW comparison testbench\n"
        "  gen_crypto_hex.py # Python assembler for crypto benchmarks\n"
        "  docs/\n"
        "    RISCV_CARD.pdf  # RISC-V instruction reference card"
    )

    # ━━ Section 2 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.section("2", "RISC-V: Why This ISA")
    pdf.body(
        "We chose RISC-V over alternatives like ARM, MIPS, or x86 for these specific reasons:"
    )

    pdf.sub2("Open standard, no licensing fees")
    pdf.body(
        "ARM requires expensive licenses. x86 is proprietary to Intel/AMD. RISC-V is free and "
        "open --anyone can build a RISC-V processor without paying royalties. For an academic "
        "project, this means we can study the full ISA specification without legal barriers."
    )

    pdf.sub2("Clean, modular design")
    pdf.body(
        "RISC-V was designed in 2010 at UC Berkeley with decades of hindsight from MIPS, ARM, "
        "and x86 mistakes. The base ISA (RV32I) has only ~47 instructions. Compare that to x86 "
        "which has thousands. Every instruction in RV32I has a clear purpose and a consistent encoding."
    )

    pdf.sub2("Extensibility built-in")
    pdf.body(
        "RISC-V reserves opcode space specifically for custom extensions. This is not an "
        "afterthought --it is a core design philosophy. We used this to add our custom ROL "
        "instruction using the custom-0 opcode space (0001011). Try doing that with ARM."
    )

    pdf.sub2("Industry relevance")
    pdf.body(
        "RISC-V is used in production by SiFive, Alibaba (T-Head), Western Digital, and others. "
        "Learning RISC-V is not an academic exercise --it is career-relevant."
    )

    # ━━ Section 3 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.section("3", "The RV32I Base Integer Instruction Set")
    pdf.body(
        "RV32I defines 6 instruction formats. Every instruction is exactly 32 bits wide. This "
        "fixed width simplifies instruction fetch (always read 4 bytes) and simplifies decode "
        "(fields are always in the same bit positions)."
    )

    pdf.sub("The 6 Instruction Formats")
    pdf.code(
        "R-type:  [funct7(7)] [rs2(5)] [rs1(5)] [funct3(3)] [rd(5)] [opcode(7)]\n"
        "I-type:  [imm[11:0]    (12)]  [rs1(5)] [funct3(3)] [rd(5)] [opcode(7)]\n"
        "S-type:  [imm[11:5](7)][rs2(5)][rs1(5)] [funct3(3)] [imm[4:0](5)][opcode(7)]\n"
        "B-type:  [imm bits (7)][rs2(5)][rs1(5)] [funct3(3)] [imm bits(5)] [opcode(7)]\n"
        "U-type:  [imm[31:12]              (20)]              [rd(5)] [opcode(7)]\n"
        "J-type:  [imm bits                (20)]              [rd(5)] [opcode(7)]"
    )

    pdf.sub2("R-type (Register)")
    pdf.body(
        "Operations between two registers. ADD x3, x1, x2 means x3 = x1 + x2. Uses funct7 and "
        "funct3 to distinguish operations (ADD vs SUB vs AND, etc.)."
    )
    pdf.sub2("I-type (Immediate)")
    pdf.body(
        "Operations with a 12-bit constant. ADDI x2, x1, 5 means x2 = x1 + 5. Also used for "
        "loads: LW x6, 0(x0) loads from memory address x0+0."
    )
    pdf.sub2("S-type (Store)")
    pdf.body(
        "Stores to memory. SW x8, 0(x0) stores x8 to memory at address x0+0. The immediate "
        "is split across two fields (bits 31:25 and 11:7) --this keeps rs1 and rs2 in the same "
        "bit positions as other formats, simplifying decode hardware."
    )
    pdf.sub2("B-type (Branch)")
    pdf.body(
        "Conditional branches. BEQ x10, x11, +12 jumps forward 12 bytes if x10 equals x11. "
        "The immediate provides a 13-bit signed offset (the LSB is always 0 since instructions "
        "are 2-byte aligned, giving +/-4KB range)."
    )
    pdf.sub2("U-type (Upper Immediate)")
    pdf.body(
        "Loads a 20-bit immediate into the upper 20 bits. LUI x1, 0x12345 sets x1 to 0x12345000. "
        "Combined with ADDI, you can load any 32-bit constant in 2 instructions."
    )
    pdf.sub2("J-type (Jump)")
    pdf.body(
        "Unconditional jump. JAL x1, offset jumps to PC+offset and saves the return address "
        "(PC+4) in x1. The 21-bit offset gives +/-1MB range."
    )

    pdf.sub("Why Are Immediates Scrambled?")
    pdf.body(
        "This is one of the cleverest parts of RISC-V. The sign bit is always bit[31] in every "
        "format, so sign-extension hardware is trivial (just replicate bit[31]). Also, rs1 is "
        "always bits[19:15] and rs2 is always bits[24:20] regardless of format. The immediate "
        "bits were deliberately shuffled so that register fields never move. This saves mux "
        "levels in the decode stage."
    )

    pdf.sub("Instructions We Implement")
    pdf.make_table(
        ["Category", "Instructions", "Count"],
        [
            ["Arithmetic", "ADD, SUB, ADDI", "3"],
            ["Logical", "AND, OR, XOR, ANDI, ORI, XORI", "6"],
            ["Shifts", "SLL, SRL, SRA, SLLI, SRLI, SRAI", "6"],
            ["Compare", "SLT, SLTU, SLTI, SLTIU", "4"],
            ["Load/Store", "LW, SW", "2"],
            ["Branch", "BEQ, BNE, BLT, BGE, BLTU, BGEU", "6"],
            ["Jump", "JAL, JALR", "2"],
            ["Upper Imm", "LUI, AUIPC", "2"],
            ["Custom", "ROL (rotate left)", "1"],
            ["Total", "", "32"],
        ],
        [40, 110, 40],
    )

    # ━━ Section 4 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.section("4", "Architecture: Single-Cycle vs Pipeline")

    pdf.sub("The Single-Cycle Starting Point")
    pdf.body(
        "Our project started as a single-cycle processor where every instruction completes in "
        "one clock cycle:"
    )
    pdf.code(
        "PC -> IMEM -> Decode -> RegFile Read -> ALU -> DMEM -> RegFile Write\n"
        "         all in one clock cycle"
    )
    pdf.body(
        "Advantage: Simple. CPI (Cycles Per Instruction) is exactly 1.00.\n\n"
        "Problem: The clock period must be long enough for the slowest instruction (a load: "
        "IMEM read + register read + ALU + DMEM read + register write). The clock frequency "
        "is limited by this critical path."
    )

    pdf.sub("Why We Moved to a 5-Stage Pipeline")
    pdf.body(
        "A pipeline breaks each instruction into 5 stages. Each stage takes one shorter clock "
        "cycle. Multiple instructions overlap in execution:"
    )
    pdf.code(
        "Cycle:    1    2    3    4    5    6    7\n"
        "Instr 1:  IF   ID   EX   MEM  WB\n"
        "Instr 2:       IF   ID   EX   MEM  WB\n"
        "Instr 3:            IF   ID   EX   MEM  WB"
    )
    pdf.body(
        "Clock frequency boost: Each stage does ~1/5 of the work, so the clock can run ~5x "
        "faster. An instruction still takes 5 cycles to complete (latency), but a new "
        "instruction finishes every cycle (throughput)."
    )
    pdf.body(
        "The trade-off: Pipelining introduces hazards --situations where the next instruction "
        "depends on a result that is not yet available. Our pipeline achieves CPI of ~1.14 on "
        "Fibonacci, meaning only 14% overhead from hazards, while gaining ~5x clock frequency. "
        "Net throughput improvement: ~4.4x over single-cycle."
    )

    pdf.sub("Harvard Architecture")
    pdf.body(
        "We use a Harvard architecture --separate instruction memory (IMEM) and data memory "
        "(DMEM). In a pipeline, the IF stage reads from instruction memory while the MEM stage "
        "simultaneously reads/writes data memory. With a single memory (Von Neumann), these "
        "would conflict. Two separate memories eliminate structural hazards."
    )

    # ━━ Section 5 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.section("5", "Module-by-Module Breakdown")

    # 5.1 PC
    pdf.sub("5.1  Program Counter (pc.v)")
    pdf.code(
        "module pc(\n"
        "    input clk, input rst, input en,\n"
        "    input [31:0] pc_next,\n"
        "    output reg [31:0] pc\n"
        ");\n"
        "    always @(posedge clk) begin\n"
        "        if (rst)       pc <= 32'b0;\n"
        "        else if (en)   pc <= pc_next;\n"
        "    end\n"
        "endmodule"
    )
    pdf.body(
        "The PC is a 32-bit register holding the address of the instruction being fetched. "
        "On every rising clock edge, it updates to pc_next --unless reset is active (PC goes "
        "to 0) or enable is low (PC holds its value). The enable signal implements stalling: "
        "when a load-use hazard is detected, en goes low, and the PC freezes for one cycle."
    )
    pdf.body(
        "Design choice: A dedicated enable signal is cleaner than muxing pc_next to feed back "
        "the current PC. It clearly separates 'what is the next PC' from 'should we update at "
        "all' and maps directly to clock-enable on a real flip-flop."
    )

    # 5.2 PC Adder
    pdf.sub("5.2  PC Adder (pc_adder.v)")
    pdf.code(
        "module pc_adder(\n"
        "    input [31:0] a,\n"
        "    output [31:0] y\n"
        ");\n"
        "    assign y = a + 32'd4;\n"
        "endmodule"
    )
    pdf.body(
        "Adds 4 to the current PC because each instruction is 4 bytes wide. PC+4 is needed "
        "in three places: as the next sequential PC, as the return address for JAL/JALR, and "
        "it propagates through the pipeline to the WB stage."
    )

    # 5.3 IMEM
    pdf.sub("5.3  Instruction Memory (imem.v)")
    pdf.code(
        "module imem(\n"
        "    input [31:0] a,\n"
        "    output [31:0] rd\n"
        ");\n"
        "    reg [31:0] RAM [63:0];  // 64 words = 256 bytes\n"
        "    integer i;\n"
        "    initial begin\n"
        "        for (i = 0; i < 64; i = i + 1)\n"
        "            RAM[i] = 32'h00000013;  // Fill with NOPs\n"
        "        $readmemh(\"src/program.hex\", RAM);\n"
        "    end\n"
        "    assign rd = RAM[a[31:2]];  // Word-addressed\n"
        "endmodule"
    )
    pdf.body(
        "64 words (256 bytes). Word-addressed via a[31:2] --the PC counts in bytes (0, 4, 8...) "
        "but memory is organized as 32-bit words. Dropping the low 2 bits converts byte address "
        "to word index (implicit divide by 4)."
    )
    pdf.body(
        "NOP initialization (0x00000013): Every location is filled with NOP (ADDI x0, x0, 0) "
        "before loading the program. This prevents undefined 'x' values from propagating through "
        "the pipeline if the PC overshoots the program. The hex value decodes as 'add 0 to x0 "
        "and store in x0' --a true no-operation."
    )

    # 5.4 Immediate Generator
    pdf.sub("5.4  Immediate Generator (imm_gen.v)")
    pdf.code(
        "always @(*) begin\n"
        "    case (instr[6:0])\n"
        "        7'b0010011, 7'b0000011:  // I-type\n"
        "            imm_ext = {{20{instr[31]}}, instr[31:20]};\n"
        "        7'b0100011:              // S-type\n"
        "            imm_ext = {{20{instr[31]}}, instr[31:25], instr[11:7]};\n"
        "        7'b1100011:              // B-type\n"
        "            imm_ext = {{20{instr[31]}}, instr[7],\n"
        "                       instr[30:25], instr[11:8], 1'b0};\n"
        "        7'b1101111:              // J-type (JAL)\n"
        "            imm_ext = {{12{instr[31]}}, instr[19:12],\n"
        "                       instr[20], instr[30:21], 1'b0};\n"
        "        7'b0110111, 7'b0010111:  // U-type (LUI, AUIPC)\n"
        "            imm_ext = {instr[31:12], 12'b0};\n"
        "    endcase\n"
        "end"
    )
    pdf.body(
        "Extracts the immediate from different formats and sign-extends to 32 bits. "
        "The expression {20{instr[31]}} replicates the sign bit 20 times. If bit 31 is 1 "
        "(negative), we get 0xFFFFF...; if 0 (positive), we get 0x00000..."
    )
    pdf.body(
        "B-type and J-type append 1'b0 at the LSB --branch/jump offsets are always multiples "
        "of 2 (instructions are at least 2-byte aligned). This implicit zero gives an extra "
        "bit of range without costing a bit in the instruction encoding."
    )
    pdf.body(
        "U-type appends 12'b0 --LUI/AUIPC place the immediate in the upper 20 bits. Combined "
        "with ADDI (lower 12 bits), any 32-bit constant can be constructed in 2 instructions."
    )

    # 5.5 Control Unit
    pdf.sub("5.5  Control Unit (control.v)")
    pdf.body(
        "Purely combinational decoder: takes opcode, funct3, and funct7 from the instruction "
        "and produces all control signals for the datapath."
    )
    pdf.make_table(
        ["Signal", "Width", "Purpose"],
        [
            ["reg_write", "1", "Enable register file write in WB"],
            ["alu_src", "1", "ALU src B: 0=register, 1=immediate"],
            ["alu_control", "4", "Which ALU operation to perform"],
            ["mem_write", "1", "Enable data memory write in MEM"],
            ["result_src", "2", "WB source: 00=ALU, 01=mem, 10=PC+4"],
            ["branch", "1", "Conditional branch instruction"],
            ["jump", "1", "JAL instruction"],
            ["jalr", "1", "JALR instruction"],
            ["alu_src1", "2", "ALU src A: 00=reg, 01=PC, 10=zero"],
        ],
        [30, 15, 145],
    )
    pdf.body(
        "Why separate jump and jalr? Both are unconditional jumps, but they compute the target "
        "differently: JAL uses PC + immediate (PC-relative), JALR uses register + immediate "
        "(register-indirect) with LSB cleared. They need different mux selections."
    )
    pdf.body(
        "Why alu_src1 has 3 options? Most instructions use a register for ALU source A. But "
        "AUIPC needs PC + immediate (source A = PC), and LUI needs 0 + immediate (source A = 0). "
        "Rather than adding separate adders, we reuse the ALU by muxing its input. Area-efficient."
    )
    pdf.body(
        "The R-type funct7 trick: ADD and SUB share the same opcode and funct3. They differ "
        "only in funct7 bit 5 (ADD=0, SUB=1). Same for SRL/SRA. This RISC-V encoding decision "
        "minimizes decode complexity --one bit distinguishes the operation."
    )

    # 5.6 Register File
    pdf.sub("5.6  Register File (regfile.v)")
    pdf.code(
        "module regfile(\n"
        "    input clk, input we3,\n"
        "    input [4:0] a1, a2, a3,\n"
        "    input [31:0] wd3,\n"
        "    output [31:0] rd1, rd2\n"
        ");\n"
        "    reg [31:0] rf [31:0];\n"
        "    always @(posedge clk) begin\n"
        "        if (we3) rf[a3] = wd3;\n"
        "    end\n"
        "    assign rd1 = (a1 == 5'b0)                    ? 32'b0 :\n"
        "                 (we3 && a3 == a1 && a3 != 5'b0) ? wd3   : rf[a1];\n"
        "    assign rd2 = (a2 == 5'b0)                    ? 32'b0 :\n"
        "                 (we3 && a3 == a2 && a3 != 5'b0) ? wd3   : rf[a2];\n"
        "endmodule"
    )
    pdf.body(
        "32 registers x 32 bits. x0 is hardwired to zero (first check). Dual-read, single-write. "
        "Synchronous write on clock edge, asynchronous (combinational) read."
    )
    pdf.body(
        "The write-through bypass (second condition in each assign) is critical: when WB writes "
        "a register in the same cycle that ID reads it, the bypass short-circuits the write data "
        "to the read output. Without this, a 3-instruction gap between producer and consumer "
        "would read stale data. The forwarding unit only covers 1 and 2-instruction gaps. "
        "This bypass was a real bug we discovered and fixed (see Section 7.4)."
    )

    # 5.7 ALU
    pdf.sub("5.7  ALU (alu.v)")
    pdf.code(
        "always @(*) begin\n"
        "    case (alu_control)\n"
        "        4'b0000: result = src1 + src2;             // ADD\n"
        "        4'b0001: result = src1 - src2;             // SUB\n"
        "        4'b0010: result = src1 & src2;             // AND\n"
        "        4'b0011: result = src1 | src2;             // OR\n"
        "        4'b0100: result = src1 ^ src2;             // XOR\n"
        "        4'b0101: result = ($signed(src1) < $signed(src2)) ? 1 : 0;  // SLT\n"
        "        4'b0110: result = src1 << src2[4:0];       // SLL\n"
        "        4'b0111: result = src1 >> src2[4:0];       // SRL\n"
        "        4'b1000: result = (src1 < src2) ? 1 : 0;   // SLTU\n"
        "        4'b1001: result = $signed(src1) >>> src2[4:0];  // SRA\n"
        "        4'b1010: result = (src1 << src2[4:0])\n"
        "                        | (src1 >> (32 - src2[4:0]));   // ROL\n"
        "    endcase\n"
        "end\n"
        "assign zero = (result == 0);"
    )
    pdf.body(
        "Purely combinational. 11 operations. Shift amounts use only src2[4:0] (5 bits for "
        "0-31 range). $signed() enables two's complement comparison for SLT. SRA uses >>> "
        "(arithmetic shift) to preserve the sign bit. ROL combines left-shift and right-shift "
        "to achieve rotation in one operation."
    )
    pdf.body(
        "The zero flag is asserted when result == 0, used by branch logic: BEQ subtracts "
        "operands --zero means equal. BNE checks ~zero."
    )

    # 5.8 DMEM
    pdf.sub("5.8  Data Memory (dmem.v)")
    pdf.code(
        "module dmem(\n"
        "    input clk, input we,\n"
        "    input [31:0] a, wd,\n"
        "    output [31:0] rd\n"
        ");\n"
        "    reg [31:0] RAM [63:0];\n"
        "    assign rd = RAM[a[31:2]];    // Async read\n"
        "    always @(posedge clk)\n"
        "        if (we) RAM[a[31:2]] <= wd;  // Sync write\n"
        "endmodule"
    )
    pdf.body(
        "64 words (256 bytes). Asynchronous read (combinational, same cycle), synchronous "
        "write (on clock edge). Same a[31:2] word-addressing as IMEM. No initialization --"
        "programs must write before reading."
    )

    # ━━ Section 6 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.section("6", "The Pipeline Deep Dive")

    pdf.sub("6.1  Stage 1: Instruction Fetch (IF)")
    pdf.code(
        "  pc_next --> [ PC ] --+--> [ IMEM ] --> instr --> [IF/ID Reg]\n"
        "              ^        |\n"
        "              |        +--> [ PC+4 ] --> pc_plus4\n"
        "          [ PC MUX ]\n"
        "          /    |    \\\n"
        "       pc+4  branch  jalr\n"
        "             target  target"
    )
    pdf.body(
        "The PC outputs the current address. IMEM reads the instruction (combinational). "
        "The PC adder computes PC+4. The PC-next mux selects: JALR target (highest priority), "
        "JAL/branch target, or PC+4 (default sequential). Everything latches into IF/ID on "
        "the clock edge."
    )
    pdf.body(
        "The IF/ID register has three behaviors: (1) Reset or flush: insert NOP (0x00000013) "
        "to cancel the speculatively fetched instruction. (2) Stall: hold current values so "
        "the instruction stays for an extra cycle. (3) Normal: latch new instruction, PC, PC+4."
    )

    pdf.sub("6.2  Stage 2: Instruction Decode (ID)")
    pdf.body(
        "The control unit decodes if_id_instr into control signals. The register file reads "
        "rs1 and rs2 (bits [19:15] and [24:20]). The immediate generator extracts and "
        "sign-extends the immediate. Everything latches into ID/EX."
    )
    pdf.body(
        "On stall or flush, ID/EX gets a bubble --all control signals zeroed. A bubble is an "
        "instruction that will not write registers, not write memory, not branch. It flows "
        "through the pipeline doing nothing."
    )

    pdf.sub("6.3  Stage 3: Execute (EX)")
    pdf.body(
        "The most complex stage. Contains forwarding muxes, ALU source muxes, the ALU itself, "
        "branch resolution, and target computation."
    )
    pdf.body(
        "Forwarding muxes select between: the register file value (no hazard), the EX/MEM "
        "value (1-instruction gap), or the MEM/WB value (2-instruction gap). The ALU source A "
        "mux further selects between the forwarded register value, PC (AUIPC), or zero (LUI). "
        "The ALU source B mux selects between the forwarded register value or the immediate."
    )
    pdf.body(
        "Branch resolution uses the ALU result: BEQ/BNE check the zero flag (SUB result). "
        "BLT/BGE check bit[0] of SLT result. BLTU/BGEU check bit[0] of SLTU result. This "
        "reuses the ALU for comparison instead of adding a separate comparator."
    )
    pdf.body(
        "JALR target = ALU result & 0xFFFFFFFE. The ALU computes rs1 + immediate, then the "
        "LSB is masked to zero per the RISC-V spec (ensures 2-byte alignment)."
    )

    pdf.sub("6.4  Stage 4: Memory Access (MEM)")
    pdf.body(
        "The simplest stage. For loads, DMEM reads from the address computed by the ALU in EX. "
        "For stores, DMEM writes the forwarded rs2 value to the computed address. For all other "
        "instructions, nothing happens --the ALU result just passes through."
    )
    pdf.body(
        "Important: the store data (ex_mem_rd2) uses the forwarded value from the EX stage, "
        "not the raw register value. This handles the case where a store needs a value that "
        "was just computed by the previous instruction."
    )

    pdf.sub("6.5  Stage 5: Write Back (WB)")
    pdf.body(
        "A 3-way mux selects what to write back to the register file: ALU result (for "
        "arithmetic/logic), memory data (for loads), or PC+4 (for JAL/JALR return address). "
        "The write happens through the register file's write port."
    )

    # ━━ Section 7 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.section("7", "Pipeline Hazards: The Real Engineering Challenge")
    pdf.body(
        "Hazards are situations where the next instruction cannot execute correctly because "
        "it depends on information that is not yet available. Without hazard handling, our "
        "pipeline would produce wrong results. This is where most of the engineering "
        "complexity lives."
    )

    pdf.sub("7.1  Data Hazards and Forwarding")
    pdf.sub2("The Problem")
    pdf.body("Consider these back-to-back instructions:")
    pdf.code(
        "ADDI x1, x0, 5     # x1 = 5       (result in EX, not yet in regfile)\n"
        "ADDI x2, x1, 1     # x2 = x1 + 1  (reads x1 from regfile --STALE!)"
    )
    pdf.body(
        "When the second instruction reads x1 in ID, the first has not yet written its result "
        "to the register file (that happens in WB, 2 stages later). This is a Read-After-Write "
        "(RAW) hazard."
    )

    pdf.sub2("The Solution: Forwarding")
    pdf.body(
        "The result already exists in the EX/MEM or MEM/WB pipeline register. We grab it from "
        "there instead of from the register file."
    )
    pdf.code(
        "// Forwarding unit (for rs1):\n"
        "if (ex_mem_reg_write && ex_mem_rd != 0\n"
        "    && ex_mem_rd == id_ex_rs1)\n"
        "    forward_a = 2'b10;   // From EX/MEM (1-instr gap)\n"
        "else if (mem_wb_reg_write && mem_wb_rd != 0\n"
        "         && mem_wb_rd == id_ex_rs1)\n"
        "    forward_a = 2'b01;   // From MEM/WB (2-instr gap)\n"
        "else\n"
        "    forward_a = 2'b00;   // No forwarding needed"
    )
    pdf.body(
        "Three conditions must be true: the earlier instruction writes a register, the "
        "destination is not x0, and the destination matches the source being read. EX/MEM "
        "has priority over MEM/WB (more recent result wins)."
    )

    pdf.sub("7.2  Load-Use Hazard and Stalling")
    pdf.sub2("The Problem")
    pdf.code(
        "LW   x6, 0(x0)     # x6 = mem[0]  (data available END of MEM)\n"
        "ADDI x7, x6, 1     # x7 = x6 + 1  (needs x6 START of EX)"
    )
    pdf.body(
        "The load data does not exist anywhere in the pipeline yet --there is nothing to "
        "forward. We must stall for one cycle."
    )
    pdf.sub2("The Solution: 1-Cycle Stall")
    pdf.code(
        "assign stall = id_ex_result_src == 2'b01 &&  // Load in EX\n"
        "               id_ex_rd != 5'b0 &&            // Not x0\n"
        "               (id_ex_rd == if_id_instr[19:15] ||  // rs1\n"
        "                id_ex_rd == if_id_instr[24:20]);   // rs2"
    )
    pdf.body(
        "When stall asserts: PC freezes (same instruction in IF), IF/ID holds (same instruction "
        "in ID), ID/EX gets a bubble. After one cycle, the load data is in MEM/WB and normal "
        "forwarding delivers it."
    )

    pdf.sub("7.3  Control Hazards and Flushing")
    pdf.sub2("The Problem")
    pdf.code(
        "BEQ x10, x11, target  # Resolved in EX stage\n"
        "ADDI x12, x0, 1       # Already in ID -- WRONG if branch taken!\n"
        "ADDI x13, x0, 2       # Already in IF -- WRONG if branch taken!"
    )
    pdf.body(
        "We do not know if the branch is taken until EX resolves it. By then, wrong "
        "instructions have entered the pipeline."
    )
    pdf.sub2("The Solution: Flush")
    pdf.code(
        "assign flush = ex_branch_taken || id_ex_jump || id_ex_jalr;"
    )
    pdf.body(
        "When flush asserts, IF/ID gets a NOP (cancels instruction in ID) and ID/EX gets "
        "a bubble (cancels instruction that was in ID). Each taken branch or jump wastes "
        "1 cycle. We chose not to implement branch prediction --the penalty is only ~10% "
        "of cycles, and the basic flush mechanism is more educational."
    )

    pdf.sub("7.4  The Write-Through Bypass Bug")
    pdf.body(
        "This was a real bug discovered during Fibonacci testing. Scenario: 3-instruction "
        "gap between producer and consumer:"
    )
    pdf.code(
        "ADDI x1, x0, 5     # Writes x1 in WB (cycle N)\n"
        "NOP                 # gap 1\n"
        "NOP                 # gap 2\n"
        "ADDI x2, x1, 1     # Reads x1 in ID (cycle N) -- SAME CYCLE!"
    )
    pdf.body(
        "The register file read is combinational (before the clock edge) but the write is "
        "synchronous (on the clock edge). Without the bypass, the read gets the OLD value. "
        "The forwarding unit does not help --it only checks EX/MEM and MEM/WB, but the "
        "writing instruction is in WB (past MEM/WB). The fix is the write-through bypass in "
        "the register file: if WB writes the same register ID reads, bypass the write data "
        "directly to the read output."
    )

    # ━━ Section 8 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.section("8", "Performance Counters: Measuring What Matters")
    pdf.body(
        "We built hardware performance counters directly into the pipeline to quantitatively "
        "analyze how well it performs."
    )
    pdf.make_table(
        ["Counter", "What It Measures"],
        [
            ["perf_cycles", "Total clock cycles elapsed"],
            ["perf_instrs", "Instructions retired (completed WB with valid=1)"],
            ["perf_stalls", "Cycles wasted on load-use stalls"],
            ["perf_flushes", "Cycles wasted on branch/jump flushes"],
            ["perf_halted", "Freezes all counters when JAL x0,0 detected"],
        ],
        [40, 150],
    )
    pdf.body(
        "CPI formula: cycles / instructions = 1.0 + (stalls + flushes) / instructions"
    )
    pdf.body(
        "Halt detection: Programs end with JAL x0, 0 (jump to self, write to x0 which is "
        "discarded). We detect this pattern and freeze counters. Without it, the processor "
        "would endlessly execute the halt loop, making metrics meaningless."
    )

    pdf.sub("Fibonacci Benchmark Results")
    pdf.make_table(
        ["Metric", "Single-Cycle", "5-Stage Pipeline"],
        [
            ["CPI", "1.00", "1.14"],
            ["Stall cycles", "0", "0 (forwarding resolves all)"],
            ["Flush cycles", "0", "8 (taken branches)"],
            ["Max clock freq", "~1/T_crit", "~5x higher"],
            ["Effective throughput", "1/T_crit", "~4.4x better"],
        ],
        [50, 60, 80],
    )
    pdf.body(
        "Zero stalls: The Fibonacci code has no load-use hazards --all values flow through "
        "registers and forwarding handles everything. The 8 flushes come from 7 taken loop "
        "branches + 1 halt jump."
    )
    pdf.body(
        "Without forwarding, CPI would be ~1.6-2.0x on this workload (every data dependency "
        "would require stalling), proving the forwarding unit's hardware cost is justified."
    )

    # ━━ Section 9 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.section("9", "Custom ISA Extension: The ROL Instruction")

    pdf.sub("Why Extend the ISA")
    pdf.body(
        "RISC-V is designed to be extended. The base ISA is minimal --no multiply, divide, "
        "floating point, or bitwise rotations. These are left to optional or custom extensions. "
        "We added Rotate Left (ROL) to demonstrate extensibility with a real workload."
    )

    pdf.sub("Instruction Encoding")
    pdf.code(
        "Bit layout: 0000000 | rs2 | rs1 | 001 | rd | 0001011\n"
        "             funct7   rs2   rs1  funct3  rd   opcode\n"
        "\n"
        "Opcode:    0001011 (custom-0 reserved space)\n"
        "Format:    R-type\n"
        "Assembly:  ROL rd, rs1, rs2\n"
        "Operation: rd = (rs1 << rs2[4:0]) | (rs1 >> (32 - rs2[4:0]))"
    )

    pdf.sub("What Changed in Hardware")
    pdf.body("Only 3 changes were needed --demonstrating clean modular design:")
    pdf.bullet(
        "ALU (alu.v): Added one case --4'b1010: result = (src1 << src2[4:0]) | (src1 >> (32 - src2[4:0]))"
    )
    pdf.bullet(
        "Control (control.v): Added one opcode case --7'b0001011: reg_write=1, alu_src=0, alu_control=4'b1010"
    )
    pdf.bullet(
        "Pipeline, forwarding, stall logic: NO changes. ROL flows through the pipeline exactly "
        "like ADD. The pipeline does not need to know what the ALU computes."
    )

    # ━━ Section 10 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.section("10", "ChaCha20 Cryptographic Benchmark")

    pdf.sub("10.1  What is ChaCha20")
    pdf.body(
        "ChaCha20 is a stream cipher designed by Daniel J. Bernstein, used in TLS 1.3 "
        "(HTTPS), WireGuard VPN, Google's QUIC protocol, and SSH. It was designed to be "
        "fast in software on processors lacking AES hardware. Its core operation is the "
        "quarter-round, using only: addition, XOR, and bitwise rotation."
    )
    pdf.body(
        "No multiplication, no table lookups, no variable-time operations. This makes it "
        "resistant to side-channel attacks and efficient on simple processors --like ours."
    )

    pdf.sub("10.2  The Quarter-Round Function")
    pdf.code(
        "a += b;  d ^= a;  d <<<= 16;\n"
        "c += d;  b ^= c;  b <<<= 12;\n"
        "a += b;  d ^= a;  d <<<= 8;\n"
        "c += d;  b ^= c;  b <<<= 7;"
    )
    pdf.body(
        "Four lines, each with ADD + XOR + ROTATE. The rotation amounts (16, 12, 8, 7) are "
        "constants chosen by Bernstein for optimal diffusion. Our benchmark runs 4 rounds "
        "on initial values a=0x61, b=0x62, c=0x63, d=0x64."
    )
    pdf.body("Expected output (verified by Python golden model):")
    pdf.code(
        "a = 0xD576E19B\n"
        "b = 0x1898E8F8\n"
        "c = 0x36858953\n"
        "d = 0x9FF722DF"
    )

    pdf.sub("10.3  Software vs Hardware Rotation")
    pdf.sub2("Software (standard RV32I): 3 instructions per rotation")
    pdf.code(
        "SLLI x5, x4, 16    # t0 = d << 16\n"
        "SRLI x6, x4, 16    # t1 = d >> 16\n"
        "OR   x4, x5, x6    # d  = t0 | t1  (rotated)"
    )
    pdf.body("Three instructions, two temporary registers (x5, x6). Each quarter-round has "
             "4 rotations = 12 instructions just for rotations out of 22 total.")

    pdf.sub2("Hardware (custom ROL): 1 instruction per rotation")
    pdf.code(
        "ROL  x4, x4, x12   # d = ROL(d, 16)  -- one cycle!"
    )
    pdf.body("One instruction, no temporaries. Loop body shrinks from 22 to 14 instructions.")

    pdf.sub("10.4  Results and Why Our Solution Was Great")
    pdf.make_table(
        ["Metric", "Software (RV32I)", "Hardware (ROL)", "Improvement"],
        [
            ["Instrs per iteration", "22", "14", "36% fewer"],
            ["Temporary registers", "2 (x5, x6)", "0", "Frees registers"],
            ["Cycles per rotation", "3-4", "1", "3-4x faster"],
        ],
        [45, 50, 45, 50],
    )

    pdf.sub2("Why this solution is great:")
    pdf.bullet(
        "Minimal hardware cost: ONE line in the ALU, ONE case in the control unit. The gate "
        "count increase is tiny --barrel shifter logic was already mostly present for SLL/SRL."
    )
    pdf.bullet(
        "Measurable real-world impact: ChaCha20 is used in production TLS. The 36% instruction "
        "reduction translates to lower energy and higher throughput."
    )
    pdf.bullet(
        "Standard extension path: Our ROL matches the RISC-V Zbb (Bitmanip) extension's "
        "semantics. We used custom-0 opcode space, but the concept is the same one the "
        "official extension standardizes."
    )
    pdf.bullet(
        "Clean verification: Python golden model computes exact expected output. Both SW and "
        "HW versions produce identical results, verified automatically by the testbench."
    )
    pdf.bullet(
        "Full-stack demonstration: Algorithm -> Python assembler -> machine code hex -> "
        "hardware execution -> automated verification. Shows complete hardware/software co-design."
    )

    # ━━ Section 11 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.section("11", "Test Programs Explained")

    pdf.sub("program.hex --Pipeline Hazard Tests")
    pdf.body("Systematically tests every hazard scenario:")
    pdf.code(
        "Test 1: EX/MEM Forwarding (back-to-back)\n"
        "  ADDI x1, x0, 5\n"
        "  ADDI x2, x1, 1   -> forward x1 from EX/MEM\n"
        "\n"
        "Test 2: MEM/WB Forwarding (2-instruction gap)\n"
        "  ADDI x4, x0, 10\n"
        "  NOP               -> 1 gap\n"
        "  ADDI x5, x4, 4   -> forward x4 from MEM/WB\n"
        "\n"
        "Test 3: Load-Use Hazard (stall + forward)\n"
        "  LW   x6, 0(x0)   -> load from memory\n"
        "  ADDI x7, x6, 1   -> stall 1 cycle, then forward\n"
        "\n"
        "Test 4: R-type Forwarding Chain\n"
        "  ADD  x1, x1, x2  -> forward both inputs\n"
        "  ADD  x2, x1, x1  -> forward x1 from EX/MEM\n"
        "\n"
        "Test 5: Store with Forwarded Data\n"
        "  ADDI x8, x0, 20\n"
        "  SW   x8, 0(x0)   -> store with forwarded x8\n"
        "\n"
        "Test 6: Branch with Forwarding\n"
        "  ADDI x10, x0, 5\n"
        "  ADDI x11, x0, 5\n"
        "  BEQ  x10, x11, +12 -> forward both, branch taken\n"
        "  ADDI x12, x0, 1    -> FLUSHED\n"
        "  ADDI x12, x0, 0    -> branch target"
    )

    pdf.sub("benchmark.hex --Fibonacci")
    pdf.code(
        "Init:  x1=0 (F0), x2=1 (F1), counter=2, limit=10\n"
        "Store: mem[0]=0, mem[4]=1\n"
        "\n"
        "Loop:\n"
        "  x3 = x1 + x2      # F(n) = F(n-2) + F(n-1)\n"
        "  mem[ptr] = x3      # store F(n)\n"
        "  x1 = x2            # shift\n"
        "  x2 = x3            # shift\n"
        "  ptr += 4, counter++\n"
        "  BNE counter, 10, loop\n"
        "\n"
        "Result: mem[0..9] = 0, 1, 1, 2, 3, 5, 8, 13, 21, 34"
    )

    # ━━ Section 12 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.section("12", "How to Build and Run Everything")
    pdf.body("Prerequisites: Icarus Verilog (iverilog), GTKWave (optional), Python 3 (optional).")
    pdf.code(
        "# Pipeline hazard test\n"
        "iverilog -o hazard_test src/*.v tb/top_tb.v && vvp hazard_test\n"
        "\n"
        "# Fibonacci benchmark\n"
        "iverilog -o bench src/*.v tb/benchmark_tb.v && vvp bench\n"
        "\n"
        "# ChaCha20 crypto benchmark (SW vs HW)\n"
        "iverilog -o crypto src/*.v tb/crypto_tb.v && vvp crypto\n"
        "\n"
        "# Regenerate crypto hex files\n"
        "python3 gen_crypto_hex.py\n"
        "\n"
        "# View waveforms\n"
        "gtkwave cpu_test.vcd"
    )

    # ━━ Section 13 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.section("13", "Project Evolution")
    pdf.body("Our git history tells the story of how this project grew:")

    pdf.sub2("Phase 1: Basic Building Blocks (Commits 1-3)")
    pdf.body("Started with individual modules (PC, IMEM, ALU, register file, control) and "
             "wired them into a single-cycle datapath. Fixed early bugs.")

    pdf.sub2("Phase 2: Complete Single-Cycle RV32I (Commits 4-6)")
    pdf.body("Added branches (BEQ, BNE, BLT, BGE, BLTU, BGEU), jumps (JAL, JALR), "
             "LUI and AUIPC. Complete single-cycle processor.")

    pdf.sub2("Phase 3: Pipelining (Commit 7)")
    pdf.body("The big rewrite. Split the datapath into 5 stages with pipeline registers. "
             "Every signal crossing a stage boundary needs to be registered.")

    pdf.sub2("Phase 4: Hazard Handling (Commits 8-9)")
    pdf.body("Added forwarding unit, load-use stall detection, branch flushing. "
             "Discovered and fixed the register file write-through bug.")

    pdf.sub2("Phase 5: Quantitative Analysis (Commits 10-11)")
    pdf.body("Added performance counters, Fibonacci benchmark, hazard test. Now we could "
             "measure CPI, stall rates, and flush rates.")

    pdf.sub2("Phase 6: Custom ISA Extension (Commit 12)")
    pdf.body("Added ROL instruction, ChaCha20 benchmark, Python hex generator. The capstone --"
             "showing the pipeline is correct, performant, and extensible.")

    # ━━ Summary Table ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    pdf.add_page()
    pdf.set_font("NotoSans", "B", 18)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 14, "Summary of Key Design Choices", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    pdf.make_table(
        ["Decision", "Choice", "Why"],
        [
            ["ISA", "RISC-V RV32I", "Open, clean, extensible"],
            ["Architecture", "Harvard", "Avoids fetch/mem structural hazards"],
            ["Pipeline depth", "5 stages", "Classic throughput vs complexity balance"],
            ["Data hazards", "Forwarding", "Eliminates ~90%+ of stalls"],
            ["Load-use", "1-cycle stall", "Data not available to forward yet"],
            ["Control hazards", "Flush", "Simple, 1-cycle penalty"],
            ["Branch resolve", "EX stage", "Reuses ALU for comparison"],
            ["Memory width", "32-bit words", "Sufficient, avoids byte alignment"],
            ["Custom instr", "ROL", "Real crypto need, minimal HW cost"],
            ["Benchmark", "ChaCha20 QR", "Production cipher, rotation-heavy"],
            ["Verification", "Python golden model", "Automated SW/HW co-verification"],
        ],
        [35, 45, 110],
    )
    pdf.ln(10)
    pdf.set_font("NotoSans", "I", 11)
    pdf.set_text_color(*GREY)
    pdf.cell(0, 8, "This processor runs real programs, handles real hazards,", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, "and demonstrates real ISA extensibility.", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 8, "It is not a textbook diagram -- it is working hardware.", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ━━ Output ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    out = os.path.join(os.path.dirname(__file__), "RV32I_Project_Guide.pdf")
    pdf.output(out)
    print(f"Generated: {out}")
    print(f"Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build()

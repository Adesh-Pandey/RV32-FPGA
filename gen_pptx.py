#!/usr/bin/env python3
"""Generate PPTX presentation for RV32I Pipelined Processor project."""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
import copy

# ── Colors ──
BG       = RGBColor(0x0A, 0x0E, 0x1A)
BG_CARD  = RGBColor(0x11, 0x18, 0x27)
ACCENT   = RGBColor(0x60, 0xA5, 0xFA)
ACCENT2  = RGBColor(0xA7, 0x8B, 0xFA)
GREEN    = RGBColor(0x34, 0xD3, 0x99)
ORANGE   = RGBColor(0xFB, 0x92, 0x3C)
RED      = RGBColor(0xF8, 0x71, 0x71)
PINK     = RGBColor(0xEC, 0x48, 0x99)
TEXT     = RGBColor(0xE2, 0xE8, 0xF0)
DIM      = RGBColor(0x94, 0xA3, 0xB8)
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
BORDER   = RGBColor(0x1E, 0x29, 0x3B)
DARK     = RGBColor(0x0D, 0x11, 0x17)

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
W = prs.slide_width
H = prs.slide_height

# ── Helper functions ──

def add_slide():
    layout = prs.slide_layouts[6]  # blank
    slide = prs.slides.add_slide(layout)
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = BG
    return slide

def add_textbox(slide, left, top, width, height):
    txBox = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    txBox.text_frame.word_wrap = True
    return txBox.text_frame

def add_text(tf, text, size=14, color=TEXT, bold=False, font_name='Calibri', alignment=PP_ALIGN.LEFT, space_after=Pt(4)):
    p = tf.add_paragraph() if len(tf.paragraphs) > 0 and tf.paragraphs[0].text != '' else tf.paragraphs[0]
    if tf.paragraphs[0].text != '' or len(tf.paragraphs) > 1:
        p = tf.add_paragraph()
    p.alignment = alignment
    p.space_after = space_after
    run = p.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.name = font_name
    return p

def add_run(paragraph, text, size=14, color=TEXT, bold=False, font_name='Calibri'):
    run = paragraph.add_run()
    run.text = text
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold
    run.font.name = font_name
    return run

def add_card(slide, left, top, width, height, fill=BG_CARD):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = BORDER
    shape.line.width = Pt(1)
    shape.shadow.inherit = False
    return shape

def add_rect(slide, left, top, width, height, fill=BG_CARD, line_color=BORDER, line_width=1):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line_color
    shape.line.width = Pt(line_width)
    shape.shadow.inherit = False
    return shape

def add_tag(slide, left, top, text_str, color=ACCENT):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(1.6), Inches(0.32))
    shape.fill.solid()
    shape.fill.fore_color.rgb = RGBColor(
        min(255, color[0] // 5), min(255, color[1] // 5), min(255, color[2] // 5)
    )
    shape.line.fill.background()
    shape.shadow.inherit = False
    tf = shape.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text_str.upper()
    run.font.size = Pt(9)
    run.font.color.rgb = color
    run.font.bold = True
    run.font.name = 'Calibri'

def slide_header(slide, tag_text, title_text, tag_color=ACCENT):
    add_tag(slide, 0.6, 0.35, tag_text, tag_color)
    tf = add_textbox(slide, 0.6, 0.72, 12, 0.55)
    add_text(tf, title_text, size=28, color=TEXT, bold=True)
    # underline bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.6), Inches(1.28), Inches(0.8), Inches(0.04))
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()
    bar.shadow.inherit = False

def add_bullet_list(tf, items, size=13, color=DIM, bold_prefix=True):
    for item in items:
        p = tf.add_paragraph()
        p.space_after = Pt(3)
        p.level = 0
        if ':' in item and bold_prefix:
            parts = item.split(':', 1)
            r1 = p.add_run()
            r1.text = '  \u2022  ' + parts[0] + ':'
            r1.font.size = Pt(size)
            r1.font.color.rgb = TEXT
            r1.font.bold = True
            r1.font.name = 'Calibri'
            r2 = p.add_run()
            r2.text = parts[1]
            r2.font.size = Pt(size)
            r2.font.color.rgb = color
            r2.font.name = 'Calibri'
        else:
            r = p.add_run()
            r.text = '  \u2022  ' + item
            r.font.size = Pt(size)
            r.font.color.rgb = color
            r.font.name = 'Calibri'

def add_table(slide, left, top, width, height, rows, cols, data, col_widths=None, header_color=ACCENT):
    table_shape = slide.shapes.add_table(rows, cols, Inches(left), Inches(top), Inches(width), Inches(height))
    table = table_shape.table

    if col_widths:
        for i, w in enumerate(col_widths):
            table.columns[i].width = Inches(w)

    for r in range(rows):
        for c in range(cols):
            cell = table.cell(r, c)
            cell.text = ''
            val, clr, bld = '', DIM, False
            entry = data[r][c]
            if isinstance(entry, tuple):
                val, clr, bld = entry[0], entry[1], entry[2] if len(entry) > 2 else False
            else:
                val = str(entry)
                clr = DIM
                bld = False

            p = cell.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = val
            run.font.size = Pt(11)
            run.font.name = 'Calibri'

            if r == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(0x15, 0x1D, 0x2E)
                run.font.color.rgb = header_color
                run.font.bold = True
                run.font.size = Pt(10)
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = BG_CARD
                run.font.color.rgb = clr
                run.font.bold = bld

            # borders
            for edge in ['top', 'bottom', 'left', 'right']:
                border = getattr(cell.border, edge, None) if hasattr(cell, 'border') else None

    return table

def add_metric_card(slide, left, top, value, label, color=ACCENT):
    card = add_card(slide, left, top, 2.7, 1.2)
    tf = card.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(12)
    r = p.add_run()
    r.text = value
    r.font.size = Pt(32)
    r.font.color.rgb = color
    r.font.bold = True
    r.font.name = 'Calibri'

    p2 = tf.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = label
    r2.font.size = Pt(9)
    r2.font.color.rgb = DIM
    r2.font.bold = True
    r2.font.name = 'Calibri'

def add_code_block(slide, left, top, width, height, code):
    shape = add_rect(slide, left, top, width, height, fill=DARK, line_color=RGBColor(0x21, 0x26, 0x2D))
    tf = shape.text_frame
    tf.word_wrap = True
    for i, line in enumerate(code.split('\n')):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.space_after = Pt(0)
        p.space_before = Pt(0)
        r = p.add_run()
        r.text = line
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0xC9, 0xD1, 0xD9)
        r.font.name = 'Consolas'

def add_highlight_box(slide, left, top, width, height, text_str, accent=ACCENT):
    # left border bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top), Inches(0.04), Inches(height))
    bar.fill.solid()
    bar.fill.fore_color.rgb = accent
    bar.line.fill.background()
    bar.shadow.inherit = False
    # background
    bg_shape = add_rect(slide, left + 0.05, top, width - 0.05, height,
                        fill=RGBColor(min(255, accent[0]//8 + BG[0]), min(255, accent[1]//8 + BG[1]), min(255, accent[2]//8 + BG[2])),
                        line_color=BORDER)
    tf = bg_shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    r = p.add_run()
    r.text = text_str
    r.font.size = Pt(12)
    r.font.color.rgb = DIM
    r.font.name = 'Calibri'
    return tf


# ════════════════════════════════════════════════
#  SLIDE 1: TITLE
# ════════════════════════════════════════════════
s = add_slide()

tf = add_textbox(s, 1.5, 1.2, 10.3, 1.5)
add_text(tf, 'Design & Implementation of a', size=22, color=DIM, alignment=PP_ALIGN.CENTER)
add_text(tf, '5-Stage Pipelined RV32I Processor', size=36, color=ACCENT, bold=True, alignment=PP_ALIGN.CENTER)
add_text(tf, 'RISC-V Base Integer Instruction Set in Verilog HDL', size=16, color=DIM, alignment=PP_ALIGN.CENTER)

# Team members
for i, (name, sid) in enumerate([('Adesh Pandey', '079BEI004'), ('Aayush Gelal', '079BEI002'), ('Bishesh Paudel', '079BEI016')]):
    x = 3.0 + i * 2.7
    card = add_card(s, x, 3.8, 2.3, 0.9)
    tf2 = card.text_frame
    tf2.word_wrap = True
    p = tf2.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(10)
    r = p.add_run()
    r.text = name
    r.font.size = Pt(14)
    r.font.color.rgb = TEXT
    r.font.bold = True
    r.font.name = 'Calibri'
    p2 = tf2.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = sid
    r2.font.size = Pt(11)
    r2.font.color.rgb = ACCENT
    r2.font.name = 'Consolas'

tf3 = add_textbox(s, 2, 5.2, 9.3, 0.8)
add_text(tf3, 'Tribhuvan University \u00b7 Institute of Engineering \u00b7 Pulchowk Campus', size=13, color=DIM, alignment=PP_ALIGN.CENTER)
add_text(tf3, 'Department of Electronics & Computer Engineering \u00b7 March 2026', size=12, color=DIM, alignment=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════
#  SLIDE 2: INTRODUCTION
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Introduction', 'Why RISC-V? Why Pipelining?')

add_card(s, 0.6, 1.5, 5.8, 2.6)
tf = add_textbox(s, 0.8, 1.55, 5.4, 0.3)
add_text(tf, 'RISC-V: The Open Standard ISA', size=14, color=ACCENT, bold=True)
tf2 = add_textbox(s, 0.8, 1.9, 5.4, 2.0)
add_bullet_list(tf2, [
    'Open & free: no licensing fees, unlike ARM or x86',
    'Modular design: base integer set (RV32I) + optional extensions',
    'Industry adoption: SiFive, Google, NVIDIA, Qualcomm',
    'Academic standard: clean ISA ideal for teaching architecture',
])

add_card(s, 0.6, 4.3, 5.8, 2.5)
tf = add_textbox(s, 0.8, 4.35, 5.4, 0.3)
add_text(tf, 'Why Pipelining?', size=14, color=ACCENT, bold=True)
tf2 = add_textbox(s, 0.8, 4.7, 5.4, 1.8)
add_bullet_list(tf2, [
    'Throughput boost: overlap execution of multiple instructions',
    'Higher clock speed: shorter critical path per stage',
    'Real-world relevance: all modern CPUs are pipelined',
])

add_card(s, 6.7, 1.5, 6.0, 5.3)
tf = add_textbox(s, 6.9, 1.55, 5.6, 0.3)
add_text(tf, 'Project Objectives', size=14, color=ACCENT, bold=True)
tf2 = add_textbox(s, 6.9, 1.9, 5.6, 3.5)
add_bullet_list(tf2, [
    'Implement full RV32I base instruction set (37 instructions)',
    'Build a 5-stage pipeline with forwarding & hazard detection',
    'Evolve from single-cycle \u2192 pipelined architecture',
    'Add performance counters for quantitative analysis',
    'Benchmark with real programs and compare CPI',
    'Extend ISA with custom crypto instruction (ROL)',
    'Verify with comprehensive testbenches',
])

add_highlight_box(s, 6.9, 5.6, 5.6, 0.9,
    'Key Insight: A 5-stage pipeline achieves ~4.4x throughput over single-cycle, despite ~14% CPI penalty. Custom ROL gives 1.35x crypto speedup.')


# ════════════════════════════════════════════════
#  SLIDE 3: RV32I ISA
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Instruction Set', 'RV32I Base Integer Instructions')

add_card(s, 0.6, 1.5, 6.0, 3.0)
tf = add_textbox(s, 0.8, 1.55, 5.6, 0.3)
add_text(tf, '37 Instructions Implemented', size=14, color=ACCENT, bold=True)

tf2 = add_textbox(s, 0.8, 1.9, 5.6, 2.4)
add_text(tf2, 'R-Type (Register-Register) \u2014 10 instructions', size=11, color=ACCENT, bold=True)
add_text(tf2, 'ADD  SUB  SLL  SLT  SLTU  XOR  SRL  SRA  OR  AND', size=11, color=DIM, font_name='Consolas')
add_text(tf2, '', size=6, color=DIM)
add_text(tf2, 'I-Type (Immediate) \u2014 9 instructions', size=11, color=ACCENT2, bold=True)
add_text(tf2, 'ADDI  SLTI  SLTIU  XORI  ORI  ANDI  SLLI  SRLI  SRAI', size=11, color=DIM, font_name='Consolas')
add_text(tf2, '', size=6, color=DIM)
add_text(tf2, 'Load / Store \u2014 2 instructions', size=11, color=GREEN, bold=True)
add_text(tf2, 'LW   SW', size=11, color=DIM, font_name='Consolas')

add_card(s, 6.9, 1.5, 5.8, 3.0)
tf = add_textbox(s, 7.1, 1.55, 5.4, 0.3)
add_text(tf, 'Branch, Jump & Upper Immediate', size=14, color=ACCENT, bold=True)

tf2 = add_textbox(s, 7.1, 1.9, 5.4, 2.4)
add_text(tf2, 'B-Type (Branch) \u2014 6 instructions', size=11, color=ORANGE, bold=True)
add_text(tf2, 'BEQ  BNE  BLT  BGE  BLTU  BGEU', size=11, color=DIM, font_name='Consolas')
add_text(tf2, '', size=6, color=DIM)
add_text(tf2, 'J-Type (Jump) \u2014 2 instructions', size=11, color=PINK, bold=True)
add_text(tf2, 'JAL   JALR', size=11, color=DIM, font_name='Consolas')
add_text(tf2, '', size=6, color=DIM)
add_text(tf2, 'U-Type (Upper Immediate) \u2014 2 instructions', size=11, color=RED, bold=True)
add_text(tf2, 'LUI   AUIPC', size=11, color=DIM, font_name='Consolas')

add_card(s, 0.6, 4.7, 12.1, 2.2)
tf = add_textbox(s, 0.8, 4.75, 11.7, 0.3)
add_text(tf, 'Instruction Format Encoding', size=14, color=ACCENT, bold=True)
add_code_block(s, 0.8, 5.15, 11.7, 1.6,
    '  31        25 24    20 19    15 14  12 11     7 6      0\n'
    'R: [ funct7   ] [ rs2  ] [ rs1  ] [f3 ] [ rd    ] [opcode ]  <- ADD, SUB ...\n'
    'I: [ imm[11:0]         ] [ rs1  ] [f3 ] [ rd    ] [opcode ]  <- ADDI, LW\n'
    'S: [ imm[11:5]] [ rs2  ] [ rs1  ] [f3 ] [imm4:0 ] [opcode ]  <- SW\n'
    'B: [imm[12|10:5]] [rs2 ] [ rs1  ] [f3 ] [im4:1|11][opcode ]  <- BEQ, BNE\n'
    'U: [ imm[31:12]                  ] [ rd    ] [opcode ]  <- LUI, AUIPC\n'
    'J: [imm[20|10:1|11|19:12]       ] [ rd    ] [opcode ]  <- JAL')


# ════════════════════════════════════════════════
#  SLIDE 4: SINGLE-CYCLE BASELINE
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Architecture', 'Single-Cycle Baseline')

add_card(s, 0.6, 1.5, 5.8, 2.4)
tf = add_textbox(s, 0.8, 1.55, 5.4, 0.3)
add_text(tf, 'How Single-Cycle Works', size=14, color=ACCENT, bold=True)
tf2 = add_textbox(s, 0.8, 1.9, 5.4, 1.8)
add_bullet_list(tf2, [
    'Each instruction completes in one clock cycle',
    'All hardware used sequentially in one cycle',
    'Clock period = longest instruction delay path',
    'CPI is always 1.0 by definition',
])

add_card(s, 0.6, 4.1, 5.8, 1.6)
tf = add_textbox(s, 0.8, 4.15, 5.4, 0.3)
add_text(tf, 'The Problem', size=14, color=ORANGE, bold=True)
tf2 = add_textbox(s, 0.8, 4.5, 5.4, 1.0)
add_text(tf2, 'Critical path bottleneck: The clock must be slow enough for the slowest instruction (LW: PC \u2192 IMEM \u2192 RegFile \u2192 ALU \u2192 DMEM \u2192 Mux). Every instruction pays this penalty.', size=12, color=DIM)

# Datapath diagram as text
add_card(s, 6.7, 1.5, 6.0, 4.2)
tf = add_textbox(s, 6.9, 1.55, 5.6, 0.3)
add_text(tf, 'Single-Cycle Datapath', size=14, color=ACCENT, bold=True)

# Draw pipeline stages as shapes
stages = [('PC', ACCENT, 7.2), ('IMEM', ACCENT2, 8.2), ('RegFile', GREEN, 9.2), ('ALU', ORANGE, 10.2), ('DMEM', RED, 11.2)]
for name, color, x in stages:
    box = add_rect(s, x, 2.8, 0.9, 0.7, fill=BG_CARD, line_color=color, line_width=2)
    tf_b = box.text_frame
    p = tf_b.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = name
    r.font.size = Pt(11)
    r.font.color.rgb = color
    r.font.bold = True
    r.font.name = 'Calibri'

# Arrow shapes between stages
for x in [8.1, 9.1, 10.1, 11.1]:
    arrow = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(3.0), Inches(0.15), Inches(0.25))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = DIM
    arrow.line.fill.background()
    arrow.shadow.inherit = False

# Critical path label
add_highlight_box(s, 7.0, 4.0, 5.4, 0.6,
    'T_critical = T_pc + T_imem + T_reg + T_alu + T_dmem + T_mux', accent=RED)

add_highlight_box(s, 0.6, 5.9, 12.1, 0.9,
    'Key Insight: In single-cycle, a simple ADD takes the same time as the slowest LW instruction. Pipelining breaks this into 5 shorter stages, allowing ~5x higher clock frequency.',
    accent=GREEN)


# ════════════════════════════════════════════════
#  SLIDE 5: 5-STAGE PIPELINE
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Architecture', '5-Stage Pipeline Architecture')

# Pipeline stages
pipe_data = [
    ('IF', 'Instruction\nFetch', ACCENT, 1.0),
    ('ID', 'Instruction\nDecode', ACCENT2, 3.3),
    ('EX', 'Execute /\nBranch', GREEN, 5.6),
    ('MEM', 'Memory\nAccess', ORANGE, 7.9),
    ('WB', 'Write\nBack', RED, 10.2),
]

regs = [('IF/ID', ACCENT2, 2.5), ('ID/EX', GREEN, 4.8), ('EX/MEM', ORANGE, 7.1), ('MEM/WB', RED, 9.4)]

for name, desc, color, x in pipe_data:
    box = add_rect(s, x, 1.7, 1.5, 1.0, fill=BG_CARD, line_color=color, line_width=2)
    tf_b = box.text_frame
    tf_b.word_wrap = True
    p = tf_b.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(4)
    r = p.add_run()
    r.text = name
    r.font.size = Pt(18)
    r.font.color.rgb = color
    r.font.bold = True
    p2 = tf_b.add_paragraph()
    p2.alignment = PP_ALIGN.CENTER
    r2 = p2.add_run()
    r2.text = desc
    r2.font.size = Pt(9)
    r2.font.color.rgb = DIM

for name, color, x in regs:
    box = add_rect(s, x, 1.8, 0.65, 0.8, fill=RGBColor(0x14, 0x1A, 0x2A), line_color=color, line_width=1)
    tf_b = box.text_frame
    p = tf_b.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(10)
    r = p.add_run()
    r.text = name
    r.font.size = Pt(8)
    r.font.color.rgb = color
    r.font.bold = True
    r.font.name = 'Consolas'

# Stage function table
data = [
    [('Stage', ACCENT, True), ('Operations', ACCENT, True), ('Key Modules', ACCENT, True)],
    [('IF', ACCENT), ('Fetch instruction at PC, compute PC+4', DIM), ('pc, imem, pc_adder', DIM)],
    [('ID', ACCENT2), ('Decode opcode, read registers, gen immediate', DIM), ('control, regfile, imm_gen', DIM)],
    [('EX', GREEN), ('ALU operation, branch decision, target calc', DIM), ('alu, forwarding mux', DIM)],
    [('MEM', ORANGE), ('Load/Store data memory access', DIM), ('dmem', DIM)],
    [('WB', RED), ('Select result and write to register file', DIM), ('result mux, regfile', DIM)],
]
add_table(s, 0.6, 3.0, 6.0, 2.8, 6, 3, data, col_widths=[0.7, 3.3, 2.0])

# Pipeline register table
data2 = [
    [('Register', ACCENT, True), ('Width', ACCENT, True), ('Key Fields', ACCENT, True)],
    [('IF/ID', ACCENT2), ('~67 bits', DIM), ('instruction, PC, PC+4', DIM)],
    [('ID/EX', GREEN), ('~180 bits', DIM), ('controls, rd1, rd2, imm, rs1/rs2/rd', DIM)],
    [('EX/MEM', ORANGE), ('~103 bits', DIM), ('ALU result, write data, rd, controls', DIM)],
    [('MEM/WB', RED), ('~104 bits', DIM), ('ALU result, mem data, rd, controls', DIM)],
]
add_table(s, 6.9, 3.0, 5.8, 2.4, 5, 3, data2, col_widths=[1.2, 1.2, 3.4])

add_highlight_box(s, 6.9, 5.7, 5.8, 0.7,
    'Key advantage: Each stage is 1/5 of the critical path -> clock runs ~5x faster.', accent=GREEN)


# ════════════════════════════════════════════════
#  SLIDE 6: PIPELINE TIMING
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Architecture', 'Pipeline Timing & Instruction Overlap')

add_card(s, 0.6, 1.5, 12.1, 3.0)
tf = add_textbox(s, 0.8, 1.55, 11.7, 0.3)
add_text(tf, 'Ideal Pipeline Execution (No Hazards)', size=14, color=ACCENT, bold=True)
add_text(tf, 'Multiple instructions execute simultaneously, each in a different stage:', size=11, color=DIM)

# Timing diagram as table
colors_map = {'IF': ACCENT, 'ID': ACCENT2, 'EX': GREEN, 'MEM': ORANGE, 'WB': RED}
timing_data = [
    [('', DIM), ('CC1', DIM, True), ('CC2', DIM, True), ('CC3', DIM, True), ('CC4', DIM, True), ('CC5', DIM, True), ('CC6', DIM, True), ('CC7', DIM, True), ('CC8', DIM, True), ('CC9', DIM, True)],
    [('Instr 1', DIM), ('IF', ACCENT), ('ID', ACCENT2), ('EX', GREEN), ('MEM', ORANGE), ('WB', RED), ('', DIM), ('', DIM), ('', DIM), ('', DIM)],
    [('Instr 2', DIM), ('', DIM), ('IF', ACCENT), ('ID', ACCENT2), ('EX', GREEN), ('MEM', ORANGE), ('WB', RED), ('', DIM), ('', DIM), ('', DIM)],
    [('Instr 3', DIM), ('', DIM), ('', DIM), ('IF', ACCENT), ('ID', ACCENT2), ('EX', GREEN), ('MEM', ORANGE), ('WB', RED), ('', DIM), ('', DIM)],
    [('Instr 4', DIM), ('', DIM), ('', DIM), ('', DIM), ('IF', ACCENT), ('ID', ACCENT2), ('EX', GREEN), ('MEM', ORANGE), ('WB', RED), ('', DIM)],
    [('Instr 5', DIM), ('', DIM), ('', DIM), ('', DIM), ('', DIM), ('IF', ACCENT), ('ID', ACCENT2), ('EX', GREEN), ('MEM', ORANGE), ('WB', RED)],
]
add_table(s, 0.8, 2.4, 11.5, 2.0, 6, 10, timing_data, col_widths=[1.2]+[1.14]*9)

# Throughput comparison
add_card(s, 0.6, 4.7, 6.0, 2.2)
tf = add_textbox(s, 0.8, 4.75, 5.6, 0.3)
add_text(tf, 'Throughput Comparison', size=14, color=ACCENT, bold=True)
tf2 = add_textbox(s, 0.8, 5.15, 5.6, 1.5)
add_text(tf2, 'Single-Cycle:               1x throughput', size=12, color=RED, font_name='Consolas')
add_text(tf2, '5-Stage (ideal CPI=1):      5x throughput', size=12, color=GREEN, font_name='Consolas')
add_text(tf2, '5-Stage (real CPI=1.14):    ~4.4x throughput', size=12, color=ACCENT, font_name='Consolas')

add_card(s, 6.9, 4.7, 5.8, 2.2)
tf = add_textbox(s, 7.1, 4.75, 5.4, 0.3)
add_text(tf, 'Why Not Perfect 5x?', size=14, color=ACCENT, bold=True)
tf2 = add_textbox(s, 7.1, 5.15, 5.4, 1.5)
add_bullet_list(tf2, [
    'Data hazards: instruction depends on unavailable result',
    'Control hazards: branch decision not known until EX',
    'Pipeline fill/drain: startup & shutdown overhead',
], size=12)
tf3 = add_textbox(s, 7.1, 6.2, 5.4, 0.3)
add_text(tf3, 'Speedup = N / CPI = 5 / 1.14 = 4.39x', size=13, color=GREEN, bold=True)


# ════════════════════════════════════════════════
#  SLIDE 7: MODULES
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Design', 'Hardware Module Breakdown')

modules = [
    ('pc.v', '32-bit program counter with reset & enable for stall control', ACCENT, '16 lines'),
    ('pc_adder.v', 'Simple combinational adder: PC + 4', ACCENT, '7 lines'),
    ('imem.v', '64-word instruction memory. NOP-initialized. Loads .hex', ACCENT2, '15 lines'),
    ('control.v', 'Combinational decoder: opcode+funct3+funct7 \u2192 10 control signals', ACCENT2, '133 lines'),
    ('regfile.v', '32x32 register file. x0=0. Write-through bypass for WB\u2192ID', GREEN, '24 lines'),
    ('imm_gen.v', 'Sign-extended immediates for all 6 instruction formats', GREEN, '33 lines'),
    ('alu.v', '11-operation ALU: ADD,SUB,AND,OR,XOR,SLT,SLTU,SLL,SRL,SRA,ROL', ORANGE, '28 lines'),
    ('dmem.v', '64-word data memory. Async read, sync write', ORANGE, '18 lines'),
    ('top.v', 'Pipeline: 4 pipe regs, forwarding, hazard detect, perf counters', RED, '401 lines'),
]

for i, (name, desc, color, lines) in enumerate(modules):
    col = i % 3
    row = i // 3
    x = 0.6 + col * 4.15
    y = 1.5 + row * 1.75
    card = add_card(s, x, y, 3.9, 1.5)
    tf = card.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.space_before = Pt(8)
    r = p.add_run()
    r.text = name
    r.font.size = Pt(13)
    r.font.color.rgb = color
    r.font.bold = True
    r.font.name = 'Consolas'
    p2 = tf.add_paragraph()
    r2 = p2.add_run()
    r2.text = desc
    r2.font.size = Pt(10)
    r2.font.color.rgb = DIM
    r2.font.name = 'Calibri'
    p3 = tf.add_paragraph()
    r3 = p3.add_run()
    r3.text = lines
    r3.font.size = Pt(9)
    r3.font.color.rgb = color
    r3.font.name = 'Consolas'

tf = add_textbox(s, 2.0, 6.9, 9.3, 0.3)
add_text(tf, 'Total: 9 modules \u00b7 675 lines of Verilog \u00b7 5 testbenches \u00b7 227 lines of test code', size=12, color=DIM, alignment=PP_ALIGN.CENTER)


# ════════════════════════════════════════════════
#  SLIDE 8: PIPELINE HAZARDS
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Hazards', 'Pipeline Hazards Overview')

# 3 hazard cards
for i, (title, desc, code, solution, color) in enumerate([
    ('Data Hazards (RAW)',
     'Instruction needs a register value not yet written back.',
     'ADD x1, x2, x3  // writes x1\nSUB x4, x1, x5  // reads x1!',
     'Data forwarding + load-use stall',
     ACCENT),
    ('Control Hazards',
     'Branch outcome unknown until EX \u2014 wrong instructions may enter pipeline.',
     'BEQ x1, x2, target\n// next 2 instrs fetched\n// must flush if taken',
     'Pipeline flush (2-cycle penalty)',
     ORANGE),
    ('Load-Use Hazard',
     'Load result only available after MEM, but next instruction needs it in EX.',
     'LW   x6, 0(x0)   // data at MEM\nADDI x7, x6, 1   // needs in EX!',
     '1-cycle stall + MEM/WB forward',
     RED),
]):
    x = 0.6 + i * 4.15
    add_card(s, x, 1.5, 3.9, 3.5)
    tf = add_textbox(s, x+0.15, 1.55, 3.6, 0.3)
    add_text(tf, title, size=13, color=color, bold=True)
    tf2 = add_textbox(s, x+0.15, 1.9, 3.6, 0.6)
    add_text(tf2, desc, size=11, color=DIM)
    add_code_block(s, x+0.15, 2.7, 3.6, 0.9, code)
    tf3 = add_textbox(s, x+0.15, 3.7, 3.6, 0.4)
    add_text(tf3, 'Solution: ' + solution, size=11, color=color, bold=True)

# Resolution table
data = [
    [('Hazard Type', ACCENT, True), ('Resolution', ACCENT, True), ('Penalty', ACCENT, True)],
    [('RAW (1-gap)', DIM), ('Forward from EX/MEM', GREEN), ('0 cycles', GREEN)],
    [('RAW (2-gap)', DIM), ('Forward from MEM/WB', GREEN), ('0 cycles', GREEN)],
    [('RAW (3-gap)', DIM), ('Register write-through', GREEN), ('0 cycles', GREEN)],
    [('Load-Use', DIM), ('Stall 1 cycle + forward', ORANGE), ('1 cycle', ORANGE)],
    [('Branch taken', DIM), ('Flush IF/ID + ID/EX', ORANGE), ('2 cycles', ORANGE)],
]
add_table(s, 0.6, 5.2, 7.0, 2.0, 6, 3, data, col_widths=[2.0, 3.0, 2.0])

add_highlight_box(s, 8.0, 5.2, 4.7, 1.3,
    '4 out of 5 hazard types resolved with ZERO penalty thanks to forwarding. Only load-use requires 1-cycle stall, and branches cost 2 cycles when taken.', accent=GREEN)


# ════════════════════════════════════════════════
#  SLIDE 9: DATA FORWARDING
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Hazards', 'Data Forwarding Unit')

# Forwarding diagram using shapes
add_card(s, 0.6, 1.5, 6.0, 3.5)
tf = add_textbox(s, 0.8, 1.55, 5.6, 0.3)
add_text(tf, 'Forwarding Paths', size=14, color=ACCENT, bold=True)

fw_stages = [('ID', ACCENT2, 1.2), ('EX', GREEN, 2.6), ('MEM', ORANGE, 4.0), ('WB', RED, 5.4)]
for name, color, x in fw_stages:
    box = add_rect(s, x, 2.4, 1.0, 0.6, fill=BG_CARD, line_color=color, line_width=2)
    tf_b = box.text_frame
    p = tf_b.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    p.space_before = Pt(6)
    r = p.add_run()
    r.text = name
    r.font.size = Pt(14)
    r.font.color.rgb = color
    r.font.bold = True

# FWD MUX box
box = add_rect(s, 2.6, 3.3, 1.0, 0.4, fill=RGBColor(0x14, 0x1E, 0x30), line_color=ACCENT, line_width=1)
tf_b = box.text_frame
p = tf_b.paragraphs[0]
p.alignment = PP_ALIGN.CENTER
r = p.add_run()
r.text = 'FWD MUX'
r.font.size = Pt(8)
r.font.color.rgb = ACCENT
r.font.bold = True

tf2 = add_textbox(s, 1.0, 3.9, 5.2, 0.9)
add_text(tf2, '\u2190 EX/MEM Forward (1-gap, 0 penalty)', size=10, color=GREEN, bold=True)
add_text(tf2, '\u2190 MEM/WB Forward (2-gap, 0 penalty)', size=10, color=ORANGE, bold=True)

# Code
add_card(s, 6.9, 1.5, 5.8, 2.2)
tf = add_textbox(s, 7.1, 1.55, 5.4, 0.3)
add_text(tf, 'Forwarding Control Logic', size=14, color=ACCENT, bold=True)
add_code_block(s, 7.1, 1.95, 5.4, 1.6,
    '// Forward A (ALU src1)\nassign forward_a =\n'
    '  // EX/MEM hazard (1-gap)\n'
    '  (ex_mem_reg_write && ex_mem_rd != 0\n'
    '   && ex_mem_rd == id_ex_rs1) ? 2\'b10 :\n'
    '  // MEM/WB hazard (2-gap)\n'
    '  (mem_wb_reg_write && mem_wb_rd != 0\n'
    '   && mem_wb_rd == id_ex_rs1) ? 2\'b01 :\n'
    '  2\'b00; // No hazard')

add_card(s, 6.9, 3.9, 5.8, 1.8)
tf = add_textbox(s, 7.1, 3.95, 5.4, 0.3)
add_text(tf, 'Write-Through Bypass (3-gap Bug Fix)', size=14, color=ACCENT, bold=True)
add_code_block(s, 7.1, 4.35, 5.4, 1.0,
    '// In regfile.v - handles WB->ID same cycle\nassign rd1 =\n'
    '  (a1 == 0)                       ? 32\'b0 :\n'
    '  (we3 && a3 == a1 && a3 != 5\'b0) ? wd3   :\n'
    '                                    rf[a1];')
tf3 = add_textbox(s, 7.1, 5.45, 5.4, 0.3)
add_text(tf3, 'Bug fix: without this, 3-instruction gap reads stale data.', size=10, color=DIM)

add_highlight_box(s, 0.6, 5.2, 6.0, 0.6,
    'Forwarding eliminates 100% of data stalls on Fibonacci benchmark. Every RAW dependency resolved with zero penalty.', accent=GREEN)


# ════════════════════════════════════════════════
#  SLIDE 10: STALL & FLUSH
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Hazards', 'Load-Use Stalls & Branch Flushes')

add_card(s, 0.6, 1.5, 6.0, 2.3)
tf = add_textbox(s, 0.8, 1.55, 5.6, 0.3)
add_text(tf, 'Load-Use Stall Mechanism', size=14, color=ACCENT, bold=True)
add_code_block(s, 0.8, 1.95, 5.6, 1.7,
    '// Detect load-use hazard\nwire load_use_hazard =\n'
    '  id_ex_result_src == 2\'b01   // load in EX\n'
    '  && (id_ex_rd == if_id_rs1\n'
    '   || id_ex_rd == if_id_rs2)\n'
    '  && id_ex_rd != 0;\n\n'
    '// Stall action:\n'
    '// 1. Freeze PC    (don\'t fetch next)\n'
    '// 2. Hold IF/ID   (re-decode same instr)\n'
    '// 3. Insert NOP in ID/EX (bubble)')

add_card(s, 6.9, 1.5, 5.8, 2.3)
tf = add_textbox(s, 7.1, 1.55, 5.4, 0.3)
add_text(tf, 'Branch Flush Mechanism', size=14, color=ACCENT, bold=True)
add_code_block(s, 7.1, 1.95, 5.4, 1.7,
    '// Branch resolved in EX stage\nwire branch_taken =\n'
    '  (id_ex_branch && alu_zero)  // BEQ\n'
    '  || id_ex_jump               // JAL\n'
    '  || id_ex_jalr;              // JALR\n\n'
    'wire flush = branch_taken;\n\n'
    '// Flush action:\n'
    '// 1. Zero out IF/ID register (NOP)\n'
    '// 2. Zero out ID/EX register (NOP)\n'
    '// 3. Redirect PC to branch target')

# Stall timing
add_card(s, 0.6, 4.0, 6.0, 1.8)
tf = add_textbox(s, 0.8, 4.05, 5.6, 0.3)
add_text(tf, 'Stall Timing', size=13, color=ACCENT, bold=True)
stall_data = [
    [('', DIM), ('1', DIM, True), ('2', DIM, True), ('3', DIM, True), ('4', DIM, True), ('5', DIM, True), ('6', DIM, True), ('7', DIM, True)],
    [('LW x6,0(x0)', DIM), ('IF', ACCENT), ('ID', ACCENT2), ('EX', GREEN), ('MEM', ORANGE), ('WB', RED), ('', DIM), ('', DIM)],
    [('ADDI x7,x6,1', DIM), ('', DIM), ('IF', ACCENT), ('ID', ACCENT2), ('stall', RED), ('EX', GREEN), ('MEM', ORANGE), ('WB', RED)],
]
add_table(s, 0.8, 4.4, 5.6, 1.0, 3, 8, stall_data, col_widths=[1.4]+[0.6]*7)

# Flush timing
add_card(s, 6.9, 4.0, 5.8, 1.8)
tf = add_textbox(s, 7.1, 4.05, 5.4, 0.3)
add_text(tf, 'Flush Timing', size=13, color=ACCENT, bold=True)
flush_data = [
    [('', DIM), ('1', DIM, True), ('2', DIM, True), ('3', DIM, True), ('4', DIM, True), ('5', DIM, True), ('6', DIM, True), ('7', DIM, True)],
    [('BEQ x1,x2,T', DIM), ('IF', ACCENT), ('ID', ACCENT2), ('EX', GREEN), ('MEM', ORANGE), ('WB', RED), ('', DIM), ('', DIM)],
    [('PC+4 (wrong)', DIM), ('', DIM), ('IF', ACCENT), ('flush', ORANGE), ('', DIM), ('', DIM), ('', DIM), ('', DIM)],
    [('Target instr', DIM), ('', DIM), ('', DIM), ('', DIM), ('IF', ACCENT), ('ID', ACCENT2), ('EX', GREEN), ('MEM', ORANGE)],
]
add_table(s, 7.1, 4.4, 5.4, 1.15, 4, 8, flush_data, col_widths=[1.4]+[0.57]*7)

add_highlight_box(s, 0.6, 6.0, 6.0, 0.6,
    'After stall, data forwarded from MEM/WB to EX (cost: 1 cycle)', accent=ORANGE)
add_highlight_box(s, 6.9, 6.0, 5.8, 0.6,
    '2 wasted cycles per taken branch (fetched instructions are flushed)', accent=ORANGE)


# ════════════════════════════════════════════════
#  SLIDE 11: PERFORMANCE COUNTERS
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Instrumentation', 'Performance Counters & Halt Detection')

data = [
    [('Counter', ACCENT, True), ('What It Measures', ACCENT, True), ('How', ACCENT, True)],
    [('perf_cycles', ACCENT), ('Total clock cycles elapsed', DIM), ('Increments every posedge clk', DIM)],
    [('perf_instrs', GREEN), ('Retired (completed) instructions', DIM), ('Counts when mem_wb_valid == 1', DIM)],
    [('perf_stalls', ORANGE), ('Load-use hazard stall cycles', DIM), ('Counts when stall signal asserted', DIM)],
    [('perf_flushes', RED), ('Branch/jump flush events', DIM), ('Counts when flush signal asserted', DIM)],
]
add_table(s, 0.6, 1.5, 7.0, 2.0, 5, 3, data, col_widths=[2.0, 2.8, 2.2])

add_card(s, 0.6, 3.7, 7.0, 1.5)
tf = add_textbox(s, 0.8, 3.75, 6.6, 0.3)
add_text(tf, 'Derived Metrics', size=14, color=ACCENT, bold=True)
tf2 = add_textbox(s, 0.8, 4.1, 6.6, 1.0)
add_text(tf2, 'CPI = perf_cycles / perf_instrs', size=12, color=DIM, font_name='Consolas')
add_text(tf2, 'Stall Rate = perf_stalls / perf_cycles x 100%', size=12, color=DIM, font_name='Consolas')
add_text(tf2, 'Flush Rate = perf_flushes / perf_cycles x 100%', size=12, color=DIM, font_name='Consolas')
add_text(tf2, 'Speedup = N / CPI  (vs single-cycle)', size=12, color=DIM, font_name='Consolas')

add_card(s, 8.0, 1.5, 4.7, 2.0)
tf = add_textbox(s, 8.2, 1.55, 4.3, 0.3)
add_text(tf, 'Valid Bit Propagation', size=14, color=ACCENT, bold=True)
add_code_block(s, 8.2, 1.95, 4.3, 1.4,
    '// Valid bit pipeline\nreg id_ex_valid, ex_mem_valid,\n    mem_wb_valid;\n\n'
    '// Count only when instr reaches WB\n'
    'if (mem_wb_valid && !halted)\n'
    '  perf_instrs <= perf_instrs + 1;')

add_card(s, 8.0, 3.7, 4.7, 1.5)
tf = add_textbox(s, 8.2, 3.75, 4.3, 0.3)
add_text(tf, 'Halt Detection', size=14, color=ACCENT, bold=True)
add_code_block(s, 8.2, 4.15, 4.3, 0.9,
    '// Detect jal x0, 0 (self-loop)\n'
    'wire halt_instr =\n'
    '  opcode == JAL && rd == x0\n'
    '  && offset == 0;\n'
    '// Freezes all counters on halt')

add_highlight_box(s, 0.6, 5.4, 12.1, 0.6,
    'Programs end with "jal x0, 0" to halt cleanly. Counters freeze so results reflect only program execution, not idle time.', accent=GREEN)


# ════════════════════════════════════════════════
#  SLIDE 12: BENCHMARKS
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Testing', 'Benchmark Programs & Verification')

add_card(s, 0.6, 1.5, 6.0, 2.5)
tf = add_textbox(s, 0.8, 1.55, 5.6, 0.3)
add_text(tf, 'Fibonacci Benchmark (benchmark.hex)', size=14, color=ACCENT, bold=True)
tf2 = add_textbox(s, 0.8, 1.9, 5.6, 0.5)
add_text(tf2, 'Iterative computation of F(0)...F(9), stores all 10 values to data memory.', size=11, color=DIM)
add_code_block(s, 0.8, 2.5, 5.6, 1.3,
    'a=0; b=1; mem[0]=a; mem[4]=b;\nfor (i=2; i<10; i++) {\n'
    '  temp = a + b;\n'
    '  mem[i*4] = temp;\n'
    '  a = b; b = temp;\n'
    '}\nhalt;  // jal x0, 0')

# Fibonacci results table
fib_data = [
    [('Address', ACCENT, True), ('Value', ACCENT, True), ('Fib', ACCENT, True)],
    [('mem[0]', DIM), ('0', GREEN), ('F(0)', DIM)],
    [('mem[1]', DIM), ('1', GREEN), ('F(1)', DIM)],
    [('mem[2]', DIM), ('1', GREEN), ('F(2)', DIM)],
    [('mem[3]', DIM), ('2', GREEN), ('F(3)', DIM)],
    [('mem[4]', DIM), ('3', GREEN), ('F(4)', DIM)],
    [('mem[5]', DIM), ('5', GREEN), ('F(5)', DIM)],
    [('mem[6]', DIM), ('8', GREEN), ('F(6)', DIM)],
    [('mem[7]', DIM), ('13', GREEN), ('F(7)', DIM)],
    [('mem[8]', DIM), ('21', GREEN), ('F(8)', DIM)],
    [('mem[9]', DIM), ('34', GREEN), ('F(9)', DIM)],
]
add_table(s, 0.6, 4.2, 3.2, 3.0, 11, 3, fib_data, col_widths=[1.1, 1.0, 1.1])

# Hazard test
add_card(s, 6.9, 1.5, 5.8, 2.5)
tf = add_textbox(s, 7.1, 1.55, 5.4, 0.3)
add_text(tf, 'Pipeline Hazard Test (program.hex)', size=14, color=ACCENT, bold=True)
test_data = [
    [('Test', ACCENT, True), ('Scenario', ACCENT, True), ('Result', ACCENT, True)],
    [('1', DIM), ('EX/MEM forwarding (back-to-back)', DIM), ('PASS', GREEN, True)],
    [('2', DIM), ('MEM/WB forwarding (2-gap)', DIM), ('PASS', GREEN, True)],
    [('3', DIM), ('Load-use hazard (stall+fwd)', DIM), ('PASS', GREEN, True)],
    [('4', DIM), ('R-type forwarding chain', DIM), ('PASS', GREEN, True)],
    [('5', DIM), ('Store with forwarded data', DIM), ('PASS', GREEN, True)],
    [('6', DIM), ('Branch with forwarding', DIM), ('PASS', GREEN, True)],
]
add_table(s, 6.9, 1.95, 5.8, 2.0, 7, 3, test_data, col_widths=[0.6, 3.6, 1.6])

# Unit tests
add_card(s, 6.9, 4.2, 5.8, 1.7)
tf = add_textbox(s, 7.1, 4.25, 5.4, 0.3)
add_text(tf, 'Unit Tests', size=14, color=ACCENT, bold=True)
unit_data = [
    [('Testbench', ACCENT, True), ('Tests', ACCENT, True), ('Status', ACCENT, True)],
    [('alu_tb.v', DIM), ('ADD, AND, SUB + zero flag', DIM), ('PASS', GREEN, True)],
    [('regfile_tb.v', DIM), ('Write, read, x0 hardwired', DIM), ('PASS', GREEN, True)],
    [('top_tb.v', DIM), ('Full pipeline (35 instrs)', DIM), ('PASS', GREEN, True)],
    [('benchmark_tb.v', DIM), ('Fibonacci (64 instrs)', DIM), ('PASS', GREEN, True)],
    [('crypto_tb.v', DIM), ('ChaCha20 SW vs HW', DIM), ('PASS', GREEN, True)],
]
add_table(s, 7.1, 4.6, 5.4, 1.2, 6, 3, unit_data, col_widths=[1.6, 2.4, 1.4])

add_highlight_box(s, 4.0, 5.0, 2.7, 0.6,
    'Exercises: back-to-back deps, forwarding paths, branches, memory ops.', accent=GREEN)


# ════════════════════════════════════════════════
#  SLIDE 13: PERFORMANCE RESULTS
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Results', 'Performance Results')

add_metric_card(s, 0.6, 1.5, '1.14', 'CPI (Fibonacci)', ACCENT)
add_metric_card(s, 3.55, 1.5, '0', 'Stall Cycles', ACCENT2)
add_metric_card(s, 6.5, 1.5, '9.9%', 'Flush Overhead', ORANGE)
add_metric_card(s, 9.45, 1.5, '4.4x', 'Throughput Gain', GREEN)

# Fibonacci table
fib_perf_data = [
    [('Metric', ACCENT, True), ('Single-Cycle', ACCENT, True), ('5-Stage Pipeline', ACCENT, True)],
    [('Clock Cycles', DIM), ('71', DIM), ('81', TEXT, True)],
    [('Instructions Retired', DIM), ('71', DIM), ('71', TEXT, True)],
    [('CPI', DIM), ('1.00', DIM), ('1.14', GREEN, True)],
    [('Stall Cycles', DIM), ('0', DIM), ('0', GREEN, True)],
    [('Flush Cycles', DIM), ('0', DIM), ('8', ORANGE, True)],
    [('Flush Rate', DIM), ('0%', DIM), ('9.9%', ORANGE, True)],
    [('Max Clock Freq', DIM), ('1/Tcrit', DIM), ('~5/Tcrit', GREEN, True)],
    [('Effective Throughput', DIM), ('1x', DIM), ('~4.4x', GREEN, True)],
]
add_table(s, 0.6, 3.0, 6.2, 3.0, 9, 3, fib_perf_data, col_widths=[2.0, 2.1, 2.1])

# Hazard test table
haz_perf_data = [
    [('Metric', ACCENT, True), ('Value', ACCENT, True)],
    [('Clock Cycles', DIM), ('60', TEXT, True)],
    [('Instructions Retired', DIM), ('55', TEXT, True)],
    [('CPI', DIM), ('1.09', GREEN, True)],
    [('Stall Cycles', DIM), ('1', ORANGE, True)],
    [('Flush Cycles', DIM), ('1', ORANGE, True)],
    [('Stall Rate', DIM), ('1.67%', DIM)],
    [('Flush Rate', DIM), ('1.67%', DIM)],
]
add_table(s, 7.1, 3.0, 5.5, 2.7, 8, 2, haz_perf_data, col_widths=[2.7, 2.8])

add_highlight_box(s, 7.1, 5.9, 5.5, 0.7,
    'Even with deliberate hazard-heavy code, CPI stays at 1.09 thanks to the forwarding unit.', accent=GREEN)


# ════════════════════════════════════════════════
#  SLIDE 14: QUANTITATIVE ANALYSIS
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Analysis', 'Quantitative Analysis & Comparison')

add_card(s, 0.6, 1.5, 6.0, 2.5)
tf = add_textbox(s, 0.8, 1.55, 5.6, 0.3)
add_text(tf, 'CPI Breakdown \u2014 Fibonacci', size=14, color=ACCENT, bold=True)
cpi_data = [
    [('Component', ACCENT, True), ('Contribution to CPI', ACCENT, True)],
    [('Base CPI (ideal pipeline)', DIM), ('+1.000', GREEN, True)],
    [('Load-use stall penalty', DIM), ('+0.000', GREEN, True)],
    [('Branch flush penalty', DIM), ('+0.113', ORANGE, True)],
    [('Pipeline fill/drain', DIM), ('+0.028', DIM)],
    [('Measured CPI', TEXT, True), ('1.141', GREEN, True)],
]
add_table(s, 0.8, 1.95, 5.6, 1.9, 6, 2, cpi_data, col_widths=[3.2, 2.4])

add_card(s, 6.9, 1.5, 5.8, 2.5)
tf = add_textbox(s, 7.1, 1.55, 5.4, 0.3)
add_text(tf, 'Cycle Breakdown \u2014 Fibonacci (81 cycles)', size=14, color=ACCENT, bold=True)
tf2 = add_textbox(s, 7.1, 1.95, 5.4, 2.0)
add_text(tf2, 'Useful work:        71 cycles (87.7%)', size=12, color=GREEN, font_name='Consolas', bold=True)
add_text(tf2, 'Branch flushes:      8 cycles ( 9.9%)', size=12, color=ORANGE, font_name='Consolas', bold=True)
add_text(tf2, 'Pipeline fill/drain: 2 cycles ( 2.5%)', size=12, color=ACCENT2, font_name='Consolas')
add_text(tf2, 'Load-use stalls:     0 cycles ( 0.0%)', size=12, color=DIM, font_name='Consolas')

# Forwarding effectiveness
add_card(s, 0.6, 4.2, 6.0, 1.5)
tf = add_textbox(s, 0.8, 4.25, 5.6, 0.3)
add_text(tf, 'Forwarding Effectiveness', size=14, color=ACCENT, bold=True)
tf2 = add_textbox(s, 0.8, 4.6, 5.6, 1.0)
add_text(tf2, 'With forwarding:      CPI = 1.14', size=13, color=GREEN, font_name='Consolas', bold=True)
add_text(tf2, 'Without forwarding:   CPI = 1.6 - 2.0 (est.)', size=13, color=RED, font_name='Consolas', bold=True)

add_highlight_box(s, 0.6, 5.9, 6.0, 0.8,
    'Forwarding eliminates 100% of data stalls on Fibonacci. Every RAW dependency resolved by EX/MEM, MEM/WB, or write-through with zero penalty.', accent=GREEN)

# Throughput table
tput_data = [
    [('Architecture', ACCENT, True), ('Clock Period', ACCENT, True), ('CPI', ACCENT, True), ('Throughput', ACCENT, True)],
    [('Single-Cycle', DIM), ('Tcrit', DIM), ('1.00', DIM), ('1/Tcrit', DIM)],
    [('Pipeline (ours)', DIM), ('Tcrit/5', GREEN), ('1.14', DIM), ('4.39/Tcrit', GREEN, True)],
    [('Pipeline (no fwd)', DIM), ('Tcrit/5', DIM), ('~1.8', ORANGE), ('~2.78/Tcrit', DIM)],
]
add_table(s, 6.9, 4.2, 5.8, 1.4, 4, 4, tput_data, col_widths=[1.8, 1.2, 0.8, 2.0])

add_highlight_box(s, 6.9, 5.9, 5.8, 0.8,
    'Throughput = IPC x f_clk = (1/1.14) x 5f = 4.39f\nSpeedup: 4.39x over single-cycle | Efficiency: 87.7%', accent=ACCENT)


# ════════════════════════════════════════════════
#  SLIDE 15: CHACHA20 ISA EXTENSION
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'ISA Extension', 'Custom ROL Instruction \u2014 ChaCha20 Quarter-Round')

add_card(s, 0.6, 1.5, 5.8, 2.0)
tf = add_textbox(s, 0.8, 1.55, 5.4, 0.3)
add_text(tf, 'What is ChaCha20?', size=14, color=ACCENT, bold=True)
tf2 = add_textbox(s, 0.8, 1.9, 5.4, 1.4)
add_bullet_list(tf2, [
    'Stream cipher: used in TLS 1.3, WireGuard, SSH, Android encryption',
    'Core op: quarter-round \u2014 built from ADD, XOR, Rotate-Left',
    'Standard RV32I has no rotate \u2014 emulate with 3 instructions',
    'RISC-V Zbkb extension adds ROL/ROR for this reason',
], size=11)

add_card(s, 0.6, 3.7, 5.8, 2.0)
tf = add_textbox(s, 0.8, 3.75, 5.4, 0.3)
add_text(tf, 'Our Custom Instruction', size=14, color=ACCENT, bold=True)
add_code_block(s, 0.8, 4.15, 5.4, 1.4,
    '// Added to alu.v\n'
    '4\'b1010: result =\n'
    '  (src1 << src2[4:0]) |\n'
    '  (src1 >> (32 - src2[4:0])); // ROL\n\n'
    '// control.v: custom-0 opcode (0001011)\n'
    '// R-type format, uses existing pipeline')

# Quarter-round algorithm
add_card(s, 6.7, 1.5, 6.0, 1.7)
tf = add_textbox(s, 6.9, 1.55, 5.6, 0.3)
add_text(tf, 'ChaCha20 Quarter-Round Algorithm', size=14, color=ACCENT, bold=True)
add_code_block(s, 6.9, 1.95, 5.6, 1.15,
    '// Input:  a=0x61  b=0x62  c=0x63  d=0x64\n'
    '// Repeat 4 rounds of:\n'
    'a += b;  d ^= a;  d <<<= 16;\n'
    'c += d;  b ^= c;  b <<<= 12;\n'
    'a += b;  d ^= a;  d <<<=  8;\n'
    'c += d;  b ^= c;  b <<<=  7;')

# Round trace table
add_card(s, 6.7, 3.4, 6.0, 2.3)
tf = add_textbox(s, 6.9, 3.45, 5.6, 0.3)
add_text(tf, 'Round-by-Round Trace', size=14, color=ACCENT, bold=True)
trace_data = [
    [('', ACCENT, True), ('a', ACCENT, True), ('b', ACCENT, True), ('c', ACCENT, True), ('d', ACCENT, True)],
    [('Input', ACCENT), ('00000061', DIM), ('00000062', DIM), ('00000063', DIM), ('00000064', DIM)],
    [('Round 1', GREEN), ('700010CD', DIM), ('DBEEECEB', DIM), ('A7B7CDD3', DIM), ('A710CD70', DIM)],
    [('Round 2', ORANGE), ('31529DEE', DIM), ('C935724B', DIM), ('72F1CAD2', DIM), ('9A711001', DIM)],
    [('Round 3', PINK), ('F0201BDA', DIM), ('1EA20D3F', DIM), ('8BA54FBB', DIM), ('187B23F0', DIM)],
    [('Round 4', RED), ('D576E19B', GREEN, True), ('1898E8F8', GREEN, True), ('36858953', GREEN, True), ('9FF722DF', GREEN, True)],
]
add_table(s, 6.9, 3.8, 5.6, 1.8, 6, 5, trace_data, col_widths=[1.0, 1.15, 1.15, 1.15, 1.15])

# SW vs HW code comparison
add_card(s, 0.6, 5.9, 5.8, 1.3)
tf = add_textbox(s, 0.8, 5.95, 2.5, 0.3)
add_text(tf, 'Standard RV32I (3 instrs):', size=11, color=ORANGE, bold=True)
add_code_block(s, 0.8, 6.3, 2.5, 0.8,
    'SLLI x5, x4, 16  // d<<16\nSRLI x6, x4, 16  // d>>16\nOR   x4, x5, x6  // combine')

tf = add_textbox(s, 3.5, 5.95, 2.8, 0.3)
add_text(tf, 'With Custom ROL (1 instr):', size=11, color=GREEN, bold=True)
add_code_block(s, 3.5, 6.3, 2.8, 0.8,
    'ROL  x4, x4, x12 // done!\n// x12 holds 16\n// 1 instruction, 1 cycle')

add_highlight_box(s, 6.7, 5.9, 6.0, 0.5,
    'Both versions produce identical output \u2014 verified in simulation.', accent=GREEN)


# ════════════════════════════════════════════════
#  SLIDE 16: CRYPTO BENCHMARK RESULTS
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'ISA Extension', 'Crypto Benchmark: Software vs Hardware \u2014 Results')

add_metric_card(s, 0.6, 1.5, '1.35x', 'Speedup', ACCENT)
add_metric_card(s, 3.55, 1.5, '26%', 'Fewer Cycles', ACCENT2)
add_metric_card(s, 6.5, 1.5, '28', 'Instrs Saved', GREEN)
add_metric_card(s, 9.45, 1.5, '36%', 'Code Reduction', ORANGE)

# Comparison table
comp_data = [
    [('Metric', ACCENT, True), ('Software (RV32I)', ACCENT, True), ('Hardware (+ROL)', ACCENT, True), ('Delta', ACCENT, True)],
    [('Clock Cycles', DIM), ('107', TEXT, True), ('79', GREEN, True), ('-28 (26%)', GREEN, True)],
    [('Instructions Retired', DIM), ('101', TEXT, True), ('73', GREEN, True), ('-28 (28%)', GREEN, True)],
    [('Loop Body Size', DIM), ('22 instrs', TEXT, True), ('14 instrs', GREEN, True), ('-8 per iter', GREEN)],
    [('Stalls', DIM), ('0', DIM), ('0', DIM), ('\u2014', DIM)],
    [('Flushes', DIM), ('4', DIM), ('4', DIM), ('\u2014', DIM)],
    [('CPI', DIM), ('1.059', DIM), ('1.082', DIM), ('\u2014', DIM)],
    [('Output (a)', DIM), ('0xD576E19B', DIM), ('0xD576E19B', GREEN), ('match', GREEN, True)],
    [('Output (b)', DIM), ('0x1898E8F8', DIM), ('0x1898E8F8', GREEN), ('match', GREEN, True)],
    [('Output (c)', DIM), ('0x36858953', DIM), ('0x36858953', GREEN), ('match', GREEN, True)],
    [('Output (d)', DIM), ('0x9FF722DF', DIM), ('0x9FF722DF', GREEN), ('match', GREEN, True)],
]
add_table(s, 0.6, 2.9, 7.0, 3.5, 11, 4, comp_data, col_widths=[1.6, 1.7, 1.7, 2.0])

# Real-world impact
add_card(s, 7.9, 2.9, 4.8, 2.4)
tf = add_textbox(s, 8.1, 2.95, 4.4, 0.3)
add_text(tf, 'Real-World Impact', size=14, color=ACCENT, bold=True)
tf2 = add_textbox(s, 8.1, 3.3, 4.4, 1.8)
add_bullet_list(tf2, [
    'IoT devices: encrypt sensor data without draining battery',
    'Secure boot: verify firmware signatures faster at startup',
    'TLS 1.3: ChaCha20-Poly1305 is the default cipher for mobile',
    '26% fewer cycles = proportionally lower energy per packet',
], size=11)

add_highlight_box(s, 7.9, 5.5, 4.8, 0.9,
    'Hardware cost: 1 extra ALU case (1 line of Verilog) + 1 opcode decode entry. Minimal area overhead for 1.35x crypto speedup.', accent=GREEN)

add_highlight_box(s, 0.6, 6.6, 12.1, 0.5,
    'VERIFIED: Both software and hardware versions produce identical ciphertext output. Custom ROL is fully compatible with existing pipeline & forwarding.', accent=ACCENT)


# ════════════════════════════════════════════════
#  SLIDE 17: CONCLUSION
# ════════════════════════════════════════════════
s = add_slide()
slide_header(s, 'Conclusion', 'Summary & Future Work')

conclusions = [
    ('What We Built', ACCENT, [
        'Complete RV32I processor with 37 + 1 custom instruction',
        '5-stage pipeline (IF/ID/EX/MEM/WB) in Verilog',
        '9 hardware modules, 675 lines of synthesizable RTL',
        'Full forwarding unit with 3 bypass paths',
        'Custom ROL instruction for crypto acceleration',
        '5 testbenches with comprehensive verification',
    ]),
    ('Key Results', GREEN, [
        'CPI = 1.14 on Fibonacci (close to ideal 1.0)',
        '4.4x throughput over single-cycle baseline',
        '0 data stalls \u2014 forwarding handles all RAW hazards',
        '87.7% pipeline efficiency',
        '1.35x crypto speedup with custom ROL instruction',
        '26% cycle reduction on ChaCha20 quarter-round',
    ]),
    ('Key Takeaways', ORANGE, [
        'Forwarding is essential \u2014 without it CPI would be 1.6-2.0x',
        'Branch penalties are the dominant overhead',
        'Performance counters are critical for analysis',
        'Custom ISA extensions give measurable speedup',
    ]),
    ('Future Enhancements', ACCENT2, [
        'Branch predictor \u2014 reduce 2-cycle penalty',
        'Cache hierarchy \u2014 L1 I-cache + D-cache',
        'RV32M extension \u2014 multiply/divide',
        'More Zbkb crypto ops \u2014 ROR, ANDN, pack',
        'FPGA synthesis \u2014 deploy on real hardware',
        'Full ChaCha20 block \u2014 20 rounds, 256-bit key',
    ]),
]

for i, (title, color, items) in enumerate(conclusions):
    col = i % 2
    row = i // 2
    x = 0.6 + col * 6.35
    y = 1.5 + row * 2.7
    card = add_card(s, x, y, 6.0, 2.5)
    tf = card.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.space_before = Pt(6)
    r = p.add_run()
    r.text = title
    r.font.size = Pt(14)
    r.font.color.rgb = color
    r.font.bold = True
    r.font.name = 'Calibri'
    for item in items:
        p2 = tf.add_paragraph()
        p2.space_after = Pt(1)
        r2 = p2.add_run()
        r2.text = '  \u2022  ' + item
        r2.font.size = Pt(11)
        r2.font.color.rgb = DIM
        r2.font.name = 'Calibri'

# Thank you
tf = add_textbox(s, 3.0, 6.8, 7.3, 0.6)
add_text(tf, 'Thank You', size=22, color=ACCENT, bold=True, alignment=PP_ALIGN.CENTER)
p = tf.add_paragraph()
p.alignment = PP_ALIGN.CENTER
r = p.add_run()
r.text = 'Adesh Pandey \u00b7 Aayush Gelal \u00b7 Bishesh Paudel  |  Pulchowk Campus \u00b7 2026'
r.font.size = Pt(11)
r.font.color.rgb = DIM
r.font.name = 'Calibri'


# ════════════════════════════════════════════════
#  SAVE
# ════════════════════════════════════════════════
output = 'presentation.pptx'
prs.save(output)
print(f'Saved {output} ({len(prs.slides)} slides)')

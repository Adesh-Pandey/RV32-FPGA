#!/usr/bin/env python3
"""Upload a RISC-V program to the Zybo RV32 SoC over UART.

The FPGA's bootloader (see src/bootloader.v) holds the CPU in reset until
a program has been received. This script parses a .hex file (one 32-bit
word per non-comment line, in hex) and pushes it across the serial link.

Wire protocol (host -> FPGA):
    bytes [0..3]: magic 'R','V','3','2'  (0x52, 0x56, 0x33, 0x32)
    byte  [4]   : length N in 32-bit words (1..255)
    bytes [5..] : N program words, each 4 bytes little-endian

Wire protocol (FPGA -> host):
    after each word stored: 0xA5
    after the final word:   0x5A   (then CPU reset is released)

Usage:
    python load_program.py <serial_port> <hex_file>

Example:
    python load_program.py /dev/cu.usbserial-XXXX ../src/uart_letter_custom.hex
    python load_program.py COM5 ..\\src\\uart_letter_custom.hex
"""

import struct
import sys

try:
    import serial
except ImportError:
    sys.exit("pyserial is required: pip install pyserial")


MAGIC = b"RV32"          # 0x52 0x56 0x33 0x32, sent in order
ACK_WORD = 0xA5
ACK_DONE = 0x5A
BAUD = 115200
IMEM_MAX_WORDS = 255     # length field is 1 byte and 0 is a no-op


def parse_hex(path):
    """Parse a hex file. Each non-comment line is one 32-bit instruction."""
    words = []
    with open(path) as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.split("//")[0].strip()
            if not line:
                continue
            try:
                w = int(line, 16)
            except ValueError:
                raise SystemExit(f"{path}:{lineno}: cannot parse '{line}'")
            if w < 0 or w > 0xFFFFFFFF:
                raise SystemExit(f"{path}:{lineno}: value out of 32-bit range")
            words.append(w)
    return words


def read_exact(ser, n, label):
    data = ser.read(n)
    if len(data) != n:
        sys.exit(f"timeout: expected {n} byte(s) for {label}, got {len(data)}")
    return data


def load(port, hex_path):
    words = parse_hex(hex_path)
    if not words:
        sys.exit(f"{hex_path} is empty")
    if len(words) > IMEM_MAX_WORDS:
        sys.exit(f"program is {len(words)} words; max is {IMEM_MAX_WORDS}")

    print(f"Opening {port} at {BAUD} 8N1 ...")
    with serial.Serial(
        port,
        baudrate=BAUD,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=3,
    ) as ser:
        ser.reset_input_buffer()
        ser.reset_output_buffer()

        # Header: magic + length
        ser.write(MAGIC + bytes([len(words)]))
        print(f"Sent header: magic + length={len(words)}")

        # Stream words, verifying ack after each one
        for i, w in enumerate(words):
            ser.write(struct.pack("<I", w))
            ack = read_exact(ser, 1, f"ack for word {i}")[0]
            if ack != ACK_WORD:
                sys.exit(
                    f"word {i}: expected ack 0x{ACK_WORD:02X}, got 0x{ack:02X}"
                )

        # Final ack
        final = read_exact(ser, 1, "final ack")[0]
        if final != ACK_DONE:
            sys.exit(
                f"final ack: expected 0x{ACK_DONE:02X}, got 0x{final:02X}"
            )

        print(f"OK: loaded {len(words)} word(s). CPU is now running.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"usage: {sys.argv[0]} <serial_port> <hex_file>")
    load(sys.argv[1], sys.argv[2])

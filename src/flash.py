import serial
import sys
import time

# --- CONFIGURE THESE ---
COM_PORT = 'COM5' # Change to your Pmod UART COM port
BAUD = 115200
HEX_FILE = 'uart_letter_custom.hex' # The code you want to flash

def main():
    words = []
    words = []
    with open(HEX_FILE, 'r') as f:
        for line in f:
            # Split the line at '//' and only keep the first part
            clean_line = line.split('//')[0].strip()
            
            # If the line is empty after stripping comments, skip it
            if not clean_line: 
                continue
                
            # Convert the clean hex string to an integer
            words.append(int(clean_line, 16))
    if len(words) > 255:
        print("Error: Loader only supports up to 255 words (1KB).")
        sys.exit(1)

    print(f"Connecting to {COM_PORT}...")
    try:
        # Use 8N1 standard to match our hardware fix!
        ser = serial.Serial(COM_PORT, BAUD, timeout=2)
    except Exception as e:
        print(f"Failed to open port: {e}")
        sys.exit(1)

    time.sleep(0.5)

    print(f"Flashing {len(words)} words...")
    # Send Magic Header 'RV32' + Length
    ser.write(b'RV32')
    ser.write(bytes([len(words)]))

    for i, w in enumerate(words):
        # Little Endian Byte Packing
        ser.write(bytes([
            w & 0xFF,
            (w >> 8) & 0xFF,
            (w >> 16) & 0xFF,
            (w >> 24) & 0xFF
        ]))

        # Wait for the FPGA's hardware 0xA5 ACK
        ack = ser.read(1)
        if ack != b'\xA5':
            print(f"\nError: Bad ACK at word {i}: {ack}")
            sys.exit(1)
        print(".", end="", flush=True)

    final_ack = ser.read(1)
    if final_ack == b'\x5A':
        print("\n[SUCCESS] Flash Complete! RISC-V CPU is booting...")
    else:
        print("\n[WARNING] Missing final boot ACK.")

    ser.close()

if __name__ == '__main__':
    main()
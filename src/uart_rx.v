module uart_rx (
    input wire clk,           // 125 MHz system clock
    input wire reset,         // Active high reset
    input wire rx_pin,        // The physical wire coming from the Pmod FTDI
    output reg [7:0] rx_data, // Received character (bits[6:0] = data, bit[7] = 0)
    output reg rx_done        // Pulses high for 1 clock cycle when a byte is fully received
);

    // 125,000,000 Hz / 115200 Baud = 1085 clock cycles per bit
    parameter CLKS_PER_BIT = 1085;

    // Frame: 1 start + 7 data + 1 parity (consumed, not checked) + 1 stop
    reg [3:0] state;
    reg [11:0] clock_count;
    reg [2:0] bit_index;

    localparam IDLE   = 4'd0;
    localparam START  = 4'd1;
    localparam DATA   = 4'd2;
    localparam PARITY = 4'd3;
    localparam STOP   = 4'd4;

    always @(posedge clk) begin
        if (reset) begin
            rx_done <= 1'b0;
            state   <= IDLE;
            rx_data <= 8'd0;
        end else begin
            rx_done <= 1'b0; // Default to zero unless byte is finished

            case (state)
                IDLE: begin
                    clock_count <= 0;
                    bit_index   <= 0;
                    if (rx_pin == 1'b0) begin // Detect Start bit (drop to Low)
                        state <= START;
                    end
                end

                START: begin
                    // Wait half a bit duration to sample the middle of the bit
                    if (clock_count == (CLKS_PER_BIT / 2)) begin
                        if (rx_pin == 1'b0) begin // Confirm it's still low
                            clock_count <= 0;
                            rx_data[7]  <= 1'b0; // Bit 7 unused in 7-bit frame
                            state       <= DATA;
                        end else begin
                            state <= IDLE; // False alarm
                        end
                    end else begin
                        clock_count <= clock_count + 1;
                    end
                end

                DATA: begin
                    if (clock_count < CLKS_PER_BIT - 1) begin
                        clock_count <= clock_count + 1;
                    end else begin
                        clock_count <= 0;
                        rx_data[bit_index] <= rx_pin; // Sample the pin

                        if (bit_index < 6) begin // 7 data bits: indices 0..6
                            bit_index <= bit_index + 1;
                        end else begin
                            state <= PARITY;
                        end
                    end
                end

                PARITY: begin
                    // Burn one bit-time for the parity bit; not validated.
                    if (clock_count < CLKS_PER_BIT - 1) begin
                        clock_count <= clock_count + 1;
                    end else begin
                        clock_count <= 0;
                        state       <= STOP;
                    end
                end

                STOP: begin
                    if (clock_count < CLKS_PER_BIT - 1) begin
                        clock_count <= clock_count + 1;
                    end else begin
                        rx_done <= 1'b1; // Signal that a byte is ready
                        state   <= IDLE;
                    end
                end
            endcase
        end
    end
endmodule
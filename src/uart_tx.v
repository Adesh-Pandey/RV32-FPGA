module uart_tx (
    input wire clk,           // 125 MHz system clock
    input wire reset,         // Active high reset
    input wire tx_start,      // Pulse high for 1 clock cycle to start transmission
    input wire [7:0] tx_data, // The 8-bit byte to send
    output reg tx_pin,        // The physical wire going to the Pmod FTDI
    output reg tx_busy        // High when sending, tells processor to wait
);

    // 125,000,000 Hz / 115200 Baud = 1085 clock cycles per bit
    parameter CLKS_PER_BIT = 1085;

    // Frame: 1 start + 8 data + 1 stop (8N1)
    reg [3:0] state;
    reg [11:0] clock_count;
    reg [2:0] bit_index;
    reg [7:0] tx_data_reg;

    localparam IDLE  = 4'd0;
    localparam START = 4'd1;
    localparam DATA  = 4'd2;
    localparam STOP  = 4'd3;

    always @(posedge clk) begin
        if (reset) begin
            tx_pin  <= 1'b1; // Idle state for UART is High
            tx_busy <= 1'b0;
            state   <= IDLE;
        end else begin
            case (state)
                IDLE: begin
                    tx_pin      <= 1'b1;
                    clock_count <= 0;
                    bit_index   <= 0;
                    if (tx_start) begin
                        tx_busy     <= 1'b1;
                        tx_data_reg <= tx_data;
                        state       <= START;
                    end else begin
                        tx_busy <= 1'b0;
                    end
                end

                START: begin
                    tx_pin <= 1'b0; // Start bit is Low
                    if (clock_count < CLKS_PER_BIT - 1) begin
                        clock_count <= clock_count + 1;
                    end else begin
                        clock_count <= 0;
                        state       <= DATA;
                    end
                end

                DATA: begin
                    tx_pin <= tx_data_reg[bit_index];
                    if (clock_count < CLKS_PER_BIT - 1) begin
                        clock_count <= clock_count + 1;
                    end else begin
                        clock_count <= 0;
                        if (bit_index < 7) begin
                            bit_index <= bit_index + 1;
                        end else begin
                            state <= STOP;
                        end
                    end
                end

                STOP: begin
                    tx_pin <= 1'b1; // Stop bit is High
                    if (clock_count < CLKS_PER_BIT - 1) begin
                        clock_count <= clock_count + 1;
                    end else begin
                        clock_count <= 0;
                        state       <= IDLE;
                    end
                end
            endcase
        end
    end
endmodule

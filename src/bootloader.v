// Bootloader: receives a program over UART and writes it into IMEM, then
// releases the CPU. While load_done == 0, the CPU stays in reset and the
// loader owns the UART TX line.
//
// Wire protocol (host -> FPGA):
//   bytes [0..3]: magic 'R','V','3','2'  (0x52, 0x56, 0x33, 0x32)
//   byte  [4]   : length N in 32-bit words (1..255)
//   bytes [5..] : N program words, each 4 bytes little-endian (LSB first)
//
// Wire protocol (FPGA -> host):
//   after each word stored in IMEM: 0xA5
//   after final word:               0x5A    (then CPU reset is released)

module bootloader (
    input  wire        clk,
    input  wire        reset,        // Global reset (not gated by load_done)

    // UART RX
    input  wire [7:0]  rx_data,
    input  wire        rx_done,

    // UART TX (mux with CPU in zybo_top)
    output reg         tx_start,
    output reg  [7:0]  tx_data,
    input  wire        tx_busy,

    // IMEM write port
    output reg         imem_we,
    output reg  [7:0]  imem_waddr,
    output reg  [31:0] imem_wdata,

    // CPU release
    output reg         load_done
);

    localparam [7:0] MAGIC_R  = 8'h52;
    localparam [7:0] MAGIC_V  = 8'h56;
    localparam [7:0] MAGIC_3  = 8'h33;
    localparam [7:0] MAGIC_2  = 8'h32;
    localparam [7:0] ACK_WORD = 8'hA5;
    localparam [7:0] ACK_DONE = 8'h5A;

    localparam [3:0]
        S_MAGIC0 = 4'd0,
        S_MAGIC1 = 4'd1,
        S_MAGIC2 = 4'd2,
        S_MAGIC3 = 4'd3,
        S_LEN    = 4'd4,
        S_B0     = 4'd5,
        S_B1     = 4'd6,
        S_B2     = 4'd7,
        S_B3     = 4'd8,
        S_WAIT   = 4'd9,   // Wait for word-ack to finish transmitting
        S_FINAL  = 4'd10,  // Wait for final-ack to finish transmitting
        S_RUN    = 4'd11;  // CPU runs; loader idle

    reg [3:0]  state;
    reg [7:0]  word_count;
    reg [7:0]  word_idx;
    reg [23:0] word_buf;   // bytes 0..2 of the current word
    reg        last_word;

    always @(posedge clk) begin
        if (reset) begin
            state       <= S_MAGIC0;
            word_count  <= 8'd0;
            word_idx    <= 8'd0;
            word_buf    <= 24'd0;
            last_word   <= 1'b0;
            imem_we     <= 1'b0;
            imem_waddr  <= 8'd0;
            imem_wdata  <= 32'd0;
            tx_start    <= 1'b0;
            tx_data     <= 8'd0;
            load_done   <= 1'b0;
        end else begin
            // One-cycle pulses default low; case can override.
            imem_we  <= 1'b0;
            tx_start <= 1'b0;

            case (state)
                S_MAGIC0: if (rx_done) state <= (rx_data == MAGIC_R) ? S_MAGIC1 : S_MAGIC0;
                S_MAGIC1: if (rx_done) state <= (rx_data == MAGIC_V) ? S_MAGIC2 : S_MAGIC0;
                S_MAGIC2: if (rx_done) state <= (rx_data == MAGIC_3) ? S_MAGIC3 : S_MAGIC0;
                S_MAGIC3: if (rx_done) state <= (rx_data == MAGIC_2) ? S_LEN    : S_MAGIC0;

                S_LEN: if (rx_done) begin
                    word_count <= rx_data;
                    word_idx   <= 8'd0;
                    if (rx_data == 8'd0) begin
                        // Degenerate: zero-word program. Skip straight to done.
                        tx_data  <= ACK_DONE;
                        tx_start <= 1'b1;
                        state    <= S_FINAL;
                    end else begin
                        state <= S_B0;
                    end
                end

                S_B0: if (rx_done) begin word_buf[7:0]   <= rx_data; state <= S_B1; end
                S_B1: if (rx_done) begin word_buf[15:8]  <= rx_data; state <= S_B2; end
                S_B2: if (rx_done) begin word_buf[23:16] <= rx_data; state <= S_B3; end

                S_B3: if (rx_done) begin
                    // Write the assembled word to IMEM.
                    imem_waddr <= word_idx;
                    imem_wdata <= {rx_data, word_buf[23:16], word_buf[15:8], word_buf[7:0]};
                    imem_we    <= 1'b1;
                    // Send per-word acknowledgement.
                    tx_data    <= ACK_WORD;
                    tx_start   <= 1'b1;
                    // Remember whether we just stored the final word.
                    last_word  <= (word_idx + 8'd1 == word_count);
                    state      <= S_WAIT;
                end

                S_WAIT: begin
                    // Wait for the ack we just dispatched to fully drain.
                    if (!tx_busy && !tx_start) begin
                        if (last_word) begin
                            tx_data  <= ACK_DONE;
                            tx_start <= 1'b1;
                            state    <= S_FINAL;
                        end else begin
                            word_idx <= word_idx + 8'd1;
                            state    <= S_B0;
                        end
                    end
                end

                S_FINAL: begin
                    if (!tx_busy && !tx_start) begin
                        load_done <= 1'b1;
                        state     <= S_RUN;
                    end
                end

                S_RUN: ; // Loader idle; CPU executing.

                default: state <= S_MAGIC0;
            endcase
        end
    end
endmodule

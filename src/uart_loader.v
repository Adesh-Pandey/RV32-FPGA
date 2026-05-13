module uart_loader (
    input  wire        clk,
    input  wire        reset,
    input  wire [7:0]  rx_data,
    input  wire        rx_done,
    input  wire        tx_busy,
    output reg         tx_start,
    output reg  [7:0]  tx_data,
    output reg         imem_we,
    output reg  [31:0] imem_addr,
    output reg  [31:0] imem_wd,
    output reg         cpu_reset_hold // 1 = Freeze CPU, 0 = Run
);

    localparam S_IDLE = 0, S_M2 = 1, S_M3 = 2, S_M4 = 3;
    localparam S_LEN  = 4, S_B0 = 5, S_B1 = 6, S_B2 = 7, S_B3 = 8;
    localparam S_ACK  = 9, S_DONE = 10;

    reg [3:0] state = S_IDLE;
    reg [7:0] words_total;
    reg [7:0] words_rcvd;
    reg [31:0] current_word;

    always @(posedge clk) begin
        if (reset) begin
            state <= S_IDLE;
            cpu_reset_hold <= 0;
            tx_start <= 0;
            imem_we <= 0;
            imem_addr <= 0;
        end else begin
            tx_start <= 0;
            imem_we <= 0;

            case (state)
                S_IDLE: begin
                    if (rx_done && rx_data == 8'h52) begin // 'R'
                        state <= S_M2;
                        cpu_reset_hold <= 1; // Freeze the CPU!
                    end
                end
                S_M2: if (rx_done) state <= (rx_data == 8'h56) ? S_M3 : S_IDLE; // 'V'
                S_M3: if (rx_done) state <= (rx_data == 8'h33) ? S_M4 : S_IDLE; // '3'
                S_M4: if (rx_done) state <= (rx_data == 8'h32) ? S_LEN : S_IDLE; // '2'
                
                S_LEN: if (rx_done) begin
                    words_total <= rx_data;
                    words_rcvd <= 0;
                    imem_addr <= 0;
                    if (rx_data == 0) state <= S_DONE;
                    else state <= S_B0;
                end
                
                S_B0: if (rx_done) begin current_word[7:0]   <= rx_data; state <= S_B1; end
                S_B1: if (rx_done) begin current_word[15:8]  <= rx_data; state <= S_B2; end
                S_B2: if (rx_done) begin current_word[23:16] <= rx_data; state <= S_B3; end
                S_B3: if (rx_done) begin
                    current_word[31:24] <= rx_data;
                    imem_wd <= {rx_data, current_word[23:16], current_word[15:8], current_word[7:0]};
                    imem_we <= 1;
                    state <= S_ACK;
                end
                
                S_ACK: begin
                    if (!tx_busy && !tx_start) begin
                        tx_data <= 8'hA5; // Send Spec ACK
                        tx_start <= 1;
                        words_rcvd <= words_rcvd + 1;
                        imem_addr <= imem_addr + 4;
                        if (words_rcvd + 1 == words_total) state <= S_DONE;
                        else state <= S_B0;
                    end
                end
                
                S_DONE: begin
                    if (!tx_busy && !tx_start) begin
                        tx_data <= 8'h5A; // Send Final ACK
                        tx_start <= 1;
                        cpu_reset_hold <= 0; // Release the CPU to Boot!
                        state <= S_IDLE;
                    end
                end
            endcase
        end
    end
endmodule
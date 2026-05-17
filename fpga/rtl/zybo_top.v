module zybo_top (
    input  wire       clk,
    input  wire       btn_reset,
    output wire [3:0] led,
    output wire [4:0] gpio,
    
    // --- ADDED FOR UART ---
    input  wire       uart_rx_pin, // Receives from laptop
    output wire       uart_tx_pin  // Transmits to laptop
);

    // --- RESET SYNCHRONIZER (Unchanged) ---
    reg  [3:0] btn_sync = 4'b1111;
    reg  [3:0] por_cnt  = 4'b0000;
    wire       por_done = &por_cnt;
    wire       reset;

    always @(posedge clk) begin
        btn_sync <= {btn_sync[2:0], btn_reset};
        if (!por_done) por_cnt <= por_cnt + 1'b1;
    end

    assign reset = (~por_done) | btn_sync[3];

    // --- CPU INSTANTIATION (Unchanged) ---
    wire [31:0] perf_cycles;
    wire [31:0] perf_instrs;
    wire        perf_halted;
    wire [31:0] pc_out;
    wire [4:0]  gpio_out;

   top cpu (
        .clk           (clk),
        .reset         (reset),
        .o_perf_cycles (perf_cycles),
        .o_perf_instrs (perf_instrs),
        .o_perf_halted (perf_halted),
        .o_pc          (pc_out),
        .o_gpio        (gpio_out),
        .i_uart_rx     (uart_rx_pin),
        .o_uart_tx     (uart_tx_pin)
    );

    assign gpio = gpio_out;

    assign led[0] = perf_halted;
    assign led[1] = perf_cycles[26];
    assign led[2] = perf_instrs[26];
    assign led[3] = pc_out[28];

    wire [7:0] uart_data;
    wire data_ready;

   

endmodule
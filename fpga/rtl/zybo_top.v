// Top-level wrapper for the RV32 SoC on the Zybo board.
//
// Owns the physical UART transceiver and a bootloader FSM. On reset the
// CPU is held off; the bootloader listens on UART for "RV32" magic, a length
// byte, and N little-endian program words. Each word is written into IMEM
// and acknowledged with 0xA5. After the final word the bootloader emits
// 0x5A and releases the CPU, which begins execution at PC = 0.
//
// While the CPU is running, it uses the same UART (TX mux selects between
// bootloader and CPU; bootloader is idle after load_done).

module zybo_top (
    input  wire       clk,
    input  wire       btn_reset,
    output wire [3:0] led,
    output wire [4:0] gpio,

    input  wire       uart_rx_pin, // Receives from host (FTDI TXD)
    output wire       uart_tx_pin  // Transmits to host  (FTDI RXD)
);

    // --- RESET SYNCHRONIZER (global reset; resets bootloader + UART core) ---
    reg  [3:0] btn_sync = 4'b1111;
    reg  [3:0] por_cnt  = 4'b0000;
    wire       por_done = &por_cnt;
    wire       global_reset;

    always @(posedge clk) begin
        btn_sync <= {btn_sync[2:0], btn_reset};
        if (!por_done) por_cnt <= por_cnt + 1'b1;
    end

    assign global_reset = (~por_done) | btn_sync[3];

    // --- UART RX (shared by bootloader and CPU) ---
    wire [7:0] rx_data;
    wire       rx_done;

    uart_rx uart_rx_inst (
        .clk(clk),
        .reset(global_reset),
        .rx_pin(uart_rx_pin),
        .rx_data(rx_data),
        .rx_done(rx_done)
    );

    // --- Bootloader ---
    wire        bl_tx_start;
    wire [7:0]  bl_tx_data;
    wire        bl_imem_we;
    wire [7:0]  bl_imem_waddr;
    wire [31:0] bl_imem_wdata;
    wire        load_done;
    wire        tx_busy;

    bootloader bl (
        .clk(clk),
        .reset(global_reset),
        .rx_data(rx_data),
        .rx_done(rx_done),
        .tx_start(bl_tx_start),
        .tx_data(bl_tx_data),
        .tx_busy(tx_busy),
        .imem_we(bl_imem_we),
        .imem_waddr(bl_imem_waddr),
        .imem_wdata(bl_imem_wdata),
        .load_done(load_done)
    );

    // --- CPU (held in reset until bootloader finishes) ---
    wire cpu_reset = global_reset | ~load_done;

    wire        cpu_tx_start;
    wire [7:0]  cpu_tx_data;
    wire [31:0] perf_cycles;
    wire [31:0] perf_instrs;
    wire        perf_halted;
    wire [31:0] pc_out;
    wire [4:0]  gpio_out;

    top cpu (
        .clk            (clk),
        .reset          (cpu_reset),
        .o_perf_cycles  (perf_cycles),
        .o_perf_instrs  (perf_instrs),
        .o_perf_halted  (perf_halted),
        .o_pc           (pc_out),
        .o_gpio         (gpio_out),
        .i_uart_rx_data (rx_data),
        .i_uart_rx_done (rx_done),
        .o_uart_tx_start(cpu_tx_start),
        .o_uart_tx_data (cpu_tx_data),
        .i_uart_tx_busy (tx_busy),
        .i_imem_we      (bl_imem_we),
        .i_imem_waddr   (bl_imem_waddr),
        .i_imem_wdata   (bl_imem_wdata)
    );

    assign gpio = gpio_out;

    // --- TX mux: bootloader owns TX during load, CPU after ---
    wire        muxed_tx_start = load_done ? cpu_tx_start : bl_tx_start;
    wire [7:0]  muxed_tx_data  = load_done ? cpu_tx_data  : bl_tx_data;

    uart_tx uart_tx_inst (
        .clk(clk),
        .reset(global_reset),
        .tx_start(muxed_tx_start),
        .tx_data(muxed_tx_data),
        .tx_pin(uart_tx_pin),
        .tx_busy(tx_busy)
    );

    // --- LED diagnostics ---
    //   led[0]: lit when program load is complete and CPU is running
    //   led[1]: TX line activity (low while transmitting start/data bits)
    //   led[2]: RX line activity
    //   led[3]: global reset (POR or button press)
    assign led[0] = load_done;
    assign led[1] = uart_tx_pin;
    assign led[2] = uart_rx_pin;
    assign led[3] = global_reset;

endmodule

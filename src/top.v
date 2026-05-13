module top(
    input             clk,
    input             reset,
    output [31:0]     o_perf_cycles,
    output [31:0]     o_perf_instrs,
    output            o_perf_halted,
    output [31:0]     o_pc,
    output [4:0]      o_gpio,
    
    // --- ADDED FOR UART ---
    input  wire       i_uart_rx,
    output wire       o_uart_tx
);

    wire [4:0] dmem_gpio;

    
    // =========================================================
    //  ALL SIGNAL DECLARATIONS (Unchanged)
    // =========================================================
    wire [31:0] pc_out, pc_plus4, pc_next, if_instr;
    reg [31:0] if_id_instr, if_id_pc, if_id_pc_plus4;
    wire [31:0] id_rd1, id_rd2, id_imm_ext;
    wire        id_reg_write, id_alu_src, id_mem_write;
    wire        id_branch, id_jump, id_jalr;
    wire [1:0]  id_result_src, id_alu_src1;
    wire [3:0]  id_alu_control;
    reg [31:0] id_ex_pc, id_ex_pc_plus4;
    reg [31:0] id_ex_rd1, id_ex_rd2, id_ex_imm_ext;
    reg [4:0]  id_ex_rd, id_ex_rs1, id_ex_rs2;
    reg [2:0]  id_ex_funct3;
    reg        id_ex_reg_write, id_ex_alu_src, id_ex_mem_write;
    reg        id_ex_branch, id_ex_jump, id_ex_jalr;
    reg [1:0]  id_ex_result_src, id_ex_alu_src1;
    reg [3:0]  id_ex_alu_control;
    reg id_ex_valid, ex_mem_valid, mem_wb_valid;
    wire [31:0] ex_alu_result, ex_srcB_mux;
    wire [31:0] ex_branch_target, ex_jalr_target;
    wire        ex_zero;
    reg [31:0]  ex_srcA;
    reg         ex_branch_taken;
    reg [1:0]  forward_a, forward_b;
    reg [31:0] ex_rd1_fwd, ex_rd2_fwd;
    wire [31:0] ex_mem_fwd_val;
    reg [31:0] ex_mem_alu_result, ex_mem_rd2, ex_mem_pc_plus4;
    reg [4:0]  ex_mem_rd;
    reg        ex_mem_reg_write, ex_mem_mem_write;
    reg [1:0]  ex_mem_result_src;
    reg [31:0] mem_wb_alu_result, mem_wb_read_data, mem_wb_pc_plus4;
    reg [4:0]  mem_wb_rd;
    reg        mem_wb_reg_write;
    reg [1:0]  mem_wb_result_src;
    reg [31:0] wb_result;

    wire flush;
    wire stall;
    assign flush = ex_branch_taken || id_ex_jump || id_ex_jalr;

    // =========================================================
    //  PERFORMANCE COUNTERS & HAZARDS (Unchanged)
    // =========================================================
    reg [31:0] perf_cycles, perf_instrs, perf_stalls, perf_flushes;
    reg        perf_halted;
    wire halt_detected = id_ex_jump && (id_ex_rd == 5'b0) && (id_ex_imm_ext == 32'b0);

    always @(posedge clk) begin
        if (reset) begin
            perf_cycles  <= 0; perf_instrs  <= 0; perf_stalls  <= 0;
            perf_flushes <= 0; perf_halted  <= 0;
        end else begin
            if (halt_detected) perf_halted <= 1;
            if (!perf_halted) begin
                perf_cycles <= perf_cycles + 1;
                if (mem_wb_valid) perf_instrs <= perf_instrs + 1;
                if (stall) perf_stalls <= perf_stalls + 1;
                if (flush) perf_flushes <= perf_flushes + 1;
            end
        end
    end

    assign stall = id_ex_result_src == 2'b01 && id_ex_rd != 5'b0 && 
                   (id_ex_rd == if_id_instr[19:15] || id_ex_rd == if_id_instr[24:20]);

    // =========================================================
    //  STAGES 1, 2, 3 (IF, ID, EX) - Unchanged 
    // =========================================================
    pc pc_unit( .clk(clk), .rst(reset), .en(!stall), .pc_next(pc_next), .pc(pc_out) );
    pc_adder pc_adder_unit( .a(pc_out), .y(pc_plus4) );
    imem imem_unit( .a(pc_out), .rd(if_instr) );

    assign pc_next = (id_ex_jalr) ? ex_jalr_target :
                     (id_ex_jump || ex_branch_taken) ? ex_branch_target : pc_plus4;

    always @(posedge clk) begin
        if (reset || flush) begin
            if_id_instr <= 32'h00000013; if_id_pc <= 0; if_id_pc_plus4 <= 0;
        end else if (!stall) begin
            if_id_instr <= if_instr; if_id_pc <= pc_out; if_id_pc_plus4 <= pc_plus4;
        end
    end

    control control_unit(.opcode(if_id_instr[6:0]), .funct3(if_id_instr[14:12]), .funct7(if_id_instr[31:25]), .reg_write(id_reg_write), .alu_src(id_alu_src), .alu_control(id_alu_control), .mem_write(id_mem_write), .result_src(id_result_src), .branch(id_branch), .jump(id_jump), .jalr(id_jalr), .alu_src1(id_alu_src1));
    regfile reg_unit(.clk(clk), .we3(mem_wb_reg_write), .a1(if_id_instr[19:15]), .a2(if_id_instr[24:20]), .a3(mem_wb_rd), .rd1(id_rd1), .rd2(id_rd2), .wd3(wb_result));
    imm_gen gen_unit( .instr(if_id_instr), .imm_ext(id_imm_ext) );

    always @(posedge clk) begin
        if (reset || flush || stall) begin
            id_ex_reg_write <= 0; id_ex_mem_write <= 0; id_ex_branch <= 0; id_ex_jump <= 0; id_ex_jalr <= 0; id_ex_result_src <= 2'b0; id_ex_alu_src1 <= 2'b0; id_ex_alu_control <= 4'b0; id_ex_alu_src <= 0; id_ex_rd <= 5'b0; id_ex_funct3 <= 3'b0; id_ex_pc <= 32'b0; id_ex_pc_plus4 <= 32'b0; id_ex_rd1 <= 32'b0; id_ex_rd2 <= 32'b0; id_ex_imm_ext <= 32'b0; id_ex_rs1 <= 5'b0; id_ex_rs2 <= 5'b0; id_ex_valid <= 0;
        end else begin
            id_ex_pc <= if_id_pc; id_ex_pc_plus4 <= if_id_pc_plus4; id_ex_rd1 <= id_rd1; id_ex_rd2 <= id_rd2; id_ex_imm_ext <= id_imm_ext; id_ex_rd <= if_id_instr[11:7]; id_ex_rs1 <= if_id_instr[19:15]; id_ex_rs2 <= if_id_instr[24:20]; id_ex_funct3 <= if_id_instr[14:12]; id_ex_reg_write <= id_reg_write; id_ex_alu_src <= id_alu_src; id_ex_mem_write <= id_mem_write; id_ex_branch <= id_branch; id_ex_jump <= id_jump; id_ex_jalr <= id_jalr; id_ex_result_src <= id_result_src; id_ex_alu_src1 <= id_alu_src1; id_ex_alu_control <= id_alu_control; id_ex_valid <= 1;
        end
    end

    assign ex_mem_fwd_val = (ex_mem_result_src == 2'b10) ? ex_mem_pc_plus4 : (ex_mem_result_src == 2'b01) ? 32'b0 : ex_mem_alu_result;

    always @(*) begin
        if (ex_mem_reg_write && ex_mem_rd != 5'b0 && ex_mem_rd == id_ex_rs1) forward_a = 2'b10;
        else if (mem_wb_reg_write && mem_wb_rd != 5'b0 && mem_wb_rd == id_ex_rs1) forward_a = 2'b01;
        else forward_a = 2'b00;

        if (ex_mem_reg_write && ex_mem_rd != 5'b0 && ex_mem_rd == id_ex_rs2) forward_b = 2'b10;
        else if (mem_wb_reg_write && mem_wb_rd != 5'b0 && mem_wb_rd == id_ex_rs2) forward_b = 2'b01;
        else forward_b = 2'b00;
    end

    always @(*) begin
        case (forward_a) 2'b10: ex_rd1_fwd = ex_mem_fwd_val; 2'b01: ex_rd1_fwd = wb_result; default: ex_rd1_fwd = id_ex_rd1; endcase
        case (forward_b) 2'b10: ex_rd2_fwd = ex_mem_fwd_val; 2'b01: ex_rd2_fwd = wb_result; default: ex_rd2_fwd = id_ex_rd2; endcase
        case (id_ex_alu_src1) 2'b00: ex_srcA = ex_rd1_fwd; 2'b01: ex_srcA = id_ex_pc; 2'b10: ex_srcA = 32'b0; default: ex_srcA = ex_rd1_fwd; endcase
    end

    assign ex_srcB_mux = (id_ex_alu_src) ? id_ex_imm_ext : ex_rd2_fwd;
    alu alu_unit(.src1(ex_srcA), .src2(ex_srcB_mux), .alu_control(id_ex_alu_control), .result(ex_alu_result), .zero(ex_zero));
    assign ex_branch_target = id_ex_pc + id_ex_imm_ext;
    assign ex_jalr_target   = ex_alu_result & 32'hFFFFFFFE;

    always @(*) begin
        ex_branch_taken = 0;
        if (id_ex_branch) begin
            case (id_ex_funct3)
                3'b000: ex_branch_taken = ex_zero; 3'b001: ex_branch_taken = ~ex_zero; 3'b100: ex_branch_taken = ex_alu_result[0]; 3'b101: ex_branch_taken = ~ex_alu_result[0]; 3'b110: ex_branch_taken = ex_alu_result[0]; 3'b111: ex_branch_taken = ~ex_alu_result[0]; default: ex_branch_taken = 0;
            endcase
        end
    end

    always @(posedge clk) begin
        if (reset) begin
            ex_mem_alu_result <= 0; ex_mem_rd2 <= 0; ex_mem_pc_plus4 <= 0; ex_mem_rd <= 0; ex_mem_reg_write <= 0; ex_mem_mem_write <= 0; ex_mem_result_src <= 0; ex_mem_valid <= 0;
        end else begin
            ex_mem_alu_result <= ex_alu_result; ex_mem_rd2 <= ex_rd2_fwd; ex_mem_pc_plus4 <= id_ex_pc_plus4; ex_mem_rd <= id_ex_rd; ex_mem_reg_write <= id_ex_reg_write; ex_mem_mem_write <= id_ex_mem_write; ex_mem_result_src <= id_ex_result_src; ex_mem_valid <= id_ex_valid;
        end
    end

    // =========================================================
    //  STAGE 4: MEMORY (MEM) & UART INTEGRATION
    // =========================================================
    
    // Address Decoders for UART
    wire is_tx_write = ex_mem_mem_write && (ex_mem_alu_result == 32'h104);
    wire is_mem_read = (ex_mem_result_src == 2'b01);
    wire is_rx_read  = is_mem_read && (ex_mem_alu_result == 32'h108);

    wire [7:0] uart_rx_data;
    wire       uart_rx_done;
    wire       uart_tx_busy;
    
    // Latch to hold RX data until the CPU actually reads it
    reg [7:0]  rx_buffer;
    reg        rx_ready;

    always @(posedge clk) begin
        if (reset) begin
            rx_buffer <= 0;
            rx_ready  <= 0;
        end else if (uart_rx_done) begin
            rx_buffer <= uart_rx_data;
            rx_ready  <= 1; // Flag high: data arrived!
        end else if (is_rx_read) begin
            rx_ready  <= 0; // Flag low: CPU read the data
        end
    end

    uart_tx my_tx (
        .clk(clk),
        .reset(reset),
        .tx_start(is_tx_write),
        .tx_data(ex_mem_rd2[7:0]), // Write the lowest 8 bits
        .tx_pin(o_uart_tx),
        .tx_busy(uart_tx_busy)
    );

    uart_rx my_rx (
        .clk(clk),
        .reset(reset),
        .rx_pin(i_uart_rx),
        .rx_data(uart_rx_data),
        .rx_done(uart_rx_done)
    );

    wire [31:0] dmem_out;
    dmem dmem_unit(
        .clk(clk),
        .we(ex_mem_mem_write),
        .a(ex_mem_alu_result),
        .wd(ex_mem_rd2),
        .rd(dmem_out),
        .gpio_out(dmem_gpio)
    );

    // THE MULTIPLEXER: Choose what to read based on the memory address
    wire [31:0] mem_read_data;
    assign mem_read_data = (ex_mem_alu_result == 32'h108) ? {24'b0, rx_buffer} :
                           (ex_mem_alu_result == 32'h10C) ? {30'b0, uart_tx_busy, rx_ready} :
                           dmem_out;

    // =========================================================
    //  STAGE 5: WRITE BACK (WB)
    // =========================================================
    always @(posedge clk) begin
        if (reset) begin
            mem_wb_alu_result <= 0; mem_wb_read_data <= 0; mem_wb_pc_plus4 <= 0; mem_wb_rd <= 0; mem_wb_reg_write <= 0; mem_wb_result_src <= 0; mem_wb_valid <= 0;
        end else begin
            mem_wb_alu_result <= ex_mem_alu_result; mem_wb_read_data <= mem_read_data; mem_wb_pc_plus4 <= ex_mem_pc_plus4; mem_wb_rd <= ex_mem_rd; mem_wb_reg_write <= ex_mem_reg_write; mem_wb_result_src <= ex_mem_result_src; mem_wb_valid <= ex_mem_valid;
        end
    end

    always @(*) begin
        case (mem_wb_result_src)
            2'b00:   wb_result = mem_wb_alu_result;
            2'b01:   wb_result = mem_wb_read_data; // This now grabs UART data if address was 0x108
            2'b10:   wb_result = mem_wb_pc_plus4;
            default: wb_result = mem_wb_alu_result;
        endcase
    end

    assign o_perf_cycles = perf_cycles;
    assign o_perf_instrs = perf_instrs;
    assign o_perf_halted = perf_halted;
    assign o_pc          = pc_out;
    assign o_gpio        = dmem_gpio;

endmodule
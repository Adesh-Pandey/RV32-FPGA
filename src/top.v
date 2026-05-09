module top(
    input clk,
    input reset
);

    // =========================================================
    //  ALL SIGNAL DECLARATIONS
    // =========================================================

    // IF stage
    wire [31:0] pc_out, pc_plus4, pc_next, if_instr;

    // IF/ID pipeline register
    reg [31:0] if_id_instr, if_id_pc, if_id_pc_plus4;

    // ID stage
    wire [31:0] id_rd1, id_rd2, id_imm_ext;
    wire        id_reg_write, id_alu_src, id_mem_write;
    wire        id_branch, id_jump, id_jalr;
    wire [1:0]  id_result_src, id_alu_src1;
    wire [3:0]  id_alu_control;

    // ID/EX pipeline register
    reg [31:0] id_ex_pc, id_ex_pc_plus4;
    reg [31:0] id_ex_rd1, id_ex_rd2, id_ex_imm_ext;
    reg [4:0]  id_ex_rd, id_ex_rs1, id_ex_rs2;
    reg [2:0]  id_ex_funct3;
    reg        id_ex_reg_write, id_ex_alu_src, id_ex_mem_write;
    reg        id_ex_branch, id_ex_jump, id_ex_jalr;
    reg [1:0]  id_ex_result_src, id_ex_alu_src1;
    reg [3:0]  id_ex_alu_control;

    // Pipeline valid bits (for accurate instruction counting)
    reg id_ex_valid, ex_mem_valid, mem_wb_valid;

    // EX stage
    wire [31:0] ex_alu_result, ex_srcB_mux;
    wire [31:0] ex_branch_target, ex_jalr_target;
    wire        ex_zero;
    reg [31:0]  ex_srcA;
    reg         ex_branch_taken;

    // Forwarding
    reg [1:0]  forward_a, forward_b;
    reg [31:0] ex_rd1_fwd, ex_rd2_fwd;
    wire [31:0] ex_mem_fwd_val;

    // EX/MEM pipeline register
    reg [31:0] ex_mem_alu_result, ex_mem_rd2, ex_mem_pc_plus4;
    reg [4:0]  ex_mem_rd;
    reg        ex_mem_reg_write, ex_mem_mem_write;
    reg [1:0]  ex_mem_result_src;

    // MEM stage
    wire [31:0] mem_read_data;

    // MEM/WB pipeline register
    reg [31:0] mem_wb_alu_result, mem_wb_read_data, mem_wb_pc_plus4;
    reg [4:0]  mem_wb_rd;
    reg        mem_wb_reg_write;
    reg [1:0]  mem_wb_result_src;

    // WB stage
    reg [31:0] wb_result;

    // Hazard control
    wire flush;
    wire stall;

    assign flush = ex_branch_taken || id_ex_jump || id_ex_jalr;

    // =========================================================
    //  PERFORMANCE COUNTERS
    // =========================================================
    reg [31:0] perf_cycles;
    reg [31:0] perf_instrs;     // Instructions retired (committed)
    reg [31:0] perf_stalls;     // Stall cycles (load-use)
    reg [31:0] perf_flushes;    // Flushed instructions (branch/jump)
    reg        perf_halted;     // Freeze counters on halt loop

    // Detect halt: JAL x0,0 in EX stage (jump to self, rd=x0)
    wire halt_detected = id_ex_jump && (id_ex_rd == 5'b0) &&
                         (id_ex_imm_ext == 32'b0);

    always @(posedge clk) begin
        if (reset) begin
            perf_cycles  <= 0;
            perf_instrs  <= 0;
            perf_stalls  <= 0;
            perf_flushes <= 0;
            perf_halted  <= 0;
        end else begin
            if (halt_detected)
                perf_halted <= 1;

            if (!perf_halted) begin
                perf_cycles <= perf_cycles + 1;

                if (mem_wb_valid)
                    perf_instrs <= perf_instrs + 1;

                if (stall)
                    perf_stalls <= perf_stalls + 1;

                if (flush)
                    perf_flushes <= perf_flushes + 1;
            end
        end
    end

    // =========================================================
    //  HAZARD DETECTION (Load-Use Stall)
    // =========================================================
    // If instruction in EX is a load, and the instruction in ID
    // needs that register, stall for 1 cycle.

    // E.g
    // lw  x5, 0(x2)    ← in EX stage now, data won't be ready until end of MEM
    // add x7, x5, x3   ← in ID stage now, needs x5 next cycle in EX — too soon!
    assign stall = id_ex_result_src == 2'b01 &&       // load in EX
                   id_ex_rd != 5'b0 &&                 // not writing x0
                   (id_ex_rd == if_id_instr[19:15] ||  // rs1 match
                    id_ex_rd == if_id_instr[24:20]);   // rs2 match

    // =========================================================
    //  STAGE 1: INSTRUCTION FETCH (IF)
    // =========================================================

    pc pc_unit( .clk(clk), .rst(reset), .en(!stall), .pc_next(pc_next), .pc(pc_out) );
    pc_adder pc_adder_unit( .a(pc_out), .y(pc_plus4) );
    imem imem_unit( .a(pc_out), .rd(if_instr) );

    // PC source mux
    assign pc_next = (id_ex_jalr)                   ? ex_jalr_target :
                     (id_ex_jump || ex_branch_taken) ? ex_branch_target :
                                                       pc_plus4;

    // =========================================================
    //  IF/ID PIPELINE REGISTER
    // =========================================================
    // Stall: keep current values. Flush: insert NOP.

    always @(posedge clk) begin
        if (reset || flush) begin
            if_id_instr    <= 32'h00000013; // NOP
            if_id_pc       <= 32'b0;
            if_id_pc_plus4 <= 32'b0;
        end else if (!stall) begin
            if_id_instr    <= if_instr;
            if_id_pc       <= pc_out;
            if_id_pc_plus4 <= pc_plus4;
        end
        // If stall: hold current values (don't update)
    end

    // =========================================================
    //  STAGE 2: INSTRUCTION DECODE (ID)
    // =========================================================

    control control_unit(
        .opcode(if_id_instr[6:0]),
        .funct3(if_id_instr[14:12]),
        .funct7(if_id_instr[31:25]),
        .reg_write(id_reg_write),
        .alu_src(id_alu_src),
        .alu_control(id_alu_control),
        .mem_write(id_mem_write),
        .result_src(id_result_src),
        .branch(id_branch),
        .jump(id_jump),
        .jalr(id_jalr),
        .alu_src1(id_alu_src1)
    );

    regfile reg_unit(
        .clk(clk),
        .we3(mem_wb_reg_write),
        .a1(if_id_instr[19:15]),
        .a2(if_id_instr[24:20]),
        .a3(mem_wb_rd),
        .rd1(id_rd1),
        .rd2(id_rd2),
        .wd3(wb_result)
    );

    imm_gen gen_unit( .instr(if_id_instr), .imm_ext(id_imm_ext) );

    // =========================================================
    //  ID/EX PIPELINE REGISTER
    // =========================================================
    // Stall: insert bubble (clear control signals).
    // Flush: insert bubble.

    always @(posedge clk) begin
        if (reset || flush || stall) begin
            // Bubble: zero all control signals
            id_ex_reg_write   <= 0;
            id_ex_mem_write   <= 0;
            id_ex_branch      <= 0;
            id_ex_jump        <= 0;
            id_ex_jalr        <= 0;
            id_ex_result_src  <= 2'b0;
            id_ex_alu_src1    <= 2'b0;
            id_ex_alu_control <= 4'b0;
            id_ex_alu_src     <= 0;
            id_ex_rd          <= 5'b0;
            id_ex_funct3      <= 3'b0;
            id_ex_pc          <= 32'b0;
            id_ex_pc_plus4    <= 32'b0;
            id_ex_rd1         <= 32'b0;
            id_ex_rd2         <= 32'b0;
            id_ex_imm_ext     <= 32'b0;
            id_ex_rs1         <= 5'b0;
            id_ex_rs2         <= 5'b0;
            id_ex_valid       <= 0;
        end else begin
            id_ex_pc          <= if_id_pc;
            id_ex_pc_plus4    <= if_id_pc_plus4;
            id_ex_rd1         <= id_rd1;
            id_ex_rd2         <= id_rd2;
            id_ex_imm_ext     <= id_imm_ext;
            id_ex_rd          <= if_id_instr[11:7];
            id_ex_rs1         <= if_id_instr[19:15];
            id_ex_rs2         <= if_id_instr[24:20];
            id_ex_funct3      <= if_id_instr[14:12];
            id_ex_reg_write   <= id_reg_write;
            id_ex_alu_src     <= id_alu_src;
            id_ex_mem_write   <= id_mem_write;
            id_ex_branch      <= id_branch;
            id_ex_jump        <= id_jump;
            id_ex_jalr        <= id_jalr;
            id_ex_result_src  <= id_result_src;
            id_ex_alu_src1    <= id_alu_src1;
            id_ex_alu_control <= id_alu_control;
            id_ex_valid       <= 1;
        end
    end

    // =========================================================
    //  FORWARDING UNIT
    // =========================================================
    // forward_a/forward_b: 00=no fwd, 10=from EX/MEM, 01=from MEM/WB

    // Value to forward from EX/MEM (ALU result or PC+4 for JAL/JALR)
    assign ex_mem_fwd_val = (ex_mem_result_src == 2'b10) ? ex_mem_pc_plus4 :
                           (ex_mem_result_src == 2'b01) ? 32'b0 :
                                                          ex_mem_alu_result;

    always @(*) begin
        // --- Forward A (rs1) ---
        if (ex_mem_reg_write && ex_mem_rd != 5'b0 && ex_mem_rd == id_ex_rs1)
            forward_a = 2'b10;  // EX/MEM has priority (more recent)
        else if (mem_wb_reg_write && mem_wb_rd != 5'b0 && mem_wb_rd == id_ex_rs1)
            forward_a = 2'b01;  // MEM/WB
        else
            forward_a = 2'b00;  // No forwarding

        // --- Forward B (rs2) ---
        if (ex_mem_reg_write && ex_mem_rd != 5'b0 && ex_mem_rd == id_ex_rs2)
            forward_b = 2'b10;
        else if (mem_wb_reg_write && mem_wb_rd != 5'b0 && mem_wb_rd == id_ex_rs2)
            forward_b = 2'b01;
        else
            forward_b = 2'b00;
    end

    // =========================================================
    //  STAGE 3: EXECUTE (EX)
    // =========================================================

    // Apply forwarding to rd1 and rd2
    always @(*) begin
        case (forward_a)
            2'b10:   ex_rd1_fwd = ex_mem_fwd_val;
            2'b01:   ex_rd1_fwd = wb_result;
            default: ex_rd1_fwd = id_ex_rd1;
        endcase
    end

    always @(*) begin
        case (forward_b)
            2'b10:   ex_rd2_fwd = ex_mem_fwd_val;
            2'b01:   ex_rd2_fwd = wb_result;
            default: ex_rd2_fwd = id_ex_rd2;
        endcase
    end

    // srcA mux (forwarded register / PC / zero)
    always @(*) begin
        case (id_ex_alu_src1)
            2'b00:   ex_srcA = ex_rd1_fwd;    // Normal (with forwarding)
            2'b01:   ex_srcA = id_ex_pc;       // AUIPC
            2'b10:   ex_srcA = 32'b0;          // LUI
            default: ex_srcA = ex_rd1_fwd;
        endcase
    end

    // srcB mux (forwarded register / immediate)
    assign ex_srcB_mux = (id_ex_alu_src) ? id_ex_imm_ext : ex_rd2_fwd;

    alu alu_unit(
        .src1(ex_srcA),
        .src2(ex_srcB_mux),
        .alu_control(id_ex_alu_control),
        .result(ex_alu_result),
        .zero(ex_zero)
    );

    // Branch/jump targets
    assign ex_branch_target = id_ex_pc + id_ex_imm_ext;
    assign ex_jalr_target   = ex_alu_result & 32'hFFFFFFFE;

    // Branch condition
    always @(*) begin
        ex_branch_taken = 0;
        if (id_ex_branch) begin
            case (id_ex_funct3)
                3'b000: ex_branch_taken = ex_zero;
                3'b001: ex_branch_taken = ~ex_zero;
                3'b100: ex_branch_taken = ex_alu_result[0];
                3'b101: ex_branch_taken = ~ex_alu_result[0];
                3'b110: ex_branch_taken = ex_alu_result[0];
                3'b111: ex_branch_taken = ~ex_alu_result[0];
                default: ex_branch_taken = 0;
            endcase
        end
    end

    // =========================================================
    //  EX/MEM PIPELINE REGISTER
    // =========================================================

    always @(posedge clk) begin
        if (reset) begin
            ex_mem_alu_result <= 32'b0;
            ex_mem_rd2        <= 32'b0;
            ex_mem_pc_plus4   <= 32'b0;
            ex_mem_rd         <= 5'b0;
            ex_mem_reg_write  <= 0;
            ex_mem_mem_write  <= 0;
            ex_mem_result_src <= 2'b0;
            ex_mem_valid      <= 0;
        end else begin
            ex_mem_alu_result <= ex_alu_result;
            ex_mem_rd2        <= ex_rd2_fwd;  // Use forwarded value for stores
            ex_mem_pc_plus4   <= id_ex_pc_plus4;
            ex_mem_rd         <= id_ex_rd;
            ex_mem_reg_write  <= id_ex_reg_write;
            ex_mem_mem_write  <= id_ex_mem_write;
            ex_mem_result_src <= id_ex_result_src;
            ex_mem_valid      <= id_ex_valid;
        end
    end

    // =========================================================
    //  STAGE 4: MEMORY (MEM)
    // =========================================================

    dmem dmem_unit(
        .clk(clk),
        .we(ex_mem_mem_write),
        .a(ex_mem_alu_result),
        .wd(ex_mem_rd2),
        .rd(mem_read_data)
    );

    // =========================================================
    //  MEM/WB PIPELINE REGISTER
    // =========================================================

    always @(posedge clk) begin
        if (reset) begin
            mem_wb_alu_result <= 32'b0;
            mem_wb_read_data  <= 32'b0;
            mem_wb_pc_plus4   <= 32'b0;
            mem_wb_rd         <= 5'b0;
            mem_wb_reg_write  <= 0;
            mem_wb_result_src <= 2'b0;
            mem_wb_valid      <= 0;
        end else begin
            mem_wb_alu_result <= ex_mem_alu_result;
            mem_wb_read_data  <= mem_read_data;
            mem_wb_pc_plus4   <= ex_mem_pc_plus4;
            mem_wb_rd         <= ex_mem_rd;
            mem_wb_reg_write  <= ex_mem_reg_write;
            mem_wb_result_src <= ex_mem_result_src;
            mem_wb_valid      <= ex_mem_valid;
        end
    end

    // =========================================================
    //  STAGE 5: WRITE BACK (WB)
    // =========================================================

    always @(*) begin
        case (mem_wb_result_src)
            2'b00:   wb_result = mem_wb_alu_result;
            2'b01:   wb_result = mem_wb_read_data;
            2'b10:   wb_result = mem_wb_pc_plus4;
            default: wb_result = mem_wb_alu_result;
        endcase
    end

endmodule

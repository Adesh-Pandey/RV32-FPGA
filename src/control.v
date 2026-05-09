module control(
    input [6:0] opcode,
    input [2:0] funct3,
    input [6:0] funct7,
    output reg reg_write,
    output reg alu_src,
    output reg [3:0] alu_control,
    output reg mem_write,
    output reg [1:0] result_src,
    output reg branch,
    output reg jump,
    output reg jalr,
    output reg [1:0] alu_src1  // 00=regfile, 01=PC, 10=zero
);

    always @(*) begin
        reg_write = 0;
        alu_src = 0;
        alu_control = 4'b0000;
        mem_write = 0;
        result_src = 2'b00;
        branch = 0;
        jump = 0;
        jalr = 0;
        alu_src1 = 2'b00;

        case (opcode)
            // R-type
            7'b0110011: begin
                reg_write = 1;
                alu_src = 0;

                case (funct3)
                    3'b000: begin
                        if (funct7[5]) alu_control = 4'b0001; // SUB
                        else           alu_control = 4'b0000; // ADD
                    end
                    3'b001: alu_control = 4'b0110; // SLL
                    3'b010: alu_control = 4'b0101; // SLT
                    3'b011: alu_control = 4'b1000; // SLTU
                    3'b100: alu_control = 4'b0100; // XOR
                    3'b101: begin
                        if (funct7[5]) alu_control = 4'b1001; // SRA
                        else           alu_control = 4'b0111; // SRL
                    end
                    3'b110: alu_control = 4'b0011; // OR
                    3'b111: alu_control = 4'b0010; // AND
                endcase
            end

            // I-type ALU
            7'b0010011: begin
                reg_write = 1;
                alu_src = 1;

                case (funct3)
                    3'b000: alu_control = 4'b0000; // ADDI
                    3'b010: alu_control = 4'b0101; // SLTI
                    3'b011: alu_control = 4'b1000; // SLTIU
                    3'b100: alu_control = 4'b0100; // XORI
                    3'b110: alu_control = 4'b0011; // ORI
                    3'b111: alu_control = 4'b0010; // ANDI
                    3'b001: alu_control = 4'b0110; // SLLI
                    3'b101: begin
                        if (funct7[5]) alu_control = 4'b1001; // SRAI
                        else           alu_control = 4'b0111; // SRLI
                    end
                    default: alu_control = 4'b0000;
                endcase
            end

            // Load (lw)
            7'b0000011: begin
                reg_write = 1;
                alu_src = 1;
                result_src = 2'b01;
                alu_control = 4'b0000; // ADD (address calc)
            end

            // Store (sw)
            7'b0100011: begin
                alu_src = 1;
                mem_write = 1;
                alu_control = 4'b0000; // ADD (address calc)
            end

            // B-type (BEQ, BNE, BLT, BGE, BLTU, BGEU)
            7'b1100011: begin
                branch = 1;
                alu_src = 0;
                case (funct3)
                    3'b000, 3'b001: alu_control = 4'b0001; // BEQ/BNE: SUB
                    3'b100, 3'b101: alu_control = 4'b0101; // BLT/BGE: SLT (signed)
                    3'b110, 3'b111: alu_control = 4'b1000; // BLTU/BGEU: SLTU (unsigned)
                    default:        alu_control = 4'b0001;
                endcase
            end

            // JAL
            7'b1101111: begin
                reg_write = 1;
                jump = 1;
                result_src = 2'b10; // PC+4
            end

            // JALR
            7'b1100111: begin
                reg_write = 1;
                jalr = 1;
                alu_src = 1;
                alu_control = 4'b0000; // ADD
                result_src = 2'b10;    // PC+4
            end

            // LUI
            7'b0110111: begin
                reg_write = 1;
                alu_src = 1;
                alu_src1 = 2'b10;      // srcA = 0
                alu_control = 4'b0000; // ADD (0 + imm)
            end

            // AUIPC
            7'b0010111: begin
                reg_write = 1;
                alu_src = 1;
                alu_src1 = 2'b01;      // srcA = PC
                alu_control = 4'b0000; // ADD (PC + imm)
            end

            // Custom-0: ROL (Rotate Left) — R-type
            7'b0001011: begin
                reg_write = 1;
                alu_src = 0;
                alu_control = 4'b1010; // ROL
            end

        endcase
    end
endmodule

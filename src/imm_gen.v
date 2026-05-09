module imm_gen(
    input [31:0] instr,
    output reg [31:0] imm_ext
);

    always @(*) begin
        case (instr[6:0])
            7'b0010011, // I-type (ADDI, ORI, etc.)
            7'b0000011: // Load (lw)
                imm_ext = {{20{instr[31]}}, instr[31:20]};

            7'b0100011: // S-type (sw)
                imm_ext = {{20{instr[31]}}, instr[31:25], instr[11:7]};

            7'b1100011: // B-type (BEQ, BNE, BLT, BGE)
                imm_ext = {{20{instr[31]}}, instr[7], instr[30:25], instr[11:8], 1'b0};

            7'b1101111: // J-type (JAL)
                imm_ext = {{12{instr[31]}}, instr[19:12], instr[20], instr[30:21], 1'b0};

            7'b1100111: // I-type (JALR)
                imm_ext = {{20{instr[31]}}, instr[31:20]};

            7'b0110111, // LUI
            7'b0010111: // AUIPC
                imm_ext = {instr[31:12], 12'b0};

            default:
                imm_ext = 32'b0;
        endcase
    end

endmodule

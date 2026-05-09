module alu(
    input [31:0] src1,
    input [31:0] src2,
    input [3:0] alu_control,
    output reg [31:0] result,
    output zero
);

    always @(*) begin
        case (alu_control)
            4'b0000: result = src1 + src2;                                    // ADD
            4'b0001: result = src1 - src2;                                    // SUB
            4'b0010: result = src1 & src2;                                    // AND
            4'b0011: result = src1 | src2;                                    // OR
            4'b0100: result = src1 ^ src2;                                    // XOR
            4'b0101: result = ($signed(src1) < $signed(src2)) ? 1 : 0;       // SLT (signed)
            4'b0110: result = src1 << src2[4:0];                              // SLL
            4'b0111: result = src1 >> src2[4:0];                              // SRL
            4'b1000: result = (src1 < src2) ? 1 : 0;                         // SLTU (unsigned)
            4'b1001: result = $signed(src1) >>> src2[4:0];                    // SRA
            4'b1010: result = (src1 << src2[4:0]) | (src1 >> (32 - src2[4:0])); // ROL (custom)
            default: result = 32'b0;
        endcase
    end

    assign zero = (result == 0) ? 1'b1 : 1'b0;

endmodule

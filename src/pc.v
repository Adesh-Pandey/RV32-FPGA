module pc(
    input clk,
    input rst,
    input en,
    input [31:0] pc_next,
    output reg [31:0] pc
);

    always @(posedge clk) begin
        if (rst)
            pc <= 32'b0;
        else if (en)
            pc <= pc_next;
    end

endmodule

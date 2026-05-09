module imem(
    input [31:0] a,
    output [31:0] rd
);
reg [31:0] RAM [63:0];


    integer i;
    initial begin
        for (i = 0; i < 64; i = i + 1) RAM[i] = 32'h00000013; // Fill with NOPs
        $readmemh("src/program.hex", RAM);
    end

    assign rd = RAM[a[31:2]]; 

endmodule
module pc_adder(
    input [31:0] a,
    output [31:0] y 
);

    assign y = a + 32'd4; 

endmodule
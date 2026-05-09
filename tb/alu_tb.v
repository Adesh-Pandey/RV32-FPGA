`timescale 1ns / 1ps

module alu_tb;

    reg [31:0] src1;
    reg [31:0] src2;
    reg [2:0] alu_control;

    wire [31:0] result;
    wire zero;

    alu uut (
        .src1(src1),
        .src2(src2),
        .alu_control(alu_control),
        .result(result),
        .zero(zero)
    );

    initial begin
        // Setup for simulation waveform
        $dumpfile("alu_test.vcd");
        $dumpvars(0, alu_tb);

        src1 = 100;
        src2 = 20;
        alu_control = 3'b000;
        #10; 

        src1=30;
        src2=10;
        alu_control=3'b010;
        #10;

      
        src1=15;
        src2=15;
        alu_control=3'b001;
        #10;
        
       

        $finish; // End simulation
    end

endmodule
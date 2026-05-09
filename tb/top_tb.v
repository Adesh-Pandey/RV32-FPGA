`timescale 1ns / 1ps
module top_tb;

    reg clk;
    reg reset;

    top uut (
        .clk(clk),
        .reset(reset)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("cpu_test.vcd");
        $dumpvars(0, top_tb);

        clk = 0;
        reset = 1;

        #10;
        reset = 0;

        #600;

        $display("=== Pipeline Hazard Tests ===");

        $display("--- EX/MEM Forwarding (back-to-back) ---");
        $display("x1  = %0d (expect 11, final after test4)", uut.reg_unit.rf[1]);
        $display("x2  = %0d (expect 22, final after test4)", uut.reg_unit.rf[2]);
        $display("x3  = %0d (expect 7,  chain fwd)",         uut.reg_unit.rf[3]);

        $display("--- MEM/WB Forwarding (2-gap) ---");
        $display("x5  = %0d (expect 14, x4+4)",              uut.reg_unit.rf[5]);

        $display("--- Load-Use Hazard (stall + forward) ---");
        $display("x6  = %0d (expect 5,  loaded)",             uut.reg_unit.rf[6]);
        $display("x7  = %0d (expect 6,  load-use fwd)",       uut.reg_unit.rf[7]);

        $display("--- Store Forwarding ---");
        $display("x8  = %0d (expect 20)",                     uut.reg_unit.rf[8]);
        $display("x9  = %0d (expect 20, store-then-load)",    uut.reg_unit.rf[9]);

        $display("--- Branch with Forwarding ---");
        $display("x10 = %0d (expect 5)",                      uut.reg_unit.rf[10]);
        $display("x11 = %0d (expect 5)",                      uut.reg_unit.rf[11]);
        $display("x12 = %0d (expect 0,  branch taken)",       uut.reg_unit.rf[12]);

        $display("");
        $display("=== Performance Counters ===");
        $display("Cycles         = %0d", uut.perf_cycles);
        $display("Instructions   = %0d", uut.perf_instrs);
        $display("Stalls         = %0d", uut.perf_stalls);
        $display("Flushes        = %0d", uut.perf_flushes);
        $display("CPI            = %0f", $itor(uut.perf_cycles) / $itor(uut.perf_instrs));

        $finish;
    end

endmodule

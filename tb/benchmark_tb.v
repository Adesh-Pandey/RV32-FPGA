module benchmark_tb;

    reg clk;
    reg reset;

    top uut (
        .clk(clk),
        .reset(reset)
    );

    always #5 clk = ~clk;

    initial begin
        $dumpfile("benchmark_test.vcd");
        $dumpvars(0, benchmark_tb);

        clk = 0;
        reset = 1;

        // Override instruction memory while CPU is in reset
        $readmemh("src/benchmark.hex", uut.imem_unit.RAM);

        #10;
        reset = 0;

        // Run long enough for fibonacci (8 setup + 8 iters * ~9 cycles + halt margin)
        #1500;

        $display("=== Fibonacci Benchmark Results ===");
        $display("");

        // Register state
        $display("--- Registers ---");
        $display("x1 = %0d (expect 21, F8)",  uut.reg_unit.rf[1]);
        $display("x2 = %0d (expect 34, F9)",  uut.reg_unit.rf[2]);
        $display("x3 = %0d (expect 34, F9)",  uut.reg_unit.rf[3]);
        $display("x4 = %0d (expect 10)",       uut.reg_unit.rf[4]);
        $display("x5 = %0d (expect 10)",       uut.reg_unit.rf[5]);
        $display("x6 = %0d (expect 40)",       uut.reg_unit.rf[6]);

        // Memory: Fibonacci sequence F(0)..F(9)
        $display("");
        $display("--- Data Memory (Fibonacci Sequence) ---");
        $display("mem[0]  = %0d (F0, expect 0)",  uut.dmem_unit.RAM[0]);
        $display("mem[1]  = %0d (F1, expect 1)",  uut.dmem_unit.RAM[1]);
        $display("mem[2]  = %0d (F2, expect 1)",  uut.dmem_unit.RAM[2]);
        $display("mem[3]  = %0d (F3, expect 2)",  uut.dmem_unit.RAM[3]);
        $display("mem[4]  = %0d (F4, expect 3)",  uut.dmem_unit.RAM[4]);
        $display("mem[5]  = %0d (F5, expect 5)",  uut.dmem_unit.RAM[5]);
        $display("mem[6]  = %0d (F6, expect 8)",  uut.dmem_unit.RAM[6]);
        $display("mem[7]  = %0d (F7, expect 13)", uut.dmem_unit.RAM[7]);
        $display("mem[8]  = %0d (F8, expect 21)", uut.dmem_unit.RAM[8]);
        $display("mem[9]  = %0d (F9, expect 34)", uut.dmem_unit.RAM[9]);

        // Performance counters
        $display("");
        $display("=== Performance Counters (5-Stage Pipeline) ===");
        $display("Cycles         = %0d", uut.perf_cycles);
        $display("Instructions   = %0d", uut.perf_instrs);
        $display("Stalls         = %0d", uut.perf_stalls);
        $display("Flushes        = %0d", uut.perf_flushes);
        $display("CPI            = %0f", $itor(uut.perf_cycles) / $itor(uut.perf_instrs));

        $display("");
        $display("=== Comparison: Single-Cycle vs Pipeline ===");
        $display("Single-cycle CPI       = 1.00 (by definition)");
        $display("Pipeline CPI           = %0f", $itor(uut.perf_cycles) / $itor(uut.perf_instrs));
        $display("Pipeline stall overhead = %0d cycles (%0f%%)", uut.perf_stalls,
            100.0 * $itor(uut.perf_stalls) / $itor(uut.perf_cycles));
        $display("Pipeline flush overhead = %0d cycles (%0f%%)", uut.perf_flushes,
            100.0 * $itor(uut.perf_flushes) / $itor(uut.perf_cycles));

        $finish;
    end

endmodule

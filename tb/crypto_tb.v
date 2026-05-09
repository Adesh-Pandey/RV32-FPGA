`timescale 1ns/1ps

module crypto_tb;
    reg clk, reset;

    top uut(.clk(clk), .reset(reset));

    always #5 clk = ~clk;

    // Storage for first run results
    reg [31:0] sw_cycles, sw_instrs, sw_stalls, sw_flushes;
    reg [31:0] sw_a, sw_b, sw_c, sw_d;

    initial begin
        $dumpfile("crypto_test.vcd");
        $dumpvars(0, crypto_tb);

        // ====================================================
        // RUN 1: Software-only (standard RV32I, no ROL)
        // ====================================================
        clk = 0; reset = 1;
        // Load software crypto program
        $readmemh("src/crypto_sw.hex", uut.imem_unit.RAM);
        #12 reset = 0;
        #2000;

        sw_cycles  = uut.perf_cycles;
        sw_instrs  = uut.perf_instrs;
        sw_stalls  = uut.perf_stalls;
        sw_flushes = uut.perf_flushes;
        sw_a = uut.reg_unit.rf[1];
        sw_b = uut.reg_unit.rf[2];
        sw_c = uut.reg_unit.rf[3];
        sw_d = uut.reg_unit.rf[4];

        $display("");
        $display("============================================================");
        $display("  ChaCha20 Quarter-Round Benchmark: SOFTWARE vs HARDWARE");
        $display("============================================================");
        $display("");
        $display("--- SOFTWARE (Standard RV32I) ---");
        $display("Cycles       = %0d", sw_cycles);
        $display("Instructions = %0d", sw_instrs);
        $display("Stalls       = %0d", sw_stalls);
        $display("Flushes      = %0d", sw_flushes);
        $display("CPI          = %f", $itor(sw_cycles) / $itor(sw_instrs));
        $display("a = 0x%08H (expect 0xD576E19B)", sw_a);
        $display("b = 0x%08H (expect 0x1898E8F8)", sw_b);
        $display("c = 0x%08H (expect 0x36858953)", sw_c);
        $display("d = 0x%08H (expect 0x9FF722DF)", sw_d);

        // ====================================================
        // RUN 2: Hardware-accelerated (custom ROL instruction)
        // ====================================================
        reset = 1;
        // Re-init IMEM with NOPs then load hardware crypto program
        begin : reinit
            integer i;
            for (i = 0; i < 64; i = i + 1)
                uut.imem_unit.RAM[i] = 32'h00000013;
        end
        $readmemh("src/crypto_hw.hex", uut.imem_unit.RAM);
        #12 reset = 0;
        #2000;

        $display("");
        $display("--- HARDWARE (Custom ROL Instruction) ---");
        $display("Cycles       = %0d", uut.perf_cycles);
        $display("Instructions = %0d", uut.perf_instrs);
        $display("Stalls       = %0d", uut.perf_stalls);
        $display("Flushes      = %0d", uut.perf_flushes);
        $display("CPI          = %f", $itor(uut.perf_cycles) / $itor(uut.perf_instrs));
        $display("a = 0x%08H (expect 0xD576E19B)", uut.reg_unit.rf[1]);
        $display("b = 0x%08H (expect 0x1898E8F8)", uut.reg_unit.rf[2]);
        $display("c = 0x%08H (expect 0x36858953)", uut.reg_unit.rf[3]);
        $display("d = 0x%08H (expect 0x9FF722DF)", uut.reg_unit.rf[4]);

        $display("");
        $display("============================================================");
        $display("  COMPARISON");
        $display("============================================================");
        $display("                  SOFTWARE    HARDWARE    SAVING");
        $display("Cycles:           %4d        %4d        %0d fewer (%0d%% reduction)",
            sw_cycles, uut.perf_cycles,
            sw_cycles - uut.perf_cycles,
            ((sw_cycles - uut.perf_cycles) * 100) / sw_cycles);
        $display("Instructions:     %4d        %4d        %0d fewer",
            sw_instrs, uut.perf_instrs,
            sw_instrs - uut.perf_instrs);
        $display("Stalls:           %4d        %4d", sw_stalls, uut.perf_stalls);
        $display("Flushes:          %4d        %4d", sw_flushes, uut.perf_flushes);
        $display("CPI:              %f  %f",
            $itor(sw_cycles) / $itor(sw_instrs),
            $itor(uut.perf_cycles) / $itor(uut.perf_instrs));
        $display("");
        $display("Speedup:          %.2fx faster with custom ROL instruction",
            $itor(sw_cycles) / $itor(uut.perf_cycles));
        $display("");

        // Verify both produce identical results
        if (uut.reg_unit.rf[1] == sw_a && uut.reg_unit.rf[2] == sw_b &&
            uut.reg_unit.rf[3] == sw_c && uut.reg_unit.rf[4] == sw_d)
            $display("VERIFIED: Both versions produce identical output!");
        else
            $display("ERROR: Results differ!");

        $display("============================================================");
        $finish;
    end
endmodule

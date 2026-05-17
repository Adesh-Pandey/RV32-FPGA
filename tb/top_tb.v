// `timescale 1ns / 1ps
// module top_tb;

//     reg clk;
//     reg reset;

//     top uut (
//         .clk(clk),
//         .reset(reset)
//     );

//     always #5 clk = ~clk;

//     initial begin
//         $dumpfile("cpu_test.vcd");
//         $dumpvars(0, top_tb);

//         clk = 0;
//         reset = 1;

//         #10;
//         reset = 0;

//         #600;

//         $display("=== Pipeline Hazard Tests ===");

//         $display("--- EX/MEM Forwarding (back-to-back) ---");
//         $display("x1  = %0d (expect 11, final after test4)", uut.reg_unit.rf[1]);
//         $display("x2  = %0d (expect 22, final after test4)", uut.reg_unit.rf[2]);
//         $display("x3  = %0d (expect 7,  chain fwd)",         uut.reg_unit.rf[3]);

//         $display("--- MEM/WB Forwarding (2-gap) ---");
//         $display("x5  = %0d (expect 14, x4+4)",              uut.reg_unit.rf[5]);

//         $display("--- Load-Use Hazard (stall + forward) ---");
//         $display("x6  = %0d (expect 5,  loaded)",             uut.reg_unit.rf[6]);
//         $display("x7  = %0d (expect 6,  load-use fwd)",       uut.reg_unit.rf[7]);

//         $display("--- Store Forwarding ---");
//         $display("x8  = %0d (expect 20)",                     uut.reg_unit.rf[8]);
//         $display("x9  = %0d (expect 20, store-then-load)",    uut.reg_unit.rf[9]);

//         $display("--- Branch with Forwarding ---");
//         $display("x10 = %0d (expect 5)",                      uut.reg_unit.rf[10]);
//         $display("x11 = %0d (expect 5)",                      uut.reg_unit.rf[11]);
//         $display("x12 = %0d (expect 0,  branch taken)",       uut.reg_unit.rf[12]);

//         $display("");
//         $display("=== Performance Counters ===");
//         $display("Cycles         = %0d", uut.perf_cycles);
//         $display("Instructions   = %0d", uut.perf_instrs);
//         $display("Stalls         = %0d", uut.perf_stalls);
//         $display("Flushes        = %0d", uut.perf_flushes);
//         $display("CPI            = %0f", $itor(uut.perf_cycles) / $itor(uut.perf_instrs));

//         $finish;
//     end

// endmodule



`timescale 1ns / 1ps

module top_tb;

    reg clk;
    reg reset;
    
    // Virtual UART Pins
    reg  virtual_rx;
    wire virtual_tx;

    // Instantiate your processor core (Not zybo_top, just the core)
    top dut (
        .clk(clk),
        .reset(reset),
        .o_perf_cycles(),
        .o_perf_instrs(),
        .o_perf_halted(),
        .o_pc(),
        .o_gpio(),
        .i_uart_rx(virtual_rx),
        .o_uart_tx(virtual_tx)
    );

    // 125 MHz Clock Generator (8ns period)
    initial begin
        clk = 0;
        forever #4 clk = ~clk;
    end

    // The timing math for 115200 Baud at 125 MHz
    // 1 bit takes exactly 8680 nanoseconds
    parameter BIT_TIME = 8680;

    // The Simulation Script
    initial begin
        // 1. Setup waveforms for GTKWave
        $dumpfile("sim/uart_sim.vcd");
        $dumpvars(0, top_tb);

        // 2. Initial state
        reset = 1;
        virtual_rx = 1; // UART idles High
        
        #100; // Hold reset for 100ns
        reset = 0;

        // 3. Let the processor boot up and enter the wait loop
        #10000; 

        // 4. FAKE KEYBOARD PRESS: Typing the letter 'A' (Binary: 01000001)
        $display("Simulating typing the letter 'A'...");
        
        virtual_rx = 0; #BIT_TIME; // START BIT (Drops Low)
        
        // Data Bits (Sent Least Significant Bit first)
        virtual_rx = 1; #BIT_TIME; // Bit 0
        virtual_rx = 0; #BIT_TIME; // Bit 1
        virtual_rx = 0; #BIT_TIME; // Bit 2
        virtual_rx = 0; #BIT_TIME; // Bit 3
        virtual_rx = 0; #BIT_TIME; // Bit 4
        virtual_rx = 0; #BIT_TIME; // Bit 5
        virtual_rx = 1; #BIT_TIME; // Bit 6
        virtual_rx = 0; #BIT_TIME; // Bit 7
        
        virtual_rx = 1; #BIT_TIME; // STOP BIT (Goes High)

        // 5. Wait for the processor to catch it and echo it back
        #(BIT_TIME * 15);

        $display("Simulation Complete!");
        $finish;
    end

endmodule

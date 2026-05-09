module regfile_tb;

    reg clk;
    reg we3;
    reg [4:0] a1, a2, a3;
    reg [31:0] wd3;
    wire [31:0] rd1, rd2;

    regfile uut (
        .clk(clk), .we3(we3), 
        .a1(a1), .a2(a2), .a3(a3), .wd3(wd3), 
        .rd1(rd1), .rd2(rd2)
    );

    // 1. Clock Generation Magic
    // This flips the clock every 5ns (Period = 10ns)
    always begin
        #5 clk = ~clk; 
    end

    initial begin
        $dumpfile("regfile_test.vcd");
        $dumpvars(0, regfile_tb);
       

        // Initialize Clock and Write Enable
        clk = 0;
        we3 = 0;

        // Test 1: Write 42 to Register 1
        // We set the data, then wait for a clock edge.
        a3 = 1;      // Select Register 1
        wd3 = 42;    // Data to write
        we3 = 1;     // Enable writing
        #10;         // Wait for clock tick
        we3 = 0;     // Turn off write

        // Test 2: Read Register 1 (Check if 42 comes out)
        a1 = 1;
        #10;

        // Test 3: Try to write to Register 0 (Should fail/stay 0)
        // --- YOU WRITE THIS CODE ---
        // Try writing '99' to address '0', then read address '0' back.
        
        $finish;
    end
endmodule
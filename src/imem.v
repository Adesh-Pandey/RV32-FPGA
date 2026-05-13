module imem(
    input              clk,
    // Write port (bootloader)
    input              we,
    input  [7:0]       waddr,    // word address, 0..255
    input  [31:0]      wdata,
    // Read port (CPU fetch)
    input  [31:0]      a,        // byte address from PC
    output [31:0]      rd
);

    // 256 words = 1 KB program memory. Matches the bootloader length-byte range.
    reg [31:0] RAM [255:0];

    integer i;
    initial begin
        for (i = 0; i < 256; i = i + 1) RAM[i] = 32'h00000013; // NOPs
    end

    always @(posedge clk) begin
        if (we) RAM[waddr] <= wdata;
    end

    assign rd = RAM[a[9:2]];
endmodule

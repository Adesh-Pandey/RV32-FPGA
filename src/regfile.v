module regfile(
    input clk,
    input we3,
    input [4:0] a1,
    input [4:0] a2,
    input [4:0] a3,
    input [31:0] wd3,    
    output [31:0] rd1,   
    output [31:0] rd2    
);

reg [31:0] rf [31:0];
always @(posedge clk) begin
    if(we3)
        rf[a3]=wd3;
    
end
    // Write-through: if WB writes the same register ID is reading
    // in the same cycle, forward the written value directly.
    assign rd1 = (a1 == 5'b0)                  ? 32'b0 :
                 (we3 && a3 == a1 && a3 != 5'b0) ? wd3   : rf[a1];
    assign rd2 = (a2 == 5'b0)                  ? 32'b0 :
                 (we3 && a3 == a2 && a3 != 5'b0) ? wd3   : rf[a2];

endmodule
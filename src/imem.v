// module imem(
//     input [31:0] a,
//     output [31:0] rd
// );
// reg [31:0] RAM [63:0];


//     integer i;
//     initial begin
//         for (i = 0; i < 64; i = i + 1) RAM[i] = 32'h00000013; // Fill with NOPs
//         $readmemh("C:/Coding/RV32-FPGA/src/uart_letter_custom.hex", RAM);
//     end

//     assign rd = RAM[a[31:2]]; 

// endmodule

module imem (
    input  wire        clk,
    
    // Port A: CPU Read Port (For executing instructions)
    input  wire [31:0] a,
    output wire [31:0] rd,
    
    // Port B: Bootloader Write Port (For injecting new programs)
    input  wire        we,
    input  wire [31:0] a_write,
    input  wire [31:0] wd
);
    reg [31:0] RAM[0:1023]; // 4KB of Instruction Memory
    integer i;

    // Keep this so it still boots a default program when you turn it on
    initial begin
       for (i = 0; i < 64; i = i + 1) RAM[i] = 32'h00000013; // Fill with NOPs
       $readmemh("C:/Coding/RV32-FPGA/src/uart_letter_custom.hex", RAM);
    end

    // The Loader writes to memory here
    always @(posedge clk) begin
        if (we) begin
            RAM[a_write[31:2]] <= wd; 
        end
    end

    // The CPU fetches from memory here
    assign rd = RAM[a[31:2]];
endmodule
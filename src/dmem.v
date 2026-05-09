module dmem(
    input  clk,
    input  we,
    input  [31:0] a,
    input  [31:0] wd,
    output [31:0] rd,
    output reg [4:0] gpio_out
);

    parameter GPIO_ADDR = 32'h0000_0100;

    reg [31:0] RAM [63:0];

    initial gpio_out = 5'b0;

    wire is_gpio = (a == GPIO_ADDR);

    assign rd = is_gpio ? {27'b0, gpio_out} : RAM[a[7:2]];

    always @(posedge clk) begin
        if (we) begin
            if (is_gpio)
                gpio_out <= wd[4:0];
            else
                RAM[a[7:2]] <= wd;
        end
    end
endmodule

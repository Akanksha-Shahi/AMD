module alu(
    input wire a,
    input wire b,
    input wire sel,
    output reg y
);

always @(*) begin
    if (sel == 0) begin
        y = a & b;
    end else begin
        y = a | b;
    end
end

endmodule

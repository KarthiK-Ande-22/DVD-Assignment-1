module full_adder (
    input  a,
    input  b,
    input  cin,
    output sum,
    output cout
);

    // Sum is the odd-parity result of the three full-adder inputs.
    assign sum  = a ^ b ^ cin;
    // Carry is asserted when at least two of the three inputs are high.
    assign cout = (a & b) | (b & cin) | (a & cin);

endmodule

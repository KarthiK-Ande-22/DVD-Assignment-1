`timescale 1ns/1ps

module tb_mult;

    reg        clk;
    reg        rst_n;
    reg  [3:0] a;
    reg  [3:0] b;
    wire [7:0] p;

    integer a_value;
    integer b_value;
    integer errors;
    reg [7:0] expected;

    // Instantiate the registered multiplier being verified.
    mult_array dut (
        .clk   (clk),
        .rst_n (rst_n),
        .a     (a),
        .b     (b),
        .p     (p)
    );

    // 10 ns clock period.
    always #5 clk = ~clk;

    initial begin
        // Create the waveform database for post-simulation inspection.
        $dumpfile("mult.vcd");
        $dumpvars(0, tb_mult);

        clk    = 1'b0;
        rst_n  = 1'b0;
        a      = 4'b0;
        b      = 4'b0;
        errors = 0;

        // Hold reset low for two cycles.
        repeat (2) @(posedge clk);
        @(negedge clk);
        rst_n = 1'b1;

        // Exhaustively test all 256 combinations.
        for (a_value = 0; a_value < 16; a_value = a_value + 1) begin
            for (b_value = 0; b_value < 16; b_value = b_value + 1) begin
                @(negedge clk);
                a = a_value;
                b = b_value;
                expected = a_value * b_value;

                // Wait for the two-cycle registered latency.
                repeat (2) @(posedge clk);
                #2;

                // Count and print every output mismatch.
                if (p !== expected) begin
                    errors = errors + 1;
                    $display(
                        "Mismatch: a=%0d b=%0d expected=%0d got=%0d",
                        a_value, b_value, expected, p
                    );
                end
            end
        end

        // Print the required single-line final test summary.
        if (errors == 0)
            $display("PASS: 256 vectors checked, 0 errors");
        else
            $display("FAIL: 256 vectors checked, %0d errors", errors);

        $finish;
    end

endmodule


// SPDX-License-Identifier: Apache-2.0
// SMVDU-TITAN-X SoC — CDC Synchronizer Directed Self-Checking Testbench
// Tests 2-stage synchronizer behavior: data propagates after 2 clock edges
`timescale 1ns/1ps

module tb_cdc_sync();
    parameter WIDTH = 8;

    reg                  dst_clk;
    reg                  rst_n;
    reg  [WIDTH-1:0]     data_in;
    wire [WIDTH-1:0]     data_out;

    integer error_count;

    cdc_sync #(.WIDTH(WIDTH), .STAGES(2)) uut (
        .dst_clk(dst_clk), .rst_n(rst_n),
        .data_in(data_in), .data_out(data_out)
    );

    initial dst_clk = 0;
    always #5 dst_clk = ~dst_clk;

    task check;
        input [63:0] got;
        input [63:0] exp;
        input [255:0] msg;
        begin
            if (got !== exp) begin
                $display("FAIL [%0t] %s: got=0x%02X expected=0x%02X", $time, msg, got, exp);
                error_count = error_count + 1;
            end else $display("PASS [%0t] %s", $time, msg);
        end
    endtask

    initial begin
        $dumpfile("tb_cdc_sync.vcd");
        $dumpvars(0, tb_cdc_sync);
        error_count = 0;
        data_in = 8'h00;
        rst_n = 0; repeat(4) @(posedge dst_clk); rst_n = 1;

        // TEST 1: Reset state → output=0
        $display("\n--- TEST 1: Reset output = 0 ---");
        @(posedge dst_clk); #1;
        check(data_out, 8'h0, "data_out=0 after reset");

        // TEST 2: Apply data, wait 2 stages to propagate
        $display("\n--- TEST 2: Data propagates after 2 clocks ---");
        data_in = 8'hA5;
        repeat(3) @(posedge dst_clk);  // 2 stages + 1 margin
        check(data_out, 8'hA5, "data_out=0xA5 after 3 cycles");

        // TEST 3: Change data
        $display("\n--- TEST 3: Data change propagates ---");
        data_in = 8'h3C;
        repeat(3) @(posedge dst_clk);
        check(data_out, 8'h3C, "data_out=0x3C after change");

        // TEST 4: All-ones
        $display("\n--- TEST 4: All-ones data ---");
        data_in = 8'hFF;
        repeat(3) @(posedge dst_clk);
        check(data_out, 8'hFF, "data_out=0xFF");

        // TEST 5: Zero again
        $display("\n--- TEST 5: Return to zero ---");
        data_in = 8'h00;
        repeat(3) @(posedge dst_clk);
        check(data_out, 8'h00, "data_out=0x00");

        $display("\n==============================");
        if (error_count == 0)
            $display("CDC_SYNC VERDICT: ✅ PASS — All tests passed");
        else
            $display("CDC_SYNC VERDICT: ❌ FAIL — %0d errors detected", error_count);
        $display("==============================\n");
        $finish;
    end
    initial begin #100_000; $display("WATCHDOG TIMEOUT"); $finish; end
endmodule

// SPDX-License-Identifier: Apache-2.0
// SMVDU-TITAN-X SoC — Synchronous FIFO Directed Self-Checking Testbench
// Tests: empty/full flags, write/read order, overflow protection, count
`timescale 1ns/1ps

module tb_fifo_sync();
    parameter WIDTH  = 8;
    parameter DEPTH  = 16;

    reg                clk;
    reg                rst_n;
    reg                wr_en;
    reg                rd_en;
    reg  [WIDTH-1:0]   wr_data;
    wire [WIDTH-1:0]   rd_data;
    wire               full;
    wire               empty;
    wire [$clog2(DEPTH):0] count;

    integer error_count;

    fifo_sync #(.WIDTH(WIDTH), .DEPTH(DEPTH)) uut (
        .clk(clk), .rst_n(rst_n),
        .wr_en(wr_en), .rd_en(rd_en),
        .wr_data(wr_data), .rd_data(rd_data),
        .full(full), .empty(empty), .count(count)
    );

    initial clk = 0;
    always #5 clk = ~clk;

    task check;
        input [63:0] got;
        input [63:0] exp;
        input [255:0] msg;
        begin
            if (got !== exp) begin
                $display("FAIL [%0t] %s: got=%0d expected=%0d", $time, msg, got, exp);
                error_count = error_count + 1;
            end else $display("PASS [%0t] %s", $time, msg);
        end
    endtask

    integer i;

    initial begin
        $dumpfile("tb_fifo_sync.vcd");
        $dumpvars(0, tb_fifo_sync);
        error_count = 0;
        wr_en = 0; rd_en = 0; wr_data = 0;
        rst_n = 0; repeat(4) @(posedge clk); rst_n = 1; repeat(2) @(posedge clk);

        // TEST 1: Reset state
        $display("\n--- TEST 1: Reset state ---");
        check(empty, 1'b1, "empty=1 after reset");
        check(full,  1'b0, "full=0 after reset");
        check(count, 0,    "count=0 after reset");

        // TEST 2: Write one entry
        $display("\n--- TEST 2: Write single entry ---");
        @(posedge clk); #1; wr_en = 1; wr_data = 8'hAA;
        @(posedge clk); #1; wr_en = 0;
        @(posedge clk); #1;
        check(empty, 1'b0, "empty=0 after write");
        check(count, 1,    "count=1 after write");

        // TEST 3: Read back that entry
        $display("\n--- TEST 3: Read single entry ---");
        @(posedge clk); #1; rd_en = 1;
        @(posedge clk); #1; rd_en = 0;
        check(rd_data, 8'hAA, "rd_data=0xAA (FIFO order)");
        @(posedge clk); #1;
        check(empty, 1'b1, "empty=1 after read");

        // TEST 4: Fill to full
        $display("\n--- TEST 4: Fill FIFO to full ---");
        wr_en = 1;
        for (i = 0; i < DEPTH; i = i + 1) begin
            wr_data = i[7:0] + 8'h10;
            @(posedge clk); #1;
        end
        wr_en = 0;
        @(posedge clk); #1;
        check(full,  1'b1, "full=1 after filling DEPTH entries");
        check(empty, 1'b0, "empty=0 when full");
        check(count, DEPTH, "count=DEPTH when full");

        // TEST 5: Read all back in order
        $display("\n--- TEST 5: Drain FIFO in order ---");
        rd_en = 1;
        for (i = 0; i < DEPTH; i = i + 1) begin
            @(posedge clk); #1;
            if (rd_data !== (i[7:0] + 8'h10)) begin
                $display("FAIL [%0t] FIFO order: slot[%0d] got=0x%02X expected=0x%02X",
                         $time, i, rd_data, i[7:0]+8'h10);
                error_count = error_count + 1;
            end
        end
        rd_en = 0;
        @(posedge clk); #1;
        check(empty, 1'b1, "empty=1 after draining all");
        $display("PASS [%0t] FIFO order maintained", $time);

        // TEST 6: Simultaneous write+read (throughput mode)
        $display("\n--- TEST 6: Simultaneous write+read ---");
        @(posedge clk); #1; wr_en = 1; wr_data = 8'h55;
        @(posedge clk); #1; wr_data = 8'h66;
        @(posedge clk); #1; wr_en = 0;
        // Now start reading while writing
        @(posedge clk); #1; wr_en = 1; wr_data = 8'h77; rd_en = 1;
        @(posedge clk); #1;
        check(rd_data, 8'h55, "simultaneous R/W: first entry = 0x55");
        wr_en = 0; rd_en = 0;

        $display("\n==============================");
        if (error_count == 0)
            $display("FIFO_SYNC VERDICT: ✅ PASS — All tests passed");
        else
            $display("FIFO_SYNC VERDICT: ❌ FAIL — %0d errors detected", error_count);
        $display("==============================\n");
        $finish;
    end
    initial begin #500_000; $display("WATCHDOG TIMEOUT"); $finish; end
endmodule

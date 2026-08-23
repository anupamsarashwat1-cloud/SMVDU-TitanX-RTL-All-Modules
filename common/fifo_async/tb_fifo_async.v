// SPDX-License-Identifier: Apache-2.0
// SMVDU-TITAN-X SoC — Asynchronous FIFO Directed Self-Checking Testbench
// Tests: write/read across clock domains, empty/full flags, Gray code CDC
`timescale 1ns/1ps

module tb_fifo_async();
    parameter WIDTH  = 8;
    parameter DEPTH  = 16;

    reg                wr_clk;
    reg                wr_rst_n;
    reg                wr_en;
    reg  [WIDTH-1:0]   wr_data;
    wire               full;

    reg                rd_clk;
    reg                rd_rst_n;
    reg                rd_en;
    wire [WIDTH-1:0]   rd_data;
    wire               empty;

    integer error_count;

    fifo_async #(.WIDTH(WIDTH), .DEPTH(DEPTH)) uut (
        .wr_clk(wr_clk), .wr_rst_n(wr_rst_n),
        .wr_en(wr_en), .wr_data(wr_data), .full(full),
        .rd_clk(rd_clk), .rd_rst_n(rd_rst_n),
        .rd_en(rd_en), .rd_data(rd_data), .empty(empty)
    );

    // Different clock frequencies: WR=100MHz, RD=60MHz
    initial wr_clk = 0;
    always #5  wr_clk = ~wr_clk;   // 100 MHz
    initial rd_clk = 0;
    always #8.3 rd_clk = ~rd_clk;  // ~60 MHz

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

    integer i;
    reg [7:0] expected_data [0:15];

    initial begin
        $dumpfile("tb_fifo_async.vcd");
        $dumpvars(0, tb_fifo_async);
        error_count = 0;
        wr_en = 0; rd_en = 0; wr_data = 0;

        // Assert resets
        wr_rst_n = 0; rd_rst_n = 0;
        repeat(6) @(posedge wr_clk);
        repeat(6) @(posedge rd_clk);
        wr_rst_n = 1; rd_rst_n = 1;
        repeat(6) @(posedge wr_clk);

        // TEST 1: Reset state
        $display("\n--- TEST 1: Reset state ---");
        check(empty, 1'b1, "empty=1 after reset");
        check(full,  1'b0, "full=0 after reset");

        // TEST 2: Write 4 entries on WR side
        $display("\n--- TEST 2: Write 4 entries ---");
        for (i = 0; i < 4; i = i + 1) begin
            expected_data[i] = 8'hA0 + i;
            @(posedge wr_clk); #1;
            wr_en = 1; wr_data = expected_data[i];
        end
        @(posedge wr_clk); #1; wr_en = 0;
        // Wait for Gray code to sync across to RD domain
        repeat(10) @(posedge rd_clk);
        check(empty, 1'b0, "empty=0 after writing 4 entries");

        // TEST 3: Read 4 entries on RD side (slower clock)
        $display("\n--- TEST 3: Read 4 entries ---");
        for (i = 0; i < 4; i = i + 1) begin
            @(posedge rd_clk); #1; rd_en = 1;
            @(posedge rd_clk); #1; rd_en = 0;
            if (rd_data !== expected_data[i]) begin
                $display("FAIL [%0t] FIFO[%0d]: got=0x%02X expected=0x%02X",
                         $time, i, rd_data, expected_data[i]);
                error_count = error_count + 1;
            end else $display("PASS [%0t] rd_data[%0d]=0x%02X", $time, i, rd_data);
        end
        repeat(8) @(posedge rd_clk);
        check(empty, 1'b1, "empty=1 after reading all entries");

        // TEST 4: Fill to full
        $display("\n--- TEST 4: Fill FIFO to full ---");
        for (i = 0; i < DEPTH; i = i + 1) begin
            @(posedge wr_clk); #1; wr_en = 1; wr_data = i[7:0] + 8'h30;
        end
        @(posedge wr_clk); #1; wr_en = 0;
        repeat(6) @(posedge wr_clk);
        check(full, 1'b1, "full=1 after writing DEPTH entries");

        // TEST 5: Drain all
        $display("\n--- TEST 5: Drain FIFO ---");
        repeat(6) @(posedge rd_clk); // wait for sync
        for (i = 0; i < DEPTH; i = i + 1) begin
            @(posedge rd_clk); #1; rd_en = 1;
            @(posedge rd_clk); #1; rd_en = 0;
        end
        repeat(10) @(posedge rd_clk);
        check(empty, 1'b1, "empty=1 after draining all");
        $display("PASS [%0t] Async FIFO drain complete", $time);

        $display("\n==============================");
        if (error_count == 0)
            $display("FIFO_ASYNC VERDICT: ✅ PASS — All tests passed");
        else
            $display("FIFO_ASYNC VERDICT: ❌ FAIL — %0d errors detected", error_count);
        $display("==============================\n");
        $finish;
    end
    initial begin #500_000; $display("WATCHDOG TIMEOUT"); $finish; end
endmodule

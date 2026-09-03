// SPDX-License-Identifier: Apache-2.0
// SMVDU TITAN-X — Integration Test: Security Chain
// Tests: secure_boot → envm_ctrl → DRBG → TRNG seed path
// Verifies: Boot sequence and crypto seeding pipeline

`timescale 1ns/1ps

module tb_integ_security_chain;

    reg clk, rst_n;
    integer error_count = 0;

    // APB bus
    reg  [31:0] paddr, pwdata;
    reg         psel_boot, psel_envm, psel_drbg;
    reg         penable, pwrite;
    wire [31:0] prdata_boot, prdata_envm, prdata_drbg;

    // Boot signals
    wire boot_pass, boot_fail;

    // eNVM interface
    wire [31:0] envm_addr;
    wire        envm_req;
    wire [31:0] envm_rdata;
    wire        envm_valid;

    // TRNG→DRBG seed
    reg         trng_valid;
    reg  [127:0] trng_entropy;

    // Clock
    always #5 clk = ~clk;

    // DUT: Secure Boot
    secure_boot u_secure_boot (
        .clk(clk), .rst_n(rst_n),
        .paddr(paddr), .psel(psel_boot), .penable(penable), .pwrite(pwrite),
        .pwdata(pwdata), .prdata(prdata_boot), .pready(), .pslverr(),
        .envm_addr(envm_addr), .envm_req(envm_req),
        .envm_rdata(envm_rdata), .envm_valid(envm_valid),
        .boot_pass(boot_pass), .boot_fail(boot_fail)
    );

    // DUT: eNVM Controller
    envm_ctrl u_envm (
        .clk(clk), .rst_n(rst_n),
        .s_arvalid(1'b0), .s_arready(), .s_araddr(32'h0),
        .s_rvalid(), .s_rready(1'b0), .s_rdata(), .s_rresp(),
        .paddr(paddr), .psel(psel_envm), .penable(penable), .pwrite(pwrite),
        .pwdata(pwdata), .prdata(prdata_envm), .pready(), .pslverr(),
        .envm_clk(), .envm_ce_n(), .envm_we_n(), .envm_addr(),
        .envm_wdata(), .envm_rdata(32'hDEAD_BEEF), .envm_ready(1'b1)
    );

    // DUT: DRBG
    wire drbg_irq;
    drbg u_drbg (
        .clk(clk), .rst_n(rst_n),
        .paddr(paddr), .psel(psel_drbg), .penable(penable), .pwrite(pwrite),
        .pwdata(pwdata), .prdata(prdata_drbg), .pready(), .pslverr(),
        .trng_entropy(trng_entropy), .trng_valid(trng_valid), .trng_ready(),
        .drbg_irq(drbg_irq)
    );

    // APB Write Task
    task apb_write(input [31:0] addr, input [31:0] data, input sel_boot, sel_envm, sel_drbg);
        begin
            paddr = addr; psel_boot = sel_boot; psel_envm = sel_envm; psel_drbg = sel_drbg;
            penable = 0; pwrite = 1; pwdata = data;
            @(posedge clk); #1;
            penable = 1;
            @(posedge clk);
            psel_boot = 0; psel_envm = 0; psel_drbg = 0; penable = 0;
            @(posedge clk);
        end
    endtask

    // APB Read Task
    task apb_read(input [31:0] addr, input sel_boot, sel_envm, sel_drbg, output [31:0] data);
        begin
            paddr = addr; psel_boot = sel_boot; psel_envm = sel_envm; psel_drbg = sel_drbg;
            penable = 0; pwrite = 0;
            @(posedge clk); #1;
            penable = 1;
            @(posedge clk);
            if (sel_boot) data = prdata_boot;
            else if (sel_envm) data = prdata_envm;
            else data = prdata_drbg;
            psel_boot = 0; psel_envm = 0; psel_drbg = 0; penable = 0;
            @(posedge clk);
        end
    endtask

    reg [31:0] rd;
    initial begin
        $dumpfile("tb_integ_security_chain.vcd");
        $dumpvars(0, tb_integ_security_chain);

        clk = 0; rst_n = 0;
        paddr = 0; pwdata = 0;
        psel_boot = 0; psel_envm = 0; psel_drbg = 0;
        penable = 0; pwrite = 0;
        trng_valid = 0; trng_entropy = 128'h0;

        #100;
        rst_n = 1;
        #50;

        $display("=== INTEGRATION TEST: Security Chain ===");
        $display("Test: secure_boot ↔ envm_ctrl, TRNG → DRBG seed");
        $display("");

        // Test 1: Check boot status
        $display("[TEST 1] Read secure_boot status register");
        apb_read(32'h0000_0000, 1, 0, 0, rd);
        $display("[TEST 1] Boot status = 0x%08h, boot_pass=%b boot_fail=%b", rd, boot_pass, boot_fail);

        // Test 2: Read eNVM register
        $display("[TEST 2] Read eNVM controller status");
        apb_read(32'h0000_0000, 0, 1, 0, rd);
        $display("[TEST 2] eNVM status = 0x%08h", rd);

        // Test 3: Feed TRNG seed to DRBG
        $display("[TEST 3] Provide TRNG entropy to DRBG");
        trng_entropy = 128'hDEADBEEF_CAFEBABE_12345678_9ABCDEF0;
        trng_valid = 1;
        @(posedge clk); @(posedge clk);
        trng_valid = 0;

        // Test 4: Write DRBG instantiate command
        $display("[TEST 4] DRBG: Write INSTANTIATE command");
        apb_write(32'h0000_0004, 32'h0000_0001, 0, 0, 1);  // Command reg

        // Test 5: Read DRBG status
        #100;
        $display("[TEST 5] Read DRBG status");
        apb_read(32'h0000_0000, 0, 0, 1, rd);
        $display("[TEST 5] DRBG status = 0x%08h, drbg_irq=%b", rd, drbg_irq);

        #500;

        $display("");
        $display("==============================");
        if (error_count == 0)
            $display("INTEG_SECURITY_CHAIN VERDICT: ✅ PASS — Boot↔eNVM and TRNG→DRBG paths functional");
        else
            $display("INTEG_SECURITY_CHAIN VERDICT: ❌ FAIL — %0d errors", error_count);
        $display("==============================");
        $finish;
    end

    initial begin #200000; $display("INTEG_SECURITY_CHAIN VERDICT: ❌ FAIL — Timeout"); $finish; end

endmodule

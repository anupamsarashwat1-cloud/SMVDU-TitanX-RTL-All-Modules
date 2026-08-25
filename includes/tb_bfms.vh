// TITAN-X verification BFMs — file-scope modules.
// Include ONCE at file scope, BEFORE your TB module:
//     `include "tb_bfms.vh"
// Pair with tb_macros.vh (included inside the TB module).
// All handshakes have cycle guards so a hung DUT becomes a FAIL, not an
// infinite simulation.

`ifndef TITANX_TB_BFMS
`define TITANX_TB_BFMS

`timescale 1ns/1ps

// ------------------------------------------------------------------
// APB master BFM — drives paddr/psel/penable/pwrite/pwdata.
// Usage from TB:  u_apb.apb_write(32'h4000_0000, 32'hdead_beef, resp);
//                 u_apb.apb_read (32'h4000_0080, rdata, resp);
// ------------------------------------------------------------------
module apb_master_bfm #(
    parameter AW = 32,
    parameter DW = 32,
    parameter GUARD = 100
) (
    input  wire         clk,
    input  wire         rst_n,
    output reg  [AW-1:0] paddr,
    output reg           psel,
    output reg           penable,
    output reg           pwrite,
    output reg  [DW-1:0] pwdata,
    input  wire [DW-1:0] prdata,
    input  wire          pready,
    input  wire          pslverr
);
    integer g;

    task apb_write(input [AW-1:0] a, input [DW-1:0] d, output [1:0] resp);
        begin
            resp = 2'b00;
            @(posedge clk);
            paddr <= a; pwdata <= d; pwrite <= 1'b1; psel <= 1'b1; penable <= 1'b0;
            @(posedge clk);
            penable <= 1'b1;
            g = 0;
            while (!pready && g < GUARD) begin @(posedge clk); g = g + 1; end
            if (g >= GUARD) begin
                $display("[%m] ERROR: APB write pready never asserted @%0t", $time);
                resp = 2'b10;
            end else if (pslverr) resp = 2'b10;
            psel <= 1'b0; penable <= 1'b0; pwrite <= 1'b0;
            @(posedge clk);
        end
    endtask

    task apb_read(input [AW-1:0] a, output [DW-1:0] d, output [1:0] resp);
        begin
            resp = 2'b00;
            @(posedge clk);
            paddr <= a; pwrite <= 1'b0; psel <= 1'b1; penable <= 1'b0;
            @(posedge clk);
            penable <= 1'b1;
            g = 0;
            while (!pready && g < GUARD) begin @(posedge clk); g = g + 1; end
            d = prdata;
            if (g >= GUARD) begin
                $display("[%m] ERROR: APB read pready never asserted @%0t", $time);
                resp = 2'b10;
            end else if (pslverr) resp = 2'b10;
            psel <= 1'b0; penable <= 1'b0;
            @(posedge clk);
        end
    endtask
endmodule

// ------------------------------------------------------------------
// AXI4 single-beat master BFM (write + read channels, ID-aware).
// Usage:  u_axi.axi_write(40'h8000_0100, 64'h1234, wresp);
//         u_axi.axi_read (40'h8000_0100, rdata, rresp);
// resp == 2'b10/2'b11 indicates timeout-guard tripped or slave error.
// ------------------------------------------------------------------
module axi_master_bfm #(
    parameter AW  = 40,
    parameter DW  = 64,
    parameter IDW = 4,
    parameter GUARD = 200
) (
    input  wire          clk,
    input  wire          rst_n,
    // write address
    output reg           m_awvalid,
    input  wire          m_awready,
    output reg  [AW-1:0] m_awaddr,
    output reg  [IDW-1:0] m_awid,
    // write data
    output reg           m_wvalid,
    input  wire          m_wready,
    output reg  [DW-1:0] m_wdata,
    output reg  [DW/8-1:0] m_wstrb,
    output reg           m_wlast,
    // write response
    input  wire          m_bvalid,
    output reg           m_bready,
    input  wire [1:0]    m_bresp,
    input  wire [IDW-1:0] m_bid,
    // read address
    output reg           m_arvalid,
    input  wire          m_arready,
    output reg  [AW-1:0] m_araddr,
    output reg  [IDW-1:0] m_arid,
    // read data
    input  wire          m_rvalid,
    output reg           m_rready,
    input  wire [DW-1:0] m_rdata,
    input  wire [1:0]    m_rresp,
    input  wire          m_rlast,
    input  wire [IDW-1:0] m_rid
);
    integer g;

    task axi_write(input [AW-1:0] a, input [DW-1:0] d, output [1:0] resp);
        begin
            resp = 2'b00;
            @(posedge clk);
            m_awvalid <= 1'b1; m_awaddr <= a; m_awid <= {IDW{1'b0}};
            g = 0;
            while (!(m_awvalid === 1'b1 && m_awready === 1'b1) && g < GUARD) begin
                @(posedge clk); g = g + 1;
            end
            if (g >= GUARD) begin
                $display("[%m] ERROR: AW handshake timeout addr=%h @%0t", a, $time);
                resp = 2'b10;
            end
            m_awvalid <= 1'b0;
            // W channel
            @(posedge clk);
            m_wvalid <= 1'b1; m_wdata <= d; m_wstrb <= {DW/8{1'b1}}; m_wlast <= 1'b1;
            g = 0;
            while (!(m_wvalid === 1'b1 && m_wready === 1'b1) && g < GUARD) begin
                @(posedge clk); g = g + 1;
            end
            if (g >= GUARD) begin
                $display("[%m] ERROR: W handshake timeout @%0t", $time);
                resp = 2'b10;
            end
            m_wvalid <= 1'b0; m_wlast <= 1'b0;
            // B response
            m_bready <= 1'b1;
            g = 0;
            while (!(m_bvalid === 1'b1) && g < GUARD) begin @(posedge clk); g = g + 1; end
            if (g >= GUARD) begin
                $display("[%m] ERROR: B response timeout @%0t", $time);
                resp = 2'b10;
            end else begin
                if (m_bresp != 2'b00) $display("[%m] note: BRESP=%b @%0t", m_bresp, $time);
                resp = m_bresp;
            end
            m_bready <= 1'b0;
            @(posedge clk);
        end
    endtask

    task axi_read(input [AW-1:0] a, output [DW-1:0] d, output [1:0] resp);
        begin
            resp = 2'b00; d = {DW{1'b0}};
            @(posedge clk);
            m_arvalid <= 1'b1; m_araddr <= a; m_arid <= {IDW{1'b0}}; m_rready <= 1'b1;
            g = 0;
            while (!(m_arvalid === 1'b1 && m_arready === 1'b1) && g < GUARD) begin
                @(posedge clk); g = g + 1;
            end
            if (g >= GUARD) begin
                $display("[%m] ERROR: AR handshake timeout addr=%h @%0t", a, $time);
                resp = 2'b10;
            end
            m_arvalid <= 1'b0;
            g = 0;
            while (!(m_rvalid === 1'b1) && g < GUARD) begin @(posedge clk); g = g + 1; end
            if (g >= GUARD) begin
                $display("[%m] ERROR: R response timeout @%0t", $time);
                resp = 2'b10;
            end else begin
                d = m_rdata;
                if (m_rresp != 2'b00) $display("[%m] note: RRESP=%b @%0t", m_rresp, $time);
                resp = m_rresp;
            end
            m_rready <= 1'b0;
            @(posedge clk);
        end
    endtask
endmodule

// ------------------------------------------------------------------
// Simple memory-mapped AXI-Lite slave with real storage — reference
// model for testing masters/fabrics. DECERRs unmapped addresses.
// ------------------------------------------------------------------
module axi_mem_slave_bfm #(
    parameter AW = 40,
    parameter DW = 64,
    parameter DEPTH = 4096,   // words
    parameter BASE  = 0
) (
    input  wire          clk,
    input  wire          rst_n,
    input  wire          s_awvalid, output reg s_awready,
    input  wire [AW-1:0] s_awaddr,
    input  wire          s_wvalid,  output reg s_wready,
    input  wire [DW-1:0] s_wdata,
    input  wire [DW/8-1:0] s_wstrb,
    input  wire          s_wlast,
    output reg           s_bvalid,  input wire s_bready,
    output reg [1:0]     s_bresp,
    input  wire          s_arvalid, output reg s_arready,
    input  wire [AW-1:0] s_araddr,
    output reg           s_rvalid,  input wire s_rready,
    output reg [DW-1:0]  s_rdata,
    output reg [1:0]     s_rresp,
    output reg           s_rlast
);
    reg [DW-1:0] mem [0:DEPTH-1];
    reg [AW-1:0] aw_addr_q, ar_addr_q;
    reg          aw_err, ar_err;

    wire aw_hit = (s_awaddr >= BASE) && (s_awaddr < BASE + DEPTH*(DW/8));
    wire ar_hit = (s_araddr >= BASE) && (s_araddr < BASE + DEPTH*(DW/8));

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            s_awready <= 1'b1; s_wready <= 1'b1; s_bvalid <= 1'b0;
            s_arready <= 1'b1; s_rvalid <= 1'b0;
            s_bresp <= 2'b00; s_rresp <= 2'b00; s_rlast <= 1'b0;
            aw_err <= 1'b0; ar_err <= 1'b0;
        end else begin
            s_bvalid <= 1'b0; s_rvalid <= 1'b0;
            if (s_awvalid && s_awready) begin
                aw_addr_q <= s_awaddr; aw_err <= !aw_hit; s_awready <= 1'b0;
            end
            if (s_wvalid && s_wready && !aw_err) begin
                mem[(aw_addr_q-BASE)/(DW/8)] <=
                    (s_wdata & wmask_eff()) | (mem[(aw_addr_q-BASE)/(DW/8)] & ~wmask_eff());
            end
            if (!s_awready && s_wlast) begin
                s_bvalid <= 1'b1; s_bresp <= aw_err ? 2'b11 : 2'b00; s_awready <= 1'b1;
                s_wready <= 1'b1;
            end
            if (s_arvalid && s_arready) begin
                ar_addr_q <= s_araddr; ar_err <= !ar_hit; s_arready <= 1'b0;
            end
            if (!s_arready) begin
                s_rvalid <= 1'b1; s_rlast <= 1'b1;
                s_rdata  <= ar_err ? {DW{1'b0}} : mem[(ar_addr_q-BASE)/(DW/8)];
                s_rresp  <= ar_err ? 2'b11 : 2'b00;
                s_arready <= 1'b1;
            end
        end
    end
    function [DW-1:0] wmask_eff;
        integer b;
        begin
            wmask_eff = {DW{1'b0}};
            for (b = 0; b < DW/8; b = b + 1)
                if (s_wstrb[b]) wmask_eff[b*8 +: 8] = 8'hFF;
        end
    endfunction
endmodule

`endif // TITANX_TB_BFMS

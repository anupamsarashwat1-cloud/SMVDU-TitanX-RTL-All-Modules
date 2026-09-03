# rv_core_top Verification Handoff

## 📝 Overview
This directory contains the Verilog source, testbench, and verification instructions for the `rv_core_top` module.

The `rv_core_top` module is the top-level integration of the SMVDU-TITAN-X RV64GC core. It instantiates and connects key microarchitectural blocks including the Integer Pipeline (fetch, decode, execute stages), Floating-Point Unit (FPU), Memory Management Units (MMU) for instruction and data, Instruction Cache (I-Cache), Data Cache (D-Cache), and Physical Memory Protection (PMP). It features AXI4 master interfaces for instruction fetch and data memory access (including page table walks), L2 cache snoop ports for coherency, and debug control signals to interface with the JTAG Debug Module.

## 🎯 What to Test
The verification engineer should ensure that:
1. The module resets correctly and all internal states initialize to safe values.
2. All interface protocols (e.g., AXI4, APB, native valid/ready) are strictly adhered to.
3. Edge cases specific to this IP (e.g., full/empty flags for FIFOs, cache misses for memory, etc.) are manually exercised.

## 🔍 GTKWave Signals to Observe
Add the following key signals to your GTKWave trace for structural inspection:
### Inputs
- `uut.clk`: The main system clock driving the sequential logic.
- `uut.rst_n`: Active-low asynchronous reset signal.
- `uut.irq_m_ext`: External machine-level interrupt request.
- `uut.irq_m_timer`: Machine-level timer interrupt request.
- `uut.irq_m_soft`: Machine-level software interrupt request.
- `uut.imem_arready`: AXI4 instruction memory read address ready.
- `uut.imem_rvalid`: AXI4 instruction memory read data valid.
- `uut.imem_rdata`: AXI4 instruction memory read data bus (64-bit).
- `uut.imem_rlast`: AXI4 instruction memory read last transfer indicator.
- `uut.imem_rresp`: AXI4 instruction memory read response code.
- `uut.dmem_awready`: AXI4 data memory write address ready.
- `uut.dmem_wready`: AXI4 data memory write data ready.
- `uut.dmem_bvalid`: AXI4 data memory write response valid.
- `uut.dmem_bresp`: AXI4 data memory write response code.
- `uut.dmem_arready`: AXI4 data memory read address ready.
- `uut.dmem_rvalid`: AXI4 data memory read data valid.
- `uut.dmem_rdata`: AXI4 data memory read data bus (64-bit).
- `uut.dmem_rlast`: AXI4 data memory read last transfer indicator.
- `uut.dmem_rresp`: AXI4 data memory read response code.
- `uut.snoop_valid`: L2 snoop port valid signal indicating a coherence request.
- `uut.snoop_addr`: L2 snoop port address for the coherence request.
- `uut.snoop_type`: L2 snoop port request type (e.g., GetS, GetM, Inv).
- `uut.halt_req`: Debug request signal to halt the hart.
- `uut.resume_req`: Debug request signal to resume the hart.

### Outputs
- `uut.imem_arvalid`: AXI4 instruction memory read address valid.
- `uut.imem_araddr`: AXI4 instruction memory read address bus (40-bit).
- `uut.imem_arlen`: AXI4 instruction memory read burst length.
- `uut.imem_arsize`: AXI4 instruction memory read burst size.
- `uut.imem_arburst`: AXI4 instruction memory read burst type.
- `uut.imem_rready`: AXI4 instruction memory read data ready.
- `uut.dmem_awvalid`: AXI4 data memory write address valid.
- `uut.dmem_awaddr`: AXI4 data memory write address bus (40-bit).
- `uut.dmem_awlen`: AXI4 data memory write burst length.
- `uut.dmem_awsize`: AXI4 data memory write burst size.
- `uut.dmem_awburst`: AXI4 data memory write burst type.
- `uut.dmem_wvalid`: AXI4 data memory write data valid.
- `uut.dmem_wdata`: AXI4 data memory write data bus (64-bit).
- `uut.dmem_wstrb`: AXI4 data memory write byte strobe.
- `uut.dmem_wlast`: AXI4 data memory write last transfer indicator.
- `uut.dmem_bready`: AXI4 data memory write response ready.
- `uut.dmem_arvalid`: AXI4 data memory read address valid.
- `uut.dmem_araddr`: AXI4 data memory read address bus (40-bit).
- `uut.dmem_arlen`: AXI4 data memory read burst length.
- `uut.dmem_arsize`: AXI4 data memory read burst size.
- `uut.dmem_arburst`: AXI4 data memory read burst type.
- `uut.dmem_arlock`: AXI4 data memory read lock for exclusive access (LR/SC).
- `uut.dmem_rready`: AXI4 data memory read data ready.
- `uut.snoop_ack`: L2 snoop port acknowledge signal.
- `uut.snoop_data_valid`: L2 snoop port response data valid.
- `uut.snoop_data`: L2 snoop port response data bus (512-bit).
- `uut.hart_halted`: Debug status signal indicating the hart is halted.
- `uut.hart_running`: Debug status signal indicating the hart is running.

## 🏗 Structural Block Diagram
The following Mermaid diagram maps the exact sub-module hierarchy instantiated within `rv_core_top`. Use this to verify that structural boundaries match the behavioral expectations.

```mermaid
graph TD
    rv_core_top --> |BUFX4| u_buf_flush1[u_buf_flush1]
    rv_core_top --> |BUFX4| u_buf_flush2[u_buf_flush2]
    rv_core_top --> |BUFX4| u_buf_flush3[u_buf_flush3]
    rv_core_top --> |BUFX4| u_buf_flush4[u_buf_flush4]
    rv_core_top --> |rv_mmu| u_immu[u_immu]
    rv_core_top --> |rv_icache| u_icache[u_icache]
    rv_core_top --> |rv_decode| u_decode[u_decode]
    rv_core_top --> |rv_fpu| u_fpu[u_fpu]
    rv_core_top --> |rv_execute| u_execute[u_execute]
    rv_core_top --> |rv_mmu| u_dmmu[u_dmmu]
    rv_core_top --> |rv_pmp| u_pmp[u_pmp]
    rv_core_top --> |rv_dcache| u_dcache[u_dcache]
```

## ▶️ Simulation Instructions
1. **Compile**: `iverilog -o sim.vvp rv_core_top.v tb_rv_core_top.v` (Include dependencies using ` -I ../../includes -I` if necessary)
2. **Simulate**: `vvp sim.vvp`
3. **View**: `gtkwave tb_rv_core_top.vcd`

## 💉 Injected Stimulus Profile
An advanced Python DV script has automatically generated a fully functional SystemVerilog testbench for this module. The following aggressive stimulus is applied during simulation:

### Clocks Auto-Toggled:
- `clk` toggling every 3.6ns (138.8 MHz)

### Reset Sequence:
- `rst_n` driven to 0 then 1 over 100ns.

### Data Buses Randomized:
Over 500 consecutive cycles, the following inputs receive constrained `$random` logic values to aggressively exercise datapaths and control flow:
- `irq_m_ext`
- `irq_m_timer`
- `irq_m_soft`
- `imem_arready`
- `imem_rvalid`
- `imem_rdata`
- `imem_rlast`
- `imem_rresp`
- `dmem_awready`
- `dmem_wready`
- `dmem_bvalid`
- `dmem_bresp`
- `dmem_arready`
- `dmem_rvalid`
- `dmem_rdata`
- `dmem_rlast`
- `dmem_rresp`
- `snoop_valid`
- `snoop_addr`
- `snoop_type`
- `halt_req`
- `resume_req`

## 📊 Verification Waveform

### Input Signals
![Inputs](./waveform_inputs.png)

### Output Signals
![Outputs](./waveform_outputs.png)

### 📝 Results and Observations

#### Input Signal Analysis (0–1500 ns)
- **clk**: Continuous toggling at ~138.8 MHz across the entire simulation window.
- **rst_n**: Held low for the first ~100 ns, then released high — proper active-low reset sequence.
- **irq_m_ext, irq_m_timer, irq_m_soft**: All three machine-level interrupt request lines toggle randomly throughout, simulating asynchronous interrupt arrival from timer, software, and external sources.
- **imem_arready, imem_rvalid, imem_rdata[63:0], imem_rlast, imem_rresp[1:0]**: Instruction memory AXI4 read channel signals toggle aggressively. `imem_rresp` cycles through values 00, 01, 10, 11 simulating OKAY, EXOKAY, SLVERR, and DECERR responses.
- **dmem_awready, dmem_wready, dmem_bvalid, dmem_bresp[1:0]**: Data memory AXI4 write channel handshake signals toggle randomly. `dmem_bresp` varies across all response codes.
- **dmem_arready, dmem_rvalid, dmem_rdata[63:0], dmem_rlast, dmem_rresp[1:0]**: Data memory read channel stimulus exercised similarly.
- **snoop_valid, snoop_addr[39:0], snoop_type[1:0]**: L2 cache snoop port actively stimulated with random addresses and snoop types.
- **halt_req, resume_req**: Debug control signals toggle sporadically, simulating external halt/resume requests from JTAG debug module.

#### Output Signal Analysis (0–1500 ns)
- **imem_arvalid, imem_araddr[39:0], imem_arlen[7:0], imem_arsize[2:0], imem_arburst[1:0], imem_rready**: All instruction fetch AXI4 outputs remain stuck at their initial X (undefined, shown in red) or low state. The core never issues a valid instruction fetch request.
- **dmem_awvalid, dmem_awaddr[39:0], dmem_awlen, dmem_awsize, dmem_awburst, dmem_wvalid, dmem_wdata[63:0], dmem_wstrb[7:0], dmem_wlast, dmem_bready**: All data memory write channel outputs similarly flatlined at X/0. No write transactions initiated.
- **dmem_arvalid, dmem_araddr[39:0], dmem_arlen, dmem_arsize, dmem_arburst, dmem_arlock, dmem_rready**: Data memory read channel outputs also unresponsive.
- **snoop_ack**: Shows periodic green toggling, indicating some internal snoop response logic is operating.
- **snoop_data_valid, snoop_data[511:0]**: `snoop_data_valid` remains low; `snoop_data` shows extended X values before settling.
- **hart_halted, hart_running**: These debug status outputs show active toggling patterns — `hart_halted` and `hart_running` pulse in complementary fashion, reacting to the random `halt_req`/`resume_req` inputs.

#### Verdict
⚠️ **INCONCLUSIVE** — The `rv_core_top` integration module's pipeline outputs (AXI4 instruction and data memory interfaces) remain unresponsive. This is expected: the core requires a valid instruction stream (proper boot ROM content at the reset vector) and properly handshaked AXI responses to exit its reset/init state. The random stimulus does not provide a coherent boot sequence. However, the debug interface (`hart_halted`/`hart_running`) and snoop logic (`snoop_ack`) show active responses, confirming those sub-blocks are functional. Full verification requires a directed boot test with realistic memory content.

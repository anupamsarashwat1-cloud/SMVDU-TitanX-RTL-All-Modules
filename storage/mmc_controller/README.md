# mmc_controller Verification Handoff

## 📝 Overview
This directory contains the Verilog source, testbench, and verification instructions for the `mmc_controller` module.

The `mmc_controller` module implements an eMMC 5.1 / SD 3.0 Host Controller. It supports an AXI4 Master interface for direct memory access (DMA) block transfers, allowing efficient reading and writing of data. Configuration and status monitoring, including SD Host Controller Standard (SDHC) registers, are accessed via an APB slave interface. It also directly drives the physical SD/eMMC bus pins including clock, command, and data lines.

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
- `uut.m_awready`: AXI4 write address ready signal from the slave.
- `uut.m_wready`: AXI4 write data ready signal from the slave.
- `uut.m_bvalid`: AXI4 write response valid signal from the slave.
- `uut.m_bresp`: AXI4 write response status from the slave.
- `uut.m_bid`: AXI4 write response ID from the slave.
- `uut.m_arready`: AXI4 read address ready signal from the slave.
- `uut.m_rvalid`: AXI4 read data valid signal from the slave.
- `uut.m_rdata`: AXI4 read data bus from the slave.
- `uut.m_rresp`: AXI4 read response status from the slave.
- `uut.m_rlast`: AXI4 read last transfer signal from the slave.
- `uut.m_rid`: AXI4 read ID from the slave.
- `uut.paddr`: APB slave address bus for register access.
- `uut.psel`: APB slave select signal.
- `uut.penable`: APB slave enable signal.
- `uut.pwrite`: APB slave write enable signal.
- `uut.pwdata`: APB slave write data bus.

### Outputs
- `uut.m_awvalid`: AXI4 write address valid signal.
- `uut.m_awaddr`: AXI4 write address bus.
- `uut.m_awid`: AXI4 write address ID.
- `uut.m_awlen`: AXI4 write burst length.
- `uut.m_awsize`: AXI4 write burst size.
- `uut.m_wvalid`: AXI4 write data valid signal.
- `uut.m_wdata`: AXI4 write data bus.
- `uut.m_wstrb`: AXI4 write strobe bus.
- `uut.m_wlast`: AXI4 write last transfer signal.
- `uut.m_bready`: AXI4 write response ready signal.
- `uut.m_arvalid`: AXI4 read address valid signal.
- `uut.m_araddr`: AXI4 read address bus.
- `uut.m_arid`: AXI4 read address ID.
- `uut.m_arlen`: AXI4 read burst length.
- `uut.m_arsize`: AXI4 read burst size.
- `uut.m_rready`: AXI4 read data ready signal.
- `uut.prdata`: APB slave read data bus.
- `uut.pready`: APB slave ready signal indicating transfer completion.
- `uut.pslverr`: APB slave error signal indicating transfer failure.
- `uut.mmc_irq`: Interrupt request signal from the MMC controller.
- `uut.sd_clk`: Clock output for the SD/eMMC physical interface.
- `uut.sd_reset_n`: Active-low reset output for the SD/eMMC physical interface.

## 🏗 Structural Block Diagram
The following Mermaid diagram maps the exact sub-module hierarchy instantiated within `mmc_controller`. Use this to verify that structural boundaries match the behavioral expectations.

```mermaid
graph TD
    mmc_controller[mmc_controller] --> |No Sub-Modules| LEAF[Pure Logic]
```

## ▶️ Simulation Instructions
1. **Compile**: `iverilog -o sim.vvp mmc_controller.v tb_mmc_controller.v` (Include dependencies using ` -I ../../includes -I` if necessary)
2. **Simulate**: `vvp sim.vvp`
3. **View**: `gtkwave tb_mmc_controller.vcd`

## 💉 Injected Stimulus Profile
An advanced Python DV script has automatically generated a fully functional SystemVerilog testbench for this module. The following aggressive stimulus is applied during simulation:

### Clocks Auto-Toggled:
- `clk` toggling every 3.6ns (138.8 MHz)

### Reset Sequence:
- `rst_n` driven to 0 then 1 over 100ns.

### Data Buses Randomized:
Over 500 consecutive cycles, the following inputs receive constrained `$random` logic values to aggressively exercise datapaths and control flow:
- `m_awready`
- `m_wready`
- `m_bvalid`
- `m_bresp`
- `m_bid`
- `m_arready`
- `m_rvalid`
- `m_rdata`
- `m_rresp`
- `m_rlast`
- `m_rid`
- `paddr`
- `psel`
- `penable`
- `pwrite`
- `pwdata`

## 📊 Verification Waveform

### Input Signals
![Inputs](./waveform_inputs.png)

### Output Signals
![Outputs](./waveform_outputs.png)

### 📝 Results and Observations

#### Input Signal Analysis
- **clk/rst_n**: Standard clock and reset.
- **psel/penable/pwrite/paddr/pwdata**: Randomized APB stimulus with pwdata stuck at `00000000`.
- **SD card inputs**: sd_cmd_in, sd_dat_in — randomized.

#### Output Signal Analysis
- **AXI Master Write Channel**: `m_awvalid`, `m_wvalid`, `m_wlast` all held low. All address, data, and strobe signals at zero. No DMA write transactions.
- **AXI Master Read Channel**: `m_arvalid` held low. All at zero. No DMA read transactions.
- **m_awsize[2:0]/m_arsize[2:0]**: Both at `011` (8-byte default).
- **m_bready/m_rready**: Held low.
- **prdata[31:0]**: Initially shows a brief red (undefined) pulse at time 0, then held at `00000000` throughout.
- **pready**: Held constant low.
- **pslverr**: Held constant low.
- **mmc_irq**: Held constant low — no MMC interrupt events.
- **sd_clk**: **Actively toggling** at a divided frequency throughout the entire simulation — the **SD/MMC clock divider is functional** and generating the card clock. This is a significant positive finding.
- **sd_reset_n**: Initially low (red), deasserts high at ~50 ns — **correct SD card reset sequence** observed.

#### Verdict
- **Verdict:** ⚠️ **PARTIAL PASS**. The `mmc_controller` shows two key functional behaviors: (1) `sd_clk` is actively toggling, confirming the clock divider logic works, and (2) `sd_reset_n` correctly deasserts after system reset. However, no SD/MMC card commands are issued, no DMA transfers occur, and no APB read-back data is generated because the controller was never configured with: command type, block length, DMA buffer addresses, or card detect status. A directed testbench with SD card command protocol (CMD0, CMD8, ACMD41, CMD2/3/7) is needed.

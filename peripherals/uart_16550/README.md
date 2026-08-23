# uart_16550 Verification Handoff

## 📝 Overview
This directory contains the Verilog source, testbench, and verification instructions for the `uart_16550` module.

The `uart_16550` module is a Multi-Mode UART based on the standard 16550 architecture. It provides support for Local Interconnect Network (LIN), Infrared Data Association (IrDA), and 9-bit data transmission modes. The module interfaces over an APB bus for configuration and provides separated multiplexed pins for standard serial, IrDA, and LIN communications.

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
- `uut.paddr`: APB slave address bus for register access.
- `uut.psel`: APB slave select signal.
- `uut.penable`: APB slave enable signal.
- `uut.pwrite`: APB slave write enable signal.
- `uut.pwdata`: APB slave write data bus.
- `uut.rxd`: Standard serial receive data input pin.
- `uut.irda_rx`: IrDA receive data input pin.
- `uut.lin_rx`: LIN receive data input pin.

### Outputs
- `uut.prdata`: APB slave read data bus.
- `uut.pready`: APB slave ready signal indicating transfer completion.
- `uut.pslverr`: APB slave error signal indicating transfer failure.
- `uut.uart_irq`: Interrupt request signal from the UART core.
- `uut.txd`: Standard serial transmit data output pin.
- `uut.irda_tx`: IrDA transmit data output pin.
- `uut.lin_tx`: LIN transmit data output pin.

## 🏗 Structural Block Diagram
The following Mermaid diagram maps the exact sub-module hierarchy instantiated within `uart_16550`. Use this to verify that structural boundaries match the behavioral expectations.

```mermaid
graph TD
    uart_16550[uart_16550] --> |No Sub-Modules| LEAF[Pure Logic]
```

## ▶️ Simulation Instructions
1. **Compile**: `iverilog -o sim.vvp uart_16550.v tb_uart_16550.v` (Include dependencies using ` -I ../../includes -I` if necessary)
2. **Simulate**: `vvp sim.vvp`
3. **View**: `gtkwave tb_uart_16550.vcd`

## 💉 Injected Stimulus Profile
An advanced Python DV script has automatically generated a fully functional SystemVerilog testbench for this module. The following aggressive stimulus is applied during simulation:

### Clocks Auto-Toggled:
- `clk` toggling every 3.6ns (138.8 MHz)

### Reset Sequence:
- `rst_n` driven to 0 then 1 over 100ns.

### Data Buses Randomized:
Over 500 consecutive cycles, the following inputs receive constrained `$random` logic values to aggressively exercise datapaths and control flow:
- `paddr`
- `psel`
- `penable`
- `pwrite`
- `pwdata`
- `rxd`
- `irda_rx`
- `lin_rx`

## 📊 Verification Waveform

### Input Signals
![Inputs](./waveform_inputs.png)

### Output Signals
![Outputs](./waveform_outputs.png)

### 📝 Results and Observations

#### Input Signal Analysis
- **clk**: Clean periodic toggling at ~138.8 MHz across the full 0–1900 ns window.
- **rst_n**: Asserted low at time 0, released high at ~50 ns — correct reset sequence.
- **paddr[31:0]**: Remains at `00000000` throughout — the testbench is only addressing register offset 0 (likely the THR/RBR register), missing the configuration registers (LCR, IER, FCR, etc.).
- **psel**: Active toggling — random APB select assertions throughout simulation.
- **penable**: Toggles with appropriate spacing after psel — APB protocol phase sequencing.
- **pwrite**: Mix of high and low — both read and write transactions attempted.
- **pwdata[31:0]**: Stays at `00000000` throughout — only zeros written to registers, so the UART divisor latch, line control, and FIFO control are never configured.
- **rxd**: Randomized toggling — simulating noisy serial receive data.
- **irda_rx**: Randomized toggling — infrared receive input exercised.
- **lin_rx**: Randomized toggling — LIN bus receive input exercised.

#### Output Signal Analysis
- **prdata[31:0]**: Shows sparse read-back values (0000000xx, 00+, 00000000, 00000+, 00000000, etc.). Most values are near-zero, confirming the UART status registers return default/reset state since the module was never configured.
- **pready**: Held constant low — **this is significant**. The APB ready signal never asserts, meaning the UART module is **not completing any APB transactions**. This likely indicates the UART requires proper initialization (divisor latch configuration) before it will respond to register accesses.
- **pslverr**: Held constant low — no APB slave errors reported.
- **uart_irq**: Held constant low (flat green line) — no interrupts generated because no interrupt sources were enabled.
- **txd**: Held constant high (flat green line) — UART transmit line idle. No transmission ever initiated because the module was never configured with baud rate or line parameters.
- **irda_tx**: Held constant high — infrared transmit idle.
- **lin_tx**: Held constant high — LIN bus transmit idle.

#### Verdict
- **Verdict:** ⚠️ **INCONCLUSIVE**. The `uart_16550` module compiles and simulates, but the randomized testbench completely fails to exercise any real UART functionality. The `paddr` is stuck at offset 0 and `pwdata` is all-zeros, so the divisor latch, line control, FIFO control, and interrupt enable registers are never programmed. As a result, `pready` never asserts (transactions never complete), `txd` stays idle, and no interrupts fire. **A directed testbench is required** that programs the divisor latch for a baud rate, configures LCR for 8N1 framing, enables FIFOs via FCR, and then writes data to THR to verify actual serial transmission.

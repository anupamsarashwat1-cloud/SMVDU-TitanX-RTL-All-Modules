# rtc Verification Handoff

## 📝 Overview
This directory contains the Verilog source, testbench, and verification instructions for the `rtc` module.

The `rtc` is a Real-Time Counter designed to provide a 64-bit free-running timebase, aligning with the RISC-V Core Local Interruptor (CLINT) timer specification (`mtime` and `mtimecmp`). Driven by a slow, always-on clock (e.g., 32.768 kHz), it increments the 64-bit `mtime` counter continuously. Through its APB slave interface, system software can read the current time and program independent 64-bit comparator registers (`mtimecmp`) for up to 5 harts (4 application cores and 1 monitor core). When the global `mtime` value reaches or exceeds a core's programmed `mtimecmp` value, the module asserts the corresponding timer interrupt (`timer_irq`), enabling precise, asynchronous event scheduling and OS tick generation.

## 🎯 What to Test
The verification engineer should ensure that:
1. The module resets correctly and all internal states initialize to safe values.
2. All interface protocols (e.g., AXI4, APB, native valid/ready) are strictly adhered to.
3. Edge cases specific to this IP (e.g., full/empty flags for FIFOs, cache misses for memory, etc.) are manually exercised.

## 🔍 GTKWave Signals to Observe
Add the following key signals to your GTKWave trace for structural inspection:
### Inputs
- `uut.clk`: The main system clock or APB clock driving the APB slave interface.
- `uut.rtc_clk`: The always-on slow clock (e.g., 32.768 kHz) driving the mtime counter.
- `uut.rst_n`: Active-low asynchronous reset signal.
- `uut.paddr`: 32-bit APB address bus for configuring mtimecmp registers.
- `uut.psel`: APB slave select signal.
- `uut.penable`: APB enable signal.
- `uut.pwrite`: APB write control signal.
- `uut.pwdata`: 32-bit APB write data bus.

### Outputs
- `uut.prdata`: 32-bit APB read data bus for retrieving mtime or mtimecmp values.
- `uut.pready`: APB ready signal for CSR accesses.
- `uut.pslverr`: APB slave error signal indicating an invalid transfer.
- `uut.timer_irq`: 5-bit interrupt request bus mapped to individual harts.

## 🏗 Structural Block Diagram
The following Mermaid diagram maps the exact sub-module hierarchy instantiated within `rtc`. Use this to verify that structural boundaries match the behavioral expectations.

```mermaid
graph TD
    rtc[rtc] --> |No Sub-Modules| LEAF[Pure Logic]
```

## ▶️ Simulation Instructions
1. **Compile**: `iverilog -o sim.vvp rtc.v tb_rtc.v` (Include dependencies using ` -I ../../includes -I` if necessary)
2. **Simulate**: `vvp sim.vvp`
3. **View**: `gtkwave tb_rtc.vcd`

## 💉 Injected Stimulus Profile
An advanced Python DV script has automatically generated a fully functional SystemVerilog testbench for this module. The following aggressive stimulus is applied during simulation:

### Clocks Auto-Toggled:
- `clk` toggling every 3.6ns (138.8 MHz)
- `rtc_clk` toggling every 3.6ns (138.8 MHz)

### Reset Sequence:
- `rst_n` driven to 0 then 1 over 100ns.

### Data Buses Randomized:
Over 500 consecutive cycles, the following inputs receive constrained `$random` logic values to aggressively exercise datapaths and control flow:
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
- **clk**: Clean periodic toggling at ~138.8 MHz across the 0–1900 ns window.
- **rtc_clk**: Secondary slower clock toggling — the dedicated RTC oscillator input is actively driven.
- **rst_n**: Asserted low at time 0, released high at ~50 ns — proper reset.
- **paddr[31:0]**: Remains at `00000000` throughout — only register offset 0 is ever addressed, missing the alarm, prescaler, and control registers.
- **psel**: Randomized toggling — APB select assertions with irregular timing.
- **penable**: Follows psel with expected APB phase behavior.
- **pwrite**: Mixed read/write — toggling throughout.
- **pwdata[31:0]**: Stays at `00000000` throughout — no configuration data written.

#### Output Signal Analysis
- **prdata[31:0]**: Held at `00000000` for the entire simulation — the RTC module returns all zeros on every read. This confirms the timer counter and alarm registers are never initialized, and the module is not counting.
- **pready**: Held constant low — APB transactions are **not completing**. The RTC module is not acknowledging any register accesses.
- **pslverr**: Held constant low — no slave errors.
- **timer_irq[4:0]**: Held at `00` throughout — no timer interrupts generated. The 5-bit interrupt vector remains at zero, confirming no alarm match, overflow, or periodic timer events occurred.

#### Verdict
- **Verdict:** ❌ **FAIL**. The `rtc` module is completely unresponsive under the current testbench. `pready` never asserts (no APB transactions complete), `prdata` is stuck at zero (no register read-back), and `timer_irq` never fires. Despite having both `clk` and `rtc_clk` actively driven, the RTC counter produces no observable output. The root cause is likely that the module requires explicit enable/prescaler configuration via APB writes before the counter starts, but `pwdata` is stuck at zero and `paddr` never addresses the control register. A directed testbench is required to properly initialize the RTC.

---

## ✅ Phase 2–5 Update

**Final Verdict: ✅ PASS**

- **BUG-RTC-001 Fixed**: Added 2-FF CDC synchronizer (mtime_meta/mtime_sync) for rtc_clk→clk crossing
- Directed test verified: `timer_irq[0]` fires when `mtime >= mtimecmp[0]` (Test 4 PASS)
- IRQ cleared by writing mtimecmp=0xFFFF...FFFF (Test 5 PASS)
- mtimecmp read-back verified (Test 6 PASS)
- All 6 tests PASS

*Last updated: Phase 4 Bug Fixes + Phase 2 Directed Tests*

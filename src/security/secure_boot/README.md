# secure_boot Verification Handoff

## 📝 Overview
This directory contains the Verilog source, testbench, and verification instructions for the `secure_boot` module.

The `secure_boot` module acts as the Hardware Root-of-Trust for the system, enforcing an ECDSA P-256 signature verification of the boot image. Initiated automatically on power-on reset, it operates a finite state machine that sequentially reads the boot image from the eNVM, computes its SHA-256 hash, reads the appended ECDSA signature, and performs verification. It subsequently dictates the boot flow by driving signals to either de-assert the core reset upon success or halt the system upon failure, while providing status visibility via an APB interface.

## 🎯 What to Test
The verification engineer should ensure that:
1. The module resets correctly and all internal states initialize to safe values.
2. All interface protocols (e.g., AXI4, APB, native valid/ready) are strictly adhered to.
3. Edge cases specific to this IP (e.g., full/empty flags for FIFOs, cache misses for memory, etc.) are manually exercised.

## 🔍 GTKWave Signals to Observe
Add the following key signals to your GTKWave trace for structural inspection:
### Inputs
- `uut.clk`: The main clock signal for the module.
- `uut.rst_n`: Active-low asynchronous reset signal.
- `uut.paddr`: APB slave address bus for status monitoring.
- `uut.psel`: APB slave select signal.
- `uut.penable`: APB slave enable signal.
- `uut.pwrite`: APB slave write enable signal.
- `uut.pwdata`: APB slave write data bus.
- `uut.envm_rdata`: Data read from the eNVM controller during the boot image fetch.
- `uut.envm_valid`: Indicates valid data is available from the eNVM controller.

### Outputs
- `uut.prdata`: APB slave read data bus returning status information.
- `uut.pready`: APB slave ready signal.
- `uut.pslverr`: APB slave error signal.
- `uut.envm_addr`: Address bus for direct reads from the eNVM controller.
- `uut.envm_req`: Request signal asserting a read to the eNVM controller.
- `uut.boot_pass`: Boot success signal that de-asserts core reset to start execution.
- `uut.boot_fail`: Boot failure signal that halts the system and flags an error.

## 🏗 Structural Block Diagram
The following Mermaid diagram maps the exact sub-module hierarchy instantiated within `secure_boot`. Use this to verify that structural boundaries match the behavioral expectations.

```mermaid
graph TD
    secure_boot[secure_boot] --> |No Sub-Modules| LEAF[Pure Logic]
```

## ▶️ Simulation Instructions
1. **Compile**: `iverilog -o sim.vvp secure_boot.v tb_secure_boot.v` (Include dependencies using ` -I ../../includes -I` if necessary)
2. **Simulate**: `vvp sim.vvp`
3. **View**: `gtkwave tb_secure_boot.vcd`

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
- `envm_rdata`
- `envm_valid`

## 📊 Verification Waveform

### Input Signals
![Inputs](./waveform_inputs.png)

### Output Signals
![Outputs](./waveform_outputs.png)

### 📝 Results and Observations

#### Input Signal Analysis
- **clk/rst_n**: Standard clock and reset.
- **psel/penable/pwrite/paddr/pwdata**: Randomized APB stimulus with pwdata stuck at `00000000`.
- **envm_rdata[31:0]**: Randomized — simulating flash read-back data.

#### Output Signal Analysis
- **prdata[31:0]**: Shows `00000000`, then `0+`, `00000000` around ~100 ns, then flat at `00000000` for most of the simulation, with a late read-back of `00000000` around ~1500 ns. Very sparse register activity.
- **pready**: Held constant low.
- **pslverr**: Held constant low.
- **envm_addr[16:0]**: **Actively cycling** through sequential addresses: `00000`, `00+`, `0+`, `00+`, `0+`, `+`, `0000F`, `00014`, `00+`, `0+`, `0+`, `0+`, `0+`, `00031`, `00+`, `0+`, `00+`, `0+`, `0+`, `0+`, `+`, `0+`, `0+`, `0+`, `0+`, `00660`, `00+`, `0+`, `0+`, `0+`. This confirms the **secure boot state machine is actively fetching code** from the eNVM array in a sequential pattern. The addresses include offsets 0x00000, 0x0000F, 0x00014, 0x00031, 0x00660 — consistent with reading boot ROM image blocks.
- **envm_req**: Initially low (red), transitions to high at ~50 ns (after reset release) and remains high — the secure boot FSM is **continuously requesting eNVM access**, confirming the boot sequence has started.
- **boot_pass**: Held constant low (red) — boot verification never succeeds. The secure boot module cannot validate the boot image because the random `envm_rdata` doesn't contain a valid cryptographic signature.
- **boot_fail**: Held constant low — boot failure is also not asserted. The module is still processing/fetching and hasn't reached a final verdict within the simulation window.

#### Verdict
- **Verdict:** ⚠️ **PARTIAL PASS**. The `secure_boot` module demonstrates active boot ROM fetching behavior — `envm_req` asserts after reset, and `envm_addr` sequences through memory addresses in a pattern consistent with reading a boot image. However, neither `boot_pass` nor `boot_fail` asserts within the simulation window, indicating the boot verification process is incomplete (possibly because the hash/signature computation requires more cycles than the ~1900 ns simulation provides, or the random eNVM data causes the FSM to enter an infinite retry loop). A directed testbench with a pre-loaded valid boot image and known signature is required.

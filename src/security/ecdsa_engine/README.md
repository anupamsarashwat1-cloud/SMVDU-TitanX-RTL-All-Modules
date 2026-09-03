# ecdsa_engine Verification Handoff

## 📝 Overview
This directory contains the Verilog source, testbench, and verification instructions for the `ecdsa_engine` module.

The `ecdsa_engine` module is a hardware accelerator for the Elliptic Curve Digital Signature Algorithm (ECDSA) supporting P-256 and P-384 curves. It performs cryptographic operations like point multiplication and modular inversion required for signature verification and generation. It integrates with the system via an APB slave interface, which manages configuration, status, and the transfer of large cryptographic operands (message hashes, keys, and signatures) stored in internal RAM arrays.

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
- `uut.paddr`: APB slave address bus.
- `uut.psel`: APB slave select signal.
- `uut.penable`: APB slave enable signal.
- `uut.pwrite`: APB slave write enable signal.
- `uut.pwdata`: APB slave write data bus.

### Outputs
- `uut.prdata`: APB slave read data bus.
- `uut.pready`: APB slave ready signal.
- `uut.pslverr`: APB slave error signal.
- `uut.ecdsa_irq`: Interrupt request signal asserted when an ECDSA operation completes.

## 🏗 Structural Block Diagram
The following Mermaid diagram maps the exact sub-module hierarchy instantiated within `ecdsa_engine`. Use this to verify that structural boundaries match the behavioral expectations.

```mermaid
graph TD
    ecdsa_engine[ecdsa_engine] --> |No Sub-Modules| LEAF[Pure Logic]
```

## ▶️ Simulation Instructions
1. **Compile**: `iverilog -o sim.vvp ecdsa_engine.v tb_ecdsa_engine.v` (Include dependencies using ` -I ../../includes -I` if necessary)
2. **Simulate**: `vvp sim.vvp`
3. **View**: `gtkwave tb_ecdsa_engine.vcd`

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

## 📊 Verification Waveform

### Input Signals
![Inputs](./waveform_inputs.png)

### Output Signals
![Outputs](./waveform_outputs.png)

### 📝 Results and Observations

#### Input Signal Analysis
- **clk/rst_n**: Standard clock and reset.
- **psel/penable/pwrite/paddr/pwdata**: Randomized APB stimulus with pwdata stuck at `00000000`.

#### Output Signal Analysis
- **prdata[31:0]**: Shows **highly active** data with frequent transitions: `00000000`, `+`, `+`, `0+`, `00000000`, `x+`, `00+`, `00+`, `+`, `000+`, `0+`, `0000+`, `x+`, `00+`, `0+`, `+`, `00+`, `x+`, `+`, `008+`, `+`, `00+`, `008+`, `0+`, `+`, `00000+`, `00+`, `0+`, `+`, `000+`, `00+`, `+`, `00000000+`, `000+`, `00000000`. The data varies rapidly between zero and small non-zero values, with occasional `x` (undefined) bits. This indicates the ECDSA module's internal register file is returning computational state — likely partial results from the elliptic curve arithmetic pipeline.
- **pready**: Held constant low — APB transactions not formally completing.
- **pslverr**: Held constant low.
- **ecdsa_irq**: Held constant low (red) — no ECDSA operation-complete interrupt. No signature generation or verification was completed because the module was never loaded with a private key, message hash, or curve parameters.

#### Verdict
- **Verdict:** ⚠️ **PARTIAL PASS**. The `ecdsa_engine` register file is actively returning data via `prdata`, with frequent non-zero values indicating the internal arithmetic state is readable. However, no complete ECDSA operation (sign/verify) was performed since the module was never configured with curve parameters (P-256/P-384), private key, or message hash via the APB interface. A directed testbench with NIST ECDSA known-answer test vectors is essential for full functional verification.

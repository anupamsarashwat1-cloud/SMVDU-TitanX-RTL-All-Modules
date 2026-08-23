#!/usr/bin/env python3
"""
===========================================================================
FIX ALL TESTBENCHES: Correct port widths and wire/logic declarations
===========================================================================
Reads each module's RTL source to extract FULL port declarations (direction,
width, name), then regenerates the testbench with:
  - Correct bit widths on every signal
  - `wire` for outputs (driven by DUT continuous assignment)
  - `logic` for inputs (driven by testbench procedural blocks)
  - Proper clock/reset detection and stimulus generation

Usage:
  python3 fix_all_testbenches.py [--skip-memory]
===========================================================================
"""
import os
import re
import sys

BASE_DIR = "/home/anupam-sarashwat/rtl_verification_handoff"
DIRECTORIES = ['common', 'frontend', 'backend', 'interconnect', 'memory',
               'security', 'peripherals', 'storage', 'video', 'top']

# Skip memory since those are already properly done
SKIP_DIRS = ['memory'] if '--skip-memory' in sys.argv else []


def strip_comments(content):
    """Remove single-line and multi-line comments."""
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*[\s\S]*?\*/', '', content)
    return content


def parse_ports_from_rtl(filepath):
    """
    Parse a Verilog/SystemVerilog source file to extract all port declarations
    with their direction, width, and name.
    
    Returns: list of (direction, width_str, name)
      e.g. [('input', '', 'clk'), ('input', '[63:0]', 'pc_in'), ('output', '[31:0]', 'data_out')]
    """
    with open(filepath, 'r') as f:
        content = f.read()
    
    clean = strip_comments(content)
    
    # Find the module declaration (handle parametrized modules)
    # Match: module name #(...) ( ports ); or module name ( ports );
    mod_match = re.search(
        r'module\s+(\w+)\s*(?:#\s*\([\s\S]*?\))?\s*\(([\s\S]*?)\);',
        clean
    )
    if not mod_match:
        return None, []
    
    module_name = mod_match.group(1)
    ports_block = mod_match.group(2)
    
    # Also get full body for ports declared in body (Verilog-95 style)
    full_body = clean
    
    # Pattern for port declarations:
    #   input  wire        clk,
    #   input  wire [63:0] addr,
    #   output reg  [31:0] data_out,
    #   output wire        valid,
    #   inout  wire [7:0]  gpio_pad,
    port_re = re.compile(
        r'(input|output|inout)\s+'           # direction
        r'(?:wire|reg|logic)?\s*'             # optional type keyword
        r'(\[[\s\S]*?\])?\s*'                 # optional width [N:M]
        r'(\w+)',                              # signal name
        re.MULTILINE
    )
    
    ports = []
    seen = set()
    
    # First try to parse from the port declaration block
    for m in port_re.finditer(ports_block):
        direction = m.group(1)
        width = (m.group(2) or '').strip()
        name = m.group(3)
        if name not in seen:
            ports.append((direction, width, name))
            seen.add(name)
    
    # If we found very few ports in the declaration, also check the body
    # (for Verilog-95 style where ports are just names in the header)
    if len(ports) < 3:
        for m in port_re.finditer(full_body):
            direction = m.group(1)
            width = (m.group(2) or '').strip()
            name = m.group(3)
            if name not in seen:
                ports.append((direction, width, name))
                seen.add(name)
    
    return module_name, ports


def is_clock(name):
    return bool(re.search(r'(?i)(clk|clock|ck_p|ck_n)', name))


def is_reset(name):
    return bool(re.search(r'(?i)(rst|reset)', name))


def generate_testbench(module_name, ports, extra_includes=None):
    """Generate a corrected testbench with proper widths."""
    tb = "`timescale 1ns / 1ps\n\n"
    tb += f"module tb_{module_name}();\n\n"
    
    # Signal declarations with correct widths
    for direction, width, name in ports:
        width_str = f" {width}" if width else ""
        if direction == 'input':
            tb += f"    logic{width_str} {name};\n"
        else:  # output or inout
            tb += f"    wire{width_str} {name};\n"
    
    # DUT instantiation
    tb += f"\n    // DUT Instantiation\n"
    tb += f"    {module_name} uut (\n"
    port_maps = [f"        .{name}({name})" for _, _, name in ports]
    tb += ",\n".join(port_maps) + "\n    );\n\n"
    
    # Clock generation
    clocks = [name for d, w, name in ports if d == 'input' and is_clock(name)]
    resets = [name for d, w, name in ports if d == 'input' and is_reset(name)]
    data_inputs = [name for d, w, name in ports
                   if d == 'input' and not is_clock(name) and not is_reset(name)]
    
    if clocks:
        tb += "    // Advanced Clock Generation (138.8 MHz -> ~7.2ns period)\n"
        tb += "    initial begin\n"
        for c in clocks:
            tb += f"        {c} = 0;\n"
        tb += "    end\n\n"
        for c in clocks:
            tb += f"    always #3.6 {c} = ~{c};\n"
    
    tb += "\n    // Main Functional Stimulus Block\n"
    tb += "    initial begin\n"
    tb += f'        $dumpfile("tb_{module_name}.vcd");\n'
    tb += f"        $dumpvars(0, tb_{module_name});\n\n"
    
    # Initialize inputs
    tb += "        // 1. Initialize all data inputs\n"
    for p in data_inputs:
        tb += f"        {p} = 0;\n"
    
    # Reset sequence
    if resets:
        tb += "\n        // 2. Assert Resets\n"
        tb += "        #10;\n"
        for r in resets:
            if '_n' in r.lower():
                tb += f"        {r} = 0; // Active low\n"
            else:
                tb += f"        {r} = 1; // Active high\n"
        
        tb += "        #100;\n"
        tb += "        // 3. De-assert Resets\n"
        for r in resets:
            if '_n' in r.lower():
                tb += f"        {r} = 1;\n"
            else:
                tb += f"        {r} = 0;\n"
        tb += "        #20;\n"
    
    # Random stimulus
    tb += "\n        // 4. Constrained Random Stimulus Injection\n"
    tb += "        // Generating aggressive random toggling to exercise internal logic\n"
    tb += "        repeat(500) begin\n"
    tb += "            #10;\n"
    for p in data_inputs:
        tb += f"            {p} = $random;\n"
    tb += "        end\n\n"
    
    tb += "        #1000;\n"
    tb += "        $finish;\n"
    tb += "    end\n\n"
    tb += "endmodule\n"
    
    return tb


def main():
    fixed = 0
    skipped = 0
    errors = []
    
    for d in DIRECTORIES:
        if d in SKIP_DIRS:
            print(f"\n=== SKIPPING {d}/ (already done) ===")
            continue
        
        dir_path = os.path.join(BASE_DIR, d)
        if not os.path.isdir(dir_path):
            continue
        
        print(f"\n{'='*60}")
        print(f"  Processing directory: {d}/")
        print(f"{'='*60}")
        
        for mod in sorted(os.listdir(dir_path)):
            mod_dir = os.path.join(dir_path, mod)
            if not os.path.isdir(mod_dir):
                continue
            
            # Find RTL source (not testbench)
            v_files = [f for f in os.listdir(mod_dir)
                       if f.endswith('.v') and not f.startswith('tb_')
                       and not f.startswith('buf_macro')]
            
            if not v_files:
                print(f"  ⚠ {mod}: No RTL source found, skipping")
                skipped += 1
                continue
            
            v_file = os.path.join(mod_dir, v_files[0])
            tb_file = os.path.join(mod_dir, f"tb_{mod}.v")
            
            # Parse RTL
            module_name, ports = parse_ports_from_rtl(v_file)
            if not module_name or not ports:
                print(f"  ⚠ {mod}: Could not parse RTL ports, skipping")
                errors.append(mod)
                continue
            
            # Check how many ports have widths vs bare
            with_width = sum(1 for _, w, _ in ports if w)
            total = len(ports)
            
            # Generate corrected testbench
            tb_content = generate_testbench(module_name, ports)
            
            with open(tb_file, 'w') as f:
                f.write(tb_content)
            
            print(f"  ✅ {mod}: {total} ports ({with_width} with explicit widths)")
            fixed += 1
    
    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Fixed:   {fixed}")
    print(f"  Skipped: {skipped}")
    print(f"  Errors:  {len(errors)} {errors if errors else ''}")


if __name__ == '__main__':
    main()

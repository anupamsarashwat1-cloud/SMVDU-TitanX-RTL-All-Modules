#!/usr/bin/env python3
"""
Resolve all parametric width references in testbenches by substituting
default values from the RTL module parameters.
"""
import os
import re

BASE_DIR = "/home/anupam-sarashwat/rtl_verification_handoff"

# Map of (module_dir) -> {param_name: int_value}
PARAM_MAP = {
    "common/cdc_sync":       {"WIDTH": 1, "STAGES": 2},
    "common/fifo_async":     {"WIDTH": 8, "DEPTH": 16, "AWIDTH": 4},
    "common/fifo_sync":      {"WIDTH": 8, "DEPTH": 16, "AWIDTH": 4},
    "backend/clint":         {"NUM_HARTS": 5},
    "backend/plic":          {"NUM_SOURCES": 186, "NUM_TARGETS": 10},
    "backend/rv_dcache":     {"WAYS": 8, "SETS": 64, "LINE_BYTES": 64, "ADDR_W": 40, "DATA_W": 64, "MSHR_DEPTH": 4},
    "backend/rv_debug":      {"NUM_HARTS": 5, "PROGBUF_SIZE": 16},
    "backend/rv_tlb":        {"WAYS": 4, "SETS": 8, "ASID_W": 16, "VA_W": 39, "PA_W": 38},
    "frontend/rv_icache":    {"WAYS": 8, "SETS": 64, "LINE_BYTES": 64, "ADDR_W": 40, "DATA_W": 64},
    "interconnect/apb_bridge":     {"AW": 32, "DW": 32},
    "interconnect/axi4_crossbar":  {"NM": 15, "NS": 9, "AW": 40, "DW": 64, "IDW": 4},
    "interconnect/axi4_to_ahb":    {"AW": 40, "DW": 32, "IDW": 4},
    "interconnect/interconnect_mpu": {"NM": 15, "AW": 40, "DW": 64, "IDW": 4, "NR": 8},
    "interconnect/mmu_arbiter":    {"N": 5, "AW": 40, "DW": 64},
    "interconnect/qos_controller": {"NM": 15, "IDW": 4},
    "security/envm_ctrl":    {"AW": 32, "DW": 32},
    "peripherals/gem_ethernet": {"AW": 40, "DW": 64, "IDW": 4},
    "peripherals/pcie_pipe_if":  {"LANES": 4},
    "peripherals/pcie_top":  {"LANES": 4, "AW": 40, "DW": 64, "IDW": 4},
    "storage/mmc_controller": {"AW": 40, "DW": 64, "IDW": 4},
    "storage/qspi_controller": {"AW": 32, "DW": 32},
    "storage/usb_otg":       {"AW": 40, "DW": 64, "IDW": 4},
    "video/mipi_csi2_rx":    {"LANES": 4},
}


def eval_expr(expr_str, params):
    """Safely evaluate a simple width expression like 'DW-1' or 'NM*DW-1' or 'DW/8-1'."""
    try:
        # Replace parameter names with values
        resolved = expr_str
        for name, val in sorted(params.items(), key=lambda x: -len(x[0])):
            resolved = re.sub(r'\b' + name + r'\b', str(val), resolved)
        return eval(resolved)
    except:
        return None


def resolve_widths(tb_path, params):
    """Replace parametric widths in a testbench file with concrete values."""
    with open(tb_path, 'r') as f:
        content = f.read()
    
    original = content
    
    # Find all [EXPR] patterns that contain parameter names
    def replace_width(match):
        full = match.group(0)  # e.g. [DW-1:0]
        inner = match.group(1)  # e.g. DW-1:0
        parts = inner.split(':')
        if len(parts) == 2:
            hi_val = eval_expr(parts[0].strip(), params)
            lo_val = eval_expr(parts[1].strip(), params)
            if hi_val is not None and lo_val is not None:
                return f"[{hi_val}:{lo_val}]"
        return full
    
    content = re.sub(r'\[([^\[\]]+)\]', replace_width, content)
    
    if content != original:
        with open(tb_path, 'w') as f:
            f.write(content)
        return True
    return False


fixed = 0
for mod_rel, params in PARAM_MAP.items():
    mod_name = os.path.basename(mod_rel)
    tb_path = os.path.join(BASE_DIR, mod_rel, f"tb_{mod_name}.v")
    
    if not os.path.exists(tb_path):
        print(f"  ⚠ {mod_rel}: testbench not found")
        continue
    
    if resolve_widths(tb_path, params):
        print(f"  ✅ {mod_rel}: resolved parametric widths")
        fixed += 1
    else:
        print(f"  - {mod_rel}: no parametric widths found (already resolved?)")

print(f"\nResolved {fixed} testbenches.")

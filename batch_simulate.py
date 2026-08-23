#!/usr/bin/env python3
"""
Batch compile and simulate ALL modules (except memory/ which is done).
For each module:
  1. Find RTL source + testbench
  2. Compile with iverilog (with -I ../../includes if params.vh is used)
  3. Simulate with vvp to generate VCD
  4. Report success/failure
"""
import os
import subprocess
import sys

BASE_DIR = "/home/anupam-sarashwat/rtl_verification_handoff"
DIRECTORIES = ['common', 'frontend', 'backend', 'interconnect',
               'security', 'peripherals', 'storage', 'video', 'top']
# memory/ is excluded — already done

INCLUDE_DIR = os.path.join(BASE_DIR, "includes")
BUFX4_PATH = os.path.join(BASE_DIR, "common", "BUFX4", "buf_macros.v")

results = {"pass": [], "fail": [], "skip": []}

for d in DIRECTORIES:
    dir_path = os.path.join(BASE_DIR, d)
    if not os.path.isdir(dir_path):
        continue

    print(f"\n{'='*60}")
    print(f"  {d}/")
    print(f"{'='*60}")

    for mod in sorted(os.listdir(dir_path)):
        mod_dir = os.path.join(dir_path, mod)
        if not os.path.isdir(mod_dir):
            continue

        # Find RTL and testbench files
        v_files = [f for f in os.listdir(mod_dir)
                   if f.endswith('.v') and not f.startswith('tb_')]
        tb_file = os.path.join(mod_dir, f"tb_{mod}.v")

        if not v_files or not os.path.exists(tb_file):
            print(f"  ⚠ {mod}: Missing RTL or testbench, skipping")
            results["skip"].append(f"{d}/{mod}")
            continue

        os.chdir(mod_dir)

        # Build iverilog command
        rtl_files = [os.path.join(mod_dir, f) for f in v_files]
        
        # Check if module uses params.vh or other includes
        needs_include = False
        for vf in v_files + [f"tb_{mod}.v"]:
            vpath = os.path.join(mod_dir, vf)
            if os.path.exists(vpath):
                with open(vpath, 'r') as fh:
                    if '`include' in fh.read():
                        needs_include = True
                        break

        # Check if module uses BUFX4
        needs_bufx4 = False
        for vf in v_files:
            vpath = os.path.join(mod_dir, vf)
            with open(vpath, 'r') as fh:
                if 'BUFX4' in fh.read():
                    needs_bufx4 = True
                    break

        cmd = ["iverilog", "-o", "sim.vvp"]
        if needs_include:
            cmd += ["-I", INCLUDE_DIR]
        
        # Add all RTL files + testbench
        cmd += rtl_files + [tb_file]
        
        if needs_bufx4 and os.path.exists(BUFX4_PATH):
            cmd.append(BUFX4_PATH)

        # Compile
        print(f"  Compiling {mod}...", end=" ", flush=True)
        comp = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if comp.returncode != 0:
            # Check if errors are just warnings
            if "error" in comp.stderr.lower():
                print(f"❌ COMPILE FAIL")
                # Print first 5 error lines
                for line in comp.stderr.split('\n'):
                    if 'error' in line.lower():
                        print(f"    {line.strip()}")
                results["fail"].append(f"{d}/{mod} (compile)")
                continue
            else:
                print(f"⚠ warnings, continuing...", end=" ", flush=True)
        
        # Simulate
        sim = subprocess.run(["vvp", "sim.vvp"], capture_output=True, text=True, timeout=60)
        
        vcd_file = f"tb_{mod}.vcd"
        if os.path.exists(vcd_file) and os.path.getsize(vcd_file) > 100:
            size_kb = os.path.getsize(vcd_file) / 1024
            print(f"✅ VCD generated ({size_kb:.0f} KB)")
            results["pass"].append(f"{d}/{mod}")
        else:
            print(f"❌ No VCD generated")
            results["fail"].append(f"{d}/{mod} (simulate)")

print(f"\n{'='*60}")
print(f"  FINAL RESULTS")
print(f"{'='*60}")
print(f"  ✅ PASS:    {len(results['pass'])}")
print(f"  ❌ FAIL:    {len(results['fail'])}")
print(f"  ⚠ SKIP:    {len(results['skip'])}")
if results["fail"]:
    print(f"\n  Failed modules:")
    for f in results["fail"]:
        print(f"    - {f}")

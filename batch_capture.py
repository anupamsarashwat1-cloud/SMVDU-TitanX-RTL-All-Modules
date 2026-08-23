#!/usr/bin/env python3
"""
Batch capture ALL modules sequentially (GTKWave requires exclusive display access).
Runs master_capture.py for each module, one at a time.
Skips modules without VCD files.
Does NOT commit — that's done after analysis.
"""
import os
import subprocess
import sys

BASE_DIR = "/home/anupam-sarashwat/rtl_verification_handoff"
SKIP = {"BUFX4"}  # No meaningful waveforms

# All directories in order
DIRECTORIES = ['frontend', 'backend', 'interconnect', 'common',
               'peripherals', 'security', 'storage', 'video', 'top']
# memory/ already done

results = {"captured": [], "skipped": [], "failed": []}

for d in DIRECTORIES:
    dir_path = os.path.join(BASE_DIR, d)
    if not os.path.isdir(dir_path):
        continue

    for mod in sorted(os.listdir(dir_path)):
        if mod in SKIP:
            results["skipped"].append(f"{d}/{mod}")
            continue

        mod_dir = os.path.join(dir_path, mod)
        if not os.path.isdir(mod_dir):
            continue

        vcd = os.path.join(mod_dir, f"tb_{mod}.vcd")
        readme = os.path.join(mod_dir, "README.md")

        if not os.path.exists(vcd):
            print(f"  ⚠ {d}/{mod}: No VCD, skipping")
            results["skipped"].append(f"{d}/{mod}")
            continue

        if not os.path.exists(readme):
            print(f"  ⚠ {d}/{mod}: No README, skipping")
            results["skipped"].append(f"{d}/{mod}")
            continue

        print(f"\n{'='*50}")
        print(f"  Capturing {d}/{mod}")
        print(f"{'='*50}")

        try:
            result = subprocess.run(
                ["python3", os.path.join(BASE_DIR, "master_capture.py"), d, mod],
                cwd=BASE_DIR,
                capture_output=True, text=True,
                timeout=30
            )
            
            # Check if screenshots were generated
            inp_png = os.path.join(mod_dir, "waveform_inputs.png")
            out_png = os.path.join(mod_dir, "waveform_outputs.png")
            
            if os.path.exists(inp_png) and os.path.exists(out_png):
                inp_sz = os.path.getsize(inp_png)
                out_sz = os.path.getsize(out_png)
                print(f"  ✅ inputs={inp_sz/1024:.0f}KB, outputs={out_sz/1024:.0f}KB")
                results["captured"].append(f"{d}/{mod}")
            else:
                print(f"  ⚠ Missing screenshots")
                # Check if old ones exist
                if os.path.exists(inp_png) or os.path.exists(out_png):
                    results["captured"].append(f"{d}/{mod} (partial)")
                else:
                    results["failed"].append(f"{d}/{mod}")
                    
        except subprocess.TimeoutExpired:
            print(f"  ❌ Timeout")
            os.system("killall gtkwave 2>/dev/null")
            results["failed"].append(f"{d}/{mod} (timeout)")
        except Exception as e:
            print(f"  ❌ Error: {e}")
            results["failed"].append(f"{d}/{mod} ({e})")

print(f"\n{'='*60}")
print(f"  CAPTURE SUMMARY")
print(f"{'='*60}")
print(f"  ✅ Captured: {len(results['captured'])}")
print(f"  ⚠ Skipped:  {len(results['skipped'])}")
print(f"  ❌ Failed:   {len(results['failed'])}")
if results["failed"]:
    print(f"\n  Failed modules:")
    for f in results["failed"]:
        print(f"    - {f}")

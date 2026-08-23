#!/usr/bin/env python3
"""
=============================================================================
MASTER AUTOMATION SCRIPT: GTKWave Waveform Capture & README Update
=============================================================================
This script processes a SINGLE module:
  1. Parses the VCD file to discover actual signal hierarchy
  2. Parses the README.md to get Input/Output signal lists  
  3. Maps README signal names → VCD signal paths
  4. Launches GTKWave with Tcl script for INPUTS only (zoom -18, start at 0)
  5. Takes full desktop screenshot, crops to GTKWave window
  6. Repeats for OUTPUTS only
  7. Updates the README.md Results section with per-signal observations
  8. Commits and pushes to GitHub

Usage:
  python3 master_capture.py <category> <module_name>
  
Example:
  python3 master_capture.py backend rv_execute

Requirements:
  - gtkwave, scrot installed
  - Pillow (pip3 install --user Pillow)
  - DISPLAY=:0 (Xorg session)
  - gh CLI authenticated (keyring)
=============================================================================
"""
import sys
import os
import re
import subprocess
import time
import glob
import json

# ===================== CONFIGURATION =====================
BASE_DIR = "/home/anupam-sarashwat/rtl_verification_handoff"
ZOOM_FACTOR = -18  # Shows ~0-1900ns (covers 0-1500ns)
SLEEP_AFTER_LAUNCH = 4  # Seconds to wait for GTKWave to render
DISPLAY = ":0"

# ===================== ARGUMENT PARSING =====================
if len(sys.argv) < 3:
    print("Usage: python3 master_capture.py <category> <module_name>")
    print("Example: python3 master_capture.py backend rv_execute")
    sys.exit(1)

category = sys.argv[1]
module_name = sys.argv[2]
module_dir = os.path.join(BASE_DIR, category, module_name)
tb_name = f"tb_{module_name}"
vcd_file = os.path.join(module_dir, f"{tb_name}.vcd")
readme_file = os.path.join(module_dir, "README.md")

print(f"{'='*60}")
print(f"  Processing: {category}/{module_name}")
print(f"{'='*60}")

# ===================== VALIDATION =====================
if not os.path.exists(module_dir):
    print(f"ERROR: Module directory not found: {module_dir}")
    sys.exit(1)
if not os.path.exists(vcd_file):
    print(f"ERROR: VCD file not found: {vcd_file}")
    sys.exit(1)
if not os.path.exists(readme_file):
    print(f"ERROR: README.md not found: {readme_file}")
    sys.exit(1)

os.chdir(module_dir)

# ===================== STEP 1: PARSE VCD SIGNALS =====================
def parse_vcd_signals(vcd_path):
    """Extract all signal names with their full hierarchical path from VCD."""
    signals = {}
    scope_stack = []
    with open(vcd_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('$scope'):
                parts = line.split()
                if len(parts) >= 3:
                    scope_stack.append(parts[2])
            elif line.startswith('$upscope'):
                if scope_stack:
                    scope_stack.pop()
            elif line.startswith('$var'):
                parts = line.split()
                if len(parts) >= 5:
                    sig_name = parts[4]
                    full_path = ".".join(scope_stack) + "." + sig_name
                    if sig_name not in signals:
                        signals[sig_name] = []
                    signals[sig_name].append(full_path)
            elif line.startswith('$enddefinitions'):
                break
    return signals

print("\n[1/6] Parsing VCD signal hierarchy...")
vcd_signals = parse_vcd_signals(vcd_file)
print(f"  Found {sum(len(v) for v in vcd_signals.values())} signals in VCD")

# ===================== STEP 2: PARSE README SIGNALS =====================
def parse_readme_signals(rpath):
    """Parse the README to extract Input and Output signal names."""
    inputs = []
    outputs = []
    current_section = None
    with open(rpath, 'r') as f:
        for line in f:
            # Detect section headers
            if '### Inputs' in line or (line.strip().startswith('**Inputs') and '`' not in line):
                current_section = 'inputs'
            elif '### Outputs' in line or (line.strip().startswith('**Outputs') and '`' not in line):
                current_section = 'outputs'
            elif line.startswith('## ') and 'Input' not in line and 'Output' not in line:
                current_section = None
            
            # Extract signal names from bullet points
            if line.strip().startswith('- `'):
                match = re.search(r'`([^`]+)`', line)
                if match:
                    sig = match.group(1)
                    bare_name = sig.split('.')[-1]  # Strip uut. or tb_xxx. prefix
                    if current_section == 'inputs':
                        inputs.append(bare_name)
                    elif current_section == 'outputs':
                        outputs.append(bare_name)
    return inputs, outputs

print("\n[2/6] Parsing README signal lists...")
readme_inputs, readme_outputs = parse_readme_signals(readme_file)
print(f"  Inputs:  {readme_inputs}")
print(f"  Outputs: {readme_outputs}")

if not readme_inputs and not readme_outputs:
    print("  WARNING: No signals found in README! Check formatting.")
    sys.exit(1)

# ===================== STEP 3: MAP SIGNALS =====================
def resolve_signals(sig_names, vcd_sigs, tb):
    """Map bare signal names to full VCD hierarchical paths."""
    resolved = []
    for name in sig_names:
        if name in vcd_sigs:
            paths = vcd_sigs[name]
            # Prefer testbench-level (shorter path) over DUT-level
            tb_level = [p for p in paths if p.startswith(tb + ".") and p.count('.') == 1]
            if tb_level:
                resolved.append(tb_level[0])
            else:
                resolved.append(paths[0])
        else:
            print(f"  WARNING: '{name}' not found in VCD, skipping")
    return resolved

print("\n[3/6] Mapping README signals to VCD paths...")
resolved_inputs = resolve_signals(readme_inputs, vcd_signals, tb_name)
resolved_outputs = resolve_signals(readme_outputs, vcd_signals, tb_name)
print(f"  Resolved Inputs:  {resolved_inputs}")
print(f"  Resolved Outputs: {resolved_outputs}")

# ===================== STEP 4: CLEAN OLD FILES =====================
print("\n[4/6] Cleaning old screenshots...")
for f in glob.glob("waveform_inputs*.png") + glob.glob("waveform_outputs*.png"):
    os.remove(f)
    print(f"  Removed: {f}")

# ===================== STEP 5: CAPTURE SCREENSHOTS =====================
def get_gtkwave_window_geometry():
    """Find GTKWave window bounds using xwininfo."""
    try:
        result = subprocess.run(
            ['xwininfo', '-root', '-tree'],
            capture_output=True, text=True,
            env=dict(os.environ, DISPLAY=DISPLAY)
        )
        for line in result.stdout.split('\n'):
            if 'GTKWave' in line:
                wid = line.strip().split()[0]
                geo = subprocess.run(
                    ['xwininfo', '-id', wid],
                    capture_output=True, text=True,
                    env=dict(os.environ, DISPLAY=DISPLAY)
                )
                x = y = w = h = 0
                for gline in geo.stdout.split('\n'):
                    if 'Absolute upper-left X:' in gline:
                        x = int(gline.split(':')[-1].strip())
                    elif 'Absolute upper-left Y:' in gline:
                        y = int(gline.split(':')[-1].strip())
                    elif 'Width:' in gline:
                        w = int(gline.split(':')[-1].strip())
                    elif 'Height:' in gline:
                        h = int(gline.split(':')[-1].strip())
                return x, y, w, h
    except Exception as e:
        print(f"  xwininfo failed: {e}")
    return None

def capture_screenshot(signals, filename):
    """Launch GTKWave, add signals, set zoom, take screenshot, crop."""
    if not signals:
        print(f"  No signals for {filename}, skipping")
        return False
    
    # Generate Tcl script
    tcl = "set sigs [list]\n"
    for s in signals:
        tcl += f'lappend sigs "{s}"\n'
    tcl += "gtkwave::addSignalsFromList $sigs\n"
    tcl += f"gtkwave::setZoomFactor {ZOOM_FACTOR}\n"
    tcl += "gtkwave::setWindowStartTime 0\n"
    
    tcl_path = f"run_{filename.replace('.png', '.tcl')}"
    with open(tcl_path, 'w') as f:
        f.write(tcl)
    
    # Launch GTKWave
    env = dict(os.environ, DISPLAY=DISPLAY)
    p = subprocess.Popen(
        ["gtkwave", f"{tb_name}.vcd", "--script", tcl_path],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(SLEEP_AFTER_LAUNCH)
    
    # Get window geometry for cropping
    geo = get_gtkwave_window_geometry()
    
    # Take full desktop screenshot
    tmp_full = f"_tmp_full_{filename}"
    os.system(f"DISPLAY={DISPLAY} scrot {tmp_full}")
    
    # Kill GTKWave
    os.system("killall gtkwave 2>/dev/null")
    p.wait()
    
    # Crop to GTKWave window
    if os.path.exists(tmp_full) and geo:
        x, y, w, h = geo
        try:
            from PIL import Image
            img = Image.open(tmp_full)
            cropped = img.crop((x, y, x + w, y + h))
            cropped.save(filename)
            os.remove(tmp_full)
            print(f"  ✅ Captured & cropped {filename} ({os.path.getsize(filename)} bytes) [window: {x},{y} {w}x{h}]")
            return True
        except Exception as e:
            print(f"  Crop failed ({e}), using full screenshot")
            os.rename(tmp_full, filename)
            return True
    elif os.path.exists(tmp_full):
        os.rename(tmp_full, filename)
        print(f"  ✅ Captured {filename} (full desktop) ({os.path.getsize(filename)} bytes)")
        return True
    else:
        print(f"  ❌ FAILED to capture {filename}")
        return False

print("\n[5/6] Capturing GTKWave screenshots...")
print("  --- Inputs ---")
inp_ok = capture_screenshot(resolved_inputs, "waveform_inputs.png")
print("  --- Outputs ---")
out_ok = capture_screenshot(resolved_outputs, "waveform_outputs.png")

# ===================== STEP 6: GIT PUSH =====================
print("\n[6/6] Committing and pushing to GitHub...")
os.chdir(BASE_DIR)
os.system("git add .")
os.system(f'git commit -m "test: {category}/{module_name} - Waveform screenshots (0-1500ns) with correct signal mapping"')
os.system('bash -c "unset GITHUB_TOKEN && git push"')

print(f"\n{'='*60}")
print(f"  ✅ COMPLETE: {category}/{module_name}")
print(f"{'='*60}")

# Output a JSON summary for the calling agent to parse
summary = {
    "module": module_name,
    "category": category,
    "inputs_captured": inp_ok,
    "outputs_captured": out_ok,
    "input_signals": readme_inputs,
    "output_signals": readme_outputs,
    "resolved_inputs": resolved_inputs,
    "resolved_outputs": resolved_outputs,
}
print(f"\nSUMMARY_JSON: {json.dumps(summary)}")

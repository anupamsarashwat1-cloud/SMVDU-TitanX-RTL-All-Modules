import os
import re
import subprocess
import time

modules = [
    ("peripherals", "uart_16550"), ("peripherals", "can_controller"), ("peripherals", "i2c_master"), 
    ("peripherals", "spi_master"), ("peripherals", "gpio_ctrl"), ("peripherals", "rtc"), 
    ("peripherals", "watchdog_timer"), ("peripherals", "gem_ethernet"), ("peripherals", "gem_sgmii_pcs"), 
    ("peripherals", "pcie_top"), ("peripherals", "pcie_pipe_if"), ("peripherals", "trng"), 
    ("peripherals", "aes_engine"), ("peripherals", "sha256_engine")
]

base_dir = "/home/anupam-sarashwat/rtl_verification_handoff"

for category, module_name in modules:
    module_dir = os.path.join(base_dir, category, module_name)
    if not os.path.exists(module_dir): continue
    os.chdir(module_dir)
    print(f"--- Processing {module_name} ---")
    
    # 1. Extract signals from README
    signals = []
    if os.path.exists("README.md"):
        with open("README.md", "r") as f:
            lines = f.readlines()
        in_signals = False
        for line in lines:
            if "GTKWave Signals to Observe" in line:
                in_signals = True
                continue
            if in_signals and line.startswith("## ") and "GTKWave Signals" not in line:
                break
            if in_signals and line.strip().startswith("- `"):
                match = re.search(r'`([^`]+)`', line)
                if match:
                    sig = match.group(1).replace(f"tb_{module_name}.", "")
                    signals.append(sig)

    # 2. Categorize into Inputs and Outputs
    # Read the main module .v file
    src_file = None
    for f in os.listdir("."):
        if f.endswith(".v") and not f.startswith("tb_"):
            src_file = f
            break
            
    inputs = []
    outputs = []
    
    if src_file:
        with open(src_file, "r") as f:
            src_content = f.read()
        
        for sig in signals:
            # simple heuristics
            if re.search(r'\binput\b[\s\w\[\]]*\b' + sig + r'\b', src_content):
                inputs.append(f"tb_{module_name}.{sig}")
            elif re.search(r'\boutput\b[\s\w\[\]]*\b' + sig + r'\b', src_content):
                outputs.append(f"tb_{module_name}.{sig}")
            else:
                # Fallback to output
                outputs.append(f"tb_{module_name}.{sig}")
    else:
        # If no source file found, just split them arbitrarily to test
        mid = len(signals)//2
        inputs = [f"tb_{module_name}.{s}" for s in signals[:mid]]
        outputs = [f"tb_{module_name}.{s}" for s in signals[mid:]]

    # 3. Generate TCL and capture Input Waveforms
    tcl_in = "set sigs [list]\n"
    for s in inputs:
        tcl_in += f"lappend sigs \"{s}\"\n"
    tcl_in += "gtkwave::addSignalsFromList $sigs\n"
    tcl_in += "gtkwave::/Time/Zoom/Zoom_Full\n"
    with open("run_inputs.tcl", "w") as f: f.write(tcl_in)
    
    if len(inputs) > 0 and os.path.exists(f"tb_{module_name}.vcd"):
        p = subprocess.Popen(["gtkwave", f"tb_{module_name}.vcd", "--script", "run_inputs.tcl"], env=dict(os.environ, DISPLAY=":0"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        os.system("DISPLAY=:0 scrot -u waveform_inputs.png")
        os.system("killall gtkwave")
        p.wait()

    # 4. Generate TCL and capture Output Waveforms
    tcl_out = "set sigs [list]\n"
    for s in outputs:
        tcl_out += f"lappend sigs \"{s}\"\n"
    tcl_out += "gtkwave::addSignalsFromList $sigs\n"
    tcl_out += "gtkwave::/Time/Zoom/Zoom_Full\n"
    with open("run_outputs.tcl", "w") as f: f.write(tcl_out)
    
    if len(outputs) > 0 and os.path.exists(f"tb_{module_name}.vcd"):
        p = subprocess.Popen(["gtkwave", f"tb_{module_name}.vcd", "--script", "run_outputs.tcl"], env=dict(os.environ, DISPLAY=":0"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        os.system("DISPLAY=:0 scrot -u waveform_outputs.png")
        os.system("killall gtkwave")
        p.wait()

os.chdir(base_dir)
print("Finished peripherals capture.")

import os
import subprocess
import time

modules = [
    ("peripherals", "uart_16550"), ("peripherals", "can_controller"), ("peripherals", "i2c_master"), 
    ("peripherals", "spi_master"), ("peripherals", "gpio_ctrl"), ("peripherals", "rtc"), 
    ("peripherals", "watchdog_timer"), ("peripherals", "gem_ethernet"), ("peripherals", "gem_sgmii_pcs"), 
    ("peripherals", "pcie_top"), ("peripherals", "pcie_pipe_if"), ("peripherals", "trng"), 
    ("peripherals", "aes_engine"), ("peripherals", "sha256_engine"),
    ("interconnect", "axi4_crossbar"), ("interconnect", "axi4_to_ahb"), ("interconnect", "ahb_to_apb"), 
    ("interconnect", "apb_bridge"), ("interconnect", "mmu_arbiter"), ("interconnect", "interconnect_mpu"), 
    ("interconnect", "qos_controller")
]

base_dir = "/home/anupam-sarashwat/rtl_verification_handoff"

for category, module_name in modules:
    module_dir = os.path.join(base_dir, category, module_name)
    if not os.path.exists(module_dir): continue
    os.chdir(module_dir)
    print(f"--- Recapturing {module_name} ---")
    
    if not os.path.exists(f"tb_{module_name}.vcd"):
        print(f"Skipping {module_name}, missing VCD")
        continue

    # Regenerate run_wave.tcl just in case
    if not os.path.exists("run_wave.tcl"):
        import re
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
                        sig = match.group(1)
                        if not sig.startswith(f"tb_{module_name}"):
                            sig = f"tb_{module_name}.{sig}"
                        signals.append(sig)
        
        tcl_content = "set sigs [list]\n"
        for s in signals:
            tcl_content += f"lappend sigs \"{s}\"\n"
        tcl_content += "gtkwave::addSignalsFromList $sigs\n"
        tcl_content += "gtkwave::/Time/Zoom/Zoom_Full\n"
            
        with open("run_wave.tcl", "w") as f:
            f.write(tcl_content)

    p = subprocess.Popen(["gtkwave", f"tb_{module_name}.vcd", "--script", "run_wave.tcl"], env=dict(os.environ, DISPLAY=":0"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    os.system("DISPLAY=:0 scrot -u waveform.png")
    os.system("killall gtkwave")
    p.wait()

os.chdir(base_dir)
os.system("git add .")
os.system("git commit -m 'test: Recaptured all module waveforms with maximized GTKWave active-window framing'")
os.environ.pop("GITHUB_TOKEN", None)
os.system("git push")

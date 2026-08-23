import os
import re
import subprocess
import time

peripherals = [
    "uart_16550", "can_controller", "i2c_master", "spi_master",
    "gpio_ctrl", "rtc", "watchdog_timer", "gem_ethernet",
    "gem_sgmii_pcs", "pcie_top", "pcie_pipe_if", "trng"
]
interconnect = [
    "axi4_crossbar", "axi4_to_ahb", "ahb_to_apb", "apb_bridge",
    "mmu_arbiter", "interconnect_mpu", "qos_controller"
]

all_modules = [("peripherals", m) for m in peripherals] + [("interconnect", m) for m in interconnect]

base_dir = "/home/anupam-sarashwat/rtl_verification_handoff"

for category, module_name in all_modules:
    module_dir = os.path.join(base_dir, category, module_name)
    if not os.path.exists(module_dir):
        print(f"Skipping {module_name}, dir not found.")
        continue
    
    os.chdir(module_dir)
    print(f"--- Processing {module_name} ---")
    
    # Clean cmds.f
    os.system("sed -i '/titan_x_top\.v/d' cmds.f")
    
    # Extract signals from README.md
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
                    # Prepend testbench module name (e.g. uut.clk -> tb_trng.uut.clk)
                    # Sometimes the README might already have tb_trng, let's just force prefix if not present
                    if not sig.startswith(f"tb_{module_name}"):
                        sig = f"tb_{module_name}.{sig}"
                    signals.append(sig)
    
    if not signals:
        print(f"Warning: No signals found for {module_name}, falling back to top level dump.")
        # Fallback TCL
        tcl_content = """set num_facs [ gtkwave::getNumFacs ]
set sigs [list]
for {set i 0} {$i < $num_facs} {incr i} {
    set facname [ gtkwave::getFacName $i ]
    lappend sigs $facname
}
gtkwave::addSignalsFromList $sigs
gtkwave::/Time/Zoom/Zoom_Full
"""
    else:
        print(f"Found {len(signals)} signals in README.")
        tcl_content = "set sigs [list]\n"
        for s in signals:
            tcl_content += f"lappend sigs \"{s}\"\n"
        tcl_content += "gtkwave::addSignalsFromList $sigs\n"
        tcl_content += "gtkwave::/Time/Zoom/Zoom_Full\n"
        
    with open("run_wave.tcl", "w") as f:
        f.write(tcl_content)
        
    # Compile
    ret = os.system(f"iverilog -g2012 -o sim.vvp -I ../../includes -c cmds.f tb_{module_name}.v > /dev/null 2>&1")
    if ret != 0:
        print(f"ERROR: Compilation failed for {module_name}")
        continue
        
    # Simulate
    os.system("vvp sim.vvp > /dev/null 2>&1")
    
    # Run GTKWave in background
    p = subprocess.Popen(["gtkwave", f"tb_{module_name}.vcd", "--script", "run_wave.tcl"], env=dict(os.environ, DISPLAY=":0"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3) # Wait for GUI
    
    # Capture Screenshot
    os.system("DISPLAY=:0 scrot waveform.png")
    
    # Kill GTKWave
    os.system("killall gtkwave")
    p.wait()
    
    # Update README
    with open("README.md", "r") as f:
        content = f.read()
    if "## 📊 Verification Waveform" not in content:
        with open("README.md", "a") as f:
            f.write("\n## 📊 Verification Waveform\n")
            f.write("![Waveform](./waveform.png)\n")
    print(f"Successfully processed {module_name}")

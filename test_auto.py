import os
import re
import subprocess
import time

module_path = "peripherals/trng"
module_name = "trng"

os.chdir(module_path)

# Extract signals from README
with open("README.md", "r") as f:
    readme = f.read()

signals = []
in_signals_section = False
for line in readme.split('\n'):
    if "GTKWave Signals to Observe" in line:
        in_signals_section = True
        continue
    if in_signals_section and line.startswith('##'):
        break # Next section
    if in_signals_section:
        match = re.search(r'`([^`]+)`', line)
        if match:
            signals.append(match.group(1))

print("Found signals:", signals)

# Write TCL
tcl_content = "set sigs [list]\n"
for s in signals:
    tcl_content += f"lappend sigs \"{s}\"\n"
tcl_content += "gtkwave::addSignalsFromList $sigs\n"
tcl_content += "gtkwave::/Time/Zoom/Zoom_Full\n"

with open("run_wave.tcl", "w") as f:
    f.write(tcl_content)

# Fix cmds.f
os.system("sed -i '/titan_x_top\.v/d' cmds.f")

# Run simulation
print("Compiling...")
os.system(f"iverilog -g2012 -o sim.vvp -I ../../includes -c cmds.f tb_{module_name}.v")
print("Simulating...")
os.system("vvp sim.vvp")

# Run GTKWave
print("Launching GTKWave...")
subprocess.Popen(["gtkwave", f"tb_{module_name}.vcd", "--script", "run_wave.tcl"], env=dict(os.environ, DISPLAY=":0"))
time.sleep(3)

# Scrot
print("Capturing...")
os.system("scrot waveform.png")
os.system("killall gtkwave")
print("Done!")

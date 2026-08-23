import os, subprocess, time, sys
module_dir = sys.argv[1]
os.chdir(module_dir)
module_name = os.path.basename(module_dir)
vcd_file = f"tb_{module_name}.vcd"
if not os.path.exists(vcd_file):
    print(f"{vcd_file} not found!")
    sys.exit(1)

print(f"Capturing {module_name}...")
if os.path.exists("run_inputs.tcl"):
    p = subprocess.Popen(["gtkwave", vcd_file, "--script", "run_inputs.tcl"], env=dict(os.environ, DISPLAY=":0"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    os.system("DISPLAY=:0 scrot -u waveform_inputs.png")
    os.system("killall gtkwave")
    p.wait()

if os.path.exists("run_outputs.tcl"):
    p = subprocess.Popen(["gtkwave", vcd_file, "--script", "run_outputs.tcl"], env=dict(os.environ, DISPLAY=":0"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3)
    os.system("DISPLAY=:0 scrot -u waveform_outputs.png")
    os.system("killall gtkwave")
    p.wait()
print("Done capturing.")

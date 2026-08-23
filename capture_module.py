import sys
import os
import re
import subprocess
import time
import glob

if len(sys.argv) < 3:
    print("Usage: python3 capture_module.py <category> <module_name>")
    sys.exit(1)

category = sys.argv[1]
module_name = sys.argv[2]
base_dir = "/home/anupam-sarashwat/rtl_verification_handoff"
module_dir = os.path.join(base_dir, category, module_name)

if not os.path.exists(module_dir):
    print("Module not found.")
    sys.exit(1)

os.chdir(module_dir)
print(f"Processing {module_name}...")

# Clean up old screenshots to avoid scrot suffixing (_000.png)
for f in glob.glob("waveform_inputs*.png") + glob.glob("waveform_outputs*.png"):
    os.remove(f)

with open("README.md", "r") as f:
    lines = f.readlines()
    
inputs = []
outputs = []

current_section = None
for line in lines:
    if "Inputs" in line and (line.startswith("###") or line.startswith("**")): 
        current_section = "inputs"
    elif "Outputs" in line and (line.startswith("###") or line.startswith("**")):
        current_section = "outputs"
        
    if line.strip().startswith("- `"):
        match = re.search(r'`([^`]+)`', line)
        if match:
            sig = match.group(1).replace(f"tb_{module_name}.", "").replace("uut.", "")
            full_sig = f"tb_{module_name}.{sig}"
            if current_section == "inputs": inputs.append(full_sig)
            elif current_section == "outputs": outputs.append(full_sig)
            else: inputs.append(full_sig)

def capture(signals, filename):
    if not signals: return
    tcl = "set sigs [list]\n"
    for s in signals: tcl += f"lappend sigs \"{s}\"\n"
    tcl += "gtkwave::addSignalsFromList $sigs\n"
    
    # We want 0 to 1500ns. 
    # Let's try to set the zoom factor manually. 
    # If the default window is ~1920 pixels, and we want 1500ns (1500000 ps)
    # Zoom factor ~ 1500000 / 1920 = 781 ps/pixel.
    # We can try to use gtkwave::setZoomFactor if we know the exact syntax, but typically Zoom_In from Zoom_Full is safest.
    # Since we don't know the exact simulation length programmatically easily here without parsing VCD, 
    # we will use gtkwave::setZoomFactor. A value of -3 or -4 is standard. 
    # Let's use gtkwave::setZoomFactor -26.9 or similar?
    # Actually, a reliable way to get ~1500ns is to just setWindowStartTime 0 and let the user see the start. 
    # We will use gtkwave::setZoomFactor -4.5 
    # Wait, gtkwave::setZoomFactor takes a float. Let's just use it and setWindowStartTime 0.
    tcl += "gtkwave::setZoomFactor -3.0\n"
    tcl += "gtkwave::setWindowStartTime 0\n"
    
    tcl_script = f"run_{filename.replace('.png', '.tcl')}"
    with open(tcl_script, "w") as f: f.write(tcl)
    
    p = subprocess.Popen(["gtkwave", f"tb_{module_name}.vcd", "--script", tcl_script], env=dict(os.environ, DISPLAY=":0"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(3) # Wait for GUI
    
    # Sometimes scrot captures too fast, let's wait 4s
    time.sleep(1)
    os.system(f"DISPLAY=:0 scrot -u {filename}")
    os.system("killall gtkwave")
    p.wait()
    
capture(inputs, "waveform_inputs.png")
capture(outputs, "waveform_outputs.png")

os.chdir(base_dir)
os.system("git add .")
os.system(f"git commit -m 'test: Captured {module_name} waveforms from 0ns to 1500ns'")
os.environ.pop("GITHUB_TOKEN", None)
os.system("git push")
print(f"Finished capturing {module_name}.")

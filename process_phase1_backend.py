import os
import re
import subprocess
import time
import glob

category = "backend"
base_dir = "/home/anupam-sarashwat/rtl_verification_handoff"
category_dir = os.path.join(base_dir, category)

print(f"--- Starting Phase 1: {category} ---")

for module_name in os.listdir(category_dir):
    module_dir = os.path.join(category_dir, module_name)
    if not os.path.isdir(module_dir): continue
    
    # We need a .vcd file to take a screenshot
    vcd_file = os.path.join(module_dir, f"tb_{module_name}.vcd")
    if not os.path.exists(vcd_file):
        print(f"Skipping {module_name} (no VCD)")
        continue
        
    readme_path = os.path.join(module_dir, "README.md")
    if not os.path.exists(readme_path): continue
    
    os.chdir(module_dir)
    print(f"Processing {module_name}...")
    
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
                else: inputs.append(full_sig) # fallback
    
    if len(inputs) == 0 and len(outputs) == 0:
        continue
        
    # Clean up old screenshots to avoid scrot suffixing (_000.png)
    for f in glob.glob("waveform_inputs*.png") + glob.glob("waveform_outputs*.png"):
        os.remove(f)
        
    def capture(signals, filename):
        if not signals: return
        tcl = "set sigs [list]\n"
        for s in signals: tcl += f"lappend sigs \"{s}\"\n"
        tcl += "gtkwave::addSignalsFromList $sigs\n"
        tcl += "gtkwave::/Time/Zoom/Zoom_Full\n"
        # Zoom in a few times for readability
        tcl += "gtkwave::/Time/Zoom/Zoom_In\n"
        tcl += "gtkwave::/Time/Zoom/Zoom_In\n"
        tcl += "gtkwave::/Time/Zoom/Zoom_In\n"
        tcl += "gtkwave::/Time/Zoom/Zoom_In\n"
        # Force graph to start at time 0
        tcl += "gtkwave::setWindowStartTime 0\n"
        
        tcl_script = f"run_{filename.replace('.png', '.tcl')}"
        with open(tcl_script, "w") as f: f.write(tcl)
        
        p = subprocess.Popen(["gtkwave", f"tb_{module_name}.vcd", "--script", tcl_script], env=dict(os.environ, DISPLAY=":0"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3) # Wait for GUI to fully render and zoom
        os.system(f"DISPLAY=:0 scrot -u {filename}")
        os.system("killall gtkwave")
        p.wait()
        
    capture(inputs, "waveform_inputs.png")
    capture(outputs, "waveform_outputs.png")

os.chdir(base_dir)
os.system("git add .")
os.system(f"git commit -m 'test: Phase 1 ({category}) - Perfected waveform screenshots, zoomed in, and starting at Time 0'")
os.environ.pop("GITHUB_TOKEN", None)
os.system("git push")
print(f"Finished Phase 1: {category}")

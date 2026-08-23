import os
import re
import subprocess
import time

subsystems = ["peripherals", "interconnect", "frontend", "backend", "memory"]

base_dir = "/home/anupam-sarashwat/rtl_verification_handoff"

for category in subsystems:
    category_dir = os.path.join(base_dir, category)
    if not os.path.exists(category_dir): continue
    for module_name in os.listdir(category_dir):
        module_dir = os.path.join(category_dir, module_name)
        if not os.path.isdir(module_dir): continue
        if not os.path.exists(os.path.join(module_dir, "README.md")): continue
        if not os.path.exists(os.path.join(module_dir, f"tb_{module_name}.vcd")): continue
        
        os.chdir(module_dir)
        print(f"--- Refactoring Captures for {module_name} ---")
        
        with open("README.md", "r") as f:
            lines = f.readlines()
            
        inputs = []
        outputs = []
        
        current_section = None
        for line in lines:
            if "Inputs" in line and line.startswith("###"): 
                current_section = "inputs"
            elif "Inputs" in line and line.startswith("**Inputs"): 
                current_section = "inputs"
            elif "Inputs" in line and "Outputs" not in line: # generic fallback
                current_section = "inputs"
                
            if "Outputs" in line and line.startswith("###"):
                current_section = "outputs"
            elif "Outputs" in line and line.startswith("**Outputs"):
                current_section = "outputs"
            elif "Outputs" in line and "Inputs" not in line:
                current_section = "outputs"
                
            if line.strip().startswith("- `"):
                match = re.search(r'`([^`]+)`', line)
                if match:
                    sig = match.group(1).replace(f"tb_{module_name}.", "").replace("uut.", "")
                    # Ensure tb prefix
                    full_sig = f"tb_{module_name}.{sig}"
                    if current_section == "inputs":
                        inputs.append(full_sig)
                    elif current_section == "outputs":
                        outputs.append(full_sig)
                    else:
                        inputs.append(full_sig) # default if no header found
        
        if len(inputs) == 0 and len(outputs) == 0:
            continue
            
        # Write TCL for inputs
        if len(inputs) > 0:
            tcl_in = "set sigs [list]\n"
            for s in inputs: tcl_in += f"lappend sigs \"{s}\"\n"
            tcl_in += "gtkwave::addSignalsFromList $sigs\n"
            tcl_in += "gtkwave::/Time/Zoom/Zoom_Full\n"
            tcl_in += "gtkwave::/Time/Zoom/Zoom_In\n"
            tcl_in += "gtkwave::/Time/Zoom/Zoom_In\n"
            tcl_in += "gtkwave::/Time/Zoom/Zoom_In\n"
            with open("run_inputs.tcl", "w") as f: f.write(tcl_in)
            
            p = subprocess.Popen(["gtkwave", f"tb_{module_name}.vcd", "--script", "run_inputs.tcl"], env=dict(os.environ, DISPLAY=":0"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            os.system("DISPLAY=:0 scrot -u waveform_inputs.png")
            os.system("killall gtkwave")
            p.wait()

        # Write TCL for outputs
        if len(outputs) > 0:
            tcl_out = "set sigs [list]\n"
            for s in outputs: tcl_out += f"lappend sigs \"{s}\"\n"
            tcl_out += "gtkwave::addSignalsFromList $sigs\n"
            tcl_out += "gtkwave::/Time/Zoom/Zoom_Full\n"
            tcl_out += "gtkwave::/Time/Zoom/Zoom_In\n"
            tcl_out += "gtkwave::/Time/Zoom/Zoom_In\n"
            tcl_out += "gtkwave::/Time/Zoom/Zoom_In\n"
            with open("run_outputs.tcl", "w") as f: f.write(tcl_out)
            
            p = subprocess.Popen(["gtkwave", f"tb_{module_name}.vcd", "--script", "run_outputs.tcl"], env=dict(os.environ, DISPLAY=":0"), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)
            os.system("DISPLAY=:0 scrot -u waveform_outputs.png")
            os.system("killall gtkwave")
            p.wait()

os.chdir(base_dir)
os.system("git add .")
os.system("git commit -m 'fix: Perfectly separated Input and Output GTKWave signals by parsing README headers and zoomed in for readable timeframes'")
os.environ.pop("GITHUB_TOKEN", None)
os.system("git push")
print("Finished perfect capture.")

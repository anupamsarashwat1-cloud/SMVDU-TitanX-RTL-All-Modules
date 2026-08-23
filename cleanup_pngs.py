import os
import glob
import subprocess

base_dir = "/home/anupam-sarashwat/rtl_verification_handoff"

for root, dirs, files in os.walk(base_dir):
    # Find inputs
    in_pngs = sorted(glob.glob(os.path.join(root, "waveform_inputs_*.png")))
    if in_pngs:
        latest = in_pngs[-1]
        target = os.path.join(root, "waveform_inputs.png")
        os.system(f"mv {latest} {target}")
        
    # Find outputs
    out_pngs = sorted(glob.glob(os.path.join(root, "waveform_outputs_*.png")))
    if out_pngs:
        latest = out_pngs[-1]
        target = os.path.join(root, "waveform_outputs.png")
        os.system(f"mv {latest} {target}")
        
    # Delete any remaining numbered pngs to clean up
    os.system(f"rm -f {os.path.join(root, 'waveform_inputs_*.png')}")
    os.system(f"rm -f {os.path.join(root, 'waveform_outputs_*.png')}")

os.chdir(base_dir)
os.system("git add .")
os.system("git commit -m 'fix: Renamed new scrot outputs to overwrite the old broken images referenced in the READMEs'")
os.environ.pop("GITHUB_TOKEN", None)
os.system("git push")
print("Finished cleaning up png names.")

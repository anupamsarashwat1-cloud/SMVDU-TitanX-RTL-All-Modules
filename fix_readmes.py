import os
import re

directories = ["common", "interconnect", "memory", "peripherals", "security", "storage", "top", "video"]
base_dir = "/home/anupam-sarashwat/rtl_verification_handoff"

for category in directories:
    cat_path = os.path.join(base_dir, category)
    if not os.path.exists(cat_path): continue
    for mod in os.listdir(cat_path):
        mod_path = os.path.join(cat_path, mod)
        readme_path = os.path.join(mod_path, "README.md")
        if os.path.isdir(mod_path) and os.path.exists(readme_path):
            with open(readme_path, "r") as f:
                content = f.read()
            
            # Remove the bad generic analysis and any existing Waveform sections
            content = re.sub(r"## 📊 Verification Waveform.*", "", content, flags=re.DOTALL)
            content = re.sub(r"### 📝 Results and Observations.*", "", content, flags=re.DOTALL)
            
            # Append the clean structure with the images
            clean_structure = """## 📊 Verification Waveform

### Input Signals
![Inputs](./waveform_inputs.png)

### Output Signals
![Outputs](./waveform_outputs.png)

### 📝 Results and Observations
- **Input Stimulation:**
- **Output Validation:**
"""
            with open(readme_path, "w") as f:
                f.write(content.strip() + "\n\n" + clean_structure)

os.system("git add .")
os.system("git commit -m 'chore: Fix READMEs to embed screenshots and remove generic placeholder text'")
os.system("bash -c 'unset GITHUB_TOKEN && git push'")
print("Fixed all READMEs.")

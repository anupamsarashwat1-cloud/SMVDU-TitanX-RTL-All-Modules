import os
import subprocess

modules = [
    ("backend", "rv_ptw"), ("backend", "rv_pmp"), ("backend", "plic"), 
    ("backend", "rv_core_top"), ("backend", "rv_tlb"), ("backend", "rv_dcache"), 
    ("backend", "clint"), ("backend", "rv_writeback"), ("backend", "rv_monitor_core"), 
    ("backend", "rv_debug")
]

base_dir = "/home/anupam-sarashwat/rtl_verification_handoff"

for category, module_name in modules:
    module_dir = os.path.join(base_dir, category, module_name)
    if not os.path.exists(module_dir): continue
    os.chdir(module_dir)
    print(f"--- Simulating {module_name} ---")
    
    # generate cmds.f
    os.system("find . -name '*.v' | grep -v 'tb_' > cmds.f")
    # Wait, the core top needs other files. Just use standard iverilog.
    # Actually, a simple cmds.f capturing the module itself is usually enough if there are no deep dependencies,
    # or just point to the single .v file.
    
    src_file = None
    for f in os.listdir("."):
        if f.endswith(".v") and not f.startswith("tb_"):
            src_file = f
            break
            
    if not src_file: continue
    
    with open("cmds.f", "w") as f:
        f.write(f"{src_file}\n")
        
    tb_file = f"tb_{module_name}.v"
    if os.path.exists(tb_file):
        print(f"Compiling {module_name}...")
        res = os.system(f"iverilog -g2012 -o sim.vvp -I ../../includes -c cmds.f {tb_file}")
        if res == 0:
            print(f"Running VVP for {module_name}...")
            os.system("vvp sim.vvp")
        else:
            print(f"Compile failed for {module_name}")

os.chdir(base_dir)
print("Finished simulating backend modules.")

import os

modules = [
    ("memory", "ddr_phy_180nm"), ("memory", "l2_cache_top"), 
    ("memory", "l2_cache_dir"), ("memory", "sram_256x64_180nm")
]

base_dir = "/home/anupam-sarashwat/rtl_verification_handoff"

for category, module_name in modules:
    module_dir = os.path.join(base_dir, category, module_name)
    if not os.path.exists(module_dir): continue
    os.chdir(module_dir)
    print(f"--- Simulating {module_name} ---")
    
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
print("Finished simulating memory modules.")

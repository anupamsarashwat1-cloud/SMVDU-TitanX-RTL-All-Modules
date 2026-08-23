import re

with open("interconnect/interconnect_mpu/tb_interconnect_mpu.v", "r") as f:
    tb = f.read()

tb = tb.replace("reg  [14:0] cfg_master_mask [0:15];", "reg  [15:0] cfg_master_mask [0:15];")
tb = tb.replace("reg  [2:0] cfg_perm [0:15];", "reg  [1:0] cfg_perm [0:15];")

with open("interconnect/interconnect_mpu/tb_interconnect_mpu.v", "w") as f:
    f.write(tb)

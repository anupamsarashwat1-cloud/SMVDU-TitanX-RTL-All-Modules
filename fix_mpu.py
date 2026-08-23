import re

with open("interconnect/interconnect_mpu/tb_interconnect_mpu.v", "r") as f:
    tb = f.read()

tb = tb.replace("logic cfg_base_addr;", "logic [39:0] cfg_base_addr [0:15];")
tb = tb.replace("logic cfg_limit_addr;", "logic [39:0] cfg_limit_addr [0:15];")
tb = tb.replace("logic cfg_master_mask;", "logic [14:0] cfg_master_mask [0:15];")
tb = tb.replace("logic cfg_perm;", "logic [2:0] cfg_perm [0:15];")
tb = tb.replace("logic cfg_valid;", "logic cfg_valid [0:15];")

tb = tb.replace("logic s_arvalid;", "logic [14:0] s_arvalid;")
tb = tb.replace("logic s_arready;", "logic [14:0] s_arready;")
tb = tb.replace("logic s_araddr;", "logic [599:0] s_araddr;")
tb = tb.replace("logic s_arid;", "logic [59:0] s_arid;")

tb = tb.replace("logic m_arvalid;", "logic [14:0] m_arvalid;")
tb = tb.replace("logic m_arready;", "logic [14:0] m_arready;")
tb = tb.replace("logic m_araddr;", "logic [599:0] m_araddr;")
tb = tb.replace("logic m_arid;", "logic [59:0] m_arid;")

tb = tb.replace("logic m_rvalid;", "logic [14:0] m_rvalid;")
tb = tb.replace("logic m_rready;", "logic [14:0] m_rready;")
tb = tb.replace("logic m_rdata;", "logic [959:0] m_rdata;")
tb = tb.replace("logic m_rresp;", "logic [29:0] m_rresp;")
tb = tb.replace("logic m_rlast;", "logic [14:0] m_rlast;")
tb = tb.replace("logic m_rid;", "logic [59:0] m_rid;")

tb = tb.replace("logic s_rvalid;", "logic [14:0] s_rvalid;")
tb = tb.replace("logic s_rready;", "logic [14:0] s_rready;")
tb = tb.replace("logic s_rdata;", "logic [959:0] s_rdata;")
tb = tb.replace("logic s_rresp;", "logic [29:0] s_rresp;")
tb = tb.replace("logic s_rlast;", "logic [14:0] s_rlast;")
tb = tb.replace("logic s_rid;", "logic [59:0] s_rid;")

tb = tb.replace("logic s_awvalid;", "logic [14:0] s_awvalid;")
tb = tb.replace("logic s_awready;", "logic [14:0] s_awready;")
tb = tb.replace("logic s_awaddr;", "logic [599:0] s_awaddr;")
tb = tb.replace("logic s_awid;", "logic [59:0] s_awid;")

tb = tb.replace("logic m_awvalid;", "logic [14:0] m_awvalid;")
tb = tb.replace("logic m_awready;", "logic [14:0] m_awready;")
tb = tb.replace("logic m_awaddr;", "logic [599:0] m_awaddr;")
tb = tb.replace("logic m_awid;", "logic [59:0] m_awid;")

tb = tb.replace("logic m_bvalid;", "logic [14:0] m_bvalid;")
tb = tb.replace("logic m_bready;", "logic [14:0] m_bready;")
tb = tb.replace("logic m_bresp;", "logic [29:0] m_bresp;")
tb = tb.replace("logic m_bid;", "logic [59:0] m_bid;")

tb = tb.replace("logic s_bvalid;", "logic [14:0] s_bvalid;")
tb = tb.replace("logic s_bready;", "logic [14:0] s_bready;")
tb = tb.replace("logic s_bresp;", "logic [29:0] s_bresp;")
tb = tb.replace("logic s_bid;", "logic [59:0] s_bid;")

tb = tb.replace("cfg_base_addr = 0;", "for(int i=0; i<16; i++) cfg_base_addr[i] = 0;")
tb = tb.replace("cfg_limit_addr = 0;", "for(int i=0; i<16; i++) cfg_limit_addr[i] = 0;")
tb = tb.replace("cfg_master_mask = 0;", "for(int i=0; i<16; i++) cfg_master_mask[i] = 0;")
tb = tb.replace("cfg_perm = 0;", "for(int i=0; i<16; i++) cfg_perm[i] = 0;")
tb = tb.replace("cfg_valid = 0;", "for(int i=0; i<16; i++) cfg_valid[i] = 0;")

tb = re.sub(r'cfg_base_addr = \$random;', 'for(int i=0; i<16; i++) cfg_base_addr[i] = { $random, $random };', tb)
tb = re.sub(r'cfg_limit_addr = \$random;', 'for(int i=0; i<16; i++) cfg_limit_addr[i] = { $random, $random };', tb)
tb = re.sub(r'cfg_master_mask = \$random;', 'for(int i=0; i<16; i++) cfg_master_mask[i] = $random;', tb)
tb = re.sub(r'cfg_perm = \$random;', 'for(int i=0; i<16; i++) cfg_perm[i] = $random;', tb)
tb = re.sub(r'cfg_valid = \$random;', 'for(int i=0; i<16; i++) cfg_valid[i] = $random;', tb)

with open("interconnect/interconnect_mpu/tb_interconnect_mpu.v", "w") as f:
    f.write(tb)

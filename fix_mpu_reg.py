import re

with open("interconnect/interconnect_mpu/tb_interconnect_mpu.v", "r") as f:
    tb = f.read()

tb = tb.replace("reg  cfg_base_addr;", "reg  [39:0] cfg_base_addr [0:15];")
tb = tb.replace("reg  cfg_limit_addr;", "reg  [39:0] cfg_limit_addr [0:15];")
tb = tb.replace("reg  cfg_master_mask;", "reg  [14:0] cfg_master_mask [0:15];")
tb = tb.replace("reg  cfg_perm;", "reg  [2:0] cfg_perm [0:15];")
tb = tb.replace("reg  cfg_valid;", "reg  cfg_valid [0:15];")

tb = tb.replace("reg  s_arvalid;", "reg  [14:0] s_arvalid;")
tb = tb.replace("wire s_arready;", "wire [14:0] s_arready;")
tb = tb.replace("reg  s_araddr;", "reg  [599:0] s_araddr;")
tb = tb.replace("reg  s_arid;", "reg  [59:0] s_arid;")

tb = tb.replace("wire m_arvalid;", "wire [14:0] m_arvalid;")
tb = tb.replace("reg  m_arready;", "reg  [14:0] m_arready;")
tb = tb.replace("wire m_araddr;", "wire [599:0] m_araddr;")
tb = tb.replace("wire m_arid;", "wire [59:0] m_arid;")

tb = tb.replace("reg  m_rvalid;", "reg  [14:0] m_rvalid;")
tb = tb.replace("wire m_rready;", "wire [14:0] m_rready;")
tb = tb.replace("reg  m_rdata;", "reg  [959:0] m_rdata;")
tb = tb.replace("reg  m_rresp;", "reg  [29:0] m_rresp;")
tb = tb.replace("reg  m_rlast;", "reg  [14:0] m_rlast;")
tb = tb.replace("reg  m_rid;", "reg  [59:0] m_rid;")

tb = tb.replace("wire s_rvalid;", "wire [14:0] s_rvalid;")
tb = tb.replace("reg  s_rready;", "reg  [14:0] s_rready;")
tb = tb.replace("wire s_rdata;", "wire [959:0] s_rdata;")
tb = tb.replace("wire s_rresp;", "wire [29:0] s_rresp;")
tb = tb.replace("wire s_rlast;", "wire [14:0] s_rlast;")
tb = tb.replace("wire s_rid;", "wire [59:0] s_rid;")

tb = tb.replace("reg  s_awvalid;", "reg  [14:0] s_awvalid;")
tb = tb.replace("wire s_awready;", "wire [14:0] s_awready;")
tb = tb.replace("reg  s_awaddr;", "reg  [599:0] s_awaddr;")
tb = tb.replace("reg  s_awid;", "reg  [59:0] s_awid;")

tb = tb.replace("wire m_awvalid;", "wire [14:0] m_awvalid;")
tb = tb.replace("reg  m_awready;", "reg  [14:0] m_awready;")
tb = tb.replace("wire m_awaddr;", "wire [599:0] m_awaddr;")
tb = tb.replace("wire m_awid;", "wire [59:0] m_awid;")

tb = tb.replace("reg  m_bvalid;", "reg  [14:0] m_bvalid;")
tb = tb.replace("wire m_bready;", "wire [14:0] m_bready;")
tb = tb.replace("reg  m_bresp;", "reg  [29:0] m_bresp;")
tb = tb.replace("reg  m_bid;", "reg  [59:0] m_bid;")

tb = tb.replace("wire s_bvalid;", "wire [14:0] s_bvalid;")
tb = tb.replace("reg  s_bready;", "reg  [14:0] s_bready;")
tb = tb.replace("wire s_bresp;", "wire [29:0] s_bresp;")
tb = tb.replace("wire s_bid;", "wire [59:0] s_bid;")

with open("interconnect/interconnect_mpu/tb_interconnect_mpu.v", "w") as f:
    f.write(tb)

import re

with open("interconnect/qos_controller/tb_qos_controller.v", "r") as f:
    tb = f.read()

tb = tb.replace("logic cfg_base_qos;", "logic [3:0] cfg_base_qos [0:14];")
tb = tb.replace("logic cfg_boost_qos;", "logic [3:0] cfg_boost_qos [0:14];")
tb = tb.replace("logic cfg_bw_limit;", "logic [15:0] cfg_bw_limit [0:14];")
tb = tb.replace("logic cfg_time_win;", "logic [15:0] cfg_time_win;")
tb = tb.replace("logic m_arvalid;", "logic [14:0] m_arvalid;")
tb = tb.replace("logic m_arready;", "logic [14:0] m_arready;")
tb = tb.replace("logic m_awvalid;", "logic [14:0] m_awvalid;")
tb = tb.replace("logic m_awready;", "logic [14:0] m_awready;")
tb = tb.replace("logic m_arqos;", "logic [3:0] m_arqos [0:14];")
tb = tb.replace("logic m_awqos;", "logic [3:0] m_awqos [0:14];")

# Fix assignments
tb = re.sub(r'cfg_base_qos = \$random;', 'for(int i=0; i<15; i++) cfg_base_qos[i] = $random;', tb)
tb = re.sub(r'cfg_boost_qos = \$random;', 'for(int i=0; i<15; i++) cfg_boost_qos[i] = $random;', tb)
tb = re.sub(r'cfg_bw_limit = \$random;', 'for(int i=0; i<15; i++) cfg_bw_limit[i] = $random;', tb)

tb = tb.replace("cfg_base_qos = 0;", "for(int i=0; i<15; i++) cfg_base_qos[i] = 0;")
tb = tb.replace("cfg_boost_qos = 0;", "for(int i=0; i<15; i++) cfg_boost_qos[i] = 0;")
tb = tb.replace("cfg_bw_limit = 0;", "for(int i=0; i<15; i++) cfg_bw_limit[i] = 0;")

with open("interconnect/qos_controller/tb_qos_controller.v", "w") as f:
    f.write(tb)

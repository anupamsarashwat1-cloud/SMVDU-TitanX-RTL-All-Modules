import re

with open("peripherals/pcie_pipe_if/tb_pcie_pipe_if.v", "r") as f:
    tb = f.read()

tb = tb.replace("logic tx_data;", "logic [63:0] tx_data;")
tb = tb.replace("logic tx_datak;", "logic [7:0] tx_datak;")
tb = tb.replace("logic rx_data;", "logic [63:0] rx_data;")
tb = tb.replace("logic rx_datak;", "logic [7:0] rx_datak;")
tb = tb.replace("logic rx_valid;", "logic [3:0] rx_valid;")
tb = tb.replace("logic rx_elecidle;", "logic [3:0] rx_elecidle;")
tb = tb.replace("logic rx_status;", "logic [11:0] rx_status;")
tb = tb.replace("logic tx_rate;", "logic [1:0] tx_rate;")
tb = tb.replace("logic power_down;", "logic [1:0] power_down [0:3];")
tb = tb.replace("logic tx_elecidle;", "logic [3:0] tx_elecidle;")
tb = tb.replace("logic tx_compliance;", "logic [3:0] tx_compliance;")
tb = tb.replace("logic rx_polarity;", "logic [3:0] rx_polarity;")
tb = tb.replace("logic pipe_tx_data;", "logic [63:0] pipe_tx_data;")
tb = tb.replace("logic pipe_tx_datak;", "logic [7:0] pipe_tx_datak;")
tb = tb.replace("logic pipe_rx_data;", "logic [63:0] pipe_rx_data;")
tb = tb.replace("logic pipe_rx_datak;", "logic [7:0] pipe_rx_datak;")
tb = tb.replace("logic pipe_tx_rate;", "logic [1:0] pipe_tx_rate;")
tb = tb.replace("logic pipe_tx_elecidle;", "logic [3:0] pipe_tx_elecidle;")
tb = tb.replace("logic pipe_tx_compliance;", "logic [3:0] pipe_tx_compliance;")
tb = tb.replace("logic pipe_rx_polarity;", "logic [3:0] pipe_rx_polarity;")
tb = tb.replace("logic pipe_power_down;", "logic [7:0] pipe_power_down;")
tb = tb.replace("logic pipe_rx_valid;", "logic [3:0] pipe_rx_valid;")
tb = tb.replace("logic pipe_rx_elecidle;", "logic [3:0] pipe_rx_elecidle;")
tb = tb.replace("logic pipe_rx_status;", "logic [11:0] pipe_rx_status;")
tb = tb.replace("logic pipe_phy_status;", "logic [3:0] pipe_phy_status;")

# Also need to fix the randomization of the unpacked array
tb = tb.replace("power_down = $random;", "power_down[0] = $random; power_down[1] = $random; power_down[2] = $random; power_down[3] = $random;")
tb = tb.replace("power_down = 0;", "power_down[0] = 0; power_down[1] = 0; power_down[2] = 0; power_down[3] = 0;")

with open("peripherals/pcie_pipe_if/tb_pcie_pipe_if.v", "w") as f:
    f.write(tb)

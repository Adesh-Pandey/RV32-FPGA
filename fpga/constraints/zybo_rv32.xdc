## Zybo (original, pre-2017) — RV32 SoC pin constraints
set_property SEVERITY {Warning} [get_drc_checks ZPS7-1]
## 125 MHz system clock
set_property -dict { PACKAGE_PIN L16  IOSTANDARD LVCMOS33 } [get_ports clk]
create_clock -add -name sys_clk_pin -period 8.00 -waveform {0 4} [get_ports clk]

## Reset button (BTN0, active-high)
set_property -dict { PACKAGE_PIN R18  IOSTANDARD LVCMOS33 } [get_ports btn_reset]

## LEDs LD0..LD3
set_property -dict { PACKAGE_PIN M14  IOSTANDARD LVCMOS33 } [get_ports {led[0]}]
set_property -dict { PACKAGE_PIN M15  IOSTANDARD LVCMOS33 } [get_ports {led[1]}]
set_property -dict { PACKAGE_PIN G14  IOSTANDARD LVCMOS33 } [get_ports {led[2]}]
set_property -dict { PACKAGE_PIN D18  IOSTANDARD LVCMOS33 } [get_ports {led[3]}]

## PMOD JB GPIO (5 external LEDs, software-driven via MMIO @ 0x100)
set_property -dict { PACKAGE_PIN T20  IOSTANDARD LVCMOS33 } [get_ports {gpio[0]}]
set_property -dict { PACKAGE_PIN U20  IOSTANDARD LVCMOS33 } [get_ports {gpio[1]}]
set_property -dict { PACKAGE_PIN V20  IOSTANDARD LVCMOS33 } [get_ports {gpio[2]}]
set_property -dict { PACKAGE_PIN W20  IOSTANDARD LVCMOS33 } [get_ports {gpio[3]}]
set_property -dict { PACKAGE_PIN Y18  IOSTANDARD LVCMOS33 } [get_ports {gpio[4]}]

## PMOD JE (Top Row) - BASED ON YOUR EXACT PINOUT
## J15 connects to Module Pin 3 (TXD). The module transmits, the FPGA receives.
set_property -dict { PACKAGE_PIN J15   IOSTANDARD LVCMOS33 } [get_ports uart_rx_pin]

## W16 connects to Module Pin 2 (RXD). The module receives, the FPGA transmits.
set_property -dict { PACKAGE_PIN W16   IOSTANDARD LVCMOS33 } [get_ports uart_tx_pin]

# Use the SKY130 typical-corner Liberty library for technology mapping.
set lib $::env(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib

# Read the complete RTL source hierarchy.
yosys read_verilog rtl/full_adder.v rtl/mult_array.v
# Flatten the hierarchy and synthesize the top-level multiplier.
yosys synth -top mult_array -flatten
# Replace generic flip-flops with SKY130 flip-flop cells.
yosys dfflibmap -liberty $lib
# Map combinational logic to SKY130 standard cells.
yosys abc -liberty $lib
# Remove unused cells and wires after mapping.
yosys opt_clean -purge
# Save cell counts and area information for Part B.
yosys tee -o synth/mult_array_stat.rpt stat -liberty $lib
# Write the mapped gate-level Verilog netlist.
yosys write_verilog -noattr synth/mult_array_netlist.v

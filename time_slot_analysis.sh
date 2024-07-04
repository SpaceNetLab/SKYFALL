#! /bin/bash  
# Main information
echo "Analyzing malicious terminal deployment for each time slot..."
echo ""

cd skyfall || exit 1
total_timeslots=$1
cpu_cores=$2
throughput_degradation=$3
seq 0 $total_timeslots | xargs -n 1 -P $cpu_cores -I{} bash -c "sudo python3 time_slot_analysis_grid.py {} $throughput_degradation; sudo python3 time_slot_analysis_circle.py {} $throughput_degradation"
seq 0 $total_timeslots | xargs -n 1 -P $cpu_cores -I{} bash -c "sudo python3 time_slot_analysis_grid_comparison.py {} $throughput_degradation; sudo python3 time_slot_analysis_circle_comparison.py {} $throughput_degradation"
cd .. || exit 1

# Calculation finished
echo "Analysis finished!"
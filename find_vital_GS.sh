#! /bin/bash  
# Main information
echo "Calculating vital GS..."
echo ""

cd skyfall || exit 1
total_timeslots=$1
cpu_cores=$2
seq 0 $total_timeslots | xargs -n 1 -P $cpu_cores -I{} bash -c "sudo python3 bottleneck_GS_rank.py {}"
cd .. || exit 1

# Calculation finished
echo "Vital GS calculation finished!"
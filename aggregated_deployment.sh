#! /bin/bash  
# Main information
echo "Analyzing aggregated deployment for the attack period..."
echo ""

cd skyfall || exit 1
total_timeslots=$1
throughput_degradation=$2
bash -c "sudo python3 aggregated_deployment_grid.py $total_timeslots $throughput_degradation & sudo python3 aggregated_deployment_circle.py $total_timeslots $throughput_degradation"
cd .. || exit 1

# Calculation finished
echo "Analysis finished!"
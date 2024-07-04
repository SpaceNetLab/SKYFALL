#! /bin/bash  
# Main information
echo "Analyzing experimental results..."
echo ""

cd skyfall || exit 1
bash -c "sudo python3 get_results.py"
cd .. || exit 1

# Calculation finished
echo "Analysis finished!"
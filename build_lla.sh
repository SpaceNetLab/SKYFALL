# Main information
echo "LLA: build"
echo ""
echo "It is highly recommend you use a recent Linux operating system (e.g., Ubuntu 20 or higher)."
echo "Python version 3.6+ is required."
echo ""

# Calculating
echo "Calculating LLA..."
cd skyfall || exit 1
sudo python3 generate_lla.py $1 || exit 1
cd .. || exit 1

# Calculation finished
echo "LLA calculation finished!"

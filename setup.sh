#!/bin/bash

# Step 1: Update system packages
echo "Updating system packages..."
sudo apt-get update -y

# Step 2: Install Mosquitto and Mosquitto clients
echo "Installing Mosquitto and its clients..."
sudo apt-get install -y mosquitto mosquitto-clients

# Step 3: Enable Mosquitto to start on boot
echo "Enabling Mosquitto service to start on boot..."
sudo systemctl enable mosquitto

# Step 4: Configure Mosquitto to listen on port 1883
# Create the Mosquitto config file if it doesn't exist
MOSQUITTO_CONFIG_FILE="/etc/mosquitto/mosquitto.conf"
if [ -f "$MOSQUITTO_CONFIG_FILE" ]; then
    echo "Mosquitto config file already exists."
else
    echo "Creating Mosquitto config file..."
    sudo touch $MOSQUITTO_CONFIG_FILE
fi

# Add configuration to listen on port 1883
echo "Configuring Mosquitto to listen on port 1883..."
sudo bash -c 'echo "listener 1883" >> /etc/mosquitto/mosquitto.conf'

# Step 5: Restart Mosquitto service to apply changes
echo "Restarting Mosquitto service..."
sudo systemctl restart mosquitto

# Step 6: Check if Mosquitto is running and listening on port 1883
echo "Verifying that Mosquitto is running and listening on port 1883..."
sudo netstat -tuln | grep 1883

echo "Mosquitto setup is complete."

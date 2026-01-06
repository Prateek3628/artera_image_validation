#!/bin/bash

# AWS Deployment Script for Image Validator Streamlit App
# This script sets up and deploys the application on an AWS EC2 instance

echo "======================================"
echo "Image Validator - AWS Deployment"
echo "======================================"

# Update system packages
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Python 3 and pip if not already installed
echo "Installing Python and pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Install Node.js and npm (required for PM2)
echo "Installing Node.js and npm..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2 globally
echo "Installing PM2..."
sudo npm install -g pm2

# Install system dependencies for OpenCV
echo "Installing OpenCV dependencies..."
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Create logs directory
echo "Creating logs directory..."
mkdir -p logs

# Configure PM2 to start on system boot
echo "Configuring PM2 startup..."
pm2 startup systemd -u $USER --hp $HOME

# Start the application with PM2
echo "Starting application with PM2..."
pm2 start ecosystem.config.json

# Save PM2 configuration
echo "Saving PM2 configuration..."
pm2 save

# Configure firewall (if UFW is installed)
if command -v ufw &> /dev/null; then
    echo "Configuring firewall..."
    sudo ufw allow 8501/tcp
    sudo ufw allow 22/tcp
    sudo ufw --force enable
fi

# Display PM2 status
echo ""
echo "======================================"
echo "Deployment Complete!"
echo "======================================"
pm2 status
echo ""
echo "Application is running on port 8501"
echo "Access it at: http://YOUR_AWS_PUBLIC_IP:8501"
echo ""
echo "Important AWS Security Group Configuration:"
echo "- Add Inbound rule: Custom TCP, Port 8501, Source: 0.0.0.0/0 (or your IP)"
echo "- Add Inbound rule: SSH, Port 22, Source: Your IP"
echo ""
echo "Useful PM2 commands:"
echo "  pm2 status          - Check application status"
echo "  pm2 logs            - View application logs"
echo "  pm2 restart all     - Restart application"
echo "  pm2 stop all        - Stop application"
echo "  pm2 monit           - Monitor resources"
echo ""

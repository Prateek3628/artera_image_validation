# Image Validator - AWS Deployment Guide

## Prerequisites

1. **AWS EC2 Instance**
   - Ubuntu 20.04 or later recommended
   - At least t2.small (1GB RAM minimum)
   - Python 3.10+ installed

2. **Security Group Configuration**
   - SSH (Port 22) - for your IP
   - HTTP (Port 8501) - for Streamlit app access

## Deployment Steps

### 1. Connect to Your EC2 Instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### 2. Upload Project Files

From your local machine:

```bash
# Create a tarball of the project
cd /Users/mac/Documents/artera/artera_image_validation
tar -czf image-validator.tar.gz *

# Upload to EC2
scp -i your-key.pem image-validator.tar.gz ubuntu@your-ec2-public-ip:~/

# Or use rsync
rsync -avz -e "ssh -i your-key.pem" \
  --exclude 'temp_*' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  . ubuntu@your-ec2-public-ip:~/image-validator/
```

### 3. Run Deployment Script on EC2

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@your-ec2-public-ip

# Extract files (if using tar)
tar -xzf image-validator.tar.gz -C ~/image-validator/
cd ~/image-validator

# Make deployment script executable
chmod +x deploy.sh

# Run deployment script
./deploy.sh
```

### 4. Start the Application with PM2

```bash
# Start the app
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Check status
pm2 status

# View logs
pm2 logs image-validator
```

### 5. Access Your Application

Open your browser and navigate to:
```
http://YOUR_EC2_PUBLIC_IP:8501
```

## PM2 Commands

```bash
# Start the app
pm2 start ecosystem.config.js

# Stop the app
pm2 stop image-validator

# Restart the app
pm2 restart image-validator

# View logs
pm2 logs image-validator

# Monitor resources
pm2 monit

# List all apps
pm2 list

# Delete app from PM2
pm2 delete image-validator

# Save current PM2 configuration
pm2 save

# Resurrect saved processes after reboot
pm2 resurrect
```

## AWS Security Group Setup

1. Go to EC2 Console → Security Groups
2. Select your instance's security group
3. Add Inbound Rules:
   - **Type**: Custom TCP
   - **Port**: 8501
   - **Source**: Your IP or 0.0.0.0/0 (for public access)

## Manual Installation (Alternative)

If you prefer manual setup:

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-pip nodejs npm

# Install Python packages
pip3 install -r requirements.txt

# Install PM2
sudo npm install -g pm2

# Start app
pm2 start ecosystem.config.js
pm2 save
```

## Using Custom Domain (Optional)

### With Nginx Reverse Proxy

1. **Install Nginx**:
```bash
sudo apt-get install -y nginx
```

2. **Configure Nginx**:
```bash
sudo nano /etc/nginx/sites-available/image-validator
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

3. **Enable site**:
```bash
sudo ln -s /etc/nginx/sites-available/image-validator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **Update Security Group**: Allow port 80 (HTTP)

## SSL Certificate (Optional)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

## Troubleshooting

### Check if app is running:
```bash
pm2 status
pm2 logs image-validator
```

### Check port availability:
```bash
sudo netstat -tulpn | grep 8501
```

### Restart services:
```bash
pm2 restart image-validator
```

### Check Python packages:
```bash
pip3 list | grep -E "streamlit|opencv|numpy"
```

### View system resources:
```bash
free -h
df -h
pm2 monit
```

## Cost Optimization

- Use **t3.micro** or **t3.small** for development
- Use **t3.medium** for production (better performance)
- Consider using AWS Lambda + API Gateway for serverless option
- Set up CloudWatch alarms for resource monitoring

## Backup and Updates

```bash
# Pull latest changes
cd ~/image-validator
git pull origin main  # if using git

# Restart app
pm2 restart image-validator
```

## Environment Variables (Optional)

Create `.streamlit/config.toml` for custom configuration:

```bash
mkdir -p .streamlit
nano .streamlit/config.toml
```

Add:
```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true
maxUploadSize = 200

[theme]
primaryColor = "#F63366"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

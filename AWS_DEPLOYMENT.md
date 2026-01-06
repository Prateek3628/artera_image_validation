# AWS Deployment Guide for Image Validator

## Prerequisites

1. **AWS EC2 Instance**
   - Ubuntu 20.04 or 22.04 LTS
   - At least t2.small (1GB RAM minimum, t2.medium recommended)
   - Security Group configured (see below)

2. **Security Group Configuration**
   - Inbound Rules:
     - SSH: Port 22, Source: Your IP
     - Custom TCP: Port 8501, Source: 0.0.0.0/0 (or restrict to your IP range)

## Deployment Steps

### 1. Connect to Your EC2 Instance

```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP
```

### 2. Upload Project Files to EC2

From your local machine:

```bash
# Using SCP
scp -i your-key.pem -r /Users/mac/Documents/artera/artera_image_validation ubuntu@YOUR_EC2_PUBLIC_IP:~/

# Or using rsync (recommended)
rsync -avz -e "ssh -i your-key.pem" \
  --exclude 'temp_*' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  /Users/mac/Documents/artera/artera_image_validation/ \
  ubuntu@YOUR_EC2_PUBLIC_IP:~/artera_image_validation/
```

### 3. Run Deployment Script

On the EC2 instance:

```bash
cd ~/artera_image_validation
chmod +x deploy.sh
./deploy.sh
```

This script will:
- Install Python, Node.js, and PM2
- Install OpenCV system dependencies
- Install Python packages from requirements.txt
- Configure PM2 to start on boot
- Start the Streamlit app
- Configure the firewall

### 4. Verify Deployment

```bash
# Check PM2 status
pm2 status

# View application logs
pm2 logs image-validator

# Monitor resources
pm2 monit
```

### 5. Access Your Application

Open your browser and navigate to:
```
http://YOUR_EC2_PUBLIC_IP:8501
```

## PM2 Management Commands

```bash
# View status
pm2 status

# View logs
pm2 logs image-validator

# Restart application
pm2 restart image-validator

# Stop application
pm2 stop image-validator

# Start application
pm2 start ecosystem.config.json

# Monitor resources
pm2 monit

# Save current PM2 configuration
pm2 save
```

## Using a Custom Domain (Optional)

### Option 1: Nginx Reverse Proxy

1. Install Nginx:
```bash
sudo apt-get install -y nginx
```

2. Create Nginx configuration:
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
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
```

3. Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/image-validator /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. Update Security Group to allow port 80

### Option 2: SSL with Let's Encrypt (HTTPS)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

## Troubleshooting

### Application not starting:
```bash
pm2 logs image-validator
pm2 restart image-validator
```

### Port 8501 not accessible:
- Check AWS Security Group rules
- Check EC2 firewall: `sudo ufw status`
- Verify app is running: `pm2 status`

### OpenCV errors:
```bash
# Reinstall system dependencies
sudo apt-get install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev
pip3 install --force-reinstall opencv-python
pm2 restart image-validator
```

### Out of memory:
- Upgrade to larger instance (t2.medium or higher)
- Add swap space:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## Updating the Application

```bash
# Pull latest changes
cd ~/artera_image_validation
git pull  # if using git

# Or upload new files via SCP/rsync

# Restart PM2
pm2 restart image-validator
```

## Monitoring and Logs

```bash
# Real-time logs
pm2 logs image-validator --lines 100

# Error logs only
pm2 logs image-validator --err

# Save logs to file
pm2 logs image-validator > logs/app.log
```

## Backup Configuration

```bash
# Backup PM2 config
pm2 save

# View saved config
cat ~/.pm2/dump.pm2
```

## Cost Optimization

- Use t2.micro for testing (free tier eligible)
- Use t2.small or t2.medium for production
- Consider using AWS Lightsail for simpler pricing
- Set up CloudWatch alarms for cost monitoring

# Quick Start Commands for AWS Deployment

## On Your Local Machine

### 1. Upload files to EC2
```bash
# Replace YOUR_KEY.pem and YOUR_EC2_IP with your actual values
rsync -avz -e "ssh -i YOUR_KEY.pem" \
  --exclude 'temp_*' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  /Users/mac/Documents/artera/artera_image_validation/ \
  ubuntu@YOUR_EC2_IP:~/artera_image_validation/
```

## On EC2 Instance

### 2. Connect to EC2
```bash
ssh -i YOUR_KEY.pem ubuntu@YOUR_EC2_IP
```

### 3. Deploy
```bash
cd ~/artera_image_validation
chmod +x deploy.sh
./deploy.sh
```

### 4. Access App
```
http://YOUR_EC2_IP:8501
```

## PM2 Commands (on EC2)

```bash
# Status
pm2 status

# Logs
pm2 logs image-validator

# Restart
pm2 restart image-validator

# Stop
pm2 stop image-validator

# Start
pm2 start ecosystem.config.json

# Monitor
pm2 monit
```

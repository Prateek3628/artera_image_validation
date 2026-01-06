# Image Validation App - Files Overview

## Core Application Files

- **`image_validation.py`** - Main validation module with face detection and blur detection functions
- **`app.py`** - Streamlit web application
- **`test_validation.py`** - Command-line test script
- **`requirements.txt`** - Python dependencies

## AWS Deployment Files

- **`ecosystem.config.json`** - PM2 configuration for running Streamlit
- **`deploy.sh`** - Automated deployment script for AWS EC2
- **`.streamlit/config.toml`** - Streamlit server configuration for production

## Documentation

- **`AWS_DEPLOYMENT.md`** - Complete deployment guide with troubleshooting
- **`QUICKSTART.md`** - Quick reference commands for deployment

## Project Structure

```
artera_image_validation/
├── image_validation.py      # Core validation logic
├── app.py                    # Streamlit web interface
├── test_validation.py        # CLI test script
├── requirements.txt          # Dependencies
├── ecosystem.config.json     # PM2 configuration
├── deploy.sh                 # Deployment script
├── .streamlit/
│   └── config.toml          # Streamlit config
├── AWS_DEPLOYMENT.md         # Full deployment guide
└── QUICKSTART.md             # Quick reference
```

## How It Works

1. **Local Development**: Run `streamlit run app.py` for testing
2. **AWS Deployment**: Upload to EC2, run `deploy.sh`, access via public IP
3. **PM2 Management**: Use PM2 commands to manage the application
4. **Production Ready**: Configured for headless mode, auto-restart, and persistent running

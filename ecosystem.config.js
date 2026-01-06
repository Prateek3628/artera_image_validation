module.exports = {
  apps: [{
    name: 'image-validator',
    script: 'streamlit',
    args: 'run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true',
    interpreter: 'none',
    env: {
      NODE_ENV: 'production'
    },
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};

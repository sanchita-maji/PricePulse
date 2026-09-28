# PricePulse – Public Hosting & Deployment Guide

This document outlines how to deploy PricePulse to public cloud platforms. The application is built with **Streamlit** (Python 3.10+) and Plotly.

---

## 1. Quick Deploy Options

### Option A: Streamlit Community Cloud (Recommended & Free)
1. Push this repository to **GitHub**.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and log in with GitHub.
3. Click **"New app"**.
4. Configure:
   - **Repository**: `your-username/your-repo-name`
   - **Branch**: `main` (or your active branch)
   - **Main file path**: `frontend/app.py` (or `app.py`)
5. Click **"Deploy!"**.
   *Note: Dependencies from `requirements.txt` and `.streamlit/config.toml` are detected automatically.*

---

### Option B: Render (Web Service)
1. Push this repository to GitHub/GitLab.
2. Sign in to [Render.com](https://render.com/) and click **"New +" -> "Web Service"**.
3. Connect your repository.
4. Set the following settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run frontend/app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`
5. Under **Advanced / Environment Variables**, add:
   - `PYTHON_VERSION`: `3.11.9`
   - `STREAMLIT_SERVER_HEADLESS`: `true`
   - `STREAMLIT_BROWSER_GATHER_USAGE_STATS`: `false`
6. Click **"Create Web Service"**.

*(Alternatively, use the included `render.yaml` blueprint via "New Blueprint Instance".)*

---

### Option C: Railway
1. Go to [Railway.app](https://railway.app/) and create a new project.
2. Select **"Deploy from GitHub repo"**.
3. Railway automatically detects `Procfile` and `requirements.txt`.
4. Ensure `PORT` is passed by Railway (default behavior).
5. Generate a public domain under **Settings -> Networking -> Generate Domain**.

---

### Option D: Docker / Container Platforms (GCP Cloud Run, AWS ECS / App Runner, Fly.io)

#### Build Container Locally:
```bash
docker build -t pricepulse:latest .
```

#### Run Container Locally:
```bash
docker run -p 8501:8501 -e PORT=8501 -e STREAMLIT_SERVER_ADDRESS=0.0.0.0 pricepulse:latest
```

#### Or Run with Docker Compose:
```bash
docker-compose up --build
```

#### Deploy to Google Cloud Run:
```bash
gcloud run deploy pricepulse \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501
```

---

### Option E: Linux VPS (Ubuntu / Debian with systemd & Nginx)

1. **Clone & Install Dependencies**:
   ```bash
   git clone <repo-url> /opt/pricepulse
   cd /opt/pricepulse
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create systemd Service** (`/etc/systemd/system/pricepulse.service`):
   ```ini
   [Unit]
   Description=PricePulse Streamlit Web Application
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/opt/pricepulse
   Environment="PATH=/opt/pricepulse/.venv/bin"
   Environment="PORT=8501"
   Environment="HOST=127.0.0.1"
   ExecStart=/opt/pricepulse/.venv/bin/streamlit run frontend/app.py --server.port=8501 --server.address=127.0.0.1 --server.headless=true
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and Start Service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable pricepulse
   sudo systemctl start pricepulse
   ```

4. **Nginx Reverse Proxy & WebSocket Configuration** (`/etc/nginx/sites-available/pricepulse`):
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8501;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
           proxy_read_timeout 86400;
       }
   }
   ```

---

## 2. Environment Variables Reference

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `PORT` | `8501` | Port on which the production web server listens (supplied by cloud providers). |
| `HOST` / `STREAMLIT_SERVER_ADDRESS` | `0.0.0.0` | Bind IP address (`0.0.0.0` allows external public traffic into containers/proxies). |
| `STREAMLIT_SERVER_HEADLESS` | `true` | Runs server without attempting to open local desktop browser windows. |
| `STREAMLIT_SERVER_ENABLE_CORS` | `false` | Disables CORS restrictions so reverse proxies and custom domains connect cleanly. |
| `STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION` | `true` | Protects endpoints against cross-site request forgery. |
| `STREAMLIT_BROWSER_GATHER_USAGE_STATS` | `false` | Disables telemetry for faster boot and data privacy. |
| `DATABASE_PATH` | *(Auto-resolved)* | Optional custom path to SQLite DB (e.g. `/tmp/amazon_analyzer.db` for read-only containers). |
| `APP_ENV` | `production` | Deployment mode flag (`production` or `development`). |

---

## 3. Database & First-Run Seeding

- On public deployments where SQLite files are not committed to Git, the application automatically initializes database tables and seeds a rich 15-product sample catalog with multi-day historical price points upon the first launch.
- If an existing database is mounted or preserved, existing records are retained completely untouched.

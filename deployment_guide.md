# Synora AI - Production Deployment Guide

This guide details how to deploy **Synora AI** to production environments. Since the project is structured with a FastAPI backend and a Streamlit frontend, you have several flexible options to choose from.

---

## ⚡ 100% Free-Tier Deployment Stack ($0/Month)

You can host your database, backend API, and frontend dashboard completely for free using this premium stack:

### Step 1: Create a Free PostgreSQL Database
Because free hosting providers (like Render) have ephemeral disks (they reset files on container restarts), we should not use SQLite in production. Instead, create a free cloud PostgreSQL database:
1. Sign up for a free account on **[Neon.tech](https://neon.tech)** or **[Supabase](https://supabase.com)**.
2. Create a new project and copy your connection URI, which looks like this:
   `postgresql://alex:password@ep-cool-snowflake-123456.us-east-2.aws.neon.tech/neondb?sslmode=require`
   *(Keep this connection string private).*

### Step 2: Deploy Backend API on Render (Free Tier)
1. Sign up on **[Render](https://render.com)** and click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Configure the Web Service:
   - **Name**: `synora-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Docker` (Render auto-detects `Dockerfile.backend`)
   - **Region**: Choose the closest to your database (e.g., US East)
   - **Instance Type**: **Free**
4. Add the following **Environment Variables** under the "Advanced" menu:
   - `DATABASE_URL` = (Your Neon/Supabase PostgreSQL connection string from Step 1)
   - `SECRET_KEY` = (A random password string to sign user logins)
   - `GEMINI_API_KEY` = (Your Google Gemini key)
5. Click **Deploy Web Service** and copy the generated link once active (e.g. `https://synora-backend.onrender.com`).

### Step 3: Deploy Frontend on Streamlit Community Cloud (Free & Instant)
Streamlit hosts Streamlit apps directly from GitHub with 0 seconds spin-up delay and unlimited usage:
1. Log in to **[Streamlit Community Cloud](https://share.streamlit.io)** using your GitHub account.
2. Click **New app**.
3. Select your repository, branch, and set the main file path to: `frontend/app.py`.
4. Click **Advanced settings** (gear icon) before deploying and add the backend URL as an environment variable:
   ```toml
   BACKEND_URL = "https://synora-backend.onrender.com"
   ```
5. Click **Deploy!** Your Synora AI portal is now globally accessible.

---

## Environment Variables Checklist

Before deploying, ensure you configure the following variables in your cloud provider dashboard or `.env` file:

| Variable | Description | Recommended Production Value |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API credentials | Your private API Key (allows fallback if missing) |
| `SECRET_KEY` | JWT signing secret key | A long, random cryptographic string |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./research_assistant.db` (for SQLite) or `postgresql://...` |
| `BACKEND_URL` | Address of your FastAPI endpoint | The public domain of your deployed Backend API |

---

## Option A: Deploying on a VPS (AWS EC2, DigitalOcean, etc.) using Docker Compose

This is the most cost-effective and robust option for hosting both backend and frontend together with persistent storage.

### 1. Prerequisites
Ensure Docker and Docker Compose are installed on your server:
```bash
sudo apt update
sudo apt install docker.io docker-compose -y
```

### 2. Copy Code & Launch
Clone or copy your project folder to the server and run:
```bash
# Start containers in detached mode (background)
docker-compose up -d --build
```

### 3. Verify Container Status
```bash
docker-compose ps
```
Your backend will be accessible on port `8000` and your Streamlit frontend on port `8501`.

---

## Option B: Deploying on Railway (Recommended PaaS)

Railway is excellent for Python monorepos and automatically deploys services from Dockerfiles.

### Step 1: Deploy Backend
1. Create a **New Project** on Railway.
2. Select **GitHub** and connect your repository.
3. In settings, set the **Root Directory** to `backend` and set the **Dockerfile** path to `Dockerfile.backend` (or let Railway auto-detect it).
4. Add the following **Environment Variables**:
   - `PORT=8000`
   - `SECRET_KEY=your_cryptographic_secret`
   - `GEMINI_API_KEY=your_gemini_key`
5. Generate a **Public Reference Domain** under Settings (e.g., `https://synora-backend.up.railway.app`).

### Step 2: Deploy Frontend
1. Add a new service from your GitHub repo.
2. Set the **Root Directory** to `frontend` and the **Dockerfile** path to `Dockerfile.frontend`.
3. Configure **Environment Variables**:
   - `PORT=8501`
   - `BACKEND_URL=https://synora-backend.up.railway.app` (pointing to your backend URL generated in Step 1)
4. Generate a **Public Domain** for the frontend (e.g., `https://synora.up.railway.app`).
5. Open your frontend link in the browser!

---

## Option C: Deploying on Render

Render offers a free tier for Web Services and handles Python applications cleanly.

### Step 1: Deploy Backend Web Service
1. In Render Dashboard, click **New +** and select **Web Service**.
2. Connect your GitHub repository.
3. Set the following settings:
   - **Name**: `synora-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Docker` (Render will automatically detect `Dockerfile.backend`)
4. In **Advanced**, add your environment variables (`SECRET_KEY`, `GEMINI_API_KEY`).
5. Click **Deploy Web Service** and copy the generated URL (e.g., `https://synora-backend.onrender.com`).

### Step 2: Deploy Frontend Web Service
1. Click **New +** and select **Web Service**.
2. Connect your repository.
3. Configure the settings:
   - **Name**: `synora-frontend`
   - **Root Directory**: `frontend`
   - **Environment**: `Docker` (detects `Dockerfile.frontend`)
4. In **Advanced**, add the environment variable:
   - `BACKEND_URL=https://synora-backend.onrender.com`
5. Click **Deploy Web Service** and open your Streamlit app once building completes!

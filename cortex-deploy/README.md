# Cortex Brain — Docker / Fly.io Deployment

Split hemisphere AI brain (Left=angel, Right=demon, Cortex=synthesis).
65,987+ nodes, Hebbian learning, HTTP API on port 8643.

## Structure

```
cortex-deploy/
├── Dockerfile          # Python 3.11-slim image
├── fly.toml            # Fly.io config (lhr region, 1GB RAM, 3GB volume)
├── entrypoint.sh       # Symlinks persistent volume into src/
├── .gitlab-ci.yml      # Auto-deploy on push to main
└── src/
    ├── online_server.py
    ├── brain.py
    ├── cortex_brain.py
    └── ... (all modules)
```

## Deploy to Fly.io

### First time
```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Create app + volume
flyctl apps create cortex-brain-sf
flyctl volumes create cortex_brain_data --region lhr --size 3

# Deploy
flyctl deploy
```

### Seed brain data (upload existing hemispheres)
```bash
# Copy brain.json files to the volume via SSH
flyctl ssh console -C "mkdir -p /app/data/left /app/data/right /app/data/cortex"
# Then use: flyctl sftp shell to upload brain.json files
```

### CI/CD (auto-deploy via GitLab)
Set `FLY_API_TOKEN` in GitLab CI/CD variables (Settings → CI/CD → Variables).
Every push to `main` triggers a redeploy.

## API Endpoints

```
POST /alive/studio/api/brain-live    — brain stats
POST /alive/studio/api/chat-cortex  — chat with the brain
GET  /health                         — health check
```

## Environment Variables

| Variable | Description |
|---|---|
| `PORT` | HTTP port (default 8643) |
| `FLY_API_TOKEN` | Fly.io deploy token (CI only) |

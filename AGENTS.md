# Workflow

- **PRO**: `/home/ruth/pinyator` — port 5000, volume `data`.
- **DEV**: `/home/ruth/pinyator-dev` — port 5001, volume `data_dev`.
- **GitHub**: `git@github.com:iwanttobefreak/pinyator.git`

## Com desplegar de DEV a PRO

1. A DEV: `git push origin dev`
2. A GitHub: PR `dev` → `main`, merge
3. A PRO:
   ```bash
   git pull origin main
   git checkout docker-compose.yml --ours
   git add docker-compose.yml && git commit -m "Keep PRO config"
   docker compose down -v && docker compose build && docker compose up -d
   ```

# Workflow

- **PRO**: `/home/ruth/pinyator` — port 5000, volume `data`.
- **DEV**: `/home/ruth/pinyator-dev` — port 5001, volume `data_dev`.
- **GitHub**: `git@github.com:iwanttobefreak/pinyator.git` — branca `main` (PRO) i `dev` (DEV)

## How to work

1. Work in DEV (`/home/ruth/pinyator-dev`).
2. Test on http://localhost:5001.
3. When changes are ready, commit and push to GitHub:
   ```bash
   cd /home/ruth/pinyator-dev
   git add -A
   git commit -m "Descripció dels canvis"
   git push origin dev
   ```
4. A GitHub: crear Pull Request de `dev` → `main`, fer merge.
5. Fer pull a PRO:
   ```bash
   cd /home/ruth/pinyator
   git pull origin main
   git checkout docker-compose.yml --ours
   git add docker-compose.yml && git commit -m "Keep PRO config"
   ```
6. Restart PRO:
   ```bash
   cd /home/ruth/pinyator
   docker compose down -v && docker compose build && docker compose up -d
   ```
7. Test on http://localhost:5000.

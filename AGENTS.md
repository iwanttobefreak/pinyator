# Workflow

- **PRO**: `/home/ruth/pinyator` — port 5000, volume `data`.
- **DEV**: `/home/ruth/pinyator-dev` — port 5001, volume `data_dev`.

## How to work

1. Work in DEV (`/home/ruth/pinyator-dev`).
2. Test on http://localhost:5001.
3. When changes are ready, push to PRO:
   ```bash
   cd /home/ruth/pinyator-dev
   git push pro HEAD:main
   cd /home/ruth/pinyator
   git checkout docker-compose.yml --ours
   git add docker-compose.yml && git commit -m "Keep PRO config"
   ```
4. Restart PRO:
   ```bash
   cd /home/ruth/pinyator
   docker compose down -v && docker compose build && docker compose up -d
   ```
5. Test on http://localhost:5000.

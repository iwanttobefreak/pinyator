# Pinyator — guía de desarrollo

Aplicación Flask para la gestión de una colla castellera.

## Entornos

| Entorno | URL | Base de datos |
|---|---|---|
| Desarrollo local | `http://127.0.0.1:5050` | SQLite en volumen Docker |
| Staging | pendiente | pendiente |
| Producción | gestionada por infraestructura | no accesible desde este repo |

**Este repo es solo de desarrollo.** El despliegue a producción lo gestiona infraestructura.

## Stack

- Flask 3 + Flask-Login + Flask-SQLAlchemy
- SQLite (un solo escritor; `busy_timeout` configurado)
- Gunicorn en producción (1 worker, 4 hilos)
- Docker + Docker Compose

## Configuración

Copia `.env.example` a `.env` y rellena los valores. **`.env` no se versiona**; `.env.example` sí.

| Variable | Uso |
|---|---|
| `FLASK_ENV` | `development` o `production` |
| `PYTHONUNBUFFERED` | logs sin buffer |
| `SECRET_KEY` | firma de sesiones; genera una aleatoria |
| `DATABASE_URL` | cadena de conexión SQLAlchemy |

No subas al repo `.env`, bases de datos, copias de seguridad ni datos personales.

## Comandos

```bash
# Levantar dev (solo accesible en 127.0.0.1:5050)
# El proyecto se llama pinyator-dev para no colisionar con producción
docker compose -f compose.dev.yaml up --build

# Parar dev
docker compose -f compose.dev.yaml down

# Shell dentro del contenedor
docker compose -f compose.dev.yaml run --rm web bash

# Tests (cuando existan)
docker compose -f compose.dev.yaml run --rm web pytest -q

# Lint (cuando esté ruff)
docker compose -f compose.dev.yaml run --rm web ruff check .
```

## Flujo de trabajo

1. Rama `feature/<tema>` desde `dev`.
2. Cambio pequeño + tests.
3. PR a `dev`; CI en verde.
4. Despliegue a staging y prueba manual.
5. PR `dev` → `main`.
6. Infraestructura: backup de SQLite, build, despliegue a producción y verificación.

## Reglas

- **No tocar producción** desde este repo.
- **Nunca** `docker compose down -v` sobre producción. En dev, solo con `compose.dev.yaml`.
- **Secretos fuera del repo**: `.env` está ignorado; usa `.env.example` con placeholders.
- No hagas `commit` ni `push` sin que te lo pidan.
- Si un cambio requiere migración de BD, prepara el script y el backup; el despliegue lo ejecuta infraestructura.
- No introduzcas credenciales por defecto ni contraseñas predecibles.

## Deuda técnica prioritaria

1. **Seguridad**: política de contraseñas, CSRF, rate limiting en `/login`, cookies `Secure`/`HttpOnly` y bloqueo por intentos.
2. **Migraciones**: `create_app()` ejecuta `db.create_all()` y `seed_all()` en cada arranque. Migrar a Flask-Migrate/Alembic y seeds idempotentes por CLI.
3. **Tests y CI**: no hay tests ni GitHub Actions. Añadir pytest, `ruff` y build de imagen en CI.
4. **Backup**: automatizar `sqlite3 .backup` diario a almacenamiento externo y probar la restauración.
5. **Observabilidad**: sonda de Prometheus/blackbox y alerta de caída.

## Problemas conocidos

- `run.py` arranca con `debug=True`; en producción se usa gunicorn. No usar ese entrypoint en producción.
- El primer arranque del entorno dev tarda varios minutos porque `seed_all()` crea los usuarios de ejemplo; los siguientes usan el volumen ya sembrado.
- El `AGENTS.md` anterior tenía un conflicto de merge y un `docker compose down -v`; este fichero lo sustituye.
- `plantilles/` está ignorado en git y se copia a mano; no contiene secretos.
- Los datos de usuarios no deben versionarse; usa seeds privados.

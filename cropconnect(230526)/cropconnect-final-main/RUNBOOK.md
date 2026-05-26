# CropConnect Operations Runbook

## Checking if everything is healthy
- Backend: GET https://cropconnect01-production.up.railway.app/api/health
  Expected: {"status":"ok","db":"ok"}
- Frontend: https://cropconnect01.vercel.app — page loads, hero visible
- UptimeRobot dashboard: all monitors green
- Sentry: no new unresolved issues in last 24h

## Deploying a new version

Backend (Railway):
  git push origin main
  Railway auto-deploys from main. Watch the deploy log in Railway dashboard.
  Migration runs automatically: python migrate_db.py runs before uvicorn starts.
  Health check: Railway pings /api/health after deploy. If it fails, Railway
  rolls back automatically (healthcheckTimeout is 30s per railway.json).

Frontend (Vercel):
  git push origin main
  Vercel auto-deploys from main. Watch the deploy log in Vercel dashboard.
  SPAs: vercel.json rewrites all routes to /index.html — React Router handles routing.

## Rolling back a bad deploy

Backend rollback in Railway:
  Railway dashboard → Deployments → click the last good deploy → Redeploy

Frontend rollback in Vercel:
  Vercel dashboard → Deployments → find the last good deploy → Promote to Production

## If the database is unreachable
1. Check /api/health — if db: "error", the pool is failing
2. Railway dashboard → MySQL service → check it is running
3. Check MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD env vars in Railway
4. Check Railway MySQL service logs for OOM or connection errors
5. If pool exhausted: restart the backend service in Railway dashboard

## If users cannot log in
1. Check browser network tab — is /api/auth/login returning 200 or an error?
2. Check CORS: browser console should not show blocked origin errors
3. Check FRONTEND_ORIGINS in Railway env — must match the exact Vercel production URL
4. Check AUTH_COOKIE_SECURE=true and AUTH_COOKIE_SAMESITE=none in Railway env
5. Check Sentry for auth-related errors in the last hour

## If the ESP32 stops sending data
1. Check the SIM800L signal on the physical device
2. Manually hit: GET https://cropconnect01-production.up.railway.app/api/esp32/relay-command
   with the device's API key — if 200, backend is reachable
3. Check Railway logs for /api/telemetry/ingest — are packets arriving?
4. Verify the device's API key is still valid in the database

## Running a database backup manually
ssh into Railway or run locally with prod env vars:
  bash cropconnect-backend/scripts/backup_db.sh
Backup is saved to /backups/cropconnect_YYYYMMDD_HHMMSS.sql.gz
Verify with: ls -lh /backups/

## Restoring from a backup
  gunzip < /backups/cropconnect_YYYYMMDD_HHMMSS.sql.gz | \
    mysql -h $MYSQL_HOST -P $MYSQL_PORT -u $MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE
WARNING: This overwrites all data. Always back up current state first.

## Key environment variables reference

Backend (set in Railway):
  CROP_DATA_SECRET_KEY        — encrypts PII fields in DB (never change after launch)
  CROP_AUTH_TOKEN_SECRET      — signs auth tokens (rotate only if compromised)
  MYSQL_HOST / PORT / USER / PASSWORD / DATABASE
  FRONTEND_ORIGINS            — comma-separated list of trusted frontend URLs
  TRUST_PROXY_HEADERS         — must be true on Railway
  SENTRY_DSN                  — backend error reporting
  GEMINI_API_KEY              — AI crop advice feature
  DATA_GOV_API_KEY            — live mandi market prices

Frontend (set in Vercel):
  VITE_BACKEND_URL            — full backend URL including /api suffix
  VITE_SENTRY_DSN             — frontend error reporting
  VITE_PUBLIC_TRANSLATION_ENABLED — enables AI whole-site translation

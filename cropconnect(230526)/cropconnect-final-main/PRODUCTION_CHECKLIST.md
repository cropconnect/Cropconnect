# CropConnect Production Checklist

## Secrets

- [ ] CROP_DATA_SECRET_KEY is a fresh randomly generated 32+ character string
- [ ] CROP_AUTH_TOKEN_SECRET is a fresh randomly generated 32+ character string
- [ ] ESP32_API_KEY rotated from any development value
- [ ] ALLOW_GLOBAL_ESP32_API_KEY=false confirmed in production env
- [ ] Run: grep -r "replace-with" . — result must be empty

## Security

- [ ] AUTH_COOKIE_SECURE=true in production env
- [ ] AUTH_COOKIE_SAMESITE=none and backend is behind HTTPS
- [ ] FRONTEND_ORIGINS contains only the production Vercel URL — no localhost

## Infrastructure

- [ ] TRUST_PROXY_HEADERS=true set in Railway environment
- [ ] GET /health endpoint responds 200 with {"status":"ok","db":"ok"}
- [ ] UptimeRobot or Betterstack monitor pointed at /health, alerting via email
- [ ] MySQL automated backup tested: backup created, restore verified

## Observability

- [ ] SENTRY_DSN configured in Railway env
- [ ] Sentry alert rule: email on every new issue
- [ ] Sentry alert rule: notify on error spike (>10 errors in 5 minutes)

## Final checks

- [ ] Load the production URL and complete a full login → dashboard → pump toggle flow
- [ ] Confirm sensor data appears or empty state renders correctly
- [ ] Check browser console — zero errors on load

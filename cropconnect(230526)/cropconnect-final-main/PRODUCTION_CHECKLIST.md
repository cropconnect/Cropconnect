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

## Setting up Sentry alerts

1. Go to your Sentry project → Alerts → Create Alert Rule
2. Rule 1 — "New issue": trigger on "A new issue is created" → notify via email
3. Rule 2 — "Error spike": trigger when "Number of errors > 10 in 5 minutes" → notify via email or Slack
4. Confirm SENTRY_DSN is set in Railway: Settings → Variables → SENTRY_DSN

## Setting up uptime monitoring (UptimeRobot — free)

1. Create account at uptimerobot.com
2. Add monitor: HTTP(S), URL = https://your-backend.railway.app/api/health
3. Check interval: every 5 minutes
4. Alert contacts: your email
5. Expected keyword: "ok" (validates DB is responding, not just HTTP 200)
6. A healthy response looks like: {"status":"ok","db":"ok"}

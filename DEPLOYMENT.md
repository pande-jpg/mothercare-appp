# MotherCare deployment guide

## 1. Codespaces checks

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py migrate
```

## 2. Commit and push

```bash
git add .
git commit -m "MotherCare staff dashboard and production admin bootstrap"
git pull --rebase origin main
git push origin main
```

## 3. Render environment variables

Keep the existing `DATABASE_URL`, `SECRET_KEY`, and `DEBUG=False` values.

For the one-time production admin bootstrap, add:

- `CREATE_ADMIN_ON_DEPLOY` = `true`
- `ADMIN_USERNAME` = your full login email
- `ADMIN_EMAIL` = your full login email
- `ADMIN_PASSWORD` = a new strong password (never put it in GitHub)

After a successful deploy, change `CREATE_ADMIN_ON_DEPLOY` to `false` and remove the three `ADMIN_*` variables if you no longer need them.

## 4. URLs

- Customer app: `/`
- Staff dashboard: `/staff/` or `/operations/`
- Django admin: `/admin/`
- Provider dashboard: `/provider/`

The staff dashboard is protected by Django `is_staff` access.

## 5. Real-world integrations still require provider credentials

Payment gateway, ambulance/hospital dispatch, SMS, email, WhatsApp, and maps integrations require their own production accounts/API credentials. The project does not fake those integrations.

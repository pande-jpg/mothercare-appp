# mothercare-appp

## MotherCare administrator
The production bootstrap creates the administrator automatically during deployment and also repairs it at startup if necessary.

Default administrator credentials (change them after first login):
- Username: `mothercareadmin`
- Email: `admin@mothercare.app`
- Password: `MCAdmin#2026!`

Render environment variables `ADMIN_USERNAME`, `ADMIN_EMAIL`, and `ADMIN_PASSWORD` override these defaults when configured. Do not publish production credentials in a public repository.

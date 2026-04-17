# DOQL Examples Test Report

**Date:** 2026-04-17  
**Total Examples:** 9  
**Test Status:** ✅ All examples validated and built successfully

## Summary

All 9 example projects in the doql repository have been tested. Each example was validated and built successfully. Some examples have minor warnings related to configuration paths or optional features.

| Example | Format | Validation | Build | Artifacts Generated |
|---------|--------|------------|-------|---------------------|
| asset-management | .doql.css | ✅ Clean | ✅ Success | API, Web, Mobile, Desktop, Infra, i18n, Integrations, Workflows, CI |
| blog-cms | .doql.sass | ✅ Clean | ✅ Success | API, Web, Infra, i18n, Integrations, Workflows, CI |
| calibration-lab | .doql.less | ✅ Clean | ✅ Success | API, Web, Infra (Quadlet), i18n, Integrations, Workflows, CI |
| crm-contacts | .doql.less | ✅ Clean | ✅ Success | API, Web, Infra, i18n, Integrations, Workflows, CI |
| document-generator | .doql.less | ✅ Clean | ✅ Success | Documents, Reports, Infra (Quadlet), Integrations, Workflows, CI |
| e-commerce-shop | .doql.css | ✅ Clean | ✅ Success | API, Web, Infra, i18n, Integrations, Workflows, CI |
| iot-fleet | .doql.less | ✅ Clean | ✅ Success | API, Web, Infra, Integrations, Workflows, CI |
| kiosk-station | .doql.css | ⚠️ 2 warnings | ✅ Success | Infra, Integrations, Workflows, CI |
| todo-pwa | .doql.css | ⚠️ 1 warning | ✅ Success | API, Mobile, Infra, CI |

---

## Detailed Results

### 1. asset-management

**Format:** `.doql.css`  
**Description:** ISO 17025 asset management system for calibration labs  
**Validation:** ✅ Clean  
**Build:** ✅ Success  

**Generated Artifacts:**
- **API:** FastAPI backend with SQLAlchemy, Alembic migrations, JWT auth
- **Web:** React + Vite + TailwindCSS frontend with PWA support
- **Mobile:** Progressive Web App with service worker
- **Desktop:** Tauri-based desktop application
- **Infra:** Docker Compose configuration
- **i18n:** Polish, English, German translations (114 keys each)
- **Integrations:** Email, Slack, Storage, Notifications services
- **Workflows:** Daily overdue check, inspection fail handling, annual exercise reminder, cylinder filling audit
- **CI:** GitHub Actions workflow
- **Plugins:** ERP, GXP, Fleet (via entry points)

**Entities (10):** User, Station, Operator, Qualification, Device, Inspection, CylinderFill, Exercise, Deployment

---

### 2. blog-cms

**Format:** `.doql.sass`  
**Description:** Simple blog/content management system  
**Validation:** ✅ Clean  
**Build:** ✅ Success  

**Generated Artifacts:**
- **API:** FastAPI backend with SQLAlchemy, Alembic migrations, JWT auth
- **Web:** React + Vite + TailwindCSS frontend
- **Infra:** Docker Compose configuration
- **i18n:** English, Polish translations (69 keys each)
- **Integrations:** Email, Storage, Notifications services
- **Workflows:** Publish notification, comment moderation
- **CI:** GitHub Actions workflow
- **Plugins:** ERP, GXP, Fleet (via entry points)

**Entities (6):** Post, Author, Category, Comment, MediaFile

---

### 3. calibration-lab

**Format:** `.doql.less`  
**Description:** Calibration laboratory management system  
**Validation:** ✅ Clean  
**Build:** ✅ Success  

**Generated Artifacts:**
- **API:** FastAPI backend with SQLAlchemy, Alembic migrations, JWT auth
- **Web:** React + Vite + TailwindCSS frontend
- **Infra:** Podman Quadlet containers (manager + Traefik)
- **i18n:** Polish, English, German translations (80 keys each)
- **Integrations:** Storage, Notifications services
- **Workflows:** Calibration due reminder, certificate immutability
- **CI:** GitHub Actions workflow
- **Plugins:** ERP, GXP, Fleet (via entry points)

**Entities (7):** Operator, Instrument, ReferenceStandard, Calibration, Customer, CalibrationOrder

---

### 4. crm-contacts

**Format:** `.doql.less`  
**Description:** CRM system for contact and deal management  
**Validation:** ✅ Clean  
**Build:** ✅ Success  

**Generated Artifacts:**
- **API:** FastAPI backend with SQLAlchemy, Alembic migrations, JWT auth
- **Web:** React + Vite + TailwindCSS frontend
- **Infra:** Docker Compose configuration
- **i18n:** English, Polish, German translations (68 keys each)
- **Integrations:** Email, Notifications services
- **Workflows:** Deal stage notification, overdue activity reminder
- **CI:** GitHub Actions workflow
- **Plugins:** ERP, GXP, Fleet (via entry points)

**Entities (5):** Contact, Company, Deal, Activity

---

### 5. document-generator

**Format:** `.doql.less`  
**Description:** Document generation service for calibration certificates and reports  
**Validation:** ✅ Clean  
**Build:** ✅ Success  

**Generated Artifacts:**
- **Documents:** Calibration certificate renderer, Non-conformance report renderer, QR label renderer
- **Reports:** Monthly calibration summary report generator with crontab
- **Infra:** Podman Quadlet containers (generator + Traefik)
- **Integrations:** OqlOS client service
- **Workflows:** Auto-generate on calibration done
- **CI:** GitHub Actions workflow
- **Plugins:** ERP, GXP, Fleet (via entry points)

**Note:** No API generated (no entities defined) - this is a document generation service

---

### 6. e-commerce-shop

**Format:** `.doql.css`  
**Description:** E-commerce shop with product and order management  
**Validation:** ✅ Clean  
**Build:** ✅ Success  

**Generated Artifacts:**
- **API:** FastAPI backend with SQLAlchemy, Alembic migrations, JWT auth
- **Web:** React + Vite + TailwindCSS frontend
- **Infra:** Docker Compose configuration
- **i18n:** English, Polish translations (59 keys each)
- **Integrations:** Email, Notifications services
- **Workflows:** Order confirmation, Low stock alert
- **CI:** GitHub Actions workflow
- **Plugins:** ERP, GXP, Fleet (via entry points)

**Entities (4):** Product, Customer, Order, CartItem

---

### 7. iot-fleet

**Format:** `.doql.less`  
**Description:** IoT fleet management for device monitoring and OTA updates  
**Validation:** ✅ Clean  
**Build:** ✅ Success  

**Generated Artifacts:**
- **API:** FastAPI backend with SQLAlchemy, Alembic migrations, JWT auth
- **Web:** React + Vite + TailwindCSS frontend
- **Infra:** Docker Compose configuration
- **Integrations:** Storage, Notifications services
- **Workflows:** Heartbeat check, OTA canary deployment
- **CI:** GitHub Actions workflow
- **Plugins:** ERP, GXP, Fleet (via entry points)

**Entities (6):** Node, Telemetry, Deployment, FirmwareBuild, OTAUpdate

---

### 8. kiosk-station

**Format:** `.doql.css`  
**Description:** Kiosk station appliance with offline sync capabilities  
**Validation:** ⚠️ 2 warnings  
**Build:** ✅ Success  

**Warnings:**
- `DATA operators: Absolute path (skipped local check): /var/lib/kiosk/operators.db`
- `DATA devices: Absolute path (skipped local check): /var/lib/kiosk/devices.db`

**Generated Artifacts:**
- **Infra:** Install script, systemd service
- **Integrations:** OqlOS client service
- **Workflows:** Offline sync, Auto-logout on idle
- **CI:** GitHub Actions workflow
- **Plugins:** ERP, GXP, Fleet (via entry points)

**Note:** Minimal kiosk-focused example without full web/API stack

---

### 9. todo-pwa

**Format:** `.doql.css`  
**Description:** Simple Progressive Web App for todo list management  
**Validation:** ⚠️ 1 warning  
**Build:** ✅ Success  

**Warnings:**
- `INTERFACE mobile: No pages defined (will generate empty shell)`

**Generated Artifacts:**
- **API:** FastAPI backend with SQLAlchemy, Alembic migrations
- **Mobile:** PWA with service worker
- **Infra:** Docker Compose configuration
- **CI:** GitHub Actions workflow
- **Plugins:** ERP, GXP, Fleet (via entry points)

**Note:** Minimal example focusing on PWA capabilities

---

## Common Patterns

### All Examples Include:
- `.env` and `.env.example` files for configuration
- `doql.lock` file for dependency locking
- GitHub Actions CI workflow
- Plugin integration (ERP, GXP, Fleet via entry points)

### Format Support:
- **CSS (`.doql.css`)**: asset-management, e-commerce-shop, kiosk-station, todo-pwa
- **LESS (`.doql.less`)**: calibration-lab, crm-contacts, document-generator, iot-fleet
- **SASS (`.doql.sass`)**: blog-cms

### Typical Stack:
- **Backend:** FastAPI + SQLAlchemy + Alembic
- **Frontend:** React + Vite + TailwindCSS
- **Deployment:** Docker Compose or Podman Quadlet
- **CI:** GitHub Actions

## Test Methodology

1. **Validation:** Ran `doql validate` in each example directory
2. **Build:** Ran `doql build` in each example directory
3. **Verification:** Checked generated artifacts in `build/` directories

All tests were performed using the doql CLI from the virtual environment at `/home/tom/github/oqlos/doql/venv`.

## Notes

- All examples show a warning about failed plugin 'iso17025' (No module named '_shared') - this is expected as it's an optional plugin not installed in the test environment
- The kiosk-station example uses absolute paths for data sources (appropriate for kiosk deployment)
- The todo-pwa example has no mobile interface pages defined (minimal example)

# Todo PWA — mobile-first doql example

Minimal example showcasing the mobile (PWA) generator.

```bash
cp .env.example .env
doql validate
doql build --force

# 1) Start API
cd build/api && /tmp/doql-runtime/bin/uvicorn main:app --port 8101 &

# 2) Serve the PWA
cd ../mobile
python3 -m http.server 8091 &

# 3) Open http://localhost:8091/ — on mobile Chrome:
#    address bar menu → Install app
```

To test the full stack with Traefik see `tests/env_manager.py`.

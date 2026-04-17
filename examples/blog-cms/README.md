# Blog CMS

DOQL example — blog/CMS with posts, categories, comments, media management.

## Features

- Post management with draft/review/publish workflow
- Category hierarchy with nested categories
- Comment system with moderation
- Media file upload with S3 storage
- Email notifications for new posts and comments
- PWA-enabled React frontend
- Role-based access (admin, editor, writer, public)

## Formats

- `app.doql` — classic DOQL format
- `app.doql.sass` — SASS indented format with $variables

## Quick Start

```bash
doql validate
doql build --force
doql run
```

# Knowledge Stack - Quick Start Guide

## Initial Setup (First Time Only)

```bash
# 1. Run the setup wizard
./setup.sh

# 2. Access your services
# Silverbullet: http://localhost:3000
# Paperless: http://localhost:8000

# 3. Start using!
```

That's it! The setup wizard handles everything.

---

## Daily Operations

### Start/Stop Services

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose stop

# Restart all services
docker compose restart

# Stop and remove containers (keeps data)
docker compose down
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f paperless-ngx
docker compose logs -f silverbullet

# Last 100 lines
docker compose logs --tail=100
```

### Check Status

```bash
# Container status
docker compose ps

# Resource usage
docker stats

# Disk usage
docker system df
du -sh data/
```

---

## Adding Documents to Paperless

### Method 1: Web Upload
1. Go to http://localhost:8000
2. Click "Upload" button
3. Drag and drop or select files

### Method 2: Consume Folder (Recommended)
```bash
# Copy PDFs to consume folder
cp ~/Downloads/*.pdf data/paperless/consume/

# Paperless auto-processes every 60 seconds
# Check logs: docker compose logs -f paperless-ngx
```

### Method 3: Organize by Subdirectories
```bash
# Create subdirectories for auto-tagging
mkdir -p data/paperless/consume/Research
mkdir -p data/paperless/consume/Invoices
mkdir -p data/paperless/consume/Personal

# Copy files
cp research-paper.pdf data/paperless/consume/Research/
# Paperless will auto-add "Research" tag
```

---

## Working with Silverbullet

### Creating Notes

1. Open http://localhost:3000
2. Press `Ctrl+N` (or `Cmd+N` on Mac) for new page
3. Type your note in Markdown
4. Save with `Ctrl+S` (auto-saves anyway)

### Wiki Links

```markdown
Link to other notes: [[Another Note]]
Link with custom text: [[Another Note|see this]]
Link to headings: [[Note#Section]]
```

### Templates

Create a template page:
```markdown
---
template: meeting-notes
---
# Meeting: {{title}}
Date: {{date}}

## Attendees
-

## Agenda
-

## Notes
{{cursor}}

## Action Items
- [ ]
```

Use template:
```markdown
---
use-template: meeting-notes
title: Weekly Standup
date: 2026-01-16
---
```

---

## Backups

### Create Backup

```bash
# Run backup script
./backup.sh

# Backup saved to: backups/YYYYMMDD-HHMMSS/
```

### Restore Backup

```bash
# List backups and restore
./restore.sh

# Or specify backup directly
./restore.sh 20260116-020000
```

### Automated Backups

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/knowledge-stack && ./backup.sh
```

---

## Searching

### Paperless Search

```bash
# Full-text search
transformer attention

# By tag
tag:machine-learning

# By date
created:2025

# Combined
tag:research transformer created:2025
```

### Silverbullet Search

- Press `/` to open search
- Type query
- Use arrow keys to navigate results
- Press `Enter` to open

---

## Linking Silverbullet and Paperless

### Reference Paperless Documents in Notes

```markdown
---
paperless_id: 123
type: research-note
---

# Attention is All You Need

**PDF:** [View in Paperless](http://localhost:8000/documents/123)

## Summary
...

## Key Points
...
```

### Organize Research

```
silverbullet/space/
├── Research/
│   ├── Machine Learning/
│   │   ├── Transformers.md
│   │   └── Attention Mechanisms.md
│   └── Papers/
│       ├── Attention is All You Need.md  (links to Paperless ID 123)
│       └── BERT.md                        (links to Paperless ID 124)
└── Index.md
```

---

## Maintenance

### Update Containers

```bash
# Pull latest images
docker compose pull

# Recreate containers with new images
docker compose up -d

# Remove old images
docker image prune -a
```

### Clean Up

```bash
# Remove unused Docker resources
docker system prune -a

# Clean old backups (older than 30 days)
find backups/ -type d -mtime +30 -delete
```

### Database Maintenance

```bash
# Optimize PostgreSQL
docker compose exec paperless-db vacuumdb -U paperless -d paperless -z
```

---

## Troubleshooting

### Service Not Responding

```bash
# Check logs
docker compose logs -f SERVICE_NAME

# Restart specific service
docker compose restart SERVICE_NAME

# Restart all services
docker compose restart
```

### Paperless Not Processing Documents

```bash
# Check consume folder
ls -la data/paperless/consume/

# Check logs
docker compose logs -f paperless-ngx

# Manually trigger consumption
docker compose exec paperless-ngx document_consumer
```

### Out of Disk Space

```bash
# Check space
df -h
du -sh data/*

# Clean Docker
docker system prune -a --volumes

# Archive old backups
tar -czf backups-archive.tar.gz backups/
rm -rf backups/old-backups/
```

### Permission Issues

```bash
# Fix Silverbullet permissions
sudo chown -R 1000:1000 data/silverbullet/

# Fix Paperless permissions
sudo chown -R 1000:1000 data/paperless/
```

### Reset Everything

```bash
# Stop and remove all containers
docker compose down

# Remove all data (WARNING: deletes everything!)
rm -rf data/

# Start fresh
./setup.sh
```

---

## Common Tasks

### Add OCR Language

```bash
# Edit .env
PAPERLESS_OCR_LANGUAGE=eng+fra+deu

# Restart Paperless
docker compose restart paperless-ngx
```

### Change Admin Password

```bash
# Paperless UI: Settings → Users → Edit admin user

# Or via command line:
docker compose exec paperless-ngx python manage.py changepassword admin
```

### Export All Data from Paperless

```bash
# Via UI: Settings → Export

# Or manually:
docker compose exec paperless-ngx document_exporter /usr/src/paperless/export
```

### Rebuild Search Index

```bash
docker compose exec paperless-ngx document_index reindex
```

---

## Performance Optimization

### Low on RAM? Reduce Workers

Edit `.env`:
```bash
PAPERLESS_WEBSERVER_WORKERS=1
PAPERLESS_TASK_WORKERS=1
```

Then restart:
```bash
docker compose restart paperless-ngx
```

### Disable Tika/Gotenberg (PDF Only Mode)

Comment out in `docker-compose.yml`:
```yaml
# gotenberg:
#   ...
# tika:
#   ...
```

Edit `.env`:
```bash
PAPERLESS_TIKA_ENABLED=0
```

Restart:
```bash
docker compose up -d
```

---

## Useful URLs

- **Silverbullet**: http://localhost:3000
- **Paperless**: http://localhost:8000
- **Paperless API**: http://localhost:8000/api/docs/

## Keyboard Shortcuts

### Silverbullet
- `Ctrl/Cmd + N`: New page
- `Ctrl/Cmd + S`: Save
- `Ctrl/Cmd + K`: Command palette
- `/`: Search
- `[[`: Create wiki link

### Paperless
- `?`: Show shortcuts
- `c`: Create document
- `/`: Focus search
- `Ctrl + K`: Command palette

---

## Getting Help

- **Full Documentation**: [README.md](README.md)
- **Research Document**: [../Docs/KNOWLEDGE-MANAGEMENT-STACK-RESEARCH.md](../Docs/KNOWLEDGE-MANAGEMENT-STACK-RESEARCH.md)
- **Silverbullet Docs**: https://silverbullet.md
- **Paperless Docs**: https://docs.paperless-ngx.com

---

**Last Updated:** January 16, 2026

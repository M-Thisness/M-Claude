# Knowledge Management Stack

A comprehensive, self-hosted knowledge management and digital gardening stack combining:
- **Silverbullet**: Personal knowledge management and note-taking
- **Paperless-ngx**: Document management with OCR and full-text search
- Supporting services: PostgreSQL, Redis, Gotenberg, Apache Tika

## Quick Start

### Prerequisites

- Docker Engine 20.10+
- Docker Compose v2.0+
- 16GB RAM (minimum 8GB)
- 4+ CPU cores
- 500GB storage (recommended)

### Installation

1. **Clone or download this directory**

```bash
cd /path/to/knowledge-stack
```

2. **Create environment file**

```bash
cp .env.template .env
```

3. **Edit `.env` and update:**
   - `PAPERLESS_SECRET_KEY` - Generate with: `openssl rand -base64 32`
   - `PAPERLESS_DBPASS` - Strong database password
   - `PAPERLESS_ADMIN_PASSWORD` - Admin user password
   - `PAPERLESS_ADMIN_MAIL` - Your email address
   - `TZ` - Your timezone

4. **Create data directories**

```bash
mkdir -p data/silverbullet/space
mkdir -p data/paperless/{data,media,export,consume,pgdata,redis}
mkdir -p backups
```

5. **Start the stack**

```bash
docker compose up -d
```

6. **Check status**

```bash
docker compose ps
docker compose logs -f
```

## Access

- **Silverbullet**: http://localhost:3000
- **Paperless-ngx**: http://localhost:8000

### First Login

**Silverbullet:**
- Username: From `SB_USER` (default: admin)
- Password: Set via `SB_PASSWORD` or prompted on first access

**Paperless-ngx:**
- Username: From `PAPERLESS_ADMIN_USER` (default: admin)
- Password: From `PAPERLESS_ADMIN_PASSWORD`

## Usage

### Silverbullet

**Creating Notes:**
1. Open http://localhost:3000
2. Click "New Page" or press `Ctrl/Cmd + N`
3. Write in Markdown
4. Save with `Ctrl/Cmd + S`

**Wiki-style Linking:**
```markdown
# My Research Note

Related: [[Another Note]]
See also: [[Concepts/Machine Learning]]
```

**Templates:**
Create a page named `template/research-paper`:
```markdown
---
template: research-paper
---
# {{title}}

## Citation
**Authors:** {{authors}}
**Year:** {{year}}
**DOI:** {{doi}}

## Abstract
{{abstract}}

## Key Points
-

## Notes
{{cursor}}

## Related Papers
-
```

Use it: Create new page, add frontmatter:
```markdown
---
use-template: research-paper
title: Attention is All You Need
authors: Vaswani et al.
year: 2017
---
```

### Paperless-ngx

**Adding Documents:**

**Method 1: Web Upload**
1. Go to http://localhost:8000
2. Click "Upload" button
3. Select files or drag-and-drop

**Method 2: Consume Folder**
```bash
# Copy files to consume directory
cp ~/Downloads/*.pdf /path/to/knowledge-stack/data/paperless/consume/

# Paperless auto-processes every 60 seconds
```

**Method 3: Email Import** (requires additional setup)

**Organizing Documents:**
1. **Tags**: Add tags manually or let ML suggest
2. **Correspondents**: Track document authors/sources
3. **Document Types**: Categorize (invoice, paper, article, etc.)
4. **Custom Fields**: Add metadata (DOI, ISBN, etc.)

**Searching:**
- Full-text search: `transformer attention mechanism`
- By tag: `tag:machine-learning`
- By correspondent: `correspondent:"IEEE"`
- By date: `created:[2020 to 2025]`
- Combined: `tag:nlp transformer created:2023`

**Advanced OCR:**
Configure in Settings → OCR:
- Add additional languages
- Adjust OCR mode (skip/redo/force)
- Enable/disable image preprocessing

### Linking Silverbullet and Paperless

**Best Practice:**

In Silverbullet, reference Paperless documents:
```markdown
---
paperless_id: 123
paperless_url: http://localhost:8000/documents/123
tags: [research, nlp]
---

# Attention is All You Need

**Paperless Document:** [View PDF](http://localhost:8000/documents/123)

## Summary
This paper introduces the Transformer architecture...

## Key Insights
- Self-attention mechanism
- No recurrence needed
- Parallelizable training

## Related Notes
- [[Transformers/Architecture]]
- [[NLP/Sequence Models]]
```

## Backup & Restore

### Automated Backups

**Enable PostgreSQL Backup:**
1. Uncomment `db-backup` service in `docker-compose.yml`
2. Restart: `docker compose up -d`
3. Backups saved to `./backups/postgres/`

**Manual Backup Script:**

Create `backup.sh`:
```bash
#!/bin/bash
set -e

BACKUP_DIR="./backups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Stopping containers..."
docker compose stop silverbullet paperless-ngx

echo "Backing up data..."
tar -czf "$BACKUP_DIR/silverbullet.tar.gz" data/silverbullet/
tar -czf "$BACKUP_DIR/paperless-media.tar.gz" data/paperless/media/
tar -czf "$BACKUP_DIR/paperless-data.tar.gz" data/paperless/data/

echo "Backing up database..."
docker compose start paperless-db
sleep 5
docker compose exec -T paperless-db pg_dump -U paperless paperless > "$BACKUP_DIR/paperless-db.sql"

echo "Restarting containers..."
docker compose start silverbullet paperless-ngx

echo "Backup complete: $BACKUP_DIR"
```

Make executable: `chmod +x backup.sh`

Run: `./backup.sh`

**Schedule with Cron:**
```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * cd /path/to/knowledge-stack && ./backup.sh >> ./backups/backup.log 2>&1
```

### Restore from Backup

```bash
# Stop containers
docker compose down

# Restore data
tar -xzf backups/BACKUP_DATE/silverbullet.tar.gz
tar -xzf backups/BACKUP_DATE/paperless-media.tar.gz
tar -xzf backups/BACKUP_DATE/paperless-data.tar.gz

# Start database
docker compose up -d paperless-db
sleep 10

# Restore database
docker compose exec -T paperless-db psql -U paperless paperless < backups/BACKUP_DATE/paperless-db.sql

# Start all services
docker compose up -d
```

### Off-site Backup

**Using Rclone:**

```bash
# Install rclone
curl https://rclone.org/install.sh | sudo bash

# Configure remote (e.g., Google Drive, S3)
rclone config

# Sync backups
rclone sync ./backups/ remote:knowledge-backups/
```

**Add to backup script:**
```bash
# At end of backup.sh
echo "Syncing to cloud..."
rclone sync ./backups/ gdrive:knowledge-backups/ --verbose
```

## Resource Management

### Monitor Resource Usage

```bash
# Real-time stats
docker stats

# Check specific container
docker stats paperless-ngx

# Disk usage
docker system df
du -sh data/
```

### Optimize for Limited Resources

**Reduce RAM usage:**

Edit `.env`:
```bash
PAPERLESS_WEBSERVER_WORKERS=1
PAPERLESS_TASK_WORKERS=1
```

**Disable Tika/Gotenberg (PDF only):**

Comment out in `docker-compose.yml`:
```yaml
# gotenberg:
#   ...
# tika:
#   ...
```

Set in `.env`:
```bash
PAPERLESS_TIKA_ENABLED=0
```

Restart: `docker compose up -d`

### Scale Up for Heavy Usage

Edit `docker-compose.yml`:
```yaml
paperless-ngx:
  environment:
    PAPERLESS_WEBSERVER_WORKERS: 4
    PAPERLESS_TASK_WORKERS: 4
  deploy:
    resources:
      limits:
        memory: 8G
        cpus: '4.0'
```

## Maintenance

### Update Containers

```bash
# Pull latest images
docker compose pull

# Recreate containers
docker compose up -d

# Remove old images
docker image prune -a
```

### Database Maintenance

```bash
# Optimize PostgreSQL
docker compose exec paperless-db vacuumdb -U paperless -d paperless -z -v
```

### Check Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f paperless-ngx

# Last 100 lines
docker compose logs --tail=100 silverbullet
```

### Health Checks

```bash
# Check container health
docker compose ps

# Detailed health status
docker inspect --format='{{.State.Health.Status}}' paperless-ngx
```

## Troubleshooting

### Paperless Not Processing Documents

**Check logs:**
```bash
docker compose logs -f paperless-ngx
```

**Common issues:**
- Insufficient RAM (increase `PAPERLESS_WEBSERVER_WORKERS`)
- Tika/Gotenberg not responding (check their logs)
- OCR language not installed (add to `PAPERLESS_OCR_LANGUAGE`)

**Manually trigger consumption:**
```bash
docker compose exec paperless-ngx document_consumer
```

### Silverbullet Cannot Save Files

**Check permissions:**
```bash
ls -la data/silverbullet/space/
```

**Fix ownership:**
```bash
sudo chown -R 1000:1000 data/silverbullet/
```

### Database Connection Errors

**Check database is running:**
```bash
docker compose ps paperless-db
```

**Restart database:**
```bash
docker compose restart paperless-db
```

**Check credentials in `.env`**

### High Memory Usage

**Check stats:**
```bash
docker stats
```

**Common culprits:**
- Tika (limit to 2GB)
- Gotenberg (limit to 1GB)
- Too many Paperless workers

**Restart hungry containers:**
```bash
docker compose restart tika gotenberg
```

## Security Hardening

### Use Reverse Proxy

**Install Caddy:**

Add to `docker-compose.yml`:
```yaml
caddy:
  image: caddy:2-alpine
  restart: unless-stopped
  ports:
    - "80:80"
    - "443:443"
  volumes:
    - ./Caddyfile:/etc/caddy/Caddyfile
    - caddy-data:/data
    - caddy-config:/config
  networks:
    - knowledge-stack

volumes:
  caddy-data:
  caddy-config:
```

**Create Caddyfile:**
```
notes.yourdomain.com {
    reverse_proxy silverbullet:3000
}

docs.yourdomain.com {
    reverse_proxy paperless-ngx:8000
}
```

**Remove direct port exposure:**
```yaml
silverbullet:
  ports:
    - "3000"  # Internal only

paperless-ngx:
  ports:
    - "8000"  # Internal only
```

### Enable HTTPS

Caddy handles this automatically with Let's Encrypt!

### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### VPN Access (Tailscale)

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh

# Login
sudo tailscale up

# Access via Tailscale IP
# http://100.x.y.z:3000
```

## Performance Tuning

### Enable PostgreSQL Tuning

Create `postgres-init.sql`:
```sql
-- Increase shared buffers
ALTER SYSTEM SET shared_buffers = '256MB';

-- Increase work memory
ALTER SYSTEM SET work_mem = '16MB';

-- Increase maintenance work memory
ALTER SYSTEM SET maintenance_work_mem = '128MB';

-- Enable query optimization
ALTER SYSTEM SET effective_cache_size = '1GB';
```

Mount in `docker-compose.yml`:
```yaml
paperless-db:
  volumes:
    - ./data/paperless/pgdata:/var/lib/postgresql/data
    - ./postgres-init.sql:/docker-entrypoint-initdb.d/tune.sql
```

### Optimize Paperless Search

```bash
# Rebuild search index
docker compose exec paperless-ngx document_index reindex
```

## Advanced Configuration

### Custom Paperless Classification Rules

In Paperless UI:
1. Go to Settings → Workflows
2. Create rule: "If title contains 'Invoice' → Add tag 'finance'"
3. Create rule: "If correspondent is 'University' → Add tag 'academic'"

### Silverbullet Plugs

Install plugs by creating `.silverbullet/plugs.md`:
```markdown
---
plugs:
  - https://raw.githubusercontent.com/silverbulletmd/silverbullet-mermaid/main/mermaid.plug.js
  - https://raw.githubusercontent.com/silverbulletmd/silverbullet-table/main/table.plug.js
---

# Installed Plugs
```

### API Access

**Paperless API:**
```bash
# Get API token from UI: Settings → API

# Example: List documents
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/documents/
```

**Silverbullet API:**
Silverbullet has built-in API - check docs: https://silverbullet.md

## Migration

### From Obsidian to Silverbullet

1. Export Obsidian vault
2. Copy Markdown files to `data/silverbullet/space/`
3. Fix wiki links if needed (Obsidian uses `[[note]]`, Silverbullet too!)
4. Adjust any Obsidian-specific syntax

### From Paperless-ng to Paperless-ngx

Paperless-ngx is backward compatible:
1. Export from Paperless-ng
2. Import to Paperless-ngx using admin interface
3. Or: Copy data directories directly

## Future Enhancements

### Add Anagora (When Docker Support Available)

Monitor: https://github.com/flancian/agora

When ready:
1. Add Anagora services to `docker-compose.yml`
2. Configure Agora Bridge to pull Silverbullet space
3. Share knowledge with the federated Agora network

### Add Full-Text Search Across All Services

Options:
- Meilisearch
- Elasticsearch
- Custom API gateway

### Add Citation Manager Integration

- Zotero API integration
- Auto-import citations from Paperless
- Generate bibliographies from Silverbullet notes

## Resources

- [Complete Research Guide](../Docs/KNOWLEDGE-MANAGEMENT-STACK-RESEARCH.md)
- [Silverbullet Documentation](https://silverbullet.md)
- [Paperless-ngx Documentation](https://docs.paperless-ngx.com)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

## Support

For issues:
- Silverbullet: https://github.com/silverbulletmd/silverbullet/issues
- Paperless-ngx: https://github.com/paperless-ngx/paperless-ngx/discussions

## License

This configuration is released under MIT License. Individual components have their own licenses:
- Silverbullet: MIT
- Paperless-ngx: GPLv3
- PostgreSQL: PostgreSQL License
- Redis: BSD 3-Clause

---

**Last Updated:** January 16, 2026

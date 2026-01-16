# Knowledge Management and Digital Gardening Stack Research

**Research Date:** January 16, 2026
**Purpose:** Design a comprehensive, self-hosted knowledge management stack

---

## Executive Summary

This document outlines a complete knowledge management and digital gardening stack combining:
- **Silverbullet**: Primary note-taking and knowledge base platform
- **Paperless-ngx**: Document management with OCR and full-text search
- **Anagora**: Distributed digital garden and knowledge graph (future integration)

The stack prioritizes local-first operation, data ownership, and seamless integration for academic/research workflows.

---

## 1. Anagora

### What is Anagora?

Anagora is a **distributed, goal-oriented social network** operating on a cooperatively built and maintained knowledge graph. It assembles this graph from a collection of digital gardens, wikis, and personal knowledge bases contributed by users.

**Key Characteristics:**
- **Federated Knowledge**: Aggregates notes from multiple users' digital gardens
- **Node-based Structure**: Each node represents a concept, aggregating related content from all contributors
- **Social Contract**: Users agree to share their knowledge openly
- **Current Implementation**: Live at https://anagora.org

### Current State (2025-2026)

**Active Development:**
- Main repository: https://github.com/flancian/agora
- Agora Server: https://github.com/flancian/agora-server
- Agora Bridge: https://github.com/flancian/agora-bridge

**Recent Updates (2025-2026):**
- Migrated from Poetry to `uv` for package management
- Default branch migration from `master` to `main` (September 2025)
- Recommended editor: Bull (MIT license)
- Integration with Fediverse and Bluesky for content contribution

**Architecture:**
Three main components required:
1. **Root repository**: Core Agora infrastructure
2. **Agora Server**: Python/Flask web app for content integration and serving
3. **Agora Bridge**: Content retrieval processes from user gardens

### Installation Methods

#### Native Installation (Current Method)

**Prerequisites:**
- Python 3.x
- Node.js and npm
- Poetry package manager

**Steps:**
```bash
# Clone repositories (preferably in $HOME of dedicated user)
git clone https://github.com/flancian/agora.git
git clone https://github.com/flancian/agora-server.git
git clone https://github.com/flancian/agora-bridge.git

# Setup agora-server
cd agora-server
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
npm install  # For JavaScript dependencies

# Install poetry
curl -sSL https://install.python-poetry.org | python3 -

# Setup agora-bridge
cd ../agora-bridge
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

**Running with uv:**
```bash
uv run pull.py --config ~/agora/gardens.yaml --output-dir ~/agora/garden
```

#### Docker Deployment

**Current Status:** Docker support is **not yet available** but is planned for future development. The project maintainers have indicated it would be a "great fit" and is on their roadmap.

**For Now:** Docker deployment requires community contribution or waiting for official implementation.

### Integration with Note-Taking Systems

**How It Works:**
1. User maintains their digital garden in a Git repository
2. Garden can be any format: Markdown files, wiki, blog, etc.
3. User provides garden URL to Anagora via signup@anagora.org
4. Agora Bridge pulls content periodically
5. Content is indexed and made searchable across all gardens
6. Bi-directional links connect related concepts across different users

**Hosting Options:**
- Self-host your garden on any Git platform
- Use git.anagora.org for hosted gardens (free service)

**Compatible Formats:**
- Plain Markdown files
- Foam/Obsidian-style wikis
- Jekyll/Hugo static sites
- Any Git-backed content

### Configuration Example

**gardens.yaml** (for Agora Bridge):
```yaml
gardens:
  - username: your-username
    url: https://github.com/yourusername/your-garden
    branch: main
    format: markdown

  - username: another-user
    url: https://git.anagora.org/another-user/garden
    branch: main
    format: foam
```

**Contribution Methods:**
- Git repository (traditional)
- Fediverse posts (follow designated account, use specific format)
- Bluesky posts (similar to Fediverse integration)

---

## 2. Silverbullet

### Overview

**Silverbullet** is a programmable, private, browser-based, open-source, self-hosted personal knowledge management platform. It's a clean Markdown-based writing/note-taking application that stores pages as plain Markdown files.

**Official Site:** https://silverbullet.md
**GitHub:** https://github.com/silverbulletmd/silverbullet
**Docker Image:** ghcr.io/silverbulletmd/silverbullet

### Core Features

**Local-First Architecture:**
- PWA (Progressive Web App) caches full Space in browser's IndexedDB
- Works flawlessly offline
- Automatic sync when online
- All data stored as plain Markdown files in a folder ("Space")

**Programmability:**
- Extended with Lua scripting
- Dynamic pages and queries
- Template system
- Custom commands and functions

**Knowledge Management:**
- Wiki-style linking
- Backlinks and references
- Full-text search
- Tag-based organization
- Metadata extraction

### Docker Deployment

**Simple Docker Run:**
```bash
docker run -d \
  --name silverbullet \
  -p 3000:3000 \
  -v /path/to/notes:/space \
  --restart unless-stopped \
  ghcr.io/silverbulletmd/silverbullet:v2
```

**Docker Compose Configuration:**
```yaml
services:
  silverbullet:
    image: ghcr.io/silverbulletmd/silverbullet:v2
    container_name: silverbullet
    ports:
      - "3000:3000"
    volumes:
      - ./silverbullet-data:/space
    environment:
      - SB_USER=your-username
      # Optional: set password via environment
    restart: unless-stopped
```

**Advanced Features:**
- Can deploy with Tailscale sidecar for secure access
- Can deploy with Cloudflare Tunnel sidecar for public access
- Supports authentication (basic auth)

### Plugin Ecosystem ("Plugs")

**What are Plugs?**
Plugs (short for plug-ins) extend Silverbullet's functionality. As of 2025, there are **15+ official plugs** available.

**Plugin Categories:**
1. **Data Integration**: Import/export from various formats
2. **Visualization**: Charts, diagrams, and data representation
3. **Automation**: Workflow automation and task management
4. **External Integration**: Connect to external services
5. **Syntax Extension**: Additional Markdown syntax support

**How Plugs Work:**
- Written in TypeScript/JavaScript
- Run in browser or server-side
- Can access full Silverbullet API
- Distributed as `.plug.js` files

**Installing Plugs:**
Use the `plugs:` frontmatter in any page:
```markdown
---
plugs:
  - https://raw.githubusercontent.com/silverbulletmd/plug-example/main/example.plug.js
---
```

### Extensibility

**Custom Queries:**
```markdown
<!-- #query page where type = "project" render [[template/project-list]] -->
```

**Templates:**
```markdown
---
template: daily-note
---
# {{date}}

## Tasks
- [ ] {{cursor}}

## Notes
```

**Commands:**
Create custom keyboard shortcuts and commands using Lua:
```lua
-- .silverbullet/commands.lua
function greet()
  return "Hello from Silverbullet!"
end
```

### Integration with Other Tools

**Git Integration:**
- Store Space in Git repository
- Track changes with version control
- Collaborate via Git workflows

**Sync Options:**
- Filesystem sync (Syncthing, Resilio)
- Cloud storage (if Space is in synced folder)
- Git-based sync

**Export Options:**
- Plain Markdown (native format)
- HTML export
- PDF export (via plugins)

### Resource Requirements

**Extremely Lightweight:**
- Memory: A few hundred megabytes of RAM
- CPU: Minimal - runs on Raspberry Pi (64-bit)
- Storage: Depends on your notes

**Recommended Docker Limits:**
```yaml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

---

## 3. Document Database Solutions

### Paperless-ngx (Recommended)

**Overview:**
Paperless-ngx is a community-supported supercharged document management system that transforms physical documents into a searchable online archive. It's the official successor to Paperless and Paperless-ng.

**Official Site:** https://docs.paperless-ngx.com
**GitHub:** https://github.com/paperless-ngx/paperless-ngx
**Docker Image:** ghcr.io/paperless-ngx/paperless-ngx

#### Core Features

**OCR Capabilities:**
- **Engine**: Uses OCRmyPDF with Tesseract engine
- **Languages**: Supports 100+ languages
- **Modes**:
  - **Skip**: OCR only pages without text (safest)
  - **Redo**: OCR all pages, replace existing text
  - **Force**: Rasterize and OCR everything

**Document Processing:**
- Automatic date detection (preserves original document dates)
- Machine learning for auto-tagging and classification
- Support for nested tags (up to 5 levels deep, v2.19+)
- Custom fields for additional metadata

**File Format Support:**
- PDF documents (primary)
- Images (PNG, JPEG, TIFF, GIF)
- Plain text files
- Office documents (Word, Excel, PowerPoint, LibreOffice)
  - Requires Tika and Gotenberg for Office document support

**Search Features:**
- Full-text search across all documents
- OCR-extracted text is searchable
- Results sorted by relevance
- Search highlighting
- Advanced filter options

#### Deployment

**Docker Compose (Recommended):**
```yaml
services:
  paperless-ngx:
    image: ghcr.io/paperless-ngx/paperless-ngx:latest
    container_name: paperless-ngx
    restart: unless-stopped
    depends_on:
      - db
      - broker
      - gotenberg
      - tika
    ports:
      - "8000:8000"
    volumes:
      - ./paperless/data:/usr/src/paperless/data
      - ./paperless/media:/usr/src/paperless/media
      - ./paperless/export:/usr/src/paperless/export
      - ./paperless/consume:/usr/src/paperless/consume
    environment:
      PAPERLESS_REDIS: redis://broker:6379
      PAPERLESS_DBHOST: db
      PAPERLESS_TIKA_ENABLED: 1
      PAPERLESS_TIKA_GOTENBERG_ENDPOINT: http://gotenberg:3000
      PAPERLESS_TIKA_ENDPOINT: http://tika:9998
      PAPERLESS_OCR_LANGUAGE: eng
      PAPERLESS_TIME_ZONE: America/New_York
      PAPERLESS_SECRET_KEY: change-me
      # Reduce workers to save memory
      PAPERLESS_WEBSERVER_WORKERS: 2

  db:
    image: postgres:16
    restart: unless-stopped
    volumes:
      - ./paperless/pgdata:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: paperless
      POSTGRES_USER: paperless
      POSTGRES_PASSWORD: paperless

  broker:
    image: redis:8-alpine
    restart: unless-stopped

  gotenberg:
    image: gotenberg/gotenberg:8.25
    restart: unless-stopped
    command:
      - "gotenberg"
      - "--chromium-disable-javascript=true"
      - "--chromium-allow-list=file:///tmp/.*"

  tika:
    image: apache/tika:latest
    restart: unless-stopped
```

#### Academic/Research Workflow

**Strengths for Academic Use:**
1. **OCR Excellence**: Handles scanned papers and books
2. **Metadata Extraction**: Auto-extracts authors, dates, titles
3. **Full-Text Search**: Find papers by content, not just filename
4. **Organization**: Tags, correspondents, document types
5. **API Access**: Programmatic document management
6. **Archival Quality**: Preserves original + adds OCR layer

**Workflow Example:**
1. Upload research papers to consume folder
2. Paperless auto-OCRs and indexes
3. ML suggests tags (e.g., "Machine Learning", "NLP")
4. Search across all papers: "transformer architecture attention mechanism"
5. Export citations or PDFs as needed

#### Resource Requirements

**Minimum Configuration (without Tika/Gotenberg):**
- 1GB RAM
- 2 CPU cores
- Handles PDF/image files only

**Recommended Configuration (with Tika/Gotenberg):**
- **Paperless-ngx**: 2-4GB RAM, 2 cores
- **Tika**: 1-2GB RAM (set JAVA_OPTS: -Xms512m -Xmx1024m)
- **Gotenberg**: 512MB-1GB RAM, 0.2-0.5 CPU
- **PostgreSQL**: 512MB RAM
- **Redis**: 256MB RAM
- **Total**: 6-8GB RAM, 2-4 CPU cores

**Optimization Tips:**
- Set `PAPERLESS_WEBSERVER_WORKERS=1` for memory savings
- Limit Tika heap: `mem_limit: 2g`
- Gotenberg minimum: 512MB RAM, 0.2 CPU
- Use PostgreSQL instead of SQLite for better performance

### Alternative: Docspell

**Overview:**
Docspell is a modern document management system designed for personal and small team use, excelling at organizing scanned documents, emails, and files through intelligent automation.

**Target Audience:** Home and SOHO (Small Office/Home Office) users

**Key Features:**
- Automated document ingestion from mail servers and scanners
- Machine learning for classification
- PostgreSQL-backed (easy backup)
- Simpler than Mayan EDMS
- Good for individuals/small teams

**Paperless Import:**
- Has a migration tool from Paperless
- Can import files, tags, correspondents
- Script needs updating for latest versions

**Compared to Paperless-ngx:**
- **Pros**: Simpler setup, stores docs in PostgreSQL
- **Cons**: Less polished UI, smaller community

### Alternative: Mayan EDMS

**Overview:**
Mayan EDMS is a powerful document manager built on Python and Django, designed for enterprise-level organizations needing robust, scalable, and automated document handling.

**Target Audience:** Enterprise, complex compliance environments

**Key Features:**
- Advanced workflow engine
- OCR capabilities
- Compliance and audit trails
- Role-based access control (RBAC)
- Complex automation rules

**Compared to Paperless-ngx:**
- **Pros**: More powerful workflows, enterprise features
- **Cons**: Much more complex, requires technical expertise, heavier resource usage

**Best For:** Organizations with compliance requirements, complex approval workflows

### Alternative: Teedy

**Overview:**
Teedy (formerly Sismics Docs) offers a lightweight and user-friendly approach to document management.

**Key Features:**
- OCR support
- Versioning
- Lightweight (lower system requirements)
- User-friendly interface

**Compared to Paperless-ngx:**
- **Pros**: Lighter weight, simpler
- **Cons**: Fewer features, smaller community

### Recommendation for Academic/Research Workflow

**Winner: Paperless-ngx**

**Reasons:**
1. **Best OCR**: Superior text extraction for research papers
2. **Active Community**: Large user base, frequent updates
3. **Full-Text Search**: Essential for academic research
4. **ML Auto-Tagging**: Saves time organizing papers
5. **API Access**: Integrate with other tools (Zotero, etc.)
6. **Docker Maturity**: Well-documented, stable deployments
7. **Resource Balance**: Not too heavy (Mayan) or light (Teedy)

**For Different Needs:**
- **Individuals on limited hardware**: Teedy or Docspell
- **Enterprise with compliance**: Mayan EDMS
- **Academic researchers**: Paperless-ngx

---

## 4. Zotero Integration

### Current State

**Direct Integration:** There is **no official Zotero plugin** for Paperless-ngx, Docspell, or similar document management systems as of 2026.

**Zotero as Standalone:** Zotero is best used as a complementary tool rather than an integrated component.

### Integration Strategies

#### Strategy 1: Parallel Systems
- **Zotero**: Reference management, citations, bibliography
- **Paperless-ngx**: Document storage, full-text search, OCR
- **Workflow**:
  1. Store PDFs in Paperless-ngx
  2. Reference them in Zotero
  3. Use Zotero for citation management
  4. Use Paperless for document retrieval

#### Strategy 2: Shared Storage
```
/research-library/
  ├── paperless-consume/    # Auto-import to Paperless
  ├── zotero-storage/       # Zotero attachment folder
  └── organized/            # Master storage, symlinked to both
```

#### Strategy 3: API-Based Workflow
- Use Paperless-ngx API to export metadata
- Import metadata to Zotero via Zotero API
- Maintain PDFs in Paperless, references in Zotero
- Custom script to sync (requires development)

### Recommended Workflow

**Best Approach (Hybrid):**
1. **Ingest**: Add papers to Paperless-ngx
2. **OCR & Index**: Paperless processes and makes searchable
3. **Discover**: Use Paperless full-text search to find relevant papers
4. **Cite**: Import citation data to Zotero manually or via DOI
5. **Link**: Use Paperless document ID in Zotero notes field

**Example Zotero Note:**
```
Paperless-ngx ID: 12345
Tags: machine-learning, nlp, transformers
Full-text available in Paperless
```

---

## 5. Integration Architecture

### Unified Knowledge Management Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
├─────────────────┬─────────────────┬────────────────────────┤
│  Silverbullet    │  Paperless-ngx  │  Anagora (Future)     │
│  (Port 3000)     │  (Port 8000)    │  (Port 5000)          │
│                  │                 │                        │
│  Notes & PKM     │  Documents      │  Shared Knowledge     │
│  Markdown Files  │  PDF + OCR      │  Federated Gardens    │
└─────────────────┴─────────────────┴────────────────────────┘
         │                  │                    │
         ▼                  ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    Integration Layer                         │
│  - Filesystem (shared volumes)                               │
│  - APIs (REST endpoints)                                     │
│  - Git (version control)                                     │
│  - Search Index (future: unified search)                     │
└─────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│                     Storage Layer                            │
│  - Silverbullet: /data/silverbullet/space                   │
│  - Paperless: /data/paperless/{media,data,consume}          │
│  - Anagora: /data/agora/garden                              │
│  - Database: PostgreSQL (Paperless)                         │
└─────────────────────────────────────────────────────────────┘
```

### Integration Patterns

#### Pattern 1: Document References in Notes

**Silverbullet → Paperless:**
```markdown
# Research Notes: Transformer Architecture

## Paper Reference
- Paperless Doc ID: [[paperless:12345]]
- Title: Attention is All You Need
- Link: http://localhost:8000/documents/12345

## Key Points
- Self-attention mechanism
- ...
```

**Implementation:**
- Store Paperless document IDs in Silverbullet notes
- Create clickable links to Paperless documents
- Use consistent naming convention

#### Pattern 2: Shared Filesystem

**Use Case:** Link documents stored in Paperless to notes in Silverbullet

**Structure:**
```
/data/
  ├── silverbullet/
  │   └── space/
  │       ├── Research/
  │       └── Attachments/ -> ../../paperless/media/documents/
  └── paperless/
      └── media/
          └── documents/
```

**Benefits:**
- Direct file access from Silverbullet
- No duplication
- Single source of truth

#### Pattern 3: Git-Based Sync (Future Anagora)

**Use Case:** Share Silverbullet notes to Anagora

**Workflow:**
```bash
# Silverbullet space is a Git repository
cd /data/silverbullet/space
git add .
git commit -m "Update research notes"
git push origin main

# Anagora Bridge pulls updates
uv run pull.py --config ~/agora/gardens.yaml
```

**Setup:**
1. Initialize Silverbullet space as Git repo
2. Add space URL to Anagora gardens.yaml
3. Anagora Bridge pulls notes periodically
4. Your notes become nodes in the knowledge graph

### Unified Search Strategies

#### Current State (2026)

No out-of-the-box unified search across Silverbullet, Paperless-ngx, and Anagora.

#### Solution 1: Browser Bookmarks
Create search shortcuts:
- Silverbullet: `http://localhost:3000/#search=query`
- Paperless: `http://localhost:8000/documents?query=query`
- Anagora: `https://anagora.org/search?q=query`

#### Solution 2: Custom Search Portal

Create a simple HTML page:
```html
<!DOCTYPE html>
<html>
<head><title>Knowledge Search</title></head>
<body>
  <h1>Search Across Knowledge Bases</h1>
  <input id="query" type="text" placeholder="Search...">
  <button onclick="searchAll()">Search</button>

  <script>
  function searchAll() {
    const q = document.getElementById('query').value;
    window.open(`http://localhost:3000/#search=${q}`, '_blank');
    window.open(`http://localhost:8000/documents?query=${q}`, '_blank');
  }
  </script>
</body>
</html>
```

#### Solution 3: API-Based Unified Search (Advanced)

**Requirements:**
- Silverbullet API access
- Paperless-ngx API access
- Custom backend service

**Pseudocode:**
```python
def unified_search(query):
    results = []

    # Search Silverbullet
    sb_results = requests.get(f'http://silverbullet:3000/api/search?q={query}')
    results.extend(format_results(sb_results, 'Silverbullet'))

    # Search Paperless
    pl_results = requests.get(
        f'http://paperless:8000/api/documents/',
        headers={'Authorization': 'Token XXX'},
        params={'query': query}
    )
    results.extend(format_results(pl_results, 'Paperless'))

    return results
```

**Deployment:**
- Deploy as separate service in Docker Compose
- Provide unified search interface
- Rank and merge results

#### Solution 4: External Search Tool

Use **Searxng** or **Meilisearch** as a unified search frontend:
- Configure custom search engines for each service
- Single search bar queries all sources
- Aggregated results

### Cross-Linking Strategy

**Best Practice:**
1. **Canonical IDs**: Use unique identifiers
   - Paperless: Document ID
   - Silverbullet: Page name
   - Anagora: Node name

2. **Consistent Naming**:
   ```markdown
   [[paper:attention-is-all-you-need]]  # Silverbullet note
   paperless:12345                       # Paperless doc ID
   [[attention is all you need]]        # Anagora node
   ```

3. **Metadata Fields**:
   - Store cross-references in frontmatter
   ```markdown
   ---
   paperless_id: 12345
   anagora_node: attention-is-all-you-need
   type: research-note
   ---
   ```

---

## 6. Backup Strategies

### Critical Importance

**Why Backups Matter:**
- Research data is irreplaceable
- OCR processing takes time (don't want to redo)
- Notes represent months/years of work
- Data corruption, hardware failure, ransomware risks

### 3-2-1 Backup Rule

**Best Practice for 2025-2026:**
- **3** copies of your data
- **2** different storage media
- **1** off-site copy

**Applied to Knowledge Stack:**
1. **Primary**: Docker volumes (production)
2. **Local Backup**: External hard drive
3. **Off-site**: Cloud storage (encrypted)

### Docker Volume Backup Strategy

#### Recommended Tools (2025-2026)

**Option 1: Offen**
- Shuts down containers before backup
- Prevents file corruption
- Clean backups without locked files

**Option 2: Backrest**
- Incremental backups using Restic
- Efficient storage (deduplication)
- Fast backup/restore
- Web UI for management

**Option 3: Restic (Direct)**
- Command-line backup tool
- Encryption built-in
- Multiple backends (S3, SFTP, local)

#### Backup Script Example

```bash
#!/bin/bash
# backup-knowledge-stack.sh

BACKUP_DIR="/mnt/backups/knowledge-stack"
DATE=$(date +%Y%m%d-%H%M%S)

# Stop containers
docker compose -f /path/to/docker-compose.yml down

# Backup volumes
tar -czf "$BACKUP_DIR/silverbullet-$DATE.tar.gz" /data/silverbullet
tar -czf "$BACKUP_DIR/paperless-$DATE.tar.gz" /data/paperless
tar -czf "$BACKUP_DIR/postgres-$DATE.tar.gz" /data/paperless/pgdata

# Restart containers
docker compose -f /path/to/docker-compose.yml up -d

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

# Sync to off-site
rclone sync $BACKUP_DIR remote:knowledge-backups
```

**Cron Job:**
```cron
0 2 * * * /usr/local/bin/backup-knowledge-stack.sh
```

### Configuration Backup

**Best Practice:** Store Docker Compose files and configs in Git

```bash
# Create backup repo
cd /path/to/configs
git init
git add docker-compose.yml .env
git commit -m "Initial knowledge stack config"
git remote add origin https://github.com/yourusername/knowledge-stack-config.git
git push -u origin main
```

**What to Version Control:**
- `docker-compose.yml`
- `.env` files (encrypted or use placeholder values)
- Silverbullet templates and config
- Paperless configuration
- Backup scripts

### Data-Specific Backup Strategies

#### Silverbullet

**Data Location:** All notes are plain Markdown files in `/space`

**Backup Options:**
1. **Git-based** (Recommended):
   ```bash
   cd /data/silverbullet/space
   git init
   git add .
   git commit -m "Backup notes $(date)"
   git push origin main
   ```

2. **Filesystem Sync**:
   - Syncthing (real-time sync to other devices)
   - Resilio Sync
   - rsync to remote server

3. **Cloud Backup**:
   ```bash
   rclone sync /data/silverbullet/space gdrive:silverbullet-backup
   ```

**Advantages:**
- Plain text = easy to backup
- No database corruption risk
- Can version control

#### Paperless-ngx

**Data Components:**
1. **Documents**: `/data/paperless/media`
2. **Database**: PostgreSQL (document metadata)
3. **Index**: Search index
4. **Configuration**: Settings and rules

**Backup Method 1: Docker Volume Backup**
```bash
# Stop Paperless
docker compose stop paperless-ngx

# Backup database
docker compose exec db pg_dump -U paperless paperless > paperless-db-backup.sql

# Backup media files
tar -czf paperless-media.tar.gz /data/paperless/media

# Restart
docker compose start paperless-ngx
```

**Backup Method 2: Paperless Export Feature**
- Use built-in export function
- Exports documents + metadata as JSON
- Easy to restore

**Database Backup (Automated):**
```yaml
services:
  db-backup:
    image: prodrigestivill/postgres-backup-local
    restart: unless-stopped
    volumes:
      - ./backups:/backups
    environment:
      - POSTGRES_HOST=db
      - POSTGRES_DB=paperless
      - POSTGRES_USER=paperless
      - POSTGRES_PASSWORD=paperless
      - SCHEDULE=@daily
      - BACKUP_KEEP_DAYS=7
```

### Disaster Recovery Testing

**Critical:** Test your backups regularly!

**Monthly Test:**
1. Spin up fresh Docker environment
2. Restore from backups
3. Verify data integrity
4. Document restore time
5. Fix any issues

**Checklist:**
- [ ] Can restore Silverbullet notes?
- [ ] Can restore Paperless documents?
- [ ] Can restore Paperless database?
- [ ] Are all links working?
- [ ] Is search functioning?
- [ ] Are all images/attachments present?

### Retention Policy

**Recommended Schedule:**
- **Hourly**: Keep 24 hours (if using incremental)
- **Daily**: Keep 30 days
- **Weekly**: Keep 12 weeks
- **Monthly**: Keep 12 months
- **Yearly**: Keep indefinitely

**Storage Calculation Example:**
- Silverbullet: ~100MB (text notes)
- Paperless: ~50GB (PDFs)
- Database: ~500MB
- Total per backup: ~50.6GB
- Monthly storage: ~50.6GB × 30 days = ~1.5TB

**With Incremental Backups (Restic):**
- Initial: 50.6GB
- Daily delta: ~500MB
- Monthly storage: ~65GB (much better!)

---

## 7. Resource Requirements Summary

### Complete Stack Requirements

**Minimum Configuration:**
- **RAM**: 8GB total
  - Silverbullet: 256MB
  - Paperless-ngx: 2GB
  - PostgreSQL: 512MB
  - Redis: 256MB
  - Tika: 1GB
  - Gotenberg: 512MB
  - System overhead: 3.5GB
- **CPU**: 4 cores
- **Storage**:
  - OS: 20GB
  - Docker images: 10GB
  - Data: Variable (plan for 100GB+)

**Recommended Configuration:**
- **RAM**: 16GB total
- **CPU**: 6-8 cores
- **Storage**: 500GB SSD (OS + Docker + data)

**Budget Configuration (without Tika/Gotenberg):**
- **RAM**: 4GB total
- **CPU**: 2 cores
- **Storage**: 250GB
- **Note**: PDF/image only, no Office document support

---

## 8. Implementation Roadmap

### Phase 1: Core Stack (Week 1)

**Goals:**
- Deploy Silverbullet
- Deploy Paperless-ngx (basic)
- Set up backups

**Tasks:**
1. Set up Docker Compose
2. Configure persistent volumes
3. Deploy Silverbullet
4. Configure basic authentication
5. Deploy Paperless-ngx with PostgreSQL and Redis
6. Test document ingestion
7. Set up daily backup script

### Phase 2: Full Document Processing (Week 2)

**Goals:**
- Add Tika and Gotenberg
- Optimize OCR
- Configure auto-tagging

**Tasks:**
1. Add Tika to Docker Compose
2. Add Gotenberg to Docker Compose
3. Configure Paperless to use Tika/Gotenberg
4. Test Office document processing
5. Configure OCR languages
6. Set up machine learning auto-tagging

### Phase 3: Integration (Week 3)

**Goals:**
- Link Silverbullet and Paperless
- Create cross-reference system
- Build search workflow

**Tasks:**
1. Design document ID system
2. Create Silverbullet templates for research notes
3. Build linking convention
4. Create search portal (optional)
5. Document workflow

### Phase 4: Anagora (Future)

**Goals:**
- Deploy Anagora (when Docker support available)
- Integrate Silverbullet notes
- Join federated knowledge graph

**Tasks:**
1. Monitor Anagora project for Docker support
2. Prepare Silverbullet space as Git repository
3. Configure Agora Bridge
4. Test federation
5. Share knowledge!

---

## 9. Security Considerations

### Authentication

**Silverbullet:**
- Enable built-in authentication
- Use strong passwords
- Consider reverse proxy with additional auth

**Paperless-ngx:**
- Create admin account immediately
- Use strong password
- Enable two-factor authentication (if available)

### Network Security

**Recommendations:**
1. **Reverse Proxy**: Use Nginx or Caddy
2. **HTTPS**: Enable TLS certificates (Let's Encrypt)
3. **Firewall**: Restrict access to trusted IPs
4. **VPN**: Use Tailscale or WireGuard for remote access

**Docker Compose Example:**
```yaml
services:
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
```

**Caddyfile:**
```
notes.yourdomain.com {
    reverse_proxy silverbullet:3000
}

docs.yourdomain.com {
    reverse_proxy paperless-ngx:8000
}
```

### Encryption

**At Rest:**
- Use encrypted filesystem (LUKS)
- Encrypt backup archives
- Use encrypted cloud storage

**In Transit:**
- Always use HTTPS
- Encrypt backups before uploading
- Use encrypted Git repositories for sensitive configs

### Secret Management

**Best Practices:**
- Never commit `.env` files with secrets to Git
- Use Docker secrets for sensitive values
- Rotate passwords regularly
- Use password manager for credentials

**Example `.env.template`:**
```bash
# Paperless
PAPERLESS_SECRET_KEY=CHANGE_ME
POSTGRES_PASSWORD=CHANGE_ME

# Silverbullet
SB_USER=CHANGE_ME
```

---

## 10. Maintenance Tasks

### Daily
- Monitor backup completion
- Check disk space

### Weekly
- Review Paperless ML suggestions
- Organize and tag new documents
- Review Silverbullet orphan pages

### Monthly
- Update Docker images
- Test backup restoration
- Review resource usage
- Clean up old backups

### Quarterly
- Security audit
- Password rotation
- Evaluate new features/plugins
- Review and optimize workflows

---

## Conclusion

This knowledge management stack provides a powerful, self-hosted solution for academic research and digital gardening:

- **Silverbullet**: Flexible, programmable note-taking
- **Paperless-ngx**: Robust document management with OCR
- **Anagora**: Future federated knowledge sharing

**Key Takeaways:**
1. Start with Silverbullet + Paperless-ngx core stack
2. Implement robust backup strategy immediately
3. Use consistent naming and cross-referencing
4. Plan for Anagora integration when Docker support arrives
5. Regular maintenance ensures long-term success

**Total Investment:**
- Time: 1-2 weeks initial setup
- Hardware: 16GB RAM, 4-6 cores, 500GB storage
- Ongoing: 2-4 hours/month maintenance

**Benefits:**
- Complete data ownership
- Privacy-first approach
- Powerful search and organization
- Extensible and customizable
- Active communities and support

---

## Sources

### Anagora
- [Installation Guide](https://www.anagora.org/Installation)
- [GitHub - flancian/agora](https://github.com/flancian/agora)
- [GitHub - flancian/agora-server](https://github.com/flancian/agora-server)
- [GitHub - flancian/agora-bridge](https://github.com/flancian/agora-bridge)
- [Anagora Homepage](https://anagora.org/)

### Silverbullet
- [SilverbulletMD Official Site](https://silverbullet.md/)
- [GitHub - silverbulletmd/silverbullet](https://github.com/silverbulletmd/silverbullet)
- [Docker Hub - zefhemel/silverbullet](https://hub.docker.com/r/zefhemel/silverbullet)
- [Self-Hosting SilverBullet with Docker](https://fossengineer.com/selfhosting-silverbullet/)
- [Silverbullet Docker Installation](https://silverbullet.md/Install/Docker)

### Paperless-ngx
- [Paperless-ngx Documentation](https://docs.paperless-ngx.com/)
- [GitHub - paperless-ngx/paperless-ngx](https://github.com/paperless-ngx/paperless-ngx)
- [Go Paperless in 2026](https://blog.elest.io/go-paperless-in-2026-how-paperless-ngx-organizes-your-documents-better-than-dropbox/)
- [The Ultimate Paperless-NGX Guide (2025)](https://deployn.de/en/guides/paperless-ngx/)
- [xTom - Setup with Docker Compose](https://xtom.com/blog/set-up-paperless-ngx-docker-compose/)

### Document Management Alternatives
- [12 Best Open-Source Document Managers for 2025](https://deepdocs.dev/document-manager-open-source/)
- [Docspell vs Mayan EDMS Comparison](https://www.saashub.com/compare-docspell-vs-mayan-edms)
- [5 Self-Hosted Document Management Systems](https://noted.lol/self-hosted-dms-applications/)
- [Docspell Paperless Import](https://docspell.org/docs/tools/paperless-import/)

### Backup Strategies
- [Easy Automated Docker Volume Backups](https://www.thepolyglotdeveloper.com/2025/05/easy-automated-docker-volume-backups-database-friendly/)
- [Docker Backup Strategies for 2025](https://portalzine.de/docker-backup-strategies-for-2025-protecting-your-container-environment/)
- [8 Essential Database Backup Strategies for 2025](https://cloudvara.com/database-backup-strategies/)
- [Data Backup Best Practices for 2025](https://www.ais-now.com/blog/data-backup-best-practices-2024/)

### Resource Requirements
- [Paperless-ngx Resource Requirements Discussion](https://github.com/paperless-ngx/paperless-ngx/discussions/4676)
- [Gotenberg Installation Docs](https://gotenberg.dev/docs/getting-started/installation)
- [Apache Tika Docker](https://hub.docker.com/r/apache/tika)

---

**Document Version:** 1.0
**Last Updated:** January 16, 2026
**Next Review:** April 2026

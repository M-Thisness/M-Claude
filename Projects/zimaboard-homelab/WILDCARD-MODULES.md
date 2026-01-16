# Wildcard Modules for Zimaboard HomeLab

## Introduction

Based on the Zimaboard's x86-64 architecture, available resources (16GB RAM), and the existing ecosystem focus (knowledge management, media automation, home automation, citizen science), here are **3 wildcard modules** that add significant value while fitting within resource constraints.

Each module is evaluated on:
- **Resource Footprint:** RAM, CPU, disk requirements
- **Ecosystem Fit:** Integration with existing services
- **Utility Score:** Practical usefulness vs resource cost
- **Fun Factor:** Educational or entertaining value

---

## Module 1: 🤖 Ollama - Local LLM Inference

### What It Is
Ollama is a lightweight framework for running large language models (LLMs) locally without cloud dependencies. Think "ChatGPT at home" - perfect for a knowledge management stack.

### Why It Fits This Ecosystem

1. **Knowledge Augmentation:**
   - Summarize research papers in Paperless-ngx
   - Generate notes/ideas in Silverbullet
   - Chat interface for querying your knowledge base
   - Extract key points from saved documents

2. **Privacy-First:**
   - All inference happens locally (no data leaves your network)
   - Sensitive documents stay private
   - No API costs

3. **Integration Potential:**
   - **Home Assistant:** Natural language automation ("turn on lights when I say 'movie time'")
   - **Paperless:** Auto-generate document tags and summaries
   - **BirdNET:** Generate birding insights and reports
   - **n8n/Automation:** AI-powered workflows

### Resource Requirements

| Component | Specification |
|-----------|---------------|
| **RAM** | 4-8GB (model dependent) |
| **CPU** | 0.5-2 cores (inference: ~10-30 tokens/sec on N3450) |
| **Disk** | 4-30GB (per model) |
| **GPU** | None (CPU inference only on Zimaboard) |

### Recommended Models for Zimaboard

| Model | Size | RAM | Speed | Use Case |
|-------|------|-----|-------|----------|
| **Phi-3-mini (3.8B)** | 2.3GB | 3-4GB | ~15 tok/sec | Q&A, summarization |
| **TinyLlama (1.1B)** | 637MB | 1-2GB | ~30 tok/sec | Quick tasks, embeddings |
| **Llama 3.2 (3B)** | 2GB | 3-4GB | ~12 tok/sec | General purpose |
| **Qwen2.5 (3B)** | 1.9GB | 3-4GB | ~14 tok/sec | Code, multilingual |

**Recommendation:** Start with **Phi-3-mini** (best quality-to-size ratio).

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
      - OLLAMA_ORIGINS=*
    mem_limit: 6g
    mem_reservation: 3g
    cpu_shares: 512  # Low priority (background)
    networks:
      - homelab

  # Optional: Web UI for Ollama
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    restart: unless-stopped
    ports:
      - "3001:8080"
    volumes:
      - open_webui_data:/app/backend/data
    environment:
      - OLLAMA_API_BASE_URL=http://ollama:11434/api
      - WEBUI_AUTH=false  # Enable for multi-user
    depends_on:
      - ollama
    mem_limit: 512m
    networks:
      - homelab

volumes:
  ollama_data:
  open_webui_data:

networks:
  homelab:
    external: true
```

### Quick Start

```bash
# Start Ollama
docker-compose up -d ollama

# Download a model
docker exec -it ollama ollama pull phi3:mini

# Test inference
docker exec -it ollama ollama run phi3:mini "Summarize the benefits of self-hosting"

# Access web UI
# Navigate to http://192.168.8.50:3001
```

### Integration Examples

#### 1. Summarize Paperless Documents
```bash
#!/bin/bash
# Auto-summarize new documents in Paperless

DOCUMENT_ID=$1
TEXT=$(curl -s "http://paperless:8000/api/documents/$DOCUMENT_ID/" | jq -r '.content')

SUMMARY=$(curl -s http://ollama:11434/api/generate -d '{
  "model": "phi3:mini",
  "prompt": "Summarize this document in 3 bullet points:\n\n'"$TEXT"'",
  "stream": false
}' | jq -r '.response')

# Update document custom field with summary
curl -X PATCH "http://paperless:8000/api/documents/$DOCUMENT_ID/" \
  -H "Content-Type: application/json" \
  -d '{"custom_fields": {"summary": "'"$SUMMARY"'"}}'
```

#### 2. Home Assistant Voice Control
```yaml
# configuration.yaml
conversation:
  intents:
    LLMQuery:
      - "Ask AI [question]"

automation:
  - alias: "LLM Query via Voice"
    trigger:
      platform: conversation
      command: "Ask AI {question}"
    action:
      service: rest_command.ollama_query
      data:
        question: "{{ trigger.slots.question }}"

rest_command:
  ollama_query:
    url: http://192.168.8.50:11434/api/generate
    method: POST
    payload: '{"model": "phi3:mini", "prompt": "{{ question }}"}'
```

### Pros & Cons

| Pros | Cons |
|------|------|
| ✅ Complete privacy (no cloud) | ❌ Slow inference on CPU (10-15 tok/sec) |
| ✅ No API costs | ❌ Large disk usage (models are GB-sized) |
| ✅ Powerful knowledge tool | ❌ High RAM usage (3-8GB per model) |
| ✅ Easy to integrate | ❌ Limited to smaller models (<7B) |
| ✅ Educational (learn about LLMs) | ❌ Can't run multiple models simultaneously |

### Resource Impact

- **Idle:** 150MB RAM, 0.1 CPU
- **Active (inference):** 4-6GB RAM, 1-2 CPU cores
- **Strategy:** Run on-demand, stop when not in use

### Utility Score: ⭐⭐⭐⭐☆ (4/5)
**Verdict:** High utility for knowledge workers. Significant resource cost but manageable if used selectively.

---

## Module 2: 🛡️ AdGuard Home - Network-Wide Ad Blocking & Privacy

### What It Is
AdGuard Home is a network-wide DNS sinkhole that blocks ads, trackers, and malware for **all devices** on your network (including IoT devices, smart TVs, phones) without per-device configuration.

### Why It Fits This Ecosystem

1. **Universal Privacy:**
   - Blocks ads on Sonos Beam (Spotify ads!)
   - Protects IoT devices (smart home trackers)
   - Filters malicious domains (security)
   - Faster browsing (no ad content downloads)

2. **Network Observability:**
   - **Complements ntopng/Suricata:** DNS-level traffic insights
   - See which devices query which domains
   - Identify compromised IoT devices (unusual DNS patterns)
   - Parental controls / content filtering

3. **Integration:**
   - **Home Assistant:** Automation based on DNS queries
   - **Grafana:** DNS metrics dashboard
   - **Prometheus:** Export blocking statistics
   - Replace your ISP's DNS (privacy, speed)

4. **Lightweight:**
   - Minimal resource usage (~100-200MB RAM)
   - Can handle 10,000+ queries/day easily
   - Better alternative to Pi-hole (more features, modern UI)

### Resource Requirements

| Component | Specification |
|-----------|---------------|
| **RAM** | 100-250MB |
| **CPU** | 0.05-0.2 cores (DNS queries are very fast) |
| **Disk** | 2GB (logs, blocklists) |
| **Network** | <1 Mbps |

**Resource Impact:** Negligible - perfect for always-on deployment.

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  adguardhome:
    image: adguard/adguardhome:latest
    container_name: adguardhome
    restart: unless-stopped
    ports:
      - "53:53/tcp"      # DNS
      - "53:53/udp"      # DNS
      - "3002:3000/tcp"  # Web UI (initial setup)
      - "8053:80/tcp"    # Web UI (after setup)
      - "853:853/tcp"    # DNS-over-TLS
      - "784:784/udp"    # DNS-over-QUIC
    volumes:
      - adguard_work:/opt/adguardhome/work
      - adguard_conf:/opt/adguardhome/conf
    environment:
      - TZ=America/New_York
    mem_limit: 512m
    mem_reservation: 128m
    cpu_shares: 1024
    cap_add:
      - NET_ADMIN  # Required for DHCP (optional)
    networks:
      homelab:
        ipv4_address: 192.168.8.53  # Static IP for DNS

volumes:
  adguard_work:
  adguard_conf:

networks:
  homelab:
    external: true
```

### Setup Instructions

```bash
# 1. Deploy AdGuard Home
docker-compose up -d adguardhome

# 2. Access web UI for initial setup
# http://192.168.8.53:3002

# 3. Configure upstream DNS servers
# Settings → DNS Settings → Upstream DNS:
#   1.1.1.1
#   1.0.0.1
#   8.8.8.8

# 4. Enable DNS blocklists
# Filters → DNS Blocklists → Add:
#   - AdGuard DNS filter
#   - OISD Big List (comprehensive)
#   - Steven Black's Unified Hosts
#   - Energized Ultimate (aggressive)

# 5. Configure client devices to use AdGuard as DNS
# Option A: Per-device (manual)
#   Set DNS to 192.168.8.53

# Option B: Network-wide (DHCP)
#   Edit /etc/dnsmasq.conf:
#   dhcp-option=6,192.168.8.53

# 6. Optional: Enable DNS-over-HTTPS (DoH)
#   Settings → Encryption → Enable DoH
#   Clients can use: https://192.168.8.53/dns-query
```

### Features & Capabilities

#### 1. **Ad Blocking Statistics**
- Real-time dashboard showing:
  - Queries per hour/day
  - % of queries blocked
  - Top blocked domains
  - Top clients (devices)

#### 2. **Custom Filtering Rules**
```
# Block specific domains
||facebook.com^
||tiktok.com^

# Allow domain even if on blocklist
@@||example.com^

# Block subdomains but allow main domain
||ads.example.com^

# Regex blocking (advanced)
/^ad[sxv]?[0-9]*\./
```

#### 3. **Parental Controls**
Enable safe browsing, block adult content:
```
# Filters → Blocklists → Add:
# - OISD NSFW (adult content)
# - UT1 Malware (malicious sites)
```

#### 4. **Per-Client Settings**
Different rules for different devices:
- Legion: Allow all (developer needs access)
- Sonos: Block trackers, allow streaming services
- IoT devices: Block all except whitelisted domains

#### 5. **DNS Rewrites (Local Domains)**
```
# Settings → DNS Rewrites
jellyfin.homelab.lan → 192.168.8.40
homeassistant.homelab.lan → 192.168.8.60
paperless.homelab.lan → 192.168.8.50
```

### Integration with Existing Services

#### 1. Home Assistant Integration
```yaml
# configuration.yaml
sensor:
  - platform: rest
    name: AdGuard Queries Today
    resource: http://192.168.8.53:8053/control/stats
    value_template: "{{ value_json.num_dns_queries }}"
    scan_interval: 300

  - platform: rest
    name: AdGuard Blocked Today
    resource: http://192.168.8.53:8053/control/stats
    value_template: "{{ value_json.num_blocked_filtering }}"
    scan_interval: 300

automation:
  - alias: "Alert on Suspicious DNS Activity"
    trigger:
      - platform: numeric_state
        entity_id: sensor.adguard_queries_today
        above: 10000  # Unusual spike
    action:
      - service: notify.mobile_app
        data:
          message: "Suspicious DNS activity detected!"
```

#### 2. Grafana Dashboard
```bash
# Export AdGuard metrics to Prometheus format
# Use AdGuard Home Exporter:
docker run -d \
  --name adguard-exporter \
  -p 9617:9617 \
  -e ADGUARD_SERVERS=http://192.168.8.53:8053 \
  ebrianne/adguard-exporter:latest

# Add to Prometheus config, visualize in Grafana
```

### Blocklist Recommendations

| Blocklist | Domains | Use Case | Aggressiveness |
|-----------|---------|----------|----------------|
| **AdGuard DNS** | ~50K | General ads | Medium |
| **OISD Big** | ~3M | Comprehensive | High |
| **Steven Black** | ~100K | Ads + malware | Medium |
| **Energized Ultimate** | ~1.5M | Maximum blocking | Very High |
| **NextDNS CNAME** | ~10K | Tracker uncloaking | Medium |

**Recommendation:** Start with **OISD Big** (good balance).

### Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Can't access certain sites | Over-blocking | Check query log, add to whitelist |
| Slow DNS resolution | Upstream DNS slow | Switch to Cloudflare (1.1.1.1) |
| IoT devices not working | Essential domains blocked | Add device to "allow all" client group |
| Ads still appear | Device using hardcoded DNS | Force all DNS to AdGuard via firewall |

### Force All Devices to Use AdGuard (Firewall)

```bash
# Redirect all DNS traffic to AdGuard
# Even if devices try to use 8.8.8.8, force through AdGuard

iptables -t nat -A PREROUTING -i vmbr+ ! -s 192.168.8.53 -p udp --dport 53 -j DNAT --to 192.168.8.53:53
iptables -t nat -A PREROUTING -i vmbr+ ! -s 192.168.8.53 -p tcp --dport 53 -j DNAT --to 192.168.8.53:53
```

### Pros & Cons

| Pros | Cons |
|------|------|
| ✅ Network-wide blocking (all devices) | ❌ Can break some websites/apps if too aggressive |
| ✅ Minimal resources (~150MB RAM) | ❌ Requires DNS configuration on clients |
| ✅ Detailed analytics | ❌ Can't block YouTube ads (served from same domain) |
| ✅ Improves privacy + security | ❌ Requires maintenance (updating blocklists) |
| ✅ Faster browsing (no ad content) | ❌ May conflict with dnsmasq (port 53 collision) |

### Resource Impact

- **Idle:** 100MB RAM, 0.05 CPU
- **Active:** 200MB RAM, 0.1-0.2 CPU
- **Peak:** 300MB RAM (updating blocklists)

### Utility Score: ⭐⭐⭐⭐⭐ (5/5)
**Verdict:** Essential service. Negligible resource cost, massive benefit. Deploy immediately.

---

## Module 3: 🔄 n8n - Workflow Automation (No-Code)

### What It Is
n8n is a powerful workflow automation tool (think "IFTTT/Zapier but self-hosted") that connects your services together with visual workflows. Perfect for automating repetitive tasks across your HomeLab ecosystem.

### Why It Fits This Ecosystem

1. **HomeLab Integration Hub:**
   - Connect all your services without writing code
   - 400+ pre-built integrations (APIs, webhooks, databases)
   - Visual workflow designer (drag-and-drop)
   - Scheduled tasks, event triggers, webhooks

2. **Practical Use Cases:**
   - **Media Automation:** Auto-organize downloads, notify when content arrives
   - **Knowledge Management:** Auto-import articles to Paperless, sync notes
   - **Home Automation:** Advanced HA automations beyond YAML
   - **Monitoring:** Aggregate alerts, send notifications
   - **Data Collection:** BirdNET logs → PostgreSQL → Grafana

3. **Learning Tool:**
   - Understand API integrations
   - Build complex workflows visually
   - Debug with execution logs
   - Export workflows as JSON (version control)

### Resource Requirements

| Component | Specification |
|-----------|---------------|
| **RAM** | 300-800MB (depends on workflow complexity) |
| **CPU** | 0.1-0.5 cores (idle: 0.05, executing: 0.5-1) |
| **Disk** | 5GB (workflows, executions, logs) |
| **Database** | PostgreSQL (shared with other services) |

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=changeme123  # Change this!
      - N8N_HOST=n8n.homelab.lan
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://192.168.8.50:5678/
      - GENERIC_TIMEZONE=America/New_York

      # PostgreSQL connection (shared with Paperless)
      - DB_TYPE=postgresdb
      - DB_POSTGRESDB_HOST=postgres
      - DB_POSTGRESDB_PORT=5432
      - DB_POSTGRESDB_DATABASE=n8n
      - DB_POSTGRESDB_USER=n8n
      - DB_POSTGRESDB_PASSWORD=n8n_secure_password

      # Execution settings
      - EXECUTIONS_DATA_SAVE_ON_ERROR=all
      - EXECUTIONS_DATA_SAVE_ON_SUCCESS=all
      - EXECUTIONS_DATA_SAVE_MANUAL_EXECUTIONS=true
      - EXECUTIONS_DATA_PRUNE=true
      - EXECUTIONS_DATA_MAX_AGE=168  # Keep 7 days

    volumes:
      - n8n_data:/home/node/.n8n
      - /mnt/storage:/mnt/storage:ro  # Access NAS (read-only for safety)
    depends_on:
      - postgres
    mem_limit: 1g
    mem_reservation: 300m
    cpu_shares: 512
    networks:
      - homelab

volumes:
  n8n_data:

networks:
  homelab:
    external: true
```

### Practical Workflow Examples

#### 1. 📺 Auto-Request Popular Content
**Trigger:** Daily at 9 AM
**Workflow:**
1. Fetch trending movies from TMDB API
2. Filter by rating (>7.0) and year (2023+)
3. Check if already in Radarr
4. If not, auto-request in Jellyseerr
5. Send notification to phone

```
┌─────────────┐    ┌──────────┐    ┌─────────┐    ┌───────────┐
│ Schedule    │───▶│ TMDB API │───▶│ Filter  │───▶│ Jellyseerr│
│ (daily 9am) │    │ Trending │    │ Rating  │    │ API       │
└─────────────┘    └──────────┘    └─────────┘    └───────────┘
                                                         │
                                                         ▼
                                                   ┌──────────┐
                                                   │ Pushover │
                                                   │ Notify   │
                                                   └──────────┘
```

#### 2. 🐦 BirdNET Daily Report
**Trigger:** Daily at 8 PM
**Workflow:**
1. Query PostgreSQL (BirdNET database)
2. Get today's bird sightings
3. Generate markdown report with Ollama
4. Save to Silverbullet as daily note
5. Send summary email

```
┌─────────────┐    ┌───────────┐    ┌─────────┐    ┌────────────┐
│ Schedule    │───▶│ PostgreSQL│───▶│ Ollama  │───▶│ Silverbullet│
│ (daily 8pm) │    │ Query     │    │ Summary │    │ API        │
└─────────────┘    └───────────┘    └─────────┘    └────────────┘
                                                           │
                                                           ▼
                                                      ┌─────────┐
                                                      │ Email   │
                                                      └─────────┘
```

#### 3. 📄 Auto-Archive Important Emails
**Trigger:** Email received (IMAP)
**Workflow:**
1. Monitor inbox for emails with attachments
2. Download PDF attachments
3. Upload to Paperless-ngx
4. Apply tags based on sender/subject
5. Delete email (archived in Paperless)

```
┌──────────┐    ┌──────────┐    ┌───────────┐    ┌─────────┐
│ IMAP     │───▶│ Filter   │───▶│ Paperless │───▶│ Delete  │
│ Trigger  │    │ Has PDF? │    │ Upload    │    │ Email   │
└──────────┘    └──────────┘    └───────────┘    └─────────┘
```

#### 4. 🔔 Smart Home Presence Detection
**Trigger:** Webhook from Home Assistant
**Workflow:**
1. Receive "person arrived home" event
2. Check time of day
3. If evening: Turn on lights, start music on Sonos
4. Query today's bird sightings
5. Send welcome notification with bird count

```
┌──────────┐    ┌─────────┐    ┌──────────┐    ┌─────────┐
│ HA       │───▶│ Time    │───▶│ Control  │───▶│ Query   │
│ Webhook  │    │ Filter  │    │ Devices  │    │ BirdNET │
└──────────┘    └─────────┘    └──────────┘    └─────────┘
                                                     │
                                                     ▼
                                               ┌──────────┐
                                               │ Notify   │
                                               └──────────┘
```

#### 5. 💾 Automated Backups
**Trigger:** Weekly (Sunday 3 AM)
**Workflow:**
1. Stop Docker containers gracefully
2. Create tar.gz backup of volumes
3. Upload to cloud (Backblaze B2, S3)
4. Verify upload integrity (checksum)
5. Restart containers
6. Send success/failure notification

```
┌─────────────┐    ┌──────────┐    ┌─────────┐    ┌─────────┐
│ Schedule    │───▶│ Stop     │───▶│ Backup  │───▶│ Upload  │
│ (Sun 3am)   │    │ Services │    │ Volumes │    │ to B2   │
└─────────────┘    └──────────┘    └─────────┘    └─────────┘
                                                        │
                                                        ▼
                                                   ┌─────────┐
                                                   │ Restart │
                                                   │ Notify  │
                                                   └─────────┘
```

### Pre-Built Integrations (Relevant to HomeLab)

| Category | Services |
|----------|----------|
| **Media** | Jellyfin, Sonarr, Radarr, Lidarr, qBittorrent |
| **Databases** | PostgreSQL, MySQL, SQLite, MongoDB, Redis |
| **Messaging** | MQTT, Telegram, Discord, Slack, Email (SMTP/IMAP) |
| **Cloud** | Google Drive, Dropbox, AWS S3, Backblaze B2 |
| **Home** | Home Assistant, IFTTT, Webhooks |
| **Docs** | Markdown, PDF, Google Docs, Notion |
| **APIs** | HTTP Request, GraphQL, REST, Webhook |
| **Code** | Execute Code (JS/Python), SSH, Bash |

### Advanced Features

#### 1. **Error Handling**
- Retry failed steps (exponential backoff)
- Send alerts on workflow failures
- Fallback paths (if X fails, do Y)

#### 2. **Conditional Logic**
```
IF weather == "rainy"
  THEN send umbrella reminder
  ELSE check if plants need watering
```

#### 3. **Data Transformation**
- JSON parsing, filtering, mapping
- Regular expressions
- Date/time manipulation
- Math operations

#### 4. **Subworkflows**
- Reusable workflow components
- Call workflows from other workflows
- Pass parameters between workflows

### Security Considerations

```yaml
# Enable authentication (required!)
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=strong_password_here

# For production, use OAuth2 or reverse proxy auth
# Example: Caddy reverse proxy with BasicAuth

# Limit access to management network only
iptables -A INPUT -p tcp --dport 5678 ! -s 192.168.8.0/24 -j DROP
```

### Resource Management

| Scenario | RAM Usage | CPU Usage |
|----------|-----------|-----------|
| Idle (no workflows running) | 250MB | 0.05 cores |
| Simple workflow (every 5 min) | 350MB | 0.1 cores |
| Complex workflow (API calls, DB queries) | 600MB | 0.5 cores |
| Heavy workflow (file processing) | 800MB | 1 core |

**Strategy:** Disable workflows you don't actively use to reduce memory.

### Learning Resources

- **Official Docs:** https://docs.n8n.io
- **Workflow Templates:** https://n8n.io/workflows
- **Community Forum:** https://community.n8n.io
- **Video Tutorials:** YouTube "n8n workflows"

### Pros & Cons

| Pros | Cons |
|------|------|
| ✅ Visual workflow designer (no code) | ❌ Moderate RAM usage (300-800MB) |
| ✅ 400+ integrations | ❌ Learning curve (workflow logic) |
| ✅ Self-hosted (data privacy) | ❌ No mobile app (web only) |
| ✅ Active development | ❌ Some advanced features require enterprise |
| ✅ Great for automation | ❌ Can be overkill for simple tasks |

### Resource Impact

- **Idle:** 250MB RAM, 0.05 CPU
- **Active:** 400-600MB RAM, 0.2-0.5 CPU
- **Peak:** 800MB RAM, 1 CPU (heavy workflows)

### Utility Score: ⭐⭐⭐⭐⭐ (5/5)
**Verdict:** Extremely powerful automation hub. Moderate resource cost justified by massive productivity gains. Essential for advanced HomeLab users.

---

## Comparison Matrix

| Module | RAM | CPU | Disk | Utility | Fun Factor | Ease of Setup |
|--------|-----|-----|------|---------|------------|---------------|
| **Ollama (LLM)** | 4-8GB | 1-2 | 10-30GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **AdGuard Home** | 150MB | 0.1 | 2GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **n8n** | 400MB | 0.2 | 5GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## Deployment Recommendations

### 🟢 Deploy Immediately (High Value, Low Cost)
1. **AdGuard Home** - Essential privacy/security, negligible resources
2. **n8n** - Automation hub, moderate resources, massive utility

### 🟡 Deploy Conditionally (High Cost, High Value)
3. **Ollama** - Only if you have 4-8GB RAM to spare after core services

### Alternative Wildcard Ideas (Honorable Mentions)

#### 4. 📸 **Immich** - Self-Hosted Photo Management
- **What:** Google Photos alternative with AI face recognition, auto-backup
- **Resources:** 2-4GB RAM, 1-2 CPU, 100GB+ storage
- **Verdict:** Great for families, but heavy on resources

#### 5. 🍳 **Mealie** - Recipe Manager
- **What:** Digital cookbook with meal planning, shopping lists
- **Resources:** 512MB RAM, 0.2 CPU, 5GB storage
- **Verdict:** Niche use case, but excellent for cooking enthusiasts

#### 6. 🎬 **Frigate NVR** - AI Camera Monitoring
- **What:** NVR with object detection (integrates with Home Assistant)
- **Resources:** 1-2GB RAM, 1-2 CPU (CPU inference), 100GB+ storage
- **Verdict:** Requires cameras, CPU-intensive, but great for security

#### 7. 🌐 **Changedetection.io** - Website Change Monitor
- **What:** Monitor websites for changes, get alerts (price drops, stock, news)
- **Resources:** 256MB RAM, 0.1 CPU, 2GB storage
- **Verdict:** Lightweight, useful for deal hunting / research monitoring

#### 8. 📊 **Actual Budget** - Personal Finance
- **What:** YNAB alternative, budget tracking, bank sync
- **Resources:** 256MB RAM, 0.1 CPU, 2GB storage
- **Verdict:** Great for financial management, simple to deploy

---

## Final Recommendations

### For the Zimaboard 16GB Setup:

**Must-Deploy:**
1. ✅ **AdGuard Home** (150MB) - Essential, negligible cost
2. ✅ **n8n** (400MB) - Automation hub, high utility

**Optional (if RAM permits after core services):**
3. ⚠️ **Ollama** (4-8GB) - Only if running minimal stack (Scenario 3)

**Total Wildcard Impact:**
- **Minimal:** AdGuard + n8n = ~550MB RAM, 0.3 CPU
- **With LLM:** All three = ~5-9GB RAM, 1-2 CPU

### Recommended Deployment Order:
1. Deploy core services first (Phases 1-3)
2. Add AdGuard Home (always fits)
3. Add n8n (for automation)
4. Monitor resources for 1 week
5. If RAM >4GB free, add Ollama with Phi-3-mini
6. If RAM <4GB free, skip Ollama or run on Legion instead

---

**Document Version:** 1.0
**Last Updated:** 2026-01-16
**Target Hardware:** Zimaboard 16GB

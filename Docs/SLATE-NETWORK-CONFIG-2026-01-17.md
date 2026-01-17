# Slate Router Network Configuration Changes

**Session Date:** 2026-01-17
**Device:** GL.iNet Slate (OpenWrt-based)
**IP:** 192.168.8.1

---

## Summary

Reconfigured the DNS architecture to:
1. Use **Mullvad DNS** (no-logs) instead of Cloudflare
2. Enable **per-client query logging** via blocky
3. Bypass GL.iNet's DNS policy routing (was causing firewall conflicts)

---

## 1. Firewall (`/etc/config/firewall`)

| Setting | Before | After | Purpose |
|---------|--------|-------|---------|
| `firewall.lan_drop_leaked_dns.enabled` | `1` | `0` | Was blocking DNS from LAN to router |
| `firewall.dns_order.enabled` | `1` | `0` | Disabled GL.iNet DNS interception script |

```bash
# Verify
uci show firewall | grep -E 'lan_drop_leaked_dns.enabled|dns_order.enabled'
```

---

## 2. GL-DNS (`/etc/config/gl-dns`)

| Setting | Before | After | Purpose |
|---------|--------|-------|---------|
| `gl-dns.@dns[0].force_dns` | `1` | `0` | Disabled "Override DNS for all clients" |

```bash
# Verify
uci get gl-dns.@dns[0].force_dns  # Should return: 0
```

---

## 3. Route Policy (`/etc/config/route_policy`)

| Setting | Before | After | Purpose |
|---------|--------|-------|---------|
| `route_policy.global.instance_on` | `1` | `0` | Disabled VPN DNS instance routing |

```bash
# Verify
uci get route_policy.global.instance_on  # Should return: 0
```

---

## 4. DHCP/dnsmasq (`/etc/config/dhcp`)

| Setting | Before | After | Purpose |
|---------|--------|-------|---------|
| `dhcp.@dnsmasq[0].port` | `53` | `0` | Disabled dnsmasq DNS (DHCP still active) |

```bash
# Verify
uci get dhcp.@dnsmasq[0].port  # Should return: 0
```

---

## 5. Blocky (`/etc/blocky/config.yml`)

**Full config:**
```yaml
upstreams:
  groups:
    default:
      - 127.0.0.1:5053          # → cloudflared
bootstrapDns:
  - tcp+udp:194.242.2.2         # Mullvad DNS (bootstrap)
  - tcp+udp:1.1.1.1             # Cloudflare (fallback)
blocking:
  loading:
    refreshPeriod: 4h
  denylists:
    ads:
      - https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard/ultimate.txt
  clientGroupsBlock:
    default:
      - ads
caching:
  minTime: 60m
  prefetching: true
clientLookup:
  clients:
    slate:
      - 192.168.8.1
    zima:
      - 192.168.8.21
    book:
      - 192.168.8.158
    legion-windows:
      - 192.168.8.231
    legion-cachy:
      - 192.168.8.130
    pixel:
      - 192.168.8.126
ports:
  dns: 53                       # Changed from 5335
  http: 4005
log:
  level: info
queryLog:
  type: csv-client              # Per-client log files
  target: /tmp/blocky-logs
  logRetentionDays: 7
```

```bash
# Verify
cat /etc/blocky/config.yml
netstat -tlnup | grep ':53.*blocky'
```

---

## 6. Cloudflared (`/etc/cloudflared/config.yml`)

| Setting | Before | After | Purpose |
|---------|--------|-------|---------|
| `proxy-dns-upstream` | `https://1.1.1.1/dns-query` | `https://dns.mullvad.net/dns-query` | Privacy: Mullvad no-logs DNS |

**Full config:**
```yaml
tunnel: --no-autoupdate
proxy-dns: true
proxy-dns-port: 5053
proxy-dns-upstream:
  - https://dns.mullvad.net/dns-query
```

```bash
# Verify
cat /etc/cloudflared/config.yml
netstat -tlnup | grep ':5053.*cloudflared'
```

---

## Final Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  CLIENTS                                                     │
│  ├── book (192.168.8.158)                                   │
│  ├── legion-windows (192.168.8.231)                         │
│  ├── legion-cachy (192.168.8.130)                           │
│  ├── pixel (192.168.8.126)                                  │
│  ├── zima (192.168.8.21)                                    │
│  └── slate (192.168.8.1)                                    │
└─────────────────┬───────────────────────────────────────────┘
                  │ DNS queries (port 53)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  BLOCKY (:53)                                               │
│  ├── Ad blocking (hagezi ultimate list)                     │
│  ├── Per-client query logging → /tmp/blocky-logs/           │
│  └── Caching (60min TTL, prefetch)                          │
└─────────────────┬───────────────────────────────────────────┘
                  │ upstream (127.0.0.1:5053)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  CLOUDFLARED (:5053)                                        │
│  └── DoH encrypted tunnel                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTPS
                  ▼
┌─────────────────────────────────────────────────────────────┐
│  MULLVAD DNS (dns.mullvad.net)                              │
│  └── No-logs policy, Sweden jurisdiction                    │
└─────────────────────────────────────────────────────────────┘
```

---

## Query Log Access

```bash
# All clients
ssh root@192.168.8.1 "cat /tmp/blocky-logs/*.log"

# Specific client
ssh root@192.168.8.1 "cat /tmp/blocky-logs/*book*.log"
ssh root@192.168.8.1 "cat /tmp/blocky-logs/*legion-windows*.log"
ssh root@192.168.8.1 "cat /tmp/blocky-logs/*legion-cachy*.log"
ssh root@192.168.8.1 "cat /tmp/blocky-logs/*zima*.log"

# Real-time monitoring
ssh root@192.168.8.1 "tail -f /tmp/blocky-logs/*.log"
```

---

## Rollback Commands (if needed)

```bash
# Re-enable GL.iNet DNS features
uci set firewall.lan_drop_leaked_dns.enabled='1'
uci set firewall.dns_order.enabled='1'
uci set gl-dns.@dns[0].force_dns='1'
uci set route_policy.global.instance_on='1'
uci set dhcp.@dnsmasq[0].port='53'
uci commit
fw4 reload
/etc/init.d/dnsmasq restart

# Restore cloudflared to Cloudflare DNS
cat > /etc/cloudflared/config.yml << 'EOF'
tunnel: --no-autoupdate
proxy-dns: true
proxy-dns-port: 5053
proxy-dns-upstream:
  - https://1.1.1.1/dns-query
  - https://1.0.0.1/dns-query
EOF
service cloudflared restart

# Restore blocky to port 5335 (behind dnsmasq)
# Edit /etc/blocky/config.yml and set ports.dns: 5335
service blocky restart
```

---

## Privacy Analysis

| Provider | Jurisdiction | Business Model | Logging | 2023 Raid Test |
|----------|-------------|----------------|---------|----------------|
| **Cloudflare** | USA | Enterprise CDN (DNS is free) | 24-48hr debug | N/A |
| **Mullvad** | Sweden | VPN subscriptions only | No logs | Police left empty-handed |

**Recommendation:** Mullvad has stronger structural incentives for privacy — their entire revenue depends on it.

---

## Key Insight

GL.iNet's VPN policy routing (`dns_table`, `force_dns`, `instance_on`) was designed for their UI-based VPN DNS leak protection, but conflicted with the custom blocky→cloudflared→Mullvad chain. Disabling these features lets blocky handle DNS directly, giving per-client visibility and full control over the DNS path.

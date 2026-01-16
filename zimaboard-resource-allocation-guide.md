# Zimaboard 16GB Resource Allocation Guide
## Home Assistant + Nessus Deployment on Proxmox

### System Overview
- **Hardware**: Zimaboard 2 1664 (Quad-Core N150, 16GB DDR5)
- **Hypervisor**: Proxmox VE
- **Services**: Home Assistant + Nessus Vulnerability Scanner

---

## Resource Allocation Strategy

### Total Available Resources
- **RAM**: 16GB total
  - Proxmox host: ~2GB reserved
  - Available for VMs/LXC: ~14GB
- **CPU**: 4 cores @ up to 3.6GHz
- **Storage**: 64GB eMMC + SATA expansion

### Recommended Allocation

#### Home Assistant (LXC or VM)
**Recommendation**: Use LXC for better resource efficiency

| Resource | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| RAM | 2GB | 4GB | Start with 2GB, scale to 4GB with add-ons |
| CPU Cores | 2 | 2 | 2 cores sufficient for most setups |
| Storage | 16GB | 32GB | Grows with recorder database |

**Configuration**:
- LXC: Privileged container for USB device access
- VM: If using Home Assistant OS (includes Supervisor)

#### Nessus (VM - Recommended)
**Recommendation**: Use VM for security isolation

| Resource | Minimum | Recommended | Maximum | Notes |
|----------|---------|-------------|---------|-------|
| RAM | 2GB | 3-4GB | 6GB | Limit to prevent host exhaustion |
| CPU Cores | 2 | 2 | 2 | CPU-intensive during scans |
| Storage | 30GB | 40GB | 50GB | Plugin database grows over time |

**Configuration**:
- VM with resource limits enforced
- CPU units: 1024 (normal priority)
- Memory ballooning: Disabled (for stability)

#### Reserve for Proxmox Host
- **RAM**: 2GB minimum for host stability
- **CPU**: 0.5-1 core equivalent for overhead
- **Storage**: 8GB for Proxmox itself

### Total Allocation Summary

```
Home Assistant:     4GB RAM,  2 CPU cores
Nessus:            4GB RAM,  2 CPU cores
Proxmox + Buffer:  2GB RAM,  ~0.5 core overhead
Other Services:    6GB RAM,  available
-------------------------------------------
Total:            16GB RAM,  4 cores
```

---

## Resource Management Strategies

### 1. Memory Management

#### Configure Memory Limits in Proxmox
For VMs, set both minimum and maximum:
```bash
# Set VM memory (VMID 100 = Nessus example)
qm set 100 -memory 4096
qm set 100 -balloon 0  # Disable ballooning for stability

# Set VM memory (VMID 101 = Home Assistant example)
qm set 101 -memory 4096
qm set 101 -balloon 0
```

For LXC containers:
```bash
# Set LXC memory limits (CTID 100 example)
pct set 100 -memory 4096 -swap 0
```

#### Enable Memory Overcommit Protection
Edit `/etc/sysctl.conf` on Proxmox host:
```bash
# Prevent OOM killer from being too aggressive
vm.overcommit_memory = 2
vm.overcommit_ratio = 80

# Swappiness (lower = less swap usage)
vm.swappiness = 10
```

Apply changes:
```bash
sysctl -p
```

### 2. CPU Management

#### CPU Units and Limits
Proxmox uses CPU units (1024 = normal share):

```bash
# Nessus - normal priority
qm set 100 -cpuunits 1024 -cores 2

# Home Assistant - higher priority
qm set 101 -cpuunits 2048 -cores 2

# CPU limit (optional, 50% = 0.5 per core)
qm set 100 -cpulimit 2
```

#### CPU Governor Settings
On Proxmox host, ensure performance governor:
```bash
# Check current governor
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Set to performance (persists until reboot)
echo performance | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Make permanent (install cpufrequtils)
apt install cpufrequtils
echo 'GOVERNOR="performance"' > /etc/default/cpufrequtils
systemctl restart cpufrequtils
```

### 3. Nessus-Specific Resource Controls

#### Nessus Scan Configuration
Edit scan settings to prevent resource exhaustion:

**Basic Settings**:
- Max simultaneous hosts: 5 (default: 10-20)
- Max checks per host: 3 (default: 5)
- Network timeout: 5 seconds
- Max scan duration: 1 hour

**Advanced Settings** (via Nessus UI):
```
Performance:
  max_hosts = 5
  max_checks = 3
  max_simult_tcp_sessions_per_host = 4
  max_simult_tcp_sessions_per_scan = 16

Throttling:
  throttle_scan = yes
  reduce_connections_on_congestion = yes
  avoid_sequential_scans = yes

Resource Control:
  stop_scan_on_disconnect = yes
  stop_scan_on_hang = yes
```

#### Nessus Service Resource Limits (systemd)
Inside Nessus VM, create `/etc/systemd/system/nessusd.service.d/limits.conf`:

```ini
[Service]
CPUQuota=150%
MemoryMax=3.5G
MemoryHigh=3G
TasksMax=200
Nice=10
```

Apply:
```bash
systemctl daemon-reload
systemctl restart nessusd
```

#### Cgroups v2 Limits (Alternative)
If using cgroups directly:
```bash
# Create cgroup for Nessus
mkdir /sys/fs/cgroup/nessus

# Set memory limit
echo "3500M" > /sys/fs/cgroup/nessus/memory.max
echo "3000M" > /sys/fs/cgroup/nessus/memory.high

# Set CPU limit (150% of one core)
echo "150000 100000" > /sys/fs/cgroup/nessus/cpu.max

# Move Nessus process to cgroup
echo $(pidof nessusd) > /sys/fs/cgroup/nessus/cgroup.procs
```

### 4. Scan Scheduling Strategy

#### Schedule Nessus for Low-Usage Hours
Create cron job on Proxmox host to start/stop Nessus VM:

```bash
# Edit crontab
crontab -e

# Start Nessus VM at 2 AM (VMID 100)
0 2 * * * /usr/sbin/qm start 100

# Stop Nessus VM at 6 AM
0 6 * * * /usr/sbin/qm shutdown 100

# Or suspend instead of shutdown to preserve state
# 0 6 * * * /usr/sbin/qm suspend 100
```

#### Nessus Internal Scheduling
Configure scans in Nessus to run:
- **Weeknights**: 2:00 AM - 5:00 AM
- **Weekends**: Extended windows if needed
- **Never during**: Peak usage hours (6 PM - 11 PM)

#### Script for Conditional Start
Create `/usr/local/bin/start-nessus-if-idle.sh`:

```bash
#!/bin/bash
# Only start Nessus if system load is low

VMID=100
LOAD_THRESHOLD=2.0

# Check 5-minute load average
LOAD=$(uptime | awk -F'load average:' '{print $2}' | awk -F, '{print $2}' | xargs)

if (( $(echo "$LOAD < $LOAD_THRESHOLD" | bc -l) )); then
    echo "System load is low ($LOAD), starting Nessus VM"
    qm start $VMID
else
    echo "System load is high ($LOAD), skipping Nessus start"
fi
```

Make executable and add to cron:
```bash
chmod +x /usr/local/bin/start-nessus-if-idle.sh
# Add to crontab: 0 2 * * * /usr/local/bin/start-nessus-if-idle.sh
```

### 5. Storage Management

#### Separate Storage for Database Growth
- **Home Assistant**: Separate disk/directory for recorder database
- **Nessus**: Separate storage for scan results and plugin cache

#### Database Maintenance
**Home Assistant**:
```yaml
# configuration.yaml
recorder:
  purge_keep_days: 7
  auto_purge: true
  auto_repack: true
```

**MariaDB** (run monthly):
```bash
docker exec homeassistant_mariadb mysqlcheck -u root -p --auto-repair --optimize homeassistant
```

**Nessus**:
- Enable automatic database optimization
- Limit scan result retention to 30-90 days

---

## Monitoring Resource Usage

### Proxmox CLI Monitoring

#### Real-time VM/LXC Resource Usage
```bash
# All VMs/containers
pvesh get /cluster/resources --type vm

# Specific VM
qm status 100
qm monitor 100

# LXC container
pct status 100
```

#### System-wide Resources
```bash
# Overall system stats
pvesh get /nodes/$(hostname)/status

# Memory usage
free -h

# CPU usage
mpstat 1

# Per-VM detailed stats
qm monitor 100
info cpus
info memory
```

### Install Monitoring Tools

#### Option 1: Prometheus + Grafana
Great for detailed metrics and dashboards.

#### Option 2: Glances (Lightweight)
```bash
# Install on Proxmox host
apt install glances

# Run in web mode
glances -w --port 61208
```

Access at: `http://<proxmox-ip>:61208`

#### Option 3: htop with sorting
```bash
apt install htop
htop  # Press F5 for tree view, F6 to sort
```

### Home Assistant Resource Monitoring
Add system monitor integration in `configuration.yaml`:

```yaml
sensor:
  - platform: systemmonitor
    resources:
      - type: memory_use_percent
      - type: processor_use
      - type: disk_use_percent
        arg: /
      - type: load_1m
      - type: load_5m
      - type: load_15m
```

### Alert Configuration

#### Proxmox Email Alerts
Configure in Proxmox GUI:
- Datacenter → Notification → Add notification
- Set thresholds for memory, CPU, storage

#### Shell Script for Alerts
Create `/usr/local/bin/check-resources.sh`:

```bash
#!/bin/bash
MEMORY_THRESHOLD=90
CPU_THRESHOLD=80

MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100.0}' | cut -d. -f1)
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1)

if [ "$MEM_USAGE" -gt "$MEMORY_THRESHOLD" ]; then
    echo "WARNING: Memory usage at ${MEM_USAGE}%" | mail -s "Proxmox Memory Alert" admin@example.com
fi

if [ "$CPU_USAGE" -gt "$CPU_THRESHOLD" ]; then
    echo "WARNING: CPU usage at ${CPU_USAGE}%" | mail -s "Proxmox CPU Alert" admin@example.com
fi
```

Run every 5 minutes via cron:
```bash
*/5 * * * * /usr/local/bin/check-resources.sh
```

---

## Emergency Procedures

### If System Becomes Unresponsive

#### 1. Access Proxmox Console
Physical access or IPMI/iKVM

#### 2. Identify Resource Hog
```bash
top -o %MEM
# or
ps aux --sort=-%mem | head -20
```

#### 3. Emergency VM Shutdown
```bash
# Graceful shutdown
qm shutdown 100

# Force stop if unresponsive
qm stop 100

# Suspend to save state
qm suspend 100
```

#### 4. Kill Runaway Process
```bash
# Find process
ps aux | grep nessus

# Kill by PID
kill -9 <PID>

# Or use killall
killall -9 nessusd
```

#### 5. Reboot If Necessary
```bash
# Sync filesystems first
sync

# Reboot
reboot
```

---

## Optimization Tips

### 1. Disable Unnecessary Services
```bash
# Disable unused Proxmox services
systemctl disable pve-ha-crm
systemctl disable pve-ha-lrm
systemctl disable corosync  # If not using clustering
```

### 2. Use LXC Where Possible
- LXC containers use 30-50% less RAM than VMs for same workload
- Faster startup times
- Better CPU efficiency

### 3. Home Assistant Optimization
- Disable unused integrations
- Use YAML mode instead of UI for less overhead
- Limit history/recorder to essential entities
- Use external database (MariaDB/PostgreSQL) instead of SQLite

### 4. Nessus Optimization
- Use Nessus Essentials if you have ≤16 IPs to scan
- Disable unnecessary plugins
- Schedule scans strategically
- Use credentialed scans (faster and more accurate)

### 5. Network Optimization
- Use VLANs to segment traffic
- Use Proxmox SDN for better network management
- Consider dedicated network interface for scan traffic

---

## Backup Strategy

### Automated Backups
```bash
# Backup VMs to Proxmox backup storage
vzdump 100 --compress zstd --mode snapshot --storage local

# Add to cron (daily at 1 AM)
0 1 * * * vzdump 100 101 --compress zstd --mode snapshot --storage local --mailto admin@example.com
```

### Home Assistant Backups
- Use built-in backup feature (if using HA OS in VM)
- For Docker: backup config directories and database
- Store backups off-host

### Configuration Backups
```bash
# Backup Proxmox config
proxmox-backup-client backup pve-config.pxar:/etc/pve
```

---

## Summary: Best Practices

1. **Start Conservative**: Begin with minimum allocations, scale up as needed
2. **Monitor Actively**: Use Glances or Grafana for real-time monitoring
3. **Schedule Wisely**: Run Nessus during off-hours only
4. **Limit Resources**: Use cgroups/systemd limits to prevent runaway processes
5. **Regular Maintenance**: Purge old data, optimize databases monthly
6. **Test Failover**: Verify system stability under load before production use
7. **Document Changes**: Keep notes on resource adjustments and their effects
8. **Backup Regularly**: Automate backups and test restoration procedures
9. **Update Incrementally**: Don't update all services simultaneously
10. **Plan for Growth**: Leave 2-4GB RAM buffer for future services

---

## Additional Resources

- [Proxmox Resource Management](https://pve.proxmox.com/wiki/Resource_Management)
- [Tenable Nessus Documentation](https://docs.tenable.com/nessus/)
- [Home Assistant Performance Tips](https://www.home-assistant.io/docs/installation/docker/#performance)
- [Linux cgroups v2 Documentation](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)

# Nessus Deployment Guide for Proxmox/Zimaboard

## Overview
Comprehensive guide for deploying Tenable Nessus vulnerability scanner on a resource-constrained Zimaboard (16GB RAM) running Proxmox.

---

## Nessus Essentials vs Professional

### Feature Comparison

| Feature | Nessus Essentials | Nessus Professional |
|---------|------------------|---------------------|
| **Cost** | Free | Paid (subscription) |
| **IP Limit** | 16 IPs (recently reduced to 5-16) | Unlimited |
| **Scan Frequency** | Unlimited | Unlimited |
| **Plugin Updates** | Weekly | Real-time (daily) |
| **Compliance Scans** | ❌ No | ✅ Yes |
| **Configuration Audits** | ❌ No | ✅ Yes |
| **Advanced Reporting** | Basic HTML/PDF | Customizable, multiple formats |
| **Data Export** | Limited | Full CSV/XML export |
| **Live Results** | ❌ No | ✅ Yes |
| **Technical Support** | Community only | Official support |
| **License Transfer** | ❌ No | ✅ Yes |
| **Virtual Appliance** | ❌ No | ✅ Yes |
| **API Access** | Limited | Full API |

### Which to Choose?

#### Choose **Nessus Essentials** if:
- ✅ Home lab with ≤16 devices
- ✅ Learning vulnerability scanning
- ✅ Basic network security auditing
- ✅ Budget constraints
- ✅ Adequate with weekly plugin updates

#### Choose **Nessus Professional** if:
- ✅ Managing >16 IP addresses
- ✅ Need compliance scanning (PCI-DSS, HIPAA, etc.)
- ✅ Require configuration audits
- ✅ Need advanced reporting features
- ✅ Commercial/professional use
- ✅ Require technical support

### Capabilities Comparison

**Nessus Essentials can:**
- Scan up to 16 IP addresses (check current limit)
- Perform credentialed and non-credentialed scans
- Detect 65,000+ vulnerabilities
- Run all vulnerability checks
- Generate basic reports
- Schedule scans
- Export basic results

**Nessus Essentials cannot:**
- Scan more than 16 IPs per scanner
- Perform compliance checks (CIS, PCI-DSS, etc.)
- Run configuration audits
- Export detailed data for other tools
- Access advanced reporting templates
- Use Live Results feature
- Get immediate plugin updates

---

## Resource Requirements

### Official Tenable Requirements

| Specification | Minimum | Recommended | Maximum (Zimaboard) |
|--------------|---------|-------------|---------------------|
| **RAM** | 2GB | 4GB | 6GB |
| **CPU Cores** | 1 @ 1GHz | 2 @ 2GHz | 2 @ 3.6GHz |
| **Disk Space** | 30GB | 40GB | 50GB |
| **Network** | 1Gbps | 2.5Gbps | 2.5Gbps (Dual) |

### Real-World Resource Usage

**Idle State**:
- RAM: ~800MB - 1.2GB
- CPU: <5%
- Disk: ~4GB (plugins + database)

**During Active Scan**:
- RAM: 1.5GB - 4GB (depending on scan complexity)
- CPU: 50-100% (very CPU-intensive)
- Disk I/O: Moderate to high
- Network: High (during network discovery)

**Important Notes**:
- Tenable Nessus is a **CPU-intensive application**
- Care should be taken to **avoid oversubscribed resources**
- **Credentialed scans** require more resources than non-credentialed
- **Complex scans** with many plugins need more RAM and CPU
- Resource usage scales with:
  - Number of simultaneous hosts
  - Number of simultaneous checks per host
  - Scan type (basic vs. comprehensive)
  - Network latency and target responsiveness

---

## Deployment: LXC vs VM

### Recommendation: Use VM for Nessus

| Consideration | LXC Container | VM (Recommended) |
|--------------|---------------|------------------|
| **Security Isolation** | ⚠️ Shared kernel | ✅ Full isolation |
| **Resource Overhead** | ✅ Lower (~5%) | ⚠️ Higher (~10-15%) |
| **Migration** | ❌ Limited | ✅ Live migration |
| **Snapshot Support** | ✅ Basic | ✅ Full |
| **USB Passthrough** | ⚠️ Complex | ✅ Straightforward |
| **Network Isolation** | ⚠️ Moderate | ✅ Complete |
| **Tenable Support** | ❌ Community only | ✅ Official images |
| **Security** | ⚠️ Root-unsafe | ✅ Root-safe |

### Why VM is Preferred

1. **Security Tool Requirements**
   - Vulnerability scanners need strong isolation
   - Running security tools in containers exposes host kernel
   - VMs provide better attack surface segmentation

2. **Official Support**
   - Tenable provides qcow2 images for KVM
   - Official documentation assumes VM deployment
   - Easier to get support with standard deployment

3. **Resource Predictability**
   - VMs have guaranteed resource allocation
   - Containers share kernel resources (potential conflicts)
   - Better control over CPU/memory limits

4. **Future Flexibility**
   - Can migrate VM to other hosts
   - Snapshots before major scans
   - Easier to scale resources

### When to Consider LXC

Only consider LXC if:
- Extreme resource constraints (<4GB total RAM)
- Running 10+ other services simultaneously
- Willing to accept security trade-offs
- Have experience hardening containers

---

## Proxmox VM Deployment

### Method 1: Using Tenable's QCOW2 Image (Recommended)

```bash
# Download Nessus virtual appliance
cd /var/lib/vz/template/iso/
wget https://downloads.tenable.com/Nessus-<version>-vm.qcow2
# Check Tenable downloads page for latest version

# Create VM
qm create 100 \
  --name nessus \
  --memory 4096 \
  --balloon 0 \
  --cores 2 \
  --cpu host \
  --scsihw virtio-scsi-pci \
  --net0 virtio,bridge=vmbr0 \
  --agent 1

# Import disk
qm importdisk 100 Nessus-<version>-vm.qcow2 local-lvm

# Attach disk
qm set 100 --scsi0 local-lvm:vm-100-disk-0

# Set boot disk
qm set 100 --boot order=scsi0

# Set resource limits
qm set 100 --cpulimit 2 --cpuunits 1024

# Start VM
qm start 100
```

### Method 2: Manual Installation on Ubuntu/Debian VM

```bash
# Create Ubuntu VM
qm create 100 \
  --name nessus \
  --memory 4096 \
  --balloon 0 \
  --cores 2 \
  --cpu host \
  --scsihw virtio-scsi-pci \
  --net0 virtio,bridge=vmbr0 \
  --cdrom local:iso/ubuntu-22.04-server-amd64.iso \
  --scsi0 local-lvm:40

# Boot and install Ubuntu (minimal installation)
qm start 100

# After Ubuntu installation, access VM console and install Nessus:
# 1. Download Nessus .deb package
wget https://www.tenable.com/downloads/api/v2/pages/nessus/files/Nessus-10.11.1-ubuntu1404_amd64.deb

# 2. Install Nessus
sudo dpkg -i Nessus-10.11.1-ubuntu1404_amd64.deb

# 3. Start Nessus service
sudo systemctl start nessusd
sudo systemctl enable nessusd

# 4. Access web interface
# https://<VM-IP>:8834
```

### VM Optimization Settings

```bash
# Disable memory ballooning (important for stability)
qm set 100 --balloon 0

# CPU topology (expose all cores)
qm set 100 --cores 2 --sockets 1

# Set CPU limit to prevent runaway usage
qm set 100 --cpulimit 2.0  # 200% = 2 full cores

# Lower CPU priority (normal = 1024)
qm set 100 --cpuunits 1024

# Use host CPU type for best performance
qm set 100 --cpu host

# Enable NUMA (if needed)
qm set 100 --numa 1

# Set machine type
qm set 100 --machine q35

# Network optimization
qm set 100 --net0 virtio,bridge=vmbr0,firewall=0

# Disk optimization (writeback cache)
qm set 100 --scsi0 local-lvm:vm-100-disk-0,cache=writeback,discard=on,ssd=1
```

---

## Resource Limiting Strategies

### 1. Proxmox VM-Level Limits

```bash
# Hard memory limit (4GB)
qm set 100 --memory 4096 --balloon 0

# CPU limit (150% = 1.5 cores max)
qm set 100 --cpulimit 1.5

# CPU scheduling priority
qm set 100 --cpuunits 512  # Lower than default 1024 = less priority

# I/O throttling (MB/s)
qm set 100 --scsi0 local-lvm:vm-100-disk-0,mbps_rd=50,mbps_wr=50
```

### 2. systemd Service Limits (Inside VM)

Create `/etc/systemd/system/nessusd.service.d/limits.conf`:

```ini
[Service]
# Memory limits
MemoryMax=3.5G
MemoryHigh=3G
MemorySwapMax=0

# CPU limits (150% = 1.5 cores)
CPUQuota=150%
CPUWeight=50

# Task limits
TasksMax=200

# Nice level (lower priority)
Nice=10

# I/O priority (best-effort, priority 4)
IOSchedulingClass=2
IOSchedulingPriority=4

# Process limits
LimitNOFILE=4096
LimitNPROC=512
```

Apply limits:
```bash
sudo systemctl daemon-reload
sudo systemctl restart nessusd
```

### 3. Cgroups v2 Limits (Inside VM)

```bash
# Create cgroup for Nessus
sudo mkdir -p /sys/fs/cgroup/nessus.slice

# Set memory limit
echo "3500M" | sudo tee /sys/fs/cgroup/nessus.slice/memory.max
echo "3000M" | sudo tee /sys/fs/cgroup/nessus.slice/memory.high

# Set CPU limit (150000 microseconds per 100000 = 150%)
echo "150000 100000" | sudo tee /sys/fs/cgroup/nessus.slice/cpu.max

# Set I/O weight (lower = less priority)
echo "50" | sudo tee /sys/fs/cgroup/nessus.slice/io.weight

# Move Nessus process to cgroup
sudo systemctl set-property nessusd.service Slice=nessus.slice
```

### 4. Nessus Scan Configuration Limits

#### Advanced Settings (via Nessus UI)

Navigate to: **Scan Template** → **Advanced** → **Performance**

```
General Settings:
  max_hosts = 5                    # Default: 10-20, Lower = less resource usage
  max_checks = 3                   # Default: 5, Lower = fewer simultaneous checks
  max_simult_tcp_sessions = 16     # Default: unlimited, Control TCP connections

Performance Tuning:
  max_simult_tcp_sessions_per_host = 4     # Default: 15
  max_simult_tcp_sessions_per_scan = 16    # Default: unlimited

Throttling:
  throttle_scan = yes              # Enable CPU throttling
  reduce_connections_on_congestion = yes
  avoid_sequential_scans = yes

Network Settings:
  network_receive_timeout = 5      # Seconds
  network_timeout = 5              # Seconds

Scan Behavior:
  stop_scan_on_disconnect = yes
  stop_scan_on_hang = yes
  auto_enable_dependencies = yes
```

#### Via nessuscli (Command Line)

```bash
# Access Nessus CLI
sudo /opt/nessus/sbin/nessuscli

# Set global scan settings
sudo /opt/nessus/sbin/nessuscli fix --set max_hosts=5
sudo /opt/nessus/sbin/nessuscli fix --set max_checks=3
sudo /opt/nessus/sbin/nessuscli fix --set throttle_scan=yes

# View current settings
sudo /opt/nessus/sbin/nessuscli fix --list
```

#### Scan Policy Configuration

Create a "Resource-Limited" scan policy:

1. **Basic Settings**:
   - Scan Type: Basic Network Scan
   - Targets: Limit to 5 hosts maximum per scan

2. **Discovery Settings**:
   - Port Scan Range: Common ports only (not all 65535)
   - Network Ping: ICMP only
   - Host Discovery: Fast method

3. **Assessment**:
   - Scan Speed: Paranoid or Sneaky (slower but less resource-intensive)
   - Max concurrent hosts: 3
   - Max concurrent checks: 2

4. **Advanced**:
   - Enable all throttling options
   - Set conservative timeouts
   - Reduce TCP sessions

### 5. Scan Scheduling Best Practices

```bash
# Schedule scans during low-usage hours via Nessus UI
# Recommended windows for 16GB Zimaboard:
#   - Weeknights: 2:00 AM - 5:00 AM
#   - Weekends: Extended 1:00 AM - 6:00 AM
#   - Never during: 6:00 PM - 11:00 PM (peak usage)

# Or use Proxmox cron to auto-start/stop VM
# Add to Proxmox host crontab:

# Start Nessus VM at 2 AM
0 2 * * * /usr/sbin/qm start 100

# Stop Nessus VM at 6 AM
0 6 * * * /usr/sbin/qm shutdown 100

# Alternative: Suspend instead of shutdown
# 0 6 * * * /usr/sbin/qm suspend 100
# 0 2 * * * /usr/sbin/qm resume 100
```

---

## Preventing Crashes and System Overload

### Common Crash Scenarios

1. **Out of Memory (OOM)**
   - Symptom: VM or entire host becomes unresponsive
   - Cause: Scan consuming all available RAM
   - Prevention: Hard memory limits + OOM killer configuration

2. **CPU Starvation**
   - Symptom: Other services become slow
   - Cause: Nessus using 100% CPU for extended periods
   - Prevention: CPU limits + nice values + scheduling

3. **I/O Bottleneck**
   - Symptom: Disk becomes saturated, system slow
   - Cause: Database writes during large scans
   - Prevention: I/O limits + separate storage

4. **Network Congestion**
   - Symptom: Network timeouts, slow connectivity
   - Cause: Aggressive port scanning
   - Prevention: Scan throttling + QoS

### Prevention Strategy

#### 1. OOM Killer Configuration (Proxmox Host)

```bash
# Protect critical services on host
# Edit: /etc/systemd/system/pveproxy.service.d/oom.conf
[Service]
OOMScoreAdjust=-1000

# Make Nessus VM more likely to be killed if OOM
qm set 100 --startup order=5  # Lower startup order = lower priority
```

#### 2. Watchdog Timer (Inside Nessus VM)

```bash
# Install watchdog
sudo apt install watchdog

# Configure /etc/watchdog.conf
max-load-1 = 24
max-load-5 = 18
max-load-15 = 12
min-memory = 512
allocatable-memory = 1024

# Enable and start
sudo systemctl enable watchdog
sudo systemctl start watchdog
```

#### 3. Monitoring and Alerting

Install monitoring inside Nessus VM:

```bash
# Install monitoring tools
sudo apt install sysstat htop iotop

# Create resource monitor script
sudo nano /usr/local/bin/monitor-resources.sh
```

```bash
#!/bin/bash
# /usr/local/bin/monitor-resources.sh

MEMORY_THRESHOLD=85
CPU_THRESHOLD=90
LOGFILE="/var/log/resource-monitor.log"

while true; do
    # Check memory usage
    MEM_USAGE=$(free | grep Mem | awk '{printf("%.0f", ($3/$2) * 100.0)}')

    # Check CPU usage
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d. -f1)

    if [ "$MEM_USAGE" -gt "$MEMORY_THRESHOLD" ]; then
        echo "$(date): WARNING - Memory usage at ${MEM_USAGE}%" >> $LOGFILE
        # Optional: Kill Nessus scan
        # sudo systemctl restart nessusd
    fi

    if [ "$CPU_USAGE" -gt "$CPU_THRESHOLD" ]; then
        echo "$(date): WARNING - CPU usage at ${CPU_USAGE}%" >> $LOGFILE
    fi

    sleep 60
done
```

```bash
chmod +x /usr/local/bin/monitor-resources.sh

# Create systemd service
sudo nano /etc/systemd/system/resource-monitor.service
```

```ini
[Unit]
Description=Resource Monitor
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/monitor-resources.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable resource-monitor
sudo systemctl start resource-monitor
```

#### 4. Emergency Kill Switch

Create script to emergency stop Nessus:

```bash
# On Proxmox host: /usr/local/bin/emergency-stop-nessus.sh
#!/bin/bash
echo "Emergency stopping Nessus VM..."

# Try graceful shutdown first
qm shutdown 100 --timeout 30

# If still running after 30s, force stop
sleep 35
if qm status 100 | grep -q "running"; then
    echo "Forcing stop..."
    qm stop 100
fi

echo "Nessus VM stopped."
```

---

## Optimization Tips

### 1. Plugin Management

```bash
# Disable unused plugin families to reduce scan time/resources
# In Nessus UI: Scan Template → Plugins → Configure

# Recommended disabled families for home lab:
#   - SCADA
#   - Policy Compliance (if using Essentials)
#   - MacOS (if no Macs)
#   - Solaris (if no Solaris)

# Keep essential families:
#   - General
#   - Service detection
#   - Web Servers
#   - Databases
#   - Backdoors
#   - Default Unix Accounts
```

### 2. Database Maintenance

```bash
# Purge old scan results (Nessus UI)
# Settings → Advanced → Scan Results

# Set retention policy:
#   - Keep results for: 30 days
#   - Auto-purge enabled: Yes

# Manual database vacuum (reduces size)
sudo systemctl stop nessusd
sudo /opt/nessus/sbin/nessuscli fix --reset-all
sudo systemctl start nessusd
```

### 3. Use Credentialed Scans

**Paradox**: Credentialed scans are **more resource-efficient**

- **Non-credentialed**: Brute-force testing, many attempts
- **Credentialed**: Direct access, accurate results, faster

Setup credentialed scans:
```
Scan Configuration → Credentials → Add
  - SSH: Username + password or SSH key
  - Windows: Username + password (SMB)
  - SNMP: Community string
```

Benefits:
- 50-70% faster scan time
- More accurate results
- Less network traffic
- Lower CPU usage per finding

### 4. Network Segmentation

Create separate VLAN for scanning:
- Isolate scan traffic from production
- Prevent interference with other services
- Better troubleshooting

Proxmox VLAN configuration:
```bash
# Create VLAN-aware bridge
# In Proxmox GUI: Datacenter → node → Network → Create → Linux Bridge
# Set VLAN aware: Yes
# Bridge ports: ens18

# Assign VM to VLAN
qm set 100 --net0 virtio,bridge=vmbr1,tag=10
```

### 5. Scan Target Organization

- **Group similar hosts**: Scan servers separately from workstations
- **Scan by priority**: Critical systems during dedicated windows
- **Use host groups**: Organize targets logically
- **Incremental scans**: Don't scan all hosts at once

Example schedule:
```
Monday 2 AM:    Critical servers (5 hosts)
Tuesday 2 AM:   Network infrastructure (3 hosts)
Wednesday 2 AM: Workstations Group 1 (8 hosts)
Thursday 2 AM:  Workstations Group 2 (8 hosts)
Friday 2 AM:    IoT/Smart devices (10 hosts)
```

---

## Monitoring Nessus Resource Usage

### From Proxmox Host

```bash
# Real-time VM resource usage
qm monitor 100

# In monitor console:
info status
info cpus
info memory
info blockstats

# CPU usage
qm status 100 | grep cpu

# Memory usage
qm status 100 | grep mem
```

### Inside Nessus VM

```bash
# Install monitoring tools
sudo apt install sysstat htop iotop nethogs

# CPU usage per process
htop

# I/O usage
sudo iotop

# Network usage
sudo nethogs

# System statistics
sar -u 2 10  # CPU
sar -r 2 10  # Memory
sar -n DEV 2 10  # Network
```

### Nessus Internal Metrics

Access Nessus web UI → Help → System Information

Shows:
- Memory usage
- CPU usage
- Active scans
- Database size
- Plugin count

### Grafana Dashboard (Advanced)

Setup Telegraf → InfluxDB → Grafana for detailed metrics:

1. Install Telegraf in Nessus VM
2. Configure to send metrics to InfluxDB
3. Create Grafana dashboard
4. Monitor in real-time

---

## Backup and Recovery

### VM Snapshots

```bash
# Create snapshot before major scans
qm snapshot 100 pre-scan-$(date +%Y%m%d)

# List snapshots
qm listsnapshot 100

# Restore snapshot
qm rollback 100 <snapshot-name>

# Delete old snapshots
qm delsnapshot 100 <snapshot-name>
```

### Nessus Configuration Backup

```bash
# Backup Nessus configuration
sudo /opt/nessus/sbin/nessuscli backup --file /backup/nessus-backup-$(date +%Y%m%d).tar

# Restore
sudo /opt/nessus/sbin/nessuscli restore --file /backup/nessus-backup-YYYYMMDD.tar
```

### Automated Backup Script

```bash
#!/bin/bash
# /usr/local/bin/backup-nessus.sh

BACKUP_DIR="/mnt/backup/nessus"
DATE=$(date +%Y%m%d)

# Create backup directory
mkdir -p $BACKUP_DIR

# Stop Nessus
sudo systemctl stop nessusd

# Backup configuration
sudo /opt/nessus/sbin/nessuscli backup --file $BACKUP_DIR/nessus-$DATE.tar

# Backup scan results (if needed)
sudo tar czf $BACKUP_DIR/nessus-scans-$DATE.tar.gz /opt/nessus/var/nessus/

# Start Nessus
sudo systemctl start nessusd

# Clean old backups (keep last 7)
find $BACKUP_DIR -name "nessus-*.tar" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/nessus-$DATE.tar"
```

---

## Summary: Zimaboard 16GB Nessus Configuration

### Recommended Setup

```
Platform:        Proxmox VM (not LXC)
RAM:             4GB (max 6GB if needed)
CPU:             2 cores with limits
Storage:         40GB
Edition:         Nessus Essentials (if ≤16 IPs)
Scan Schedule:   2-5 AM weeknights
Concurrent Hosts: 3-5 maximum
Resource Limits: Enabled (systemd + Proxmox)
Monitoring:      Basic (built-in + htop)
```

### Critical Settings

```bash
# Proxmox VM config
qm set 100 --memory 4096 --balloon 0
qm set 100 --cores 2 --cpulimit 2.0
qm set 100 --cpuunits 1024

# Nessus scan settings
max_hosts = 5
max_checks = 3
throttle_scan = yes

# systemd limits
MemoryMax=3.5G
CPUQuota=150%
```

### Monitoring Checklist

- [ ] VM resource usage stays below 80%
- [ ] Host memory usage stays below 85%
- [ ] Scans complete without timeouts
- [ ] Other services remain responsive
- [ ] No OOM kills in logs
- [ ] Network latency acceptable

### Troubleshooting Steps

1. Check VM resource usage
2. Review scan configuration (reduce hosts/checks)
3. Verify systemd limits applied
4. Check Proxmox host resources
5. Review Nessus logs: `/opt/nessus/var/nessus/logs/`
6. Restart services if needed
7. Consider reducing concurrent scans

---

## Additional Resources

- [Tenable Nessus Documentation](https://docs.tenable.com/nessus/)
- [Nessus Scan Tuning Guide](https://docs.tenable.com/quick-reference/nessus-scan-tuning/)
- [Proxmox Resource Management](https://pve.proxmox.com/wiki/Resource_Management)
- [Linux Cgroups Documentation](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)

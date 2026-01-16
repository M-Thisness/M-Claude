# Zimaboard Homelab Deployment Guide
## Home Assistant + Nessus on 16GB RAM

This comprehensive guide provides everything needed to deploy Home Assistant and Nessus vulnerability scanner on a Zimaboard with 16GB RAM running Proxmox.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Documentation Overview](#documentation-overview)
3. [Hardware Specifications](#hardware-specifications)
4. [Deployment Recommendations](#deployment-recommendations)
5. [Resource Allocation Summary](#resource-allocation-summary)
6. [File Reference](#file-reference)
7. [Step-by-Step Deployment](#step-by-step-deployment)
8. [Troubleshooting](#troubleshooting)
9. [Additional Resources](#additional-resources)

---

## 🚀 Quick Start

### For Home Assistant (Docker Container Method)

```bash
# 1. Create LXC container in Proxmox
pct create 100 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname homeassistant \
  --memory 4096 \
  --cores 2 \
  --storage local-lvm \
  --rootfs local-lvm:16 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1,keyctl=1

# 2. Start and enter container
pct start 100
pct enter 100

# 3. Run setup script
chmod +x setup-homeassistant.sh
./setup-homeassistant.sh

# 4. Deploy with docker-compose
cd /opt/homeassistant
docker compose up -d

# 5. Access Home Assistant
# http://<IP>:8123
```

### For Nessus (VM Method)

```bash
# 1. Create VM for Nessus
qm create 101 --name nessus --memory 4096 --cores 2 --cpu host \
  --net0 virtio,bridge=vmbr0 --scsihw virtio-scsi-pci

# 2. Install from ISO or import qcow2 image
# See nessus-deployment-guide.md for details

# 3. Access Nessus
# https://<IP>:8834
```

---

## 📚 Documentation Overview

This repository contains comprehensive guides for deploying a production-ready homelab:

### Core Documentation

| Document | Purpose | Best For |
|----------|---------|----------|
| **home-assistant-deployment-comparison.md** | Compares HA OS vs Container vs Supervised | Choosing deployment method |
| **nessus-deployment-guide.md** | Complete Nessus setup and optimization | Security scanning setup |
| **zimaboard-resource-allocation-guide.md** | Resource management strategies | System administration |

### Configuration Files

| File | Purpose |
|------|---------|
| **home-assistant-docker-compose.yml** | Production-ready HA stack |
| **home-assistant.env.example** | Environment variables template |
| **mosquitto.conf** | MQTT broker configuration |
| **homeassistant-recorder-config.yaml** | Database and MQTT integration |
| **setup-homeassistant.sh** | Automated setup script |

---

## 💻 Hardware Specifications

### Zimaboard 2 1664
- **CPU**: Intel N150 Quad-Core @ 3.6GHz
- **RAM**: 16GB DDR5 (non-upgradable)
- **Storage**: 64GB eMMC + Dual SATA 3.0
- **Network**: Dual 2.5GbE
- **Form Factor**: Fanless, low-power (6W TDP)
- **Use Case**: 24/7 homelab, NAS, Docker host

### Resource Constraints
With only 16GB RAM, careful resource allocation is critical when running multiple services.

---

## 🎯 Deployment Recommendations

### Home Assistant: Container vs VM

| Scenario | Recommendation | Reasoning |
|----------|---------------|-----------|
| **Limited resources (16GB)** | ✅ **Container (LXC)** | 50% less overhead, more RAM for other services |
| **Need add-ons** | ⚠️ VM (Home Assistant OS) | Only option for official add-on support |
| **Running with Nessus** | ✅ **Container (LXC)** | Better resource sharing |
| **Beginner friendly** | VM (Home Assistant OS) | Easier setup, better documentation |
| **Advanced users** | ✅ **Container (LXC)** | More control, flexibility |

**For Zimaboard 16GB + Nessus**: Use **Home Assistant Container (LXC)**

### Nessus: VM Required

| Consideration | Recommendation |
|--------------|----------------|
| **Deployment Type** | ✅ **VM** (not LXC) |
| **Reasoning** | Security isolation, official support |
| **RAM Allocation** | 4GB (max 6GB) |
| **CPU Allocation** | 2 cores with limits |

---

## 📊 Resource Allocation Summary

### Optimal 16GB Distribution

```
Service              RAM     CPU    Storage   Notes
─────────────────────────────────────────────────────
Proxmox Host         2GB     0.5    8GB       Base system
Home Assistant       4GB     2.0    16GB      LXC container
Nessus              4GB     2.0    40GB      VM (scheduled)
MariaDB             512MB   0.5    10GB      In HA container
Mosquitto           256MB   0.25   1GB       In HA container
Buffer/Other        5.25GB  1.0    -         Future services
─────────────────────────────────────────────────────
Total               ~16GB   4.0    75GB+
```

### Key Strategies

1. **Home Assistant**: LXC container with Docker Compose
2. **Nessus**: VM with strict resource limits
3. **Scheduling**: Run Nessus during off-hours only (2-5 AM)
4. **Limits**: Enforce memory/CPU caps to prevent crashes
5. **Monitoring**: Active resource tracking

---

## 📁 File Reference

### Quick Access

```bash
# All files in /home/user/M-Claude/

# Documentation
├── HOMELAB-DEPLOYMENT-README.md              # This file
├── home-assistant-deployment-comparison.md   # HA deployment guide
├── nessus-deployment-guide.md                # Nessus setup guide
├── zimaboard-resource-allocation-guide.md    # Resource management

# Home Assistant Configuration
├── home-assistant-docker-compose.yml         # Main compose file
├── home-assistant.env.example                # Environment template
├── homeassistant-recorder-config.yaml        # HA config snippet
├── mosquitto.conf                            # MQTT broker config
└── setup-homeassistant.sh                    # Automated setup
```

---

## 🛠️ Step-by-Step Deployment

### Phase 1: Proxmox Setup

1. **Install Proxmox VE** on Zimaboard
2. **Update system**: `apt update && apt upgrade -y`
3. **Configure network**: Set static IP, firewall rules
4. **Install basic tools**: `apt install vim htop iotop`

### Phase 2: Home Assistant Deployment

#### Option A: Container Method (Recommended for 16GB)

**Step 1: Create LXC Container**
```bash
# Create privileged container for USB access
pct create 100 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname homeassistant \
  --memory 4096 \
  --cores 2 \
  --storage local-lvm \
  --rootfs local-lvm:16 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1,keyctl=1

# Add USB device passthrough (adjust device path)
echo "lxc.cgroup2.devices.allow: c 188:* rwm" >> /etc/pve/lxc/100.conf
echo "lxc.mount.entry: /dev/ttyUSB0 dev/ttyUSB0 none bind,optional,create=file" >> /etc/pve/lxc/100.conf

pct start 100
```

**Step 2: Run Setup Script**
```bash
# Copy files to container
pct push 100 setup-homeassistant.sh /root/setup-homeassistant.sh
pct push 100 home-assistant-docker-compose.yml /root/docker-compose.yml
pct push 100 home-assistant.env.example /root/.env.example
pct push 100 mosquitto.conf /root/mosquitto.conf

# Enter container and run setup
pct enter 100
cd /root
chmod +x setup-homeassistant.sh
./setup-homeassistant.sh
```

**Step 3: Configure Environment**
```bash
cd /opt/homeassistant
cp /root/docker-compose.yml .
cp /root/.env.example .env
cp /root/mosquitto.conf mosquitto/config/

# Edit .env and change passwords
nano .env

# Edit docker-compose.yml and update USB device paths
nano docker-compose.yml
```

**Step 4: Deploy Stack**
```bash
docker compose up -d

# View logs
docker compose logs -f homeassistant

# Access Home Assistant at http://<IP>:8123
```

#### Option B: VM Method (If you need add-ons)

See **home-assistant-deployment-comparison.md** for detailed VM setup instructions.

### Phase 3: Nessus Deployment

**Step 1: Create Nessus VM**
```bash
# Download Nessus image (or use Ubuntu ISO)
# See nessus-deployment-guide.md for download links

# Create VM
qm create 101 \
  --name nessus \
  --memory 4096 \
  --balloon 0 \
  --cores 2 \
  --cpu host \
  --scsihw virtio-scsi-pci \
  --net0 virtio,bridge=vmbr0

# If using qcow2 image:
qm importdisk 101 Nessus-*.qcow2 local-lvm
qm set 101 --scsi0 local-lvm:vm-101-disk-0
qm set 101 --boot order=scsi0

# Start VM
qm start 101
```

**Step 2: Configure Resource Limits**
```bash
# Set CPU and memory limits
qm set 101 --cpulimit 2.0 --cpuunits 1024
qm set 101 --balloon 0

# Enable monitoring
qm set 101 --agent 1
```

**Step 3: Install and Configure Nessus**
```bash
# Access VM console
# Install Nessus from downloaded package or configure appliance
# Access web UI: https://<IP>:8834

# Register for Nessus Essentials license
# Configure first scan
```

**Step 4: Apply Resource Limits**

Inside Nessus VM, create `/etc/systemd/system/nessusd.service.d/limits.conf`:
```ini
[Service]
MemoryMax=3.5G
CPUQuota=150%
Nice=10
```

Reload and restart:
```bash
systemctl daemon-reload
systemctl restart nessusd
```

**Step 5: Schedule Automatic Start/Stop**

On Proxmox host:
```bash
# Edit crontab
crontab -e

# Add scheduling
0 2 * * * /usr/sbin/qm start 101
0 6 * * * /usr/sbin/qm shutdown 101
```

### Phase 4: Monitoring and Optimization

**Step 1: Install Monitoring Tools**

On Proxmox host:
```bash
apt install glances htop iotop
```

**Step 2: Monitor Resources**
```bash
# Real-time monitoring
glances

# Or run web interface
glances -w --port 61208
# Access at http://<proxmox-ip>:61208

# Per-VM monitoring
qm status 100
qm status 101
```

**Step 3: Configure Alerts**

Create monitoring script (see **zimaboard-resource-allocation-guide.md** for full script).

**Step 4: Setup Backups**
```bash
# Automated daily backups
vzdump 100 101 --compress zstd --mode snapshot --storage local
```

---

## 🔧 Troubleshooting

### Home Assistant Issues

#### Container Won't Start
```bash
# Check logs
docker compose -f /opt/homeassistant/docker-compose.yml logs

# Check container status
docker ps -a

# Restart container
docker compose -f /opt/homeassistant/docker-compose.yml restart homeassistant
```

#### USB Device Not Detected
```bash
# Check device on host
lsusb
ls -l /dev/serial/by-id/

# Check LXC config
cat /etc/pve/lxc/100.conf

# Add device manually
echo "lxc.mount.entry: /dev/ttyUSB0 dev/ttyUSB0 none bind,optional,create=file" >> /etc/pve/lxc/100.conf

# Restart container
pct restart 100
```

#### Database Connection Failed
```bash
# Check MariaDB is running
docker ps | grep mariadb

# Test connection
docker exec -it homeassistant_mariadb mysql -u homeassistant -p -h localhost

# Check credentials in .env file
cat /opt/homeassistant/.env
```

### Nessus Issues

#### High Memory Usage
```bash
# Check VM resources
qm status 101

# Inside VM, check service
systemctl status nessusd

# Check memory limits are applied
systemctl show nessusd | grep Memory

# Restart service
systemctl restart nessusd
```

#### Scans Taking Too Long
- Reduce `max_hosts` to 3-5
- Enable scan throttling
- Use credentialed scans
- Disable unused plugin families
- See **nessus-deployment-guide.md** for tuning

#### VM Crashes System
```bash
# Reduce memory allocation
qm set 101 --memory 3072

# Lower CPU limit
qm set 101 --cpulimit 1.5

# Check OOM killer logs
dmesg | grep -i kill

# Emergency stop
qm stop 101
```

### System-Wide Issues

#### Out of Memory
```bash
# Check memory usage
free -h

# Identify memory hog
ps aux --sort=-%mem | head -20

# Stop non-critical VMs
qm stop <vmid>

# Clear cache (as last resort)
sync; echo 3 > /proc/sys/vm/drop_caches
```

#### High CPU Load
```bash
# Check CPU usage
htop

# Identify CPU hog
top -o %CPU

# Reduce Nessus CPU limit
qm set 101 --cpulimit 1.0
```

---

## 📖 Additional Resources

### Official Documentation
- [Home Assistant Documentation](https://www.home-assistant.io/docs/)
- [Tenable Nessus Documentation](https://docs.tenable.com/nessus/)
- [Proxmox VE Documentation](https://pve.proxmox.com/wiki/Main_Page)
- [Docker Documentation](https://docs.docker.com/)
- [Zimaboard Documentation](https://www.zimaboard.com/docs/)

### Community Resources
- [Home Assistant Community Forum](https://community.home-assistant.io/)
- [Proxmox Forum](https://forum.proxmox.com/)
- [Reddit r/homeassistant](https://www.reddit.com/r/homeassistant/)
- [Reddit r/homelab](https://www.reddit.com/r/homelab/)

### Key Topics from Research

#### Home Assistant
- **Container vs VM**: Container uses ~50% less resources
- **Supervisor Add-ons**: Only available in HA OS (VM) or Supervised
- **Docker equivalent**: Most add-ons have standard Docker containers
- **Network Mode**: Use `host` for device discovery
- **Database**: MariaDB recommended over SQLite for performance

#### Nessus
- **Essentials vs Professional**: Essentials limited to 16 IPs (recently 5-16)
- **Resource Requirements**: Minimum 2GB RAM, 4GB recommended
- **CPU Intensive**: Can use 100% CPU during scans
- **Resource Limiting**: Use systemd + cgroups + Proxmox limits
- **Scan Throttling**: Essential for small systems
- **Scheduling**: Run during off-hours to prevent interference

#### Resource Management
- **16GB Total**: 2GB Proxmox, 4GB HA, 4GB Nessus, ~6GB buffer
- **CPU Limits**: Prevent runaway processes
- **Memory Limits**: Hard caps prevent OOM crashes
- **Scheduling**: Time-based VM start/stop
- **Monitoring**: Essential for early problem detection

---

## 🎓 Best Practices Summary

### General
1. ✅ Start with minimal resource allocations
2. ✅ Monitor actively for first week
3. ✅ Enable resource limits on all services
4. ✅ Schedule resource-intensive tasks for off-hours
5. ✅ Maintain regular backups
6. ✅ Document all configuration changes
7. ✅ Test disaster recovery procedures

### Home Assistant
1. ✅ Use external database (MariaDB/PostgreSQL)
2. ✅ Enable recorder purging (7-14 days)
3. ✅ Use USB device by-id paths for stability
4. ✅ Disable ModemManager service
5. ✅ Exclude high-frequency sensors from recorder
6. ✅ Use host network mode for discovery

### Nessus
1. ✅ Deploy in VM (not LXC)
2. ✅ Enable all resource limits
3. ✅ Use credentialed scans when possible
4. ✅ Limit concurrent hosts to 3-5
5. ✅ Enable scan throttling
6. ✅ Schedule scans for 2-5 AM
7. ✅ Auto-stop VM after scan window

### Monitoring
1. ✅ Install Glances or similar monitoring
2. ✅ Set up resource usage alerts
3. ✅ Review logs weekly
4. ✅ Track resource trends over time
5. ✅ Adjust allocations based on actual usage

---

## 📝 Checklist

### Initial Deployment
- [ ] Proxmox installed and updated
- [ ] Network configured (static IP, firewall)
- [ ] Storage configured (local-lvm)
- [ ] LXC templates downloaded
- [ ] VM ISOs/images downloaded

### Home Assistant
- [ ] LXC container created
- [ ] Docker and Docker Compose installed
- [ ] USB devices configured
- [ ] docker-compose.yml deployed
- [ ] .env file customized (passwords changed)
- [ ] MariaDB initialized
- [ ] Mosquitto configured
- [ ] HA accessible at http://IP:8123
- [ ] Initial HA setup completed
- [ ] Integrations configured
- [ ] Resource usage monitored

### Nessus
- [ ] VM created with resource limits
- [ ] Nessus installed
- [ ] License activated
- [ ] systemd limits configured
- [ ] Scan policies created
- [ ] Scan throttling enabled
- [ ] Scheduling configured (cron)
- [ ] First scan completed successfully
- [ ] Resource usage monitored

### Operations
- [ ] Backup strategy implemented
- [ ] Monitoring tools installed
- [ ] Alert notifications configured
- [ ] Documentation updated
- [ ] Disaster recovery tested

---

## 🔗 Quick Reference

### Common Commands

```bash
# Proxmox
pvesh get /cluster/resources           # List all resources
qm list                                 # List VMs
pct list                                # List containers
qm start <vmid>                         # Start VM
pct start <ctid>                        # Start container

# Home Assistant (Docker)
cd /opt/homeassistant
docker compose up -d                    # Start
docker compose down                     # Stop
docker compose logs -f homeassistant    # View logs
docker compose restart                  # Restart all
docker compose pull && docker compose up -d  # Update

# Nessus
systemctl status nessusd                # Check status
systemctl restart nessusd               # Restart
/opt/nessus/sbin/nessuscli --help      # CLI help

# Monitoring
htop                                    # CPU/memory usage
iotop                                   # Disk I/O
free -h                                 # Memory usage
df -h                                   # Disk usage
```

### Important Paths

```bash
# Proxmox
/etc/pve/                               # Proxmox configs
/etc/pve/lxc/<ctid>.conf               # LXC config
/var/lib/vz/template/                  # Templates

# Home Assistant
/opt/homeassistant/                    # Base directory
/opt/homeassistant/homeassistant/config/  # HA config
/opt/homeassistant/.env                # Environment vars

# Nessus
/opt/nessus/                           # Nessus install
/opt/nessus/var/nessus/logs/          # Logs
/etc/systemd/system/nessusd.service.d/ # Service limits
```

---

## ✅ Success Criteria

Your deployment is successful when:

1. ✅ Home Assistant accessible and responsive
2. ✅ All integrations working (MQTT, database, USB devices)
3. ✅ Nessus scans complete without system impact
4. ✅ Total memory usage stays below 85%
5. ✅ Other services remain responsive during Nessus scans
6. ✅ No OOM killer events in logs
7. ✅ Automated backups running
8. ✅ System uptime >99%

---

## 🙏 Support

For questions or issues:
1. Review troubleshooting section in relevant guide
2. Check official documentation links
3. Search community forums
4. Review Proxmox/system logs

---

## 📄 License

This documentation is provided as-is for personal and educational use.

---

**Last Updated**: 2026-01-16
**Version**: 1.0
**Platform**: Zimaboard 16GB + Proxmox VE
**Services**: Home Assistant + Nessus

# Home Assistant Deployment Comparison for Proxmox/Zimaboard

## Overview
This guide compares different Home Assistant deployment methods on Proxmox, specifically for the Zimaboard 16GB platform.

---

## Deployment Options Summary

| Deployment Type | Supervisor/Add-ons | Resource Usage | Complexity | USB Passthrough | Recommended For |
|----------------|-------------------|----------------|------------|-----------------|-----------------|
| **Home Assistant OS (VM)** | ✅ Full support | High | Low | Easy | Beginners, full ecosystem |
| **Home Assistant Container** | ❌ No support | Low | Medium | Medium | Advanced users, Docker-centric |
| **Home Assistant Supervised** | ✅ Full support | Medium | High | Medium | Advanced users wanting add-ons |
| **HA Core (Python venv)** | ❌ No support | Very Low | Very High | Easy | Developers only |

---

## Option 1: Home Assistant OS (VM)

### Description
Full Home Assistant Operating System running in a QEMU/KVM virtual machine. This is the **recommended approach** for most users.

### Specifications
- **Base OS**: Custom Linux distribution
- **Includes**: Home Assistant Core + Supervisor + Add-ons store + OS management
- **Image Format**: QCOW2 for Proxmox

### Resource Requirements

| Resource | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| RAM | 2GB | 4GB | 2GB adequate for basic setups |
| CPU Cores | 2 | 2 | More cores don't significantly help |
| Storage | 32GB | 64GB | Grows with add-ons and database |
| Network | Bridge or Virtio | Virtio | Better performance |

### Pros
✅ **Complete ecosystem** - Full Supervisor and add-ons support
✅ **Easy updates** - One-click OS and core updates
✅ **Beginner-friendly** - Minimal Linux knowledge needed
✅ **USB passthrough** - Simple USB device mapping
✅ **Community support** - Most documentation assumes this method
✅ **Backup/restore** - Built-in snapshot functionality
✅ **Add-on store** - 100+ official and community add-ons

### Cons
❌ **Higher overhead** - Full VM with dedicated OS
❌ **Resource intensive** - Uses more RAM/CPU than containers
❌ **Less flexible** - Harder to customize underlying OS
❌ **Slower boot** - VM initialization takes longer

### Setup on Proxmox

```bash
# Download latest HAOS image
cd /var/lib/vz/template/iso/
wget https://github.com/home-assistant/operating-system/releases/download/12.0/haos_ova-12.0.qcow2.xz
unxz haos_ova-12.0.qcow2.xz

# Create VM (VMID 101)
qm create 101 \
  --name home-assistant \
  --memory 4096 \
  --cores 2 \
  --net0 virtio,bridge=vmbr0 \
  --agent 1 \
  --bios ovmf

# Import disk
qm importdisk 101 haos_ova-12.0.qcow2 local-lvm

# Configure disk
qm set 101 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-101-disk-0

# Add EFI disk
qm set 101 --efidisk0 local-lvm:1,format=raw,efitype=4m,pre-enrolled-keys=1

# Set boot order
qm set 101 --boot order=scsi0

# USB passthrough (adjust bus/port to match your device)
qm set 101 --usb0 host=10c4:ea60  # Example: SkyConnect Zigbee dongle

# Start VM
qm start 101
```

### USB Device Identification
```bash
# List USB devices
lsusb

# Find by-id path (more stable)
ls -l /dev/serial/by-id/

# Add persistent USB passthrough
qm set 101 --usb0 host=/dev/serial/by-id/usb-Silicon_Labs_Sonoff_Zigbee_3.0_USB_Dongle_Plus
```

### Initial Setup
1. Wait 5-10 minutes for first boot
2. Access UI: `http://homeassistant.local:8123` or `http://<IP>:8123`
3. Create admin account
4. Configure integrations and add-ons

---

## Option 2: Home Assistant Container (Docker)

### Description
Home Assistant Core running as a Docker container. **Best for resource-constrained systems** like Zimaboard 16GB.

### Specifications
- **Base**: Docker container on any Linux distribution
- **Includes**: Home Assistant Core only
- **Requires**: Separate containers for MQTT, database, etc.

### Resource Requirements

| Resource | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| RAM | 1GB | 2GB | Base container only |
| CPU Cores | 1 | 2 | Shared with other containers |
| Storage | 8GB | 16GB | Plus database storage |
| Host OS | Any | Debian/Ubuntu | Popular choices |

### Pros
✅ **Low overhead** - No VM layer, minimal resource usage
✅ **Fast startup** - Containers start in seconds
✅ **Flexible** - Easy integration with other Docker services
✅ **Efficient** - Better resource utilization on limited hardware
✅ **Portable** - Easy to migrate or backup
✅ **Composable** - Mix and match services via docker-compose
✅ **Resource limits** - Fine-grained control via Docker

### Cons
❌ **No Supervisor** - Cannot use add-ons from add-on store
❌ **Manual setup** - Must configure MQTT, databases, etc. separately
❌ **More complexity** - Requires Docker knowledge
❌ **USB passthrough** - Slightly more complex device mapping
❌ **Less documentation** - Most guides assume HAOS
❌ **No backup UI** - Must implement own backup strategy

### Setup on Proxmox LXC

#### Create LXC Container
```bash
# Create privileged LXC (needed for device access)
pct create 100 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname homeassistant \
  --memory 4096 \
  --cores 2 \
  --storage local-lvm \
  --rootfs local-lvm:16 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1,keyctl=1

# Allow device passthrough (add to LXC config file)
echo "lxc.cgroup2.devices.allow: c 188:* rwm" >> /etc/pve/lxc/100.conf
echo "lxc.mount.entry: /dev/ttyUSB0 dev/ttyUSB0 none bind,optional,create=file" >> /etc/pve/lxc/100.conf

# Start container
pct start 100
```

#### Install Docker in LXC
```bash
# Enter container
pct enter 100

# Update and install prerequisites
apt update && apt upgrade -y
apt install -y curl gnupg lsb-release

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
apt install -y docker-compose-plugin

# Enable Docker
systemctl enable docker
systemctl start docker
```

#### Deploy Home Assistant Stack
See the provided `home-assistant-docker-compose.yml` file.

```bash
# Create directory structure
mkdir -p /opt/homeassistant
cd /opt/homeassistant

# Copy docker-compose.yml to /opt/homeassistant/docker-compose.yml
# Copy .env.example to .env and customize

# Create directories
mkdir -p homeassistant/config mariadb/data mosquitto/{config,data,log}

# Copy mosquitto.conf to mosquitto/config/
cp /path/to/mosquitto.conf mosquitto/config/

# Start stack
docker compose up -d

# View logs
docker compose logs -f homeassistant
```

### USB Device Passthrough for Docker
```bash
# Find device
ls -l /dev/serial/by-id/

# Add to docker-compose.yml devices section:
devices:
  - /dev/serial/by-id/usb-Silicon_Labs_Sonoff:/dev/ttyUSB0
```

---

## Option 3: Home Assistant Supervised (Advanced)

### Description
Home Assistant Core + Supervisor on a generic Linux system. **Not recommended** due to complexity and support limitations.

### Specifications
- **Base OS**: Debian 12 only (officially supported)
- **Includes**: Core + Supervisor (add-ons supported)
- **Complexity**: High - strict requirements

### Resource Requirements
Similar to Container deployment but with Supervisor overhead.

### Pros
✅ **Add-on support** - Full add-on store access
✅ **Lower overhead** - No VM layer compared to HAOS
✅ **Flexibility** - Can run other services on host

### Cons
❌ **Unsupported** - Many configurations marked "unsupported"
❌ **Fragile** - OS updates can break installation
❌ **Complex** - Difficult to troubleshoot
❌ **Strict requirements** - Must use specific OS versions
❌ **Limited documentation** - Community support is limited

### When to Use
Only if you specifically need:
1. Supervisor/add-ons functionality
2. Without VM overhead
3. And are willing to handle complexity

**Recommendation**: Use HAOS VM instead unless you have specific needs.

---

## Supervisor and Add-ons Deep Dive

### What is the Supervisor?

The Supervisor is a management layer that:
- Manages Home Assistant Core updates
- Provides add-on store and installation
- Handles backups and snapshots
- Manages OS updates (in HAOS)
- Provides API for system management

### Add-ons vs Docker Containers

| Feature | Supervisor Add-ons | Docker Containers |
|---------|-------------------|-------------------|
| **Installation** | One-click from store | Manual docker-compose |
| **Updates** | Automatic via UI | Manual or Watchtower |
| **Configuration** | Web UI forms | YAML/env files |
| **Integration** | Automatic HA integration | Manual configuration |
| **Networking** | Supervisor managed | Manual network setup |
| **Resource limits** | Basic (via UI) | Advanced (cgroups) |

### Popular Add-ons and Docker Equivalents

| Add-on | Docker Container | Notes |
|--------|------------------|-------|
| **Mosquitto MQTT** | `eclipse-mosquitto:2.0` | Near identical |
| **MariaDB** | `mariadb:11.6` | Same, manual config needed |
| **Node-RED** | `nodered/node-red` | Same functionality |
| **ESPHome** | `esphome/esphome` | Same, manual setup |
| **File Editor** | N/A | Use SSH + nano/vim |
| **Samba Share** | `dperson/samba` | Manual SMB setup |
| **Zigbee2MQTT** | `koenkk/zigbee2mqtt` | Identical container |
| **VS Code** | `codercom/code-server` | Similar, not HA-specific |
| **AdGuard Home** | `adguard/adguardhome` | Same product |
| **Nginx Proxy** | `nginxproxy/nginx-proxy` | Same, manual config |

### Migrating from Add-ons to Docker

If switching from HAOS to Container:

1. **Export configurations** from add-ons
2. **Create docker-compose.yml** with equivalent services
3. **Import configurations** to new containers
4. **Update Home Assistant** integrations to point to new services
5. **Test thoroughly** before decommissioning HAOS

Example migration:
```yaml
# HAOS Add-on Config (Mosquitto)
logins:
  - username: homeassistant
    password: secret

# Becomes Docker Container
mosquitto:
  image: eclipse-mosquitto:2.0
  volumes:
    - ./mosquitto/config:/mosquitto/config
    - ./mosquitto/passwd:/mosquitto/passwd
```

---

## Integration with Other Services

### MQTT Broker Configuration

#### For HAOS VM
Install Mosquitto add-on from add-on store → Configure in add-on UI

#### For Docker Container
```yaml
# docker-compose.yml (already in provided file)
mosquitto:
  image: eclipse-mosquitto:2.0
  ports:
    - "1883:1883"
  volumes:
    - ./mosquitto/config:/mosquitto/config
```

Then in Home Assistant `configuration.yaml`:
```yaml
mqtt:
  broker: mosquitto  # Container name (if using host network: use IP)
  port: 1883
```

### Database Configuration (Recorder)

#### SQLite (Default)
- **Pros**: No setup, included
- **Cons**: Slow, not recommended for long-term use

#### MariaDB (Recommended)
- **Pros**: Fast, efficient, well-supported
- **Cons**: Requires separate service

#### PostgreSQL
- **Pros**: Advanced features, excellent performance
- **Cons**: More complex, higher resource usage

**Recommendation**: Use MariaDB for Zimaboard 16GB setup.

Configuration in `configuration.yaml`:
```yaml
recorder:
  db_url: mysql://homeassistant:password@mariadb:3306/homeassistant?charset=utf8mb4
  purge_keep_days: 7
  auto_purge: true
```

### Zigbee/Z-Wave Integration

#### Option 1: ZHA (Zigbee Home Automation) - Built-in
```yaml
# configuration.yaml
zha:
  usb_path: /dev/ttyUSB0
  database_path: /config/zigbee.db
```

No additional containers needed.

#### Option 2: Zigbee2MQTT - Separate Service
Requires MQTT broker + Zigbee2MQTT container.

**Pros**: More device support, active development
**Cons**: Additional service to manage

```yaml
# docker-compose.yml
zigbee2mqtt:
  image: koenkk/zigbee2mqtt
  devices:
    - /dev/ttyUSB0:/dev/ttyACM0
  volumes:
    - ./zigbee2mqtt/data:/app/data
  environment:
    - TZ=America/New_York
```

#### Option 3: Z-Wave JS - Recommended for Z-Wave
```yaml
# docker-compose.yml
zwave-js:
  image: zwavejs/zwavejs2mqtt
  devices:
    - /dev/ttyUSB1:/dev/ttyUSB1
  ports:
    - "8091:8091"
    - "3000:3000"
```

---

## Network Mode Considerations

### Host Network Mode (Recommended for HA)

```yaml
homeassistant:
  network_mode: host
```

**Pros**:
- ✅ Device discovery works (mDNS, UPnP)
- ✅ HomeKit integration works
- ✅ Chromecast discovery
- ✅ Simpler configuration

**Cons**:
- ❌ Less network isolation
- ❌ Port conflicts possible
- ❌ Cannot use custom networks

### Bridge Network Mode

```yaml
homeassistant:
  networks:
    - homeassistant
  ports:
    - "8123:8123"
```

**Pros**:
- ✅ Better isolation
- ✅ No port conflicts
- ✅ More secure

**Cons**:
- ❌ mDNS discovery broken (HomeKit, Chromecast)
- ❌ Requires avahi-daemon for discovery
- ❌ More complex setup

**Recommendation**: Use host mode unless you have specific security requirements.

### Hybrid Approach
Run HA in host mode, other services in bridge:

```yaml
services:
  homeassistant:
    network_mode: host

  mariadb:
    networks:
      - backend
    ports:
      - "3306:3306"

  mosquitto:
    networks:
      - backend
    ports:
      - "1883:1883"

networks:
  backend:
    driver: bridge
```

---

## Best Practices for Proxmox Deployment

### 1. VM Configuration (HAOS)

```bash
# Machine type: q35 (modern)
qm set 101 --machine q35

# BIOS: OVMF (UEFI)
qm set 101 --bios ovmf

# Network: VirtIO (best performance)
qm set 101 --net0 virtio,bridge=vmbr0

# Disk: VirtIO SCSI
qm set 101 --scsihw virtio-scsi-pci

# CPU type: host (best performance)
qm set 101 --cpu host

# Enable QEMU agent
qm set 101 --agent enabled=1
```

### 2. LXC Configuration (Container)

```bash
# Features
pct set 100 --features nesting=1,keyctl=1

# Memory with swap
pct set 100 --memory 4096 --swap 512

# Unprivileged vs Privileged
# Privileged needed for USB devices:
pct set 100 --unprivileged 0

# Startup order
pct set 100 --startup order=1,up=30
```

### 3. Storage Optimization

```bash
# Use separate storage for database
pct set 100 --mp0 /mnt/data,mp=/mnt/database

# Or add second disk to VM
qm set 101 --scsi1 local-lvm:32,format=raw
```

### 4. Backup Configuration

```bash
# Enable backup
qm set 101 --protection 1

# Schedule (via GUI or CLI)
vzdump 101 --compress zstd --mode snapshot --storage backup-storage
```

### 5. Resource Limits

```bash
# CPU limit (2 cores at 75% = 1.5 cores max)
qm set 101 --cores 2 --cpulimit 1.5

# CPU units (priority)
qm set 101 --cpuunits 2048  # Higher = more priority

# Memory balloon (disable for stability)
qm set 101 --balloon 0
```

---

## Recommendation Matrix

### Choose Home Assistant OS (VM) if:
- ✅ You want the simplest setup
- ✅ You need add-on support
- ✅ You're new to Home Assistant
- ✅ You have >4GB RAM available
- ✅ You don't need to run many other services

### Choose Home Assistant Container if:
- ✅ You're comfortable with Docker
- ✅ You want maximum resource efficiency
- ✅ You need to run multiple services (HAOS + Nessus on 16GB)
- ✅ You want fine-grained control
- ✅ You don't need add-ons

### For Zimaboard 16GB with Home Assistant + Nessus:
**Recommended**: Home Assistant Container (LXC)
- More efficient resource usage
- Allows 4GB for HA, 4GB for Nessus, 2GB for Proxmox
- Better co-existence with resource-intensive Nessus
- Still powerful and flexible

**Alternative**: Home Assistant OS (VM) if you need add-ons
- Allocate 4-6GB RAM
- Run Nessus in separate VM with 4GB
- Monitor resource usage closely
- Schedule Nessus for off-hours only

---

## Migration Paths

### From HAOS to Container

1. **Backup HAOS**: Settings → System → Backups → Create backup
2. **Download backup** to local machine
3. **Extract configuration**:
   ```bash
   tar -xzf backup.tar.gz
   # Extract configuration.yaml and other configs
   ```
4. **Deploy Container** using docker-compose
5. **Copy configurations** to container
6. **Migrate add-ons** to separate containers
7. **Test thoroughly** before retiring HAOS VM

### From Container to HAOS

1. **Backup** all container volumes
2. **Deploy HAOS VM**
3. **Complete initial setup**
4. **Copy `configuration.yaml`** and custom components
5. **Install add-ons** for services (MQTT, etc.)
6. **Restore automations** and UI configs
7. **Test all integrations**

---

## Troubleshooting Common Issues

### VM Won't Boot
- Check EFI disk is configured
- Verify boot order in VM options
- Try changing machine type to i440fx

### USB Passthrough Not Working
- Verify device ID: `lsusb`
- Check permissions in LXC config
- Try different USB port
- Disable modemmanager: `systemctl disable ModemManager`

### Discovery Not Working (Container)
- Use `network_mode: host`
- Check firewall rules
- Install avahi-daemon for mDNS

### Database Connection Failed
- Verify container names in network
- Check database credentials
- Ensure database container is running
- Test connection: `mysql -h mariadb -u homeassistant -p`

### High Memory Usage
- Enable recorder purging
- Reduce `purge_keep_days`
- Exclude high-frequency sensors
- Check for memory leaks in custom components

---

## Conclusion

For a **Zimaboard 16GB** running both Home Assistant and Nessus:

1. **Best approach**: Home Assistant Container in LXC
2. **Alternative**: Home Assistant OS in VM (if add-ons required)
3. **Key consideration**: Resource efficiency is critical
4. **Strategy**: Monitor usage, adjust allocations as needed
5. **Long-term**: Can always migrate between deployment types

Both methods are viable - choose based on your comfort level with Docker and whether you need the add-on ecosystem.

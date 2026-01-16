# Proxmox VE Networking Strategies for Zimaboard with 4-Port 2.5GbE PCIe Card

**Last Updated:** January 16, 2026
**Target Platform:** Zimaboard x86 with 16GB RAM, 4-port 2.5GbE PCIe Network Card
**Use Case:** Home lab with network monitoring, routing between multiple client devices

---

## Table of Contents

1. [Network Configuration Options](#1-network-configuration-options)
2. [Network Monitoring Solutions](#2-network-monitoring-solutions)
3. [Sample Configuration](#3-sample-configuration)
4. [Performance Considerations](#4-performance-considerations)
5. [Sources](#sources)

---

## 1. Network Configuration Options

### 1.1 Linux Bridge vs Open vSwitch (OVS)

#### **Current State (2025-2026)**

As of January 2026, the Proxmox community consensus strongly favors **Linux Bridge** for most use cases, including home labs with limited resources.

#### **Performance Comparison**

| Aspect | Linux Bridge | Open vSwitch (OVS) |
|--------|-------------|-------------------|
| **Throughput** | 40GB/s+ easily achievable | Same as Linux Bridge (without DPDK) |
| **CPU Usage** | Lower | Consistently higher |
| **Latency** | Lower (full kernel implementation) | Slightly higher (kernel + userspace daemon) |
| **DPDK Support** | No | Yes, but NOT implemented in Proxmox |
| **Stability** | Very stable, full kernel implementation | More buggy; if OVS service crashes, you lose network |

**Key Finding:** Performance should be the same until you use DPDK with OVS (not implemented in Proxmox). The only way for OVS to be faster than bridge is to use OVS-DPDK, which is mainly for packets per second, not bandwidth.

#### **Feature Comparison**

| Feature | Linux Bridge | Open vSwitch |
|---------|-------------|-------------|
| **Layer** | Layer 2 only | Layer 2 and Layer 3 |
| **VLAN Support** | Yes (basic) | Yes (advanced) |
| **QoS** | Limited | Full support |
| **Tunneling** | No | GRE, VXLAN, Geneve, MPLS |
| **Routing** | No | Yes (L3) |
| **Port Mirroring** | Basic (bridge_ageing 0) | Advanced (SPAN ports) |
| **NetFlow/sFlow** | No | Yes |
| **BGP** | No | Yes |

#### **Proxmox SDN Integration**

**Critical:** Proxmox SDN currently uses **Linux Bridge everywhere** in the background, supporting advanced features like BGP-EVPN, standard VXLAN, and standard BGP, working only with Linux Bridge.

#### **Recommendation for Zimaboard**

✅ **Use Linux Bridge** unless you need specific OVS features

**Reasons:**
- More stable and reliable (full kernel implementation)
- Lower CPU overhead (important for 16GB RAM constraint)
- Better supported by Proxmox SDN
- Simpler configuration and troubleshooting
- If you don't know why you need OVS, you probably don't need it

**When to use OVS:**
- You need advanced tunneling (GRE, VXLAN, Geneve)
- You require NetFlow/sFlow for traffic analysis
- You need VLAN support for host storage networking and VMs
- You want advanced QoS features

### 1.2 PCIe Network Card Passthrough vs Bridging

#### **Key Limitation: No True PCIe Passthrough for LXC**

**Important:** PCI-passthrough (including SR-IOV) is **not possible** with LXC containers. PCI passthrough allows you to use a physical PCI device inside a VM (KVM virtualization only).

#### **Why LXC is Different**

With NICs, true passthrough shouldn't be necessary, since the **host kernel is also the guest kernel**, so the device is shared by default. This is the key architectural difference - LXC containers share the Proxmox host's kernel, unlike VMs.

#### **Alternatives for LXC Containers**

##### **Option 1: Direct Physical NIC Assignment (Privileged Container)**

You can assign physical NICs directly to LXC containers, but the container must be **privileged**.

Edit the LXC config file (`/etc/pve/lxc/<VMID>.conf`):

```bash
lxc.net.1.type: phys
lxc.net.1.link: enp2s0
lxc.net.1.flags: up
lxc.net.1.hwaddr: 00:16:3e:xx:xx:xx
```

**Drawbacks:**
- Requires privileged container (security risk)
- Removes NIC from host and other VMs/containers
- Less flexible for sharing network resources

##### **Option 2: Linux Bridge (Recommended)**

Standard Linux bridging (vmbr) provides excellent performance with better flexibility for sharing network resources across multiple containers.

**Configuration:**
```bash
# In container config
net0: name=eth0,bridge=vmbr1,firewall=1,hwaddr=XX:XX:XX:XX:XX:XX,ip=dhcp,type=veth
```

**Advantages:**
- Works with unprivileged containers
- Minimal overhead due to shared kernel architecture
- Easy to share NICs across multiple containers/VMs
- Better security isolation

#### **Performance: Bridging vs Direct Assignment**

**Question:** Will adding a NIC as a standard Linux bridge to an LXC add any overhead to a 40Gbe/50Gbe connection?

**Answer:** The overhead is typically **minimal** for LXC containers due to the shared kernel architecture. Real-world testing shows 25-30Gbps VM-to-VM performance on the same Proxmox host using bridges.

#### **VMs vs LXC for Network Applications**

| Use Case | Recommended | Why |
|----------|-------------|-----|
| **Network Monitoring (ntopng, Zeek)** | LXC | Lower overhead, shared kernel |
| **Firewall/Router (OPNsense, pfSense)** | VM with PCIe Passthrough | Full hardware isolation, better driver support |
| **IDS/IPS (Suricata)** | Either | LXC for efficiency, VM for isolation |
| **Traffic Analysis** | LXC | Promiscuous mode works with bridges |

#### **Recommendation for Zimaboard 4-Port 2.5GbE Setup**

✅ **Use Linux Bridges for all ports** - create separate bridges (vmbr0-vmbr3) for the 4 PCIe NIC ports

**Reasons:**
- Maximum flexibility to route traffic between devices
- Easy to implement traffic mirroring for monitoring
- Lower resource overhead vs VM passthrough
- Can use both VMs and LXC containers as needed
- Better for creating a "managed switch" setup

### 1.3 Turning Proxmox into a Managed Switch

#### **Approach: Multiple Bridges with Inter-VLAN Routing**

Proxmox can function as a Layer 2/3 switch by:
1. Creating separate bridges for each physical port or VLAN
2. Enabling IP forwarding on the host
3. Assigning IP addresses to bridge interfaces
4. Configuring routing tables

#### **Configuration Steps**

##### **1. Enable IP Forwarding**

```bash
# Edit /etc/sysctl.conf
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1

# Apply changes
sysctl -p
```

##### **2. Create VLANs and Bridges**

```bash
# Example: Split trunk into VLANs with separate bridges
auto eno0.10
iface eno0.10 inet manual

auto vmbr10
iface vmbr10 inet static
    address 192.168.10.1/24
    bridge-ports eno0.10
    bridge-stp off
    bridge-fd 0

auto eno0.20
iface eno0.20 inet manual

auto vmbr20
iface vmbr20 inet static
    address 192.168.20.1/24
    bridge-ports eno0.20
    bridge-stp off
    bridge-fd 0
```

##### **3. Add Routing Rules (if needed)**

For policy-based routing between bridges:

```bash
# Add custom routing tables in /etc/iproute2/rt_tables
200 rt_vmbr1
201 rt_vmbr2

# Add routing rules
ip route add default via 192.168.1.1 dev vmbr1 table rt_vmbr1
ip route add default via 192.168.2.1 dev vmbr2 table rt_vmbr2
ip rule add from 192.168.1.0/24 table rt_vmbr1
ip rule add from 192.168.2.0/24 table rt_vmbr2
```

#### **Best Practices**

1. **Use VLANs** for logical separation while using fewer physical ports
2. **Disable STP** (`bridge-stp off`) unless you have network loops
3. **Set bridge_fd 0** to reduce latency from spanning tree protocol
4. **Consider a dedicated router VM** (OPNsense/pfSense) for advanced routing
5. **Document your VLAN scheme** clearly in `/etc/network/interfaces` comments

---

## 2. Network Monitoring Solutions

### 2.1 Tool Comparison: ntopng vs Zeek vs Suricata

#### **Purpose and Philosophy**

**Key Insight:** These tools serve **different purposes** and are often used **together** rather than as alternatives.

| Tool | Primary Purpose | Type | Detection Method |
|------|----------------|------|------------------|
| **ntopng** | Network visibility & traffic monitoring | Flow analyzer | NetFlow/packet inspection |
| **Suricata** | Real-time threat detection | IDS/IPS | Signature-based + anomaly |
| **Zeek** | Deep traffic analysis | IDS (passive) | Behavioral analysis + scripting |

#### **Detailed Comparison**

##### **ntopng - Network Visibility & Monitoring**

**What it does:**
- Network flow and traffic visualization
- Intuitive dashboards and usage analytics
- Real-time bandwidth monitoring
- Historical traffic analysis
- Basic anomaly detection

**What it lacks:**
- No signature-based attack detection
- No active prevention mechanisms (not a true IDS)
- Limited deep packet inspection

**Resource Usage:**
- **Minimum:** 2GB RAM, 1GHz processor, 10GB disk
- **Production:** 8GB+ RAM, multi-core processor, SSD storage
- CPU intensive during high traffic

**Best for:**
- Understanding who/what is using your network
- Bandwidth monitoring and capacity planning
- Identifying network bottlenecks
- Visualizing traffic patterns

##### **Suricata - Real-Time Threat Detection (IDS/IPS)**

**What it does:**
- Inspects traffic in real time
- Uses community and custom signatures to detect known threats
- Can actively block threats (IPS mode)
- Multi-threaded architecture for multi-core CPUs
- Supports rule-based detection

**Strengths:**
- **Best multi-threading:** Takes full advantage of multi-core CPUs
- Can run as IDS (passive) or IPS (active blocking)
- High-performance architecture
- Large community rule sets (ET Open, Snort rules)

**Resource Usage:**
- **Minimum:** 4-8GB RAM for basic deployment
- **Recommended:** 16GB+ RAM for modest rule sets
- **High-performance:** 32GB+ RAM for full rule sets
- Very CPU intensive - roughly 200Mbps per Suricata worker
- Memory-consuming when packet rate is high

**Best for:**
- Active threat detection and prevention
- Real-time security monitoring
- Multi-core systems (better than Snort/Zeek)
- Small to medium networks (< 1Gbps)

##### **Zeek (formerly Bro) - Deep Traffic Analysis**

**What it does:**
- Generates rich metadata and behavioral insights
- Creates detailed logs of network activity
- Identifies anomalies and suspicious patterns
- Passive approach (observation only)
- Highly scriptable and extensible

**Strengths:**
- Deep protocol analysis
- Powerful scripting framework
- Excellent for forensics and investigation
- Network behavior analysis

**Weaknesses:**
- CPU intensive and memory consuming
- High system load and packet loss at high packet rates
- Passive only (no IPS mode)
- Steeper learning curve

**Resource Usage:**
- Very CPU intensive
- High memory consumption
- Can cause packet loss on resource-constrained systems

**Best for:**
- Network forensics
- Behavioral analysis
- Research and advanced threat hunting
- Environments with dedicated analysis resources

### 2.2 Recommendation for 16GB RAM Zimaboard

#### **Primary Recommendation: Suricata + ntopng**

For a **16GB RAM home lab**, the optimal approach is:

**1. Start with Suricata alone** or **Suricata + ntopng**

**Rationale:**
- Suricata provides the best performance-to-resource ratio with multi-threading
- Handles both detection (IDS) and prevention (IPS)
- ntopng adds visualization without heavy IDS overhead
- Together they form a complete visibility solution

**2. Skip Zeek initially**

**Why:**
- Zeek is very resource-intensive for minimal benefit in a home lab
- Better suited for dedicated security operations centers
- Can be added later if needed for specific investigations

#### **Combined Approach: The Complete Stack**

If you have resources available:

```
ntopng → Visualization & Monitoring
Suricata → Threat Detection & Alerts
Zeek → Deep Context & Forensics
```

**Quote from research:** "Each tool serves a different purpose, but together they form a complete visibility solution - Suricata alerts you to active threats, Zeek reveals the context, and ntopng visualizes patterns and anomalies."

#### **Resource Allocation Strategy for 16GB RAM**

```
Proxmox Host: 4GB
Suricata (LXC): 4-6GB
ntopng (LXC): 2-3GB
Other VMs/Containers: 4-5GB
```

**Warning from real users:**
- "16GB RAM wasn't going to get them far and bumped it to 64GB when running OPNsense with IDS on Proxmox"
- "Suricata/darkstat/ntopng will use all available memory"

### 2.3 Deployment Methods: LXC vs VM vs Bare Metal

#### **ntopng Deployment**

##### **Option 1: LXC Container (Recommended)**

**Advantages:**
- Lower overhead than VM
- Easy to deploy (Docker in LXC or native)
- Good performance with shared kernel

**Challenges:**
- Must have access to Proxmox VE host bridges
- Requires bridge configuration (bridge acts as switch, not hub)

**Configuration:**
```bash
# Container must use bridge with promiscuous mode
# See Section 3.3 for detailed configuration
```

**Installation:**
```bash
# Debian/Ubuntu LXC container
apt update && apt install ntopng
systemctl enable ntopng
systemctl start ntopng
```

##### **Option 2: Docker Container in LXC**

```bash
docker run -d \
  --name ntopng \
  --net=host \
  --privileged \
  -v /var/lib/ntopng:/var/lib/ntopng \
  ntop/ntopng:stable \
  -i bridge=vmbr1
```

#### **Suricata Deployment**

##### **Option 1: LXC Container with SR-IOV VF (Advanced)**

For wirespeed performance, pass a SR-IOV VF to an LXC container.

**Note:** After changing `lxc.network.name` in vmid.conf, host reboot is required.

##### **Option 2: LXC Container with Promiscuous Bridge (Recommended)**

**Configuration:**
```bash
# In /etc/pve/lxc/<VMID>.conf
lxc.cgroup2.devices.allow: c 10:200 rwm
lxc.mount.entry: /dev/net dev/net none bind,create=dir

# Container must be privileged for raw socket access
unprivileged: 0
```

**Installation:**
```bash
# In container
apt update && apt install suricata suricata-update
suricata-update
systemctl enable suricata
systemctl start suricata
```

##### **Option 3: VM with Dedicated NIC (Maximum Isolation)**

Best for production or when you need hardware isolation.

**Passthrough configuration:**
1. Enable IOMMU in BIOS and GRUB
2. Pass specific NIC to VM
3. Install Suricata in VM

#### **Zeek Deployment**

##### **LXC Container (If Needed)**

Similar to Suricata setup but with more RAM allocation.

```bash
# Installation in Debian/Ubuntu container
apt update && apt install zeek
zeekctl deploy
```

#### **Deployment Comparison**

| Method | CPU Overhead | RAM Overhead | Isolation | Complexity |
|--------|-------------|-------------|-----------|------------|
| **Bare Metal** | Lowest | Lowest | None | Highest management |
| **LXC Container** | Very Low | Very Low | Medium | Low |
| **VM** | Medium | High | High | Medium |
| **Docker in LXC** | Low | Low | Medium | Low |

**Recommended for Zimaboard 16GB:**

```
ntopng:   LXC container (2-3GB RAM)
Suricata: LXC container (4-6GB RAM)
Zeek:     Only if absolutely needed (4-6GB RAM)
```

### 2.4 Configuration Examples for Traffic Monitoring

#### **Suricata Configuration**

##### **/etc/suricata/suricata.yaml**

```yaml
# Interface configuration for home network
af-packet:
  - interface: eth0
    threads: 4
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    use-mmap: yes
    tpacket-v3: yes

# Address groups for home network
vars:
  address-groups:
    HOME_NET: "[192.168.1.0/24,192.168.2.0/24]"
    EXTERNAL_NET: "!$HOME_NET"

# Performance tuning for limited resources
stream:
  memcap: 512mb
  max-sessions: 262144

# Enable rule categories
rule-files:
  - suricata.rules
```

#### **ntopng Configuration**

##### **/etc/ntopng/ntopng.conf**

```
# Interfaces to monitor
-i=vmbr1
-i=vmbr2
-i=vmbr3

# Web interface
-w=3000

# Data directory
-d=/var/lib/ntopng

# Local networks
--local-networks="192.168.1.0/24,192.168.2.0/24"

# DNS resolution
-m=192.168.1.1

# Enable historical data
--dump-flows=true

# Authentication
--disable-login=0
```

#### **Monitoring Multiple Devices**

To monitor traffic between Legion, Book, Sonos Beam, and external network:

**1. Create monitoring bridge with port mirroring**
```bash
# See Section 3.3 for detailed configuration
auto vmbr_monitor
iface vmbr_monitor inet manual
    bridge_ports dummy0
    bridge_stp off
    bridge_fd 0
    bridge_ageing 0
    post-up ip link set vmbr_monitor promisc on
```

**2. Configure Suricata to monitor all bridges**
```yaml
af-packet:
  - interface: vmbr1  # Client bridge
  - interface: vmbr2  # Server bridge
  - interface: vmbr3  # IoT bridge
```

**3. Configure ntopng for flow analysis**
```bash
ntopng -i vmbr1 -i vmbr2 -i vmbr3 --local-networks="192.168.1.0/24"
```

---

## 3. Sample Configuration

### 3.1 Overview: Zimaboard Network Topology

**Hardware:**
- Zimaboard onboard: 2x 2.5GbE (Intel chipsets)
- PCIe card: 4x 2.5GbE

**Devices to connect:**
- Legion (desktop/laptop)
- Book (laptop)
- Sonos Beam (IoT device)
- Uplink to external network/router

**Objective:**
- Route traffic between all devices
- Monitor all traffic for analysis
- Enable traffic mirroring for IDS/monitoring tools

### 3.2 Complete /etc/network/interfaces Configuration

```bash
# /etc/network/interfaces
# Proxmox VE Network Configuration
# Zimaboard with 4-port 2.5GbE PCIe Card
# Updated: 2026-01-16

# Loopback
auto lo
iface lo inet loopback

# ============================================================================
# PHYSICAL INTERFACES - Zimaboard Onboard NICs
# ============================================================================

# Onboard NIC 1 - Management Interface
auto eth0
iface eth0 inet manual

# Onboard NIC 2 - Uplink to External Router
auto eth1
iface eth1 inet manual

# ============================================================================
# PHYSICAL INTERFACES - PCIe 4-Port 2.5GbE Card
# ============================================================================
# Identify interface names with: ip link show
# Example names: enp1s0, enp2s0, enp3s0, enp4s0

# PCIe Port 1 - Client Network 1 (Legion)
auto enp1s0
iface enp1s0 inet manual

# PCIe Port 2 - Client Network 2 (Book)
auto enp2s0
iface enp2s0 inet manual

# PCIe Port 3 - IoT Network (Sonos Beam)
auto enp3s0
iface enp3s0 inet manual

# PCIe Port 4 - Monitor/Spare
auto enp4s0
iface enp4s0 inet manual

# ============================================================================
# BRIDGE 0 - Management Interface (Proxmox Access)
# ============================================================================

auto vmbr0
iface vmbr0 inet static
    # Proxmox management IP
    address 192.168.1.100/24
    gateway 192.168.1.1
    # DNS servers
    dns-nameservers 192.168.1.1 1.1.1.1
    # Bridge configuration
    bridge-ports eth0
    bridge-stp off
    bridge-fd 0
    # Optional: VLAN-aware bridge
    bridge-vlan-aware yes
    bridge-vids 2-4094
    # Disable filtering for better performance
    post-up echo 0 > /sys/class/net/vmbr0/bridge/multicast_snooping

    # Management network for VMs/containers
    # VMs on this bridge get DHCP from main router

# ============================================================================
# BRIDGE 1 - External Uplink
# ============================================================================

auto vmbr1
iface vmbr1 inet manual
    # Connected to main router/internet
    bridge-ports eth1
    bridge-stp off
    bridge-fd 0
    # Enable promiscuous mode for monitoring
    post-up ip link set vmbr1 promisc on
    post-up ip link set eth1 promisc on

    # This bridge connects to your main router
    # Firewall/router VM will use this as WAN interface

# ============================================================================
# BRIDGE 2 - Client Network 1 (Legion)
# ============================================================================

auto vmbr2
iface vmbr2 inet static
    # Subnet for Client Network 1
    address 192.168.10.1/24
    # Bridge configuration
    bridge-ports enp1s0
    bridge-stp off
    bridge-fd 0
    bridge-ageing 300
    # Enable for traffic monitoring
    post-up ip link set vmbr2 promisc on
    post-up ip link set enp1s0 promisc on

    # Legion device connects here
    # Proxmox will act as gateway: 192.168.10.1
    # DHCP range: 192.168.10.100-200 (configure in dnsmasq or DHCP server)

# ============================================================================
# BRIDGE 3 - Client Network 2 (Book)
# ============================================================================

auto vmbr3
iface vmbr3 inet static
    # Subnet for Client Network 2
    address 192.168.20.1/24
    # Bridge configuration
    bridge-ports enp2s0
    bridge-stp off
    bridge-fd 0
    bridge-ageing 300
    # Enable for traffic monitoring
    post-up ip link set vmbr3 promisc on
    post-up ip link set enp2s0 promisc on

    # Book device connects here
    # Proxmox will act as gateway: 192.168.20.1

# ============================================================================
# BRIDGE 4 - IoT Network (Sonos Beam)
# ============================================================================

auto vmbr4
iface vmbr4 inet static
    # Subnet for IoT devices
    address 192.168.30.1/24
    # Bridge configuration
    bridge-ports enp3s0
    bridge-stp off
    bridge-fd 0
    bridge-ageing 300
    # Enable for traffic monitoring
    post-up ip link set vmbr4 promisc on
    post-up ip link set enp3s0 promisc on

    # Sonos Beam connects here
    # Isolated from other networks (add firewall rules)

# ============================================================================
# BRIDGE 5 - Monitoring Mirror Interface
# ============================================================================

auto vmbr_monitor
iface vmbr_monitor inet manual
    # Create dummy interface for monitoring
    pre-up ip link add dummy0 type dummy 2>/dev/null || true
    # Bridge configuration for traffic mirroring
    bridge-ports dummy0
    bridge-stp off
    bridge-fd 0
    # KEY: Set ageing to 0 to mirror ALL traffic
    bridge-ageing 0
    # Enable promiscuous mode
    post-up ip link set vmbr_monitor promisc on
    post-up ip link set dummy0 promisc on

    # Cleanup on shutdown
    post-down ip link delete dummy0 type dummy 2>/dev/null || true

    # This bridge will receive mirrored traffic from other bridges
    # Attach monitoring VMs/containers (Suricata, ntopng, Zeek) here
    # Configure port mirroring with ovs-vsctl or tc commands

# ============================================================================
# IP FORWARDING AND ROUTING
# ============================================================================
# Configured in /etc/sysctl.conf:
# net.ipv4.ip_forward = 1
# net.ipv6.conf.all.forwarding = 1
#
# Apply with: sysctl -p
```

### 3.3 Traffic Mirroring Configuration

Traffic mirroring allows your monitoring tools to see all network traffic without being in-line.

#### **Method 1: Linux Bridge with bridge_ageing 0 (Simple)**

Already configured in `vmbr_monitor` above. This makes the bridge flood all traffic to all ports.

**How it works:**
- Set `bridge_ageing 0` - bridge never learns MAC addresses
- All traffic gets flooded to all ports (acts like a hub)
- Attach monitoring container to this bridge

**Attach monitoring tools:**

```bash
# For Suricata LXC (VMID 100)
pct set 100 -net1 name=eth1,bridge=vmbr_monitor,firewall=0

# For ntopng LXC (VMID 101)
pct set 101 -net1 name=eth1,bridge=vmbr_monitor,firewall=0
```

**To mirror traffic from other bridges to vmbr_monitor, use tc:**

```bash
#!/bin/bash
# /usr/local/bin/setup-port-mirror.sh

# Mirror traffic from vmbr2 (Legion) to vmbr_monitor
tc qdisc add dev vmbr2 ingress
tc filter add dev vmbr2 parent ffff: \
    protocol all \
    u32 match u8 0 0 \
    action mirred egress mirror dev vmbr_monitor

# Mirror traffic from vmbr3 (Book) to vmbr_monitor
tc qdisc add dev vmbr3 ingress
tc filter add dev vmbr3 parent ffff: \
    protocol all \
    u32 match u8 0 0 \
    action mirred egress mirror dev vmbr_monitor

# Mirror traffic from vmbr4 (IoT) to vmbr_monitor
tc qdisc add dev vmbr4 ingress
tc filter add dev vmbr4 parent ffff: \
    protocol all \
    u32 match u8 0 0 \
    action mirred egress mirror dev vmbr_monitor

echo "Port mirroring configured successfully"
```

**Make it persistent:**

```bash
chmod +x /usr/local/bin/setup-port-mirror.sh

# Add to crontab
crontab -e
# Add line:
@reboot /usr/local/bin/setup-port-mirror.sh
```

#### **Method 2: Open vSwitch with SPAN Ports (Advanced)**

If you switch to OVS, you can use proper SPAN port configuration:

```bash
# Install OVS
apt update && apt install openvswitch-switch

# Create OVS bridge
ovs-vsctl add-br ovs-vmbr1

# Add port mirroring
ovs-vsctl -- --id=@p get port tap100i0 \
    -- --id=@m create mirror name=span0 select-all=true output-port=@p \
    -- set bridge ovs-vmbr1 mirrors=@m
```

**Note:** OVS port mirrors do not survive reboot - requires hook scripts.

### 3.4 Firewall and Routing Rules

#### **Enable IP Forwarding**

```bash
# Edit /etc/sysctl.conf
cat >> /etc/sysctl.conf << 'EOF'

# Enable IP forwarding for routing between bridges
net.ipv4.ip_forward = 1
net.ipv6.conf.all.forwarding = 1

# Increase connection tracking table size
net.netfilter.nf_conntrack_max = 262144

# Optimize for low latency
net.ipv4.tcp_low_latency = 1
EOF

# Apply changes
sysctl -p
```

#### **Basic iptables Rules for Inter-Bridge Routing**

```bash
#!/bin/bash
# /usr/local/bin/proxmox-firewall-rules.sh

# Flush existing rules
iptables -F
iptables -t nat -F

# Default policies
iptables -P FORWARD DROP
iptables -P INPUT DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow Proxmox management
iptables -A INPUT -i vmbr0 -p tcp --dport 8006 -j ACCEPT
iptables -A INPUT -i vmbr0 -p tcp --dport 22 -j ACCEPT

# Allow inter-network routing
# Legion (vmbr2) can access Book (vmbr3)
iptables -A FORWARD -i vmbr2 -o vmbr3 -j ACCEPT
iptables -A FORWARD -i vmbr3 -o vmbr2 -j ACCEPT

# Legion can access external (vmbr1)
iptables -A FORWARD -i vmbr2 -o vmbr1 -j ACCEPT

# Book can access external
iptables -A FORWARD -i vmbr3 -o vmbr1 -j ACCEPT

# IoT (vmbr4) ISOLATED - only external access
iptables -A FORWARD -i vmbr4 -o vmbr1 -j ACCEPT
# Block IoT from accessing other internal networks
iptables -A FORWARD -i vmbr4 -o vmbr2 -j DROP
iptables -A FORWARD -i vmbr4 -o vmbr3 -j DROP

# NAT for outbound traffic
iptables -t nat -A POSTROUTING -o vmbr1 -j MASQUERADE

# Save rules
iptables-save > /etc/iptables/rules.v4

echo "Firewall rules applied successfully"
```

**Install and enable:**

```bash
# Install iptables-persistent
apt install iptables-persistent

# Make script executable
chmod +x /usr/local/bin/proxmox-firewall-rules.sh

# Run on boot
cat > /etc/systemd/system/proxmox-firewall.service << 'EOF'
[Unit]
Description=Proxmox Firewall Rules
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/proxmox-firewall-rules.sh
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable proxmox-firewall
systemctl start proxmox-firewall
```

### 3.5 DHCP Configuration (Optional)

If you want Proxmox to provide DHCP for client networks:

```bash
# Install dnsmasq
apt install dnsmasq

# Configure /etc/dnsmasq.conf
cat > /etc/dnsmasq.conf << 'EOF'
# Don't read /etc/resolv.conf
no-resolv

# Upstream DNS servers
server=1.1.1.1
server=8.8.8.8

# Legion network (vmbr2)
interface=vmbr2
dhcp-range=vmbr2,192.168.10.100,192.168.10.200,24h
dhcp-option=vmbr2,3,192.168.10.1   # Gateway
dhcp-option=vmbr2,6,192.168.10.1   # DNS

# Book network (vmbr3)
interface=vmbr3
dhcp-range=vmbr3,192.168.20.100,192.168.20.200,24h
dhcp-option=vmbr3,3,192.168.20.1
dhcp-option=vmbr3,6,192.168.20.1

# IoT network (vmbr4)
interface=vmbr4
dhcp-range=vmbr4,192.168.30.100,192.168.30.200,24h
dhcp-option=vmbr4,3,192.168.30.1
dhcp-option=vmbr4,6,192.168.30.1

# Static DHCP assignments
dhcp-host=XX:XX:XX:XX:XX:XX,legion,192.168.10.10
dhcp-host=YY:YY:YY:YY:YY:YY,book,192.168.20.10
dhcp-host=ZZ:ZZ:ZZ:ZZ:ZZ:ZZ,sonos-beam,192.168.30.10
EOF

# Enable and start
systemctl enable dnsmasq
systemctl start dnsmasq
```

---

## 4. Performance Considerations

### 4.1 CPU and RAM Overhead for Network Monitoring

#### **Real-World Resource Usage**

Based on 2025-2026 home lab experiences with limited resources:

| Configuration | RAM Usage | CPU Usage | Notes |
|---------------|-----------|-----------|-------|
| **Proxmox Host Only** | 2-4GB | 5-10% | Base overhead |
| **+ Suricata (basic rules)** | +4-6GB | +30-50% | Scales with traffic |
| **+ Suricata (full rules)** | +8-12GB | +50-80% | Can cause packet loss |
| **+ ntopng** | +2-3GB | +10-20% | Depends on flows |
| **+ Zeek** | +4-6GB | +40-60% | Very resource intensive |

#### **Recommendations for 16GB Zimaboard**

```
Total RAM: 16GB
├── Proxmox Host: 3-4GB
├── Suricata LXC: 4-6GB (limit rule sets)
├── ntopng LXC: 2-3GB
└── Remaining: 3-5GB for other VMs/containers
```

**Critical Warnings from Real Users:**

1. **"16GB RAM wasn't going to get them far"** - One user running OPNsense with IDS on Proxmox quickly bumped to 64GB

2. **"Suricata/darkstat/ntopng will use all available memory"** - These tools are aggressive memory consumers

3. **Packet loss at high traffic rates** - Zeek and Suricata cause "high system load and packet loss when the packet rate becomes high"

#### **Optimization Strategies for Limited Resources**

##### **For Suricata:**

```yaml
# /etc/suricata/suricata.yaml - Resource-constrained configuration

# Limit worker threads (don't exceed CPU cores)
threading:
  set-cpu-affinity: no
  cpu-affinity:
    - management-cpu-set:
        cpu: [ 0 ]
    - receive-cpu-set:
        cpu: [ 0, 1 ]
    - worker-cpu-set:
        cpu: [ 1, 2, 3 ]

# Reduce memory footprint
stream:
  memcap: 256mb              # Reduced from default 512mb
  max-sessions: 131072       # Half of default

# Limit flow tracking
flow:
  memcap: 128mb
  hash-size: 65536

# Disable features you don't need
app-layer:
  protocols:
    # Disable protocols you don't monitor
    krb5:
      enabled: no
    snmp:
      enabled: no
    ikev2:
      enabled: no

# Use limited rule sets
rule-files:
  - emerging-exploit.rules
  - emerging-malware.rules
  - emerging-scan.rules
  # Comment out heavy rule sets
  # - emerging-all.rules
```

**Estimated CPU usage:** ~200Mbps per Suricata worker thread

##### **For ntopng:**

```bash
# /etc/ntopng/ntopng.conf - Optimized for low resources

# Reduce historical data retention
--max-num-flows=32768
--max-num-hosts=2048

# Disable unnecessary features
--disable-aggregations
--disable-autologout

# Limit packet capture
--dump-flows=false

# Reduce memory usage
--shaping-max-mem=256
```

### 4.2 Latency Implications of Different Bridging Strategies

#### **Measured Performance**

Based on recent Proxmox community testing (2024-2025):

| Configuration | Throughput | Latency | CPU Overhead |
|--------------|------------|---------|--------------|
| **Direct connection** | Line rate | < 1ms | 0% |
| **Linux Bridge (basic)** | 25-30 Gbps | 1-2ms | 5-10% |
| **Linux Bridge (STP enabled)** | 25-30 Gbps | 3-5ms | 10-15% |
| **OVS Bridge** | 25-30 Gbps | 2-3ms | 15-20% |
| **Linux Bridge + Monitoring** | 20-25 Gbps | 2-4ms | 20-30% |

#### **Key Findings**

1. **STP introduces latency** - "The Spanning Tree Protocol (STP) is used to prevent network loops, but it can introduce latency, and disabling it can improve performance if your network doesn't have loops."

2. **Bridge performance is excellent** - Users achieved 25-30Gbps between VMs on the same Proxmox host using both Linux bridge and OVS configurations.

3. **MTU matters** - Increasing MTU to 9000 (Jumbo Frames) and multiqueue to 4 significantly improved performance.

4. **Bare metal is best** - "Bare metal Proxmox provides full, line-rate throughput (10/25Gbps+) and direct control over the physical NIC, Linux bridge, and kernel networking stack."

#### **Optimization for 2.5GbE Setup**

##### **1. Disable Spanning Tree Protocol**

```bash
# Already configured in sample config
bridge-stp off
```

**Impact:** Reduces latency by 1-2ms

##### **2. Set bridge_fd to 0**

```bash
bridge-fd 0
```

**Impact:** Eliminates forwarding delay

##### **3. Enable Jumbo Frames (if supported)**

```bash
# Edit /etc/network/interfaces for each interface
auto vmbr2
iface vmbr2 inet static
    address 192.168.10.1/24
    bridge-ports enp1s0
    bridge-stp off
    bridge-fd 0
    mtu 9000
    post-up ip link set enp1s0 mtu 9000
```

**Requirements:**
- All devices on the network must support MTU 9000
- Switches must support Jumbo Frames
- Can increase throughput and reduce CPU overhead

**Impact:**
- Increases packet size from 1500 bytes to 9000 bytes
- Reduces packet processing overhead
- Lowers CPU usage by 10-20%

##### **4. Disable Multicast Snooping**

```bash
# In bridge configuration
post-up echo 0 > /sys/class/net/vmbr2/bridge/multicast_snooping
```

**Impact:** Better performance, especially for streaming (Sonos)

##### **5. Enable Multi-Queue for Virtual NICs**

```bash
# For VMs in Proxmox GUI or config file
# /etc/pve/qemu-server/<VMID>.conf
net0: virtio=XX:XX:XX:XX:XX:XX,bridge=vmbr2,queues=4
```

**Impact:** Distributes NIC interrupts across multiple CPU cores

#### **Expected Performance for Zimaboard Setup**

##### **ZimaBoard 2 Network Specifications**

- Dual 2.5GbE onboard (Intel chipsets)
- "File transfers over the onboard 2.5GbE interfaces reached full saturation in controlled conditions"
- CPU and I/O subsystems capable of pushing maximum throughput

##### **Performance Targets**

With proper configuration:

| Scenario | Expected Throughput | Expected Latency |
|----------|-------------------|------------------|
| **Direct client-to-client** (e.g., Legion to Book) | 2.3-2.5 Gbps | < 2ms |
| **Client-to-external** (through NAT) | 2.3-2.5 Gbps | 2-3ms |
| **With Suricata IDS** | 1.8-2.2 Gbps | 3-5ms |
| **With full monitoring stack** | 1.5-2.0 Gbps | 5-10ms |

**Note:** Performance estimates assume:
- Properly configured Linux Bridges
- STP disabled
- Limited Suricata rule sets
- Adequate RAM allocation

### 4.3 Bottleneck Analysis

#### **Potential Bottlenecks in Order of Likelihood**

1. **RAM exhaustion** (16GB is tight for full stack)
2. **CPU limitations** (Suricata is CPU-bound)
3. **Packet processing** (high packet-per-second rates)
4. **Disk I/O** (logging for Suricata/Zeek/ntopng)

#### **Mitigation Strategies**

##### **1. RAM Management**

```bash
# Monitor RAM usage
watch -n 2 free -h

# Adjust container memory limits
pct set 100 -memory 4096    # Suricata: 4GB
pct set 101 -memory 2048    # ntopng: 2GB

# Enable swap (emergency only - will hurt performance)
```

##### **2. CPU Optimization**

```bash
# Pin containers to specific CPU cores
pct set 100 -cores 2

# Check CPU usage
htop

# Limit Suricata threads to match CPU cores
# In suricata.yaml: worker-cpu-set: cpu: [ 1, 2, 3 ]
```

##### **3. Disk I/O Optimization**

```bash
# Use SSD for logs if possible
# Limit log retention

# For Suricata - rotate logs frequently
# /etc/logrotate.d/suricata
/var/log/suricata/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
}

# For ntopng - limit historical data
--max-num-flows=32768
--max-num-hosts=2048
```

##### **4. Network Tuning**

```bash
# /etc/sysctl.conf - Network performance tuning

# Increase network buffer sizes
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.core.rmem_default = 16777216
net.core.wmem_default = 16777216
net.ipv4.tcp_rmem = 4096 87380 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864

# Increase connection tracking
net.netfilter.nf_conntrack_max = 262144

# Enable TCP optimizations
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_sack = 1

# Low latency
net.ipv4.tcp_low_latency = 1

# Apply
sysctl -p
```

### 4.4 Monitoring and Troubleshooting

#### **Performance Monitoring Tools**

```bash
# Network throughput
iftop -i vmbr2

# Packet statistics
watch -n 1 'cat /proc/net/dev'

# Bridge statistics
brctl show
brctl showmacs vmbr2

# Connection tracking
conntrack -L | wc -l
conntrack -S

# CPU per process
htop

# Network latency
ping -c 10 192.168.10.10
mtr 192.168.10.10
```

#### **Common Issues and Solutions**

| Issue | Symptom | Solution |
|-------|---------|----------|
| **High latency** | > 10ms between bridges | Disable STP, check CPU load |
| **Packet loss** | Dropped packets in ifconfig | Reduce Suricata rules, add RAM |
| **Low throughput** | < 1Gbps on 2.5GbE link | Check MTU, enable multi-queue |
| **CPU spikes** | 100% CPU usage | Limit Suricata threads, reduce monitoring |
| **RAM exhaustion** | OOM killer activated | Reduce container allocations, disable Zeek |
| **Network unreachable** | Can't ping between bridges | Check IP forwarding, iptables rules |

---

## Sources

### Network Configuration

- [Proxmox Forum: linux bridge vs ovs Bridge](https://forum.proxmox.com/threads/linux-bridge-vs-ovs-bridge.66320/)
- [Proxmox Forum: Questions about OVS vs Linux Bridge and VM Isolation](https://forum.proxmox.com/threads/questions-about-ovs-vs-linux-bridge-and-vm-isolation-in-proxmox.179272/)
- [NodeSpace Blog: Linux Bridge vs OVS Bridge](https://blog.nodespace.com/linux-bridge-vs-ovs-bridge/)
- [NetApp Community: Linux Bridge vs Open vSwitch for Proxmox VE](https://community.netapp.com/t5/Tech-ONTAP-Blogs/Linux-Bridge-vs-Open-vSwitch-for-Proxmox-VE/ba-p/465060)
- [IOFlood: Linux Bridge vs OpenVSwitch](https://ioflood.com/blog/linux-bridge-vs-openvswitch-how-to-improve-virtualization-network-performance/)

### PCIe Passthrough and LXC

- [Proxmox Forum: Can you passthrough a high-speed NIC to an LXC container?](https://forum.proxmox.com/threads/can-you-passthrough-a-high-speed-nic-to-an-lxc-container.70994/)
- [Netgate Forum: Linux Bridge vs. NIC Passthrough for VLANs](https://forum.netgate.com/topic/187156/linux-bridge-vs-nic-passthrough-for-vlans-in-proxmox-ve)
- [Proxmox Wiki: PCI(e) Passthrough](https://pve.proxmox.com/wiki/PCI(e)_Passthrough)
- [Propel RC: VM vs LXC in Proxmox: Performance, Use Cases & Setup Guide](https://www.propelrc.com/vm-vs-lxc-in-proxmox/)

### Network Monitoring Tools

- [Tolu Michael: Snort vs Suricata vs Zeek: Which Open-Source IDS is Best for 2025?](https://tolumichael.com/snort-vs-suricata-vs-zeek/)
- [ntop: Enabling Zeek and Suricata On-Demand at 40/100 Gbit using PF_RING](https://www.ntop.org/enabling-zeek-and-suricata-on-demand-at-40-100-gbit-using-pf_ring/)
- [ACK Security: Network Visibility with Suricata, Zeek, and ntopng](https://acksecurity.io/blog/first-post.html)
- [Tolu Michael: Zeek Vs Suricata: Everything About the Open-Source Tools](https://tolumichael.com/zeek-vs-suricata/)
- [Stamus Networks: Suricata vs Zeek](https://www.stamus-networks.com/suricata-vs-zeek)
- [ntop: Can ntopng be considered an IDS?](https://www.ntop.org/can-ntopng-be-considered-an-ids-intrusion-detection-system/)

### Deployment and Configuration

- [Proxmox Forum: NTOPNG on LXC Container](https://forum.proxmox.com/threads/ntopng-on-lxc-container.75673/)
- [XDA Developers: I monitor my home network by self-hosting ntopng](https://www.xda-developers.com/ntopng-guide/)
- [Virtualization Howto: Complete Guide to Proxmox Containers in 2025](https://www.virtualizationhowto.com/2025/11/complete-guide-to-proxmox-containers-in-2025-docker-vms-lxc-and-new-oci-support/)

### Traffic Mirroring and Port Monitoring

- [Proxmox Forum: how to let network traffic mirror to guest os using linux bridge](https://forum.proxmox.com/threads/how-to-let-network-traffic-mirror-to-guest-os-using-linux-bridge-port-mirroring-%EF%BC%9F.111334/)
- [Coding Packets: Proxmox VM Bridge Port Mirror](https://codingpackets.com/blog/proxmox-vm-bridge-port-mirror/)
- [Coding Packets: Proxmox Enable Port Mirror](https://codingpackets.com/blog/proxmox-enable-port-mirror/)
- [Medium: Mirroring multiple ports in Proxmox for network sniffing](https://medium.com/@mwc00941/mirroring-multiple-ports-in-proxmox-for-network-sniffing-487f329b7775)
- [Zanshi Dojo: Threat Hunting with SecurityOnion, Proxmox & Port Mirroring](https://blog.zanshindojo.org/securityonion-proxmox-port-mirroring/)
- [Trisul: Configuring a Port Mirror on Proxmox VE for Trisul NSM](https://www.trisul.org/devzone/doku.php/articles:proxmox_span)

### Inter-VLAN Routing and Multiple Bridges

- [Proxmox Wiki: Network Configuration](https://pve.proxmox.com/wiki/Network_Configuration)
- [Proxmox Forum: Proxmox networking and layer 3 routing](https://forum.proxmox.com/threads/proxmox-networking-and-layer-3-routing.129967/)
- [Proxmox Forum: Split VLAN Trunk into multiple Access Port Bridges](https://forum.proxmox.com/threads/split-vlan-trunk-into-multiple-access-port-bridges.131388/)
- [GetLabsDone: Steps to Create Proxmox Bridge with Multiple Ports using LACP bonding](https://getlabsdone.com/steps-to-create-proxmox-bridge-with-multiple-ports-using-lacp-bonding/)
- [Medium: Setting up ProxMox on a Trunk with multiple Interfaces](https://medium.com/@LDS_Cyber/setting-up-proxmox-in-a-trunk-with-multiple-interfaces-e5ed312cba45)
- [Proxmox Wiki: Open vSwitch](https://pve.proxmox.com/wiki/Open_vSwitch)

### Resource Usage and Performance

- [Security Onion Documentation: Hardware Requirements](https://docs.securityonion.net/en/2.4/hardware.html)
- [ntop Documentation: Hardware Sizing](https://www.ntop.org/guides/ntopng/performances/hardware_sizing.html)
- [ntop Support: System Requirements Guide](https://support.ntop.com/hc/en-us/articles/360061698333-System-Requirements-Guide)
- [ntop: Best Practices for Efficiently Running ntopng](https://www.ntop.org/best-practices-for-running-ntopng/)
- [Suricata: High Performance Configuration](https://redmine.openinfosecfoundation.org/projects/suricata/wiki/High_Performance_Configuration)
- [Netgate Forum: Hardware reqs for heavy Suricata](https://forum.netgate.com/topic/119802/hardware-reqs-for-heavy-suricata/)

### Proxmox Performance and Optimization

- [Blockbridge: Low Latency Storage Optimizations for Proxmox](https://kb.blockbridge.com/technote/proxmox-tuning-low-latency-storage/)
- [Atlantic.net: Optimizing Proxmox for Real-Time Workloads](https://www.atlantic.net/dedicated-server-hosting/proxmox-rtb-tuning-guide/)
- [Toxigon: Boost Your Proxmox Network Speed](https://toxigon.com/optimizing-proxmox-network-performance/)
- [Proxmox Forum: How to increase networking performance between 2 Linux VM's](https://forum.proxmox.com/threads/how-to-increase-networking-performance-between-2-linux-vms-on-the-same-host-bridge.153314/)

### Zimaboard-Specific

- [ZimaSpace Shop: ZimaBoard 2 Product Page](https://shop.zimaspace.com/products/zimaboard2-single-board-server)
- [ZimaSpace Blog: Configuring a Cluster in Proxmox with ZimaBoard SBC](https://www.zimaspace.com/blog/configuring-a-cluster-in-proxmox-with-zimaboard.html)
- [Flaviu Vlaicu: Zimaboard](https://vlaicu.io/posts/zimaboard/)
- [NAS Compares: Zimaboard 2 Review](https://nascompares.com/2025/05/16/zimaboard-2-review/)

### Proxmox Interface Configuration Examples

- [Proxmox Forum: single nic to multiple bridges](https://forum.proxmox.com/threads/single-nic-to-multiple-bridges.141546/)
- [Proxmox Forum: Setting up multiple nic Network and routing](https://forum.proxmox.com/threads/solved-setting-up-multiple-nic-network-and-routing-on-proxmox.81897/)
- [Intermittent Technology: Proxmox multi-NIC configuration](https://blog.quindorian.org/2025/05/proxmox-multi-nic-configuration.html/)

### Promiscuous Mode and Bridge Configuration

- [Proxmox Forum: Network Sensor (monitor session - promiscuous)](https://forum.proxmox.com/threads/network-sensor-monitor-session-promiscuous.37845/)
- [GitHub: Security Onion and Proxmox FYI on promisc setup](https://github.com/Security-Onion-Solutions/securityonion/discussions/8245)
- [Proxmox Forum: Promiscuous mode for VM](https://forum.proxmox.com/threads/promiscuous-mode-for-vm.84239/)
- [Proxmox Forum: Bridge ageing time not configurable](https://forum.proxmox.com/threads/bridge-ageing-time-not-configurable-brctl-setageing-bridge_ageing-0.27223/)

---

**Document Version:** 1.0
**Created:** 2026-01-16
**Author:** Research compiled from 2024-2026 sources
**Next Review:** 2026-04-16


# Keychron M7 8kHz Mouse Investigation Report

**Date:** January 17, 2026
**Device:** Keychron M7 (Ultra-Link 8K Receiver)
**OS:** macOS

## Issue Description
The user reported "jerky" mouse movement.

## Diagnosis
Investigation revealed the root cause to be a mismatch between the mouse's high polling rate (8000Hz) and macOS's system timer / event handling capabilities.

### Findings
1.  **Hardware Connection:** The Keychron Ultra-Link 8K receiver was detected and connected, though operating at USB 2.0 speeds in some contexts.
2.  **System Limitations:** 
    - `kern.clockrate` confirmed the system timer running at **100Hz**.
    - This creates a massive frequency mismatch with an 8000Hz input device (80x difference).
3.  **Resource Usage:** `WindowServer` showed elevated activity, a known symptom of high polling rate mice on macOS as the system struggles to process the flood of interrupt events.
4.  **Known Issue:** This is a documented limitation of macOS, which is not optimized for polling rates above 1kHz (1000Hz). 4kHz and 8kHz rates frequently cause stuttering, lag, and high CPU usage in `WindowServer`.

## Recommendations

### 1. Reduce Polling Rate (Primary Fix)
The most effective solution is to lower the polling rate to **1000Hz** or **500Hz**.
- **Action:** Use the Keychron web configurator ([launcher.keychron.com](https://launcher.keychron.com)) or installed software.
- **Why:** 1000Hz provides a smooth experience on macOS without overwhelming the event queue.

### 2. Lower DPI
If using 8kHz is mandatory (not recommended on macOS), lowering the DPI (e.g., to 800-1600) can mitigate some "jitter" perception, though it won't fix the underlying system bottleneck.

### 3. Connection Quality
Ensure the receiver is connected directly to the Mac or a high-quality powered hub, not a passive hub which might introduce further latency.

## Conclusion
The jerkiness is not a hardware defect but a system compatibility issue with 8kHz polling on macOS. Lowering the polling rate to 1000Hz is the standard resolution.

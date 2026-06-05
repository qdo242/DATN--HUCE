# 16-WEEK ROADMAP: IOT PAYLOAD ENCRYPTION PROJECT

This document is used to track the project's progress. Completed items are marked with [x].

---

## STAGE 1: RESEARCH AND FOUNDATION BUILDING (Weeks 1 - 4) - COMPLETED

- [x] Research on Application Layer Encryption (AES-128-CBC and XOR) as an alternative to lower-layer solutions.
- [x] Design the overall system architecture (Node X, Node Y, Gateway, Server).
- [x] Design an optimized binary packet structure for bandwidth efficiency.
- [x] Implement core encryption and decryption modules using Python.
- [x] Build a Flask Server supporting JSON and Hex string data reception.
- [x] Implement AES-128-CBC encryption on Xi node and decryption on Server.
- [x] Develop a basic monitoring Dashboard.

---

## STAGE 2: PROFESSIONALIZATION AND DATA MANAGEMENT (Weeks 5 - 8) - COMPLETED

### Week 5: Database Management and Device Management
- [x] Migrate storage from JSON files to SQLite Database.
- [x] Implement a device management table to assign unique keys to each IoT Node.
- [x] Upgrade the Dashboard with real-time data charts (Line Chart, Pie Chart).
- [x] Develop an end-to-end latency measurement module.

### Week 6: Security Analysis and Advanced Monitoring
- [x] Implement a detailed log table for attack attempts (attack type, timestamp).
- [x] Add Blacklist feature: Automatically block devices for violating security rules more than 3 times.
- [x] Display connection status and health of each Node on the Dashboard.

### Week 7: System Administration via Web Interface
- [x] Build a management interface for handling device lists and cryptographic keys (CRUD).
- [x] Integrate data export functionality (CSV/Excel) for analytical purposes.
- [ ] Implement an alert system via Email/Telegram for serious attack detection (API Keys pending).

### Week 8: Security Audit and System Stability
- [ ] Test the Flask Server's load capacity under continuous data reception.
- [ ] Optimize database queries to ensure processing speed.
- [ ] Document the successful prevention of various attack scenarios.

---

## STAGE 3: ADVANCED CRYPTOGRAPHY (Weeks 9 - 12)

### Weeks 9 - 10: Dynamic Key Exchange Protocol (ECDH)
- [ ] Research and implement the Elliptic Curve Diffie-Hellman (X25519) algorithm.
- [ ] Build a Handshake process for automatic session key agreement.
- [ ] Completely eliminate the use of static keys in communications.

### Weeks 11 - 12: Key Rotation and Forward Secrecy
- [ ] Implement an automatic Key Rotation mechanism (per session or per day).
- [ ] Verify the Perfect Forward Secrecy (PFS) property of the system.
- [ ] Develop a program for automatic cryptographic security evaluation.

---

## STAGE 4: HARDWARE INTEGRATION AND COMPLETION (Weeks 13 - 16)

### Weeks 13 - 14: C++ Firmware and ESP32 Optimization
- [ ] Write sample C++ source code for ESP32 using specialized cryptographic libraries.
- [ ] Utilize the AES hardware accelerator on the ESP32 chip for speed optimization.
- [ ] Implement a real-world communication scenario between two ESP32 devices via a Gateway.

### Week 15: Measurement and Experimental Analysis
- [ ] Measure RAM, Flash, and power consumption metrics on actual hardware.
- [ ] Experimentally compare performance with other standard security solutions.
- [ ] Synthesize comparison charts for the final report.

### Week 16: Final Report and Thesis Defense
- [ ] Finalize the content of the graduation thesis.
- [ ] Prepare the presentation slides and system demo video.
- [ ] Perform a final check of the entire system before the committee evaluation.

---
*Note: This roadmap will be updated continuously based on actual progress.*

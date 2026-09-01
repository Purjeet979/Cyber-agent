# 🛡️ Kalki: Comprehensive Technical Report

This document is a detailed, end-to-end explanation of **Kalki (Autonomous SOC Analyst Platform)**. It is designed to help you present the project to judges at the Smart India Hackathon (SIH), explaining every technical decision, agent behavior, and log detection capability.

---

## 1. 🎯 What is Kalki? (The Core Idea)
In traditional SOCs (Security Operations Centers), security analysts suffer from **Alert Fatigue**. They have to manually read thousands of raw network logs to figure out if an alert is a real attack or a false positive. 

**Kalki** solves this by replacing the Level-1 Human Analyst with **Agentic AI**. Kalki reads raw network logs, understands the context without hardcoded rules, correlates different events into a single "Incident", maps them to the MITRE ATT&CK framework, and generates actionable response reports.

---

## 2. 💻 Tech Stack
Kalki is built using a modern, lightweight, and scalable stack:
- **Backend Framework:** Python (Flask)
- **Frontend UI:** HTML5, CSS3 (Modern Glassmorphism), JavaScript
- **Real-Time Communication:** WebSockets (`flask-sock`) for instant, bi-directional live updates without page reloads.
- **AI Brain (LLM):** Groq API (Running Meta's Llama-3 model for lightning-fast inference)
- **Database:** SQLite (In-Memory for real-time demo performance)
- **Data Standard:** OCSF (Open Cybersecurity Schema Framework) for normalizing logs.
- **Endpoint Agent:** Native Windows Python scripts leveraging `ipconfig` and `urllib`.

---

## 3. 🤖 The Multi-Agent Architecture
Kalki does not rely on a single script. It uses a **Multi-Agent System**, where specialized AI agents handle different phases of the investigation:

### A. The Triage Agent (`src/kalki/triage/agent.py`)
- **What it does:** It acts as the frontline guard. Every single log that enters the system goes to the Triage Agent.
- **How it works:** It uses a specialized prompt to analyze the raw log text. It doesn't use Regex; it *reads* the log like a human. It assigns a **Verdict** (Suspicious or Benign) and generates a human-readable **AI Reasoning** (e.g., *"This log indicates an abnormal data exfiltration attempt..."*).
- **Auto-Closing:** If the agent marks a log as 'Benign', it is auto-closed to save the human analyst's time.

### B. The Investigation Agent (`src/kalki/investigate/agent.py`)
- **What it does:** It connects the dots. A single alert (like a failed login) isn't dangerous, but 10 failed logins followed by a successful login and a huge file download is an **APT (Advanced Persistent Threat)**.
- **How it works:** It scans the pool of 'Suspicious' alerts and correlates them based on **Time** and **Source IP**. It groups these alerts into a single **Incident** and maps the hacker's steps to the **MITRE ATT&CK Framework** (e.g., Reconnaissance → Initial Access → Lateral Movement).

### C. The Hunter & Response Agent (`src/kalki/hunt/` & `playbook/`)
- **What it does:** It acts as the Incident Responder.
- **How it works:** Once an Incident is created, this agent generates a **Remediation Playbook**. It tells the security team exactly what to do (e.g., "Isolate IP 192.168.1.55 on the internal VLAN", "Block domain trycloudflare.com on the firewall").

---

## 4. 📊 What Logs Does Kalki Detect? (Network Protocols)
Kalki is **Log-Agnostic** because of the AI. It doesn't rely on strict log formats. However, it specifically excels at detecting anomalies in these protocols:

1. **DNS (Domain Name System):**
   - **How it detects:** Kalki monitors DNS requests (like a user trying to visit `evil-phishing.com`). 
   - **What it catches:** Malware connecting to C2 (Command & Control) servers, DGA (Domain Generation Algorithms), and Phishing Tunnels (like Cloudflare Tunnels).

2. **HTTP/HTTPS (Web Traffic):**
   - **How it detects:** It analyzes proxy logs containing URL paths, HTTP Status Codes (200, 404, 500), and Payload Sizes.
   - **What it catches:** Drive-by malware downloads, SQL Injections in URL parameters, and massive Data Exfiltration (e.g., uploading 50GB to Mega.nz).

3. **TCP/UDP (Network Flow):**
   - **How it detects:** It looks at source/destination IPs and ports.
   - **What it catches:** Port Scanning (Nmap), DDoS attacks, and Lateral Movement (e.g., unauthorized RDP connections on Port 3389).

4. **Authentication Logs (Active Directory / Windows Events):**
   - **How it detects:** It monitors Windows Event IDs (like 4625 for Failed Logon).
   - **What it catches:** Brute-force password attacks, Pass-the-Hash, and Mimikatz credential dumping.

---

## 5. 📡 The Real-Time Endpoint Agent (`endpoint_agent.py`)
To prove that Kalki works in the real world (and not just with simulated data), we built a **Live Windows Endpoint Agent**.
- **The Concept:** Traditional SOCs use agents like Wazuh or CrowdStrike installed on laptops. Our script mimics this.
- **How it works:** It continuously reads the Windows OS DNS cache (`ipconfig /displaydns`).
- **The Flow:** 
  1. A user clicks a malicious link (e.g., Camphishing link hosted on a Cloudflare tunnel).
  2. The Windows OS resolves the domain and stores it in the DNS cache.
  3. The `endpoint_agent.py` detects the new entry, formats it into a raw log, and sends a POST request to Kalki's API (`/api/v1/alerts`).
  4. The **Triage Agent** instantly reads the log, flags the tunneling service as 'Medium/High' severity, and alerts the dashboard.

---

## 6. ⚡ The Real-Time Architecture (WebSockets)
A traditional dashboard requires the user to constantly refresh the page (or uses heavy AJAX polling) to see new alerts. Kalki is built for speed.
- **What it does:** The dashboard updates instantly the millisecond an attack is detected, without the user ever clicking "refresh".
- **How it does it (The Tech):** We implemented **WebSockets** using `flask-sock`. 
  1. When the dashboard loads, it opens a persistent WebSocket connection to the server (`/ws/alerts`).
  2. As soon as the `endpoint_agent.py` sends a new log and the Triage LLM finishes analyzing it, the backend pushes the JSON result directly through the active WebSocket channel.
  3. The JavaScript on the frontend intercepts this message and dynamically injects a new row into the Alert Feed table. This creates a true, live "hacker movie" feel during the demo.

---

## 7. 🏆 Why This Wins Hackathons (Your USP)
1. **Zero-Rule Engine:** Competitors use hardcoded `if-else` rules and Regex to find threats. Kalki uses **Cognitive AI (LLM)**. If a hacker slightly changes their attack pattern, rule-based systems fail. Kalki still catches it because it understands the *intent* of the log.
2. **Real-time Live Demo:** You aren't just showing a slideshow; you are clicking a live phishing link and showing the AI catching it within 3 seconds on a beautiful dashboard.
3. **Correlation over Alerting:** Kalki proves it understands enterprise security by prioritizing "Incidents" (Correlated Attacks) over spamming "Alerts", solving the biggest problem in the industry today.

---
*Created for the SIH Final Presentation.*

<div align="center">
  <h1>🛡️ Kalki</h1>
  <p><b>Autonomous SOC Analyst Platform</b></p>
  <p><i>Next-Generation Agentic AI for Cybersecurity Threat Detection & Response</i></p>
</div>

---

## 🎯 The Problem
Modern Security Operations Centers (SOCs) are overwhelmed with alert fatigue. Thousands of raw, uncontextualized logs are generated every minute by Firewalls, Proxies, and EDRs. Human analysts spend countless hours manually parsing logs, correlating IP addresses, and investigating false positives, which delays the response to real critical threats.

## 💡 Our Solution: Kalki
**Kalki** is an intelligent, autonomous SOC Analyst platform. Instead of just displaying logs, Kalki uses **Agentic AI (Groq Llama-3)** to act as a virtual Level-1/Level-2 SOC Analyst. It ingests raw logs, translates them into human-readable insights, correlates scattered alerts into full attack storylines (Incidents), and maps them to the MITRE ATT&CK framework—in real-time.

---

## 🤖 The AI Agents (How It Works)
Kalki relies on a multi-agent architecture where different AI models handle specific stages of the cybersecurity pipeline:

1. **The Triage Agent (`src/kalki/triage/`)** 
   - **Role:** The Frontline Defender.
   - **Action:** Ingests unstructured raw logs (Syslog, JSON, Windows Events). It uses the LLM to instantly evaluate the log, assign a Severity (Critical, High, Medium, Low), generate a clear `AI Reasoning`, and give a `Verdict` (Suspicious/Benign). Benign alerts are auto-closed to reduce noise.
   
2. **The Investigation Agent (`src/kalki/investigate/`)**
   - **Role:** The Detective.
   - **Action:** Continuously monitors the alert pool. When it sees multiple alerts from the same IP or targeting the same host within a timeframe, it groups them into a single **Incident**. It analyzes the sequence of events to construct a full **Kill Chain** and maps the behaviors to specific MITRE ATT&CK tactics (e.g., *Reconnaissance*, *Lateral Movement*).

3. **The Hunter/Response Agent (`src/kalki/hunt/` & `playbook/`)**
   - **Role:** The Responder.
   - **Action:** Generates a comprehensive Incident Report and dynamic Response Playbooks. It recommends exact remediation steps to the security admin (e.g., "Isolate host 192.168.1.55", "Block IP on perimeter firewall").

---

## 📡 Live Endpoint Monitoring (Real Setup)
We didn't just build a log analyzer; we built a real-time sensor. 
Included in this project is `endpoint_agent.py` — a lightweight **Windows Endpoint Agent**.
- **How it works:** It continuously monitors the Windows OS DNS cache (`ipconfig /displaydns`).
- **Detection:** The moment a user clicks a phishing link or hidden malware tries to contact a C2 server (e.g., Cloudflare Tunnels), the agent intercepts the DNS resolution and forwards the raw log to Kalki.
- **Result:** The Kalki Dashboard instantly flags the malicious DNS activity in real-time, proving end-to-end real-world detection capability.

---

## ✨ Key Features
- **Zero-Rule Engine:** No hardcoded regex rules for threat detection. The AI dynamically understands the context of the attack.
- **Smart Correlation:** Groups 100+ noisy alerts into 1 structured Incident.
- **OCSF Standardized:** Converts all ingested logs into the industry-standard Open Cybersecurity Schema Framework.
- **Glassmorphic 3D UI:** A stunning, futuristic, real-time dashboard built with vanilla CSS and JS.
- **Simulated & Live Modes:** Capable of running simulated Kill Chain demos and processing real live hardware traffic simultaneously.

---

## 🚀 Quick Start Guide

### 1. Installation
Clone the repository and set up a virtual environment:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

### 2. Environment Variables
Kalki uses Groq's lightning-fast inference for real-time AI processing.
```powershell
$env:GROQ_API_KEY="your_api_key_here"
$env:PYTHONIOENCODING="utf-8"
```

### 3. Launching the System
Start the main Dashboard server:
```powershell
kalki dashboard
```
Open your browser to `http://127.0.0.1:5000/`.

### 4. Testing the System
- **Simulation:** Click **"▶ Run Attack Simulation"** in the dashboard header to inject a multi-stage APT attack into the system.
- **Live Endpoint Test:** Start the live agent from the dashboard UI **"🔌 Live Agent: ON"**, then visit any phishing link (e.g., a Cloudflare tunnel) to see real-time detection.

---

## 🔮 Future Roadmap (Scaling Kalki)
- **Active Response (SOAR):** Integrating Python APIs to automatically apply Firewall rules or disable Active Directory accounts without human intervention.
- **Multi-OS Support:** Expanding the Endpoint Agent to support eBPF on Linux for kernel-level network tracing.
- **Local LLM Integration:** Supporting local models via Ollama to ensure complete data privacy for highly secure air-gapped environments.
- **Graph Database Correlation:** Moving from relational tables to Neo4j to visualize complex lateral movement paths across enterprise networks.

---
<div align="center">
  <p>Built with ❤️ for Smart India Hackathon</p>
</div>

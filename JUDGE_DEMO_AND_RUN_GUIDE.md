# National Helpline Against Atrocities (NHAA - 14566)
## Complete Presentation & Execution Guide for Judges

---

## 1. Quick Startup (3 Terminals on Your Laptop)

Open 3 PowerShell terminals on your laptop:

### Terminal 1: Backend Server (FastAPI + AI Triage Engine)
```powershell
cd D:\sih2026\dosje-clone\backend
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```
> Verified: Server runs on `http://localhost:8000`.

---

### Terminal 2: Frontend Government Command Portal
```powershell
cd D:\sih2026\dosje-clone
npm run dev
```
> Open in Chrome:
> - **Operator Desk (Level 0)**: `http://localhost:5173/#/admin/operator`
> - **DSP Command Desk (Level 1)**: `http://localhost:5173/#/admin/dsp`
> - **SP State Command (Level 2)**: `http://localhost:5173/#/admin/sp`
> - **National Ministry (Level 3)**: `http://localhost:5173/#/admin/ig`

*(Default demo login: Username `dsp` or `operator`, Password `Test@1234`)*

---

### Terminal 3: Cloudflare Telephony Tunnel (Only needed for phone calls)
```powershell
D:\sih2026\cloudflared.exe tunnel --protocol http2 --url http://localhost:8000
```
> Within 5 seconds, Cloudflare prints a box with your live link:
> `https://<random-name>.trycloudflare.com`
> 
> Copy that link and append `/twilio/voice`. Example:
> `https://combine-over-cashiers-delete.trycloudflare.com/twilio/voice`

---

## 2. Live Phone Call Workflow (Primary Demo)

If you want to amaze the judges with a **live phone call**:

1. Open **Twilio Console** &rarr; **Try out Voice** &rarr; **Outbound**.
2. Set **To**: Your verified phone number (`+917898585900`).
3. Set **From**: Twilio number (`+17372508034`).
4. Select **Custom** &rarr; Paste your tunnel URL + `/twilio/voice`:
   ```
   https://combine-over-cashiers-delete.trycloudflare.com/twilio/voice
   ```
5. Click **Call**:
   - **Press 2** for Hindi.
   - **Press 1** for Peedit / Victim.
   - Speak your complaint clearly (e.g. *"Mera naam Ramesh hai. Hamare parivaar par dandon se hamla hua aur police ne FIR nahi likhi..."*).
   - **Press `#`** on your keypad when done speaking.
   - Listen to the spoken Hindi confirmation: *"Dhanyavaad. Aapki shikayat safaltapoorvak darj kar li gayi hai..."*
   - Hang up.
6. Look at your dashboard on screen &mdash; **the case instantly appears at the top**!
7. Click **Examine**: Show judges the **Transcribed Voice Statement**, **SVI Score (86.46)**, and **Extracted POA Atrocity Flags**.

---

## 3. FAIL-SAFE BACKUP PLANS (If WiFi / Cloud Tunnel Fails)

Judges' venues often have strict firewalls, slow WiFi, or Cloudflare blocks. **Do not panic &mdash; use these 2 instant backups:**

### Backup 1: The Instant 1-Click AI Test Run (No Phone / No Tunnel Needed!)
If the tunnel drops or you have zero internet, run this single PowerShell command in a new terminal:
```powershell
cd D:\sih2026\dosje-clone\backend
.venv\Scripts\python.exe -c "import requests; r = requests.post('http://127.0.0.1:8000/calls/test-auto'); print(r.json())"
```
**What happens instantly:**
- The backend runs 3 multi-lingual distress complaints (Hindi, English, and Marathi).
- Triggers the SVI perception layer and legal classification.
- Saves the cases to PostgreSQL and broadcasts them live via WebSocket directly onto the dashboard in front of the judges!

### Backup 2: Restore Benchmark Demonstration Cases
On the **Operator Desk** (`http://localhost:5173/#/admin/operator`):
- Click the blue **"Restore demo data"** button in the top-right corner.
- Instantly re-seeds a complete hierarchy of benchmark cases (`NHAA-1001` through `NHAA-1008`) covering Physical Violence, Denial of Water, Social Boycott, and Silent Distress SOS signals.

---

## 4. Winning Presentation Pitch to the Judges (2-Minute Script)

### Step 1: The Problem (30 seconds)
> *"Honorable Judges, currently over 50,000 SC/ST atrocity grievances are reported annually across India under the POA Act. However, victims facing violence in rural areas often face police refusal to file FIRs, language barriers, and critical delays in distress triage. Victims need an immediate, toll-free voice intake that cannot be silenced."*

### Step 2: Our Innovation (45 seconds)
> *"We built the next-generation National Helpline Against Atrocities (NHAA - 14566) featuring:*
> 1. **Multi-Lingual Voice Intake (IVRS)**: Callers can speak naturally in Hindi, Marathi, or English.
> 2. **AI Severity Vulnerability Index (SVI)**: Rather than simple keyword matching, our Perception Engine analyzes trauma, violence indicators, and police non-compliance to calculate a continuous SVI vulnerability score (0 to 100).
> 3. **Automated Legal Escalation**: High SVI cases (>70) automatically bypass operator queues directly to District DSPs and SPs with strict statutory SLAs under the SC/ST POA Rules."*

### Step 3: The Live Demonstration (45 seconds)
> 1. *"Show the live roster table: Notice our recent IVRS calls at the top with timestamp `04 Sep 2026`."*
> 2. *"Click **Examine** on Case 20 / Case 19: Point to the **Recorded Grievance Statement / Transcribed Speech** box. Show them that the victim's spoken Hindi was accurately captured and tagged with Legal Flags (Physical Violence, Section 4 Police Refusal)."*
> 3. *"Click **Take Ownership** or **Escalate to SP**: Demonstrate multi-level police accountability (Operator L-0 &rarr; DSP L-1 &rarr; SP L-2)."*
> 4. *"Highlight NIC GIGW Compliance: Zero cartoonish styling, formal Government of India light theme, dual Indian emblem, and full audit trail."*

---

## 5. Summary of Test Credentials

| Role | Username | Password | Jurisdiction |
| :--- | :--- | :--- | :--- |
| **L-0 Operator** | `operator` | `Test@1234` | Central Delhi |
| **L-1 DSP (District)** | `dsp` | `Test@1234` | Central Delhi |
| **L-2 SP (State)** | `sp` | `Test@1234` | Delhi State |
| **L-3 IG (Ministry)** | `ig` | `Test@1234` | National Command |

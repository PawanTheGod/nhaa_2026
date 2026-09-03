# NHAA Voice Call - Twilio Setup (For India)

## What's already done (no setup needed)
- `backend/app/routes/twilio_webhook.py` - Twilio webhook (POST /twilio/voice + WebSocket /twilio/stream)
- `backend/app/services/calls/orchestrator.py` - text -> AI flags -> auto-create case
- `backend/app/services/stt/deepgram_client.py` - live audio transcription
- `backend/.env` - DEEPGRAM_API_KEY and OPENROUTER_API_KEY already filled

## What you need from Twilio (free trial = $15.50 credit, enough for ~150 mins of calls)

### Step 1: Sign up (2 min)
1. Go to https://www.twilio.com/try-twilio
2. Click "Start free trial"
3. Use your Indian phone number
4. Verify with OTP
5. They'll ask "what are you building?" - say: "Government helpline callback system, voice intake for victims"

### Step 2: Get a US number (1 min, free from $15 credit)
1. Twilio Console home -> "Phone Numbers" -> "Manage" -> "Buy a number"
2. Country: **United States** (cheapest to receive, and any Indian phone can call it)
3. Capabilities: check **Voice**
4. Click "Search"
5. Pick any number (cost: $1.15/month, comes out of free credit)
6. Click "Buy" - done

### Step 3: Copy 3 things from Twilio console to your `.env`
Open https://console.twilio.com -> top right shows your **Account SID** and **Auth Token** (click to reveal).
The phone number you just bought is in: Phone Numbers -> Manage -> Active numbers.

Open `backend/.env` and fill these 3 lines (replace empty values):
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
```

### Step 4: Expose your local backend to the internet (3 min)
Twilio's webhook can't reach `http://127.0.0.1:8000` on your laptop. You need a public URL.

**Option A: ngrok (recommended)**
1. Go to https://ngrok.com/download
2. Download the Windows version, unzip, you'll get `ngrok.exe`
3. Open PowerShell, run: `ngrok config add-authtoken YOUR_TOKEN` (get free token from https://dashboard.ngrok.com/get-started/your-authtoken)
4. Start tunnel: `ngrok http 8000`
5. You'll see output like: `Forwarding https://abc-123.ngrok-free.app -> http://localhost:8000`
6. Copy that `https://abc-123.ngrok-free.app` URL - this is your public URL

**Option B: Cloudflare Tunnel (no signup needed)**
1. Download from https://github.com/cloudflare/cloudflared/releases/latest (Windows amd64)
2. Run: `cloudflared tunnel --url http://localhost:8000`
3. Copy the `https://...trycloudflare.com` URL

### Step 5: Tell Twilio where to send calls
1. Twilio Console -> Phone Numbers -> Manage -> Active numbers
2. Click your number
3. Scroll to "Voice & Fax" section
4. Under "A CALL COMES IN" select **Webhook**
5. URL: `https://your-ngrok-url/twilio/voice` (use your actual URL from Step 4)
6. HTTP: **POST**
7. Click **Save**

### Step 6: Test it
1. Make sure backend is running: `cd backend && .venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Make sure ngrok is running: `ngrok http 8000`
3. From ANY phone (your Indian mobile, your friend's phone, anything), dial the US number you bought
4. Twilio answers, plays greeting in Hindi+English
5. Speak your complaint in Hindi/English/Tamil/etc
6. Hang up
7. The case auto-creates in your Supabase DB within 5 seconds
8. Open the operator dashboard at `/#/admin/operator` - the new case appears LIVE

## Test without making a real call (always works, no Twilio signup)
```powershell
# 1. Start backend
cd D:\sih2026\dosje-clone\backend
.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 2. In another PowerShell, run the auto-test (feeds 2 pre-baked Hindi complaints through the full pipeline)
$body = '{"transcript": "Mere gaon mein Dalit parivar par attack hua, police ne FIR nahi li"}'
Invoke-WebRequest -Uri "http://127.0.0.1:8000/calls/transcript" -Method POST -ContentType "application/json" -Body $body

# OR even simpler - runs 2 realistic test cases automatically
Invoke-WebRequest -Uri "http://127.0.0.1:8000/calls/test-auto" -Method POST
```

## Cost breakdown (for SIH demo)
| Item | Cost | Source |
|---|---|---|
| Twilio free trial credit | $15.50 | free on signup |
| US number (1 month) | $1.15 | from credit |
| Inbound call (per minute) | $0.0085/min | from credit |
| 10 test calls of 2 mins each | $0.17 | from credit |
| **Total demo cost** | **$1.32** | **fits in free credit** |
| After trial ends | $1.15/month + per-min | pay-as-you-go |

## What happens during a call (full pipeline)
```
1. You dial +1-xxx-xxx-xxxx from your Indian phone
2. Twilio answers, plays greeting in Hindi
3. You speak: "Mere gaon mein Dalit parivar par attack hua"
4. Twilio streams audio to your backend (via WebSocket)
5. Deepgram converts audio to text
6. Text goes to OpenRouter LLM (free Llama-3)
7. LLM extracts: { physical_violence, police_complicity, social_exclusion }
8. Aatmman's engine computes: tier=critical, svi=87
9. Case auto-creates in Supabase DB
10. WebSocket pushes to operator dashboard
11. Operator sees it appear in 2-5 seconds
12. Officer clicks "Confirm Notifications" -> agencies get SMS/email
13. Backend speaks back to you via TwiML:
    "Aapka case NHAA-2026-XXX register ho gaya hai.
     District officer ko bhej diya gaya hai."
```

## Time estimate for full setup
- Twilio signup + US number: **5 min**
- ngrok install: **3 min** (or use cloudflared, no signup)
- Twilio webhook config: **2 min**
- Test call: **2 min**
- **Total: 12 minutes**

## Free alternatives to Twilio (if you don't want to sign up)
- **Retell AI** (https://retell.ai) - 10 mins free, gives you a US number, built-in STT/TTS
- **Vapi** (https://vapi.ai) - 10 mins free
- Both work the same way: sign up, buy/get a number, set webhook URL, call

Tell me when you've signed up and I'll add the credentials and run the test.

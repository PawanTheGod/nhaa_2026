import os
import httpx
from dotenv import load_dotenv

load_dotenv('.env')
sid = os.getenv('TWILIO_ACCOUNT_SID')
token = os.getenv('TWILIO_AUTH_TOKEN')
url = 'https://promoted-rpm-tim-marsh.trycloudflare.com/twilio/voice'

print(f"Connecting to Twilio with SID: {sid}")

client = httpx.Client(auth=(sid, token), timeout=15.0)
r = client.get(f'https://api.twilio.com/2010-04-01/Accounts/{sid}/IncomingPhoneNumbers.json')

if r.status_code != 200:
    print(f"Failed to list numbers: {r.status_code} {r.text}")
    exit(1)

data = r.json()
numbers = data.get('incoming_phone_numbers', [])
print(f"Found {len(numbers)} numbers")

for p in numbers:
    pn_sid = p['sid']
    pn_num = p['phone_number']
    print(f"Updating {pn_num} (SID: {pn_sid})...")
    update_r = client.post(
        f'https://api.twilio.com/2010-04-01/Accounts/{sid}/IncomingPhoneNumbers/{pn_sid}.json',
        data={'VoiceUrl': url, 'VoiceMethod': 'POST'}
    )
    if update_r.status_code == 200:
        print(f"SUCCESS: {pn_num} VoiceUrl set to {url}")
    else:
        print(f"FAILED to update {pn_num}: {update_r.status_code} {update_r.text}")

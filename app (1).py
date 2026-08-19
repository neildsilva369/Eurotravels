
import streamlit as st
from pathlib import Path
from datetime import date
import requests
import pandas as pd

st.set_page_config(page_title="EuroVoyage", page_icon="✦", layout="wide")

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "trips.csv"

# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,500&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

.stApp{
  --ink:#060b14; --ink2:#0d1728; --panel:#101d33; --panel2:#0a1524;
  --border:#25405f; --brass:#d7a34e; --brass-bright:#f2c877; --teal:#56d6b0;
  --text:#edf2f8; --muted:#8ba0b7;
  background:
    radial-gradient(circle at 12% -8%, #1c3a5e 0%, transparent 42%),
    radial-gradient(circle at 90% 10%, #17304e 0%, transparent 30%),
    radial-gradient(1px 1px at 20% 15%, rgba(242,200,119,.35) 0, transparent 60%),
    radial-gradient(1px 1px at 65% 8%, rgba(242,200,119,.25) 0, transparent 60%),
    radial-gradient(1px 1px at 85% 35%, rgba(86,214,176,.3) 0, transparent 60%),
    radial-gradient(1px 1px at 35% 60%, rgba(242,200,119,.2) 0, transparent 60%),
    radial-gradient(1px 1px at 10% 80%, rgba(86,214,176,.2) 0, transparent 60%),
    repeating-linear-gradient(90deg, rgba(255,255,255,.015) 0 1px, transparent 1px 64px),
    repeating-linear-gradient(0deg, rgba(255,255,255,.015) 0 1px, transparent 1px 64px),
    linear-gradient(160deg, var(--ink) 0%, var(--ink2) 55%, #05090f 100%);
  color:var(--text);
  font-family:'IBM Plex Sans',sans-serif;
}
.block-container{max-width:1250px;padding-top:2rem}

/* Animated flight-path scene */
.skyline{position:relative;height:64px;margin:6px 0 8px;overflow:hidden}
.flight-path{position:absolute;left:0;top:50%;width:100%;height:0;border-top:1.5px dashed rgba(215,163,78,.3)}
.plane-icon{position:absolute;top:50%;left:-8%;transform:translateY(-50%);animation:flypast 16s linear infinite;filter:drop-shadow(0 0 6px rgba(242,200,119,.5))}
@keyframes flypast{
  0%{left:-8%; top:60%}
  25%{top:35%}
  50%{top:55%}
  75%{top:30%}
  100%{left:108%; top:45%}
}

/* Animated transit strip (train + bus) */
.transit-strip{position:relative;height:46px;margin:34px 0 6px}
.rail-line{position:absolute;left:0;top:14px;width:100%;height:3px;background:repeating-linear-gradient(90deg, var(--border) 0 10px, transparent 10px 20px)}
.train-icon{position:absolute;top:-4px;animation:trainmove 11s linear infinite}
@keyframes trainmove{0%{left:-6%}100%{left:104%}}
.road-line{position:absolute;left:0;top:38px;width:100%;height:2px;background:repeating-linear-gradient(90deg, var(--brass) 0 14px, transparent 14px 26px);opacity:.5}
.bus-icon{position:absolute;top:20px;animation:busmove 13s linear infinite reverse}
@keyframes busmove{0%{left:-6%}100%{left:104%}}


.logo{font-family:'Fraunces',serif;font-size:27px;font-weight:600;font-style:italic;border-bottom:1px solid var(--border);padding-bottom:20px;margin-bottom:38px;letter-spacing:.3px}
.logo span{color:var(--brass-bright);font-style:normal}

.eyebrow{color:var(--brass);font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;letter-spacing:3px;margin-top:18px}

.hero{font-family:'Fraunces',serif;font-size:clamp(42px,6.4vw,74px);font-weight:600;line-height:1.03;letter-spacing:-2px;max-width:860px;margin-top:10px}

.sub{color:var(--muted);font-size:16px;line-height:1.65;max-width:680px;margin:20px 0 36px}

.box{background:var(--panel2);border:1px solid var(--border);border-radius:6px;padding:22px}

/* Ticket-stub result cards */
.card{background:linear-gradient(160deg,var(--panel),var(--panel2));border:1px solid var(--border);border-radius:10px;padding:0;margin-bottom:20px;position:relative;overflow:visible}
.card-top{padding:20px 22px 18px}
.mode{color:var(--brass);font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;letter-spacing:1.5px}
.route{font-family:'Fraunces',serif;font-size:23px;font-weight:600;margin-top:14px}
.operator-line{color:var(--muted);font-size:13px;margin-top:6px}
.muted{color:var(--muted);font-size:12px}
.direct{background:rgba(86,214,176,.1);color:var(--teal);padding:4px 10px;border-radius:3px;font-size:10px;font-weight:700;letter-spacing:.5px;border:1px solid rgba(86,214,176,.28)}

.stub-divider{position:relative;height:0;border-top:1px dashed var(--border)}
.stub-divider::before,.stub-divider::after{content:'';position:absolute;top:-9px;width:18px;height:18px;border-radius:50%;background:var(--ink2)}
.stub-divider::before{left:-9px}
.stub-divider::after{right:-9px}

.card-bottom{padding:16px 22px 20px;display:flex;justify-content:space-between;align-items:flex-end}
.price-label{color:var(--muted);font-size:10px;letter-spacing:1.5px;text-transform:uppercase;font-family:'IBM Plex Mono',monospace}
.price{font-family:'IBM Plex Mono',monospace;font-size:27px;font-weight:600;color:var(--brass-bright);margin-top:4px}

.detail{background:var(--ink2);border:1px solid var(--border);border-radius:5px;padding:14px;margin:6px 0}
.label{color:var(--muted);font-size:10px;text-transform:uppercase;letter-spacing:1.5px;font-family:'IBM Plex Mono',monospace}
.value{font-size:14px;font-weight:600;margin-top:4px}
.notice{background:rgba(215,163,78,.08);border-left:3px solid var(--brass);padding:12px;border-radius:3px;color:var(--muted);font-size:12px;margin-top:10px}

.live{color:var(--teal);font-weight:700;font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:.5px}
.sample{color:var(--brass);font-weight:700;font-family:'IBM Plex Mono',monospace;font-size:12px;letter-spacing:.5px}

.stButton>button{border-radius:4px;background:var(--panel);color:var(--text);border:1px solid var(--border);font-weight:600}
.stButton>button:hover{border-color:var(--brass);color:var(--brass-bright)}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Helpers
# -----------------------------
def duration(minutes):
    h, m = divmod(int(minutes), 60)
    return f"{h} hr {m} min" if h else f"{m} min"

def euro(value):
    return f"€{float(value):.2f}"

AIRPORTS = {
    "LHR":"London Heathrow", "LGW":"London Gatwick",
    "CDG":"Paris Charles de Gaulle", "ORY":"Paris Orly",
    "AMS":"Amsterdam Schiphol", "BRU":"Brussels Airport",
    "DUB":"Dublin Airport", "BHX":"Birmingham Airport",
    "ORK":"Cork Airport", "SNN":"Shannon Airport",
    "LPL":"Liverpool John Lennon", "MUC":"Munich Airport",
    "PRG":"Prague Airport", "FCO":"Rome Fiumicino",
    "MAD":"Madrid Barajas", "BCN":"Barcelona El Prat",
    "FRA":"Frankfurt Airport", "ZRH":"Zurich Airport",
    "VIE":"Vienna International",
}

CITY_CODES = {
    "london":"LON","paris":"PAR","amsterdam":"AMS","brussels":"BRU",
    "dublin":"DUB","birmingham":"BHX","cork":"ORK","shannon":"SNN",
    "liverpool":"LPL","munich":"MUC","prague":"PRG","rome":"ROM",
    "madrid":"MAD","barcelona":"BCN","frankfurt":"FRA","zurich":"ZRH",
    "vienna":"VIE"
}

@st.cache_data(ttl=300)
def get_amadeus_token(client_id, client_secret):
    response = requests.post(
        "https://test.api.amadeus.com/v1/security/oauth2/token",
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["access_token"]

def city_code(text):
    cleaned = text.strip()
    if len(cleaned) == 3:
        return cleaned.upper()
    return CITY_CODES.get(cleaned.lower(), cleaned.upper()[:3])

def live_flight_search(origin, destination, travel_date, adults, client_id, client_secret, max_results=12):
    token = get_amadeus_token(client_id, client_secret)
    params = {
        "originLocationCode": city_code(origin),
        "destinationLocationCode": city_code(destination),
        "departureDate": travel_date.isoformat(),
        "adults": adults,
        "currencyCode": "EUR",
        "max": max_results,
        "nonStop": "false",
    }
    response = requests.get(
        "https://test.api.amadeus.com/v2/shopping/flight-offers",
        headers={"Authorization": f"Bearer {token}"},
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()

def parse_flights(payload):
    carriers = payload.get("dictionaries", {}).get("carriers", {})
    results = []
    for offer in payload.get("data", []):
        itineraries = offer.get("itineraries", [])
        if not itineraries:
            continue
        itinerary = itineraries[0]
        segments = itinerary.get("segments", [])
        if not segments:
            continue

        first = segments[0]
        last = segments[-1]
        dep = first.get("departure", {})
        arr = last.get("arrival", {})
        price = offer.get("price", {}).get("grandTotal")
        currency = offer.get("price", {}).get("currency", "EUR")

        carrier_code = first.get("carrierCode", "")
        airline = carriers.get(carrier_code, carrier_code or "Airline")

        dep_code = dep.get("iataCode", "")
        arr_code = arr.get("iataCode", "")
        stops = max(len(segments) - 1, 0)

        try:
            dep_time = pd.to_datetime(dep.get("at"))
            arr_time = pd.to_datetime(arr.get("at"))
            mins = int((arr_time - dep_time).total_seconds() // 60)
            dep_display = dep_time.strftime("%d %b %Y, %H:%M")
            arr_display = arr_time.strftime("%d %b %Y, %H:%M")
        except Exception:
            mins = 0
            dep_display = dep.get("at", "—")
            arr_display = arr.get("at", "—")

        results.append({
            "mode": "Flight",
            "icon": "✈️",
            "from": dep_code,
            "to": arr_code,
            "operator": airline,
            "carrier_code": carrier_code,
            "price": float(price) if price else 0,
            "currency": currency,
            "duration_minutes": mins,
            "stops": stops,
            "departure": dep_display,
            "arrival": arr_display,
            "flight_number": f"{carrier_code} {first.get('number','')}".strip(),
            "fare_type": offer.get("travelerPricings", [{}])[0].get("fareOption", "Economy"),
            "source": "Live",
        })
    return results

@st.cache_data
def sample_trips():
    return pd.read_csv(DATA)

# -----------------------------
# Header
# -----------------------------
st.markdown('<div class="logo">Euro<span>Voyage</span> ✦</div>', unsafe_allow_html=True)
st.markdown('<div class="eyebrow">LIVE TRAVEL SEARCH · EUROPE</div>', unsafe_allow_html=True)
st.markdown('<div class="hero">Find your fastest way across Europe.</div>', unsafe_allow_html=True)
st.markdown("""
<div class="sub">
Search live flight offers when your Amadeus credentials are connected,
while trains and buses remain clearly labelled as sample data until a
licensed live provider is connected.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="skyline">
  <div class="flight-path"></div>
  <svg class="plane-icon" width="30" height="30" viewBox="0 0 24 24" fill="none">
    <path d="M2 16.5L22 12L2 7.5L2 11L14 12L2 13Z" fill="#f2c877"/>
  </svg>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# Search
# -----------------------------
st.markdown('<div class="box">', unsafe_allow_html=True)
a,b,c,d,e=st.columns([1.2,1.2,1,1,.8])
with a: origin=st.text_input("FROM","London")
with b: destination=st.text_input("TO","Paris")
with c: travel_date=st.date_input("DATE",date.today())
with d:
    passenger_label=st.selectbox("PASSENGERS",["1 traveller","2 travellers","3 travellers","4 travellers"])
    adults=int(passenger_label.split()[0])
with e:
    st.markdown("<br>",unsafe_allow_html=True)
    search=st.button("Search trips",type="primary",use_container_width=True)
st.markdown("</div>",unsafe_allow_html=True)

transport=st.radio("TRANSPORT",["All","✈ Flights","🚆 Trains","🚌 Buses"],horizontal=True)
sorting=st.selectbox("SORT BY",["Recommended","Lowest price","Shortest trip"])

# -----------------------------
# Search results
# -----------------------------
results = []
live_status = False
live_error = None

if search and transport in ("All", "✈ Flights"):
    try:
        client_id = st.secrets["AMADEUS_CLIENT_ID"]
        client_secret = st.secrets["AMADEUS_CLIENT_SECRET"]
        payload = live_flight_search(
            origin, destination, travel_date, adults,
            client_id, client_secret
        )
        results.extend(parse_flights(payload))
        live_status = True
    except KeyError:
        live_error = "Live flight access is not configured yet."
    except requests.HTTPError as exc:
        live_error = f"The flight provider returned an error ({exc.response.status_code}). Check your API credentials and search details."
    except Exception as exc:
        live_error = f"Live flight search could not be completed: {exc}"

# Add sample train/bus results for demonstration
if transport in ("All","🚆 Trains","🚌 Buses"):
    samples = sample_trips()
    if transport == "🚆 Trains":
        samples = samples[samples.mode=="Train"]
    elif transport == "🚌 Buses":
        samples = samples[samples.mode=="Bus"]
    if search:
        if origin.strip():
            samples=samples[samples["from"].str.lower().str.contains(origin.strip().lower(),na=False)]
        if destination.strip():
            samples=samples[samples["to"].str.lower().str.contains(destination.strip().lower(),na=False)]
    for _, row in samples.iterrows():
        results.append({
            "mode":row["mode"],"icon":row["icon"],"from":row["from"],"to":row["to"],
            "operator":row["operator"],"price":row["price"],"currency":"EUR",
            "duration_minutes":row["duration_minutes"],"stops":row["stops"],
            "departure":"Not provided in sample data","arrival":"Not provided in sample data",
            "flight_number":"","fare_type":row["fare_type"],"source":"Sample",
            "note":row["note"]
        })

if sorting=="Lowest price":
    results=sorted(results,key=lambda x:x["price"])
elif sorting=="Shortest trip":
    results=sorted(results,key=lambda x:x["duration_minutes"])

if live_status:
    st.markdown('<p class="live">● LIVE FLIGHT RESULTS · refreshed for this search</p>',unsafe_allow_html=True)
elif live_error:
    st.warning(live_error + " Train/bus sample results can still be viewed.")

st.markdown(f'<div class="muted">{len(results)} options · {travel_date.strftime("%d %b %Y")} · {passenger_label}</div>',unsafe_allow_html=True)

if not results:
    st.info("Enter your route and click Search trips. If live flight access is configured, the app will query the flight provider.")

cols=st.columns(3)
for i,t in enumerate(results):
    with cols[i%3]:
        source_badge = '<span class="live">● LIVE</span>' if t["source"]=="Live" else '<span class="sample">● SAMPLE</span>'
        stops_text = "Direct" if int(t["stops"])==0 else f'{int(t["stops"])} stop{"s" if int(t["stops"]) != 1 else ""}'
        st.markdown(f"""
        <div class="card">
          <div class="card-top">
            <div style="display:flex;justify-content:space-between;align-items:center">
              <div class="mode">{t["icon"]} {t["mode"].upper()}</div>
              <div class="direct">{stops_text.upper()}</div>
            </div>
            <div style="margin-top:10px">{source_badge}</div>
            <div class="route">{t["from"]} → {t["to"]}</div>
            <div class="operator-line">{t["operator"]} · ◷ {duration(t["duration_minutes"])}</div>
          </div>
          <div class="stub-divider"></div>
          <div class="card-bottom">
            <div>
              <div class="price-label">Fare from</div>
              <div class="price">{t["currency"]} {float(t["price"]):.2f}</div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("✦ View travel details"):
            st.markdown(f"### {t['icon']} {t['mode']} details")
            x,y=st.columns(2)
            with x:
                dep_name = AIRPORTS.get(t["from"], t["from"])
                st.markdown(f'<div class="detail"><div class="label">Departure</div><div class="value">{t["from"]} · {dep_name}</div></div>',unsafe_allow_html=True)
            with y:
                arr_name = AIRPORTS.get(t["to"], t["to"])
                st.markdown(f'<div class="detail"><div class="label">Arrival</div><div class="value">{t["to"]} · {arr_name}</div></div>',unsafe_allow_html=True)

            x,y=st.columns(2)
            with x:
                st.markdown(f'<div class="detail"><div class="label">Operator</div><div class="value">{t["operator"]}</div></div>',unsafe_allow_html=True)
            with y:
                st.markdown(f'<div class="detail"><div class="label">Journey time</div><div class="value">{duration(t["duration_minutes"])}</div></div>',unsafe_allow_html=True)

            if t["source"]=="Live":
                x,y=st.columns(2)
                with x:
                    st.markdown(f'<div class="detail"><div class="label">Departure time</div><div class="value">{t["departure"]}</div></div>',unsafe_allow_html=True)
                with y:
                    st.markdown(f'<div class="detail"><div class="label">Arrival time</div><div class="value">{t["arrival"]}</div></div>',unsafe_allow_html=True)
                st.markdown(f'<div class="detail"><div class="label">Flight</div><div class="value">{t["flight_number"] or "Not supplied"}</div></div>',unsafe_allow_html=True)
                st.markdown(f'<div class="detail"><div class="label">Fare</div><div class="value">{t["currency"]} {float(t["price"]):.2f} · {t["fare_type"]}</div></div>',unsafe_allow_html=True)
                st.markdown('<div class="notice">This result was returned by the connected flight API for the selected search. Prices and availability can change, so verify again before booking.</div>',unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="detail"><div class="label">Fare</div><div class="value">€{float(t["price"]):.2f} · {t["fare_type"]}</div></div>',unsafe_allow_html=True)
                st.markdown('<div class="notice">This transport result is sample data in the prototype. It is not live availability or a guaranteed current fare.</div>',unsafe_allow_html=True)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")

st.markdown("""
<div class="transit-strip">
  <div class="rail-line"></div>
  <svg class="train-icon" width="34" height="26" viewBox="0 0 24 24" fill="none">
    <rect x="4" y="2" width="16" height="14" rx="3" fill="#56d6b0"/>
    <rect x="6" y="4" width="5" height="5" rx="1" fill="#060b14"/>
    <rect x="13" y="4" width="5" height="5" rx="1" fill="#060b14"/>
    <circle cx="7" cy="19" r="2" fill="#56d6b0"/>
    <circle cx="17" cy="19" r="2" fill="#56d6b0"/>
    <rect x="9" y="16" width="6" height="2" fill="#56d6b0"/>
  </svg>
  <div class="road-line"></div>
  <svg class="bus-icon" width="34" height="22" viewBox="0 0 24 24" fill="none">
    <rect x="2" y="4" width="20" height="10" rx="2.5" fill="#d7a34e"/>
    <rect x="4" y="6" width="4" height="3.5" rx=".5" fill="#060b14"/>
    <rect x="10" y="6" width="4" height="3.5" rx=".5" fill="#060b14"/>
    <rect x="16" y="6" width="4" height="3.5" rx=".5" fill="#060b14"/>
    <circle cx="6.5" cy="16.5" r="2" fill="#d7a34e"/>
    <circle cx="17.5" cy="16.5" r="2" fill="#d7a34e"/>
  </svg>
</div>
""", unsafe_allow_html=True)

st.markdown('<div style="font-family:\'Fraunces\',serif;font-size:22px;font-weight:600;margin-bottom:14px">EuroVoyage live-data roadmap</div>', unsafe_allow_html=True)
x,y,z=st.columns(3)
x.markdown("**✈️ Flights**  \nLive search is connected through the Amadeus API when credentials are supplied.")
y.markdown("**🚆 Trains**  \nNeeds a licensed European rail data provider for live fares/schedules.")
z.markdown("**🚌 Buses**  \nNeeds operator/aggregator APIs for live prices and availability.")
st.caption("EuroVoyage prototype. Live flight results depend on the connected provider and its coverage. Never commit API credentials to GitHub.")

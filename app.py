
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
.stApp{background:radial-gradient(circle at 10% 0%,#17365b 0,transparent 35%),linear-gradient(135deg,#07111f,#091727 55%,#070d18);color:#eef6ff}
.block-container{max-width:1250px;padding-top:2rem}
.logo{font-size:25px;font-weight:900;border-bottom:1px solid #18304a;padding-bottom:20px;margin-bottom:42px}.logo span{color:#6ee7ff}
.hero{font-size:clamp(45px,7vw,78px);font-weight:900;line-height:.95;letter-spacing:-5px;max-width:850px}
.eyebrow{color:#6ee7ff;font-size:13px;font-weight:800;letter-spacing:2px}
.sub{color:#91a5bc;font-size:17px;line-height:1.6;max-width:720px;margin:20px 0 35px}
.box{background:#0d1b2c;border:1px solid #29435f;border-radius:24px;padding:24px}
.card{background:linear-gradient(145deg,#0d1b2d,#0a1625);border:1px solid #203852;border-radius:20px;padding:22px;margin-bottom:16px;min-height:310px}
.mode{color:#6ee7ff;font-size:12px;font-weight:800}.route{font-size:21px;font-weight:850;margin-top:16px}.muted{color:#91a5bc;font-size:12px}.price{font-size:30px;font-weight:900}.direct{background:#113a2b;color:#67e8a5;padding:5px 9px;border-radius:999px;font-size:11px;font-weight:700}
.detail{background:#091525;border:1px solid #203852;border-radius:12px;padding:14px;margin:6px 0}.label{color:#71869d;font-size:10px;text-transform:uppercase;letter-spacing:1px}.value{font-size:14px;font-weight:600;margin-top:3px}.notice{background:#10253a;border-left:4px solid #6ee7ff;padding:12px;border-radius:7px;color:#b7c7d8;font-size:12px;margin-top:10px}
.live{color:#67e8a5;font-weight:800}.sample{color:#f3c969;font-weight:800}
.stButton>button{border-radius:12px;background:#0b1828;color:#eef6ff;border:1px solid #29435f;font-weight:700}.stButton>button:hover{border-color:#6ee7ff;color:#6ee7ff}
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
          <div style="display:flex;justify-content:space-between">
            <div class="mode">{t["icon"]} {t["mode"].upper()}</div>
            <div class="direct">{stops_text.upper()}</div>
          </div>
          <div style="margin-top:8px">{source_badge}</div>
          <div class="route">{t["from"]} → {t["to"]}</div>
          <div class="muted">{t["operator"]}</div>
          <p>◷ {duration(t["duration_minutes"])}</p>
          <div class="muted">FROM</div>
          <div class="price">{t["currency"]} {float(t["price"]):.2f}</div>
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
st.markdown("### EuroVoyage live-data roadmap")
x,y,z=st.columns(3)
x.markdown("**✈️ Flights**  \nLive search is connected through the Amadeus API when credentials are supplied.")
y.markdown("**🚆 Trains**  \nNeeds a licensed European rail data provider for live fares/schedules.")
z.markdown("**🚌 Buses**  \nNeeds operator/aggregator APIs for live prices and availability.")
st.caption("EuroVoyage prototype. Live flight results depend on the connected provider and its coverage. Never commit API credentials to GitHub.")

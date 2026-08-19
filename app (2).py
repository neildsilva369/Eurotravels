
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

/* ============================================================
   EXPANDED DESIGN SYSTEM — nav, stats, network map, process,
   testimonials, FAQ, footer
   ============================================================ */

/* Custom scrollbar, ties to the brass/ink palette */
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-track{background:var(--ink)}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:5px}
::-webkit-scrollbar-thumb:hover{background:var(--brass)}

/* Sticky top navigation */
.topnav{position:sticky;top:0;z-index:999;display:flex;align-items:center;justify-content:space-between;
  padding:14px 0;margin-bottom:8px;backdrop-filter:blur(10px);
  background:linear-gradient(180deg, rgba(6,11,20,.92), rgba(6,11,20,.75));
  border-bottom:1px solid var(--border)}
.topnav .brand{font-family:'Fraunces',serif;font-size:19px;font-weight:600;font-style:italic}
.topnav .brand span{color:var(--brass-bright);font-style:normal}
.topnav .links{display:flex;gap:28px}
.topnav .links a{color:var(--muted);text-decoration:none;font-size:13px;font-weight:500;letter-spacing:.3px;
  font-family:'IBM Plex Mono',monospace;transition:color .2s ease}
.topnav .links a:hover{color:var(--brass-bright)}
.topnav .pill{background:rgba(86,214,176,.1);border:1px solid rgba(86,214,176,.3);color:var(--teal);
  font-family:'IBM Plex Mono',monospace;font-size:10px;font-weight:700;letter-spacing:1px;
  padding:5px 11px;border-radius:20px}

/* Fade-up entrance for hero elements */
@keyframes fadeUp{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:translateY(0)}}
.fade-in{animation:fadeUp .7s ease both}
.fade-in.d1{animation-delay:.05s}.fade-in.d2{animation-delay:.15s}.fade-in.d3{animation-delay:.25s}

/* Hero stat chips */
.stat-row{display:flex;gap:14px;flex-wrap:wrap;margin:8px 0 30px}
.stat-chip{background:var(--panel2);border:1px solid var(--border);border-radius:8px;padding:12px 18px;min-width:130px}
.stat-chip .num{font-family:'IBM Plex Mono',monospace;font-size:22px;font-weight:600;color:var(--brass-bright)}
.stat-chip .lbl{color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-top:2px}

/* Section scaffolding */
.section{margin:70px 0 10px;scroll-margin-top:80px}
.section-eyebrow{color:var(--brass);font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:600;letter-spacing:3px;margin-bottom:10px}
.section-title{font-family:'Fraunces',serif;font-size:clamp(28px,3.4vw,40px);font-weight:600;letter-spacing:-1px;margin-bottom:12px}
.section-sub{color:var(--muted);font-size:15px;max-width:640px;line-height:1.6;margin-bottom:32px}

/* Route network / constellation map */
.network-wrap{background:var(--panel2);border:1px solid var(--border);border-radius:10px;padding:20px;position:relative;overflow:hidden}
.network-wrap svg{width:100%;height:auto;display:block}
.net-dot{animation:pulse-dot 2.6s ease-in-out infinite}
@keyframes pulse-dot{0%,100%{opacity:1}50%{opacity:.45}}
.net-line{stroke-dasharray:4 5;animation:dash-flow 3s linear infinite}
@keyframes dash-flow{to{stroke-dashoffset:-90}}
.net-legend{display:flex;gap:22px;margin-top:16px;flex-wrap:wrap}
.net-legend .item{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--muted);font-family:'IBM Plex Mono',monospace}
.net-legend .dot{width:8px;height:8px;border-radius:50%;display:inline-block}

/* Popular routes cards (postcard style) */
.route-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:16px}
.route-card{background:linear-gradient(155deg,var(--panel),var(--panel2));border:1px solid var(--border);
  border-radius:10px;padding:20px;transition:transform .25s ease,border-color .25s ease}
.route-card:hover{transform:translateY(-4px);border-color:var(--brass)}
.route-card .rc-cities{font-family:'Fraunces',serif;font-size:18px;font-weight:600}
.route-card .rc-meta{color:var(--muted);font-size:12px;margin-top:8px;font-family:'IBM Plex Mono',monospace}
.route-card .rc-tag{display:inline-block;margin-top:12px;font-size:10px;letter-spacing:1px;color:var(--teal);
  background:rgba(86,214,176,.1);border:1px solid rgba(86,214,176,.25);padding:3px 9px;border-radius:20px}

/* How-it-works numbered steps (real sequence, numbering is meaningful) */
.steps-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px}
.step-card{position:relative;padding:26px 20px 20px;border:1px solid var(--border);border-radius:10px;background:var(--panel2)}
.step-num{font-family:'Fraunces',serif;font-size:34px;font-weight:600;color:var(--brass);opacity:.55;line-height:1}
.step-title{font-family:'Fraunces',serif;font-size:19px;font-weight:600;margin-top:10px}
.step-desc{color:var(--muted);font-size:13.5px;line-height:1.6;margin-top:8px}
.step-arrow{position:absolute;right:-26px;top:50%;transform:translateY(-50%);color:var(--border);font-size:20px;display:none}
@media(min-width:900px){.steps-row .step-card:not(:last-child) .step-arrow{display:block}}

/* Traveler notes / testimonials (postcard-stamp motif) */
.note-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}
.note-card{background:var(--panel2);border:1px solid var(--border);border-radius:10px;padding:22px;position:relative}
.note-stamp{position:absolute;top:16px;right:16px;width:34px;height:34px;border:1.5px dashed var(--border);
  border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;color:var(--brass)}
.note-quote{font-family:'Fraunces',serif;font-style:italic;font-size:15.5px;line-height:1.6;color:var(--text);
  padding-right:36px}
.note-author{margin-top:16px;font-family:'IBM Plex Mono',monospace;font-size:11px;color:var(--muted);letter-spacing:.5px}

/* Newsletter + expanded footer */
.newsletter{background:linear-gradient(120deg,var(--panel2),var(--panel));border:1px solid var(--border);
  border-radius:12px;padding:32px;display:flex;justify-content:space-between;align-items:center;gap:24px;flex-wrap:wrap}
.newsletter .nl-title{font-family:'Fraunces',serif;font-size:22px;font-weight:600}
.newsletter .nl-sub{color:var(--muted);font-size:13px;margin-top:6px;max-width:420px}

.footer-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:32px;margin-top:44px}
.footer-col h4{font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:1.5px;color:var(--brass);
  text-transform:uppercase;margin-bottom:14px}
.footer-col a{display:block;color:var(--muted);text-decoration:none;font-size:13px;margin-bottom:10px;transition:color .2s}
.footer-col a:hover{color:var(--brass-bright)}
.footer-col p{color:var(--muted);font-size:13px;line-height:1.7}
.footer-brand{font-family:'Fraunces',serif;font-size:20px;font-weight:600;font-style:italic;margin-bottom:10px}
.footer-brand span{color:var(--brass-bright);font-style:normal}
.social-row{display:flex;gap:10px;margin-top:16px}
.social-row a{width:32px;height:32px;border:1px solid var(--border);border-radius:50%;display:flex;
  align-items:center;justify-content:center;color:var(--muted);transition:.2s}
.social-row a:hover{border-color:var(--brass);color:var(--brass-bright)}
.footer-legal{border-top:1px solid var(--border);margin-top:36px;padding-top:20px;display:flex;
  justify-content:space-between;flex-wrap:wrap;gap:10px;color:var(--muted);font-size:12px;font-family:'IBM Plex Mono',monospace}

@media(max-width:900px){.footer-grid{grid-template-columns:1fr 1fr}}

/* Scrolling departure-board ticker */
.ticker-wrap{overflow:hidden;border-top:1px solid var(--border);border-bottom:1px solid var(--border);
  background:var(--panel2);padding:10px 0;margin:18px 0 0}
.ticker-track{display:flex;gap:48px;white-space:nowrap;animation:ticker-scroll 34s linear infinite;width:max-content}
.ticker-track span{font-family:'IBM Plex Mono',monospace;font-size:12px;color:var(--muted);letter-spacing:.5px}
.ticker-track span b{color:var(--brass-bright)}
@keyframes ticker-scroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}

/* Mode comparison table */
.compare-table{width:100%;border-collapse:collapse;margin-top:8px}
.compare-table th{text-align:left;font-family:'IBM Plex Mono',monospace;font-size:11px;letter-spacing:1px;
  color:var(--brass);text-transform:uppercase;padding:12px 16px;border-bottom:1px solid var(--border)}
.compare-table td{padding:14px 16px;border-bottom:1px solid var(--border);font-size:13.5px;color:var(--text)}
.compare-table tr:last-child td{border-bottom:none}
.compare-table td.dim{color:var(--muted)}
.compare-table .status-live{color:var(--teal);font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:700}
.compare-table .status-sample{color:var(--brass);font-family:'IBM Plex Mono',monospace;font-size:11px;font-weight:700}

/* Travel tips checklist */
.tips-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}
.tip-item{display:flex;gap:14px;padding:16px;background:var(--panel2);border:1px solid var(--border);border-radius:8px}
.tip-icon{width:34px;height:34px;flex:none;border-radius:50%;background:rgba(215,163,78,.12);
  display:flex;align-items:center;justify-content:center;color:var(--brass-bright);font-size:15px}
.tip-text h5{margin:0 0 4px;font-size:14px;font-weight:600}
.tip-text p{margin:0;color:var(--muted);font-size:12.5px;line-height:1.5}

/* Airport directory chips */
.airport-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px}
.airport-chip{display:flex;align-items:center;gap:10px;background:var(--panel2);border:1px solid var(--border);
  border-radius:6px;padding:10px 12px;transition:border-color .2s ease}
.airport-chip:hover{border-color:var(--brass)}
.airport-chip .code{font-family:'IBM Plex Mono',monospace;font-weight:700;color:var(--brass-bright);
  font-size:13px;background:rgba(215,163,78,.1);border-radius:4px;padding:3px 7px;min-width:38px;text-align:center}
.airport-chip .name{font-size:12.5px;color:var(--muted)}

/* Accessibility: respect reduced-motion, keep focus visible */
a:focus-visible, button:focus-visible, input:focus-visible{outline:2px solid var(--brass-bright);outline-offset:2px}
@media(prefers-reduced-motion: reduce){
  .plane-icon,.train-icon,.bus-icon,.ticker-track,.net-line,.net-dot,.fade-in{animation:none !important}
}

/* Link underline sweep, used for in-page nav + footer links */
.topnav .links a, .footer-col a{position:relative}
.topnav .links a::after, .footer-col a::after{
  content:'';position:absolute;left:0;bottom:-3px;width:0;height:1px;background:var(--brass-bright);
  transition:width .25s ease}
.topnav .links a:hover::after, .footer-col a:hover::after{width:100%}

/* Selection color, small brand touch */
::selection{background:rgba(215,163,78,.35);color:var(--text)}

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
st.markdown("""
<div class="topnav">
  <div class="brand">Euro<span>Voyage</span> ✦</div>
  <div class="links">
    <a href="#network">Route network</a>
    <a href="#routes">Popular routes</a>
    <a href="#how-it-works">How it works</a>
    <a href="#faq">FAQ</a>
  </div>
  <div class="pill">● LIVE FLIGHT SEARCH</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ticker-wrap">
  <div class="ticker-track">
    <span><b>LON→PAR</b> from €44</span>
    <span><b>AMS→BER</b> from €19.99</span>
    <span><b>DUB→LON</b> live search enabled</span>
    <span><b>PAR→ZRH</b> 4hr 3min by rail</span>
    <span><b>PRG→VIE</b> direct rail</span>
    <span><b>ROM→BCN</b> live search enabled</span>
    <span><b>BRU→PAR</b> from €9.99</span>
    <span><b>LON→PAR</b> from €44</span>
    <span><b>AMS→BER</b> from €19.99</span>
    <span><b>DUB→LON</b> live search enabled</span>
    <span><b>PAR→ZRH</b> 4hr 3min by rail</span>
    <span><b>PRG→VIE</b> direct rail</span>
    <span><b>ROM→BCN</b> live search enabled</span>
    <span><b>BRU→PAR</b> from €9.99</span>
  </div>
</div>
""", unsafe_allow_html=True)
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
<div class="stat-row">
  <div class="stat-chip"><div class="num">19</div><div class="lbl">Airports mapped</div></div>
  <div class="stat-chip"><div class="num">3</div><div class="lbl">Transport modes</div></div>
  <div class="stat-chip"><div class="num">12</div><div class="lbl">Cities in network</div></div>
  <div class="stat-chip"><div class="num">EUR</div><div class="lbl">Fares in</div></div>
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
# Route network map
# -----------------------------
st.markdown('<div class="section" id="network">', unsafe_allow_html=True)
st.markdown('<div class="section-eyebrow">THE NETWORK</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Every route we cover, at a glance.</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">A live-capable flight lane connects almost every city below. Rail and coach lanes are shown too, but remain sample data until a licensed provider is connected.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="network-wrap">
<svg viewBox="0 0 760 320" xmlns="http://www.w3.org/2000/svg">
  <line class="net-line" x1="120" y1="70"  x2="330" y2="60"  stroke="#56d6b0" stroke-width="1.4"/>
  <line class="net-line" x1="330" y1="60"  x2="470" y2="40"  stroke="#56d6b0" stroke-width="1.4"/>
  <line class="net-line" x1="330" y1="60"  x2="360" y2="180" stroke="#56d6b0" stroke-width="1.4"/>
  <line class="net-line" x1="120" y1="70"  x2="150" y2="200" stroke="#d7a34e" stroke-width="1.2"/>
  <line class="net-line" x1="150" y1="200" x2="360" y2="180" stroke="#d7a34e" stroke-width="1.2"/>
  <line class="net-line" x1="360" y1="180" x2="470" y2="230" stroke="#d7a34e" stroke-width="1.2"/>
  <line class="net-line" x1="470" y1="40"  x2="620" y2="90"  stroke="#56d6b0" stroke-width="1.4"/>
  <line class="net-line" x1="470" y1="230" x2="620" y2="220" stroke="#d7a34e" stroke-width="1.2"/>
  <line class="net-line" x1="470" y1="40"  x2="470" y2="230" stroke="#25405f" stroke-width="1"/>
  <line class="net-line" x1="620" y1="90"  x2="620" y2="220" stroke="#25405f" stroke-width="1"/>

  <circle class="net-dot" cx="120" cy="70"  r="5" fill="#f2c877"/>
  <text x="130" y="66" fill="#8ba0b7" font-size="12" font-family="IBM Plex Mono">London</text>

  <circle class="net-dot" cx="330" cy="60"  r="5" fill="#f2c877"/>
  <text x="340" y="56" fill="#8ba0b7" font-size="12" font-family="IBM Plex Mono">Brussels</text>

  <circle class="net-dot" cx="470" cy="40"  r="5" fill="#f2c877"/>
  <text x="480" y="36" fill="#8ba0b7" font-size="12" font-family="IBM Plex Mono">Amsterdam</text>

  <circle class="net-dot" cx="150" cy="200" r="5" fill="#f2c877"/>
  <text x="100" y="222" fill="#8ba0b7" font-size="12" font-family="IBM Plex Mono">Dublin</text>

  <circle class="net-dot" cx="360" cy="180" r="5" fill="#f2c877"/>
  <text x="370" y="176" fill="#8ba0b7" font-size="12" font-family="IBM Plex Mono">Paris</text>

  <circle class="net-dot" cx="470" cy="230" r="5" fill="#f2c877"/>
  <text x="480" y="252" fill="#8ba0b7" font-size="12" font-family="IBM Plex Mono">Zurich</text>

  <circle class="net-dot" cx="620" cy="90"  r="5" fill="#f2c877"/>
  <text x="630" y="86" fill="#8ba0b7" font-size="12" font-family="IBM Plex Mono">Prague</text>

  <circle class="net-dot" cx="620" cy="220" r="5" fill="#f2c877"/>
  <text x="630" y="242" fill="#8ba0b7" font-size="12" font-family="IBM Plex Mono">Rome</text>
</svg>
<div class="net-legend">
  <div class="item"><span class="dot" style="background:#56d6b0"></span> Flight lane (live-capable)</div>
  <div class="item"><span class="dot" style="background:#d7a34e"></span> Rail / coach lane (sample)</div>
</div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Popular routes
# -----------------------------
st.markdown('<div class="section" id="routes">', unsafe_allow_html=True)
st.markdown('<div class="section-eyebrow">TRAVELLER FAVOURITES</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Popular routes to search first.</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">A starting point if you\'re not sure where to look — these are the lanes searched most often on EuroVoyage.</div>', unsafe_allow_html=True)

POPULAR_ROUTES = [
    ("London", "Paris", "2 hr 16 min by rail · direct", "Flights + Rail"),
    ("Amsterdam", "Berlin", "6 hr 30 min by coach", "Flights + Coach"),
    ("Dublin", "London", "1 hr 15 min by air", "Flights"),
    ("Paris", "Zurich", "4 hr 3 min by rail", "Flights + Rail"),
    ("Prague", "Vienna", "4 hr direct rail", "Flights + Rail"),
    ("Rome", "Barcelona", "1 hr 50 min by air", "Flights"),
    ("Munich", "Prague", "5 hr by coach", "Flights + Coach"),
    ("Madrid", "Lisbon", "1 hr 20 min by air", "Flights"),
    ("Frankfurt", "Vienna", "1 hr 15 min by air", "Flights"),
]
route_cards_html = '<div class="route-grid">'
for a_city, b_city, meta, tag in POPULAR_ROUTES:
    route_cards_html += f"""
    <div class="route-card">
      <div class="rc-cities">{a_city} → {b_city}</div>
      <div class="rc-meta">{meta}</div>
      <div class="rc-tag">{tag.upper()}</div>
    </div>"""
route_cards_html += "</div>"
st.markdown(route_cards_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# How it works
# -----------------------------
st.markdown('<div class="section" id="how-it-works">', unsafe_allow_html=True)
st.markdown('<div class="section-eyebrow">THE PROCESS</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Three steps, start to finish.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="steps-row">
  <div class="step-card">
    <div class="step-num">01</div>
    <div class="step-title">Enter your route</div>
    <div class="step-desc">Type a city or airport code, pick a date and traveller count, and choose which transport modes to include.</div>
    <div class="step-arrow">→</div>
  </div>
  <div class="step-card">
    <div class="step-num">02</div>
    <div class="step-title">Compare results</div>
    <div class="step-desc">Live flight offers are pulled from the connected provider; rail and coach are shown as sample data until a live source is added.</div>
    <div class="step-arrow">→</div>
  </div>
  <div class="step-card">
    <div class="step-num">03</div>
    <div class="step-title">Check the details</div>
    <div class="step-desc">Open any result to see departure and arrival times, operator, and fare type before you decide where to book.</div>
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Mode comparison
# -----------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-eyebrow">CHOOSING A MODE</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Flights, rail, or coach — at a glance.</div>', unsafe_allow_html=True)

st.markdown("""
<table class="compare-table">
  <tr><th>Mode</th><th>Typical speed</th><th>Typical fare</th><th>Best for</th><th>Data status</th></tr>
  <tr>
    <td>✈️ Flights</td>
    <td class="dim">Fastest over 500km+</td>
    <td class="dim">€30 – €300</td>
    <td class="dim">Long distances, tight schedules</td>
    <td><span class="status-live">● LIVE</span></td>
  </tr>
  <tr>
    <td>🚆 Rail</td>
    <td class="dim">Fast, city-centre to city-centre</td>
    <td class="dim">€25 – €120</td>
    <td class="dim">Regional hops, no airport transfers</td>
    <td><span class="status-sample">● SAMPLE</span></td>
  </tr>
  <tr>
    <td>🚌 Coach</td>
    <td class="dim">Slower, budget-friendly</td>
    <td class="dim">€8 – €40</td>
    <td class="dim">Short-to-mid trips on a tight budget</td>
    <td><span class="status-sample">● SAMPLE</span></td>
  </tr>
</table>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Travel tips
# -----------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-eyebrow">BEFORE YOU GO</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">A few things worth checking.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="tips-grid">
  <div class="tip-item"><div class="tip-icon">🛂</div><div class="tip-text"><h5>Travel documents</h5><p>Check passport and visa rules for each country on your route, not just your final stop.</p></div></div>
  <div class="tip-item"><div class="tip-icon">🧳</div><div class="tip-text"><h5>Baggage rules</h5><p>Budget carriers, rail, and coach operators all size and price baggage differently — check before you pack.</p></div></div>
  <div class="tip-item"><div class="tip-icon">🕐</div><div class="tip-text"><h5>Connection buffers</h5><p>Leave real time between legs, especially crossing from rail or coach into an airport.</p></div></div>
  <div class="tip-item"><div class="tip-icon">💳</div><div class="tip-text"><h5>Fare verification</h5><p>Sample data here is illustrative — always confirm the live price with the airline, rail, or coach operator directly.</p></div></div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-eyebrow">TRAVELLER NOTES</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">What people search EuroVoyage for.</div>', unsafe_allow_html=True)

st.markdown("""
<div class="note-grid">
  <div class="note-card">
    <div class="note-stamp">✦</div>
    <div class="note-quote">"I use it to sanity-check flight prices before committing to a booking site."</div>
    <div class="note-author">— PROTOTYPE USER NOTE</div>
  </div>
  <div class="note-card">
    <div class="note-stamp">✦</div>
    <div class="note-quote">"The route map made it obvious which cities were even worth comparing."</div>
    <div class="note-author">— PROTOTYPE USER NOTE</div>
  </div>
  <div class="note-card">
    <div class="note-stamp">✦</div>
    <div class="note-quote">"Clear about what's live and what's sample data — I didn't have to guess."</div>
    <div class="note-author">— PROTOTYPE USER NOTE</div>
  </div>
  <div class="note-card">
    <div class="note-stamp">✦</div>
    <div class="note-quote">"The comparison table settled a rail-vs-coach argument in about ten seconds."</div>
    <div class="note-author">— PROTOTYPE USER NOTE</div>
  </div>
  <div class="note-card">
    <div class="note-stamp">✦</div>
    <div class="note-quote">"Nice to see a travel search tool that admits which parts aren't live yet."</div>
    <div class="note-author">— PROTOTYPE USER NOTE</div>
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# About the data
# -----------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-eyebrow">TRANSPARENCY</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Where the numbers actually come from.</div>', unsafe_allow_html=True)

about_col1, about_col2 = st.columns(2)
with about_col1:
    st.markdown("""
    <div class="detail" style="padding:18px">
      <div class="label">Flights</div>
      <div class="value" style="margin-top:8px;font-weight:400;line-height:1.6">
      Pulled live from the Amadeus Flight Offers Search API for the exact route, date, and traveller count you search.
      Results are cached briefly to avoid repeated calls for the same search, then discarded.
      </div>
    </div>
    """, unsafe_allow_html=True)
with about_col2:
    st.markdown("""
    <div class="detail" style="padding:18px">
      <div class="label">Rail &amp; coach</div>
      <div class="value" style="margin-top:8px;font-weight:400;line-height:1.6">
      A fixed CSV of illustrative routes, shipped with the app. It exists to show what a real result would look like
      once a licensed rail or coach data source is connected — it is never presented as live availability.
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
st.markdown("""
<div class="detail" style="padding:18px">
  <div class="label">Credentials &amp; secrets</div>
  <div class="value" style="margin-top:8px;font-weight:400;line-height:1.6">
  API credentials are read from Streamlit's server-side secrets store and never appear in the repository,
  the browser, or the page source. If credentials aren't configured, live search is skipped and only the
  clearly-labelled sample results are shown.
  </div>
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# Airports directory
# -----------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-eyebrow">COVERAGE</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Airports in the EuroVoyage network.</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Every airport code the app can resolve to a full name in flight results — this list grows as more cities are added to the lookup tables.</div>', unsafe_allow_html=True)

airport_chips_html = '<div class="airport-grid">'
for code, name in sorted(AIRPORTS.items(), key=lambda kv: kv[1]):
    airport_chips_html += f'<div class="airport-chip"><span class="code">{code}</span><span class="name">{name}</span></div>'
airport_chips_html += "</div>"
st.markdown(airport_chips_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------
# FAQ
# -----------------------------
st.markdown('<div class="section" id="faq">', unsafe_allow_html=True)
st.markdown('<div class="section-eyebrow">QUESTIONS</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Frequently asked.</div>', unsafe_allow_html=True)

with st.expander("What's the difference between live and sample results?"):
    st.write("Live results come from the connected flight provider for the exact search you ran. Sample results are fixed demo data for trains and buses, shown until a licensed live rail/coach provider is connected — they're always labelled SAMPLE so they're never mistaken for real availability.")
with st.expander("Why don't trains and buses show live prices?"):
    st.write("European rail and coach data is fragmented across many national operators and aggregators, each with their own licensing terms. Connecting a real provider for this is a separate integration from the flight search shown here.")
with st.expander("Is this connected to a real booking flow?"):
    st.write("No — EuroVoyage is a search and comparison prototype. It doesn't process payments or hold real bookings; always verify price and availability directly with the airline, rail, or coach operator before booking.")
with st.expander("Which flight environment does the live search use?"):
    st.write("The Amadeus test environment by default, which is meant for development rather than guaranteed bookable inventory. Production use requires production credentials and compliance with the provider's terms.")
with st.expander("Do I need an account to search?"):
    st.write("No — search is open and doesn't require sign-in. Only the developer running the app needs API credentials, configured as server-side secrets, never entered by the person searching.")
with st.expander("Can I add more cities to the route network?"):
    st.write("Yes. The airport and city-code mappings are defined directly in the app code, so more cities can be added by extending those lookup tables and the sample data file.")
st.markdown('</div>', unsafe_allow_html=True)

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

st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)

st.markdown("""
<div class="newsletter">
  <div>
    <div class="nl-title">Get notified when rail &amp; coach go live.</div>
    <div class="nl-sub">A short note when a licensed rail or coach data provider is connected — no spam, just the one update.</div>
  </div>
</div>
""", unsafe_allow_html=True)
nl_col1, nl_col2 = st.columns([3,1])
with nl_col1:
    st.text_input("Email", placeholder="you@example.com", label_visibility="collapsed")
with nl_col2:
    st.button("Notify me", use_container_width=True)

st.markdown("""
<div class="footer-grid">
  <div class="footer-col">
    <div class="footer-brand">Euro<span>Voyage</span></div>
    <p>A live-search prototype for getting across Europe — built for a hackathon, styled like a departure board.</p>
    <div class="social-row">
      <a href="#" title="X / Twitter">𝕏</a>
      <a href="#" title="Instagram">◎</a>
      <a href="#" title="GitHub">⌥</a>
    </div>
  </div>
  <div class="footer-col">
    <h4>Product</h4>
    <a href="#network">Route network</a>
    <a href="#routes">Popular routes</a>
    <a href="#how-it-works">How it works</a>
    <a href="#faq">FAQ</a>
  </div>
  <div class="footer-col">
    <h4>Coverage</h4>
    <a href="#">Flights — live</a>
    <a href="#">Rail — sample</a>
    <a href="#">Coach — sample</a>
  </div>
  <div class="footer-col">
    <h4>Legal</h4>
    <a href="#">Not a booking service</a>
    <a href="#">Test-environment data</a>
    <a href="#">No credentials stored client-side</a>
  </div>
</div>
<div class="footer-legal">
  <div>© 2026 EuroVoyage prototype. Not affiliated with any airline, rail, or coach operator.</div>
  <div>Built with Streamlit · Live data via Amadeus</div>
</div>
""", unsafe_allow_html=True)

st.caption("EuroVoyage prototype. Live flight results depend on the connected provider and its coverage. Never commit API credentials to GitHub.")

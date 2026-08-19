# EuroVoyage — Live Flight Version

This version keeps the existing EuroVoyage UI but adds a live flight-search integration using Amadeus Flight Offers Search.

## What is live?

- Flights: live API search when Amadeus credentials are configured.
- Trains: sample data.
- Buses: sample data.

European rail and bus data is fragmented across providers, so those should be connected to licensed live sources separately rather than pretending the CSV is live.

## GitHub structure

```text
EuroVoyage/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── trips.csv
└── assets/
```

## Streamlit secrets

Do NOT put API credentials in GitHub.

In Streamlit Community Cloud, open your app settings and add these secrets:

```toml
AMADEUS_CLIENT_ID = "YOUR_CLIENT_ID"
AMADEUS_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
```

The app reads them with `st.secrets`.

## Local secrets

Create:

```text
.streamlit/secrets.toml
```

with the same two lines. Keep that file out of GitHub.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Important

The app uses the Amadeus TEST environment by default. Test-environment results are for development and should not be presented as guaranteed bookable live inventory.

For a production travel site, use the appropriate Amadeus production environment/credentials and comply with the provider's terms, rate limits, and commercial requirements.

## Deploy

Because your GitHub repository currently contains an `EuroVoyage` folder, your Streamlit entrypoint is:

```text
EuroVoyage/app.py
```

Community Cloud can accept that file path during deployment.

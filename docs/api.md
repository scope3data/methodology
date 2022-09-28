# API

API code is located `./scope3_methodology/api/api.py`

# Usage
From within `./scope3_methodology/api` run
```
uvicorn api:app --reload
```
or 
```
python3 scope3_methodology/api/api.py
``` 

# Example Queries

Calculate Corporate Emissions
```
curl -v  -X 'GET' 'localhost:8000/calculate/corporate'   -H 'Content-Type: application/json'  -d '{"org_type": "atp", "number_of_employees": 50}'
```

Calculate Ad Tech Platfrom Emissions
```
curl -v  -X 'GET' 'localhost:8000/calculate/atp'   -H 'Content-Type: application/json'  -d '{"atp_template": "dsp"}'
```

Calculate Ad Tech Platfrom Distribution Partner Secondary Emissions
```
curl -v  -X 'GET' 'localhost:8000/calculate/atp_secondary_bid_request_emissions'   -H 'Content-Type: application/json'  -d '{
  "partners": [
    {
      "partner": {
        "name": "string",
        "identifier": "string",
        "primary_bid_request_emissions_g_co2e": 0.0007033278081937295,
        "primary_cookie_sync_emissions_g_co2e": 0.004111234960495689,
        "corporate_emissions_g_co2e_per_bid_request": 0.00015648471735020598
      },
      "bid_request_distribution_rate": 1.0
    }
  ]
}'
```

Get Defaults for a ATP Template
```
curl -v  -X 'GET' 'localhost:8000/defaults/atp/dsp'
```

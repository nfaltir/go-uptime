# Site Uptime Monitor

A Go-based application to track website uptime and latency, with dashboards built using Streamlit and Grafana.

<br><hr>


## Overview
This project monitors the uptime and latency of a web application, storing results in a SQLite database (`site_status.db`). It provides:
- A Go backend with an API endpoint (`/data`) serving JSON data.
- A Streamlit dashboard (Python) to visualize API data.
- A Grafana dashboard to analyze SQLite data with advanced tools.

<br>

## Project Setup

- create  a `touch .env` file inside root folder
- inside the file create an environment variable called `targetURL=<url for your site>`
- run app `go run main.go`
- to run the frontend end you might need to create a python environemnt first, then start frontend server. `streamlit run app.py`
- to visuaize Grafana, you need to docker for installation.

<br>

## Features

<br><hr>

### Streamlit Dashboard
- Built with the [Streamlit](https://streamlit.io/) Python framework.
- Visualizes JSON data from `http://localhost:8080/data` in a simple, interactive UI.
- Screenshot:  
  ![Streamlit Dashboard](./assets/streamlit.png "Streamlit dashboard showing latency and uptime")

<br>


### Grafana Dashboard
- Uses [Grafana](https://grafana.com/), an open-source visualization platform.
- Connects to `site_status.db` for detailed metrics (e.g., latency trends, uptime stats).
- Requires Docker to run on port `3000`—see setup below.
- Screenshot:  
  ![Grafana Dashboard](./assets/grafana.png "Grafana dashboard with latency and status visualizations")

<br>

## Golang API Endpoint 

- localhost:8080/data
- Screenshot:
      ![Api Endpoint](./assets/api.png "Api endpoint serving at port 8080/data")


<br>

## Notes

Latency is relatively high—this is due to:
- The hosting server configuration.
- Rate-limiting on the monitored site.
- The app pings the server every 10 minutes to check if it's online.
- Future enhancements will include push notifications via Grafana alerting tools.
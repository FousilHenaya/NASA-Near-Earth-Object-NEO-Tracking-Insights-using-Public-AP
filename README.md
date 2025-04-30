
 # 🚀 NASA Asteroid Data Explorer

This project combines a backend data pipeline and a frontend dashboard for analyzing near-Earth asteroid data using NASA's API. It consists of two components:

- **Backend**: Collects, processes, and stores asteroid data from NASA into a MySQL database.
- **Frontend (Streamlit App)**: Allows users to explore and query the data visually.

---

## 📦 Features

- Fetches data from NASA NEO API
- Stores asteroid data in MySQL
- Streamlit dashboard for filtering and querying data
- Analytical SQL queries:
  - Fastest, slowest, brightest asteroids
  - Hazardous asteroid counts
  - Monthly/daily approach stats
  - Distance and diameter comparisons

---

## 📂 Project Structure

- `nasaproject.py`: Backend script for data ingestion and SQL analytics
- `astro.py`: Streamlit app for interactive visualization

---


## 🧠 How It Works

### Backend (`nasaproject.py`):
1. Connects to NASA's NEO API
2. Extracts asteroid data and approach metrics
3. Stores in two MySQL tables:
   - `asteroids`
   - `CLOSE_APPROACH`
4. Executes SQL-based data analysis

### Frontend (`astro.py`):
1. Uses Streamlit to build a web UI
2. Users can filter data by:
   - Magnitude, size, velocity, distance
   - Date range
   - Hazardous status
3. Dropdown for pre-defined SQL queries
4. Displays results in an interactive format

---


## 📊 Example Insights

- Asteroids that approached faster than 50,000 km/h
- Closest approach dates and distances
- Fastest and slowest NEOs
- Approach trends by month
- Most and least active dates
- Hazardous asteroids count

---

## 🖼️ Dashboard Preview

Streamlit UI provides:
- Sidebar filters
- Query dropdown
- Data tables
- Real-time results




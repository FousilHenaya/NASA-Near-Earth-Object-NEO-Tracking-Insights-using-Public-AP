import streamlit as st

import requests

import pandas as pd

from datetime import datetime

import mysql.connector as db

connection = db.connect(
    host = 'localhost',
    user = 'root',
    password ='Shaffie0000' ,
    database = 'astro'
)

curr = connection.cursor()

st.title("ASTEROID DATA ☄️ ")

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/e/e5/NASA_logo.svg", width=150)

st.sidebar.markdown(
    "<h2 style='font-size:30px;'>📺 ASTEROID APPROACHES</h2>", 
    unsafe_allow_html=True
)

st.sidebar.markdown("---")



if "show_filters" not in st.session_state:
    st.session_state.show_filters = False

if "show_queries" not in st.session_state:
    st.session_state.show_queries = False

query=None

if st.sidebar.button("🚀 Filter criteria"):
    st.session_state.show_filters = True
    st.session_state.show_queries = False
    
if st.sidebar.button("🔍 Show Queries"):
    st.session_state.show_queries = True
    st.session_state.show_filters = False
    

    
if st.session_state.show_filters:
    from datetime import date

    
    # Title
    st.markdown("### 🚀 NASA Asteroid Tracker 🪐")
    
    # Create columns
    col1, col2, col3 = st.columns(3)
    
    # Column 1 Filters
    with col1:
        st.markdown("**Min Magnitude**")
        min_magnitude = st.slider(" ",18.0, 30.0, (18.0, 30.0), key="magnitude")
        
        st.markdown("**Min Estimated Diameter (km)**")
        min_diameter = st.slider("  ", 0.001, 0.620, (0.001, 0.620), key="min_diameter")
        
        st.markdown("**Max Estimated Diameter (km)**")
        max_diameter = st.slider("   ", 0.003, 1.400, (0.003, 1.400), key="max_diameter")
    
    # Column 2 Filters
    with col2:
        st.markdown("**Relative Velocity (km/h) Range**")
        velocity_range = st.slider("    ", 1909.58, 136268.00, (1909.58, 136268.00), key="velocity")
        
        st.markdown("**Astronomical Unit**")
        au = st.slider("     ", 0.0,0.50, (0.0, 0.50), key="au")
        
        st.markdown("**Only Show Potentially Hazardous**")
        hazard = st.selectbox("", options=["Yes", "No"], index=1)
    
    # Column 3 Filters
    with col3:
        st.markdown("**Start Date**")
       
        start_date = st.date_input("", value=date(2024, 1, 1), key="start_date")
        
        st.markdown("**End Date**")
        end_date = st.date_input(" ", value=date(2025, 4, 29), key="end_date")
    
    # Submit button
    if  st.button("Filter"):
        curr.execute("SELECT distinct * FROM ASTEROIDS")
        asteroid_data = curr.fetchall()
        asteroid_df = pd.DataFrame(asteroid_data, columns=[desc[0] for desc in curr.description])
    
        curr.execute("SELECT distinct * FROM CLOSE_APPROACH")
        approach_data = curr.fetchall()
        approach_df = pd.DataFrame(approach_data, columns=[desc[0] for desc in curr.description])
           
        merged_df = pd.merge(asteroid_df, approach_df,left_on="id", right_on="neo_reference_id")
       
        merged_df['close_approach_date']=pd.to_datetime(merged_df['close_approach_date'], errors='coerce')
        start_date= pd.to_datetime(start_date)
        end_date= pd.to_datetime(end_date)
        filter_mask = (
            (merged_df['absolute_magnitude_h'].between(min_magnitude[0], min_magnitude[1])) &
            (merged_df['estimated_diameter_min_km'].between(min_diameter[0], min_diameter[1])) &
            (merged_df['estimated_diameter_max_km'].between(max_diameter[0], max_diameter[1])) &
            (merged_df['relative_velocity_km_per_hr'].between(velocity_range[0], velocity_range[1])) &
            (merged_df['astronomical_unit'].between(au[0], au[1])) &
            (merged_df['close_approach_date'].between(start_date, end_date))
        )
        
        filtered_df = merged_df[filter_mask]
                 
    
        # Add hazard condition if selected
        if hazard == "Yes":
             filtered_df = filtered_df[filtered_df["is_potentially_hazardous"] == 1]
        elif hazard == "No":
            filtered_df = filtered_df[filtered_df["is_potentially_hazardous"] == 0]

         
            # Execute query and display result
            
        st.markdown("### ☄️ Filtered Asteroid Data")
        st.dataframe(filtered_df)
        
     
           


if st.session_state.show_queries:
        query = st.selectbox("📌 Select a query",[
        "Count how many times each asteroid has approached Earth",
        "List top 10 fastest asteroids",
        "Average velocity of each asteroid over multiple approaches",
        "Potentially hazardous asteroids that have approached Earth more than 3 times",
        "Find the month with the most asteroid approaches",
        "Get the asteroid with the fastest ever approach speed",
        "Sort asteroids by maximum estimated diameter (descending)",
        "Asteroids whose closest approach is getting nearer over time",
        "List names of asteroids that approached Earth with velocity > 50,000 km/h",
        "Display the name of each asteroid along with the date and miss distance of its closest approach to Earth.",
        "Count how many approaches happened per month",
        "Find asteroid with the highest brightness (lowest magnitude value)",
        "Get number of hazardous vs non-hazardous asteroids",
        "asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance.",
        "asteroids that came within 0.05 AU(astronomical distance)",
        "Range of diameter of asteroids",
        "Biggest diameter and shortest diameter",
        "Get the asteroid with the slowest ever approach speed",
        "Date with most asteroids",
        "Date with least asteroids"
        ])
    

        st.markdown(f"<h3 style='font-size:24px;'>You selected: {query}</h3>", unsafe_allow_html=True)

if query=="Count how many times each asteroid has approached Earth":
    query2 = """
    select neo_reference_id, count(*) as approach_count
    from CLOSE_APPROACH
    group by neo_reference_id;
    """
    curr.execute(query2)
    results = curr.fetchall()

    columns = [desc[0] for desc in curr.description]
    df = pd.DataFrame(results, columns = columns)
    st.dataframe(df)

if query=="List top 10 fastest asteroids":
    query1 = """
    select DISTINCT neo_reference_id,relative_velocity_km_per_hr
    from CLOSE_APPROACH
    order by relative_velocity_km_per_hr desc
    LIMIT 10
    """

    curr.execute(query1)
    results1 = curr.fetchall()

    columns = [desc[0] for desc in curr.description]
    df = pd.DataFrame(results1, columns = columns)
    st.dataframe(df)
    
if query=="Average velocity of each asteroid over multiple approaches":
    query3 = """
    select neo_reference_id,relative_velocity_km_per_hr
    from CLOSE_APPROACH
    """

    curr.execute(query3)
    results1 = curr.fetchall()

    columns = [desc[0] for desc in curr.description]
    df = pd.DataFrame(results1, columns = columns)

    average_velocities = df.groupby("neo_reference_id")["relative_velocity_km_per_hr"].mean().reset_index()
    average_velocities = average_velocities.rename(columns={"relative_velocity_km_per_hr": "average_velocity"})
    st.dataframe(df)
    
if query=="Potentially hazardous asteroids that have approached Earth more than 3 times":
    query4 = """
    select id, is_potentially_hazardous
    from asteroids
    """
    curr.execute(query4)
    results = curr.fetchall()
    
    columns = [desc[0] for desc in curr.description]
    df = pd.DataFrame(results, columns = columns)
    
    hazardous_df = df[df["is_potentially_hazardous"] == True]
    approach_counts = hazardous_df.groupby("id").size().reset_index(name="approach_count")
    hazardous_frequent = approach_counts[approach_counts["approach_count"] >3]
    st.dataframe(df)

if query=="Find the month with the most asteroid approaches":
    query2 = """
    select close_approach_date
    from CLOSE_APPROACH
    """
    curr.execute(query2)
    results = curr.fetchall()
    
    columns = [desc[0] for desc in curr.description]
    df = pd.DataFrame(results, columns = columns)
    
    df['close_approach_date'] = pd.to_datetime(df['close_approach_date'])
    df['month'] = df['close_approach_date'].dt.month
    
    monthly_counts = df['month'].value_counts().sort_values(ascending=False).reset_index()
    monthly_counts.columns = ['month', 'approach_count']
    st.dataframe(monthly_counts.head(1))
    
if query=="Get the asteroid with the fastest ever approach speed":
    query1 = """
    select DISTINCT neo_reference_id,relative_velocity_km_per_hr
    from CLOSE_APPROACH
    order by relative_velocity_km_per_hr desc
    LIMIT 1
    """
    
    curr.execute(query1)
    results1 = curr.fetchall()
    
    columns = [desc[0] for desc in curr.description]
    df = pd.DataFrame(results1, columns = columns)
    st.dataframe(df)
    
if query=="Sort asteroids by maximum estimated diameter (descending)":
    query1 = """
    select DISTINCT id,estimated_diameter_max_km
    from asteroids
    order by estimated_diameter_max_km desc
    """
    
    curr.execute(query1)
    results1 = curr.fetchall()
    
    columns = [desc[0] for desc in curr.description]
    df = pd.DataFrame(results1, columns = columns)
    st.dataframe(df)

if query=="Asteroids whose closest approach is getting nearer over time":
    query1 = """
    select DISTINCT neo_reference_id, close_approach_date, miss_distance_km
    from CLOSE_APPROACH
    ORDER BY neo_reference_id, close_approach_date
    """
    
    curr.execute(query1)
    results1 = curr.fetchall()
    
    columns = [desc[0] for desc in curr.description]
    df = pd.DataFrame(results1, columns = columns)
    
    def is_getting_closer(group):
        return group['miss_distance_km'].is_monotonic_decreasing
        
    closer_over_time = df.groupby('neo_reference_id').filter(is_getting_closer)
    unique_asteroids = closer_over_time['neo_reference_id'].unique()
    st.dataframe(df)
    
if query=="List names of asteroids that approached Earth with velocity > 50,000 km/h":
    query_asteroids = "SELECT distinct id, name FROM ASTEROIDS"
    curr.execute(query_asteroids)
    asteroid_data = curr.fetchall()
    asteroid_df = pd.DataFrame(asteroid_data, columns=[desc[0] for desc in curr.description])
    
    query_approach = "SELECT distinct neo_reference_id, relative_velocity_km_per_hr FROM CLOSE_APPROACH"
    curr.execute(query_approach)
    approach_data = curr.fetchall()
    approach_df = pd.DataFrame(approach_data, columns=[desc[0] for desc in curr.description])
    
    merged_df = pd.merge(approach_df, asteroid_df, left_on="neo_reference_id", right_on="id")
    
    filtered_df = merged_df[merged_df["relative_velocity_km_per_hr"] > 50000]
    
    result_df = filtered_df[["name", "relative_velocity_km_per_hr"]].sort_values(by="relative_velocity_km_per_hr", ascending=False)
    st.dataframe(df)
    
if query=="Display the name of each asteroid along with the date and miss distance of its closest approach to Earth.":
    query_asteroids = "SELECT distinct id, name FROM ASTEROIDS"
    curr.execute(query_asteroids)
    asteroid_data = curr.fetchall()
    asteroid_df = pd.DataFrame(asteroid_data, columns=[desc[0] for desc in curr.description])
    
    query_approach = "SELECT distinct neo_reference_id, close_approach_date,miss_distance_km FROM CLOSE_APPROACH"
    curr.execute(query_approach)
    approach_data = curr.fetchall()
    approach_df = pd.DataFrame(approach_data, columns=[desc[0] for desc in curr.description])
    
    merged_df = pd.merge(
        approach_df,
        asteroid_df,
        left_on="neo_reference_id",
        right_on="id",
        how="inner" 
    )
    result_df = merged_df[["name", "close_approach_date", "miss_distance_km"]]
    st.dataframe(df)
    
if query=="Count how many approaches happened per month":
    query2 = """
    select close_approach_date
    from CLOSE_APPROACH
    """
    curr.execute(query2)
    results = curr.fetchall()
    
    columns = [desc[0] for desc in curr.description]
    df = pd.DataFrame(results, columns = columns)
    
    df['close_approach_date'] = pd.to_datetime(df['close_approach_date'])
    df['month'] = df['close_approach_date'].dt.month_name()
    
    monthly_counts = df['month'].value_counts().sort_values(ascending=False).reset_index()
    monthly_counts.columns = ['month', 'approach_count']
    
    
    st.markdown("### Asteroid Approaches by Month")
    st.dataframe(monthly_counts)
    
if query=="Find asteroid with the highest brightness (lowest magnitude value)":
    query_asteroids = "SELECT distinct id,name, absolute_magnitude_h FROM ASTEROIDS"
    curr.execute(query_asteroids)
    asteroid_data = curr.fetchall()
    asteroid_df = pd.DataFrame(asteroid_data, columns=[desc[0] for desc in curr.description])
    
    brightest = asteroid_df.loc[asteroid_df["absolute_magnitude_h"].idxmin()]
    
    st.write(f"The brightest asteroid is **{brightest['name']}** with a magnitude of **{brightest['absolute_magnitude_h']}**.")
    
if query=="Get number of hazardous vs non-hazardous asteroids":
    query_asteroids = "SELECT distinct id,is_potentially_hazardous FROM ASTEROIDS"
    curr.execute(query_asteroids)
    asteroid_data = curr.fetchall()
    asteroid_df = pd.DataFrame(asteroid_data, columns=[desc[0] for desc in curr.description])
    
    hazardous_count = asteroid_df[asteroid_df["is_potentially_hazardous"] == True].shape[0]
    non_hazardous_count = asteroid_df[asteroid_df["is_potentially_hazardous"] == False].shape[0]
    
    st.write(f"Number of hazardous asteroids: {hazardous_count}")
    st.write(f"Number of non-hazardous asteroids: {non_hazardous_count}")
    
if query=="asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance.":
    query_asteroids = "SELECT distinct id, name FROM ASTEROIDS"
    curr.execute(query_asteroids)
    asteroid_data = curr.fetchall()
    asteroid_df = pd.DataFrame(asteroid_data, columns=[desc[0] for desc in curr.description])
    
    query_approach = "SELECT distinct neo_reference_id, lunar_distance, miss_distance_km,close_approach_date FROM CLOSE_APPROACH"
    curr.execute(query_approach)
    approach_data = curr.fetchall()
    approach_df = pd.DataFrame(approach_data, columns=[desc[0] for desc in curr.description])
    
    approach_df = approach_df[approach_df["miss_distance_km"] < 384400]
    
    merged_df = pd.merge(
        approach_df,
        asteroid_df,
        left_on="neo_reference_id",
        right_on="id",
        how="inner"
    )
    
    result_df = merged_df[["name", "close_approach_date", "miss_distance_km"]]
    st.dataframe(df)
    
if query=="asteroids that came within 0.05 AU(astronomical distance)":
    query_approach = "SELECT distinct neo_reference_id, astronomical_unit, close_approach_date from CLOSE_APPROACH "
    curr.execute(query_approach)
    approach_data = curr.fetchall()
    approach_df = pd.DataFrame(approach_data, columns=[desc[0] for desc in curr.description])
    
    query_asteroids = "SELECT DISTINCT id, name FROM ASTEROIDS"
    curr.execute(query_asteroids)
    asteroid_data = curr.fetchall()
    asteroid_df = pd.DataFrame(asteroid_data, columns=[desc[0] for desc in curr.description])
    
    merged_df = pd.merge(
        approach_df,
        asteroid_df,
        left_on="neo_reference_id",
        right_on="id",
        how="inner")
    
    filtered_df = merged_df[merged_df["astronomical_unit"] < 0.05]
    
    result_df = merged_df[["name", "close_approach_date", "astronomical_unit"]]
    st.dataframe(df)
    
if query=="Range of diameter of asteroids":
    query_asteroids = "SELECT distinct id, name,estimated_diameter_min_km,estimated_diameter_max_km FROM ASTEROIDS"
    curr.execute(query_asteroids)
    asteroid_data = curr.fetchall()
    asteroid_df = pd.DataFrame(asteroid_data, columns=[desc[0] for desc in curr.description])
    
    asteroid_df['estimated_diameter_min_km'] = pd.to_numeric(asteroid_df['estimated_diameter_min_km'], errors='coerce')
    asteroid_df['estimated_diameter_max_km'] = pd.to_numeric(asteroid_df['estimated_diameter_max_km'], errors='coerce')
    
    asteroid_df['diameter_range_km'] = asteroid_df['estimated_diameter_max_km'] - asteroid_df['estimated_diameter_min_km']
    
    st.write("### Asteroid Diameter Range")
    st.write(asteroid_df[['name', 'estimated_diameter_min_km', 'estimated_diameter_max_km', 'diameter_range_km']])
  
if query=="Biggest diameter and shortest diameter":
    query_asteroids = "SELECT distinct id, name,estimated_diameter_min_km,estimated_diameter_max_km FROM ASTEROIDS"
    curr.execute(query_asteroids)
    asteroid_data = curr.fetchall()
    asteroid_df = pd.DataFrame(asteroid_data, columns=[desc[0] for desc in curr.description])
    
    
    biggest_asteroid = asteroid_df.loc[asteroid_df['estimated_diameter_max_km'].idxmax()]
    
    smallest_asteroid = asteroid_df.loc[asteroid_df['estimated_diameter_min_km'].idxmin()]
    
    st.write("Biggest Asteroid:")
    st.dataframe(biggest_asteroid[['name', 'estimated_diameter_max_km']])
    
    st.write("\nSmallest Asteroid:")
    st.dataframe(smallest_asteroid[['name', 'estimated_diameter_min_km']])
  
if query=="Get the asteroid with the slowest ever approach speed":
    query1 = """
    select DISTINCT neo_reference_id,relative_velocity_km_per_hr
    from CLOSE_APPROACH
    order by relative_velocity_km_per_hr 
    LIMIT 1
    """
    
    curr.execute(query1)
    results1 = curr.fetchall()
    
    columns = [desc[0] for desc in curr.description]
    df = pd.DataFrame(results1, columns = columns)
    st.dataframe(df)

if query=="Date with most asteroids":
    query2 = """
    select close_approach_date
    from CLOSE_APPROACH
    """
    curr.execute(query2)
    results = curr.fetchall()
    
    columns = [desc[0] for desc in curr.description]
    df = pd.DataFrame(results, columns = columns)
    
    df['close_approach_date'] = pd.to_datetime(df['close_approach_date'])
    
    date_counts = df['close_approach_date'].value_counts().sort_values(ascending=False).reset_index()
    date_counts.columns = ['close_approach_date', 'approach_count']
    
    st.write("Date with the most approaches:")
    st.dataframe(date_counts.head(1))

if query=="Date with least asteroids":
    query2 = """
    select close_approach_date
    from CLOSE_APPROACH
    """
    curr.execute(query2)
    results = curr.fetchall()
    
    columns = [desc[0] for desc in curr.description]
    df = pd.DataFrame(results, columns = columns)
    
    df['close_approach_date'] = pd.to_datetime(df['close_approach_date'])
    
    date_counts = df['close_approach_date'].value_counts().sort_values(ascending=False).reset_index()
    date_counts.columns = ['close_approach_date', 'approach_count']
    
    st.write("Date with the most approaches:")
    st.dataframe(date_counts.tail(1))
    

import requests

import pandas as pd

from datetime import datetime

API_KEY = "TgIjc2C35ULxg5jDTWCYCIuRXGGBe09YMC6fRz1W"

url = F"https://api.nasa.gov/neo/rest/v1/feed?start_date=2024-01-01&end_date=2024-01-08&api_key={API_KEY}"

all_asteroids = []

target = 10000

while url and len(all_asteroids) < target:
    response = requests.get(url)

    data = response.json()
    neo_data = data["near_earth_objects"]

    for date, asteroids in neo_data.items():
        for asteroid in asteroids:
            asteroid_data = {
                'id':asteroid['id'],
                'neo_ref_id':asteroid['neo_reference_id'],
                'name':asteroid['name'],
                'absolute_magnitude_h':asteroid['absolute_magnitude_h'],
                'estimated_diameter_min_km':asteroid['estimated_diameter']['kilometers']['estimated_diameter_min'],
                'estimated_diameter_max_km':asteroid['estimated_diameter']['kilometers']['estimated_diameter_max'],
                'is_potentially_hazardous':asteroid['is_potentially_hazardous_asteroid'],
                'close_approach_date':(datetime.strptime(asteroid['close_approach_data'][0]['close_approach_date'],'%Y-%m-%d').strftime("%Y-%m-%d")),
                'relative_velocity_(km/h)':float(asteroid['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']),
                'astronomical_unit':float(asteroid['close_approach_data'][0]['miss_distance']['astronomical']),
                'lunar_distance':float(asteroid['close_approach_data'][0]['miss_distance']['lunar']),
                'miss_distance_km':float(asteroid['close_approach_data'][0]['miss_distance']['kilometers']),
                'orbiting_body':asteroid['close_approach_data'][0]['orbiting_body']
            }
            all_asteroids.append(asteroid_data)

            
            
            #stops if we reach the target
            if len(all_asteroids)>=10000:
                break
        if len(all_asteroids)>=10000:
                break

url = data['links']['next']


!pip install mysql-connector-python

import mysql.connector as db

import pandas as pd

connection = db.connect(
    host = 'localhost',
    user = 'root',
    password ='Shaffie0000' ,
    database = 'astro'
)

curr = connection.cursor()

curr.execute(
    """
    CREATE TABLE asteroids(
    id INT,
    name VARCHAR(100),
    absolute_magnitude_h FLOAT,
    estimated_diameter_min_km FLOAT,
    estimated_diameter_max_km FLOAT,
    is_potentially_hazardous BOOL
    );
    
    """
)

insert_query = "insert into asteroids values(%s,%s,%s,%s,%s,%s)"

for i in all_asteroids:
    id = int(i['id'])
    name = i['name']
    magnitude = float(i['absolute_magnitude_h'])
    dia_min = float(i['estimated_diameter_min_km'])
    dia_max = float(i['estimated_diameter_max_km'])
    hazard = i['is_potentially_hazardous'] 
    values = [(id,name,magnitude,dia_min,dia_max,hazard)]

    curr.executemany(insert_query,values)
    connection.commit()
    
    
    
query = "select * from asteroids"
df = pd.read_sql(query, connection)
df



curr.execute(
    '''
    create table CLOSE_APPROACH (
    neo_reference_id INT,
    close_approach_date DATE,
    relative_velocity_km_per_hr FLOAT,
    astronomical_unit FLOAT,
    lunar_distance FLOAT,
    miss_distance_km FLOAT,
    orbiting_body VARCHAR(100)
    );
    
    '''
)


insert_query = "insert into CLOSE_APPROACH values(%s,%s,%s,%s,%s,%s,%s)"

for i in all_asteroids:
    neo_id = int(i['neo_ref_id'])
    close_app_date =  i['close_approach_date']
    velocity = float(i['relative_velocity_(km/h)'])
    atronomical_unit = float(i['astronomical_unit'])
    lunar_distance = float(i['lunar_distance'])
    miss_distance = float( i['miss_distance_km']) 
    orbiting_body = i['orbiting_body']
    values = [(neo_id,close_app_date,velocity,atronomical_unit,lunar_distance,miss_distance,orbiting_body)]

    curr.executemany(insert_query,values)
    connection.commit()
    
query = "select * from CLOSE_APPROACH"
df = pd.read_sql(query, connection)
df

#queries

#Count how many times each asteroid has approached Earth

query2 = """
select neo_reference_id, count(*) as approach_count
from CLOSE_APPROACH
group by neo_reference_id;
"""
curr.execute(query2)
results = curr.fetchall()

columns = [desc[0] for desc in curr.description]
df = pd.DataFrame(results, columns = columns)
print(df)


#List top 10 fastest asteroids

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
print(df)


#Average velocity of each asteroid over multiple approaches
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
print(average_velocities)


#Find potentially hazardous asteroids that have approached Earth more than 3 times
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
print(hazardous_frequent)



#Find the month with the most asteroid approaches
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

print("Month with the most approaches:")
print(monthly_counts.head(1))


#Get the asteroid with the fastest ever approach speed

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
print(df)


#Sort asteroids by maximum estimated diameter (descending)

query1 = """
select DISTINCT id,estimated_diameter_max_km
from asteroids
order by estimated_diameter_max_km desc
"""

curr.execute(query1)
results1 = curr.fetchall()

columns = [desc[0] for desc in curr.description]
df = pd.DataFrame(results1, columns = columns)
print(df)


#Asteroids whose closest approach is getting nearer over time(Hint: Use ORDER BY close_approach_date and look at miss_distance)

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

print("Asteroids whose closest approach is getting nearer over time:")
print(unique_asteroids)


#List names of asteroids that approached Earth with velocity > 50,000 km/h

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
print(result_df)



#Display the name of each asteroid along with the date and miss distance of its closest approach to Earth.

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

print(result_df)


#Count how many approaches happened per month


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


print(monthly_counts)


#Find asteroid with the highest brightness (lowest magnitude value)

query_asteroids = "SELECT distinct id,name, absolute_magnitude_h FROM ASTEROIDS"
curr.execute(query_asteroids)
asteroid_data = curr.fetchall()
asteroid_df = pd.DataFrame(asteroid_data, columns=[desc[0] for desc in curr.description])

brightest = asteroid_df.loc[asteroid_df["absolute_magnitude_h"].idxmin()]

print(f"The brightest asteroid is {brightest['name']} with a magnitude of {brightest['absolute_magnitude_h']}.")


#Get number of hazardous vs non-hazardous asteroids

query_asteroids = "SELECT distinct id,is_potentially_hazardous FROM ASTEROIDS"
curr.execute(query_asteroids)
asteroid_data = curr.fetchall()
asteroid_df = pd.DataFrame(asteroid_data, columns=[desc[0] for desc in curr.description])

hazardous_count = asteroid_df[asteroid_df["is_potentially_hazardous"] == True].shape[0]
non_hazardous_count = asteroid_df[asteroid_df["is_potentially_hazardous"] == False].shape[0]

print(f"Number of hazardous asteroids: {hazardous_count}")
print(f"Number of non-hazardous asteroids: {non_hazardous_count}")



#asteroids that passed closer than the Moon (lesser than 1 LD), along with their close approach date and distance.


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

print(result_df)


#asteroids that came within 0.05 AU(astronomical distance)

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

print(result_df)


#range of diameter of asteroids
query_asteroids = "SELECT distinct id, name,estimated_diameter_min_km,estimated_diameter_max_km FROM ASTEROIDS"
curr.execute(query_asteroids)
asteroid_data = curr.fetchall()
asteroid_df = pd.DataFrame(asteroid_data, columns=[desc[0] for desc in curr.description])

asteroid_df['estimated_diameter_min_km'] = pd.to_numeric(asteroid_df['estimated_diameter_min_km'], errors='coerce')
asteroid_df['estimated_diameter_max_km'] = pd.to_numeric(asteroid_df['estimated_diameter_max_km'], errors='coerce')

asteroid_df['diameter_range_km'] = asteroid_df['estimated_diameter_max_km'] - asteroid_df['estimated_diameter_min_km']

print(asteroid_df[['name', 'estimated_diameter_min_km', 'estimated_diameter_max_km', 'diameter_range_km']])


#biggest diameter and shortest diameter

query_asteroids = "SELECT distinct id, name,estimated_diameter_min_km,estimated_diameter_max_km FROM ASTEROIDS"
curr.execute(query_asteroids)
asteroid_data = curr.fetchall()
asteroid_df = pd.DataFrame(asteroid_data, columns=[desc[0] for desc in curr.description])


biggest_asteroid = asteroid_df.loc[asteroid_df['estimated_diameter_max_km'].idxmax()]

smallest_asteroid = asteroid_df.loc[asteroid_df['estimated_diameter_min_km'].idxmin()]

print("Biggest Asteroid:")
print(biggest_asteroid[['name', 'estimated_diameter_max_km']])

print("\nSmallest Asteroid:")
print(smallest_asteroid[['name', 'estimated_diameter_min_km']])


#Get the asteroid with the slowest ever approach speed

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
print(df)


#date with most asteroids
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

print("Date with the most approaches:")
print(date_counts.head(1))



##date with least asteroids

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

print("Date with the most approaches:")
print(date_counts.tail(1))


curr.close()
connection.close()
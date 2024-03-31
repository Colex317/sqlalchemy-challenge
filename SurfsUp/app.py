# Import the dependencies.
import numpy as np
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask , jsonify

#--------------------------------------------------------------------------------------------------------------------------------------------------------
# Database Setup

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#--------------------------------------------------------------------------------------------------------------------------------------------------------
# Flask Setup

app = Flask(__name__)

#--------------------------------------------------------------------------------------------------------------------------------------------------------
# Flask Routes

# 1. List all the available routes.
@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end"
    )

#--------------------------------------------------------------------------------------------------------------------------------------------------------
# 2. Convert the query results from your precipitation analysis to a dictionary using date as the key and prcp as the value. 
   
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the last 12 months of precipitation data
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= '2016-08-23').all()
    
    session.close()
    
    # Convert query results to dictionary
    prcp_date_dict = {}
    for date, prcp in precipitation_data:
        prcp_date_dict[date] = prcp

    # Return the JSON representation of your dictionary.
    return jsonify(prcp_date_dict)

#--------------------------------------------------------------------------------------------------------------------------------------------------------
# 3. Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def station(): 
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query all stations
    stations_list = session.query(Station.station).all()
    
    session.close()

    # Extract the station names from the query results
    stations = [station[0] for station in stations_list]

    # Return JSON representation of the list
    return jsonify(stations)

#--------------------------------------------------------------------------------------------------------------------------------------------------------
# 4. Query the dates and temperature observations of the most-active station for the previous year of data. 

@app.route("/api/v1.0/tobs")
def tobs(): 

     # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Query the most active station
    most_active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first()[0]

    # Query temperature observations for the previous year from the most active station
    temp_observation = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date > '2016-08-17').all()

    for date, tobs in temp_observation:
        print(f"Date: {date}, Temperature: {tobs}")
    
    session.close()
    
    # Create a list of temperature observations for the previous year
    tobs_list = [{'date': date, 'temperature': tobs} for date, tobs in temp_observation]

    # Return JSON list of temperature observations for the previous year.
    return jsonify(tobs_list)

#--------------------------------------------------------------------------------------------------------------------------------------------------------
# 5. Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

@app.route("/api/v1.0/temp/<start>")
def temp_range_start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query minumum, average and maximum temperature statistics for dates greater than or equal to a specified start date
    start_date_temp = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    # Return JSON representation of temperature statistics
    return jsonify(start_date_temp)



# For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/temp/<start>/<end>")
def temp_range_start_end(start,end):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query minimum, average, and maximum temperature statistics for dates within a specified start-end date range (inclusive)
    start_end_date_temp = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Return JSON representation of temperature statistics
    return jsonify(start_end_date_temp)


if __name__ == "__main__":
    app.run(debug=True)
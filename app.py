# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    year_before = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    precipitation = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= year_before).all()
    return jsonify(dict(precipitation))

@app.route("/api/v1.0/stations")
def stations():
    stations_list = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).order_by(func.count(measurement.station).desc()).all()
    return(dict(stations_list))

@app.route("/api/v1.0/tobs")
def tobs():
    recent = session.query(measurement.date).order_by(measurement.date.desc()).first()
    year_before = dt.date(2017, 8, 23) - dt.timedelta(days = 365)
    most_active = session.query(measurement.station, func.count(measurement.station)).\
        group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()[0]
    temperature = session.query(measurement.date, measurement.tobs).\
        filter(measurement.date >= year_before).filter(measurement.station == most_active).all()
    return jsonify(dict(temperature))

@app.route("/api/v1.0/<start>")
def start_date(start):
    min_max_avg = session.query(func.min(measurement.tobs), func.max(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date >= start).all()
    TMIN = min_max_avg[0][0]
    TMAX = min_max_avg[0][1]
    TAVG = min_max_avg[0][2]
    start_dict = {"Minimum Temperature": TMIN, "Maximum Temperature": TMAX, "Average Temperature": TAVG}
    return jsonify(start_dict)

@app.route("/api/v1.0/<start>/<end>")
def start_and_end_date(start, end):
    min_max_avg = session.query(func.min(measurement.tobs), func.max(measurement.tobs),func.avg(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= end).all()
    TMIN = min_max_avg[0][0]
    TMAX = min_max_avg[0][1]
    TAVG = min_max_avg[0][2]
    start_and_end_dict = {"Minimum Temperature": TMIN, "Maximum Temperature": TMAX, "Average Temperature": TAVG}
    return jsonify(start_and_end_dict)

if __name__ == "__main__":
   app.run(debug=True)
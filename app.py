import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
        f"/api/v1.0/<start> and /api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    
    last_year = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date=last_year[0]
    # Calculate the date 1 year ago from the last data point in the database
    one_year_ago = dt.datetime.strptime(last_date,'%Y-%m-%d') - dt.timedelta(days=365)
    # Perform a query to retrieve the data and precipitation scores
    one_year_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    one_year_dict = dict(one_year_data)
    
    return jsonify(one_year_dict)

@app.route("/api/v1.0/stations")
def stations():
    
    most_active_stations = session.query(Measurement.station).\
    group_by(Measurement.station).\
    order_by(Measurement.station).all()
    
    stations = list(np.ravel(most_active_stations))
    
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():
    
    last_year = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date=last_year[0]
    one_year_ago = dt.datetime.strptime(last_date,'%Y-%m-%d') - dt.timedelta(days=365)
    
    date_temp = session.query(Measurement.date,Measurement.tobs).filter(Measurement.date >= one_year_ago).all()
    
    date_temp_list = list(date_temp)
    
    return jsonify(date_temp_list)

@app.route("/api/v1.0/<start>")
def start(start=None):
    
    start_temps = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    start_temps_list = list(start_temps)
    
    return jsonify(start_temps_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start = None, end = None):
    
    start_end_temps = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()
    
    se_temps_list = list(start_end_temps)
    
    return jsonify(se_temps_list)

if __name__ == '__main__':
    app.run(debug=True)

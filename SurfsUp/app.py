# Import the dependencies.

import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
from flask import Flask, jsonify
from dateutil.relativedelta import relativedelta
app = Flask(__name__)

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

#reflect db
Base = automap_base()

#reflect tables
Base.prepare(autoload_with=engine)

#save references
measurement= Base.classes.measurement
station = Base.classes.station

#create a session
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
        "Available Routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/temp/start<br/>"
        "/api/v1.0/temp/start/end"
    )

#------precip route

@app.route('/api/v1.0/precipitation')
def precipitation():

    #calc last data year
    year_ago = session.query(func.max(measurement.date)).scalar()
    year_ago = dt.datetime.strptime(year_ago, '%Y-%m-%d')
    over_year = year_ago - dt.timedelta(days=365)

    #last 12 months
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= over_year).all()

    #convert query results to dictionary
    precip = {date: prcp for date, prcp in results}
    return jsonify(precip)


#------stations route

@app.route('/api/v1.0/stations')
def stations():

    #query stations list
    results = session.query(station.station).all()

    #convert results to list
    stations = list(np.ravel(results))
    return jsonify({'Stations': stations})


#------temp oberservation route

@app.route("/api/v1.0/tobs")
def temp_monthly():
    
    #calc last data year
    past_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    #query temps for past year
    results = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= past_year).all()
    temperatures = list(np.ravel(results))
    return jsonify({'temps': temperatures})


#------temp stats route

@app.route("/api/v1.0/temp/<start>")
def temperature_stats_start(start):

    #convert date string to datetime
    start_date = dt.datetime.strptime(start, '%Y-%m-%d')

    #query temp stats for the year
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()
    
    #convert query to dictionary
    temp_stats = {
        "min temperature": results[0][0],
        "avg temperature": results[0][1],
        "max temperature": results[0][2]
    }
    return jsonify(temp_stats)


@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):

    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]
    if not end:
        results = session.query(*sel).filter(measurement.date >= start).all()
        temps = list(np.ravel(results))
        return jsonify({'temps': temps})

    results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()
    temps = list(np.ravel(results))

    temp_stats = {
        "min temperature": results[0][0],
        "avg temperature": results[0][1],
        "max temperature": results[0][2]
    }
    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)
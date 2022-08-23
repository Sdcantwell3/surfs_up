#################################################
# Import the Flask Dependency
#################################################
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
#Set up the Database and Flask
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")

#Reflect the databas into our classes.

Base = automap_base()

#Reflect the tables.

Base.prepare(engine, reflect=True)

#Save the table references

Measurement = Base.classes.measurement
Station = Base.classes.station

#Create our session link from Python to our database.

session = Session(engine)

#Creating a flask app - the below code makes an app called "app". All routes are entered after app = Flask(__name__) for proper functionality

app = Flask(__name__)

#################################################
# Create the Welcome Route
## When creating routes we follow the naming convention "/api/v1.0/" followed by the name of the route.
#################################################

@app.route("/")
def welcom():
    return(
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )

#################################################
# Precipitation Route
##Every time you create a new route, your code should be aligned to the left in order to avoid errors
##We'll use jsonify() to format our results into a JSON structured file
#################################################

@app.route("/api/v1.0/precipitation")

def precipitation():
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
   precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_year).all()
   precip = {date: prcp for date, prcp in precipitation}
   return jsonify(precip)
   
#################################################
# Stations Route
## We use 'ravel' to unravel our results into one-dimensional arrays.
#################################################

@app.route("/api/v1.0/stations")

def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify(stations=stations)

#################################################
# Monthly Temperature Route
#################################################

@app.route("/api/v1.0/tobs")

def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)   

#################################################
# Statistics Route

#Since we need to determine the starting and ending date, add an 'if-not' statement to our code.
#This will help us accomplish a few things. We'll need to query our database using the list that
#we just made. Then, we'll unravel the results into a one-dimensional array and convert them to a
#list. Finally, we will jsonify our results and return them
#################################################

@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        results = session.query(*sel).\
            filter(Measurement.date >= start).\
            filter(Measurement.date <= end).all()
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

#################################################
# Finish
#################################################
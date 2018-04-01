# import dependencies
import numpy as np
import datetime as dt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sqlalchemy
from sqlalchemy import create_engine,inspect,func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify

# create an engine to a SQLite database file called `hawaii.sqlite`
engine = create_engine('sqlite:///hawaii.sqlite')

# reflect Database and tables into ORM class
Base = automap_base()
Base.prepare(engine,reflect=True)
Station = Base.classes.station
Measurement = Base.classes.measurement

# create a session
session = Session(engine)

# since the last date point in the dataset is back in August 2017, change current date to one year prior to today
current_date = dt.date.today() - dt.timedelta(days=365)
# make the lookback period as 12 months from current date
lookback_date = current_date - dt.timedelta(days=365)

# set up Flask
app = Flask(__name__)

# define routes
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        "Available Routes:<br/>"
        "<a href='http://localhost:5000/api/v1.0/precipitation'>/api/v1.0/precipitation</a> <br/>"
        "<a href='http://localhost:5000/api/v1.0/stations'>/api/v1.0/stations</a> <br/>"
        "<a href='http://localhost:5000/api/v1.0/tobs'>/api/v1.0/tobs</a> <br/>"
        "<a href='http://localhost:5000/api/v1.0/start_date/'>/api/v1.0/start_date/end_date(optional)<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """return a dictionary of dates and average precipitation observations from the last year"""
    # query the average precipitation of last 12 months, group and order by date
    result = session.query(Measurement.date, func.avg(Measurement.prcp))\
    .filter(Measurement.date >= lookback_date)\
    .filter(Measurement.date < current_date)\
    .group_by(Measurement.date)\
    .order_by(Measurement.date).all()
    
    # create a dictionary for precipitation
    precipitation = {}
    # add data row by row to the dictorary
    for line in result:
        date = line[0]
        prcp = line[1]
        precipitation[date] = prcp

    #return results in json format
    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
	"""return a list of stations from the dataset"""
	# qurey the station table
	result = session.query(Station.name).all()
	# Convert list of tuples into a list of stations
	station_list = list(np.ravel(result))
	return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def temporature():
    """return temporature observations from the last year"""
    # query the average temporature of last 12 months
    result = session.query(Measurement.tobs).filter(Measurement.date >= lookback_date)\
    .filter(Measurement.date < current_date).all()

    # convert result into a list of data converted in int type, otherwise json cannot serialize it
    temporatures = list(np.ravel(result))
    temp = []
    for t in temporatures:
    	temp.append(int(t))
    #return results in json format
    return jsonify(temp)

# specify end_date as an optional variable to the path
@app.route("/api/v1.0/<start_date>/", defaults = {'end_date': None})
@app.route("/api/v1.0/<start_date>/<end_date>/")
def temp_lookup(start_date,end_date):
	try:
		# check if start_date and end_date are entered in the correct date format
		start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
		if end_date:
			end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
		# when end_date is not provided, query the data with date greater or equal to start_date
		if end_date is None:
			result = {}
			min = session.query(Measurement.date,func.min(Measurement.tobs))\
			    .filter(Measurement.date >= start_date).all()
			max = session.query(Measurement.date,func.max(Measurement.tobs))\
			    .filter(Measurement.date >= start_date).all()    
			avg = session.query(Measurement.date,func.avg(Measurement.tobs))\
			    .filter(Measurement.date >= start_date).all()    
			    
			result['TMIN'] = min[0][1]
			result['TMAX'] = max[0][1]
			result['TAVG'] = avg[0][1]

			return jsonify(result)
		# when end_date is provided, query the data between start_date and end_date, both inclusive
		result = {}
		min = session.query(Measurement.date,func.min(Measurement.tobs))\
		    .filter(Measurement.date >= start_date)\
		    .filter(Measurement.date <= end_date).all()
		max = session.query(Measurement.date,func.max(Measurement.tobs))\
		    .filter(Measurement.date >= start_date)\
		    .filter(Measurement.date <= end_date).all()  
		avg = session.query(Measurement.date,func.avg(Measurement.tobs))\
		    .filter(Measurement.date >= start_date)\
		    .filter(Measurement.date <= end_date).all()   
		    
		result['TMIN'] = min[0][1]
		result['TMAX'] = max[0][1]
		result['TAVG'] = avg[0][1]
		return jsonify(result)
	# if start_date or end_date not entered in the correct date format, show reminder for correct format
	except ValueError:
		return 'Please enter date in YYYY-MM-DD format'


if __name__ == '__main__':
	app.run(debug=True)
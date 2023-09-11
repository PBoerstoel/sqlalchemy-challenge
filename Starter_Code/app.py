# Import the dependencies.
from flask import Flask, jsonify
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine) #use automap to reflect database

# reflect the tables
measure = Base.classes.measurement
station = Base.classes.station #putting tables as variables

# Save references to each table


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
    return (
        f"Welcome to the Hawaii weather API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"For the destinations with start and end, you have to replace 'start' and 'end' with a beginning and end date.<br/>"
        f"Please format dates in YYYY-MM-DD format!"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    last_date = session.query(measure.date).order_by(measure.date.desc()).first() #find last date
    last_date_dt = dt.datetime.strptime(last_date[0],'%Y-%m-%d') #make it into a datetime object
    year_ago = last_date_dt - dt.timedelta(days=365) #use datetime to find one year before then
    prcp_data = session.query(measure.prcp,measure.date).filter(measure.date >=year_ago).all() 
    #query date and precipitation when date is more or equal to a year ago
    prcp_only =[]
    date_only=[] #empty lists to be filled with date and precipitation data to make making the dictionary easier
    for i in range(len(prcp_data)):
        prcp_only.append(prcp_data[i][0])
        date_only.append(prcp_data[i][1])
    prcp_dict=dict(zip(date_only,prcp_only))  
    #zip function pairs first object of first list and first object of second. Makes it easy to make the dictionary
    return jsonify(prcp_dict) #return jsonified dictionary

@app.route("/api/v1.0/stations")
def stations():
    station_list=session.query(station.name, station.station).all() #get station name and code
    station_py_list = []
    station_code=[] #again, lists to be filled with data to make dictionary easier to form
    for i in station_list:
        station_py_list.append(i[0])
        station_code.append(i[1])
    return jsonify(dict(zip(station_py_list, station_code))) #zip function again. jsonified dict
#will return dictionary in form station_name:station_code

@app.route("/api/v1.0/tobs")
def tobs():
    last_date = session.query(measure.date).order_by(measure.date.desc()).first() #last date
    last_date_dt = dt.datetime.strptime(last_date[0],'%Y-%m-%d')
    year_ago = last_date_dt - dt.timedelta(days=365) #year ago
    active= session.query(measure.station,func.count(measure.station)).\
    group_by(measure.station).order_by(func.count(measure.station).desc()).all()
    #use query to group count of measurements by station, then sort by number of measurements
    #first item in list will be most active
    temp_data = session.query(measure.tobs,measure.date).filter(measure.date >=year_ago).\
    filter(measure.station == active[0][0]).all()
    #query years worth of data from active station. Similar to in precipitation route
    py_list_temp =[]
    date_only=[] #lists to be filled for dictionary
    for i in range(len(temp_data)):
        py_list_temp.append(temp_data[i][0])
        date_only.append(temp_data[i][1])
    return jsonify(dict(zip(date_only,py_list_temp))) #create and return jsonified dict

@app.route("/api/v1.0/<start>")
def startonly(start): #input start date
    dt_date = dt.datetime.strptime(str(start),"%Y-%m-%d") #convert start date to datetime
    data=session.query(func.min(measure.tobs),func.max(measure.tobs),func.avg(measure.tobs)).\
        filter(measure.date >= dt_date).all() #query where date > input date
    #also uses min, max, avg functions
    data_py=[] #empty list to be filled to convert data types
    for i in data[0]:
        data_py.append(i)
    return jsonify(dict(zip(["min","max","average"],data_py))) #return dict of results

@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    start_dt_date = dt.datetime.strptime(str(start),"%Y-%m-%d") #convert start date to datetime
    end_dt_date = dt.datetime.strptime(str(end),"%Y-%m-%d") #convert end date to datetime
    data=session.query(func.min(measure.tobs),func.max(measure.tobs),func.avg(measure.tobs)).\
        filter(measure.date >= start_dt_date).filter(measure.date <= end_dt_date).all()
    #query filtered by date more than start date and date less than end date
    data_py=[] #empty list to convert datatype
    for i in data[0]:
        data_py.append(i)
    return jsonify(dict(zip(["min","max","average"],data_py)))


if __name__ == "__main__":
    app.run(debug=True)
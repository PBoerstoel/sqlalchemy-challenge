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
station = Base.classes.station

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
        f"For the destinations with start and end, you have to include a beginning and end date.<br/>"
        f"Please format dates in YYYY-MM-DD format!"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    lastdate = session.query(measure.date).order_by(measure.date.desc()).first()
    lastdatedt = dt.datetime.strptime(lastdate[0],'%Y-%m-%d')
    yearago = lastdatedt - dt.timedelta(days=365)
    prcpdata = session.query(measure.prcp,measure.date).filter(measure.date >=yearago).all()
    prcponly =[]
    dateonly=[]
    for i in range(len(prcpdata)):
        prcponly.append(prcpdata[i][0])
        dateonly.append(prcpdata[i][1])
    prcp_dict=dict(zip(dateonly,prcponly))
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    stationlist=session.query(station.name, station.station).all()
    stationpylist = []
    stationcode=[]
    for i in stationlist:
        stationpylist.append(i[0])
        stationcode.append(i[1])
    return jsonify(dict(zip(stationpylist, stationcode)))

@app.route("/api/v1.0/tobs")
def tobs():
    lastdate = session.query(measure.date).order_by(measure.date.desc()).first()
    lastdatedt = dt.datetime.strptime(lastdate[0],'%Y-%m-%d')
    yearago = lastdatedt - dt.timedelta(days=365)
    active= session.query(measure.station,func.count(measure.station)).\
    group_by(measure.station).order_by(func.count(measure.station).desc()).all()
    tempdata = session.query(measure.tobs,measure.date).filter(measure.date >=yearago).\
    filter(measure.station == active[0][0]).all()
    acttemp =[]
    dateonly=[]
    for i in range(len(tempdata)):
        acttemp.append(tempdata[i][0])
        dateonly.append(tempdata[i][1])
    return jsonify(dict(zip(dateonly,acttemp)))

@app.route("/api/v1.0/<start>")
def startonly(start):
    dtdate = dt.datetime.strptime(str(start),"%Y-%m-%d")
    data=session.query(func.min(measure.tobs),func.max(measure.tobs),func.avg(measure.tobs)).\
        filter(measure.date >= dtdate).all()
    datapy=[]
    for i in data[0]:
        datapy.append(i)
    return jsonify(dict(zip(["min","max","average"],datapy)))

@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    startdtdate = dt.datetime.strptime(str(start),"%Y-%m-%d")
    enddtdate = dt.datetime.strptime(str(end),"%Y-%m-%d")
    data=session.query(func.min(measure.tobs),func.max(measure.tobs),func.avg(measure.tobs)).\
        filter(measure.date >= startdtdate).filter(measure.date <= enddtdate).all()
    datapy=[]
    for i in data[0]:
        datapy.append(i)
    return jsonify(dict(zip(["min","max","average"],datapy)))


if __name__ == "__main__":
    app.run(debug=True)
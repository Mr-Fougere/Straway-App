# python 3.8

import inspect
import os
from os import error
from random import randint, random
import sys
from types import NoneType
from unittest import result
import requests
import random
import string
from asyncio.windows_events import NULL
import json
from sqlite3 import Date
import mysql.connector
from datetime import date, datetime, timedelta
from mysql.connector import errorcode
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename

#-----------CONFIG ----------------#

config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'raise_on_warnings': True
}

app = Flask(__name__)
CORS(app)
app.config["IMAGE_UPLOADS"]= "C:/Users/alexa/Documents/Projets/Straway-app/static/uploads"
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

#-----------CONSTANTES ----------------#

DB_NAME = "straway_db"
TABLES = {}
IP = "127.0.0.1"
COL_TYPES={"varchar":"text","int":"number","datetime":"date","json":"json","text":"text","boolean":"number","float":"number"}
ABC123= string.ascii_letters+string.digits
TABLES['users'] = (
    "CREATE TABLE `users` ("
    "  `id` int(255) NOT NULL AUTO_INCREMENT,"
    "  `first_name` varchar(20) NOT NULL,"
    "  `last_name` varchar(20) NOT NULL,"
    "  `email` varchar(20) NOT NULL,"
    "  `password` varchar(255) NOT NULL,"
    "  `roles` int(1) NOT NULL DEFAULT 0,"
    "  `picture` varchar(255),"
    "  `pots` json ,"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB")

TABLES['pots'] = (
    "CREATE TABLE `pots` ("
    "  `id` int(255) NOT NULL AUTO_INCREMENT,"
    "  `ip` int(255) NOT NULL UNIQUE,"
    "  `name` varchar(20) NOT NULL,"
    "  `collection` varchar(20) NOT NULL,"
    "  `model` varchar(20) NOT NULL,"
    "  `plant_types` json NOT NULL,"
    "  `current_plant` int(255),"
    "  `release_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,"
    "  `temperature` float,"
    "  `humidity_rate` int(5),"
    "  `tank_level` int(5) ,"
    "  `sunshine_rate` int(5),"
    "  `price` float,"
    "  `picture` varchar(255),"
    "  `is_connected` boolean NOT NULL DEFAULT 0,"
    "  PRIMARY KEY (`id`),"
    " FOREIGN KEY (`current_plant`) REFERENCES plants(`id`)"
    ") ENGINE=InnoDB")

TABLES['plants'] = (
    "CREATE TABLE `plants` ("
    "  `id` int(255) NOT NULL AUTO_INCREMENT,"
    "  `name` varchar(20) NOT NULL,"
    "  `type` varchar(20) NOT NULL,"
    "  `temperature` float,"
    "  `humidity_rate` int(5),"
    "  `sunshine_rate` int(5),"
    "  `picture` varchar(255),"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB") 

#-----------FONCTIONS ----------------#

def create_database(cursor, db_name):
    try:
        print("Creating database {}: ".format(db_name), end='')
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(db_name))
        print("Database {} created successfully.".format(DB_NAME))
        cnx.database = db_name
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_DB_CREATE_EXISTS:
            cursor.execute("USE {}".format(DB_NAME))
            print("Databse "+db_name+" already exists")
            cnx.database = DB_NAME
        else:
            print(err.msg)

def create_tables(database, cursor, tables):
    cnx.database = database
    for table_name in tables:
        table_description = tables[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("Table "+format(table_name)+" already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

def form_table(database, json_table):
  cnx.database= database
  query="CREATE TABLE `"+json_table["tableName"]+"` (`id` int(255) NOT NULL AUTO_INCREMENT,PRIMARY KEY (`id`),"
  for key in json_table:
    if key != "tableName":
      if json_table[key] == "varchar":
        query+=" `"+key+"` "+json_table[key]+"(255),"
      else:  
        query+=" `"+key+"` "+json_table[key]+","
  query = query[0:-1]
  query+=") ENGINE=InnoDB"
  return query 

def readRow(database, table, id):
    cnx.database = database
    cursor = cnx.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM "+table+" WHERE id = "+str(id))
        result = cursor.fetchall()[0]
    except:
        return "Error : doesn't exists"
    else:
        return result

def insert_into(database, table, object):
    cursor.execute("DESCRIBE "+database+"."+table)
    indexList = cursor.fetchall()
    values_tags = ""
    values = ""
    for index in indexList:
        if index[0] != "id":
            values_tags = values_tags+str(index[0])+", "
            values = values+"%s, "
    values_tags = values_tags[0:-2]
    values = values[0:-2]
    insert = ("INSERT INTO "+table+" "
              "("+values_tags+") "
              "VALUES ("+values+")")
    cnx.database = database
    cursor.execute(insert, object)
    try:
        cnx.commit()
    except mysql.connector.Error as err:
        print(err.msg)
    else:
        print("Inserted values into table "+table)

def deleteRow(database, table, conditions):
    cnx.database = database
    cursor.execute("DELETE FROM "+table + " WHERE "+conditions+";")
    try:
        cnx.commit()
    except mysql.connector.Error as err:
        print(err.msg)
    else:
        print("Deleted values into table "+table)

def updateRow(database, table, conditions, new_values):
    cnx.database = database
    values_to_up = ""
    for attr, value in new_values.items():
        values_to_up = values_to_up+attr+"='"+str(value)+"', "
    values_to_up = values_to_up[0:-2]
    update = ("UPDATE "+table + " "
              "SET "+values_to_up+""
              "WHERE "+conditions+";")
    print(update)
    cursor.execute(update)
    cnx.commit()

def getNameColumns(database, table):
    cursor.execute("DESCRIBE "+database+"."+table)
    columnsList = cursor.fetchall()
    names = []
    for column in columnsList:
        names.append(column[0])
    return names

def getTypeTable(database, table):
    cnx.database = database
    cursor.execute("SHOW COLUMNS FROM "+table)
    table = cursor.fetchall()
    values = {}
    for column in table:
        if column[0] != "id":
            values[column[0]] = column[1]
    print(values)
    return values

def getClass(classname):
  all_class=inspect.getmembers(sys.modules[__name__])
  chosen_class={}
  for c in all_class:
    if c[0]==classname:
      chosen_class=c[1]
      break
  return chosen_class

def getTables(database):
  cnx.database = database
  cursor.execute("SHOW TABLES")
  tables = cursor.fetchall()
  list_table=[]
  for table in tables:
    list_table.append(table[0])
  print(list_table)
  return list_table

def init_class(self, user):
        attributes = getNameColumns('straway_db', self.TABLENAME)
        for attr in attributes:
            try:
                user[attr]
            except:
                setattr(self, attr, NULL)
            else:
                setattr(self, attr, user[attr])

@classmethod
def create(self, values):  # function add from database
        current_class=getClass(self.TABLENAME)
        new = current_class(values)
        delattr(new, 'id')
        insert_into(DB_NAME, self.TABLENAME, list(new.__dict__.values()))
        print("New "+self.NAME+" created ")

@classmethod
def read(self, id):  # function read from database
        current_class=getClass(self.TABLENAME)
        rowValues = readRow(DB_NAME, self.TABLENAME, id)
        return current_class(rowValues)

@classmethod
def delete(self, id): # function delete from database 
        deleteRow(DB_NAME, self.TABLENAME, "id="+str(id))
        print(self.NAME+" "+str(id)+" deleted")

def update(self, updated):
        updateRow(DB_NAME, self.TABLENAME, "id="+str(self.id), updated)
        print(self.NAME+" "+str(self.id)+" updated")

@classmethod
def readAll(self,chosen_values):
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM "+self.TABLENAME)
        fetch = cursor.fetchall()
        all = []
        if chosen_values:
          columns=chosen_values
        else:
          columns=getNameColumns(DB_NAME,self.TABLENAME)
        for f in fetch:
          obj={}
          for c in columns:
            try:
              obj[c] = f[c]
            except:
              if c == "picture":
                obj[c] = "Icon Logo.svg"
            all.append(obj)

        return all

def createClass(name):
  globals()[name] = type(name, 
              (), 
              {"TABLENAME":name, 
                "NAME":name,
               "__init__": init_class,
               "create":create,
               "delete":delete,
               "read":read,
               "readAll":readAll,
               "update":update,
               }
                )
  
#-----------CLASSES ----------------#
tables_index=getTables(DB_NAME)
for table in tables_index:
  
  try:
    createClass(table)
  except:
    print("error: class not created")
  else:
    print(getClass(table).read(1))
    print("class "+table+" created successfully")
#-----------PROGRAMME ----------------#

create_database(cursor, DB_NAME)
create_tables(DB_NAME, cursor, TABLES)

#---------Routes---------------------#

@app.route('/')
def index():
  tables=getTables(DB_NAME)
  if not request.args.get("interface"):
    tables_index=[]
    for table in tables:
      tables_index.append("http://127.0.0.1:5000/list/"+table)

    return tables_index 
  else:
    return render_template('index.html',tables=tables)
  
@app.route('/show/<type>/<id>',methods=['GET'])
def showing(type,id):
  current_class=getClass(type)
  try:
    response=current_class.read(id).__dict__
  except mysql.connector.Error as err:
    return err
  else: 
    if not request.args.get("interface"):
        return response
    else:
        return render_template("list.html", data=[response], type=type)

@app.route('/delete/<type>/<id>',methods=['GET'])
def deleting(type,id):
    current_class=getClass(type)
    try:
      current_class.delete(id)
    except mysql.connector.Error as err:
        return err
    else:
        if not request.args.get("interface"):
            return type+" "+id+" deleted successfully"
        else:
            return render_template("display.html",type=type,message=type+" "+id+" deleted successfully")


@app.route('/edit/<type>/<id>', methods=['POST', 'GET'])
def editing(type, id):
    current_class=getClass(type)
    response=current_class.read(id)
    if request.method=="POST":
        try:
          current_class.update(response,request.form)
        except mysql.connector.Error as err:
            return "Error : "+err.msg
        else:
          if not request.args.get("interface"):
            return type+" "+id+" edit successfully"
          else:
            return render_template("display.html",type=type,message=type+" "+id+" edit successfully")

    else:
        delattr(response,'id')
        return render_template("create.html", data=response.__dict__, type=type,values=getTypeTable(DB_NAME, type),id=id,col_types=COL_TYPES)

@app.route('/list/<type>', methods=['GET'])
def listing(type):
    current_class=getClass(type)
    response = current_class.readAll(["id","name","picture"])
    if not request.args.get("interface"):
        return response
    else:
        return render_template("list.html", data=response, type=type)

@app.route('/create/<type>', methods=['GET', 'POST'])
def creating(type):
    current_class=getClass(type)
    if request.method == "POST":
        json_request = json.loads(json.dumps(request.form))
        try:
          image = request.files.get("picture",None)
          if image.filename=="":
              print("Filename is invalid")
          else:
              random_name=  ''.join(random.choice(ABC123) for i in range(50))+".png"
              image.save(os.path.join(app.config["IMAGE_UPLOADS"],random_name))
          json_request["picture"]=random_name  

        except Exception as e:
          print(e)
            
        if type == "table":
          create_tables(DB_NAME, cursor,{"newtable":form_table(DB_NAME,json_request)})
          createClass(json_request["tableName"])
        else:
          current_class.create(json_request)
        if not request.args.get("interface"):
            return type+" created successfully"
        else:
            return render_template("display.html",type=type,message=type+" create successfully")
    else:
      if type=="table":
        values=""
      else:
        values=getTypeTable(DB_NAME, type)
      return render_template('create.html', values=values, type=type,data="",col_types=COL_TYPES)

#-------------LOOP-----------------#
if __name__ == "__main__":
    app.run()
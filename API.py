# python 3.8

import inspect
from os import error
from random import randint, random
import sys
import requests
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
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

#-----------CONSTANTES ----------------#

DB_NAME = "straway_db"
TABLES = {}
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

test_user = {
    'first_name': "alexandre",
    'last_name': "gaubert",
    'email': "alexandre@gmail.com",
    'password': "password",
    'picture': "iunubi",
    'pots': '{}',
    'roles': 0
}

test_pot = {
    'ip': "162.132.124.123",
    'name': "Pot1",
    'collection': "Collection1",
    'model': "Model1",
    'plant_types': json.dumps([{'nom': 'plante1'}, {'nom': 'plante2'}]),
    'current_plant': 1,
    'release_date': Date(2022, 8, 26),
    'temperature': 23.5,
    'humidity_rate': 30,
    'tank_level': randint(0, 100),
    'sunshine_rate': randint(0, 100),
    'price': 15.99,
    'picture': "",
    'is_connected': randint(0, 1)
}

test_plant = {
    'name': "Plant1",
    'type': "Type1",
    'temperature': 25.5,
    'humidity_rate': 30,
    'sunshine_rate': 40,
    'picture': "",
}

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


def readRow(database, table, id):
    cnx.database = database
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT * FROM "+table+" WHERE id = "+str(id))
    try:
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
    print(insert, object)
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
  all_class=inspect.getmembers(sys.modules[__name__],inspect.isclass)
  chosen_class={}
  for c in all_class:
    if c[0]==classname:
      chosen_class=c[1]
      break
  return chosen_class

def getTables(database):
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
def create(self, user):  # function add from database
        new_user = User(user)
        delattr(new_user, 'id')
        insert_into(DB_NAME, self.TABLENAME, list(new_user.__dict__.values()))
        print("New "+self.NAME+" created : " +
              new_user.first_name.capitalize()+" "+new_user.last_name.capitalize())
@classmethod
def read(self, id):  # function read from database
        rowValues = readRow(DB_NAME, self.TABLENAME, id)
        print(rowValues)
        return User(rowValues)

@classmethod
def delete(self, id): # function delete from database 
        deleteRow(DB_NAME, self.TABLENAME, "id="+str(id))
        print(self.NAME+" "+str(id)+" deleted")

def update(self, updated):
        updateRow(DB_NAME, self.TABLENAME, "id="+str(self.id), updated)
        print(self.NAME+" "+str(self.id)+" updated")

@classmethod
def readAll(self):
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM "+self.TABLENAME)
        fetch = cursor.fetchall()
        all = []
        for f in fetch:
            all.append(f)
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


class User():
    TABLENAME = 'users'
    NAME = "User"

def __init__(self, init):
        attributes = getNameColumns('straway_db', self.TABLENAME)
        for attr in attributes:
            try:
                init[attr]
            except:
                setattr(self, attr, NULL)
            else:
                setattr(self, attr, init[attr])

    @classmethod
    def create(self, entry):  # add new user to database
        new = Pot(entry)
        delattr(new, 'id')
        insert_into(DB_NAME, self.TABLENAME, list(new.__dict__.values()))
        print("New "+self.NAME+" created : "+new.name.capitalize()+" "+new.ip)

    @classmethod
    def read(self, id):  # read user information from database
        rowValues = readRow(DB_NAME, self.TABLENAME, id)
        print(rowValues)
        return Pot(rowValues)

    @classmethod
    def delete(self, id):
        deleteRow(DB_NAME, self.TABLENAME, "id="+str(id))
        print(self.NAME+" "+str(id)+" deleted")

    def update(self, updated):
        updateRow(DB_NAME, self.TABLENAME, "id="+str(self.id), updated)
        print(self.NAME+" "+str(self.id)+" updated")

    @classmethod
    def readAll(self):
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM "+self.TABLENAME)
        fetch = cursor.fetchall()
        all = []
        for f in fetch:
            all.append(f)
        return all

    
    pass


class Pot():

    TABLENAME = 'pots'
    NAME = 'Pot'

    def __init__(self, init):
        attributes = getNameColumns('straway_db', self.TABLENAME)
        for attr in attributes:
            try:
                init[attr]
            except:
                setattr(self, attr, NULL)
            else:
                setattr(self, attr, init[attr])

    @classmethod
    def create(self, entry):  # add new user to database
        new = Pot(entry)
        delattr(new, 'id')
        insert_into(DB_NAME, self.TABLENAME, list(new.__dict__.values()))
        print("New "+self.NAME+" created : "+new.name.capitalize()+" "+new.ip)

    @classmethod
    def read(self, id):  # read user information from database
        rowValues = readRow(DB_NAME, self.TABLENAME, id)
        print(rowValues)
        return Pot(rowValues)

    @classmethod
    def delete(self, id):
        deleteRow(DB_NAME, self.TABLENAME, "id="+str(id))
        print(self.NAME+" "+str(id)+" deleted")

    def update(self, updated):
        updateRow(DB_NAME, self.TABLENAME, "id="+str(self.id), updated)
        print(self.NAME+" "+str(self.id)+" updated")

    @classmethod
    def readAll(self):
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM "+self.TABLENAME)
        fetch = cursor.fetchall()
        all = []
        for f in fetch:
            all.append(f)
        return all

    pass


class Plant:
    TABLENAME = 'plants'
    NAME = 'Plant'

    def __init__(self, init):
        attributes = getNameColumns('straway_db', self.TABLENAME)
        for attr in attributes:
            try:
                init[attr]
            except:
                setattr(self, attr, NULL)
            else:
                setattr(self, attr, init[attr])

    @classmethod
    def create(self, entry):  # add new user to database
        new = Plant(entry)
        delattr(new, 'id')
        insert_into(DB_NAME, self.TABLENAME, list(new.__dict__.values()))
        print("New "+self.NAME+" created : "+new.name.capitalize())

    @classmethod
    def read(self, id):  # read user information from database
        rowValues = readRow(DB_NAME, self.TABLENAME, id)
        print(rowValues)
        return Plant(rowValues)

    @classmethod
    def delete(self, id):
        deleteRow(DB_NAME, self.TABLENAME, "id="+str(id))
        print(self.NAME+" "+str(id)+" deleted")

    def update(self, updated):
        updateRow(DB_NAME, self.TABLENAME, "id="+str(self.id), updated)
        print(self.NAME+" "+str(self.id)+" updated")

    @classmethod
    def readAll(self):
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM "+self.TABLENAME)
        fetch = cursor.fetchall()
        all = []
        for f in fetch:
            all.append(f)
        return all

    pass
#-----------PROGRAMME ----------------#


create_database(cursor, DB_NAME)
create_tables(DB_NAME, cursor, TABLES)

#---------Routes---------------------#


@app.route('/')
def index():
  tables=getTables(DB_NAME)
  if not request.args.get("interface"):
    return tables 
  else:
    return render_template('index.html',tables=tables)


@app.route('/show/<type>/<id>',methods=['GET'])
def showing(type,id):
  current_class=getClass(type[0:-1].capitalize())
  try:
    response=current_class.read(id).__dict__
  except mysql.connector.Error as err:
    return err
  else: 
    return response

@app.route('/delete/<type>/<id>',methods=['GET'])
def deleting(type,id):
    current_class=getClass(type[0:-1].capitalize())
    try:
      current_class.delete(id)
    except mysql.connector.Error as err:
        return err
    else:
        return type+" "+id+" successfully deleted"


@app.route('/edit/<type>/<id>', methods=['POST', 'GET'])
def editing(type, id):
    current_class=getClass(type[0:-1].capitalize())
    response=current_class.read(id)
    if not request.args.get("interface") and request.method=='POST':
        try:
          current_class.update(response,request.form)
        except mysql.connector.Error as err:
            return "Error : "+err.msg
        else:
            return type+" "+id+" updated successfully"
    else:
        delattr(response,'id')
        return render_template("create.html", data=response.__dict__, type=type,values=getTypeTable(DB_NAME, type),id=id)


@app.route('/list/<type>', methods=['GET'])
def listing(type):
    current_class=getClass(type[0:-1].capitalize())
    response = current_class.readAll()
    if not request.args.get("interface"):
        return response
    else:
        return render_template("list.html", data=response, type=type)

@app.route('/create/<type>', methods=['GET', 'POST'])
def creating(type):
    current_class=getClass(type[0:-1].capitalize())
    if request.method == "POST":
        json_request = json.loads(json.dumps(request.form))
        print(json_request)
        current_class.create(json_request)
        return type+" created successfully"
    else:
        return render_template('create.html', values=getTypeTable(DB_NAME, type), type=type,data="")

#-------------LOOP-----------------#
getTables(DB_NAME)
if __name__ == "__main__":
    app.run()

"""
Created on Tue May 4 12:00:00 2021

@author: Mukesh Kumar | Algo8.ai

"""
# standard library for sql connection and fetch data from sql
from sqlalchemy import create_engine,text
import pandas as pd
import logging as lg
import configparser
import logging
import numpy as np
import urllib.parse
import os
# Get the absolute path of the current file
file_path = os.path.abspath(__file__)
# Construct the relative path to the logs directory
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(file_path))), 'logs')
# Construct the relative path to the config directory
config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(file_path)))), 'config')



class DatabaseHandler:
    def __init__(self):
        self.config_Url = configparser.ConfigParser()
        self.config_Url.read('database/database.ini')
        self.name = self.config_Url["db_credentials"]["name"]
        self.user = self.config_Url["db_credentials"]["user"]
        self.password = self.config_Url["db_credentials"]["password"]
        self.host = self.config_Url["db_credentials"]["host"]
        self.port = self.config_Url["db_credentials"]["port"]
        self.dbtype = self.config_Url["db_credentials"]["dbtype"]
        self.db = self.config_Url["db_credentials"]["db"]
        self.table_name = self.config_Url["db_credentials"]["table"]

        DATABASES = {
            self.db:{
                'NAME': self.name,
                'user': self.user,
                'password': self.password,
                'host': self.host,
                'port': self.port,
            },
        }

        # choose the database to use
        db = DATABASES[self.db]

        # construct an engine connection string
        if self.dbtype == "postgres":
            estring = "postgresql+psycopg2"
        elif self.dbtype == "mysql":
            estring = "mysql+pymysql"

        # handle special characters in username and password
        if "@" in db['user'] or "@" in db['password']:
            user = urllib.parse.quote(db['user'])
            password = urllib.parse.quote(db['password'])
            engine_string = estring+"://"+user+":"+password+"@"+db['host']+":"+db['port']+"/"+db['NAME']
        else:
            engine_string = estring+"://{user}:{password}@{host}:{port}/{database}".format(
                user = db['user'],
                password = db['password'],
                host = db['host'],
                port = db['port'],
                database = db['NAME']
            )

        # create sqlalchemy engine
        try:
            self.engine = create_engine(engine_string)
            logging.info("Successfully Connected to database.")
        except Exception as e:
            logging.error(f"Error while connecting to database: {e}")
            raise

    def run(self, cols, colvalues,table_name):
        df_feed = pd.DataFrame({cols[i]: [colvalues[i]] for i in range(len(cols))})

        # appending to table
        try:
            df_feed.to_sql(table_name, self.engine, if_exists='append', index=False)
            logging.info("Data Pushed Into DB")
        except Exception as e:
            logging.error(f"Error while pushing data to database: {e}")
            raise

    def run_df(self,table_name, df):
        # df_feed = pd.DataFrame({cols[i]: [colvalues[i]] for i in range(len(cols))})

        # appending to table
        try:
            df.to_sql(table_name, self.engine, if_exists='append', index=False)
            logging.info("Data Pushed Into DB")
        except Exception as e:
            logging.error(f"Error while pushing data to database: {e}")
            raise

    def get_engine(self):
        return self.engine
    
    def execute_query(self,query):
        try:
            print("engine",self.engine)
            with self.engine.begin() as conn:
                conn.execute(text(query))
                logging.info("SQL Updated")
            return (True, "Sql Updated")

        except Exception as e:
            logging.error("not able to run sql query")
            logging.exception(e)
            return (False,"not able to run sql query.")
        
    def execute_insert(self, table_name, columns, values):
        try:
            query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join([':%s' % i for i in range(len(columns))])})"
            with self.engine.begin() as conn:
                conn.execute(text(query), values)
            logging.info("Data inserted into the table.")
            return True, "Data inserted into the table."
        except Exception as e:
            logging.error("Failed to insert data into the table.")
            logging.exception(e)
            return False, "Failed to insert data into the table."


    def fetch_data(self, query):
        try:
            print("Engine",self.engine)
            with self.engine.connect() as conn:
                data = pd.read_sql(text(query), conn)
            logging.info("fetched_data")
            return  data

        except Exception as e:
            logging.error("No info fetched")
            logging.exception(e)
            return (False, "No info fetched")
        
    def execute_query_excel(self, sql, values):
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql), values)
                logging.info("SQL Updated")
                return (True, result.rowcount)

        except Exception as e:
            logging.error("not able to run sql query")
            logging.exception(e)
            return (False, 0)






class Context:
    """
    #How to Run this Module
        we have two class in this module (sql ,postgreSql)
        steps 1:
            import module (from ConnectDb import sql,postgreSql
            import configparser
        steps 2:
            Update your db Credentials on database.ini file For Both SQL and POSTGRESQL.
                example:
                    [SQL]
                    sql_username=admin
                    sql_password=Dev123456
                    sql_ip= localhost
                    sql_port=3306
                    sql_database= db_test
        step 3:
            Load Your Credentials
            config_Url = configparser.ConfigParser()
            config_Url.read('database.ini')
            sql_username = config_Url["SQL"]["sql_username"]
            sql_password = config_Url["SQL"]["sql_password"]
            sql_ip = config_Url["SQL"]["sql_ip"]
            sql_port = config_Url["SQL"]["sql_port"]
            sql_database = config_Url["SQL"]["sql_database"]
        steps 4:
            create an obj for both class if needed ( example : db = sql() , db_postgreSql = postgreSql() )
        steps 5:
            1. For sql
                Call your function to create a engine on Sql ( db_conn = db.connect_with_sql(sql_username, sql_password, sql_ip, sql_port, sql_database)
            2. For postgreSql
                Call your function to create a cursor on postgreSql(db_conn = db_postgreSql.connect_postgreSql())

        steps 6:
            For SQL
            Use Function run_query(query,engine) # Run Any Query Of Sql
            example : query = ("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) VALUES (22, 'Mohit', 32, 'California',20000.00 )")
            Now call function to execute query
            db.run_query(query,db_conn[1]) # db_conn[1] convert tuple  into 'sqlalchemy.engine.base.Engine'.
            Use Function fetch_details(query,engine) # Fetch Any Data From Database
            example : query = "show databases;"
            Now call function to execute query
            db.fetch_details(query, db_conn[1])) # db_conn[1] convert tuple  into 'sqlalchemy.engine.base.Engine'.

            For PostgreSql
            write your any query on postgreSql
            Use Function run_query(query,engine) # Run Any Query Of postgreSql
            example : query = ("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) VALUES (22, 'Mohit', 32, 'California', 20000.00 )")
            Now call function to execute query
            db_postgreSql.run_query(query,db_conn[1]) # db_conn[1] convert tuple  into 'class 'psycopg2.extensions.cursor'
            Function fetch_details(query,cursor) # Fetch Any Data From Database
            query =("SELECT id, name, address, salary  from COMPANY")
            Now call function to execute query
            db_postgreSql.fetch_details(query,conn[1]) # db_conn[1] convert tuple  into 'class 'psycopg2.extensions.cursor'
    """


#import libraries
import requests
import json
import pandas as pd
from src.receiveResponse.CleanBody import clean_body_mail
#import ConnectDb
import numpy as np
import datetime
#import environ
from sqlalchemy import create_engine
from urllib.parse import quote as urlquote

#env = environ.Env()
#environ.Env.read_env('.env')

# graph api credentials
client_id = "09aacaa6-422b-4dcc-9a2f-fc39644f4b32"
client_secret = "SvM8Q~WXrMGl~gvHtkJZkydx.O7UeeD-LA2htdav"
scope = "https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Read.Shared https://graph.microsoft.com/Mail.ReadWrite.Shared https://graph.microsoft.com/Files.Read https://graph.microsoft.com/Files.ReadWrite"
username = "demo@algo8.ai"
password = "AI@algo8"


#SQl Credentials
sql_username="root"
sql_password="Dev123456"
sql_ip="34.132.79.126"
sql_port="3306"
sql_database="certainty"

# create engine for sql engine
connect_query = "mysql+pymysql://"+sql_username+":%s"%urlquote(sql_password)+"@"+sql_ip+":"+sql_port+"/"+sql_database
engine = create_engine(connect_query)

# column name from datframe and create emtpy dataframe with just column names
column_names = ["conversationID","mailID","sendDateTime","hasAttachment","Subject","CleanBody","SenderEmailID","toRecipients","ccRecipients"]

# function to get unique values
def unique(list1):
    # insert the list to the set
    list_set = set(list1)
    # convert the set to the list
    unique_list = (list(list_set))
    return unique_list


def get_access_token():
    # Token request configuration
    token_url = "https://login.microsoftonline.com/08b7cfeb-897e-469b-9436-974e694a8df2/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope,
        "grant_type": "password",
        "username": username,
        "password": password
    }

    # Send token request
    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()

    # Extract and return the access token
    access_token = response.json().get("access_token")
    return access_token

def dumpmailsfunction():

    token = get_access_token()  

    # fetch max datatime in the database
    query_fetch_max_datatime = "select max(sendDateTime) from nagging_mails;"
    df_max_date = pd.read_sql(query_fetch_max_datatime,engine)
    df_max_test_check = str(df_max_date["max(sendDateTime)"][0])
    df_max_test_check = df_max_test_check.replace(" ","T")
    df_max_test_check = df_max_test_check + "Z" 

    #a = "2023-02-11T00:00:00Z"
    #b = "2023-03-10T00:00:00Z"
    #  and (receivedDateTime le 2022-12-17T00:00:00Z)
    # and(receivedDateTime le 2022-08-10T00:00:00Z)
    email_url = 'https://graph.microsoft.com/v1.0/users/demo@algo8.ai/mailFolders/AAMkADk5Y2UxYTdjLWUxNzYtNDA3MS05Mzc4LWE1NzNmN2VhMzE1ZQAuAAAAAAADJMSc0UrESKAS1-u316dMAQBKjFfBgKliQpCbZy8yHgATAABj4jxMAAA=/messages?$filter=(receivedDateTime ge {})'.format(df_max_test_check)
    # header for api call
    headers = {
    'Authorization': 'Bearer {}'.format(token)
    }
    email_response_data = json.loads(requests.get(email_url, headers=headers).text)
    
    #print(email_response_data)
    value_for_While = True
    count = 0
    new_df_combined = pd.DataFrame()
    count_check = 0
    while value_for_While:
        count+=1
        final_list = []
        # iterate over each mail returend by graph api
        for i in range(len(email_response_data["value"])):
            ccRecipients = []
            toRecipients = []
            to_domain = []
            cc_domain = []
            # fetch all the recipients of the mail
            to_count = len(email_response_data["value"][i]["toRecipients"])
            for to_i in range(to_count):
                try:
                    to_domain.append(str(email_response_data["value"][i]["toRecipients"][to_i]["emailAddress"]["address"]).split("@")[1])
                except: to_domain.append(str(email_response_data["value"][i]["toRecipients"][to_i]["emailAddress"]["address"]))
                toRecipients.append(str(email_response_data["value"][i]["toRecipients"][to_i]["emailAddress"]["address"]))
            toRecipients = str(toRecipients)

            to_domain = unique(to_domain)
            # same steps as above for users in CC
            cc_count = len(email_response_data["value"][i]["ccRecipients"])
            for cc_i in range(cc_count):
                cc_domain.append(str(email_response_data["value"][i]["ccRecipients"][cc_i]["emailAddress"]["address"]).split("@")[1])
                ccRecipients.append(str(email_response_data["value"][i]["ccRecipients"][cc_i]["emailAddress"]["address"]))
            ccRecipients = str(ccRecipients)
            cc_domain = unique(cc_domain)  
            ConversationId = email_response_data["value"][i]["conversationId"]
            status,clean_body = clean_body_mail(email_response_data["value"][i]["body"]["content"])
            clean_body = clean_body.encode('utf-8').decode('ascii', 'ignore')
            attachmentPresent = email_response_data["value"][i]["hasAttachments"]
            try:
                emailSender = email_response_data["value"][i]["sender"]["emailAddress"]["address"]
            except: emailSender = ""
            # some processing on send date time fields
            sendDateTime  = email_response_data["value"][i]["sentDateTime"]
            sendDateTime = sendDateTime.replace("T"," ")
            sendDateTime = sendDateTime.replace("Z","")
            sendDateTime = datetime.datetime.strptime(sendDateTime, '%Y-%m-%d %H:%M:%S')
            time_change = datetime.timedelta(hours=5,minutes=30)
            sendDateTime = sendDateTime + time_change
            subject = str(email_response_data["value"][i]["subject"])
            subject = subject.encode('utf-8').decode('ascii', 'ignore')
            id = email_response_data["value"][i]["id"]
            # sequence = dictTest[id]
            list_Values = [ConversationId,id,sendDateTime,attachmentPresent,subject,str(clean_body),emailSender,toRecipients,ccRecipients]
            final_list.append(list_Values)
        df = pd.DataFrame(final_list, columns = column_names)
        print(df)
        status = df.to_sql(name = "nagging_mails",con = engine,if_exists="append", index=False)
        new_df_combined = pd.concat([new_df_combined,df],ignore_index=True)
        print('data transferred to database.')    
        try:
            # post request to get access token and refresh token
            token = get_access_token()
            header2 = {"Authorization": 'Bearer {}'.format(token)}
            email_response_data = json.loads(requests.get(email_response_data["@odata.nextLink"],headers = header2).text)
            value_for_While = True    
        except:
            value_for_While = False
    print("count of internal mails: {}".format(count_check))
    print("count of total iterations: {}".format(count))
    return new_df_combined

dumpmailsfunction()

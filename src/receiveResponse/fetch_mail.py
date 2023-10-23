import requests
import json
import pandas as pd
import time
import pandas as pd
from database.ConnectDb import DatabaseHandler
from datetime import datetime
import time
from src.receiveResponse.utils import clean_body_mail

# Authentication configuration
client_id = "09aacaa6-422b-4dcc-9a2f-fc39644f4b32"
client_secret = "SvM8Q~WXrMGl~gvHtkJZkydx.O7UeeD-LA2htdav"
scope = "https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/Mail.ReadWrite https://graph.microsoft.com/Mail.Read.Shared https://graph.microsoft.com/Mail.ReadWrite.Shared https://graph.microsoft.com/Files.Read https://graph.microsoft.com/Files.ReadWrite"
username = "demo@algo8.ai"
password = "AI@algo8"

db_sql = DatabaseHandler()

# dbcolumns = ['timestamp','receivedDateTime', 'sender', 'receivedOn', 'subject', 'documentTitle', 'po', 'invoicedFrom', 'invoicedTo', 'invoiceDate','dueDate', 'taxId', 'totalBeforeTax','tax', 'totalAfterTax','currency', 'reject','validate','markedForReview','email','invoicePdf','status','comment','validatedOn','reviewedBy','poPDF']

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

def fetch_emails(filter_params):
    # Microsoft Graph API endpoint for fetching emails
    graph_api_endpoint = "https://graph.microsoft.com/v1.0/users/demo@algo8.ai/messages"

    # Fetch emails using Microsoft Graph API
    while True:
        access_token = get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        params = {
            "$select": "sender,receivedDateTime,subject,hasAttachments,body,conversationId",
            "$filter": f"{filter_params}"
        }

        # Fetch emails using Microsoft Graph API
        response = requests.get(graph_api_endpoint, headers=headers, params=params)
        if response.status_code == 401:  # Token expired
            time.sleep(1)  # Sleep for a second to avoid excessive token requests
            continue
        response.raise_for_status()
        emails = response.json().get("value", [])
        return emails


def process_email(email):
    try:
        
        email_data = []  # List to store email-related data for each row
        dt = datetime.now()
        timestamp_data = dt.date()
        columns = ['sender','received_date','subject','repliedByEmployee']
        conversation_id = email.get('conversationId') 
        if conversation_id:
            email_id = email['id']
            sender = email['sender']['emailAddress']['address']
            received_date = email['receivedDateTime']
            subject = email['subject']
            email_body = email['body']['content']
            
            print("subject",subject)
            if subject.startswith('Re:'):
                clean_context = clean_body_mail(email_body)
                # print(clean_context[1])
                values = [sender,received_date,subject,clean_context[1]]
                df = pd.DataFrame([values],columns=columns)
                return df
    except Exception as e:
        print("Error Occured! " ,e)

import multiprocessing

def run_pipeline(args):
    email = args
    return  process_email(email)


def pipeline(start_date_filter, end_date_filter, start_time_filter, end_time_filter):
    try:
        start_time = time.time()
        graph_api_endpoint = "https://graph.microsoft.com/v1.0/users/demo@algo8.ai/messages"
        access_token = get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        print("Code Started")
        
        # Combine date and time filters
        if start_date_filter and start_time_filter and end_time_filter:
            start_datetime = datetime.combine(start_date_filter, start_time_filter)
            end_datetime = datetime.combine(end_date_filter, end_time_filter)
            start_datetime_str = start_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
            end_datetime_str = end_datetime.strftime('%Y-%m-%dT%H:%M:%SZ')
            date_time_filter = f"receivedDateTime ge {start_datetime_str} and receivedDateTime le {end_datetime_str}"
        else:
            date_time_filter = ''
        
        print("Filter:", date_time_filter)  # Added for logging
        
        # Fetch emails based on filters
        filter_params = []
        if date_time_filter:
            filter_params.append(date_time_filter)
        if filter_params:
            filter_query = ' and '.join(filter_params)
            print("Filter Query:", filter_query)  # Added for logging
            emails = fetch_emails(filter_query)
            args_list = [(email) for email in emails]
            # Create a multiprocessing pool and map the function to the arguments
            with multiprocessing.Pool(processes=2) as pool:
                df_list =  pool.map(run_pipeline, args_list)
            final_df = pd.concat(df_list, ignore_index=True, keys=None)  # Set keys=None to avoid repeating column names   
            print("Processing emails completed.")
            end_time = time.time()
            time_taken = end_time-start_time
            print(f"Time taken for Processing:{time_taken}")
            return final_df
    except Exception as e:
        print("Error occurred:", e)  # Added for logging

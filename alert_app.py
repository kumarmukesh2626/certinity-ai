import argparse
import configparser
from flask import Flask,request
import src.config_log as  cf
from email import encoders
# from database.ConnectDb import sql
from src.sent_mail.sentMailpipline import certinaityAI
from src.sent_mail.sendMail import send_mail
import pandas as pd


app = Flask(__name__)

@app.route('/naggMailSent', methods=["POST"])
def fetch_details():
    if request.method == "POST":
        try:
            data = request.json
            projectDescription = data["projectDescription"]
            # time_period = data['timePeriod']
            nagMailSent = certinaityAI(projectDescription)
            return {
                    "funcName": "alert()",
                    "msg": "Alert Sent Successfully",
                    "status": "OK",
                    "statusCode": 200
                }
        except Exception as error:
            return {
                "funcName": "alert()",
                "msg": f"Alert Sending Failed: {error}",
                "status": "Error",
                "statusCode": 500
            }
        except Exception as e:
            print(e)

@app.route('/alert', methods=["POST"])
def alert():
    if request.method == "POST":
        try:
            data = request.json
            to_email_id = data['email']
            to_cc_id = data['cc_mail']
            employeeName = data["employeeName"]
            timesheetPeriod = data["timesheetPeriod"]
            projectDescription = data["projectDescription"]
            projectTaskDescription = data["projectTaskDescription"]
            timsheetEffort = data['timsheetEffort']

            mail_sent =  send_mail(employeeName, to_email_id, to_cc_id, timesheetPeriod, projectDescription, projectTaskDescription, timsheetEffort)
            if mail_sent:
                return {
                    "funcName": "alert()",
                    "msg": "Alert Sent Successfully",
                    "status": "OK",
                    "statusCode": 200
                }
            else:
                return {
                    "funcName": "alert()",
                    "msg": f"Alert Sent Successfully",
                    "status": "OK",
                    "statusCode": 200
                }
        except Exception as error:
            return {
                "funcName": "alert()",
                "msg": f"Alert Sending Failed: {error}",
                "status": "Error",
                "statusCode": 500
            }


config_Url = configparser.ConfigParser()
config_Url.read('config/config.ini')
ip = config_Url["alert"]["ip"]
log_path = config_Url["LOGS"]["log_path"]
port = config_Url["alert"]["port"]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Flask api exposing yolov5 model")
    parser.add_argument("--port", default=port, type=int, help="port number")
    args = parser.parse_args()

      # force_reload = recache latest code
    app.run(host=ip, port=args.port,debug=True) # debug=True causes Restarting with stat


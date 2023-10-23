import unittest
from alert_app import app  # Import your Flask app
import json
from src.sent_mail.sendMail import send_mail
class TestAlertEndpoint(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_alert_success(self):
        data = {
            "email": "demo@algo8.ai",
            "cc_mail": "mukesh.kumar@algo8.ai",
            "employeeName": "John Doe",
            "timesheetPeriod": "2023-09",
            "projectDescription": "Project ABC",
            "projectTaskDescription": "Task 123",
            "timsheetEffort": "8 hours"
        }
        response = self.app.post('/alert', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data["status"], "OK")

    def test_alert_failure(self):
        data = {
            "email": "demo@algo8.ai",
            "cc_mail": "mukesh.kumar@algo8.ai",
            "employeeName": "John Doe",
            "timesheetPeriod": "2023-09",
            "projectDescription": "Project ABC",
            "projectTaskDescription": "Task 123",
            "timsheetEffort": "8 hours"
        }
        # Simulate an error condition in your API, for example by setting mail_sent to False
        mail_sent = False
        with unittest.mock.patch('send_mail', return_value=mail_sent):
            response = self.app.post('/alert', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data["status"], "Error")

    def test_alert_exception(self):
        # Simulate an exception in your API
        data = {
            "email": "demo@algo8.ai",
            "cc_mail": "mukesh.kumar@algo8.ai",
            "employeeName": "John Doe",
            "timesheetPeriod": "2023-09",
            "projectDescription": "Project ABC",
            "projectTaskDescription": "Task 123",
            "timsheetEffort": "8 hours"
        }
        with unittest.mock.patch('send_mail', side_effect=Exception("Simulated Error")):
            response = self.app.post('/alert', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data["status"], "Error")

if __name__ == '__main__':
    unittest.main()

import unittest
from alert_app import app  # Import your Flask app
import json

class TestNaggMailSentEndpoint(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def test_nagg_mail_sent_success(self):
        data = {
            "projectDescription": "Rogers",
            "timePeriod": "6"
        }
        response = self.app.get('/naggMailSent', data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data["status"], "OK")

    def test_nagg_mail_sent_failure(self):
        data = {
            "projectDescription": "Rogers",
            "timePeriod": "6"
        }
        # Simulate an error condition in your API, for example by setting nagMailSent to False
        nagMailSent = False
        with unittest.mock.patch('your_module.certinaityAI', return_value=nagMailSent):
            response = self.app.get('/naggMailSent', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data["status"], "Error")

    def test_nagg_mail_sent_exception(self):
        # Simulate an exception in your API
        data = {
            "projectDescription": "Rogers",
            "timePeriod": "6"
        }
        with unittest.mock.patch('your_module.certinaityAI', side_effect=Exception("Simulated Error")):
            response = self.app.get('/naggMailSent', data=json.dumps(data), content_type='application/json')
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data["status"], "Error")

if __name__ == '__main__':
    unittest.main()

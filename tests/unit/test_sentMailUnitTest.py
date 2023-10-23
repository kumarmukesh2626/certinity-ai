import unittest
import pandas as pd
from unittest.mock import patch
from src.sent_mail.sentMailpipline import certinaityAI  # Import your certinaityAI function
from database.ConnectDb import DatabaseHandler
class TestCertinaityAI(unittest.TestCase):

    @patch('DatabaseHandler.fetch_data')
    def test_certinaityAI_success(self, mock_fetch_data):
        # Test the case when certinaityAI succeeds in sending an alert
        # You need to set up the mock_fetch_data to return some data
        # Adjust the data as needed for your test case
        mock_fetch_data.return_value = pd.DataFrame({
            'employeeId': [1, 2],
            'employeeName': ['John Doe', 'Jane Smith'],
            'spocEmailId': ['john@example.com', 'jane@example.com'],
            'spocName': ['Spoc1', 'Spoc2'],
            'timesheetDate': ['2023-09-01', '2023-09-02'],
            'timesheetEfforts': [8, 8],
            'projectDescription': ['Project A', 'Project B'],
            'projectTaskDescription': ['Task 1', 'Task 2'],
            'taskType': ['Pending', 'Pending']
        })
        
        month = 3
        projectDescription = "Rogers"  # Adjust as needed
        result = certinaityAI(month, projectDescription)
        self.assertTrue(result)  # Assert that the function returns True for success

    @patch('DatabaseHandler.fetch_data')
    def test_certinaityAI_failure(self, mock_fetch_data):
        # Test the case when certinaityAI fails to send an alert
        # You need to set up the mock_fetch_data to return some data
        # Adjust the data as needed for your test case
        mock_fetch_data.return_value = pd.DataFrame({
            'employeeId': [1, 2],
            'employeeName': ['John Doe', 'Jane Smith'],
            'spocEmailId': ['john@example.com', 'jane@example.com'],
            'spocName': ['Spoc1', 'Spoc2'],
            'timesheetDate': ['2023-09-01', '2023-09-02'],
            'timesheetEfforts': [8, 8],
            'projectDescription': ['Project A', 'Project B'],
            'projectTaskDescription': ['Task 1', 'Task 2'],
            'taskType': ['Pending', 'Pending']
        })

        month = 3
        projectDescription = "Rogers"  # Adjust as needed
        result = certinaityAI(month, projectDescription)
        self.assertFalse(result)  # Assert that the function returns False for failure

    @patch('DatabaseHandler.fetch_data')
    def test_certinaityAI_exception(self, mock_fetch_data):
        # Test the case when certinaityAI encounters an exception
        # You need to set up the mock_fetch_data to raise an exception
        mock_fetch_data.side_effect = Exception("Test Exception")

        month = 6
        projectDescription = "Rogers"  # Adjust as needed
        result = certinaityAI(month, projectDescription)
        self.assertFalse(result)  # Assert that the function returns False for exception

if __name__ == '__main__':
    unittest.main()

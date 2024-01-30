import unittest
from unittest.mock import patch
from api_integration import fetch_betting_data

# Python's unittest framework and unittest.
# mock can be used for testing and mocking.

class TestApiIntegration(unittest.TestCase):

    @patch('api_integration.requests.get')
    def test_fetch_betting_data(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': 'some data'}
        
        response = fetch_betting_data('dummy_url', {'Authorization': 'Bearer dummy_token'})
        self.assertEqual(response, {'data': 'some data'})

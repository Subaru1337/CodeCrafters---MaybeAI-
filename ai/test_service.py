import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from ai.service import get_summary, search_company, get_bias_report

class TestService(unittest.TestCase):

    @patch('ai.service.Session')
    @patch('ai.service.generate_summary')
    def test_get_summary_cached(self, mock_generate_summary, mock_session_class):
        # Setup mock session
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Setup mock row
        mock_row = MagicMock()
        mock_row.id = 1
        mock_row.summary_text = "Test summary"
        mock_row.confidence_score = 0.95
        mock_row.sentiment = "Bullish"
        mock_row.sentiment_score = 0.8
        mock_row.conflicts_found = False
        mock_row.conflict_description = ""
        mock_row.sources_used = '["source1"]'
        mock_row.generated_at = datetime.utcnow()
        
        mock_session.execute.return_value.fetchone.return_value = mock_row
        
        # Call function
        result = get_summary(company_id=123)
        
        # Asserts
        self.assertTrue(result["cached"])
        self.assertEqual(result["summary_text"], "Test summary")
        self.assertEqual(result["sources_used"], ["source1"])
        mock_generate_summary.assert_not_called()
        mock_session.close.assert_called_once()
        
    @patch('ai.service.Session')
    @patch('ai.service.generate_summary')
    def test_get_summary_not_cached_no_row(self, mock_generate_summary, mock_session_class):
        # Setup mock session returning None
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.execute.return_value.fetchone.return_value = None
        
        # Setup generate_summary return
        mock_generate_summary.return_value = {"summary_text": "New summary"}
        
        # Call function
        result = get_summary(company_id=123, language="French")
        
        # Asserts
        self.assertFalse(result["cached"])
        self.assertEqual(result["summary_text"], "New summary")
        mock_generate_summary.assert_called_once_with(123, "French")
        mock_session.close.assert_called_once()

    @patch('ai.service.Session')
    @patch('ai.service.generate_summary')
    def test_get_summary_db_exception(self, mock_generate_summary, mock_session_class):
        # Setup mock session raising exception
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.execute.side_effect = Exception("DB error")
        
        # Setup generate_summary return
        mock_generate_summary.return_value = {"summary_text": "Fallback summary"}
        
        # Call function
        result = get_summary(company_id=123)
        
        # Asserts
        self.assertFalse(result["cached"])
        self.assertEqual(result["summary_text"], "Fallback summary")
        mock_generate_summary.assert_called_once_with(123, 'English')
        mock_session.close.assert_called_once()
        
    @patch('ai.service.Session')
    def test_search_company_empty_query(self, mock_session_class):
        result = search_company("")
        self.assertEqual(result, [])
        mock_session_class.assert_not_called()

    @patch('ai.service.Session')
    def test_search_company_with_query(self, mock_session_class):
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_row1 = MagicMock()
        mock_row1.id = 1
        mock_row1.name = "Apple Inc."
        mock_row1.ticker = "AAPL"
        mock_row1.sector = "Technology"
        
        mock_row2 = MagicMock()
        mock_row2.id = 2
        mock_row2.name = "Apple Hospitality"
        mock_row2.ticker = "APLE"
        mock_row2.sector = "Real Estate"
        
        mock_session.execute.return_value.fetchall.return_value = [mock_row1, mock_row2]
        
        result = search_company("Apple")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["ticker"], "AAPL")
        self.assertEqual(result[1]["ticker"], "APLE")
        mock_session.close.assert_called_once()
        
    @patch('ai.service.Session')
    def test_search_company_exception(self, mock_session_class):
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.execute.side_effect = Exception("DB error")
        
        result = search_company("Apple")
        
        self.assertEqual(result, [])
        mock_session.close.assert_called_once()

    @patch('ai.service.detect_biases')
    def test_get_bias_report(self, mock_detect_biases):
        mock_detect_biases.return_value = {"biases_found": ["Recency Bias"]}
        
        result = get_bias_report(1)
        
        self.assertEqual(result["biases_found"], ["Recency Bias"])
        mock_detect_biases.assert_called_once_with(1)

if __name__ == '__main__':
    unittest.main()

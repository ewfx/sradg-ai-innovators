
import pytest
from unittest.mock import patch, MagicMock
from anomaly_detection.modules.llm_integration import LLMIntegration

@patch("anomaly_detection.modules.llm_integration.OpenAI")
def test_categorize_anomaly_cached(mock_openai):
    llm = LLMIntegration()
    comment = "This is a test comment"
    
    # Mock shelve to always hit cache
    with patch("shelve.open") as mock_shelve:
        mock_cache = {llm.hash_comment(comment): "Timing Issue"}
        mock_shelve.return_value.__enter__.return_value = mock_cache
        result = llm.categorize_anomaly(comment)
        assert result == "Timing Issue"

@patch("anomaly_detection.modules.llm_integration.OpenAI")
def test_generate_resolution_summary_success(mock_openai_class):
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Check config mismatch"))]
    mock_client.chat.completions.create.return_value = mock_response

    llm = LLMIntegration()
    result = llm.generate_resolution_summary({"TRADEID": 123, "COMMENT": "Mismatch in data"})
    assert "Check" in result or "config" in result

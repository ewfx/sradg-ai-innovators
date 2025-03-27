
import pytest
from unittest.mock import patch, MagicMock
from anomaly_detection.modules.jira_integration import JiraIntegration

@patch("anomaly_detection.modules.jira_integration.requests.post")
def test_create_ticket_success(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"key": "JIRA-456"}
    mock_post.return_value = mock_response

    jira = JiraIntegration()
    issue_key = jira.create_ticket("Test Summary", "Test Description")
    
    assert issue_key == "JIRA-456"
    mock_post.assert_called_once()

@patch("anomaly_detection.modules.jira_integration.requests.post")
def test_create_ticket_failure(mock_post):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Bad Request"
    mock_post.return_value = mock_response

    jira = JiraIntegration()
    result = jira.create_ticket("Test Summary", "Test Description")
    
    assert result is None
    mock_post.assert_called_once()

@patch("anomaly_detection.modules.jira_integration.requests.post", side_effect=Exception("API error"))
def test_create_ticket_exception(mock_post):
    jira = JiraIntegration()
    result = jira.create_ticket("Test Summary", "Test Description")
    
    assert result is None

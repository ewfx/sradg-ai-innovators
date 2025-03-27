
import pandas as pd
from unittest.mock import patch, MagicMock
from anomaly_detection.modules.agentic_ai import AgenticAI

@patch("anomaly_detection.modules.agentic_ai.JiraIntegration")
def test_apply_agentic_resolution(mock_jira_class):
    mock_jira = MagicMock()
    mock_jira.create_ticket.return_value = "JIRA-123"
    mock_jira_class.return_value = mock_jira

    data = {
        "TRADEID": [101],
        "DESKNAME": ["DeskA"],
        "COMMENT": ["Timing mismatch"],
        "Anomaly_Category": ["Timing Issue"],
        "Resolution_Summary": ["Resolve timing delay"]
    }
    df = pd.DataFrame(data)
    result_df = AgenticAI.apply_agentic_resolution(df)

    assert result_df.loc[0, "Feedback"] == "Resolved by Agent"
    assert result_df.loc[0, "Ticket_ID"] == "JIRA-123"
    assert "Resolution_Task_ID" in result_df.columns

def test_apply_feedback_mechanism():
    df = pd.DataFrame({
        "TRADEID": [123],
        "DESKNAME": ["DeskX"],
        "COMMENT": ["Check needed"],
        "Anomaly_Category": ["Data Entry Error"]
    })
    updated_df = AgenticAI.apply_feedback_mechanism(df)
    assert "Feedback" in updated_df.columns
    assert updated_df.loc[0, "Feedback"] == "Pending User Review"

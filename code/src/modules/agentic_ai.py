# modules/agentic_ai.py
import pandas as pd
import logging
import uuid
from modules.jira_integration import JiraIntegration


class AgenticAI:
    @staticmethod
    def apply_agentic_resolution(df: pd.DataFrame):
        try:
            resolved_count = 0
            jira = JiraIntegration()  # ← Initialize once outside the loop

            for index, row in df.iterrows():
                if row['Anomaly_Category'] == 'Timing Issue':
                    approval = 'yes'  # You can replace this with rule-based logic if needed

                    if approval == 'yes':
                        df.at[index, 'Feedback'] = "Resolved by Agent"
                        df.at[index, 'Feedback_Details'] = "Resolved by Agent"
                        df.at[index, 'Resolution_Task_ID'] = str(uuid.uuid4())

                        # ✅ ADD THIS BLOCK FOR JIRA TICKET CREATION
                        summary = f"Anomaly Detected: {row['TRADEID']} - {row['Anomaly_Category']}"
                        description = (
                            f"Trade ID: {row['TRADEID']}\n"
                            f"Desk: {row['DESKNAME']}\n"
                            f"Comment: {row['COMMENT']}\n"
                            f"Category: {row['Anomaly_Category']}\n"
                            f"Resolution: {row['Resolution_Summary']}"
                        )
                        ticket_id = jira.create_ticket(summary, description)
                        df.at[index, 'Ticket_ID'] = ticket_id or str(uuid.uuid4())

                        resolved_count += 1

            logging.info({"message": f"{resolved_count} anomalies resolved via agentic AI."})
            return df
        except Exception as e:
            logging.error({"message": "Error during agentic AI resolution.", "error": str(e)})
            return df

    @staticmethod
    def apply_feedback_mechanism(df: pd.DataFrame):
        """
        Applies a feedback mechanism to anomalies.

        Args:
            df (pd.DataFrame): DataFrame containing anomalies.

        Returns:
            pd.DataFrame: DataFrame with feedback mechanism applied.
        """
        try:
            df['Feedback'] = 'Pending User Review'
            df['Feedback_Details'] = ''
            df['Ticket_ID'] = ''
            df['Resolution_Task_ID'] = ''
            logging.info({"message": "Feedback mechanism applied."})
            return df
        except Exception as e:
            logging.error({"message": "Error during feedback mechanism.", "error": str(e)})
            return df


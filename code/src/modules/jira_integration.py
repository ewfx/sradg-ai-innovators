import logging
import requests
import yaml
import base64

# Load config once
try:
    with open('config/config.yaml') as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    logging.error("Jira config file not found.")
    config = {}

class JiraIntegration:
    def __init__(self):
        self.jira_url = config.get("jira", {}).get("url")
        self.project_key = config.get("jira", {}).get("project_key")
        self.username = config.get("jira", {}).get("username")
        self.api_token = config.get("jira", {}).get("api_token")
        self.issue_type = config.get("jira", {}).get("issue_type", "Task")

        if not all([self.jira_url, self.project_key, self.username, self.api_token]):
            logging.warning("Incomplete Jira configuration.")

        # Encode auth
        auth_str = f"{self.username}:{self.api_token}"
        self.auth_header = {
            "Authorization": f"Basic {base64.b64encode(auth_str.encode()).decode()}",
            "Content-Type": "application/json"
        }

    def create_ticket(self, summary: str, description: str) -> str:
        try:
            payload = {
                "fields": {
                    "project": {"key": self.project_key},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"name": self.issue_type}
                }
            }

            response = requests.post(
                f"{self.jira_url}/rest/api/2/issue",
                headers=self.auth_header,
                json=payload
            )

            if response.status_code == 201:
                issue_key = response.json().get("key")
                logging.info(f"Jira ticket created: {issue_key}")
                return issue_key
            else:
                logging.error(f"Failed to create Jira ticket: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logging.error(f"Exception in Jira ticket creation: {str(e)}")
            return None

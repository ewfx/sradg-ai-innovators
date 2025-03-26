import logging
import openai
import shelve
import hashlib
from ratelimit import limits, sleep_and_retry
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
import json
import yaml

# Load configuration
try:
    with open('config/config.yaml') as file:
        config = yaml.safe_load(file)

except FileNotFoundError:
    print("Error: config.yaml file not found. Using default configurations.")
    config = {
        'api_keys': {'openai': 'YOUR_OPENAI_API_KEY'},
        'llm': {'enabled': True},
    }

class LLMIntegration:
    CACHE_FILE = 'cache/anomaly_cache.db'

    def __init__(self):
        self.client = OpenAI(api_key=config['api_keys']['openai'])

    def hash_comment(self, comment: str) -> str:
        return hashlib.sha256(comment.strip().lower().encode('utf-8')).hexdigest()

    #@sleep_and_retry
    #@limits(calls=1, period=60)
    def categorize_anomaly(self, comment: str) -> str:

        if config.get('llm', {}).get('enabled', True):
            logging.info("LLM is disabled via config.")
            return "LLM Disabled"

        cache_key = self.hash_comment(comment)
        try:
            with shelve.open(self.CACHE_FILE) as cache:
                if cache_key in cache:
                    logging.info({"message": "Returning cached category.", "category": cache[cache_key]})
                    return cache[cache_key]

                prompt = (
                    "Categorize the following reconciliation anomaly reason into predefined buckets "
                    "such as [Rounding Error, Timing Issue, Data Entry Error, System Error, New Issue]. "
                    "If the reason does not fit in given categories, use 'New Issue' category. \n\n"
                    f"{comment}\n\nCategory:"
                )

                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1,
                    temperature=0.7
                )

                category = response.choices[0].message.content.strip()
                cache[cache_key] = category
                logging.info({"message": "Anomaly categorized.", "category": category})
                return category

        except openai.RateLimitError:
            logging.warning("Rate limit hit for categorize_anomaly.")
            return "Rate Limit Exceeded"
        except openai.APIError as e:
            if getattr(e, "code", "") == "insufficient_quota":
                logging.error("OpenAI quota exceeded.")
                return "Quota Exceeded"
            logging.error(f"OpenAI API error: {e}")
            return "API Error"
        except Exception as e:
            logging.error({"message": "LLM anomaly categorization failed.", "error": str(e)})
            return "Uncategorized"

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def generate_resolution_summary(self, anomaly_details: dict) -> str:
        if not config.get('llm', {}).get('enabled', True):
            logging.info("LLM is disabled via config.")
            return "LLM Disabled"

        prompt = f"Given the following anomaly details: {json.dumps(anomaly_details)}, provide a concise summary of the potential resolution."
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.6
            )
            summary = response.choices[0].message.content.strip()
            logging.info({"message": "Resolution summary generated.", "summary": summary})
            return summary

        except openai.RateLimitError:
            logging.warning("Rate limit hit for resolution summary.")
            return "Rate Limit Exceeded"
        except openai.APIError as e:
            if getattr(e, "code", "") == "insufficient_quota":
                logging.error("OpenAI quota exceeded.")
                return "Quota Exceeded"
            logging.error(f"OpenAI API error: {e}")
            return "API Error"
        except Exception as e:
            logging.error({"message": "Failed to generate resolution summary.", "error": str(e)})
            return "Resolution summary unavailable."

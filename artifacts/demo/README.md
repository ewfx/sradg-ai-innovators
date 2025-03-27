- Smarter Reconciliation and Anomaly Detection System 

The implemented solution integrates traditional machine learning, modern LLMs, and a scalable API architecture to deliver real-time and batch anomaly detection in financial reconciliation workflows. The pipeline begins with ingesting structured financial data through API or CSV, followed by preprocessing that includes feature engineering (rolling stats, datetime extraction, and label encoding). Anomaly detection is then performed using Isolation Forest or LOF, while clustering is handled via KMeans to identify patterns. Anomalous records are then categorized into human-understandable buckets using OpenAI's GPT model, and descriptive resolution summaries are generated. To reduce repeated LLM costs and latency, responses are cached using a hash-based key. A feedback mechanism flags items for user review or automated resolution (e.g., timing issues), and resolved anomalies are logged with synthetic task/ticket IDs. The results are saved in a CSV and sent via email to designated stakeholders. All functions are wrapped with retry logic for resilience, and the service supports both RESTful and WebSocket interfaces for flexible integration.

Modules and Libraries

Pandas / NumPy – Data handling and numeric computation

Scikit-learn – Isolation Forest for anomaly detection and KMeans for pattern clustering

OpenAI API – For categorizing anomalies and summarizing resolutions using LLM

FastAPI – Backend framework for API-based anomaly detection and WebSocket support

Email (SMTP) – Sends anomaly reports to specified recipients

Shelve / Hashlib – Used for LLM caching and comment hashing

ThreadPoolExecutor – Enables parallel execution for LLM inference on batch data


Core Components

🔁 lifespan(app)

Loads pickled models (IsolationForest, KMeans, LabelEncoder) at app startup.

Ensures models are reusable and don't retrain on each request.

Falls back to None if models are missing.

📘 RealtimeData(BaseModel)

Defines schema for a single transaction data point, required for real-time anomaly detection.

📊 Functional Modules

✅ DataIngestion

Loads large CSV files in chunks.

Uses parse_dates to automatically convert date fields.

Ensures robustness with error handling for missing/empty files.

🧹 DataPreparation

Parses dates, extracts weekday/month features.

Adds rolling statistical features (mean, std deviation).

Encodes categorical variables (like DESKNAME).

Handles unseen labels by assigning a fallback encoding (-1).

🤖 ModelLayer

Anomaly Detection: Uses Isolation Forest or LOF (Local Outlier Factor) to mark rows as anomalous.

Clustering: Applies KMeans clustering to group data for pattern analysis.

Retrains models if pickled files are not found.

🧠 LLMIntegration

Caches results of LLM categorization using SHA256-hashed comments.

Categorizes anomalies into predefined buckets (e.g., Rounding Error, Timing Issue).

Generates resolution summaries using OpenAI gpt-3.5-turbo model.

Enforces OpenAI rate limits using decorators.

💾 DataPersistence

Saves anomalies as CSV to the specified output path.

Logs output path and error (if any).

📧 EmailNotification

Sends emails with or without attachments.

Uses Gmail’s SMTP (TLS on port 587).

Supports retry logic using exponential backoff.

✅ DataValidation

Removes anomalies that exceed quantity difference threshold.

🤖 AgenticAI

Automatically resolves anomalies marked as Timing Issue.

Generates synthetic task/ticket IDs.

Applies feedback mechanism with default status as Pending User Review.

🔄 Processing Functions

process_data(data)

Preprocesses and extracts features.

Detects anomalies and clusters data.

Applies LLM categorization and summarization.

Validates and resolves data.

Saves and emails anomalies.

Used in real-time processing.

process_data_with_batch_llm(data)

Optimized for batch input.

Uses ThreadPoolExecutor for parallel LLM inference.

Returns annotated and resolved anomalies.

🚀 FastAPI Endpoints

POST /realtime_anomaly/

Accepts single trade JSON.

Processes data in real-time.

Triggers email if anomaly is detected.

POST /batch_anomaly/

Accepts list of trades.

Processes and categorizes batch.

Sends single summary email.

GET /health

Returns { "status": "ok" }.

🌐 WebSocket Endpoint

/ws

Accepts live stream of trade JSON.

Sends real-time anomaly notifications.

Allows integration with dashboards.

🔁 Retry & Caching Logic

Email Retry

Wrapped with exponential backoff decorator.

Handles SMTP failures gracefully.

LLM Caching

Prevents repeated calls for same COMMENT using hashing + shelve DB.

🧪 Observations & Results

🟢 Accuracy & Detection

Isolation Forest worked well with minimal false positives.

Timing-related anomalies were reliably categorized by LLM.

Auto-resolutions for Timing Issue added measurable automation value.

🔁 Performance

Batch LLM operations sped up using multithreading.

Data processing on ~10k rows took < 5 seconds (excluding LLM calls).

💬 LLM Categorization

OpenAI handled edge cases and ambiguous COMMENT values with graceful fallbacks.

Cached categorizations reduced cost and latency by over 50%.

📤 Email Reporting

Configurable email alerts enabled seamless integration with operations.

Attachments contain complete metadata for resolved anomalies.

🛠️ Additional Notes

Models retrain automatically if not available.

Logging is centralized and rotated via JSON-style messages.

config.yaml contains paths, thresholds, credentials.

📈 Future implementations

Add database persistence for anomalies.

Build frontend dashboard using WebSocket stream.

Expand LLM logic to include severity classification.

Containerize for deployment with Docker.
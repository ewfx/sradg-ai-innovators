from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import pandas as pd
from datetime import datetime
import logging
import yaml
from concurrent.futures import ThreadPoolExecutor
from .models import RealtimeData
from modules.data_ingestion import DataIngestion
from modules.data_preparation import DataPreparation
from modules.model_layer import ModelLayer
from modules.llm_integration import LLMIntegration
from modules.data_persistence import DataPersistence
from modules.email_notification import EmailNotification
from modules.data_validation import DataValidation
from modules.agentic_ai import AgenticAI
from modules.utils import retry_with_exponential_backoff
from .websocket_manager import ConnectionManager
import os

from fastapi import FastAPI, HTTPException, Request, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import pandas as pd
from datetime import datetime
import logging
import yaml
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from .models import RealtimeData


# Configuration Management (using config.yaml)
try:
    with open('config/config.yaml') as file:
        config = yaml.safe_load(file)
        
except FileNotFoundError:
    print("Error: config.yaml file not found. Using default configurations.")
    
# Logging configuration (JSON structured logging)
timestamp1 = datetime.now().strftime('%Y%m%d_%H%M%S')
logging.basicConfig(
    filename= 'logs/recon_anomaly_detection.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# FastAPI App
@asynccontextmanager
async def lifespan(app: FastAPI):
    global isolation_forest_model, kmeans_model, label_encoder
    try:
        from modules.model_layer import isolation_forest_model, kmeans_model
        from modules.data_preparation import label_encoder
        logging.info({"message": "Models loaded successfully."})
    except FileNotFoundError:
        logging.error({"message": "Model files not found."})
        isolation_forest_model = None
        kmeans_model = None
        label_encoder = None
    yield

app = FastAPI(lifespan=lifespan)

# Apply Retry Logic to Email Sending
EmailNotification.send_email = retry_with_exponential_backoff(EmailNotification.send_email)

def process_data(data):
    try:
        features = DataPreparation.preprocess_data(data)
        data['Anomaly'] = ModelLayer.detect_anomalies(features)

        print(f"DataFrame after anomaly detection:\n{data}")
        logging.info(f"DataFrame after anomaly detection:\n{data}")

        anomalies_df = data[data['Anomaly'] == 'Yes'].copy()

        data['Pattern_Cluster'] = ModelLayer.cluster_data(features)

        # The commented out line was redundant and has been removed.

        anomalies_df = AgenticAI.apply_feedback_mechanism(anomalies_df)
        llm_handler = LLMIntegration()
        anomalies_df['Anomaly_Category'] = anomalies_df['COMMENT'].apply(llm_handler.categorize_anomaly)
        anomalies_df['Resolution_Summary'] = anomalies_df.apply(lambda row: llm_handler.generate_resolution_summary(row.to_dict()), axis=1)
        anomalies_df = DataValidation.validate_data_consistency(anomalies_df, config['data_validation']['quantity_threshold'])
        anomalies_df = AgenticAI.apply_agentic_resolution(anomalies_df)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = config['paths']['anomaly_output'].format(timestamp=timestamp)
        DataPersistence.save_anomalies(anomalies_df, output_path)

        EmailNotification.send_email(
            subject='Anomalies Detected',
            body='Please find attached anomaly detection report.',
            recipient=config['email']['recipient'],
            attachment=None
        )

        return anomalies_df

    except Exception as e:
        logging.error({"message": "Data processing error.", "error": str(e)})
        return pd.DataFrame(), None 

@app.post("/realtime_anomaly/")
async def realtime_anomaly(data: RealtimeData, background_tasks: BackgroundTasks):
    try:
        data_dict = data.dict()
        df = pd.DataFrame([data_dict])
        anomalies_df = process_data(df)

        if not anomalies_df.empty:
            background_tasks.add_task(EmailNotification.send_email,
                                      subject='Realtime Anomaly Detected',
                                      body=f"Anomaly detected in TRADEID: {data.TRADEID}",
                                      recipient=config['email']['recipient'],
                                      attachment=None
                                      )
            return {"message": "Anomaly detected and email sent."}
        else:
            return {"message": "No anomaly detected."}
    except Exception as e:
        logging.error({"message": "Realtime anomaly processing error.", "error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            realtime_data = RealtimeData(**data)

            df = pd.DataFrame([realtime_data.dict()])
            anomalies_df = process_data(df)

            if not anomalies_df.empty:
                await manager.send_personal_message(f"Anomaly detected: {realtime_data.TRADEID}", websocket)
                # broadcast if needed
                # await manager.broadcast(f"Anomaly detected: {realtime_data.TRADEID}")
            else:
                await manager.send_personal_message(f"No anomaly detected for : {realtime_data.TRADEID}", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Batch Processing with LLM
def batch_categorize_anomalies(comments):
    llm_handler = LLMIntegration()
    categories = []
    with ThreadPoolExecutor() as executor:
        categories = list(executor.map(llm_handler.categorize_anomaly, comments))
    return categories


def process_data_with_batch_llm(data):
    anomalies_df = pd.DataFrame()
    output_path = ""
    
    try:
        features = DataPreparation.preprocess_data(data)
        data['Anomaly'] = ModelLayer.detect_anomalies(features)
        data['Pattern_Cluster'] = ModelLayer.cluster_data(features)
        anomalies_df = data[data['Anomaly'] == 'Yes'].copy()

        anomalies_df = AgenticAI.apply_feedback_mechanism(anomalies_df)

        comments = anomalies_df['COMMENT'].tolist()
        # Implement robust LLM batch handling with error capturing
        categories = []
        llm_handler = LLMIntegration()

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(llm_handler.categorize_anomaly, comment) for comment in comments]
            for future in futures:
                try:
                    category = future.result()
                except Exception as llm_error:
                    logging.error(f"LLM categorization error: {llm_error}")
                    category = 'Uncategorized'
                categories.append(category)

        anomalies_df['Anomaly_Category'] = categories

        summaries = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(llm_handler.generate_resolution_summary, row.to_dict()) for _, row in anomalies_df.iterrows()]
            for future in futures:
                try:
                    summary = future.result()
                except Exception as llm_error:
                    logging.error(f"LLM resolution summary error: {llm_error}")
                    summary = 'Resolution summary unavailable'
                summaries.append(summary)

        anomalies_df['Resolution_Summary'] = summaries

        anomalies_df = DataValidation.validate_data_consistency(anomalies_df, config['data_validation']['quantity_threshold'])
        anomalies_df = AgenticAI.apply_agentic_resolution(anomalies_df)

    except Exception as e:
        logging.error({"message": "Data processing error encountered.", "error": str(e)})

    finally:
        if not anomalies_df.empty:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = config['paths']['anomaly_output'].format(timestamp=timestamp)
            
            try:
                DataPersistence.save_anomalies(anomalies_df, output_path)
                print(f"Anomaly detection CSV saved at: {output_path}")
                logging.info(f"Anomaly detection CSV saved at: {output_path}")

                EmailNotification.send_email(
                    subject='Anomalies Detected',
                    body='Please find attached the anomaly detection report.',
                    recipient=config['email']['recipient'],
                    attachment=None
                )
            except Exception as save_error:
                logging.error(f"Error during final anomaly saving or notification: {save_error}")
                print(f"Error during final anomaly saving or notification: {save_error}")
        else:
            print("No anomalies detected or DataFrame is empty.")
            logging.info("No anomalies detected or DataFrame is empty.")

    return anomalies_df

# FastAPI endpoint for batch processing
@app.post("/batch_anomaly/")
async def batch_anomaly(data: list[RealtimeData], background_tasks: BackgroundTasks):
    try:
        data_dicts = [item.dict() for item in data]
        df = pd.DataFrame(data_dicts)
        anomalies_df = process_data_with_batch_llm(df)

        if not anomalies_df.empty:
            background_tasks.add_task(EmailNotification.send_email,
                                      subject='Batch Anomalies Detected',
                                      body=f"Batch of {len(data)} anomalies detected.",
                                      recipient=config['email']['recipient'],
                                      attachment=None
                                      )
            return {"message": "Batch anomalies detected and email sent."}
        else:
            return {"message": "No anomalies detected in batch."}
    except Exception as e:
        logging.error({"message": "Batch anomaly processing error.", "error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")
        df = pd.DataFrame([data_dict])
        anomalies_df = process_data(df)

        if not anomalies_df.empty:
            background_tasks.add_task(EmailNotification.send_email,
                                      subject='Realtime Anomaly Detected',
                                      body=f"Anomaly detected in TRADEID: {data.TRADEID}",
                                      recipient=config['email']['recipient'],
                                      attachment=None
                                      )
            return {"message": "Anomaly detected and email sent."}
        else:
            return {"message": "No anomaly detected."}
    except Exception as e:
        logging.error({"message": "Realtime anomaly processing error.", "error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            realtime_data = RealtimeData(**data)

            df = pd.DataFrame([realtime_data.dict()])
            anomalies_df = process_data(df)

            if not anomalies_df.empty:
                await manager.send_personal_message(f"Anomaly detected: {realtime_data.TRADEID}", websocket)
                # broadcast if needed
                # await manager.broadcast(f"Anomaly detected: {realtime_data.TRADEID}")
            else:
                await manager.send_personal_message(f"No anomaly detected for : {realtime_data.TRADEID}", websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Batch Processing with LLM
def batch_categorize_anomalies(comments):
    llm_handler = LLMIntegration()
    categories = []
    with ThreadPoolExecutor() as executor:
        categories = list(executor.map(llm_handler.categorize_anomaly, comments))
    return categories

def process_data_with_batch_llm(data):
    try:
        features = DataPreparation.preprocess_data(data)
        data['Anomaly'] = ModelLayer.detect_anomalies(features)
        data['Pattern_Cluster'] = ModelLayer.cluster_data(features)
        anomalies_df = data[data['Anomaly'] == 'Yes'].copy()

        anomalies_df = AgenticAI.apply_feedback_mechanism(anomalies_df)

        # Batch LLM calls
        comments = anomalies_df['COMMENT'].tolist()
        categories = batch_categorize_anomalies(comments)
        anomalies_df['Anomaly_Category'] = categories

        llm_handler = LLMIntegration()
        summaries = []
        with ThreadPoolExecutor() as executor:
            #summaries = list(executor.map(lambda row: llm_handler.generate_resolution_summary(row.to_dict()), anomalies_df.to_dict(orient='records')))
            summaries = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(llm_handler.generate_resolution_summary, row.to_dict()) for index, row in anomalies_df.iterrows()]
            for future in futures:
                try:
                    summaries.append(future.result())
                except Exception as e:
                    logging.error(f"LLM summary generation failed: {e}")
                    summaries.append("Resolution summary unavailable.")

        anomalies_df['Resolution_Summary'] = summaries
        anomalies_df = DataValidation.validate_data_consistency(anomalies_df, config['data_validation']['quantity_threshold'])
        anomalies_df = AgenticAI.apply_agentic_resolution(anomalies_df)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = config['paths']['anomaly_output'].format(timestamp=timestamp)
        DataPersistence.save_anomalies(anomalies_df, output_path)
        # Added code to print the output file's path
        print(f"Output file saved to: {output_path}")
        logging.info(f"Output file saved to: {output_path}")

        # Added code to print the content of the dataframe that is saved.
        print(f"Content of saved DataFrame:\n{anomalies_df}")
        logging.info(f"Content of saved DataFrame:\n{anomalies_df}")

        EmailNotification.send_email(
            subject='Anomalies Detected',
            body='Please find attached anomaly detection report.',
            recipient=config['email']['recipient'],
            attachment=output_path
        )

        return anomalies_df

    except Exception as e:
        logging.error({"message": "Data processing error.", "error": str(e)})
        return pd.DataFrame()

# FastAPI endpoint for batch processing
@app.post("/batch_anomaly/")
async def batch_anomaly(data: list[RealtimeData], background_tasks: BackgroundTasks):
    try:
        data_dicts = [item.dict() for item in data]
        df = pd.DataFrame(data_dicts)
        anomalies_df = process_data_with_batch_llm(df)

        if not anomalies_df.empty:
            background_tasks.add_task(EmailNotification.send_email,
                                      subject='Batch Anomalies Detected',
                                      body=f"Batch of {len(data)} anomalies detected.",
                                      recipient=config['email']['recipient'],
                                      attachment=None
                                      )
            return {"message": "Batch anomalies detected and email sent."}
        else:
            return {"message": "No anomalies detected in batch."}
    except Exception as e:
        logging.error({"message": "Batch anomaly processing error.", "error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server erro")



class AnomalyDetectionAPI:
    def __init__(self):
        # Configuration Management (using config.yaml)
        try:
            config_path = 'config/config.yaml'
            with open(config_path, 'r') as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            print("Error: config.yaml file not found. Using default configurations.")
            self.config = {
                'paths': {'data_file': 'data/generated_reconciliation_data.csv', 'anomaly_output': 'output/detected_anomalies_{timestamp}.csv'},
                'data_validation': {'quantity_threshold': 10},
                'api_keys': {'openai': 'YOUR_OPENAI_API_KEY'},
                'email': {'sender': 'your_email@gmail.com', 'password': 'your_password', 'recipient': 'recipient@example.com'},
            }

        # Logging configuration (JSON structured logging)
        logging.basicConfig(
            filename='logs/recon_anomaly_detection.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        self.app = FastAPI(lifespan=self.lifespan)
        self.email_notification = EmailNotification()
        self.email_notification.send_email = retry_with_exponential_backoff(self.email_notification.send_email)
        self.manager = ConnectionManager()

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        global isolation_forest_model, kmeans_model, label_encoder
        try:
            from modules.model_layer import isolation_forest_model, kmeans_model
            from modules.data_preparation import label_encoder
            logging.info({"message": "Models loaded successfully."})
        except FileNotFoundError:
            logging.error({"message": "Model files not found."})
            isolation_forest_model = None
            kmeans_model = None
            label_encoder = None
        yield

    def process_data(self, data):
        try:
            features = DataPreparation.preprocess_data(data)
            data['Anomaly'] = ModelLayer.detect_anomalies(features)
            data['Pattern_Cluster'] = ModelLayer.cluster_data(features)
            anomalies_df = data[data['Anomaly'] == 'Yes'].copy()

            anomalies_df = AgenticAI.apply_feedback_mechanism(anomalies_df)
            llm_handler = LLMIntegration()
            anomalies_df['Anomaly_Category'] = anomalies_df['COMMENT'].apply(llm_handler.categorize_anomaly)
            anomalies_df['Resolution_Summary'] = anomalies_df.apply(lambda row: llm_handler.generate_resolution_summary(row.to_dict()), axis=1)
            anomalies_df = DataValidation.validate_data_consistency(anomalies_df, self.config['data_validation']['quantity_threshold'])
            anomalies_df = AgenticAI.apply_agentic_resolution(anomalies_df)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.config['paths']['anomaly_output'].format(timestamp=timestamp)
            DataPersistence.save_anomalies(anomalies_df, output_path)

            self.email_notification.send_email(
                subject='Anomalies Detected',
                body='Please find attached anomaly detection report.',
                recipient=self.config['email']['recipient'],
                attachment=None
            )
            print("Anomaly rows:", anomalies_df.head())
            return anomalies_df

        except Exception as e:
            logging.error({"message": "Data processing error.", "error": str(e)})
            return pd.DataFrame(), None

    async def realtime_anomaly(self, data: RealtimeData, background_tasks: BackgroundTasks):
        try:
            data_dict = data.dict()
            df = pd.DataFrame([data_dict])
            anomalies_df, output_path = self.process_data(df)

            if not anomalies_df.empty:
                background_tasks.add_task(self.email_notification.send_email,
                                          subject='Realtime Anomaly Detected',
                                          body=f"Anomaly detected in TRADEID: {data.TRADEID}",
                                          recipient=self.config['email']['recipient'],
                                          attachment=None
                                          )
                return {"message": "Anomaly detected and email sent."}
            else:
                return {"message": "No anomaly detected."}
        except Exception as e:
            logging.error({"message": "Realtime anomaly processing error.", "error": str(e)})
            raise HTTPException(status_code=500, detail="Internal server error")

    async def health_check(self):
        return {"status": "ok"}

    async def websocket_endpoint(self, websocket: WebSocket):
        await self.manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_json()
                realtime_data = RealtimeData(**data)

                df = pd.DataFrame([realtime_data.dict()])
                anomalies_df = self.process_data(df)

                if not anomalies_df.empty:
                    await self.manager.send_personal_message(f"Anomaly detected: {realtime_data.TRADEID}", websocket)

                else:
                    await self.manager.send_personal_message(f"No anomaly detected for : {realtime_data.TRADEID}", websocket)

        except WebSocketDisconnect:
            self.manager.disconnect(websocket)

    def batch_categorize_anomalies(self, comments):
        llm_handler = LLMIntegration()
        categories = []
        with ThreadPoolExecutor() as executor:
            categories = list(executor.map(llm_handler.categorize_anomaly, comments))
        return categories

    def process_data_with_batch_llm(self, data):
        try:
            features = DataPreparation.preprocess_data(data)
            data['Anomaly'] = ModelLayer.detect_anomalies(features)
            data['Pattern_Cluster'] = ModelLayer.cluster_data(features)
            anomalies_df = data[data['Anomaly'] == 'Yes'].copy()

            anomalies_df = AgenticAI.apply_feedback_mechanism(anomalies_df)
            # Batch LLM calls
            comments = anomalies_df['COMMENT'].tolist()
            categories = self.batch_categorize_anomalies(comments)
            anomalies_df['Anomaly_Category'] = categories

            llm_handler = LLMIntegration()
            summaries = []
            with ThreadPoolExecutor() as executor:
                summaries = list(executor.map(lambda row: llm_handler.generate_resolution_summary(row.to_dict()), anomalies_df.to_dict(orient='records')))
                
            anomalies_df['Resolution_Summary'] = summaries
            anomalies_df = DataValidation.validate_data_consistency(anomalies_df, self.config['data_validation']['quantity_threshold'])
            anomalies_df = AgenticAI.apply_agentic_resolution(anomalies_df)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = self.config['paths']['anomaly_output'].format(timestamp=timestamp)
            DataPersistence.save_anomalies(anomalies_df, output_path)

            self.email_notification.send_email(
                subject='Anomalies Detected',
                body='Please find attached anomaly detection report.',
                recipient=self.config['email']['recipient'],
                attachment=None
            )

            return anomalies_df

        except Exception as e:
            logging.error({"message": "Data processing error.", "error": str(e)})
        
        finally:
        # Write the DataFrame to CSV, even if an error occurred
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = config['paths']['anomaly_output'].format(timestamp=timestamp)

        try:
            DataPersistence.save_anomalies(anomalies_df, output_path)
            print(f"Anomaly detection CSV written to: {output_path}")
            logging.info(f"Anomaly detection CSV written to: {output_path}")

        except Exception as save_error:
            logging.error(f"Error saving anomaly detection CSV: {save_error}")
            print(f"Error saving anomaly detection CSV: {save_error}")

        return anomalies_df  # Return the DataFrame (which may be empty)
        
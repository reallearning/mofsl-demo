import os
import json
import time
import logging
from logging.handlers import RotatingFileHandler
import asyncio
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import threading
from bs4 import BeautifulSoup
import pyodbc
import datetime
import requests
import schedule
from threading import Thread
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from agent.classifier_agent import classifier_agent
from agent.generate_response_agent import ResponseGeneratorAgent

# Create logs directory if it doesn't exist
os.makedirs("logs", exist_ok=True)

# Create a thread pool for running synchronous IO operations
# This is crucial for preventing blocking of the event loop
thread_pool = ThreadPoolExecutor(max_workers=10)

# Configure logging
def setup_logger():
    """
    Set up a basic logger with rotation.
    """
    # Create logger
    logger = logging.getLogger("talisma_processor")
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # File handler (with rotation)
    file_handler = RotatingFileHandler(
        "logs/talisma_email_processor.log", 
        maxBytes=10485760,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    # Console handler for terminal output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - [%(levelname)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logger()

# Configuration
CONFIG = {
    "UAT": {
        "server": os.getenv("UAT_SERVER", ""),
        "port": os.getenv("UAT_PORT", ""),
        "database": os.getenv("UAT_DATABASE", ""),
        "username": os.getenv("UAT_USERNAME", ""),
        "password": os.getenv("UAT_PASSWORD", ""),
        "driver": os.getenv("UAT_DRIVER", "")
    },
    "LIVE": {
        "server": os.getenv("LIVE_SERVER", ""),
        "port": os.getenv("LIVE_PORT", ""),
        "database": os.getenv("LIVE_DATABASE", ""),
        "username": os.getenv("LIVE_USERNAME", ""),
        "password": os.getenv("LIVE_PASSWORD", ""),
        "driver": os.getenv("LIVE_DRIVER", "")
    },
    "environment": os.getenv("ENVIRONMENT", "UAT"),  # Change to "LIVE" for production
    "processed_emails_file": os.getenv("PROCESSED_EMAILS_FILE", "processed_emails.json"),
    "queue_file": os.getenv("QUEUE_FILE", "email_queue.json"),
    "output_dir": os.getenv("OUTPUT_DIR", "processed_output"),
    "poll_interval_minutes": int(os.getenv("POLL_INTERVAL_MINUTES", "1")),
    "max_concurrent_emails": int(os.getenv("MAX_CONCURRENT_EMAILS", "5")),
    "queue_check_interval_seconds": int(os.getenv("QUEUE_CHECK_INTERVAL_SECONDS", "10")),
    "last_pull_time_file": os.getenv("LAST_PULL_TIME_FILE", "last_pull_time.json"),
    "base_url": os.getenv("BASE_URL", "http://localhost:8000")
}

# Ensure output directory exists
os.makedirs(CONFIG["output_dir"], exist_ok=True)

# Email Queue Class
class EmailQueue:
    def __init__(self, queue_file):
        self.queue_file = queue_file
        self.lock = threading.Lock()
        self.queue = self._load_queue()
    
    def _load_queue(self):
        """Load queue from file."""
        try:
            if os.path.exists(self.queue_file):
                with self.lock:
                    with open(self.queue_file, "r") as f:
                        data = json.load(f)
                        logger.info(f"SYSTEM | Loaded {len(data)} emails in queue")
                        return data
            logger.info("SYSTEM | No existing queue found, starting fresh")
            return []
        except Exception as e:
            logger.error(f"SYSTEM | Error loading queue: {e}")
            return []
    
    def _save_queue(self):
        """Save queue to file."""
        try:
            with self.lock:
                with open(self.queue_file, "w") as f:
                    json.dump(self.queue, f, indent=2)
                    logger.info(f"SYSTEM | Saved {len(self.queue)} emails to queue")
        except Exception as e:
            logger.error(f"SYSTEM | Error saving queue: {e}")
    
    def add_emails(self, emails):
        """Add emails to queue. Avoid duplicates."""
        added_count = 0
        with self.lock:
            existing_ids = {email["interaction_id"] for email in self.queue}
            for email in emails:
                if email["interaction_id"] not in existing_ids:
                    self.queue.append(email)
                    existing_ids.add(email["interaction_id"])
                    added_count += 1
        
        if added_count > 0:
            logger.info(f"SYSTEM | Added {added_count} new emails to queue")
            self._save_queue()
        
        return added_count
    
    def get_batch(self, batch_size):
        """Get a batch of emails for processing."""
        with self.lock:
            batch = self.queue[:batch_size]
            return batch
    
    def remove_emails(self, interaction_ids):
        """Remove processed emails from queue."""
        if not interaction_ids:
            return 0
        
        removed_count = 0
        with self.lock:
            self.queue = [email for email in self.queue if email["interaction_id"] not in interaction_ids]
            removed_count = len(interaction_ids)
        
        if removed_count > 0:
            logger.info(f"SYSTEM | Removed {removed_count} processed emails from queue")
            self._save_queue()
        
        return removed_count
    
    def get_length(self):
        """Get current queue length."""
        with self.lock:
            return len(self.queue)

# Initialize email queue
email_queue = EmailQueue(CONFIG["queue_file"])

def load_processed_emails():
    """Load the list of already processed email IDs."""
    try:
        if os.path.exists(CONFIG["processed_emails_file"]):
            with open(CONFIG["processed_emails_file"], "r") as f:
                data = json.load(f)
                logger.info(f"SYSTEM | Loaded {len(data)} previously processed emails")
                return data
        logger.info("SYSTEM | No previously processed emails found, starting fresh")
        return []
    except Exception as e:
        logger.error(f"SYSTEM | Error loading processed emails: {e}")
        return []

def save_processed_emails(processed_emails):
    """Save the updated list of processed email IDs."""
    try:
        with open(CONFIG["processed_emails_file"], "w") as f:
            json.dump(processed_emails, f, indent=2)
            logger.info(f"SYSTEM | Saved {len(processed_emails)} processed email IDs")
    except Exception as e:
        logger.error(f"SYSTEM | Error saving processed emails: {e}")

def get_last_pull_time():
    """Get the timestamp of the last successful pull."""
    try:
        if os.path.exists(CONFIG["last_pull_time_file"]):
            with open(CONFIG["last_pull_time_file"], "r") as f:
                data = json.load(f)
                return datetime.datetime.fromisoformat(data["last_pull_time"])
        # Default to 1 day ago if no previous pull
        return datetime.datetime.now() - datetime.timedelta(minutes=30)
    except Exception as e:
        logger.error(f"SYSTEM | Error loading last pull time: {e}")
        return datetime.datetime.now() - datetime.timedelta(minutes=30)

def save_last_pull_time(pull_time):
    """Save the timestamp of the last successful pull."""
    try:
        with open(CONFIG["last_pull_time_file"], "w") as f:
            json.dump({"last_pull_time": pull_time.isoformat()}, f)
            logger.info(f"SYSTEM | Last pull time saved: {pull_time.isoformat()}")
    except Exception as e:
        logger.error(f"SYSTEM | Error saving last pull time: {e}")

def clean_html(raw_html):
    # Use BeautifulSoup to remove HTML tags.
    soup = BeautifulSoup(raw_html, "html.parser")
    # Get the text, joining multiple tags with a space and stripping extra whitespace.
    return soup.get_text(separator=' ', strip=True)

# Modified to run in thread pool to avoid blocking the event loop
async def getUserType_async(email):
    """Async wrapper for getUserType to run in thread pool."""
    return await asyncio.get_event_loop().run_in_executor(
        thread_pool, getUserType, email
    )

def getUserType(email):
    """Get user type from MOFSL API for given email address.
    
    Args:
        email (str): Email address to lookup
        
    Returns:
        tuple: (user_type, client_id) - User type and client ID from API response
               Returns ("", "") if API call fails
    """
    try:
        # Step 1: Generate token
        token_url = f"{CONFIG['base_url']}/getuserinfo/api/getuserinfo/generatetoken"
        token_payload = {"username": "TOKEN"}
        token_headers = {"Content-Type": "application/json"}
        
        token_response = requests.post(token_url, json=token_payload, headers=token_headers)
        token = token_response.json()
        
        # Step 2: Get user info with token
        user_url = f"{CONFIG['base_url']}/getuserinfo/api/getuserinfo/fetchdata"
        user_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        user_payload = {"emailid": email}
        
        user_response = requests.post(user_url, json=user_payload, headers=user_headers)
        user_data = user_response.json()

        if "Table" in user_data and len(user_data["Table"]) > 0:
            user = user_data["Table"][0]
            return user["UserRole"].lower(), user["ClientId"].lower()
            
        return "", ""
        
    except Exception as e:
        logger.error(f"API | Error getting user type for email [{email}]: {e}")
        return "", ""

# Modified to run in thread pool to avoid blocking the event loop
async def pull_emails_from_talisma_async():
    """Async wrapper for pull_emails_from_talisma to run in thread pool."""
    return await asyncio.get_event_loop().run_in_executor(
        thread_pool, pull_emails_from_talisma
    )

def pull_emails_from_talisma():
    """
    Retrieve new emails from Talisma database using ODBC connection.
    Returns a list of email dictionaries.
    """
    logger.info(f"SYSTEM | Pulling emails from Talisma ({CONFIG['environment']} environment)")
    
    env = CONFIG["environment"]
    server = CONFIG[env]["server"]
    port = CONFIG[env]["port"]
    database = CONFIG[env]["database"]
    username = CONFIG[env]["username"]
    password = CONFIG[env]["password"]
    driver = CONFIG[env]["driver"]
    
    # Get last pull time
    start_date = get_last_pull_time()
    end_date = datetime.datetime.now()
    
    logger.info(f"SYSTEM | Pulling emails from {start_date.isoformat()} to {end_date.isoformat()}")
    
    # Connection string
    conn_str = (
        f'DRIVER={driver};'
        f'SERVER={server},{port};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
    )
    
    conn = None
    cursor = None
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        logger.info("DATABASE | Connection successful")
        
        # Execute the stored procedure
        sql = "EXEC SP_EBOT_Interactions @Startdate = ?, @Enddate = ?"
        cursor.execute(sql, start_date, end_date)
        
        # Fetch results
        rows = cursor.fetchall()
        logger.info(f"DATABASE | Fetched {len(rows)} interaction rows from Talisma")
        
        # Convert rows to list of dictionaries
        data = []
        columns = [column[0] for column in cursor.description]
        
        for row in rows:
            row_dict = {}
            for i in range(len(columns)):
                value = row[i]
                # Handle datetime conversion
                if isinstance(value, datetime.datetime):
                    value = value.isoformat()
                row_dict[columns[i]] = value

            created_at = row_dict.get("dCreatedAt")
            if not created_at:
                continue
                
            # Convert string date to datetime if needed
            if isinstance(created_at, str):
                try:
                    created_at = datetime.datetime.fromisoformat(created_at)
                except ValueError:
                    continue
                    
            # Check if interaction falls within date range
            if created_at.date() not in [datetime.date(2025, 5, 9), datetime.date(2025, 5, 12)]:
                continue

            from_email=row_dict.get("tFrom","")
            interaction_id=row_dict.get("aGlobalCaseId","")
            mMsgContent=row_dict.get("mMsgContent","")
            case_subject=row_dict.get("CaseSubject","")
            content=clean_html(mMsgContent)

      
            email_data = {
                "interaction_id": interaction_id,
                "from_email": from_email,
                "to_email": row_dict.get("tTo", ""),
                "subject": case_subject,
                "content": content,
                "user_type": "",
                "created_at": created_at
            }
            data.append(email_data)
        
        # If successful, update the last pull time
        if len(rows) > 0:
            save_last_pull_time(end_date)
        
        return data
        
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logger.error(f"DATABASE | Error occurred (SQLSTATE: {sqlstate}): {ex}")
        return []
    except Exception as e:
        logger.error(f"SYSTEM | Error pulling emails from Talisma: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
            logger.debug("DATABASE | Cursor closed")
        if conn:
            conn.close()
            logger.debug("DATABASE | Connection closed")

# Modified to run in thread pool to avoid blocking the event loop
async def generate_token_async(username):
    """Async wrapper for generate_token to run in thread pool."""
    return await asyncio.get_event_loop().run_in_executor(
        thread_pool, generate_token, username
    )

def generate_token(username):
    """Function to generate token for closure validation"""
    url = f"{CONFIG['base_url']}/aimodelresponse/api/airesponse/generatetoken"

    headers = {"Content-Type": "application/json"}
    data = {"username": username}

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()  # Assuming the response contains the token in JSON format
    except requests.exceptions.HTTPError as e:
        logger.error(f"API | HTTP Error generating token: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"API | Request Error generating token: {e}")
    return None

async def sendResponseToMO(response: dict):
    interaction_id = response['interaction_id']
    token = await generate_token_async("TOKEN")
    if token:
        url = f"{CONFIG['base_url']}/aimodelresponse/api/airesponse/insertdata"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Run this potentially blocking call in a thread pool
        def send_api_request():
            return requests.post(url, json=response, headers=headers)
        
        api_response = await asyncio.get_event_loop().run_in_executor(
            thread_pool, send_api_request
        )

        if api_response.status_code == 200:
            logger.info(f"Interaction id: {interaction_id} | Response sent to MO successfully")
        else:
            logger.error(f"Interaction id: {interaction_id} | Failed to send response to MO: Status {api_response.status_code}")
    else:
        logger.error(f"Interaction id: {interaction_id} | Failed to generate token")

async def process_single_email(email):
    """Process a single email."""
    email_start_time = time.time()
    interaction_id = email["interaction_id"]
    
    try:
        logger.info(f"Interaction id: {interaction_id} | Processing started")
        # Classify the email
        logger.info(f"Interaction id: {interaction_id} | Sending to classifier")
        category_start_time = time.time()
        # actual_from_email=from_email.split("\r")[1]
        actual_from_email=email["from_email"].split("\r")[1]

        def find_account_closure_required(subject: str, content: str) -> bool:
            """
            Check if email is related to account closure by looking for closure keywords
            in subject and content.
            """
            try:
                # Convert to lowercase for case-insensitive matching
                subject = subject.lower()
                content = content.lower()
                
                # Keywords to check for
                closure_keywords = ['close', 'closure']
                
                # Check subject and content for keywords
                for keyword in closure_keywords:
                    if keyword in subject or keyword in content:
                        return True
                return False
            except Exception as e:
                logger.error(f"Error checking for account closure: {e}")
                return False

        # Get user type asynchronously
        is_account_closure_required = find_account_closure_required(email["subject"], email["content"])
        [user_type, ClientId] = await getUserType_async(actual_from_email)
        logger.info(f"Interaction id: {interaction_id} | User Classification: User type: {user_type} | ClientId: {ClientId}")

        category={}

        if user_type=="nonclient":
            user_type="ba"
        if not(user_type=="client" or user_type=="ba"):
            logger.info(f"Interaction id: {interaction_id} | Skipping email from {actual_from_email} - User type is {user_type}")
            category = {
                "status": "success",
                "classification": "na",
                "is_spam": False,
                "escalation_required": True,
                "escalation_reason": f"User is not a client or BA. Current User Type is {user_type}"
            }
        elif not  is_account_closure_required:
            logger.info(f"Interaction id: {interaction_id} | Skipping email from {actual_from_email} - Account closure not required")
            category = {
                "status": "success",
                "classification": "na",
                "is_spam": False,
                "escalation_required": True,
                "escalation_reason": f"Account closure not required"
            }
        else:
            email["user_type"]=user_type
            category = await classifier_agent(
                email["from_email"], 
                email["subject"], 
                email["content"], 
                email["user_type"]
            )

        classification_time = time.time() - category_start_time
        
        if category.get("status") == "error":
            logger.error(f"Interaction id: {interaction_id} | Classification error: {category.get('error_message')}")
            return False

        # Log classification results
        classification = category.get("classification", "na")
        is_spam = category.get("is_spam", False)
        needs_escalation = category.get("escalation_required", False)
        
        logger.info(f"Interaction id: {interaction_id} | Classification: {classification} | Spam: {is_spam} | Escalation: {needs_escalation} | Time: {classification_time:.2f}s")
        
        response = {
            "explanation": "na",
            "apis_called": [], 
            "draft": "na",
            "scenario_id": "na",
            "cpg": {
                "scenario_id": "na",
                "scenario_name": "na",
                "sop": "na",
                "path": "na"
            }
        }
        
        # Handle spam or escalation
        if category["is_spam"]:
            logger.info(f"Interaction id: {interaction_id} | Identified as spam")
        elif category["escalation_required"]:
            logger.info(f"Interaction id: {interaction_id} | Requires escalation: {category['escalation_reason']}")
        elif category["classification"] == "na":
            logger.info(f"Interaction id: {interaction_id} | Classification not available")
        else:
            # Generate response
            response_start_time = time.time()
            logger.info(f"Interaction id: {interaction_id} | Generating response")
            custom_subject=email['subject']
            if ClientId != "":
                custom_subject=f"{email['subject']} - my ClientId is {ClientId}"
                logger.info(f"Interaction id: {interaction_id} | custom_subject : {custom_subject}")
            
            response_generator = ResponseGeneratorAgent()
            
            response = await response_generator.process_email(
                
                email_data = {
                    "from_email": email["from_email"],
                    "subject": custom_subject,
                    "content": email["content"],
                    "user_type": email["user_type"],
                    "classification": category["classification"]
                }
            )
            
            response_time = time.time() - response_start_time
            logger.info(f"Interaction id: {interaction_id} | Response generated in {response_time:.2f}s")
        
        output = {
            "interaction_id": email["interaction_id"],
            "body": {
                "interaction_id": email["interaction_id"],
                "from_email": email["from_email"],
                "to_email": email["to_email"],
                "subject": email["subject"],
                "body": email["content"],
                "user_type": email["user_type"],
                "classification": category["classification"],
                "escalation":{
                    "escalation_required": category["escalation_required"],
                    "escalation_reason": category["escalation_reason"] if category["escalation_reason"] is not None else "na"
                },
                "is_spam": category["is_spam"],
                "ask": response.get("explanation", "na"),
                "apis_called": response.get("apis_called", []),
                "response_draft": response.get("draft", "na"),
                "cpg": response.get("cpg", {}),
                 "additional_fields": {
                    "folio_number": -1,
                    "set_to_resolved": "na",
                    "pms_end_client": "na",
                    "lan": "na",
                    "query_nature": "na",
                    "location": "na",
                    "others": "na",
                    "reopen": "na",
                    "ftr_or_follow_up": "na",
                    "mode_of_interaction": "na",
                    "master_department": "na",
                    "department": "na",
                    "query_type": "na",
                    "sub_query_type": "na",
                    "interaction_category": "na",
                    "process_deviation": "na",
                    "originated": "na",
                    "beyond_tat": "na",
                    "remark_of_deviation": "na",
                    "updated_value": "na",
                    "processed_by": "na",
                    "ebot_mail_received": "na"
                }
            }
        }
        
        # Send response to MO asynchronously
        # await sendResponseToMO(output)
        
        # Save to JSON file - run in thread pool to avoid blocking
        async def save_output_file():
            output_file = os.path.join(CONFIG["output_dir"], f"{email['interaction_id']}.json")
            def save_file():
                with open(output_file, "w") as f:
                    json.dump(output, f, indent=2)
            await asyncio.get_event_loop().run_in_executor(thread_pool, save_file)
        
        await save_output_file()
        
        # Log processing summary
        email_processing_time = time.time() - email_start_time
        logger.info(f"Interaction id: {interaction_id} | Processing completed in {email_processing_time:.2f}s")
        
        return {
            "status":"success",
            **output
        }
        
    except Exception as e:
        logger.error(f"Interaction id: {interaction_id} | Processing failed: {str(e)}")
        return {
            "status":"failed"
        }

async def process_email_batch():
    """Process a batch of emails from the queue concurrently."""
    # Load processed emails to avoid reprocessing
    processed_email_ids = load_processed_emails()
    
    # Get batch of emails from queue
    max_emails = CONFIG["max_concurrent_emails"]
    batch = email_queue.get_batch(max_emails)
    
    if not batch:
        logger.debug("SYSTEM | Queue empty - no emails to process")
        return
    
    logger.info(f"SYSTEM | Processing batch of {len(batch)} emails from queue")
    
    # Filter out already processed emails
    new_emails = [email for email in batch if email["interaction_id"] not in processed_email_ids]
    skipped_count = len(batch) - len(new_emails)
    
    if skipped_count > 0:
        logger.info(f"SYSTEM | Skipped {skipped_count} already processed emails")
    
    if not new_emails:
        # Remove all emails in this batch from queue since they're already processed
        email_queue.remove_emails([email["interaction_id"] for email in batch])
        return
    
    # Process emails concurrently
    tasks = [process_single_email(email) for email in new_emails]
    results = await asyncio.gather(*tasks)
    
    # Identify successfully processed emails
    successful_ids = [email["interaction_id"] for email, result in zip(new_emails, results) if isinstance(result, dict) and result.get("status")=="success"]
    
    # Update processed emails list
    if successful_ids:
        processed_email_ids.extend(successful_ids)
        save_processed_emails(processed_email_ids)
    
    # Remove processed emails from queue
    removed_count = email_queue.remove_emails(successful_ids)
    logger.info(f"SYSTEM | Removed {removed_count} successfully processed emails from queue")
    
    # Log summary
    success_count = len(successful_ids)
    failure_count = len(new_emails) - success_count
    logger.info(f"SYSTEM | Batch processing summary: {success_count} succeeded, {failure_count} failed, {skipped_count} skipped")

async def pull_emails_task():
    """Task to pull emails from Talisma and add them to the queue."""
    logger.info("SYSTEM | Starting email pull cycle")
    
    try:
        # Pull new emails from Talisma asynchronously
        emails = await pull_emails_from_talisma_async()
        logger.info(f"SYSTEM | Retrieved {len(emails)} emails from Talisma")
        
        # Add emails to queue
        if emails:
            added_count = email_queue.add_emails(emails)
            logger.info(f"SYSTEM | Added {added_count} new emails to queue")
        
        logger.info(f"SYSTEM | Current queue size: {email_queue.get_length()} emails")
        
    except Exception as e:
        logger.error(f"SYSTEM | Error in pull emails task: {e}")
    
    logger.info("SYSTEM | Email pull cycle complete")

async def queue_processor_task():
    """Background task that continuously processes emails from the queue."""
    logger.info("SYSTEM | Starting queue processor task")
    
    while True:
        try:
            queue_size = email_queue.get_length()
            if queue_size > 0:
                logger.info(f"SYSTEM | Processing queue with {queue_size} emails")
                await process_email_batch()
            else:
                logger.debug("SYSTEM | Queue is empty, waiting for new emails")
                
            # Wait before checking queue again
            await asyncio.sleep(CONFIG["queue_check_interval_seconds"])
            
        except Exception as e:
            logger.error(f"SYSTEM | Error in queue processor: {e}")
            await asyncio.sleep(30)  # Longer wait on error

async def api_process_single_email(email_data):
    """Process a single email received via API."""
    # Add email to queue
    added = await process_single_email(email_data)
    return added

async def scheduler_loop():
    """Run the email pull task on schedule."""
    logger.info(f"SYSTEM | Starting scheduler loop with {CONFIG['poll_interval_minutes']} minute intervals")
    
    while True:
        try:
            await pull_emails_task()
            # Wait for next scheduled run
            await asyncio.sleep(CONFIG['poll_interval_minutes'] * 60)
        except Exception as e:
            logger.error(f"SYSTEM | Error in scheduler loop: {e}")
            await asyncio.sleep(60)  # Wait a minute before retrying

# Create a lifespan context manager for handling startup/shutdown events
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application"""
    # Startup: Initialize everything when the FastAPI app starts
    logger.info("SYSTEM | Application starting")

    await pull_emails_task()
    
    # Start the background tasks
    # task1 = asyncio.create_task(scheduler_loop())
    task2 = asyncio.create_task(queue_processor_task())
    
    logger.info("SYSTEM | Application initialized successfully")
    
    try:
        yield  # This is where FastAPI runs and serves requests
    finally:
        # Shutdown: Clean up resources
        logger.info("SYSTEM | Application shutting down")
        # Cancel background tasks
        # task1.cancel()
        task2.cancel()
        # Close thread pool
        thread_pool.shutdown(wait=False)
        logger.info("SYSTEM | Background tasks and resources cleaned up")


# Create FastAPI app with lifespan
app = FastAPI(
    title="Talisma Email Processor API",
    description="API for processing individual emails from Talisma",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define email model
class EmailData(BaseModel):
    interaction_id: int
    from_email: str
    to_email: str
    subject: str
    content: str
    user_type: str

# Process email endpoint
@app.post("/api/process-email", tags=["Email Processing"])
async def api_process_email(email_data: EmailData):
    """
    Process a single email immediately
    
    This endpoint allows processing a single email by adding it to the queue.
    """
    logger.info(f"API | Received request to process email {email_data.interaction_id}")
    
    # Convert Pydantic model to dict
    email_dict = {
        "interaction_id": email_data.interaction_id,
        "from_email": email_data.from_email,
        "to_email": email_data.to_email,
        "subject": email_data.subject,
        "content": email_data.content,
        "user_type": email_data.user_type
    }
    
    # Add email to processing queue
    result = await api_process_single_email(email_dict)
    return result

# Queue status endpoint
@app.get("/api/queue-status", tags=["Queue Management"])
async def queue_status():
    """
    Get the current status of the email processing queue
    
    Returns the number of emails currently in the queue
    """
    queue_length = email_queue.get_length()
    return {
        "status": "active",
        "queue_size": queue_length,
        "max_concurrent_processing": CONFIG["max_concurrent_emails"]
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns the status of the API and scheduler
    """
    return {
        "status": "healthy",
        "environment": CONFIG["environment"],
        "poll_interval": f"{CONFIG['poll_interval_minutes']} minutes",
        "queue_size": email_queue.get_length(),
        "max_concurrent": CONFIG["max_concurrent_emails"]
    }

# Main entry point
if __name__ == "__main__":
    try:
        logger.info("SYSTEM | Starting Talisma Email Processor with queue-based processing")
        port = int(os.getenv("API_PORT", 8080))
        
        # Configure uvicorn with log settings to prevent color code issues
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port, 
            log_level="info",
            log_config={
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "()": "uvicorn.logging.DefaultFormatter",
                        "fmt": "%(asctime)s - %(levelname)s - %(message)s",
                        "use_colors": False,
                    },
                    "access": {
                        "()": "uvicorn.logging.AccessFormatter",
                        "fmt": '%(asctime)s - %(levelname)s - %(client_addr)s - "%(request_line)s" %(status_code)s',
                        "use_colors": False,
                    },
                },
                "handlers": {
                    "default": {
                        "formatter": "default",
                        "class": "logging.StreamHandler",
                        "stream": "ext://sys.stderr",
                    },
                    "access": {
                        "formatter": "access",
                        "class": "logging.StreamHandler",
                        "stream": "ext://sys.stdout",
                    },
                },
                "loggers": {
                    "uvicorn": {"handlers": ["default"], "level": "INFO"},
                    "uvicorn.error": {"level": "INFO"},
                    "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
                },
            }
        )
    except KeyboardInterrupt:
        logger.info("SYSTEM | Server stopping due to keyboard interrupt")
    except Exception as e:
        logger.error(f"SYSTEM | Unexpected error: {e}")
    finally:
        logger.info("SYSTEM | Server stopped")
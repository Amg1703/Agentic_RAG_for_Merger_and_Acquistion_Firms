import os 
import logging 
import uuid
import datetime

# LETS LOAD THE ENVIRONMENTAL VARIABLES 
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pipeline.ingestion_and_embedding_pipeline import ingest_document

import inngest
import inngest.fast_api
from inngest.experimental import ai
import logging 

# LETS DEFINE THE INNGEST CLIENT 

inngest_client=inngest.Inngest(
    # HERE APP ID IS THE NAME IS THE NAME OF APPLICATION INNGEST SHOULD OBSERVE
    app_id='M&A_AGENTIC_RAG',
    # LOGGER IS USED TO CHECK THE LOGS OF OUR APPLICATION AND SINCE WE USE FASTAPI WE USE UVICORN AS THE LOGGER
    logger=logging.getLogger('uvicorn'),
    # IS_PRODUCTION IS SET TO FALSE AS ELSE THE SECURITY WILL BE A BIT TIGHT
    is_production=False,
    # SERIALIZER ARE NOTHING BUT TYPE HINTING FOR PYTHON HERE WE USE PYDANTIC AS THE SERIALIZER
    serializer=inngest.PydanticSerializer()
)
# SO WE IN ORDER TO GIVE INNGEST THE ACCESS TO OBSERVE AND MONITOR OUR APIS WE NEED TO CREATE INNGEST FUNCTIONS 

@inngest_client.create_function(
    fn_id='RAG: INGEST DOCUMENTS',
    trigger=inngest.TriggerEvent(event="call_ingest_document_pipeline")
)
async def call_ingest_document_pipeline(context: inngest.Context):
    # THIS FUNCTION WILL BE TRIGGERED WHEN THE EVENT "ingest_document" IS CALLED 
    # THE CONTEXT PARAMETER CONTAINS ALL THE INFORMATION ABOUT THE EVENT AND THE DATA THAT IS PASSED TO THE EVENT 
    # WE CAN ACCESS THE DATA USING context.data 
    data = context.data
    # NOW WE CAN CALL THE ACTUAL INGEST FUNCTION THAT WE HAVE DEFINED IN pipeline/ingest.py 
    result = await ingest_document_pipeline(context)
    return result

@inngest_client.create_function(fn_id='RETRIEVE DOCUMENTS BASED ON USER QUERY', 
                                trigger=inngest.TriggerEvent(event='call_retrieve_documents_pipeline'))
async def call_retrieve_documents_pipeline(context: inngest.Context):
    result = await retrieve_documents(context)
    return result 



app = FastAPI()

#  SO HERE INNGEST SIT IN BETWEEN OUR API AND CLIENT 
# NORMALLY WHEN THE USER SENDS A REQUEST TO OUR FRONTEND IT IS DIRECTED TO OUR API DIRECTLY
# BUT NOW INNGEST THE CLIENTS REQUEST IS FORWARED TO INNGEST'S DEVELOPMENTAL SERVER WHICH THEN FORMATS AND FORWARDS IT TO OUR API 
inngest.fast_api.serve(app, inngest_client, functions=[ingest_document,retrieve_documents])


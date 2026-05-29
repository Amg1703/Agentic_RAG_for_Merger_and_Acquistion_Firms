import os 
import logging 
import uuid
import datetime

# LETS LOAD THE ENVIRONMENTAL VARIABLES 
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI

# import inngest
# import inngest.fast_api
# from inngest.experimental import ai
# import logging 

# # LETS DEFINE THE INNGEST CLIENT 

# inngest_client=inngest.Inngest(
#     # HERE APP ID IS THE NAME IS THE NAME OF APPLICATION INNGEST SHOULD OBSERVE
#     app_id='M&A_AGENTIC_RAG',
#     # LOGGER IS USED TO CHECK THE LOGS OF OUR APPLICATION AND SINCE WE USE FASTAPI WE USE UVICORN AS THE LOGGER
#     logger=logging.getLogger('uvicorn'),
#     # IS_PRODUCTION IS SET TO FALSE AS ELSE THE SECURITY WILL BE A BIT TIGHT
#     is_production=False,
#     # SERIALIZER ARE NOTHING BUT TYPE HINTING FOR PYTHON HERE WE USE PYDANTIC AS THE SERIALIZER
#     serializer=inngest.PydanticSerializer()
# )
# # SO WE IN ORDER TO GIVE INNGEST THE ACCESS TO OBSERVE AND MONITOR OUR APIS WE NEED TO CREATE INNGEST FUNCTIONS 

# @inngest_client.create_function(
#     fn_id='RAG: INGEST DOCUMENTS',
#     trigger=inngest.TriggerEvent(event="call_ingest_document_pipeline")
# )
# async def call_ingest_document_pipeline(context: inngest.Context):
#     # THIS FUNCTION WILL BE TRIGGERED WHEN THE EVENT "ingest_document" IS CALLED 
#     # THE CONTEXT PARAMETER CONTAINS ALL THE INFORMATION ABOUT THE EVENT AND THE DATA THAT IS PASSED TO THE EVENT 
#     # WE CAN ACCESS THE DATA USING context.data 
#     data = context.data
#     # NOW WE CAN CALL THE ACTUAL INGEST FUNCTION THAT WE HAVE DEFINED IN pipeline/ingest.py 
#     result = await ingest_document_pipeline(context)
#     return result

# @inngest_client.create_function(fn_id='RETRIEVE DOCUMENTS BASED ON USER QUERY', 
#                                 trigger=inngest.TriggerEvent(event='call_retrieve_documents_pipeline'))
# async def call_retrieve_documents_pipeline(context: inngest.Context):
#     result = await retrieve_documents(context)
#     return result 



app = FastAPI()

# #  SO HERE INNGEST SIT IN BETWEEN OUR API AND CLIENT 
# # NORMALLY WHEN THE USER SENDS A REQUEST TO OUR FRONTEND IT IS DIRECTED TO OUR API DIRECTLY
# # BUT NOW INNGEST THE CLIENTS REQUEST IS FORWARED TO INNGEST'S DEVELOPMENTAL SERVER WHICH THEN FORMATS AND FORWARDS IT TO OUR API 
# inngest.fast_api.serve(app, inngest_client, functions=[ingest_document,retrieve_documents])

import os
import logging
import uuid

import inngest
from inngest import Inngest
from inngest.experimental import ai
import inngest.fast_api

from pipeline.ingestion_and_embedding_pipeline import pdf_loading_and_chunking_pipeline, embedding_pipeline
from pipeline.vector_db_storage_and_retrieval_pipeline import QdrantStorage
from pipeline.custom_data_types_pipeline import RAGChunkAndSource, RAGUpsertResult, RAGQueryResult, RAGSearchResult

inngest_client=Inngest(
    # HERE APP ID IS THE NAME IS THE NAME OF APPLICATION INNGEST SHOULD OBSERVE
    app_id='M&A_AGENTIC_RAG',   
    # WE HAVE SET A TIMEOUT OF 60 SECONDS BEYOND WHICH THE CONNECTION WILL BE CUT 
    request_timeout=60,
    # LOGGER IS USED TO CHECK THE LOGS OF OUR APPLICATION AND SINCE WE USE FASTAPI WE USE UVICORN AS THE LOGGER
    logger=logging.getLogger('uvicorn'),
    # IS_PRODUCTION IS SET TO FALSE AS ELSE THE SECURITY WILL BE A BIT TIGHT
    is_production=False,
    # SERIALIZER ARE NOTHING BUT TYPE HINTING FOR PYTHON HERE WE USE PYDANTIC AS THE SERIALIZER
    serializer=inngest.PydanticSerializer())

@inngest_client.create_function(fn_id='RAG: INGEST DOCUMENT', 
                                trigger=inngest.TriggerEvent(event='PDF_Loading_Chunking_Ingestion_and_VectorDB_storage_Pipeline'))
async def PDF_Loading_Chunking_Ingestion_and_VectorDB_Pipeline_Observation(context: inngest.Context):
    """ THIS FUNCTION WILL BE TRIGGERED WHEN THE EVENT "ingest_document" IS CALLED 
        THE CONTEXT PARAMETER CONTAINS ALL THE INFORMATION ABOUT THE EVENT AND THE DATA THAT IS PASSED TO THE EVENT 
        WE CAN ACCESS THE DATA USING context.data 
        NOW WE CAN CALL THE ACTUAL INGEST FUNCTION THAT WE HAVE DEFINED IN pipeline/ingestion pipeline and vector db storage pipeline"""
    
    """STEP - 1 - LOADING AND CHUNKING PIPELINE TO BE OBSERVED"""
    def PDF_loading_and_chunking_observation(context: inngest.Context) -> RAGChunkAndSource:
        pdf_path=context.event.data["pdf_path"]
        source_id=context.event.data.get("source_id", pdf_path)
        pdf_chunks=pdf_loading_and_chunking_pipeline(pdf_path)
        return RAGChunkAndSource(chunks=pdf_chunks, source_id=source_id)
    
    """ STEP - 2 - EMBEDDING THE PDF CHUNKS WITH OPENAI EMBEDDING MODEL 
        SO IT WILL TAKE IN THE PARAMETER OF LIST OF CHUNKS TO BE EMBEDDED AND RETURN EMBEDDING DATA TYPES WHICH IS 2 D LIST OF VECTORS
        EMBEDDINGS"""
    def embedding_PDF_chunks_observation(data: RAGChunkAndSource):
        source_id=data.source_id
        chunks_to_be_embedded=data.chunks
        embedded_PDF_chunks=embedding_pipeline(chunks_to_be_embedded)
        return embedded_PDF_chunks
    
    
    """ STEP - 3 - STORING THE CHUNKS IN THE VECTOR DB BY UPDATING AND INSERTING THEM IN THE QDRANT VECTOR DB"""
    def updating_inserting_embeddings_in_vector_db_observation(embedding_to_be_stored_in_vector_DB, chunks_for_payload: RAGChunkAndSource) -> RAGUpsertResult:
        
        qdrant = QdrantStorage()
        chunks=chunks_for_payload.chunks
        source_id=chunks_for_payload.source_id
        vectors=embedding_to_be_stored_in_vector_DB

        ids=[str(uuid.uuid4()) for _ in range(len(vectors))]
        payload=[{"source":source_id,"text":chunks[i]} for i in range(len(chunks))]

        qdrant.update_and_insert_new_vectors(ids, vectors, payload)
        return RAGUpsertResult(No_of_vectors_stored=len(vectors))
    
    PDF_ingestion_and_chunking_result=await context.step.run("PDF_ingestion_and_Chunking",lambda: PDF_loading_and_chunking_observation(context), output_type=RAGChunkAndSource)
    Embedding_PDF_result=await context.step.run("Embedding PDF Chunks",lambda: embedding_PDF_chunks_observation(PDF_ingestion_and_chunking_result))
    Storing_embeddings_in_vector_DB_result=await context.step.run("Storing Embeddings in Vector DB", lambda: updating_inserting_embeddings_in_vector_db_observation(Embedding_PDF_result,PDF_ingestion_and_chunking_result),output_type=RAGUpsertResult)
    return Storing_embeddings_in_vector_DB_result.model_dump()

    


""" SO HERE INNGEST SIT IN BETWEEN OUR API AND CLIENT 
    NORMALLY WHEN THE USER SENDS A REQUEST TO OUR FRONTEND IT IS DIRECTED TO OUR API DIRECTLY
    BUT NOW INNGEST THE CLIENTS REQUEST IS FORWARED TO INNGEST'S DEVELOPMENTAL SERVER WHICH THEN FORMATS AND FORWARDS IT TO OUR API""" 
inngest.fast_api.serve(app=app, client=inngest_client, functions=[PDF_Loading_Chunking_Ingestion_and_VectorDB_Pipeline_Observation])
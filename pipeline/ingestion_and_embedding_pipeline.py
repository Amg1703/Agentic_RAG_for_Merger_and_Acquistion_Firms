import os
from dotenv import load_dotenv
""" LLMSHERPA READERS IS USED FOR CHUNKING THE PDF BASED ON HIERARCHIAL INFORMATION SUCH AS SECTIONS SUBSECTIONS PARAGRAPHS AND TABLES
    THE CHUNKS ARE CONTEXT AWARE"""
from llmsherpa.readers import LayoutPDFReader
from llama_index.embeddings.openai import OpenAIEmbedding

# INITIALLIZING THE ENVIRONMENTAL VARIABLES FOR THIS PIPELINE 
load_dotenv()
os.environ['OPENAI_api_key']=os.getenv('OPENAI_API_KEY')
llmsherpa_api_url=os.getenv("LLMSHERPA_API_URL")

# THE DIMENSIONS SHOULD MATCH THE SAME NUMBER OF DIMENSIONS YOU SET IN THE VECTOR DB STORAGE 
embedding=OpenAIEmbedding(model='text-embedding-3-small', dimensions=3072, timeout=300)

""" THIS IS THE LOADING AND CHUNKING PIPELINE WHERE WE SUPPLY THE LOCAL PATH OR URL OF THE PDF FILE AND THEN USE LLMSHERPA API TO 
    TO LOAD AND CHUNK THE PDF THE LAYOUT PDF READER AUTOMATICALLY CHUNKS THE PDF BASED ON SECTIONS PARAGRAPHS AND TABLES"""
def pdf_loading_and_chunking_pipeline(path_of_uploaded_file:str):
    pdf_loader_and_reader=LayoutPDFReader(parser_api_url=llmsherpa_api_url)
    """ NOW THE PDF IS JUST CONVERTED INTO A DOCUMENT DATASTRUCTURE WHERE IT WILL OF ELEMENTS LIKE SECTION,PARAGRAPH, TABLES AND IN 
        THE END CHUNKS() 
        ESENTIALLY HERE IT IS JUST A STRUCTURED VERSION OF THE PDF STORED AS A DOCUMENT OBJECT"""
    ingested_pdf_as_document_object=pdf_loader_and_reader.read_pdf(path_or_url=path_of_uploaded_file)
    """NOW LETS DEFINE AN EMPTY OF LIST OF CHUNKS WHERE EACH CHUNK OF THE DOCUMENT DATASTRUCTURE WILL BE APPENDED ONE BY ONE
        THE DOCUMENT_OBJECT.CHUNKS() CONSISTS OF THE SEMANTIC CHUNKS 
        AND EACH OF THESE CHUNKS IS STORED UNDER CHUNKS() IN THE DOCUMENT AND WE .TO_CONTEXT_TEXT() TO """
    list_of_chunks_from_ingested_pdf=[]
    
    for each_chunk in ingested_pdf_as_document_object.chunks():
        list_of_chunks_from_ingested_pdf.append(each_chunk.to_context_text())

    return list_of_chunks_from_ingested_pdf


def embedding_pipeline(text_to_be_chunked: list[str]) -> list[list[float]]:
    embedding.get_text_embedding(text_to_be_chunked)
import os
from dotenv import load_dotenv
from llama_index.embeddings.openai import OpenAIEmbedding
from liteparse import LiteParse
from llama_index.core.text_splitter import SentenceSplitter
import camelot
import uuid
import re

# INITIALLIZING THE ENVIRONMENTAL VARIABLES FOR THIS PIPELINE 
load_dotenv()
os.environ['OPENAI_API_KEY']=os.getenv('OPENAI_API_KEY')

# THE DIMENSIONS SHOULD MATCH THE SAME NUMBER OF DIMENSIONS YOU SET IN THE VECTOR DB STORAGE 
embedding=OpenAIEmbedding(model='text-embedding-3-small', dimensions=1536, timeout=300)

""" THIS IS THE LOADING AND CHUNKING PIPELINE WHERE WE SUPPLY THE LOCAL PATH OR URL OF THE PDF FILE AND THEN USE LLMSHERPA API TO 
    TO LOAD AND CHUNK THE PDF THE LAYOUT PDF READER AUTOMATICALLY CHUNKS THE PDF BASED ON SECTIONS PARAGRAPHS AND TABLES"""
def pdf_loading_and_chunking_pipeline(path_of_uploaded_file:str):
    import os
    print("PDF exists:", os.path.exists(path_of_uploaded_file))
    print("PDF path:", path_of_uploaded_file)

    parser=LiteParse()
    extracted_text_from_pdf=parser.parse(file_data=path_of_uploaded_file,ocr_enabled=True,ocr_language="en")
    # THE EXTRACTED TEXT THAT LITEPARSER GIVES IS FULLY SCATTER WITH SPACE HENCE WE USING REGEX EXPRESSION TO BIND THE SCATTERED
    # SPLIT WORDS INTO PROPER FORM THAT CAN BE CHUNKED AND EMBEDDED PROPERLY 

    def clean_liteparser_text(text):
         text=re.sub(r"\s+", " ",text)
         return text.strip()
    
    splitter=SentenceSplitter(chunk_size=512,chunk_overlap=100)
    textual_chunks_from_document=[]

    for page in extracted_text_from_pdf.pages:

        page_num = page.pageNum

        page_text=clean_liteparser_text(page.text)
        if not page_text:
            continue

        split_chunks = splitter.split_text(page_text)

        for chunk in split_chunks:

            textual_chunks_from_document.append({
                "text": chunk,
                "type": "text",
                "page": page_num,
                "source": path_of_uploaded_file,
                "chunk_id": str(uuid.uuid4())
            })
    
    """EXTRACTING TABLES - ONLY TABLES ARE EXTRACTED FROM THE PDF USING CAMELOT"""
    extracted_table_from_camelot=camelot.read_pdf(path_of_uploaded_file, pages="all")

    tabular_chunks_from_document=[]

    for i, each_element_of_table in enumerate(extracted_table_from_camelot):
            # CONVERTING TABLE INTO A DATAFRAME
            df=each_element_of_table.df
            # CONVERTING THE DATA FRAME INTO STRING AS OPENAI EMBEDDINGS ONLY EMBED STRINGS NOT DATAFRAMES
            text_extracted_from_table=f"""
                                        Financial Table:
                                        {df.to_markdown(index=False)}"""
            
            if len(text_extracted_from_table.replace("|", "").strip()) < 30:
                continue

            # APPENDING AND STORING THE EXTRACTED TEXT FROM THE TABLE AND ITERATING THIS FOR EACH AND EVERY ROW OF THE TABLE
            tabular_chunks_from_document.append({
                 "text":text_extracted_from_table,
                 "type":"table",
                 "page":each_element_of_table.page,
                 "source": path_of_uploaded_file,
                 "chunk_id": str(uuid.uuid4())
            })

    print("Text Chunks:", len(textual_chunks_from_document))
    print("Table Chunks:", len(tabular_chunks_from_document))

    text_and_table_chunks_in_documents=textual_chunks_from_document+tabular_chunks_from_document

    return text_and_table_chunks_in_documents
    
    """IMAGE EXTRACTION FROM DOCUMENT - ONLY PAGES WITH LESS TEXT DENSITY ARE EXTRACTED 
        WILL BE AVAILABLE IN NEXT VERSION """ 

"""CALLING THE GET_TEXT_EMBEDDING BATCH FUNCTION SINCE EMBEDDING TEXT EMBEDDS ONLY A STRING BUT WHEREASE WE ARE PASSING A LIST OF STRINGS
WHICH CAN ONLY BE EMBEDDED BY THE EMBEDDING BATCH FUNCTIONS AND PASSING THE LIST OF TEXTS TO BE EMBEDDED AND RETURNING THE EMBEDDED PDF WHICH IS THE
VECTORIZED VERSION OF THE PDF"""
def embedding_pipeline(chunks):
    collective_list_of_all_chunks=[chunk["text"] 
                                   for chunk in chunks]
    payload=[]
    for chunk in chunks:
         payload.append({
              "text":chunk["text"],
              "type":chunk["type"],
              "page":chunk["page"],
              "source":chunk["source"],
              "chunk_id":chunk["chunk_id"]
         })
    embedded_pdf=embedding.get_text_embedding_batch(collective_list_of_all_chunks)

    return {
         "vectors":embedded_pdf,
         "payloads":payload
            }


def query_embedding_pipeline(user_query:str):
     return embedding.get_query_embedding(user_query)


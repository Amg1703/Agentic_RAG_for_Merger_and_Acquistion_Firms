from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from ingestion_and_embedding_pipeline import query_embedding_pipeline

"""LETS CREATE A CLASS FOR QDRANT STORAGE 
 HERE THE URL WILL BE THE URL OF THE QDRANT VECTOR DB INITIALIZED IN DOCKER FOR PRODUCTION IT WILL BE THE INSTANCE OF THE VECTOR DB
 YOU ARE CONNECTED TO, COLLECTION PARAMATER IS THE COLLECTION NAME WE WANT TO GIVE TO COLLECTION IN THE VECTOR DATBASE 
 THAT WILL BE STORED HERE IT IS DOCS , THE DIM IS THE NUMBER OF DIMENSIONS IN THE VECTOR DB HERE IT 3072 WHICH MEANS THERE WILL BE 
 3072 ROWS FOR EACH MATRIX 
 """

class QdrantStorage:
    def __init__(self, url_of_vector_db_instance="http://localhost:6333", collection_name="docs", dimension_of_vector_db=1536):
        """WE ARE CREATING AN INSTANCE OF CLIENT CONNECTION TO THE VECTOR DB PASSING THE PARAMETER URL AND TIMEOUT BEYOND WHICH THE 
         CONNECTION WILL BE CUT AND THIS SELF.CLIENT WILL INHERIT ALL THE FUNCTION OF QDRANTCLIENT LIKE COLLECTION EXISTS AND 
         SEARCHING THE COLLECTION"""
        self.client=QdrantClient(url=url_of_vector_db_instance, timeout=30)
        # WE ARE JUST NAMING OUR COLLECTION HERE 
        self.collection_name=collection_name
        
        """ WE ARE CHECKING IF THE SELF.CLIENT ALREADY HAS CREATED A COLLECTION OR NOT IF IT DOESNT WE CREATE A NEW COLLECTION 
        PASSING THE COLLECTION NAME AS THE PARAMETER"""
        if not self.client.collection_exists(self.collection_name):
            """ CREATING A NEW COLLECTION PASSING THE COLLECTION AND VECTOR CONFIGS WHERE VECTORCONFIGS IS DEFINED USING VECTORPARAMS 
            FUNCTION WITH IT TAKING 2 PARAMETERS WITH SIZE DEFINED AS INITIAL DIMENSIONS OF VECTOR DB AND THE DISTANCE IS NOTHING BUT 
            THE DISTANCE AND SIMILARITY CALCULATED BETWEEN EACH VECTOR WHICH WILL BE CALCULATED BY COSINE SIMILARITY"""
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=dimension_of_vector_db, distance=Distance.COSINE)
            )
          
    # THIS METHOD IS USED TO UPDATE THE COLLECTION BY ADDING NEW INCOMING VECTOR

    def update_and_insert_new_vectors(self, incoming_ids,incoming_vectors, incoming_payloads):
        """ THIS FUNCTION WILL UPDATE THE VECTOR DB WITH THE NEW VECTORS AND PAYLOADS 
        THE IDS ARE THE UNIQUE IDENTIFIERS FOR EACH VECTOR 
        THE VECTORS ARE THE ACTUAL VECTORS THAT WE WANT TO STORE IN THE VECTOR DB 
        THE PAYLOADS ARE THE METADATA ASSOCIATED WITH EACH VECTOR WHICH 
        WE ARE CREATING A LIST OF POINTSTRUCT THAT WILL BE INSERTED INTO THE VECTOR DB
        THE POINTSTRUCT IS BASICALLY THE DATA STRUCTURE THAT QDRANT USES TO STORE THE VECTORS AND PAYLOADS
        SO HERE THE INCOMING POINTS IS A VARIABLE TO STORE THE POINTSTRUCT DATA STRUCT AND IT TAKES 3 PARAMETERS ID WHICH IS JUST 
        THE INDEXES OF EACH OF THE VECTORS AND THE VECTORS WHICH TAKES IN INCOMING VECTORS AND PAYLOAD IS THE HUMAN READABLE FORMAT OF
        EACH OF THE VECTOR AND EACH ELEMENT IS PASSED AND UPDATED AND IT IS ITERATED TILL IDS AS TOTAL NUMBER OF VECTORS AND PAYLOADS 
        CAN BE DIRECTLY CALCULATED BY THE LENGTH OF THE LIST OF INDEXES WHICH IS NOTHING BUT THE INCOMING IDS   """
        Incoming_points = [PointStruct(id=incoming_ids[i],vector=incoming_vectors[i],payload=incoming_payloads[i]) for i in range(len(incoming_ids))]
        self.client.upsert(collection_name=self.collection_name, points=Incoming_points)
    
    #  THIS METHOD IS USED TO SEARCH FOR THE SIMILAR VECTORS AND RETRIEVE IT 
    #  IT TAKES 2 PARAMETER ONE IS THE INCOMING QUERY VECTOR FROM THE USER AND THE OTHER 
    def search_based_on_user_query(self,user_query,top_k:int=5):
        """SEARCH CAN BE PERFORMED BY QUERY POINTS FUNCTION OF CLIENT WHICH TAKES IN THE PARAMETER
        COLLECTION_NAME WHICH WILL BE THE NAME OF COLLECTION WE CREATED
        WITH PAYLOAD IS SET TO TRUE INORDER TO RETRIEVE THE HUMAN READABLE CONTENT OF THE VECTORS 
        THE LIMIT IS NUMBER OF VECTORS THAT WILL BE RETURNED WHICH WE CAN SET TO WHATVEVER VALUE WE WANT TO MAKE IT OPTIMAL WE HAVE
        SET IT TO TOP_K=5"""
        # TO EMBED THE INCOMING USER QUERY TO CONVERT THE TEXT INTO EMBEDDING WHICH CAN BE USED TO MATCH FOR SIMILAR EMBEDDING IN THE VECTOR DB 
        incoming_query_vector_from_user=query_embedding_pipeline(user_query)
        results=self.client.query_points(
            collection_name=self.collection_name,
            query=incoming_query_vector_from_user,
            with_payload=True,
            limit=top_k
            )
        # NOW LETS DEFINE A SET AND A LIST TO STORE THE CONTEXT AND SOURCES WHICH WILL BE RETURNED IN THE RESULTS OF THE SEARCH
        # BUT HERE THERE IS NOT PARTICULAR ORDER OF THIS CONTEXT BELONGS TO THIS SOURCE
        # WE ARE CHOOSING SET FOR SOURCES SINCE WE DONT WANT THE SAME SOURCES TO BE REPEATED AND SINCE SET CANNOT HAVE DUPLICATES
    
        """ ITERATING THROUGH THE LISTS AND GETATTR IS USED TO GET A SPECIFC ATTRIBUTE WE ARE INDEXING THE PAYLOAD ATTRIBUTE IF NOT DEFAULT TO NONE
        AND CREATE AN EMPTY DICTIONARY
        FROM THE RETRIEVED RESULTS WE ARE EXTRACTING THE TEXT WHICH WILL BE THE CONTEXT AND BY DEFAULT THE SOURCES WILL ALSO BE 
        INCLUDED """
        retrieved_chunks=[]

        for r in results.points:
            retrieved_results=getattr(r,"payload",None) or {}
            retrieved_text=retrieved_results.get('text',"")
            retrieved_type=retrieved_results.get("type","")
            retrived_page=retrieved_results.get("page","")
            retrieved_source=retrieved_results.get('source',"")
            retrieved_chunk_id=retrieved_results.get("chunk_id","")

            retrieved_chunks.append({
                "text":retrieved_text,
                "type":retrieved_type,
                "page":retrived_page,
                "source":retrieved_source,
                "chunk_id":retrieved_chunk_id
            })

        return {
            "Retrieved Chunks, Page Number and its sources":retrieved_chunks
            }
    


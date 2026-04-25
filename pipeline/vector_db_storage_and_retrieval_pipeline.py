from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct


"""LETS CREATE A CLASS FOR QDRANT STORAGE 
 HERE THE URL WILL BE THE URL OF THE QDRANT VECTOR DB INITIALIZED IN DOCKER, COLLECTION IS THE COLLECTION OF THE VECTOR DATABASE 
 THAT WILL BE STORED THE DIM IS THE NUMBER OF DIMENSIONS IN THE VECTOR DB
 """
class QdrantStorage:
    def __init__(self, url="http://localhost:6333", collection="docs", dim=3072):
        # WE ARE CREATING AN OBEJECT OF QDRANT CLIENT THAT WILL INHERIT ALL THE FUNCTION OF QDRANTCLIENT 
        self.client=QdrantClient(url=url)
        # WE ARE CREATING OBJECTS OF VARIOUS COLLECTIONS
        self.collection=collection 

        # IF COLLECTION DOESTN EXISTS WE CREATE ONE
        if not self.client.collection_exists(self.collection):
            # THE CREATE COLLECTION TAKES IN 2 PARAMETER COLLECTION NAME AND VECTOR CONFIGS 
            self.client.create_collection(
                # THE COLLECTION NAME WILL BE NAMED AFTER THE COLLECTION INSTANCE 
                collection_name=self.collection
                vectors_config=VectorParams(size=dim, Distance=Distance.COSINE)
            )
        
    def update_and_insert(self, ids,vectors, payloads tfy)
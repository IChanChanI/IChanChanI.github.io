from pymongo import MongoClient
from bson.objectid import ObjectId

class AnimalShelter(object):
    """ CRUD operations for Animal collection in MongoDB """

    def __init__(self, user, pwd):
        self.client = MongoClient('mongodb://localhost:27017/aac') 
        # Change to personal MongoID
        self.database = self.client['aac']
        self.collection = self.database['animals']

#C
    def create(self, data):
        if data is not None:
                self.collection.insert_many(data) 
        else:
            raise Exception ("This is empty. Noting to save.")
        
#R
    def read(self, data):
        # Checks to see if the data is null or empty and returns exception in either case
        if data is not None:
                return self.collection.find(data, {"_id":False})
        else:
            raise Exception("This is empty. Noting to search.")
            
#U
    def update(self, data):
        if data is not None:
            return self.collection.update_many(data)
        else:
            raise Exception("This is empty. Noting to update.")
            
#D
    def delete(self, data):
        if data is not None:
            return self.collection.delete_many(data)
            
        else:
            raise Exception("This is empty. Nothing to delete.")

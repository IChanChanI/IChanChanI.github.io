from pymongo import MongoClient
from bson.objectid import ObjectId
from pprint import pprint

print('Hi there! Welcome to the Austin animal application.')

class AnimalShelter(object):
    ##CRUD implemtation
    
    def __init__(self, USER, PASS):
        #USER ='aacuser'
        #PASS ='SNHU1234'
        HOST = 'nv-desktop-services.apporto.com'
        PORT = 31163
        DB = 'AAC'
        COL = 'animals'
        
        self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT))
        self.database = self.client['%s' % (DB)]
        self.collection = self.database['%s' % (COL)]
        print ("Connection Successful")
        
    def create(self, data):
        if data is not None:
            result = self.collection.insert_one(data)
            return True if result.acknowledged else False
        else:
            raise Exception("There is nothing to save, data is empty")
            
            # R 
    def read(self, query):
        if query is not None:
            cursor = self.collection.find(query)
            return list(cursor)
        else:
            raise Exception("There is nothing to read, data is empty")
            
            #U
    def update(self, query, new_data):
        if query is not None and new_data is not None:
            update_result = self.collection.update_many(query, {'$set': new_data})
            return update_result.modified_count
        else:
            raise Exception("There is nothing to update because query data is empty")
            
            #D
    def delete(self, query):
        if query is not None:
            delete_result = self.collection.delete_many(query)
            return delete_result.deleted_count
        else:
            raise Exception("There is nothing to delete because data is empty")
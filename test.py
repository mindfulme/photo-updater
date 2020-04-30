import requests
import pymongo

mongo_token = "mongodb+srv://avo:q464602@citvylun-fksaq.mongodb.net/test?retryWrites=true&w=majority"
base_data = "olx2"
name_coll = "products"

client = pymongo.MongoClient(mongo_token)
data_base = client[base_data]
collection = data_base[name_coll]
i = 0
for data in collection.find({}):
    images = data['images']
    i += 1
    if images[0] is not None and "lh3.googleusercontent.com" in images[0]:
    #if images is None or images[0] is None:
        #collection.delete_one({'redirect_link': data['redirect_link']})
        for img in images:
            res = requests.get(img)
            if not res.ok:
                print(img)
                print("[{}]".format(i), data['name'])
            else:
                print("403 forbidden or image not found")
        print("[{}]".format(i), data['_id'])

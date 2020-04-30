import pickle
import requests
from quickstart import build_server
from config import mongo_token, base_data, name_coll
import grabber
import pymongo
import json
import os


def upload_on_server(image_urls):
    service = build_server()
    REST_API = "https://photoslibrary.googleapis.com/v1/uploads"

    cloud_ids = list()
    items = list()

    with open("token.pickle", "rb") as p:
        token = pickle.load(p)

    status = "Making data for upload"
    t_width = os.get_terminal_size().columns
    for i in range(len(image_urls)):
        url = image_urls[i].replace("/4000/4000/", "/1500/1500/")
        percent = "%.2f" % float(((i+1) / len(image_urls))*100) + "%"
        fileName = url.split("/")[-1]
        binaryBody = requests.get(url).content
        if binaryBody is bytes():
            return 1/0
        headers = {
            "Authorization": f"Bearer {token.token}",
            "Content-type": "application/octet-stream",
            "X-Goog-Upload-Content-Type": "image/jpeg",
            "X-Goog-Upload-Protocol": "raw",
            "X-Goog-Upload-File-Name": fileName
        }
        response = requests.post(REST_API, data=binaryBody, headers=headers)
        uploadToken = response.content.decode("utf-8")
        if not uploadToken:
            return 1/0
        try:
            response.json()
            return 1/0
        except:
            pass
        description = fileName.split(".")[0]
        items.append({'description': description, 'simpleMediaItem': {'uploadToken': uploadToken}})
        end = "\n" if i == len(image_urls) - 1 else "\r"
        print(status.ljust(t_width)[:-len(percent)] + percent, end=end)

    request_body = {
        'newMediaItems': items
    }

    try:
        service.mediaItems().batchCreate(body=request_body).execute()
    except:
        return 1/0

    request_body = {
        'album': {'title': 'citvy-cloud'}
    }
    response = service.albums().create(body=request_body).execute()
    album_id = response['id']

    response = service.mediaItems().list().execute()
    cloud = response.get("mediaItems")

    for d in [item['description'] for item in items]:
        for img in cloud:
            if d == img['description']:
                cloud_ids.append(img['id'])
                break

    upload_response = service.albums().batchAddMediaItems(albumId=album_id, body={"mediaItemIds": cloud_ids}).execute()

    request_body = {
        'sharedAlbumOptions': {'isCollaborative': True, 'isCommentable': True}
    }
    response = service.albums().share(albumId=album_id, body=request_body).execute()

    response = service.sharedAlbums().list().execute()
    album = response.get("sharedAlbums")[0]
    shared_album_url = album['shareInfo']['shareableUrl']
    media_items_count = int(album['mediaItemsCount'])

    return grabber.get_redirects(shared_album_url, t_width, media_items_count)

def updating():
    with pymongo.MongoClient(mongo_token) as client:
        data_base = client[base_data]
        collection = data_base[name_coll]
        width = os.get_terminal_size().columns
        requests_count = 0
        try:
            for data in collection.find({}):
                images = data['images']
                try:
                    if images[0] is not None and "lh3.googleusercontent.com" not in images[0]: # need update
                        data['images'] = upload_on_server(images)
                        collection.update_one({'redirect_link': data['redirect_link']}, {"$set": data}, upsert=True)
                        print('[{}] Card has been updated'.format(data['_id']))
                        requests_count += 1
                except KeyboardInterrupt:
                    exit()
                except: # images links of current section has been changed and need delete this
                    collection.delete_one({'redirect_link': data['redirect_link']})
                    print('[{}] Card has been deleted'.format(data['_id']).ljust(width))
                if requests_count == 10:
                    break
        except KeyboardInterrupt:
            exit()
        except:
            pass

print("starting process of filtering and updating")

while True:
    updating()
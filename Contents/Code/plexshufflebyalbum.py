#!/usr/bin/env python

import sys
import os
import json
from pprint import pprint 
import random
try:
    # see if we're running in a plex plug-in
    HTTP
except:
    import requests
    HTTP = None

def http_comm(url, method, headers):
    if HTTP:
        r = HTTP.Request(url, headers=headers, cacheTime=0, method=method)
    else:
        if method == "GET":
            request_func = requests.get
        if method == "POST":
            request_func = requests.post
        if method == "DELETE":
            request_func = requests.delete
        r = request_func(url, headers=headers, allow_redirects=True)
    return r    
    
class PlexServer(object):
    def __init__(self, host='localhost',port=32400, token = ""):
        self.base_url = "http://{}:{}".format(host,port)
        self.token = token

    def query(self, path, method):
        url = self.base_url + path
        headers = dict()
        headers['Accept'] = 'application/json'
        headers['X-Plex-Client-Identifier'] = '77777777-abab-4bc3-86a6-809c4901fb87'
        headers['X-Plex-Token'] = self.token


        r = http_comm(url, method, headers)
        try:
            response = json.loads( r.content )
            return response
        except:
            return None
        
    def get(self, path):
        return self.query(path, "GET")

    def post(self, path):
        return self.query(path, "POST")

    def delete(self, path):
        return self.query(path, "DELETE")

    def getClients(self):
        path = "/clients"
        response = self.get(path)
        try:
            return response['_children']
        except:
            return []
        
    def getSections(self):
        path = "/library/sections"
        response = self.get(path)
        try:
            return response['_children']
        except:
            return []
        
    def getAlbums(self, section):
        path = "/library/sections/{}/albums".format(section)
        response = self.get(path)
        try:
            albums = response['_children']
            
            for a in albums:
                # massage the genres info:
                genre_list = []
                for c in a['_children']:
                    if c['_elementType'] == 'Genre':
                        genre_list.append(c['tag'])
                a['genres'] = genre_list
            return albums
        except:
            return []

    def getServerInfo(self):
        path = ""
        response = self.get(path)
        try:
            return response
        except:
            return {}

    def getPlaylists(self):
        path = "/playlists"
        response = self.get(path)
        try:
            return response['_children']
        except:
            return []

    # takes a dict item as returned from getPlaylists
    def deletePlaylist(self, playlist):
        playlist_key = playlist['key']
        path = playlist_key.replace("/items", "")
        return self.delete(path)        

    # takes a list of album dict items as returned from getAlbums
    def createPlaylistOfAlbums(self, title, album_list, guid):
        key_list = []
        for a in album_list:
            key_num = a['key'].replace("/children","").replace("/library/metadata/", "")
            key_list.append(key_num) 
            
        path = "/playlists"
        path += "?type=audio"
        path += "&title={}".format(title)
        path += "&smart=0"
        path += "&uri=library://{}/directory//library/metadata/".format(guid)
        path += ",".join(key_list)
        response = self.post(path)
        try:
            return response['_children'][0]
        except:
            return []        

    
    def createPlayQueueForPlaylist(self, playlist_id):
        path = "/playQueues"
        path += "?playlistID={}".format(playlist_id)
        path += "&shuffle=0&type=audio&includeChapters=1&includeRelated=1"    
        return self.post(path)
    

def get_music_sections(server_ip, server_port, token):
    server = PlexServer(server_ip, server_port, token)

    music_sections = []
    # Look for music sections
    sections = server.getSections()
    for s in sections:
        if s['type'] == 'artist':
            music_sections.append(s)
    return music_sections

    
def generate_playlist(server_ip, server_port, token, section, playlist_name, list_size):
    server = PlexServer(server_ip, server_port, token)
    max_num_of_random_albums = list_size
    
    section_key = section['key']
    section_uuid = section['uuid']

    # list all albums for section
    print "Getting full album list from music section..."
    all_albums = server.getAlbums(section_key)

    # TODO: filter out unwanted genres here...

    num_of_random_albums = min(max_num_of_random_albums, len(all_albums))
    
    # choose random set of albums
    print "Creating random list of {} albums".format(num_of_random_albums)
    random_album_list = []
    while len(random_album_list) < num_of_random_albums:
        idx = random.randrange(len(all_albums))
        a = all_albums[idx]
        if a not in random_album_list:
            print u"   {} - {}".format(a['title'], a['parentTitle'])    
            random_album_list.append(a)
 
    if not random_album_list:
        print "No albums in random list.  Done."
        return
    
    # Delete old playlist with the same name, if it exists
    print "Getting list of existing playlists..."
    playlists = server.getPlaylists()

    for p in playlists:
        if p['title'] == playlist_name:
            print u"Deleting playlist: [{}]...".format(playlist_name)
            server.deletePlaylist(p)
            break
            
    # create new playlist with the selected albums
    print u"Creating playlist: [{}]".format(playlist_name)            
    playlist = server.createPlaylistOfAlbums(playlist_name, random_album_list, section_uuid)
    return playlist

def get_clients(server_ip, server_port, token):
    server = PlexServer(server_ip, server_port, token)
    return server.getClients()

def play_on_client(server_ip, server_port, token, client, playlist):
    server = PlexServer(server_ip, server_port, token)
     
    CLIENT_IP = client['address']
    CLIENT_PORT = client['port']
    MEDIA_ID = playlist['ratingKey']
    CLIENT_ID = client['machineIdentifier']
    SERVER_ID = server.getServerInfo()['machineIdentifier']

    # Make a playqueue for the playlist
    playqueue = server.createPlayQueueForPlaylist(MEDIA_ID)

    playqueue_selected_metadata_item_id = playqueue[u'playQueueSelectedMetadataItemID'] 
    playqueue_id = playqueue[u'playQueueID'] 

    # Tell the client to play the playlist
    url = "http://{}:{}/player/playback/playMedia".format(CLIENT_IP,CLIENT_PORT)
    url += "?key=%2Flibrary%2Fmetadata%2F{}".format(playqueue_selected_metadata_item_id)
    url += "&offset=0"
    #url += "&X-Plex-Client-Identifier={}".format(CLIENT_ID)
    url += "&machineIdentifier={}".format(SERVER_ID)
    url += "&address={}".format(server_ip)
    url += "&port={}".format(server_port)
    url += "&protocol=http"
    url += "&containerKey=%2FplayQueues%2F{}%3Fown%3D1%26window%3D200".format(playqueue_id)
    url += "&commandID=2"
    
    headers = dict()
    headers['X-Plex-Target-Client-Identifier'] = CLIENT_ID
    r = http_comm(url, "GET", headers=headers)
    print r.content    
    
def test():
    name = "ShuffleByAlbum"
    list_size = 15
    server_ip = "localhost"
    server_port = 32400
    token = "9494tdZFWpKRXsWV6Fjp"
 
    music_sections = get_music_sections(server_ip, server_port, token)
    
    if not music_sections:
        print "No music sections"
        return
    
    # choose the first section
    section = music_sections[0]
   
    playlist = generate_playlist(server_ip, server_port, token, section, name, list_size)
    clients = get_clients(server_ip, server_port, token)
    new_list = []
    for c in clients:
        if c['product'] != "Plex Web":
           new_list.append(c)
    clients = new_list

    if not clients:
        print "No clients"
        return
    
    # choose the first client
    client = clients[0]
    
    try:
        play_on_client(server_ip, server_port, token, client, playlist)
    except:
        print "Error talking to client"
#------------------------------------
if __name__ == "__main__":
    test()

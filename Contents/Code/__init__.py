from plexshufflebyalbum import *

ART = 'art-default.jpg'
ICON = 'icon-default.png'
ICON_PREFS = 'icon-prefs.png'
ICON_CLIENT = 'plex.png'

####################################################################################################
def Start():

    Plugin.AddPrefixHandler('/music/shufflebyalbum', MainMenu, 'Shuffle By Album', ICON, ART)
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    Plugin.AddViewGroup("Details", viewMode="InfoList", mediaType="items")    

    ObjectContainer.art = R(ART)
    ObjectContainer.title1 = 'Shuffle By Album'
    
    DirectoryObject.thumb = R(ICON)
     
    Dict['server_ip'] = 'localhost'
    Dict['server_port'] = os.environ['PLEXSERVERPORT']

    if 'PLEXTOKEN' in os.environ:
        Dict['plextoken'] = os.environ['PLEXTOKEN']
    else:
        Dict['plextoken'] = None

    Log("Plex Token: {}".format(Dict['token']))    

    HTTP.CacheTime = 0
        
####################################################################################################     
def MainMenu():

    Dict['music_sections'] = get_music_sections(Dict['server_ip'], Dict['server_port'], Dict['plextoken'])
    clients = get_clients(Dict['server_ip'], Dict['server_port'], Dict['plextoken'])

	# Plex web clients don't seem to work
    clients2 = []
    for c in clients:
        if c['product'] != "Plex Web":
            clients2.append(c)

	Dict['clients' ] = clients2
    
    if len(Dict['music_sections']) == 0:
        return ObjectContainer(header="ShuffleByAlbum",
                     message="No music sections to shuffle!")

    oc = ObjectContainer( view_group="Details")
    oc.add(DirectoryObject(key=Callback(GeneratePlaylist), title='New Playlist',
                           summary="Create a new playlist shuffled by album!"))
    oc.add(PrefsObject(title='Preferences', thumb=R(ICON_PREFS),
                        summary="Set plug-in preferences"))

    return oc
        
    
@route('/music/shufflebyalbum/generate')
def GeneratePlaylist():
        
    if len(Dict['music_sections']) > 1:
        return section_selection_menu()
    else:
        Dict['playlist'] = generate_playlist(Dict['server_ip'],
                                             Dict['server_port'],
                                             Dict['plextoken'],
                                             Dict['music_sections'][0],
                                             Prefs['playlist_name'],
                                             int(Prefs['album_count']))        
        return client_selection_menu()

    #return ObjectContainer(header="ShuffleByAlbum",
    #             message="Done!")

def section_selection_menu():
    oc = ObjectContainer(view_group="Details")
    oc.title1 = "Choose Music Library"
    for idx,section in enumerate(Dict['music_sections']):
        oc.add(DirectoryObject(key=Callback(SectionSelection, idx=idx),
                               title=section['title'],
                               summary="Create playlist from {} music library".format(section['title'])))
    return oc

def client_selection_menu():
    if len(Dict['clients']) == 0:
        return ObjectContainer(header="Shuffle By Album",
                     message="Found no viable clients to play on! Go to the playlists and play from there.")

    oc = ObjectContainer(view_group="Details")
    oc.title1 = "Play on Plex Client"

    for idx,client in enumerate(Dict['clients']):
        oc.add(DirectoryObject(key=Callback(ClientSelection, idx=idx),
                               title="Play on {}".format(client['name'],
                               thumb=R(ICON_CLIENT),
                               summary="Start playing new playlist on {}".format(client['name']))))
    return oc


@route('/music/shufflebyalbum/sectionselection')
def SectionSelection(idx):
    idx=int(idx)
    
    Dict['playlist'] = generate_playlist(Dict['server_ip'],
                                         Dict['server_port'],
                                         Dict['plextoken'],
                                         Dict['music_sections'][idx],
                                         Prefs['playlist_name'],
                                         int(Prefs['album_count']))        
    return client_selection_menu()

@route('/music/shufflebyalbum/clientselection')
def ClientSelection(idx):
    idx=int(idx)
    #TODO: figure out server IP??
    Log.Debug("ShuffleByAlbum: Going to play on client #{} {})".format(idx, Dict['clients'][idx]['address']))
    play_on_client(Dict['server_ip'],
                   Dict['server_port'],
                   Dict['plextoken'],
                   Dict['clients'][idx],
                   Dict['playlist'])

    return ObjectContainer()
    #return ObjectContainer(header="Shuffle By Album",
    #             message="Playing on {}".format(Dict['clients'][idx]['name']))


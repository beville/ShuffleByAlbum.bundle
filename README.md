

ShuffleByAlbum.bundle   <img src="https://raw.githubusercontent.com/beville/ShuffleByAlbum.bundle/master/Contents/Resources/icon-default.png" width="64">
==================

A Plex plugin to generate random playlists of albums in original order.

Generally, my prefered way to listen my music is play entire albums at once.  In particular, it's nice to have a random selection of music that preserves the album structure.  Unfortunately, a lot of current music library players are missing this feature (https://plex.tv/) or, inexplicably, have dropped it (I'm looking at you iTunes).  

This plugin attempts to provide a randomized album selection by generating long playlists on Plex.  It's a bit of a hack as it uses the REST API of Plex to control the server and the client that's controlling it.   

It's pretty easy to use:  just select the music library you want to shuffle (if there's more than one), and then if, you want, select the client you want to start the playlist on.

Enjoy!

Installation Instructions
-------------------------
1.  After unzipping, make sure the folder name is called "ShuffleByAlbum.bundle"
2.  Copy or move ShuffleByAlbum.bundle to your plugin directory
    * Mac: ~/Library/Application Support/Plex Media Server/Plug-ins
    * Windows: C:\Users\\[user]\AppData\Local\Plex Media Server\Plug-ins
    * Linux: /var/lib/plexmediaserver/Library/Application Support/Plex Media  Server/Plug-ins

![bg-art]

[bg-art]: https://github.com/beville/ShuffleByAlbum.bundle/blob/master/Contents/Resources/art-default.jpg?raw=true
[app-icon]: https://raw.githubusercontent.com/beville/ShuffleByAlbum.bundle/master/Contents/Resources/icon-default.png

import os
import mutagen
import re
import sys
import shutil
from mutagen.mp3 import MP3

music_dest = "/home/mark/ipodMusic/NewMusic/"
music_root = "/home/mark/ipodMusic/Music"
music_dirs = os.listdir(music_root)
music_files = []

artists = {}

tagDict = { "mp3" : { "album":'TALB',
                      "artist":'TPE1',
                      "song":'TIT2' },
            "m4a" : { "album":'\xa9alb',
                      "artist":'\xa9ART',
                      "song":'xa9nam' }
            }

def createDir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def createSym(src, dst):
    if not os.path.exists(dst):
        os.symlink(src, dst)       
        
class MusicFile:
    def __init__(self, audio):
        self.artist = self.getArtist(audio)
        self.album = self.getAlbum(audio)
        self.song = self.getSong(audio)
    def getAlbum(self):
        raise NotImplementedError("Override this")
    def getArtist(self):
        raise NotImplementedError("Override this")
    def getSong(self):
        raise NotImplementedError("Override this")

class myMP3(MusicFile):
    def getAlbum(self, audio):
        if 'TALB' in audio.tags.keys():
            thisAlbum = audio.tags['TALB'].text[0]
            return thisAlbum
        else:
            return None
    def getArtist(self, audio):
        if 'TPE1' in audio.tags.keys():
            thisArtist = audio.tags['TPE1'].text[0]
            return thisArtist
        else:
            return None
    def getSong(self, audio):
        if 'TIT2' in audio.tags.keys():
            thisSong = audio.tags['TIT2'].text[0]
            return thisSong
        else:
            return None

class myM4A(MusicFile):
    def getAlbum(self, audio):
        if '\xa9alb' in audio.tags.keys():
            thisAlbum = audio.tags['\xa9alb'][0]
            return thisAlbum
        else:
            return None
    def getArtist(self, audio):
        if '\xa9ART' in audio.tags.keys():
            thisArtist = audio.tags['\xa9ART'][0]
            return thisArtist
        else:
            return None
    def getSong(self, audio):
        if '\xa9nam' in audio.tags.keys():
            thisSong = audio.tags['\xa9nam'][0]
            return thisSong
        else:
            return None

def parseAudio(mf):

    match = re.search('.*mp3', mf, re.IGNORECASE)
    if match is not None:
        audio = MP3("/".join([music_root,directory,mf]))
        if audio != {}:
            myaudio = myMP3(audio) # parse the mp3 file
            artist = myaudio.artist
            album = myaudio.album
            song = myaudio.song
            return artist,album,song,".mp3"
                
    match = re.search('.*m4a', mf, re.IGNORECASE)
    if match is not None:
        audio = mutagen.File("/".join([music_root,directory,mf]))
        if audio != {}:
            myaudio = myM4A(audio) # parse the m4a file
            artist = myaudio.artist
            album = myaudio.album
            song = myaudio.song
            return artist,album,song,".m4a"

    return None,None,None,None

for directory in music_dirs:
    new_music_files = os.listdir(music_root + "/" + directory)
    music_files += new_music_files
    for mf in new_music_files:

        artist,album,song,ext = parseAudio(mf)
        
        if artist is not None:
            if artist in artists:
                pass
            else:
                artists[artist] = {}
            if album is not None:
                if album in artists[artist]:
                    pass
                else:
                    artists[artist][album] = [] # new list of songs
                if song is not None:
                    
                                        
                    artists[artist][album].append(song)

                    song = song.replace('/','_') # no slashes!
                    artist = artist.replace('/','_') # no slashes!
                    album = album.replace('/','_') # no slashes!

                    
                    newAlbumDir = music_dest + "Albums/" + album + "/"
                    oldAlbumDir = music_root + "/" + directory + "/"
                    createDir(newAlbumDir)
                    shutil.copyfile(oldAlbumDir + mf, newAlbumDir + song + ext)

                    newArtistDir = music_dest + "Artists/" + artist + "/"
                    createDir(newArtistDir)
                    createSym(newAlbumDir, newArtistDir + album) # symlink to album from artist

                    newSongDir = music_dest + "Songs/"
                    createDir(newSongDir)
                    createSym(newAlbumDir + song + ext, newSongDir + song + ext)
                    print(": ".join([artist, album, song]))


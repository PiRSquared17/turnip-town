#!/usr/bin/env python
import httplib
import StringIO
import hashlib
import uuid
import random
import string
import sys
import os
import subprocess
import gzip
import threading
if sys.version_info[1] >= 6:  import json
else: import simplejson as json


class MeatSlicer():
    def __init__(self):
        self.useragent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.56 Safari/536.5"
        self.token = None
        
        self.URL = "grooveshark.com" #The base URL of Grooveshark
        self.htmlclient = ('htmlshark', '20120312', 'reallyHotSauce', {"User-Agent":self.useragent, "Content-Type":"application/json", "Accept-Encoding":"gzip"}) #Contains all the information posted with the htmlshark client
        self.jsqueue = ['jsqueue', '20120312.08', 'circlesAndSquares']
        self.jsqueue.append({"User-Agent":self.useragent, "Referer": 'http://%s/JSQueue.swf?%s' % (self.URL, self.jsqueue[1]), "Accept-Encoding":"gzip", "Content-Type":"application/json"}) #Contains all the information specific to jsqueue
        
        #Setting the static header (country, session and uuid)
        self.h = {}
        self.h["country"] = {}
        self.h["country"]["CC1"] = 72057594037927940
        self.h["country"]["CC2"] = 0
        self.h["country"]["CC3"] = 0
        self.h["country"]["CC4"] = 0
        self.h["country"]["ID"] = 57
        self.h["country"]["IPR"] = 0
        self.h["privacy"] = 0
        self.h["session"] = (''.join(random.choice(string.digits + string.letters[:6]) for x in range(32))).lower()
        self.h["uuid"] = str.upper(str(uuid.uuid4()))
        
        #The string that is shown when the program loads
        entrystring = \
        """A Grooveshark song downloader in python
        by George Stephanos <gaf.stephanos@gmail.com>
        """
        
    #Generate a token from the method and the secret string (which changes once in a while)
    def prepToken(self, method, secret):
        rnd = (''.join(random.choice(string.hexdigits) for x in range(6))).lower()
        return rnd + hashlib.sha1('%s:%s:%s:%s' % (method, self.token, secret, rnd)).hexdigest()
    
    #Fetch a queueID (right now we randomly generate it)
    def getQueueID(self):
        return random.randint(10000000000000000000000,99999999999999999999999) #For now this will do
    
    #Get the static token issued by sharkAttack!
    def getToken(self):
        #global h, _token
        p = {}
        p["parameters"] = {}
        p["parameters"]["secretKey"] = hashlib.md5(self.h["session"]).hexdigest()
        p["method"] = "getCommunicationToken"
        p["header"] = self.h
        p["header"]["client"] = self.htmlclient[0]
        p["header"]["clientRevision"] = self.htmlclient[1]
        conn = httplib.HTTPSConnection(self.URL)
        conn.request("POST", "/more.php", json.JSONEncoder().encode(p), self.htmlclient[3])
        self.token = json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]
        return self.token
    
    #Process a search and return the result as a list.
    def getResultsFromSearch(self, query, what="Songs"):
        p = {}
        p["parameters"] = {}
        p["parameters"]["type"] = what
        p["parameters"]["query"] = query
        p["header"] = self.h
        p["header"]["client"] = self.htmlclient[0]
        p["header"]["clientRevision"] = self.htmlclient[1]
        p["header"]["token"] = self.prepToken("getResultsFromSearch", self.htmlclient[2])
        p["method"] = "getResultsFromSearch"
        conn = httplib.HTTPConnection(self.URL)
        conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), self.htmlclient[3])
        j = json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())
        try:
            return j["result"]["result"]["Songs"]
        except:
            return j["result"]["result"]
    
    #Get all songs by a certain artist
    def artistGetSongsEx(id, isVerified):
        p = {}
        p["parameters"] = {}
        p["parameters"]["artistID"] = id
        p["parameters"]["isVerifiedOrPopular"] = isVerified
        p["header"] = h
        p["header"]["client"] = htmlclient[0]
        p["header"]["clientRevision"] = htmlclient[1]
        p["header"]["token"] = prepToken("artistGetSongsEx", htmlclient[2])
        p["method"] = "artistGetSongsEx"
        conn = httplib.HTTPConnection(URL)
        conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), htmlclient[3])
        return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())
    
    #Get the streamKey used to download the songs off of the servers.
    def getStreamKeyFromSongIDs(self, id):
        p = {}
        p["parameters"] = {}
        p["parameters"]["type"] = 8
        p["parameters"]["mobile"] = False
        p["parameters"]["prefetch"] = False
        p["parameters"]["songIDs"] = [id]
        p["parameters"]["country"] = self.h["country"]
        p["header"] = self.h
        p["header"]["client"] = self.jsqueue[0]
        p["header"]["clientRevision"] = self.jsqueue[1]
        p["header"]["token"] = self.prepToken("getStreamKeysFromSongIDs", self.jsqueue[2])
        p["method"] = "getStreamKeysFromSongIDs"
        conn = httplib.HTTPConnection(self.URL)
        conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), self.jsqueue[3])
        return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]
    
    #Add a song to the browser queue, used to imitate a browser
    def addSongsToQueue(self, songID, artistID, songQueueID, source = "user"):    
        queueObj = {}
        queueObj["songID"] = songID
        queueObj["artistID"] = artistID
        queueObj["source"] = source
        queueObj["songQueueSongID"] = 1
        p = {}
        p["parameters"] = {}
        p["parameters"]["songIDsArtistIDs"] = [queueObj]
        p["parameters"]["songQueueID"] = songQueueID
        p["header"] = self.h
        p["header"]["client"] = self.jsqueue[0]
        p["header"]["clientRevision"] = self.jsqueue[1]
        p["header"]["token"] = self.prepToken("addSongsToQueue", self.jsqueue[2])
        p["method"] = "addSongsToQueue"
        conn = httplib.HTTPConnection(self.URL)
        conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), self.jsqueue[3])
        return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]
    
    #Remove a song from the browser queue, used to imitate a browser, in conjunction with the one above.
    def removeSongsFromQueue(songQueueID, userRemoved = True):
        p = {}
        p["parameters"] = {}
        p["parameters"]["songQueueID"] = songQueueID
        p["parameters"]["userRemoved"] = True
        p["parameters"]["songQueueSongIDs"]=[1]
        p["header"] = h
        p["header"]["client"] = jsqueue[0]
        p["header"]["clientRevision"] = jsqueue[1]
        p["header"]["token"] = prepToken("removeSongsFromQueue", jsqueue[2])
        p["method"] = "removeSongsFromQueue"
        conn = httplib.HTTPConnection(URL)
        conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), jsqueue[3])
        return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]
    
    #Mark the song as being played more then 30 seconds, used if the download of a songs takes a long time.
    def markStreamKeyOver30Seconds(songID, songQueueID, streamServer, streamKey):
        p = {}
        p["parameters"] = {}
        p["parameters"]["songQueueID"] = songQueueID
        p["parameters"]["streamServerID"] = streamServer
        p["parameters"]["songID"] = songID
        p["parameters"]["streamKey"] = streamKey
        p["parameters"]["songQueueSongID"] = 1
        p["header"] = h
        p["header"]["client"] = jsqueue[0]
        p["header"]["clientRevision"] = jsqueue[1]
        p["header"]["token"] = prepToken("markStreamKeyOver30Seconds", jsqueue[2])
        p["method"] = "markStreamKeyOver30Seconds"
        conn = httplib.HTTPConnection(URL)
        conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), jsqueue[3])
        return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]
    
    #Mark the song as downloaded, hopefully stopping us from getting banned.
    def markSongDownloadedEx(self, streamServer, songID, streamKey):
        p = {}
        p["parameters"] = {}
        p["parameters"]["streamServerID"] = streamServer
        p["parameters"]["songID"] = songID
        p["parameters"]["streamKey"] = streamKey
        p["header"] = self.h
        p["header"]["client"] = self.jsqueue[0]
        p["header"]["clientRevision"] = self.jsqueue[1]
        p["header"]["token"] = self.prepToken("markSongDownloadedEx", self.jsqueue[2])
        p["method"] = "markSongDownloadedEx"
        conn = httplib.HTTPConnection(self.URL)
        conn.request("POST", "/more.php?" + p["method"], json.JSONEncoder().encode(p), self.jsqueue[3])
        return json.JSONDecoder().decode(gzip.GzipFile(fileobj=(StringIO.StringIO(conn.getresponse().read()))).read())["result"]

if __name__ == "__main__":
    #if len(sys.argv) < 2: #Check if we were passed any parameters
    #    import gui
    #    gui.main() #Open the gui
    #    exit() #Close the command line
    print entrystring #Print the welcome message
    print "Initializing..."
    getToken() #Get a static token
    i = ' '.join(sys.argv[1:]) #Get the search parameter
    #i = raw_input("Search: ") #Same as above, if you uncomment this, and comment the first 4 lines this can be run entirely from the command line.
    print "Searching for '%s'..." % i
    m = 0
    s = getResultsFromSearch(i) #Get the result from the search
    l = [('%s: "%s" by "%s" (%s)' % (str(m+1), l["SongName"], l["ArtistName"], l["AlbumName"])) for m,l in enumerate(s[:10])] #Iterate over the 10 first returned items, and produce descriptive strings.
    if l == []: #If the result was empty print a message and exit
        print "No results found"
        exit()
    else:
        print '\n'.join(l) #Print the results
    songid = raw_input("Enter the Song ID you wish to download or (q) to exit: ")
    if songid == "" or songid == "q": exit() #Exit if choice is empty or q
    songid = eval(songid)-1 #Turn it into an int and subtract one to fit it into the list index
    queueID = getQueueID()
    addSongsToQueue(s[songid], queueID) #Add the song to the queue
    print "Retrieving stream key.."
    stream = getStreamKeyFromSongIDs(s[songid]["SongID"]) #Get the StreamKey for the selected song
    for k,v in stream.iteritems():
		stream=v
    if stream == []:
        print "Failed"
        exit()
    cmd = 'wget --post-data=streamKey=%s -O "%s - %s.mp3" "http://%s/stream.php"' % (stream["streamKey"], s[songid]["ArtistName"], s[songid]["SongName"], stream["ip"]) #Run wget to download the song    
    print cmd
    #cmd = 'wget --post-data=streamKey=%s -O "%s - %s.mp3" "http://%s/stream.php"' % (stream["streamKey"], s[songid]["ArtistName"], s[songid]["SongName"], stream["ip"]) #Run wget to download the song
    #p = subprocess.Popen(cmd, shell=True)
    markTimer = threading.Timer(30 + random.randint(0,5), markStreamKeyOver30Seconds, [s[songid]["SongID"], str(queueID), stream["ip"], stream["streamKey"]]) #Starts a timer that reports the song as being played for over 30-35 seconds. May not be needed.
    markTimer.start()
    #try:
    #    p.wait() #Wait for wget to finish
    #except KeyboardInterrupt: #If we are interrupted by the user
    #    os.remove('%s - %s.mp3' % (s[songid]["ArtistName"], s[songid]["SongName"])) #Delete the song
    #    print "\nDownload cancelled. File deleted."
    markTimer.cancel()
    print "Marking song as completed"
    markSongDownloadedEx(stream["ip"], s[songid]["SongID"], stream["streamKey"]) #This is the important part, hopefully this will stop grooveshark from banning us.
    #Natural Exit

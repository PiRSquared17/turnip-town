#!/usr/bin/env python
"""
GrooveWalrus: Tinysong
Copyright (C) 2009
11y3y3y3y43@gmail.com
http://groove-walrus.turnip-town.net
-----
This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 2 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc., 59 Temple
Place, Suite 330, Boston, MA 02111-1307 USA
"""

import urllib
#import xml.etree.ElementTree as ET

#Example
#    http://tinysong.com/s/Beethoven?limit=3
#Returns
#    http://tinysong.com/DjY; 564004; Fur Elise; 1833; Beethoven; 268605; The Best Of Beethoven; http://listen.grooveshark.com/song/Fur_Elise/564004
#    http://tinysong.com/N7c; 716886; Moonlight Sonata; 1833; Beethoven; 168699; Ludwig Van Beethoven; http://listen.grooveshark.com/song/Moonlight_Sonata/716886
#    http://tinysong.com/29V; 564008; Moonlight; 1833; Beethoven; 268605; The Best Of Beethoven; http://listen.grooveshark.com/song/Moonlight/564008 


# http://tinysong.com/s/Beethoven?limit=3
# http://www.tinysong.com/index.php?s=u2+lemon

TRACK_GETINFO = "http://tinysong.com/s/"
Q_LIMIT = "?limit="


    
# ===================================================================
class Tsong(object):
    def __init__(self):
    	pass
    	#self.last_similar_file_name = ''    	
        #self.last_country_name = ''

    def get_search_results(self, query_string, limit=16):
        # http://ws.audioscrobbler.com/2.0/?method=track.getinfo&api_key=b25b959554ed76058ac220b7b2e0a026&artist=cher&track=believe
        # get an image for track requested
        # <lfm <album <image
        results_array = []
        # replace "of" "and" "a" "the"
        small_words_array = [" the ", " The ", "The ", "the ", " Of ", " And ", " A ", " Are ", " are ", " I ", " if ", " If ", " of ", " and ", " a ", "A ", " is ", " Is ", " to ", " To ", "I'm ", " i'm ", " I'm ", "I'd ", " i'd ", " I'd "]        
        #query_string = query_string.lower()
        for x in small_words_array:
            query_string = query_string.replace(x, ' ')
        query_string = url_quote(query_string)
        #print query_string
        data_url = TRACK_GETINFO + query_string + Q_LIMIT + str(limit)
        #print data_url

        url_connection = urllib.urlopen(data_url.replace(' ', '+'))
        raw_results = url_connection.read()
        
        results_array = raw_results.split('\n')

        #print results_array
        #print len(results_array)

        return results_array
        

charset = 'utf-8'
        
def url_quote(s, safe='/', want_unicode=False):
    """
    Wrapper around urllib.quote doing the encoding/decoding as usually wanted:
    
    @param s: the string to quote (can be str or unicode, if it is unicode,
              config.charset is used to encode it before calling urllib)
    @param safe: just passed through to urllib
    @param want_unicode: for the less usual case that you want to get back
                         unicode and not str, set this to True
                         Default is False.
    """
    if isinstance(s, unicode):
        s = s.encode(charset)
    elif not isinstance(s, str):
        s = str(s)
    s = urllib.quote(s, safe)
    if want_unicode:
        s = s.decode(charset) # ascii would also work
    return s
     
# ===================================================================            

 

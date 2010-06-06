"""
GrooveWalrus: sync Plug-in 
Copyright (C) 2010
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
#import urllib2

import wx
import wx.xrc as xrc
import os #, sys
import shutil
import hashlib
#import re

from main_utils.read_write_xml import xml_utils
from main_utils import system_files
from main_utils import local_songs
from main_utils import file_cache

#SYSLOC = os.getcwd()
#TWITTER_SETTINGS = os.path.join(os.getcwd(), 'plugins','sync') + os.sep + "settings_sync.xml"
sync = os.path.join(os.getcwd(), 'plugins','sync') + os.sep
RESFILE = os.path.join(os.getcwd(), 'plugins','sync') + os.sep + "layout_sync.xml"


class MainPanel(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Sync", size=(375,460), style=wx.FRAME_SHAPED) #STAY_ON_TOP)        
        self.parent = parent
        
        self.SYNC_SETTINGS = system_files.GetDirectories(self).MakeDataDirectory('plugins') + os.sep
        
        
        # XML Resources can be loaded from a file like this:
        res = xrc.XmlResource(RESFILE)

        # Now create a panel from the resource data
        panel = res.LoadPanel(self, "m_pa_plugin_sync")

        # control references --------------------
        self.st_sync_device = xrc.XRCCTRL(self, 'm_st_sync_device')
        self.st_sync_space = xrc.XRCCTRL(self, 'm_st_sync_space')
        self.st_sync_file = xrc.XRCCTRL(self, 'm_st_sync_file')
        #header for dragging and moving
        self.st_sync_header = xrc.XRCCTRL(self, 'm_st_sync_header')
        self.bm_sync_close = xrc.XRCCTRL(self, 'm_bm_sync_close')
        self.lb_sync_directories = xrc.XRCCTRL(self, 'm_lb_sync_directories')

        # bindings ----------------
        #self.Bind(wx.EVT_BUTTON, self.SaveOptions, id=xrc.XRCID('m_bu_sync_save'))
        #self.Bind(wx.EVT_BUTTON, self.Twat, id=xrc.XRCID('m_bu_sync_tweet'))
        
        #self.Bind(wx.EVT_BUTTON, self.Getsync, id=xrc.XRCID('m_bu_sync_update'))
        #self.Bind(wx.EVT_BUTTON, self.GetMentions, id=xrc.XRCID('m_bu_sync_update_at'))
        #self.Bind(wx.EVT_BUTTON, self.CopyReplace, id=xrc.XRCID('m_bu_sync_update_default'))
        self.Bind(wx.EVT_BUTTON, self.OnAddClick, id=xrc.XRCID('m_bu_sync_add'))
        self.Bind(wx.EVT_BUTTON, self.OnRemoveClick, id=xrc.XRCID('m_bu_sync_remove'))
        self.Bind(wx.EVT_BUTTON, self.OnSyncClick, id=xrc.XRCID('m_bu_sync_sync'))
        
        self.Bind(wx.EVT_LISTBOX, self.EvtListBox, self.lb_sync_directories)
        
        self.bm_sync_close.Bind(wx.EVT_LEFT_UP, self.CloseMe)
        
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.st_sync_header.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.st_sync_header.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.st_sync_header.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.st_sync_header.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)       

            
        #self.bu_update_restart.Enable(False)    
        # set layout --------------
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND|wx.ALL, 5)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        
        self.LoadSettings()
        #self.CopyReplace()
        #self.OnChars()
        #xrc.XRCCTRL(self, 'm_notebook1').SetPageText(1, '@' + self.tc_sync_username.GetValue())
            
    def OnAddClick(self, event):
        # In this case we include a "New directory" button. 
        dlg = wx.DirDialog(self, "Choose a directory:",
                          style=wx.DD_DEFAULT_STYLE
                           #| wx.DD_DIR_MUST_EXIST
                           #| wx.DD_CHANGE_DIR
                           )
        if dlg.ShowModal() == wx.ID_OK:
            print dlg.GetPath()
            self.lb_sync_directories.Insert(dlg.GetPath(), 0)
            self.SaveOptions()
        dlg.Destroy()
        
    def OnRemoveClick(self, event):
        # check for selected folder and remove
        list_item = self.lb_sync_directories.GetSelection()
        if list_item >= 0:
            folder_name = self.lb_sync_directories.GetString(list_item)
            if len(folder_name) > 1:
                self.SaveOptions()                
        
    def ErrorMessage(self, message):
            dlg = wx.MessageDialog(self, message, 'Alert', wx.OK | wx.ICON_WARNING)
            if (dlg.ShowModal() == wx.ID_OK):
                dlg.Destroy()
            
    def CloseMe(self, event=None):
        self.Destroy()
        
    def LoadSettings(self):
        #load the setting from settings_sync.xml if it exists
        settings_dict = xml_utils().get_generic_settings(self.SYNC_SETTINGS + "settings_sync.xml")
        print settings_dict
        if len(settings_dict) >= 1:
            directories=''
            if settings_dict.has_key('directories'):
                directories = settings_dict['directories']
                h = directories.split(';')
                counter = 0
                for x in h:
                    if len(x) > 0:
                        self.lb_sync_directories.Insert(x, counter)
                        counter = counter + 1
                
    def SaveOptions(self):
        # save value to options.xml
        dir_string = ''
        num_items = len(self.lb_sync_directories.GetItems())
        if num_items > 0:
            for x in range(num_items, 0, -1):                
                dir_string = dir_string + self.lb_sync_directories.GetString(x-1) + ';'

        if len(dir_string) > 1:
            window_dict = {}
            window_dict['directories'] = dir_string
            xml_utils().save_generic_settings(self.SYNC_SETTINGS, "settings_sync.xml", window_dict)
            
         
    def EvtListBox(self, event):
        #set disk free space label for selected device
        self.st_sync_space.SetLabel(self.GetDeviceFreeSpace(event.GetString()))
               
    def OnSyncClick(self, event):
        #try and copy files from playlist to device
        #check if dir is selected
        sync_dir = self.lb_sync_directories.GetStringSelection()
        if sync_dir != '':
            #check if dir exists
            if os.path.isdir(sync_dir):
                #get playlist
                for x in range(0, self.parent.lc_playlist.GetItemCount()):
                    artist = self.parent.lc_playlist.GetItem(x, 0).GetText()
                    track = self.parent.lc_playlist.GetItem(x, 1).GetText()                    
                    query_string = artist + ' ' + track
                    #check for file locally
                    local_file = self.SearchLocal(query_string, artist, track)
                    copy_file = None
                    if local_file != None:
                        copy_file = local_file
                    else:
                        #check for cached file
                        copy_file = self.SearchCache(artist, track)
                        
                    if copy_file != None:                        
                        #copy the file
                        file_name_plain = artist + '-' + track + '.mp3'
                        charset = 'utf-8'
                        ufile_string = file_name_plain.encode(charset)    
                        hex_file_name = hashlib.md5(ufile_string).hexdigest()
                        destination_file = sync_dir + os.sep + hex_file_name + '.mp3'
                        
                        if os.path.isfile(destination_file) == False:
                            try:
                                shutil.copy (copy_file, destination_file)
                                print destination_file
                            except e, error:
                                self.ErrorMessage(error) 
            else:
                self.ErrorMessage('Can\'t find ' + sync_dir + '.')
        else:
            self.ErrorMessage('Device not selected.')
        #cycle throught each file
        #check if file exists on device
        #check cache
        #check songdb
        #copy file
        #cancel
        
    def GetDeviceCapacity(self):
        #gets drive capacity
        pass
    
    def GetDeviceFreeSpace(self, path):
        #gets drive free space
        #print path
        x = os.popen("dir " + path).readlines()        
        return x[-1].strip()

        
        # linux
        #disk = os.statvfs("/")
        # Information is recieved in numbers of blocks free
        # so we need to multiply by the block size to get the space free in bytes
        #capacity = disk.f_bsize * disk.f_blocks
        #available = disk.f_bsize * disk.f_bavail
        #used = disk.f_bsize * (disk.f_blocks - disk.f_bavail) 
    
        
    def SearchLocal(self, query_string, artist, track):           
        # check locally for song
        #query_results = local_songs.GetResults(query_string, 1)
        query_results = local_songs.DbFuncs().GetSpecificResultArray(query_string, artist, track)
        #GetResultsArray(query, qlimit, with_count=False, folder_query=1)
        song_id = ''
        if len(query_results) >= 1:
            #song_id = str(query_results[0])
            song_id = str(query_results[0][4])                        
        #check if file exists
        if os.path.isfile(song_id):            
            return song_id
        else:
            return None
            
    def SearchCache(self, artist, track):
        temp_dir = system_files.GetDirectories(self).TempDirectory()
        file_name_plain = artist + '-' + track + '.mp3'
        
        # check if file previously cached
        cached_file = file_cache.CreateCachedFilename(temp_dir, file_name_plain)
        cached_file_name = cached_file[0]
        if cached_file[1] == True:
            return(cached_file_name)
        else:
            return(None)

        
# --------------------------------------------------------- 
# titlebar-like move and drag
    
    def OnMouseLeftDown(self, evt):
        self.Refresh()
        self.ldPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
        self.wPos = self.ClientToScreen((0,0))
        self.CaptureMouse()

    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            dPos = evt.GetEventObject().ClientToScreen(evt.GetPosition())
            #nPos = (self.wPos.x + (dPos.x - self.ldPos.x), -2)
            nPos = (self.wPos.x + (dPos.x - self.ldPos.x), self.wPos.y + (dPos.y - self.ldPos.y))
            self.Move(nPos)

    def OnMouseLeftUp(self, evt):
        try:
            self.ReleaseMouse()
        except wx._core.PyAssertionError:
            pass

    def OnRightUp(self, evt):
        self.hide_me()
        #self..Destroy()
        
# --------------------------------------------------------- 
            
           
# ===================================================================            

              
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
    #s = urllib.quote(s)#, safe)
    if want_unicode:
        s = s.decode(charset) # ascii would also work
    return s
     
# ===================================================================   
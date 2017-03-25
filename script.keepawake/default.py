# -*- coding: utf-8 -*-
'''
KeepAwake for Kodi/XBMC
Copyright (C) 2017 noam09
https://github.com/noam09

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import xbmc
import xbmcaddon
import xbmcgui
import os

import os
import sys
import requests
import simplejson as json

__addon__ = xbmcaddon.Addon()
__cwd__ = __addon__.getAddonInfo('path')
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__icon__ = __addon__.getAddonInfo('icon')
__ID__ = __addon__.getAddonInfo('id')
__language__ = __addon__.getLocalizedString

__profile__ = xbmc.translatePath(__addon__.getAddonInfo('profile'))
__resource__ = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib'))
__icons__ = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'media' ))

sys.path.append (__resource__)

# Set Icons
iconAddon = os.path.join(__icons__, 'toad.png')

API_URL = 'http://{}:{}/jsonrpc'

def log(msg):
    xbmc.log("### [%s] - %s" % (__scriptname__,msg,), level=xbmc.LOGDEBUG)

log("[%s] - Version: %s Started" % (__scriptname__, __version__))

def api(device, method, params=None):
    """ Call JSON-RPC API for specified device, using method and optional parameters """
    query = {"id": "1",
        "jsonrpc": "2.0",
        "method": method}
    if params:
        query['params'] = params
    r = requests.post(API_URL.format(device['host'], str(device['port'])),
        data=json.dumps(query), auth=requests.auth.HTTPBasicAuth(device['username'], device['password']))
    return json.loads(r.text)

def left_right(device):
    api(device, "Input.Left")
    r = api(device, "Input.Right")
    return r

def is_playing(device, playtype=None):
    """ Determine if device is playing something, optionally specify type of media """
    # Get Now Playing
    result = api(device, "Player.GetActivePlayers")['result']
    if len(result) == 0:
        log('Nothing playing')
        return False
    else:
        log('Something playing: {}'.format(result))
        log('No need to keep awake for now')
        if playtype:
            if lower(result[0]['type']) == playtype:
                return True
            else:
                return False
        else:
            return True

# Helper function to get string type from settings
def getSetting(setting):
    return __addon__.getSetting(setting).strip()

# Helper function to get bool type from settings
def getSettingAsBool(setting):
    return __addon__.getSetting(setting).lower() == "true"

#global g_wakeOnLan
g_wakeOnLan = getSettingAsBool("wakeOnLan")
#global g_macAddress
g_macAddress = __addon__.getSetting("macAddress")

def loadSettings():
    global g_interval
    global g_wakeOnLan
    global g_macAddress
    global g_parentHost
    global g_parentPort
    global g_parentUser
    global g_parentPass
    global g_mediaType

    global g_master

    g_interval = int(float(__addon__.getSetting("interval")))
    g_wakeOnLan = getSettingAsBool("wakeOnLan")
    g_macAddress = __addon__.getSetting("macAddress")
    g_parentHost = __addon__.getSetting("parentHost")
    g_parentPort = int(float(__addon__.getSetting("parentPort")))
    g_parentUser = __addon__.getSetting("parentUser")
    g_parentPass = __addon__.getSetting("parentPass")
    g_mediaType = int(float(__addon__.getSetting("mediaType")))

    log('Settings loaded!')
    log('interval \t%s' % g_interval)
    log('wakeOnLan \t%s' % g_wakeOnLan)
    log('macAddress \t%s' % g_macAddress)
    log('parentHost \t%s' % g_parentHost)
    log('parentPort \t%s' % g_parentPort)
    log('parentUser \t%s' % g_parentUser)
    log('parentPass \t%s' % g_parentPass)
    log('mediaType \t%s' % g_mediaType)

    g_master = {'host': g_parentHost,
        'port': g_parentPort,
        'username': g_parentUser,
        'password': g_parentPass}

class MyPlayer(xbmc.Player):
    def __init__(self, *args, **kwargs):
        xbmc.Player.__init__(self)
        log('MyPlayer - initiate')
        g_wakeOnLan = getSettingAsBool("wakeOnLan")
        g_macAddress = __addon__.getSetting("macAddress")

    def mediaTypeCheck(self):
        # Returns True if g_mediaType matches currently playing media type, otherwise returns False
        log('Enter mediaTypeCheck')
        if g_mediaType == 0 and self.isPlayingVideo() \
            or g_mediaType == 1 and self.isPlayingAudio() \
            or g_mediaType == 2:
            log('mediaTypeCheck return True')
            return True
        else:
            log('mediaTypeCheck return False')
            return False

    def waker(self):
        log('Enter waker')
        log('g_wakeOnLan %s' % g_wakeOnLan)
        if g_wakeOnLan:
            log('Issue Wake-On-Lan: %s' % g_macAddress)
            # Check MAC address format
            if len(g_macAddress) == 12:
                macAddress = ':'.join(g_macAddress[i:i+2] for i in range(0,12,2))
            elif len(g_macAddress) == 12 + 5:
                sep = g_macAddress[2]
                if sep == ':':
                    macAddress= g_macAddress
                else:
                    macAddress = g_macAddress.replace(sep, ':')
            else:
                log('Incorrect MAC address format: %s' % g_macAddress)
            xbmc.executebuiltin('XBMC.WakeOnLan("' + macAddress + '")')
            xbmc.sleep(5*1000)

    def onPlayBackStarted(self):
        # This gets triggered when a file starts playing
        log('Enter onPlayBackStarted')
        # May need a WOL here before playing?
        # Is onPlayBackStarted triggered even if the file isn't available? No.
        if self.mediaTypeCheck():
            self.waker()
        while 1:
            try:
                _filename = self.getPlayingFile()
                log('Locally playing filename: %s' % _filename)
            except:
                xbmc.sleep(1000)
            # TODO: In the future, this filename can be used to filter by specific sources
            if _filename:
                log('File playing locally, checking if parent is playing anything')
                if not is_playing(device=g_master):
                    if self.mediaTypeCheck():
                        ret = left_right(device=g_master)
                        log('Parent playing nothing, left_right returned %s' % ret)
                else:
                    log('Parent playing something, no need to keep awake')
            xbmc.sleep(g_interval*1000*60)

    def onPlayBackStopped(self):
       log('Enter onPlayBackStopped')
       # This could mean the file finished playing,
       # but could also mean the file was unreachable because parent is asleep
       # So now we wake it
       # If relying on parent for video only, and local is playing audio, waker shouldn't run
       # TODO: Detect failed plays, WOL, retry playing - maybe OnPlay announces filename
       if not self.mediaTypeCheck():
           self.waker()

    def onPlayBackEnded(self):
        log('Enter onPlayBackEnded')
        self.onPlayBackStopped() 

    def onPlayBackPaused(self):
        # Gets triggered when a file is paused, no need to keep awake here
        log('Enter onPlayBackPaused')
        while 1:
            try:
                _filename = self.getPlayingFile()
                log('Locally playing filename: %s' % _filename)
            except:
                xbmc.sleep(1000)
            xbmc.sleep(g_interval*1000*60)

    def onPlayBackResumed(self):
        # Gets triggered when a file is already playing, and then gets paused and resumed
        log('Enter onPlayBackResumed')
        # May need a WOL here before resuming
        self.waker()
        while 1:
            try:
                _filename = self.getPlayingFile()
                log('Locally playing filename: %s' % _filename)
            except:
                xbmc.sleep(1000)
            if _filename:
                log('File playing locally, checking if parent is playing anything')
                if not is_playing(device=g_master):
                    if self.mediaTypeCheck():
                        ret = left_right(device=g_master)
                        log('Parent playing nothing, left_right returned %s' % ret)
                else:
                    log('Parent playing something, no need to keep awake')
            xbmc.sleep(g_interval*1000*60)

try:
    class MyMonitor(xbmc.Monitor):
        def __init__(self, *args, **kwargs):
            xbmc.Monitor.__init__(self)
            log('MyMonitor - initiate')

        def onSettingsChanged(self):
            loadSettings()

    xbmc_monitor = MyMonitor()
except:
    log('Using Eden API - you need to restart addon for changing settings')

loadSettings()
player_monitor = MyPlayer()

while not xbmc.abortRequested:
    xbmc.sleep(1000)

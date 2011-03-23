#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.dom.minidom as minidom
import hashlib
import urllib
import re

class GmObject():

    def __init__(self):
        pass

    def parse_node(self, node):
        # append attributes from node
        for childNode in node.childNodes:
            name = childNode.tagName
            if childNode.hasChildNodes():
                value = childNode.childNodes[0].data
            else:
                value = ""
            setattr(self, name, value)
            
    def parse_dict(self, dict):
        # append attributes from dict
        for key in dict:
            setattr(self, key, unicode(dict[key]))
            
    @staticmethod
    def decode_html_text(text):
        html_escape_table = {
            "&nbsp;" : " ",
            "&quot;" : '"',
            "&ldquo;" : "“",
            "&rdquo;" : "”",
            "&mdash;" : "—",
            "&amp;" : "&",
            "&middot;" : "·"
        }
        for key, value in html_escape_table.items():
            text = text.replace(key, value)
        numbers = re.findall('&#([^;]+);', text)
        for number in numbers:
            text = text.replace("&#%s;" % number, unichr(int(number)))
        return text

class Song(GmObject):

    def __init__(self, id=None):
        if id is not None:
            self.id = id
            self.load_detail()

    def load_streaming(self):
        if not hasattr(self, "songUrl"):
            template = "http://www.google.cn/music/songstreaming?id=%s&cd&sig=%s&output=xml"
            flashplayer_key = "c51181b7f9bfce1ac742ed8b4a1ae4ed"
            sig = hashlib.md5(flashplayer_key + self.id).hexdigest()
            url = template % (self.id, sig)
            urlopener = urllib.urlopen(url)
            xml = urlopener.read()
            dom = minidom.parseString(xml)
            self.parse_node(dom.getElementsByTagName("songStreaming")[0])
        
    def load_detail(self):
        if not hasattr(self, "albumId"):
            template = "http://www.google.cn/music/song?id=%s&output=xml"
            url = template % self.id
            urlopener = urllib.urlopen(url)
            xml = urlopener.read()
            dom = minidom.parseString(xml)
            self.parse_node(dom.getElementsByTagName("song")[0])
            
    def load_download(self):
        if not hasattr(self, "downloadUrl") or self.downloadUrl == "":
            self.downloadUrl = Song.musicdownload(self.id)

    @staticmethod 
    def musicdownload(id):    
        template = "http://www.google.cn/music/top100/musicdownload?id=%s"
        url = template % id
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        matches = re.search('<a href="/(music/top100/url[^"]+)">', html)
        if matches is not None:
            return "http://www.google.cn/%s" % matches.group(1).replace("&amp;", "&")
        else:
            # to many request in the same time, ask for captcha
            return ""

class Songlist(GmObject):       

    def __init__(self):
        self.songs = []
        self.has_more = False

    def parse_xml(self, xml, song_tag="songList"):
        songs = []
        dom = minidom.parseString(xml)
        info_node = dom.getElementsByTagName("info")
        if len(info_node) > 0:
            self.parse_node(info_node[0])
        for childNode in dom.getElementsByTagName(song_tag)[0].childNodes:
            if (childNode.nodeType == childNode.ELEMENT_NODE):
                song = Song()
                song.parse_node(childNode)
                songs.append(song)
        return songs

    def parse_html(self, html):                       
        # find id      
        ids = []  
        matches = re.findall('<!--freemusic/song/result/([^-]+)-->', html)
        for match in matches:
            ids.append(match)
            
        # find name
        names = []
        matches = re.findall('<td class="Title BottomBorder">.+?>(.+?)</.+?></td>', html, re.DOTALL)
        for match in matches:   
            match = GmObject.decode_html_text(match)         
            names.append(match)

        # find artist
        artists = []
        matches = re.findall('<td class="Artist BottomBorder">(.+?)</td>', html, re.DOTALL)
        for match in matches:
            # some song may has one more aritsts
            match = re.findall('<.+?>(.+?)</.*>', match)
            match = " ".join(match)
            match = GmObject.decode_html_text(match)
            artists.append(match)
            
        # find album
        albums = []
        matches = re.findall('<td class="Album BottomBorder"><a .+?>《(.+?)》</a></td>', html, re.DOTALL)
        for match in matches:
            match = GmObject.decode_html_text(match)
            albums.append(match)
            
        # album maybe empty
        if len(albums) == 0:
            for i in range(len(ids)):
                albums.append("")
            
        # create song object, three list should have same len
        songs = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "artist":artists[i], "album":albums[i]}
            song = Song()
            song.parse_dict(dict)
            songs.append(song)
        return songs            

class Album(Songlist):
    
    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()
        
    def load_songs(self):
        template = "http://www.google.cn/music/album?id=%s&output=xml"
        url = template % self.id
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songs = self.parse_xml(xml)
        self.songs.extend(songs)
        return songs
            
class Search(Songlist):
    
    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()
        
    def load_songs(self, start=0, number=20):
        template = "http://www.google.cn/music/search?cat=song&q=%s&start=%d&num=%d&output=xml"
        url = template % (self.id, start, number + 1)
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songs = self.parse_xml(xml)
        if len(songs) == number + 1:
            self.has_more = True
            songs.pop()
        else:
            self.has_more = False
        self.songs.extend(songs)
        return songs
                    
class Chartlisting(Songlist):
    
    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()
        
    def load_songs(self, start=0, number=20):
        template = "http://www.google.cn/music/chartlisting?q=%s&cat=song&start=%d&num=%d&output=xml"
        url = template % (self.id, start, number + 1)
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songs = self.parse_xml(xml)
        if len(songs) == number + 1:
            self.has_more = True
            songs.pop()
        else:
            self.has_more = False
        self.songs.extend(songs)
        return songs

class Topiclisting(Songlist):
    
    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()
        
    def load_songs(self):
        template = "http://www.google.cn/music/topiclisting?q=%s&cat=song&output=xml"
        url = template % self.id
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songs = self.parse_xml(xml)
        self.songs.extend(songs)
        return songs
    
class ArtistSong(Songlist):
    
    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()
        
    def load_songs(self):
        template = "http://www.google.cn/music/artist?id=%s&output=xml"
        url = template % self.id
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songs = self.parse_xml(xml, "hotSongs")
        self.songs.extend(songs)
        return songs
            
class Tag(Songlist):
    
    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()
        
    def load_songs(self, start=0, number=20):
        template = "http://www.google.cn/music/tag?q=%s&cat=song&type=songs&start=%d&num=%d"
        url = template % (self.id, start, number + 1)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songs = self.parse_html(html)
        if len(songs) == number + 1:
            self.has_more = True
            songs.pop()
        else:
            self.has_more = False
        self.songs.extend(songs)
        return songs
            
class Screener(Songlist):
    
    def __init__(self, args_dict={}):
        Songlist.__init__(self)
        self.args_dict = args_dict
        self.load_songs()
        
    def load_songs(self, start=0, number=20):
        template = "http://www.google.cn/music/songscreen?start=%d&num=%d&client=&output=xml"
        url = template % (start, number + 1)
        request_args = []
        for key, value in self.args_dict.items():
            text = "&%s=%s" % (key, value)
            request_args.append(text)
        url = url + "".join(request_args)
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songs = self.parse_xml(xml)
        if len(songs) == number + 1:
            self.has_more = True
            songs.pop()
        else:
            self.has_more = False
        self.songs.extend(songs)
        return songs
            
class Similar(Songlist):
    
    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()
        
    def load_songs(self):
        template = "http://www.google.cn/music/song?id=%s"
        url = template % self.id
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songs = self.parse_html(html)
        self.songs.extend(songs)       
        return songs 
            
class Starrecc(Songlist):
    
    def __init__(self, id=None):
        Songlist.__init__(self)
        if id is not None:
            self.id = id
            self.load_songs()
            
    def html_handler(self, html):        
        # find id      
        ids = []  
        matches = re.findall('onclick="window.open([^"]+)"', html)
        for match in matches:
            match = re.search('download.html\?id=([^\\\]+)', urllib.unquote(match)).group(1)
            ids.append(match)
 
        # find name and artist
        names = []
        artists = []
        matches = re.findall('<td class="Title"><a .+?>《(.+?)》\n&nbsp;(.+?)</a></td>', html, re.DOTALL)
        for match in matches:
            name = GmObject.decode_html_text(match[0])
            artist = GmObject.decode_html_text(match[1])
            names.append(name)
            artists.append(artist)
            
        # create song object, three list should have same len
        songs = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "artist":artists[i]}
            song = Song()
            song.parse_dict(dict)
            songs.append(song)
        return songs  
        
    def load_songs(self):
        template = "http://www.google.cn/music/playlist/playlist?id=sys:star_recc:%s&type=star_recommendation"
        url = template % self.id
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songs = self.html_handler(html)
        self.songs.extend(songs)      
        return songs  
            
class Directory(GmObject):

    def __init__(self):
        self.songlists = []
        self.has_more = False

class DirSearch(Directory):
    
    def __init__(self, id):
        Directory.__init__(self)
        self.id = id
        self.load_songlists()
        
    def load_songlists(self, start=0, number=20):
        template = "http://www.google.cn/music/search?q=%s&cat=album&start=%d&num=%d"
        url = template % (self.id, start, number + 1)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songlists = self.parse_html(html)
        if len(songlists) == number + 1:
            self.has_more = True
            songlists.pop()
        else:
            self.has_more = False
        self.songlists.extend(songlists)
        return songlists
            
    def parse_html(self, html):                       
        # find id      
        ids = []  
        matches = re.findall('<!--freemusic/album/result/([^-]+)-->', html)
        for match in matches:
            ids.append(match)

        # find name
        names = []
        matches = re.findall('《(.+)》', html)
        for match in matches:
            match = match.replace("<b>", "")
            match = match.replace("</b>", "")
            match = GmObject.decode_html_text(match)
            names.append(match)
    
        # find artist
        artists = []
        matches = re.findall('<td class="Tracks" colspan="10" align="left">(.+?)</td>', html)
        for match in matches:
            match = match.replace("<b>", "")
            match = match.replace("</b>", "")
            match = match.split()[0]
            match = GmObject.decode_html_text(match)
            artists.append(match)
            
        # find thumbnail
        thumbnails = []
        matches = re.findall('<img [^/]+ class="thumb-img" [^/]+ src="([^"]+)"', html)
        for match in matches:
            thumbnails.append(match)

        # create song object, three list should have same len
        songlists = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "artist":artists[i], "thumbnailLink":thumbnails[i]}
            album = Album()
            album.parse_dict(dict)
            songlists.append(album)
        return songlists
         
class DirChartlisting(Directory):
    
    def __init__(self, id):
        Directory.__init__(self)
        self.id = id
        self.load_songlists()
            
    def load_songlists(self, start=0, number=20):
        template = "http://www.google.cn/music/chartlisting?q=%s&cat=album&start=%d&num=%d&output=xml"
        url = template % (self.id, start, number + 1)
        urlopener = urllib.urlopen(url)
        xml = urlopener.read()
        songlists = self.parse_xml(xml)
        if len(songlists) == number + 1:
            self.has_more = True
            songlists.pop()
        else:
            self.has_more = False
        self.songlists.extend(songlists)
        return songlists
    
    def parse_xml(self, xml):
        songlists = []
        dom = minidom.parseString(xml)
        for node in dom.getElementsByTagName("node"):
            if (node.nodeType == node.ELEMENT_NODE):
                album = Album()
                album.parse_node(node)
                songlists.append(album)
        return songlists

class DirTopiclistingdir(Directory):
    
    def __init__(self):
        Directory.__init__(self)
        self.load_songlists()
            
    def load_songlists(self, start=0, number=20):
        template = "http://www.google.cn/music/topiclistingdir?cat=song&start=%d&num=%d"
        url = template % (start, number + 1)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songlists = self.parse_html(html)  
        if len(songlists) == number + 1:
            self.has_more = True
            songlists.pop()
        else:
            self.has_more = False
        self.songlists.extend(songlists)
        return songlists
        
    def parse_html(self, html):
        html = urllib.unquote(html)               
        # find id      
        ids = []  
        matches = re.findall('<a class="topic_title" href="([^"]+)">', html)
        for match in matches:
            match = re.search('topiclisting\?q=([^&]+)&', urllib.unquote(match)).group(1)
            ids.append(match)

        # find name
        names = []
        matches = re.findall('<a class="topic_title" [^>]+>([^<]+)</a>', html)
        for match in matches:
            match = GmObject.decode_html_text(match)
            names.append(match)

        # find description
        descriptions = []
        matches = re.findall('<td class="topic_description"><div title="([^"]+)"', html)
        for match in matches:
            match = match.split()[0]
            match = GmObject.decode_html_text(match)
            descriptions.append(match)

        # find thumbnail
        thumbnails = []
        # setup default thumbnail
        for i in range(len(ids)):
            thumbnails.append("http://www.google.cn/music/images/cd_cover_default_big.png")
        matches = re.findall('<td class="td-thumb-big">.+?topiclisting\?q=(.+?)&.+?src="(.+?)"', html, re.DOTALL)
        for match in matches:
            for i in range(len(ids)):
                if match[0] == ids[i]:
                    thumbnails[i] = match[1]

        # create song object, three list should have same len
        songlists = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "descriptions":descriptions[i],
                    "thumbnailLink":thumbnails[i]}
            topiclisting = Topiclisting()
            topiclisting.parse_dict(dict)
            songlists.append(topiclisting)
        return songlists
    
    
class DirArtist(Directory):
    
    def __init__(self, id):
        Directory.__init__(self)
        self.id = id
        self.load_songlists()
        
    def parse_html(self, html):
        html = urllib.unquote(html)                   
        # find id      
        ids = []  
        matches = re.findall('<!--freemusic/artist/result/([^-]+)-->', html)
        for match in matches:
            ids.append(match)

        # find name
        names = []
        matches = re.findall('<a href="/music/url\?q=/music/artist\?id.+?>(.+?)</a>', html)
        for match in matches:
            match = match.replace("<b>", "")
            match = match.replace("</b>", "")
            match = GmObject.decode_html_text(match)
            names.append(match)
            
        # find thumbnail
        thumbnails = []
        # setup default thumbnail
        for i in range(len(ids)):
            thumbnails.append("http://www.google.cn/music/images/shadow_background.png")
        matches = re.findall('<div class="thumb">.+?artist\?id=(.+?)&.+?src="(.+?)"', html, re.DOTALL)
        for match in matches:
            for i in range(len(ids)):
                if match[0] == ids[i]:
                    thumbnails[i] = match[1]

        # create song object, three list should have same len
        songlists = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "thumbnailLink":thumbnails[i]}
            artist_song = ArtistSong()
            artist_song.parse_dict(dict)
            songlists.append(artist_song)
        return songlists
        
    def load_songlists(self, start=0, number=20):
        template = "http://www.google.cn/music/search?q=%s&cat=artist&start=%d&num=%d"
        url = template % (self.id, start, number + 1)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songlists = self.parse_html(html)
        if len(songlists) == number + 1:
            self.has_more = True
            songlists.pop()
        else:
            self.has_more = False
        self.songlists.extend(songlists)
        return songlists

class DirArtistAlbum(Directory):
    
    def __init__(self, id):
        Directory.__init__(self)
        self.id = id
        self.load_songlists()
        
    def parse_html(self, html):                       
        # find id      
        ids = []  
        matches = re.findall('<!--freemusic/album/result/([^-]+)-->', html)
        for match in matches:
            ids.append(match)

        # find name
        names = []
        matches = re.findall('《(.+)》</a>&nbsp;-&nbsp;', html)
        for match in matches:
            match = match.replace("<b>", "")
            match = match.replace("</b>", "")
            match = GmObject.decode_html_text(match)
            names.append(match)
    
        # find artist
        artists = []
        matches = re.findall('<td class="Tracks" colspan="10" align="left">(.+?)</td>', html)
        for match in matches:
            match = match.replace("<b>", "")
            match = match.replace("</b>", "")
            match = match.split()[0]
            match = GmObject.decode_html_text(match)
            artists.append(match)
            
        # find thumbnail
        thumbnails = []
        matches = re.findall('<img [^/]+ class="thumb-img" [^/]+ src="([^"]+)"', html)
        for match in matches:
            thumbnails.append(match)
        # remove the first one, the artist thumbnail
        thumbnails = thumbnails[1:]

        # create song object, three list should have same len
        songlists = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "artist":artists[i], "thumbnailLink":thumbnails[i]}
            album = Album()
            album.parse_dict(dict)
            songlists.append(album)
        return songlists
        
    def load_songlists(self):
        template = "http://www.google.cn/music/artist?id=%s"
        url = template % self.id
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songlists = self.parse_html(html)
        self.songlists.extend(songlists)
        return songlists
        
class DirTag(DirTopiclistingdir):
    
    def __init__(self, id):
        Directory.__init__(self)
        self.id = id
        self.load_songlists()
        
    def load_songlists(self, start=0, number=20):
        template = "http://www.google.cn/music/tag?q=%s&cat=song&type=topics&start=%d&num=%d"
        url = template % (self.id, start, number + 1)
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songlists = self.parse_html(html)
        if len(songlists) == number + 1:
            self.has_more = True
            songlists.pop()
        else:
            self.has_more = False
        self.songlists.extend(songlists)
        return songlists
    
class DirStarrecc(Directory):
    
    def __init__(self):
        Directory.__init__(self)
        self.load_songlists()
        
    def parse_html(self, html):
        html = urllib.unquote(html)       
        # find id and name
        ids = []  
        names = []
        matches = re.findall('<div class="artist_name"><a .+?sys:star_recc:(.+?)&.+?>(.+?)</a></div>', html)
        for match in matches:
            id = match[0]
            name = GmObject.decode_html_text(match[1])
            ids.append(id)
            names.append(name)

        # find description
        descriptions = []
        matches = re.findall('<div class="song_count">(.+?)</div>', html, re.DOTALL)
        for match in matches:
            match = GmObject.decode_html_text(match)
            descriptions.append(match)

        # find thumbnail
        thumbnails = []
        matches = re.findall('<div class="artist_thumb">.+?src="(.+?)".+?</div>', html, re.DOTALL)
        for match in matches:
            thumbnails.append(match)

        # create song object, three list should have same len
        songlists = []
        for i in range(len(ids)):
            dict = {"id":ids[i], "name":names[i], "descriptions":descriptions[i],
                    "thumbnailLink":thumbnails[i]}
            starrecc = Starrecc()
            starrecc.parse_dict(dict)
            songlists.append(starrecc)
        return songlists
        
    def load_songlists(self):
        template = "http://www.google.cn/music/starrecommendationdir?num=100"
        url = template
        urlopener = urllib.urlopen(url)
        html = urlopener.read()
        songlists = self.parse_html(html)
        self.songlists.extend(songlists)
        return songlists

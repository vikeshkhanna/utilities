# Developed by Vikesh Khanna
# Lexy is an open-source utility which comes as-is WITHOUT ANY WARRANTY. 
# It uses lyrics.wikia.com to fetch lyrics. There is no guarantee that fetched lyrics would be correct or of the same song but Lexy tries her best.

# Lexy is a word play on Sexy and Lexicon :)


import urllib, urllib2
import sys
import re, htmlentitydefs
from BeautifulSoup import BeautifulSoup
from mutagen.id3 import ID3
from mutagen import *

import re, htmlentitydefs

## Thanks to Fredrik Lundh - http://effbot.org/zone/re-sub.htm#unescape-html
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

def extract_lyrics(html):
	soup = BeautifulSoup(html)
	text = str(soup.find('div', {"class" : "lyricbox"}));
	#erase all div opening and closing tags
	text = re.sub('</?\s*div.*?>','', str(text))
	
	#convert all br/ tags to new lines
	text = re.sub('<\s*br.*?>',"\n", text)	
	
	#erase all other tags
	text = re.sub('<.*?>.*</?.*?>','', text)
	
	#erase all comments - this is necessary even if DOM does not have comments because HTML parser will append template limit comment
	text = re.sub('<\s*!--.*--\s*>','', text, flags = re.DOTALL)
	
	return unescape(text)
	
def get_lyrics(title):
	title = "Wherever I may Roam"
	params = urllib.urlencode({'sourceid': 'navclient', 'btnI': 1, 'q': 'site:lyrics.wikia.com ' + title})
	url = "http://google.com/search?%s" % params;
	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
	headers = { 'User-Agent' : user_agent };
	req = urllib2.Request(url, None, headers)
	response = urllib2.urlopen(req)
	return extract_lyrics(response.read())

#print get_lyrics("Wherever I may Roam");

try:
	root = sys.argv[1];
except IndexError:
	root = str(raw_input("\nPlease enter the path of the root directory without trailing slash : "));
	
if not os.path.exists(root):
	print "\n\n" + root + " does not exist. Using current working directory.\n";
	root = os.getcwd();


print "\nWelcome to Lexy.\n"

print "0: Quit (already?)"
print "1: Fetch missing lyrics only"
print "2: Fetch lyrics for all songs"

opt = int(raw_input("\nWhat would you like to do?: "));

if opt == 0:
	print "\nBye!"
	sys.exit(0)
	
final = False

while not final:
	print "\nWarning! Lexy will change the 'lyrics' ID3 tag of all songs recursively under " + root + " if you choose to add lyrics.\n \
0: Quit\n1: Add lyrics to songs\n2: Show fetched lyrics (Test Lexy before modifying songs)"
	
	t = int(raw_input("\nWhat would you like to do?: "));
	
	if t == 0:
		print "\nBye!"
		sys.exit(0);
	elif t == 1:
		final = True
		
	for dirpath, dirnames, filenames in os.walk(root):
		for file in filenames:	
			
			replace = False
			
			try:
				audio = ID3(os.path.join(dirpath, file));
				easy_audio = EasyID3(os.path.join(dirpath, file))
				
				#okay to throw exception if no title is found
				title = ' '.join(easy_audio["title"])
				
				try: 
					title = title + ' '.easy_audio["artist"]
				except KeyError:
					print "[Warning] Artist name was not found for " + title + ". Lyrics may be wrong."
				
				lyrics = get_lyrics(title)
				print "\n" + title + " : \n" + lyrics[:len(lyrics)/10] + "...(continued) "
				
				#fetch missing songs only
				if opt == 1:
					if not audio["lyrics"] or len(audio["lyrics"]) == 0:
						replace = True
				#fetch all songs
				elif opt == 2:
					replace = True
				
				if replace:
					audio[u"USTL::'eng'"] = USLT()
					audio[u"USTL::'eng'"].text = lyrics
					audio[u"USTL::'eng'"].encoding = 0
					audio[u"USTL::'eng'"].lang = 'eng'
			except Exception as (errno, strerror):
				print "[error] Could not add lyrics : " + strerror + "(" + str(errno) +")"
		
			
	
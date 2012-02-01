# Developed by Vikesh Khanna
# Lexy is an open-source utility which comes as-is WITHOUT ANY WARRANTY. 
# It uses lyrics.wikia.com to fetch lyrics. There is no guarantee that fetched lyrics would be correct or of the same song but Lexy tries her best.

# Lexy is a word play on Sexy and Lexicon :)

import urllib, urllib2
import sys, os
import re, htmlentitydefs
from BeautifulSoup import BeautifulSoup

from mutagen.id3 import ID3
from mutagen.easyid3 import EasyID3
from mutagen import *

import re, htmlentitydefs

#max number of tries to get lyrics
MAX_ATTEMPTS = 6

#Minimum legit lyrics will have at least MIN_LEN characters
MIN_LEN  = 20

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

#Extract lyrics from plain html
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
	
	text = unescape(text)
	
	if text != "None" :
		return text
	else:
		return None

#Scrape web for lyrics from lyrics.wikia.com
def get_lyrics(title):
	params = urllib.urlencode({'sourceid': 'navclient', 'btnI': 1, 'q': 'site:lyrics.wikia.com ' + title})
	url = "http://google.com/search?%s" % params;
	user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
	headers = { 'User-Agent' : user_agent };
	req = urllib2.Request(url, None, headers)
	response = urllib2.urlopen(req)
	return extract_lyrics(response.read())

#Fault tolerant fetch lyrics
def fetch_lyrics(artist, title, filename):
	artist_store = artist
	attempts = 0
	current_request = artist + ' ' + title
	new_request = current_request
	
	print("\nFetching lyrics for " + current_request + ". Please wait.")
	lyrics = get_lyrics(current_request)
	
	#Fault tolerance 
	while attempts < MAX_ATTEMPTS:
		if lyrics and len(lyrics)>0:
			print "\n" + title + " : \n" + lyrics[:len(lyrics)/5] + "...(continued) "
			break
		else:
			message = "[retry unsuccessful] Lyrics not found. "
			
			if attempts == 0:
				message +=  "Cleaning leading numbers in title and retrying"
				title = re.sub("^([(]?\d+[)]?\s*[.]?\s*[-_]?\s*)?\s*","", title)
			elif attempts == 1:
				message += "Trying without artist name"
				artist = ''
			elif attempts == 2:
				message += "Cleaning all numbers from the title and retrying"
				title = re.sub("\d+",'',title)
			elif attempts == 3:
				message += "Cleaning trailing braced words and retrying"
				title = re.sub("\s*\((.\s*)*\)\s*$", '', title)
			elif attempts == 4:
				message += "Using file name instead of ID3 tag as title"
				title = filename
				#must try all over again with this new approach, restoring artist name
				attempt = -1
				artist = artist_store
			print message
			
		new_request = artist + ' ' + title

		# dont waste bandwidth on false guesses
		if new_request != current_request:
				current_request = new_request
				print("[retry] Fetching lyrics for " + current_request + ". Please wait.")
				lyrics = get_lyrics(current_request)
				
		attempts += 1
	
	return lyrics
	
#Check if an audio object has missing lyrics
def missing_lyrics(audio):
	if len(audio.getall("USLT")) == 0:
			return True
	else:
		full_text = ""

		for uslt in audio.getall("USLT"):
			if uslt.desc != u"None":
				full_text +=  uslt.text
			
		if len(full_text) < MIN_LEN:
			return True	

#Get title
def get_title(easy_audio, audio, file):
	filename = filename = file[0:file.rindex('.')]
				
	try:
		title = ' '.join(easy_audio["title"])
	except Exception as err:
		print("[warning] Couldn't read easyID3 for " + file + " " + str(err))
		
		for entry in audio.getall("TIT2"):
			title += ' '.join(entry.text)
	
	if len(re.sub("\s*",'',title)) == 0:
		print("[warning] Title not found in ID3 tags for " + file + ". Using file name.")
		title = filename

	return title

#Get artist
def get_artist(easy_audio, audio, file):
	artist = ''
	
	try: 
		artist = ' '.join(easy_audio["artist"])
	except KeyError:
		print("[warning] Couldn't read artist from easyID3 for " + file + " " + str(err))
	
		# Testing lead artist 
		for entry in audio.getall("TPE1"):
			artist += ' '.join(entry.text)
		
		# Testing band / orchestra
		for entry in audio.getall("TPE2"):
			artist += ' '.join(entry.text)
		
		if len(re.sub("\s*",'',artist))==0:
			print "[Warning] Artist name was not found for " + file + ". Lyrics may be wrong."
	
	return artist
	
#Set lyrics
def set_lyrics(audio, lyrics):
	audio.delall("USLT")
	audio[u"USLT::'eng'"] = id3.USLT()
	audio[u"USLT::'eng'"].text = lyrics
	audio[u"USLT::'eng'"].encoding = 0
	audio[u"USLT::'eng'"].lang = 'eng'
	audio[u"USLT::'eng'"].desc = u''
		
	audio.save(v2=3)

try:
	root = sys.argv[1];
except IndexError:
	root = str(raw_input("\nPlease enter the path of the root directory without trailing slash : "));

root = re.sub("/|\$",'', root)
	
if not os.path.exists(root):
	print "\n\n" + root + " does not exist. Using current working directory.\n";
	root = os.getcwd();


print "\nWelcome to Lexy.\n"

def get_input():
	print "0: Quit (already?)"
	print "1: Show which songs have missing lyrics"
	print "2: Fetch missing lyrics only"
	print "3: Fetch lyrics for all songs"

	opt = int(raw_input("\nWhat would you like to do?: "));

	return opt
	
final = False
recount = 0

while not final:
	
	#get user input
	opt = get_input()
	
	if opt == 0:
		print "\nBye!"
		sys.exit(0)
	
	#No secondary options needed for showing songs with missing lyrics
	if opt != 1:
		print "\nWarning! Lexy will change the 'lyrics' ID3 tag of all songs recursively under " + root + " if you choose to add lyrics.\n\
0: Quit\n1: Add lyrics to songs\n2: Show fetched lyrics (Test Lexy before modifying songs)"
		
		t = int(raw_input("\nWhat would you like to do?: "));
		
		if t == 0: # quit
			print "\nBye!"
			sys.exit(0);
		elif t == 1: #add lyrics is the final stage
			final = True
	
	for dirpath, dirnames, filenames in os.walk(root):
		for file in filenames:	
			
			#file properties
			try:
				filename = file[0:file.rindex('.')]
				extension = file[file.rindex('.') + 1:]
			
				fetch = False
			
				easy_audio = EasyID3(os.path.join(dirpath, file))
				audio = ID3(os.path.join(dirpath, file));
				
				#fetch missing songs only or show missing lyrics
				if opt == 1 or opt == 2:
					missing = missing_lyrics(audio)
							
					if missing:
						#fetch missing song
						if opt == 2:
							fetch = True
						#show missing song
						elif opt == 1:
							print "\n[Missing Lyrics] " + file
							
				#fetch all songs
				elif opt == 3:
					fetch = True
				
				if fetch:
					title = get_title(easy_audio, audio, file)
					artist = get_artist(easy_audio, audio, file)
					lyrics = fetch_lyrics(artist, title, filename)
					
					try:
						if lyrics and len(lyrics)>0 and final:
							set_lyrics(audio, lyrics)
							print "********Successfully added lyrics for " + title + "*************"
							
					except Exception as err:
							print "\n[error] Could not add lyrics: " + str(err)
							
			except Exception as err:	
				print "\n[error] " + str(err)
			
raw_input("Press enter to quit...")	
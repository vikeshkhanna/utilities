# Developed by Vikesh Khanna
# Graffiti is an open-source utility which comes as-is WITHOUT ANY WARRANTY. 
#
# Graffiti will set the cover art for all the music files under the folder to the supplied argument
#
# Usage - python graffity.py "<folder>" "<cover art>"
# If cover art image is not found relative to the root folder, graffiti will try it as absolute path

import re, os, sys
from mutagen.id3 import ID3, APIC

print("\nWelcome to Graffiti!")

if len(sys.argv) < 3:
	print("\nWrong arguments. Usage : python <album-folder> <cover-art>")
	sys.exit(1)

root = sys.argv[1]
root = re.sub("/|\$",'', root)	

#root must exist and be a directory
if not os.path.exists(root) or not os.path.isdir(root):
	print("[error] '" + root + "' does not exist or is not a directory. Appending root with current working directory")
	root = os.path.join(os.getcwd(), root)
	
	if not os.path.exists(root) or not os.path.isdir(root):
		print("[error] '" + root + "' does not exist or is not a directory. Using current working directory")
		root = os.getcwd()

print("Root folder : " + root)

art_relative = os.path.join(root,sys.argv[2])
art_absolute = sys.argv[2]
art = art_relative

extension = art[art.rindex('.')+1:];

#cover art must exist and be a regular file
if not os.path.exists(art_relative):
	if not os.path.exists(art_absolute):
		print("[error] '" + art_absolute + " does not exist")
		sys.exit(1)
	else:
		art = art_absolute

print("Cover art : " + art)

#wrong extension		
if not os.path.isfile(art):
	print("[error] '" + art + "' is not a regular file.")
	sys.exit(1)
	
if extension.find("jpg" or "jpge" or "png" or "gif") < 0:
	print("[error] '" + art + "' is not a supported image file.")
	sys.exit(1)

final = False

while not final:
	final = True
	
	t = int(raw_input("\nAre you sure you want to use this image as cover art for all songs under this directory. \n0: Quit\n1: Show Image\n2: Confirm\n\n\
What would you like to do? : "))

	if t == 0:
		print("Cool! Nothing happened")
		sys.exit(1)
	elif t == 1:
		os.startfile(art)
		final = False

for file in os.listdir(root):
	try:
		audio = ID3(os.path.join(root, file))
		audio.delall("APIC")
		audio["APIC"] = APIC(encoding=3, mime="image/" + extension, type = 3, desc = u"Cover", data = open(art,"rb").read())
		audio.save(v2=3)
		print("Successfully added artwork for " + file)
	except Exception as err:
		print("[error] " + str(err))

raw_input('Press enter to quit...');

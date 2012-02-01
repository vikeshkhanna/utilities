# Developed by Vikesh Khanna
# Graffiti is an open-source utility which comes as-is WITHOUT ANY WARRANTY. 
#
# Graffiti will set the cover art for all the music files under the folder to the supplied argument
#
# Usage - python graffity.py "<folder>" "<cover art>"
# If cover art image is not found relative to the root folder, graffiti will try it as absolute path

import re, os, sys, ctypes
from mutagen.id3 import ID3, APIC

def set_artwork(file, art):
	extension = art[art.rindex('.'):]
	audio = ID3(file)
	audio.delall("APIC")
	audio["APIC"] = APIC(encoding=3, mime="image/" + extension, type = 3, desc = u"Cover", data = open(art,"rb").read())
	audio.save(v2=3)

def is_hidden(filepath):
    name = os.path.basename(os.path.abspath(filepath))
    return name.startswith('.') or has_hidden_attribute(filepath)

def has_hidden_attribute(filepath):
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(unicode(filepath))
        assert attrs != -1
        result = bool(attrs & 2)
    except (AttributeError, AssertionError):
        result = False
    return result	

recursive = False

#must have at least 2 arguments
if len(sys.argv) < 2:
	print("\nWrong arguments. Usage : python <album-folder> <cover-art>")
	sys.exit(1)	
elif len(sys.argv) == 2:
	recursive = True

print("\nWelcome to Graffiti!")

root = sys.argv[1]
root = re.sub("/|\$",'', root)	

#root must exist and be a directory
if not os.path.exists(root) or not os.path.isdir(root):
	print("[error] '" + root + "' does not exist or is not a directory. Appending root with current working directory")
	root = os.path.join(os.getcwd(), root)
	
	if not os.path.exists(root) or not os.path.isdir(root):
		print("[error] '" + root + "' does not exist or is not a directory.")
		sys.exit(1)
		
print("Root folder : " + root)

if not recursive:
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
	print("Image type : image/" + extension)
	 
	#wrong extension		
	if not os.path.isfile(art):
		print("[error] '" + art + "' is not a regular file.")
		sys.exit(1)

	if not re.search("jpg|png|gif|jpeg", extension):
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
			set_artwork(os.path.join(root,file), art)
			print("Successfully added artwork for " + file)
		except Exception as err:
			print("[error] " + str(err))

#recursive search
else:
	t = int(raw_input("\nGraffiti will recursively edit the music files under " + root + "\n0: Quit\n1: Confirm\n\n\What would you like to do? : "))
	
	if t == 0:
		print "Cool! Nothing happened!"
		sys.exit(0)
		
	for dirpath, dirnames, filenames in os.walk(root):
			art = None
	
			# find the first image
			for file in filenames:
				try:
					path = os.path.join(dirpath, file)
					print path
					extension = file[file.rindex('.'):]
					
					if not is_hidden(path):
						if re.search("jpg|png|gif|jpeg", extension):
							art = path
							break
							
				except Exception as err:
					print("[error] " + str(err))
			
			if art:
				#set cover art
				for file in filenames:
					try:
						set_artwork(os.path.join(dirpath, file), art)
						print("***********[success] Artwork added for " + file + " ***************")
					except Exception as err:
						print("[error] " + str(err))
			else:
				print("[error] No artwork was found for " + dirpath)
				
raw_input('Press enter to quit...');

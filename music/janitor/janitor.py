import os
import sys
import re
from mutagen.easyid3 import EasyID3

utility_name = "Janitor"
user_regex = "";

#root directory
try:
	root = sys.argv[1];
except IndexError:
	root = str(raw_input("\nPlease enter the path of the root directory without trailing slash : "));
	
	if not os.path.exists(root):
		print "\n\n" + root + " does not exist. Using current working directory.\n";
		root = os.getcwd();

#custom regex input
user_regex = str(raw_input("\n\nYou can specify your own python-style regular expression if you have anything apart from numbers leading every file name, \
like, say, the artist name. Press enter if you don't understand this part: "));

if user_regex != "":
	message = "\nWarning! " + utility_name + " will rename all files that meet the criteria recursively from " + root + ". \n0 to Quit, 1 to Rename Files Only, 2 to Rename Files and Song Title, 3 to Test Custom Regex: "
else:
	message = "\nWarning! " + utility_name + " will rename all files that meet the criteria recursively from " + root + ". \n0 to Quit, 1 to Rename Files Only, 2 to Rename Files and Song Title : "

#user decision
t = int(raw_input(message));

if t == 0:
	print "\nCool! Nothing happened!\n"
	sys.exit(0);
else:
	print "\nRunning " + utility_name + "! Please be patient.\n";

#logic
for dirpath, dirnames, filenames in os.walk(root):
	for file in filenames:
			#print re.sub('^(\d+\s*[.]?\s*[-_]?\s*)?\s*(' + user_regex + ')?\s*','', file);
			old_filename = file[0: file.rindex('.')];
			extension = file[file.rindex('.'):];
			
			new_name = re.sub('^([(]?\d+[)]?\s*[.]?\s*[-_]?\s*)?\s*(' + user_regex + ')?\s*','', old_filename);
			new_filename = new_name + extension;
			
			print "[Filename] " + file + " > " + new_filename
			
			#test custom regex
			if t != 3:
				try:
					os.rename(os.path.join(dirpath, file), os.path.join(dirpath, new_filename));
					
					#rename files and ID3
					if t == 2:
						try:
							new_file = os.path.join(dirpath, new_filename);
							audio = EasyID3(os.path.join(dirpath, new_file));
							old_title = str(audio["title"])
							audio["title"] = new_name;
							audio.save()
							print "[Title] " + old_title + " > " + str(audio["title"])
							
						except Exception as err:
							print "Could not rename audio title : " + str(err)
			
				except Exception as (errno, strerror):
					print "Could not rename file : " + strerror + "(" + str(errno) +")"
					
raw_input('Press enter to quit...');

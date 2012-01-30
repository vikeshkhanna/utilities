# Developed by Vikesh Khanna
# Janitor is an open-source utility which comes as-is WITHOUT ANY WARRANTY. Janitor renames files on your drive - Use at your own risk.

# TODO : Regex presets

import os
import sys
import re
from mutagen.easyid3 import EasyID3

utility_name = "Janitor"
user_regex = "";
regex = "";
final = False
recount = 0

#root directory
try:
	root = sys.argv[1];
except IndexError:
	root = str(raw_input("\nPlease enter the path of the root directory without trailing slash : "));

root = re.sub("/|\$",'', root)	

if not os.path.exists(root):
	print "\n\n" + root + " does not exist. Using current working directory.\n";
	root = os.getcwd();

print "\nWelcome to Janitor.\n"
print "0: Quit"
print "1: Remove leading numbers followed by dots / underscores / dashes"
print "2: Remove all leading words upto and including a '-' or '_' "
print "3: Remove anything inside and including the last set of curly braces, as in Heartbreaker (Led Zeppelin).mp3"
print "4: Custom Regex (Recommended for experienced users only. This does not default to leading characters)" 

opt = int(raw_input("\nWhat would you like to do?: "));

if opt == 0:
	sys.exit(0)
elif opt == 1:
	regex = '^([(]?\d+[)]?\s*[.]?\s*[-_]?\s*)?\s*';
elif opt == 2:
	regex = '^(.)*\s*[-_]\s*';
elif opt == 3:
	regex = '\s*\((.\s*)*\)\s*$'
else:
	#custom regex input
	regex = str(raw_input("Please specify your custom regex to match. You can test your regex before applying: "));

while not final:
	#custom regex
	if opt == 4 and recount > 0:
			tempregex = str(raw_input("\nYou just tested your regex - " + regex + ". Press enter to use the same or enter the new regex here: "));
			
			if tempregex and len(tempregex) > 0:
				regex = tempregex

	message = "\nWarning! " + utility_name + " will rename all files that meet the criteria recursively from " + root + " if you choose renaming.\
\n0 to Quit\n1 to Rename Files Only\n2 to Rename Files and Song Title\n3 to Test Regex\n\nWhat would you like to do? :"

	#user decision
	t = int(raw_input(message));

	if t == 0:
		print "\nCool! Nothing happened!\n"
		sys.exit(0);
	else:
		# test regex
		if t==3:
			final = False
		else:
			final = True
		print "\nRunning " + utility_name + "! Please be patient.\n";

	#logic
	for dirpath, dirnames, filenames in os.walk(root):
		for file in filenames:
				#print re.sub('^(\d+\s*[.]?\s*[-_]?\s*)?\s*(' + user_regex + ')?\s*','', file);
				try:
					old_filename = file[0: file.rindex('.')];
					extension = file[file.rindex('.'):];
					
					new_name = re.sub(regex,'', old_filename);
					new_filename = new_name + extension;
					
					print "[Filename] " + file + " > " + new_filename
					
					# !test custom regex
					if t != 3:
						try:
							os.rename(os.path.join(dirpath, file), os.path.join(dirpath, new_filename));
							
							#rename files and ID3
							if t == 2:
								try:
									new_file = os.path.join(dirpath, new_filename);
									audio = EasyID3(os.path.join(dirpath, new_file));
									old_title = ' '.join(audio["title"])
									audio["title"] = new_name;
									audio.save()
									print "[Title] " + old_title + " > " + ' '.join(audio["title"])
									
								except Exception as err:
									print "Could not rename audio title : " + str(err)
					
						except Exception as (errno, strerror):
							print "Could not rename file : " + strerror + "(" + str(errno) +")"
				except Exception as err:
					print "Could not read file: " + str(err)
	
	recount = recount + 1
	
raw_input('Press enter to quit...');

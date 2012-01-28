import os
import sys
import re

utility_name = "Janitor"
user_regex = "";

try:
	root = sys.argv[1];
except IndexError:
	root = str(raw_input("\nPlease enter the path of the root directory without trailing slash : "));
	
	if not os.path.exists(root):
		print "\n\n" + root + " does not exist. Using current working directory.\n";
		root = os.getcwd();

user_regex = str(raw_input("\n\nYou can specify you own python-style regular expression if you have anything apart from numbers leading every file name, \
like, say, the artist name. Press enter if you don't understand this part: "));

t = raw_input("Warning! " + utility_name + " will rename all files recursively from " + root + " beginning with numbers. 0 to quit, 1 to confirm: ");

if int(t) == 0:
	print "\nCool! Nothing happened!\n"
	sys.exit(0);
else:
	print "\nRunning " + utility_name + "! Please be patient.\n";

for dirpath, dirnames, filenames in os.walk(root):
	for file in filenames:
			#print re.sub('^(\d+\s*[.]?\s*[-_]?\s*)?\s*(' + user_regex + ')?\s*','', file);
			new_name = re.sub('^(\d+\s*[.]?\s*[-_]?\s*)?\s*(' + user_regex + ')?\s*','', file);
			print file + " > " + new_name
			try:
				os.rename(os.path.join(dirpath, file), os.path.join(dirpath, new_name));
			except Exception as err:
				print "Could not rename file : " + str(err)
				
raw_input('Press enter to quit...');

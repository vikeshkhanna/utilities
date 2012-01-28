import os
import sys
import re

utility_name = "Janitor"

try:
	root = sys.argv[1];
except IndexError:
	root = raw_input("\nPlease enter the path of the root directory without trailing slash : ");

	if not os.path.exists(root):
		print "\n" + root + " does not exist. Using current working directory.\n";
		root = os.getcwd();
	
t = raw_input("Warning! " + utility_name + " will rename all files recursively from " + root + " beginning with numbers. 0 to quit, 1 to confirm: ");

if int(t) == 0:
	print "\nCool! Nothing happened!\n"
	sys.exit(0);
else:
	print "\nRunning " + utility_name + "! Please be patient.\n";

for dirpath, dirnames, filenames in os.walk(root):
	for file in filenames:
			#print re.sub('^\d+\s*[.]?\s*','', file);
			new_name = re.sub('^\d+\s*[.]?\s*','', file);
			print file + " > " + new_name
			os.rename(os.path.join(dirpath, file), os.path.join(dirpath, new_name));

raw_input('Press enter to quit...');

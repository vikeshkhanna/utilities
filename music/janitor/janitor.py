import os
import sys
import re

try:
	root = sys.argv[1];
except IndexError:
	root = os.getcwd();

t = raw_input("Warning! This utility will rename all files recursively from " + root + " beginning with numbers. 0 to quit, 1 to confirm: ");

if int(t) == 0:
	print "Cool! Nothing happened!"
	sys.exit(0);
else:
	print "\nRunning utility! Please be patient.\n";

for dirpath, dirnames, filenames in os.walk(root):
	for file in filenames:
			#print re.sub('^\d+\s*[.]?\s*','', file);
			new_name = re.sub('^\d+\s*[.]?\s*','', file);
			print file + " > " + new_name
			os.rename(os.path.join(dirpath, file), os.path.join(dirpath, new_name));

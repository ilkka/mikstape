#!/usr/bin/env python
"""
Mikstape Copyright (C)2005 Ilkka Poutanen
<if.iki@opi.backwards.invalid>

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

Get a random playlist from mikseri.net and download the files
to the specified location (e.g. mp3 player).
"""
__author__ = "Ilkka Poutanen <if.iki@opi.backwards.invalid>"
__date__ = "2005-03-17"
__version__ = "0.4"

import os
import sys
import getopt
import string
import urllib
import urlparse
import re # regexes

# usage message
def usage():
    print """Usage: %s OPTIONS GENRE [ GENRE [ GENRE ... ] ]
Supported options:
\t-h (--help)        Display this message
\t-v (--verbose)     Be more verbose
\t-d (--destination) Destination directory for files
\t-g (--genres)      List the supported genres
\t-f (--file)        Get the playlist from a file instead of the net
\t-n (--numeric)     Use numeric filenames
\t-c (--count)       Number of files to get (10-100 in increments
\t                   of 10, default 100)""" % (sys.argv[0])

# progress tracker
def tracker(numblocks, blocksize, filesize):
# calculate progress in percent
# check for unreported size
    if filesize==-1:
        sys.stdout.write("<unknown>\b\b\b\b\b\b\b\b\b")
    else:
        done = ((numblocks*blocksize)/float(filesize))*100
        sys.stdout.write("%3d%%\b\b\b\b" % done)
    
# global state variables
be_verbose = False
destination = "."
count = 100
genres = []
get_from_file = False
playlist_filename = "";
numeric = False

# constants
GENRE_KEYS = {
    'Blues':2,
    'Jazz':2,
    'Funk':3,
    'Hiphop':4,
    'Rap':4,
    'Metal':5,
    'Pop':6,
    'Rock':6,
    'Electronic':8,
    'Soul':9,
    '''R'n'B''':9,
    'Alternative':10,
    'Muut':11
}

URLBASE = 'http://www.mikseri.net/www/makeplaylist.php'

# Option handling
try:
# args are the genres to use
	opts, args = getopt.getopt(sys.argv[1:],
		    'vhgd:c:f:n',
		    ['verbose','help','genres','destination=','count=','file=', 'numeric'])
# process switches
	for opt, arg in opts:
		if opt in ('-v', '--verbose'):
			be_verbose = True
		elif opt in ('-h', '--help'):
			usage()
			sys.exit(0)
		elif opt in ('-g', '--genres'):
			for g,i in GENRE_KEYS.iteritems():
				print g
			sys.exit(0)
		elif opt in ('-d', '--destination'):
			print 'Destination: %s' % (arg)
			destination = arg
		elif opt in ('-c', '--count'):
			try:
				count = int(arg)
				if (count % 10 != 0 or count < 10 or count > 100):
					raise count
			except:
				print 'Invalid count arg: %s' % (arg)
				usage()
				sys.exit(2)
				
			print 'Count: %d' % (count)
			
		elif opt in ('-f', '--file'):
			playlist_filename = arg
			get_from_file = True
		elif opt in ('-n', '--numeric'):
			numeric = True

		else:
			print 'Invalid opt: %s=%s' % (opt, arg)
			usage()
			sys.exit(2)
		
# process genre args
	for genre in args:
		if GENRE_KEYS.has_key(genre):
			print 'Include genre: %s' % (genre)
			genres.append(GENRE_KEYS[genre])
		else:
			print 'Unsupported genre: %s' % (genre)
			sys.exit(2)
		
except getopt.GetoptError:
	print 'Invalid options'
	usage()
	sys.exit(1)

# we need at least one genre, unless it's a playlist file
if (get_from_file == False and len(genres)==0):
	print 'You must specify at least one genre.'
	sys.exit(3)

# test destination
if os.path.isdir(destination)==False:
	print 'Destination "%s" is not a directory.' % destination
	sys.exit(5)

# build the GET request
if (get_from_file == False):
	urlparts = [URLBASE,'?limit=',str(count)]
	for g in genres:
		urlparts.append(''.join(['&genre[',str(g),']=1']))
		url = ''.join(urlparts)
		
	if be_verbose:
		print 'GET: %s' % url

# open the url
	pl_fh = urllib.urlopen(url)

else:
	pl_fh = open(playlist_filename)
	
song_urls = []
# read the file and grab the song urls
while True:
	line = pl_fh.readline()
	if line=='':
		break

	if re.search(r'^http.*mp3', line):
		url = line.splitlines()[0]
		song_urls.append(url)

if len(song_urls)==0:
	print 'No songs found in playlist'
	sys.exit(4)

# ok, now download the tunes
current = 1
for url in song_urls:
# get the filename part from the url
	tmp = urlparse.urlsplit(url)
	filename = ""
	if numeric == True:
		filename = "audio_%d.%s" % (current, tmp[2][-3:])
	else:
		filename = os.path.basename(tmp[2])
	destname = os.path.join (destination, filename)
	sys.stdout.write('[%d of %d] Fetching %s to %s: ' %
	(current, count, url, destname))
	urllib.urlretrieve(url, destname, tracker)
	sys.stdout.write("\n")
	current = current+1


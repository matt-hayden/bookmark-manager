#!/usr/bin/env python3
from contextlib import closing
from datetime import datetime
import os, os.path

import requests

from backend import *

debug = info = warning = error = panic = print

capture_root = 'capture'
thumbnail_root = 'thumbnails'


def probe_uri(uri):
	proto, _ = uri.split(':', 1)
	if proto.upper() in ['RTMP']:
		uri, _ = uri.split(' ', 1)
		raise ValueError()
	try:
		r = requests.head(uri)
		return r.status_code
	except:
		return False

def check_channel(con, arg, ok=requests.codes.ok):
	segment_id, uri, key = get_channel(con, arg)
	proto, _ = uri.split(':', 1)
	sc = probe_uri(uri)
	if sc:
		with closing(con.cursor()) as cur:
			cur.execute('INSERT INTO channel_status (segment_id, status) VALUES (?,?);', (segment_id, sc) )
	return sc == ok
#
def get_thumbnails(con, arg, count=6, **kwargs):
	segment_id, uri, key = get_channel(con, arg)
	now = datetime.now()
	ds, ts = now.strftime('%Y%m%d'), now.strftime('%H%M')
	thumbnail_directory = os.path.join(thumbnail_root, str(segment_id), ds, ts)
	#
	command = [ 'thumbnail.bash', '-d', thumbnail_directory, '-n', str(count), uri ]
	proc = subprocess.Popen(command, stdout=subprocess.PIPE)
	out, _ = proc.communicate()
	assert not proc.returncode
	fns = eval( '['+out+']' ) if out else [] # quick form a list from output
	#
	if fns:
		with closing(con.cursor()) as cur:
			cur.execute('INSERT INTO channel_thumbnails (segment_id, thumbnail_directory, thumbnail_filenames) VALUES (?,?,?);', (segment_id, thumbnail_directory, ';'.join(fns)) )
		con.commit()
	return len(fns)
def get_capture(con, arg, duration='4:00:00:00.000', **kwargs):
	segment_id, uri, key = get_channel(con, arg)
	now = datetime.now()
	ds, ts = now.strftime('%Y%m%d'), now.strftime('%H%M')
	capture_directory = os.path.join(capture_root, str(segment_id), ds, ts)
	#
	command = [ 'capture.bash', '-d', capture_directory, uri ]
	proc = subprocess.Popen(command, stdout=subprocess.PIPE)
	out, _ = proc.communicate()
	assert not proc.returncode
	fns = eval( '['+out+']' ) if out else [] # quick form a list from output
	#
	if fns:
		with closing(con.cursor()) as cur:
			cur.execute('INSERT INTO channel_captures (segment_id, capture_directory, capture_filenames) VALUES (?,?,?);', (segment_id, capture_directory, ';'.join(fns)) )
		con.commit()
	return len(fns)

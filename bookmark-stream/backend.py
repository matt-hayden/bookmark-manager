#!/usr/bin/env python3
from contextlib import closing
from datetime import datetime
import os, os.path

import requests

from backend_base import *
from media import thumbnails

debug = info = warning = error = panic = print

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
	with closing(con.cursor()) as cur:
		cur.execute('SELECT segment_id, absolute_uri, key FROM channels WHERE (?) in (segment_id, absolute_uri, title);', (arg,) )
		#assert len(cur) == 1
		[ (segment_id, uri, key) ] = cur.fetchall()
		proto, _ = uri.split(':', 1)
		sc = probe_uri(uri)
		if sc:
			cur.execute('INSERT INTO channel_status (segment_id, uri_status) VALUES (?,?);', (segment_id, sc) )
		return sc == ok
#
def make_thumbnails(con, arg, **kwargs):
	with closing(con.cursor()) as cur:
		cur.execute('SELECT segment_id, absolute_uri, key FROM valid_channels WHERE (?) in (segment_id, absolute_uri, title);', (arg,) )
		#assert len(cur) == 1
		[ (segment_id, uri, key) ] = cur.fetchall()
	now = datetime.now()
	ds, ts = now.strftime('%Y%m%d'), now.strftime('%H%M')
	thumbnail_directory = os.path.join(thumbnail_root, str(segment_id), ds)
	if not os.path.isdir(thumbnail_directory):
		os.makedirs(thumbnail_directory)
		nthumbs = 0
	else:
		nthumbs = -len(os.listdir(thumbnail_directory))
	if 'frames' not in kwargs:
		kwargs['frames'] = 3
	if 'output_file_pattern' not in kwargs:
		kwargs['output_file_pattern'] = ts+'+%01d.JPEG'
	if thumbnails(uri, **kwargs):
		tfs = os.listdir(thumbnail_directory)
		nthumbs += len(tfs)
		if nthumbs:
			with closing(con.cursor()) as cur:
				cur.execute('INSERT INTO channel_status (segment_id, thumbnail_directory, thumbnail_filenames) VALUES (?,?,?);', (segment_id, thumbnail_directory, ';'.join(tfs)) )
			con.commit()
		return nthumbs

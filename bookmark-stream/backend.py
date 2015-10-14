
from contextlib import closing
import sqlite3 as sqlite

import requests

from backend_base import *

debug = info = warning = error = panic = print

def check_channel(con, arg, ok=requests.codes.ok):
	with closing(con.cursor()) as cur:
		cur.execute('SELECT segment_id, absolute_uri, key FROM channels WHERE (?) in (segment_id, absolute_uri, title);', (arg,) )
		#assert len(cur) == 1
		[ (segment_id, uri, key) ] = cur.fetchall()
		if uri.startswith('rtmp'):
			uri, _ = uri.split(' ', 1)
		try:
			r = requests.head(uri)
			sc = r.status_code
			del r
		except:
			sc = -1
		if sc:
			cur.execute('INSERT INTO channel_status (segment_id, uri_status) VALUES (?, ?);', (segment_id, sc) )
		return sc == ok
#
def get_valid_channels(con, quick=True, ok=requests.codes.ok):
	with closing(con.cursor()) as cur:
		#query = cur.execute('SELECT segment_id, thumbnail_directory, thumbnail_filenames WHERE uri_status == (?);', (ok,) )
		query = cur.execute('SELECT * from channel_status WHERE uri_status == (?) ORDER BY uri_checked DESC;', (ok,) )
		results = query.fetchall()
	debug("{} valid channels".format(len(results)) )
	return results

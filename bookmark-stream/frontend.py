#!/usr/bin/env python3
import m3u8

import backend

debug = info = warning = error = panic = print


def import_playlist(con, filename):
	pl = m3u8.load(filename)
	rows = [ (s.absolute_uri, s.title, s.duration, s.program_date_time, s.key) for s in pl.segments if s.absolute_uri ]
	debug("Read {} rows".format(len(rows)) )
	n = backend.populate_channels(con, rows)
	debug("Wrote {} rows".format(n))
	return n

if __name__ == '__main__':
	import sys
	con = backend.open_backend('test.sqlite')
	for arg in sys.argv[1:]:
		import_playlist(con, arg)

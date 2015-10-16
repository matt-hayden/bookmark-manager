#!/usr/bin/env python3
from contextlib import closing, suppress
import sqlite3 as sqlite

import m3u8

import middle

debug = info = warning = error = panic = print


def format_m3u8_entry(row):
	'''Jam the output of a m3u8 segment into a local format
	'''
	if isinstance(row, m3u8.Segment):
		segment = row
		row = (segment.absolute_uri, segment.title, segment.duration, segment.program_date_time, segment.key)
	absolute_uri, title, duration, program_date_time, key = row
	proto, _ = absolute_uri.split(':', 1)
	if proto.upper() in ['RTMP']: ### TODO
		proto_options = absolute_uri.split()
		uri = proto_options.pop(0)
	else:
		uri, proto_options = absolute_uri, ''
	return uri, ' '.join(proto_options), title.strip(), duration, program_date_time, key


def populate_channels(con, iterable):
	with closing(con.cursor()) as cur:
		cur.execute('select count(*) from channels;')
		[(old_n,)] = cur.fetchall()
		syntax = '''INSERT INTO channels (absolute_uri, proto_options, title, duration, program_date_time, key) VALUES (?, ?, ?, ?, ?, ?);'''
		for row in iterable:
			try:
				cur.execute(syntax, format_m3u8_entry(row))
				debug("{} added".format(row))
			except sqlite.IntegrityError as e:
				info("Duplicate uri ignored: {}".format(e))
		cur.execute('select count(*) from channels;')
		[(new_n,)] = cur.fetchall()
	con.commit()
	return new_n - old_n


def import_playlist(con, filename):
	pl = m3u8.load(filename)
	debug("Read {} rows".format(len(pl.segments)) )
	n = populate_channels(con, pl.segments)
	debug("Wrote {} rows".format(n))
	return n



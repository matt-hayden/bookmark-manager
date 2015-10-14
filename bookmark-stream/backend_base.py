#!/usr/bin/env python3
from contextlib import closing
import os, os.path
import sqlite3 as sqlite

debug = info = warning = error = panic = print

CREATE_SYNTAXES = ['''CREATE TABLE channels
(segment_id			INTEGER		PRIMARY KEY,
 added				DATETIME	DEFAULT CURRENT_TIMESTAMP,
 absolute_uri		TEXT(1023)	UNIQUE NOT NULL,
 rtmp_options		TEXT(1023),
 title				TEXT(1023),
 duration			REAL		DEFAULT NULL,
 program_date_time	DATETIME,
 key				TEXT(1023)
 );''',
'''CREATE TABLE channel_status
(segment_id				INTEGER		NOT NULL,
 uri_checked			DATETIME	DEFAULT CURRENT_TIMESTAMP,
 uri_status				INTEGER,
 thumbnail_directory	TEXT(1023),
 thumbnail_filenames	TEXT(1023), -- semicolon-separated --
 FOREIGN KEY(segment_id) REFERENCES channels(segment_id) ON UPDATE CASCADE ON DELETE CASCADE
 );''',
'''CREATE VIEW valid_channels AS
SELECT * FROM channels WHERE segment_id IN (SELECT segment_id FROM channel_status WHERE uri_status == 200);'''
 ]

def create_backend(arg, **kwargs):
	if isinstance(arg, str):
		assert not os.path.exists(arg), "Refusing to overwrite {}".format(arg)
		con = sqlite.connect(arg, **kwargs)
	elif arg:
		con = arg
	else:
		con = sqlite.connect(':memory:', **kwargs)
	with closing(con.cursor()) as cur:
		try:
			for statement in CREATE_SYNTAXES:
				debug("Executing {}".format(statement))
				cur.execute(statement)
			cur.close()
			con.commit()
		except sqlite.OperationalError as e:
			error(e)
def open_backend(arg=None, **kwargs):
	if isinstance(arg, str):
		if os.path.exists(arg):
			con = sqlite.connect(arg, **kwargs)
		else:
			create_backend(arg)
	elif arg:
		con = arg
	else:
		con = sqlite.connect(':memory:', **kwargs)
	return con
#
def add_channel(con, (absolute_uri, title, duration, program_date_time, key)):
	uri = absolute_uri
	if uri.startswith('rtmp'):
		uri, _ = uri.split(' ',1)
def populate_channels(con, iterable):
	def make_rows(iterable):
		# rows is absolute_uri, title, duration, program_date_time, key
		for row in iterable:
			absolute_uri, title, duration, program_date_time, key = row
			if absolute_uri.startswith('rtmp'):
				uri, rtmp_options = absolute_uri.split(None, 1)
			else:
				uri, rtmp_options = absolute_uri, ''
			yield uri, rtmp_options, title, duration, program_date_time, key
	with closing(con.cursor()) as cur:
		cur.execute('select count(*) from channels;')
		[(old_n,)] = cur.fetchall()
		syntax = '''INSERT INTO channels (absolute_uri, rtmp_options, title, duration, program_date_time, key) VALUES (?, ?, ?, ?, ?, ?);'''
		cur = con.cursor()
		cur.executemany(syntax, make_rows(iterable))
		cur.execute('select count(*) from channels;')
		[(new_n,)] = cur.fetchall()
	con.commit()
	return new_n - old_n
#
def get_all_channels(con):
	uniques, dups = [], []
	with closing(con.cursor()) as cur:
		query = cur.execute('SELECT absolute_uri, count(*) FROM channels GROUP BY absolute_uri;')
		for address, count in query.fetchall(): # fetchmany():
			(uniques if count == 1 else dups).append(address)
	return uniques, dups
#

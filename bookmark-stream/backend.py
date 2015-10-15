#!/usr/bin/env python3
from contextlib import closing
import os, os.path
import sqlite3 as sqlite

debug = info = warning = error = panic = print

def create_backend(arg=None, **kwargs):
	if isinstance(arg, str):
		assert not os.path.exists(arg), "Refusing to overwrite {}".format(arg)
		con = sqlite.connect(arg, **kwargs)
	elif arg:
		con = arg
	else:
		con = sqlite.connect(':memory:', **kwargs)
	with open('structure.sql') as fi:
		statements = [ s+';' for s in fi.read().split(';') ]
	info("Creating new sqlite database in {} statements".format(len(statements)) )
	with closing(con.cursor()) as cur:
		for statement in statements:
			debug("Executing {}".format(statement))
			cur.execute(statement)
	con.commit()
	return con
def open_backend(arg=None, **kwargs):
	if not arg:
		return create_backend(arg)
	elif isinstance(arg, str):
		if not os.path.exists(arg):
			return create_backend(arg)
		else:
			con = sqlite.connect(arg, **kwargs)
	else:
		con = arg
	return con
#
def get_channel(con, arg):
	with closing(con.cursor()) as cur:
		cur.execute('SELECT segment_id, absolute_uri, key FROM channels WHERE (?) in (segment_id, absolute_uri, title);', (arg,) )
		#assert len(cur) == 1
		[ (segment_id, uri, key) ] = cur.fetchall()
	return (segment_id, uri, key)
#

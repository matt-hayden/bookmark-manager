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
		statements = fi.read().split('\n\n')
	info("Creating new sqlite database in {} statements".format(len(statements)) )
	with closing(con.cursor()) as cur:
		try:
			for statement in statements:
				debug("Executing {}".format(statement))
				cur.execute(statement)
		except sqlite.OperationalError as e:
			error(e)
		else:
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
def get_all_channels(con):
	uniques, dups = [], []
	with closing(con.cursor()) as cur:
		query = cur.execute('SELECT absolute_uri, count(*) FROM channels GROUP BY absolute_uri;')
		for address, count in query.fetchall(): # fetchmany():
			(uniques if count == 1 else dups).append(address)
	return uniques, dups
#

#!/usr/bin/env python3
import collections

from utils import *
#
def add(tree, path, leaf_value=None):
	key = path.pop(-1)
	for node in path:
		if node.isdigit():
			node = int(node)
		tree = tree[node]
	if key:
		tree[key] = unbox(leaf_value)
#
def parse_flat(iterable, result=None): # see utils.py for Tree()
	"""Very general parser for ffprobe and ffmpeg 'flat' file output
	"""
	if not result:
		result = Tree()
	for line in iterable:
		tpath, value = line.rstrip().split('=', 1)
		v = dequote(value)
		if v and v not in ['N/A', '0/0', '']:
			add(result, tpath.split('.'), v)
	return result

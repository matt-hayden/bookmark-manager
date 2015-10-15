#!/usr/bin/env python3
import collections
#from decimal import Decimal
#from fractions import Fraction
import os, os.path
import urllib.parse

def Decimal(f):
	return float(f)
def Fraction(n, d):
	return n, d

import requests

debug = info = warning = error = panic = print

def is_valid_url(t, parser=urllib.parse.urlparse):
	u = parser(t)
	return u.netloc
def is_playlist(t, parser=urllib.parse.urlparse):
	u = parser(t)
	netloc = u.netloc
	dirname, basename = os.path.split(netloc)
	filepart, ext = os.path.splitext(basename)
	return ext.upper() in ['.M3U8', '.M3U']
def probe_url(u, ok=[requests.codes.ok]):
	try:
		r = requests.head(u)
		return r.status_code in ok
	except:
		return False
#
def Tree():
	"""Initializes a Python tree with arbitrary depth.
	
	Member functions should be customized for adding nodes.
	"""
	return collections.defaultdict(Tree)
#
def dequote(t, quote_chars='''"'`'''):
	if 2 < len(t):
		while t and (t[0] == t[-1]) and t[0] in quote_chars:
			t = t[1:-1]
	return t
#
def isdecimal(t, alphabet=set('0123456789.,')):
	if set(t) <= alphabet:
		if t.count('.') <= 1:
			return True
	return False
def ishex(t, alphabet=set('0123456789abcdefABCDEFx')):
	if set(t) <= alphabet:
		if t.count('x') <= 1:
			return True
	return False
def isfraction(t, alphabet=set('0123456789/ ')):
	if set(t) <= alphabet:
		if t.count('/') <= 1:
			return True
	return False
#
def unbox(t):
	value = dequote(t.strip())
	if value.isdigit():
		return int(value)
	elif ishex(value):
		return int(value, 16)
	elif isdecimal(value):
		try:
			return Decimal(value)
		except:
			return value
	elif isfraction(value):
		try:
			n, d = value.split('/')
			if d == '1':
				return int(n)
			return Fraction(int(n), int(d))
		except:
			return value
	else:
		return value

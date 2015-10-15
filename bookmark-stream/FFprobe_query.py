#!/usr/bin/env python3
import json
import os, os.path
import subprocess
import tempfile

from FFprobe_output import *


def blackdetect(src, vfilter='blackdetect=d=1/15:picture_black_ratio_th=0.85:pixel_black_th=0.1', encoding='UTF-8'):
	command = ['ffprobe', '-v', 'error', '-of', 'flat', '-show_entries', \
			   'tags=lavfi.black_start,lavfi.black_end,lavfi.black_duration', \
			   '-f', 'lavfi', 'movie={src},{vfilter}[out0]'.format(**locals()) ]
	print(command)
	proc = subprocess.Popen(command, stdout=subprocess.PIPE)
	out, _ = proc.communicate()
	if out:
		content = parse_flat(out.decode(encoding).splitlines())
		return content

class FFprobe_query:
	def __init__(self, src, encoding='UTF-8'):
		self.src = src
		proc = subprocess.Popen(['ffprobe', '-v', 'error', src, '-of', 'flat', '-show_streams', '-show_format'], stdout=subprocess.PIPE)
		out, _ = proc.communicate()
		self.flat = parse_flat(out.decode(encoding).splitlines())
	def save(self, filename):
		with open(filename, 'w') as fo:
			json.dump(self.flat, fo)
	def get_bit_rates(self, **kwargs):
		for i, s in self.flat['streams']['stream'].items():
			if 'bit_rate' in s:
				yield i, s['bit_rate']
	@property
	def bit_rate(self):
		return sum(b for i, b in self.get_bit_rates())
	@property
	def video(self):
		return self.get_stream('video')
	@property
	def audio(self):
		return self.get_stream('audio')
	def get_stream(self, codec_type=[]):
		if isinstance(codec_type, str):
			codec_type = [codec_type]
		for k, d in self.flat['streams']['stream'].items():
			if d['codec_type'] in codec_type:
				yield k, d
	@property
	def dimensions(self):
		try:
			[(vtn, vt)] = self.video # one and only one video track
			return vt['width'], vt['height']
		except:
			pass
	def blackdetect(self, **kwargs):
		try:
			return self._blackdetect
		except:
			pass
		assert os.path.exists(self.src)
		try:
			blackdetect_file = self.blackdetect_file
		except:
			self.blackdetect_file = blackdetect_file = self.src+'.blackdetect'
		if os.path.exists(blackdetect_file):
			with open(blackdetect_file) as fi:
				content = json.load(fi)
		else:
			content = blackdetect(self.src, **kwargs)
			with open(blackdetect_file, 'w') as fo:
				if content:
					json.dump(content, fo)
		self._blackdetect = content
		return content
#
def parse_blackdetect(blackdetect_iterable, mode='times'):
	frame_tags = sorted((int(k), v['tags']) for k, v in blackdetect_iterable.items())
	if 'lavfi_black_end' in frame_tags[0][1]:
		ends = frame_tags[0::2]
		starts = frame_tags[1::2]
	elif 'lavfi_black_start' in frame_tags[0][1]:
		starts = frame_tags[0::2]
		ends = [ (0, {'lavfi_black_end': 0}) ]+frame_tags[1::2]
	else:
		raise ValueError(frame_tags[0])
	if 'lavfi_black_start' in frame_tags[-1][1]:
		# normal
		pass
	elif 'lavfi_black_end' in frame_tags[-1][1]:
		starts.append( ( 1E6, {'lavfi_black_start': 1E6} ) ) # TODO
	else:
		raise ValueError(frame_tags[0])
	if len(ends) != len(starts):
		print("Different sizes:", ends, starts)
	pairs = zip(ends, starts)
	if 'times' == mode:
		for endp, startp in pairs:
			end, start = Decimal(endp[1]['lavfi_black_end']), Decimal(startp[1]['lavfi_black_start'])
			if 0 <= end and 0 <= start:
				yield end, start
			else:
				print(endp, startp, "ignored")
		#return [ (endp[1]['lavfi_black_end'], startp[1]['lavfi_black_start']) for endp, startp in pairs ]
	elif 'frames' == mode:
		for endp, startp in pairs:
			end, start = int(endp[0]), int(startp[0])
			yield end, start
		#return [ (endp[0], startp[0]) for endp, startp in pairs ]
	else:
		raise ValueError(mode)

def make_scenes(filename):
	props = FFprobe_query(filename)
	black_frames = props.blackdetect()['frames']['frame']
	pairs = parse_blackdetect(black_frames)
	return pairs
def get_thumbs(filename, from_t=None, to_t=None, output='{filepart}-%08d.PNG'):
	dirname, basename = os.path.split(filename)
	filepart, ext = os.path.splitext(basename)
	try:
		output = output.format(**locals())
	except:
		print("{output} is likely not what you want".format(**locals()) )
	if os.path.sep not in output:
		output = os.path.join(tempfile.mkdtemp(), output)
	if from_t and to_t:
		command = [ 'ffmpeg', '-skip_frame', 'nokey', '-ss', str(from_t), '-i', filename, '-to', str(to_t), '-f', 'image2', output ]
	else:
		command = [ 'ffmpeg', '-skip_frame', 'nokey', '-i', filename, '-f', 'image2', output ]
	print(command)
	if subprocess.check_call(command):
		print('succeeded')
	else:
		print('failed')
	return output
		
#
if __name__ == '__main__':
	import pprint
	import sys
	args = sys.argv[1:]
	filename = args[0]
	ffp=FFprobe_query(filename)
	print("Blackdetect:")
	pprint.pprint(ffp.blackdetect())
	pairs = make_scenes(filename)
	for from_t, to_t in pairs:
		get_thumbs(filename, from_t=from_t, to_t=to_t)

import os, os.path
import subprocess

import FFprobe_query

debug = info = warning = error = panic = print

def get_media_type(src):
	debug("Opening {}".format(src))
	ffp = FFprobe_query.FFprobe_query(src)
	if ffp:
		bit_rate = ffp.bit_rate # total stream bit rate
		dim = ffp.dimensions
		if dim:
			return "{0:.0f} Mb video at {1[0]}x{1[1]}".format(bit_rate/1E6, dim)
		else:
			return "{0:.0f} Kb audio".format(bit_rate/1E3)
def thumbnail(src, output_file_pattern='{filepart}-%08d.PNG', frames=1):
	assert 1 <= frames
	_, basename = os.path.split(src)
	filepart, ext = os.path.splitext(basename)
	try:
		ofn = output_file_pattern.format(**locals())
	except:
		ofn = output_file_pattern
		warning("Output is {}, which is likely not what you want".format(ofn))
	if 1 < frames:
		frames += 1
		command = [ 'ffmpeg', '-v', 'error', '-nostdin', '-i', src, '-frames:v', str(frames), '-r', '1/100', '-f', 'image2', ofn ]
	else:
		command = [ 'ffmpeg', '-v', 'error', '-nostdin', '-i', src, '-frames:v', str(frames), '-f', 'image2', ofn ]
	proc = subprocess.Popen(command)
	_, _ = proc.communicate()
	return not proc.returncode

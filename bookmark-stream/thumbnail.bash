#! /bin/bash
set -e

SCRIPT="${BASH_SOURCE[0]##*/}"
prefix=thumbnails

: using executables : ${FFMPEG='ffmpeg -v info -nostdin'} ${FFPROBE='ffprobe -v info'}
: using temporary files : ${errors=`mktemp`}


function help() {
	cat <<- EOF
This is help
EOF
	caller 0
	exit -1
}

function usage() {
	cat <<- EOF
This is usage
EOF
	caller 0
	exit -1
}

function die() {
	echo <<< "$@"
	exit -1
}

: defaults : ${output_dir="${prefix}-$$"}

case $- in
	*x*)
		leave_log=yes
	;;
esac

while getopts "a:d:n:p:q -:" OPT
do
	if [[ $OPT == '-' ]] # Long option
	then
		if [[ $OPTARG ]]
		then
			OPT=$OPTARG
			eval $OPT && continue || usage # you may or may not want the continue
		else # just --, so commence with no option parsing
			break
		fi
	fi
	case $OPT in
		-) # long argument, test above does not let us reach here
		;;
		h|help) help
		;;
		a|all)
			count=1
		;;
		d|output_dir)
			output_dir="$OPTARG"
		;;
		n|count)
			count="$OPTARG"
			$(( count + 0 ))
		;;
		p|prefix)
			prefix="$OPTARG"
		;;
		q|quiet)
			quiet=yes
		;;
		\?) usage # unrecognized option it a literal '?'
		;;
	esac
done >&2
shift $((OPTIND-1))

[[ -d "$output_dir" ]] || mkdir -p "$output_dir"

uri="$1"
[[ "$@" ]] || usage

thumb_dest="${output_dir}/${prefix}-%04d.JPEG"
log_dest="${thumbs_dest}.log"
error_dest="${thumbs_dest}.errors"

case $count in
	0)
		function thumbs() {
			$FFMPEG -i "$1" -r '1/600' -f image2 "${thumb_dest}"
		}
	;;
	1)
		function thumbs() {
			$FFMPEG -i "$1" -frames:v 1 -f image2 "${thumb_dest}"
		}
	;;
	*)
		function thumbs() {
			$FFMPEG -i "$1" -frames:v $(( count + 1 )) -r '1/600' -f image2 "${thumb_dest}"
		}
	;;
esac

if thumbs "$uri" &> "$errors"
then
	[[ $quiet == no ]] || ls -mtr --quoting-style=c "${output_dir}/${prefix}"*
	[[ $leave_log == yes ]] && [[ -s "$errors" ]] && gzip -cn "$errors" >> "${log_dest}.GZ"
elif [[ -s "$errors" ]]
then
	gzip -cn "$errors" >> "${error_dest}.GZ"
fi

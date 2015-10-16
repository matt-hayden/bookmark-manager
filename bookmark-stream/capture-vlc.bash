#! /bin/bash
set -e

SCRIPT="${BASH_SOURCE[0]##*/}"
prefix="${SCRIPT%.*}"

: using executables : ${FFMPEG=ffmpeg} ${VLC="cvlc --sout-keep --sout-all"}
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

: defaults : ${retries=1} ${output_dir="${prefix}-$$"} ${duration=14400}

case $- in
	*x*)
		leave_log=yes
	;;
esac

while getopts ":d:D:Lp:qr: -:" OPT
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
		d|output_dir)
			output_dir="$OPTARG"
		;;
		D|duration)
			duration="$OPTARG"
		;;
		L|leave_log)
			leave_log=yes
		;;
		p|prefix)
			prefix="$OPTARG"
		;;
		q|quiet)
			quiet=yes
		;;
		r|retries)
			retries="$OPTARG"
		;;
		\?) usage # unrecognized option it a literal '?'
		;;
	esac
done >&2
shift $((OPTIND-1))

[[ -d "$output_dir" ]] || mkdir -p "$output_dir"

uri="$1"
shift
[[ "$@" ]] && usage

for r in `eval echo {1..$retries}`
do
	file_dest="${output_dir}/${prefix}-${r}.MKV"
	thumb_dest="${file_dest%.*}-%04d.JPEG"
	log_dest="${file_dest}.log"
	error_dest="${file_dest}.errors"
	if $VLC --run-time "${duration}" --stop-time "${duration}" --sout file/mkv:"${file_dest}" "$uri" "vlc://quit" &> "$errors"
	#if $VLC --sout file/mkv:"${file_dest}" "$uri" &> "$errors"
	then
		$FFMPEG -i "${file_dest}" -r '1/600' -f image2 "${thumb_dest}" &>> "$errors" &
	else
		[[ $leave_log == yes ]] && [[ -s "$errors" ]] && gzip -cn "$errors" >> "${log_dest}.gz"
	fi
	sleep 24
done
[[ $quiet == no ]] || ls -mtr --quoting-style=c "${output_dir}/${prefix}"*

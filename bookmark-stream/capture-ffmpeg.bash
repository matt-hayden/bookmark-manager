#! /bin/bash
set -e

SCRIPT="${BASH_SOURCE[0]##*/}"
prefix="${SCRIPT%.*}"

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

: defaults : ${retries=1} ${output_dir="${prefix}-$$"} ${duration='4:00:00.000'}

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
[[ "$@" ]] || usage

for r in `eval echo {1..$retries}`
do
	list_dest="${output_dir}/${prefix}-${r}.FFCONCAT"
	file_dest="${list_dest%.*}-%04d.MKV"
	thumb_dest="${list_dest%.*}-%04d.JPEG"
	log_dest="${list_dest}.log"
	error_dest="${list_dest}.errors"
	if $FFMPEG -i "$uri" -to "${duration}" -c:v copy -flags +global_header \
		   -f segment -segment_atclocktime 1 -segment_time 600 -segment_list_type ffconcat -segment_list "${list_dest}" \
		   "${file_dest}" &> "$errors"
	then
		$FFMPEG -i "${list_dest}" -r '1/600' -f image2 "${thumb_dest}" &>> "$errors" &
	else
		[[ $leave_log == yes ]] && [[ -s "$errors" ]] && gzip -cn "$errors" >> "${log_dest}.GZ"
	fi
	sleep 24
done
[[ $quiet == no ]] || ls -mtr --quoting-style=c "${output_dir}/${prefix}"*

#! /bin/bash
set -e

SCRIPT="${BASH_SOURCE[0]##*/}"
prefix="${SCRIPT%.*}"

: using executables : ${FFMPEG=ffmpeg} ${FFPROBE=ffprobe}
: using temporary files : ${log=`mktemp`} ${errors=`mktemp`}


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

: defaults : ${retries=1} ${output_dir="capture-$$"} ${duration='4:00:00.000'}

while getopts ":d:D:L:r: -:" OPT
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
			leave_log=1
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
	file_dest="${output_dir}/${prefix}-${r}-%04d.NUT"
	list_dest="${output_dir}/${prefix}-${r}.ffconcat"
	log_dest="${output_dir}/${prefix}-${r}.log"
	error_dest="${output_dir}/${prefix}-${r}.errors"
	if $FFMPEG -nostdin -v info -i "$uri" -to "${duration}" -c:v copy -flags +global_header \
		   -f segment -segment_atclocktime 1 -segment_time 600 -segment_list_type ffconcat -segment_list "${list_dest}" \
		   "${file_dest}" &> "$errors"
	then
		((leave_log)) && mv -b "$errors" "${log_dest}"
	else
		mv -b "$errors" "${error_dest}"
	fi
done

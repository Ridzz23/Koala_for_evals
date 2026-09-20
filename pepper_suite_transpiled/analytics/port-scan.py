import sys
import warnings
warnings.filterwarnings('ignore', category=SyntaxWarning)
_arg1 = sys.argv[1] if len(sys.argv) > 1 else ''
_arg2 = sys.argv[2] if len(sys.argv) > 2 else ''
_arg3 = sys.argv[3] if len(sys.argv) > 3 else ''
_arg4 = sys.argv[4] if len(sys.argv) > 4 else ''
_arg5 = sys.argv[5] if len(sys.argv) > 5 else ''
_arg6 = sys.argv[6] if len(sys.argv) > 6 else ''

filename = _arg1
mrt_file = _arg2
annotated = _arg3
file1 = _arg4
file2 = _arg5
as_popularity = _arg6
y = cat filename $| zannotate -routing f"-routing-mrt-file={mrt_file}" "-input-file-type=json" $> f"{annotated}"
y = cat annotated $| jq ".ip" $| tr -d '"' $> f"{file1}"
y = cat annotated $| jq -c ".zannotate.routing.asn" $> f"{file2}"
y = pr "-mts," file1 file2 $| awk "-F," '{ a[$2]++; } END { for (n in a) print n "," a[n] } ' $| sort -k2 -n "-t," -r $> f"{as_popularity}"
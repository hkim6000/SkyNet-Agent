#!/usr/bin/env bash
input="$(cat)"
cwd="$(printf '%s' "$input" | python3 -c 'import json,sys
try:
    print(json.load(sys.stdin).get("cwd",""))
except Exception:
    print("")' 2>/dev/null)"
[ -n "$cwd" ] || cwd="$PWD"
self=$$
skip=" $self "
p=$PPID
while [ -n "$p" ] && [ "$p" != "0" ] && [ "$p" != "1" ]; do
  skip="$skip$p "
  p="$(awk '{print $4}' "/proc/$p/stat" 2>/dev/null)"
done
found=""
while IFS= read -r line; do
  pid="${line%% *}"
  args="${line#* }"
  case "$skip" in *" $pid "*) continue ;; esac
  case "$args" in
    *preview_server.py*|*shots.js*|*readme_shots.js*|*interact*.js*|*capture.js*|*check.js*|*stub_check.sh*|*"dotnet build"*|*"dotnet run"*|*"dotnet test"*|*"dotnet publish"*|*playwright*) ;;
    *) continue ;;
  esac
  pcwd="$(readlink "/proc/$pid/cwd" 2>/dev/null)"
  case "$pcwd/" in "$cwd/"*) ;; *) case "$args" in *"$cwd"*) ;; *) continue ;; esac ;; esac
  found="$found
  $pid  $(printf '%s' "$args" | cut -c1-110)"
done < <(ps -eo pid=,args= 2>/dev/null)
if [ -n "$found" ]; then
  printf 'These processes you started are still running:%s\nWait for them (poll with ps or wait), read their results, stop any server by pid (kill <pid>, never pkill -f), and only then report.\n' "$found" >&2
  exit 2
fi
exit 0

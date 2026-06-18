#!/usr/bin/env bash
set -u

endpoint=${1:-https://loki.linksfoundation.com/reevaluate-graphdb/repositories/art}
directory=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT

printf 'cq\tstatus\trows\n'
for query in "$directory"/cq*.rq; do
    cq=$(basename "$query" .rq)
    if curl -L --max-time 60 -fsS -G \
        -H 'Accept: text/tab-separated-values' \
        --data-urlencode "query@$query" "$endpoint" >"$tmp"; then
        rows=$(awk 'END { print (NR > 0 ? NR - 1 : 0) }' "$tmp")
        status=empty
        [ "$rows" -gt 0 ] && status=answered
    else
        status=error
        rows=0
    fi
    printf '%s\t%s\t%s\n' "$cq" "$status" "$rows"
done

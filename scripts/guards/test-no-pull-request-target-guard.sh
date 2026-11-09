#!/bin/sh
# test-no-pull-request-target-guard.sh -- the guard must go red on each bad form and green on clean ones.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
guard="$here/no-pull-request-target-guard.sh"
tmp=$(mktemp -d)
[ -n "$tmp" ] && [ -d "$tmp" ] || exit 2
trap 'rm -rf "${tmp:?}"' EXIT
fail=0

# expect <name> <want-rc> <dir> [allowlist]
expect() {
  name=$1 want=$2 d=$3 al=${4:-$tmp/none}
  rc=0
  sh "$guard" "$d" "$al" >/dev/null 2>&1 || rc=$?
  if [ "$rc" -ne "$want" ]; then
    echo "FAIL $name: want rc=$want got rc=$rc"
    fail=$((fail + 1))
  else
    echo "ok   $name"
  fi
}

mk() { mkdir -p "$tmp/$1"; }

mk clean;   printf 'on:\n  pull_request:\n    types: [opened]\n' > "$tmp/clean/a.yml"
mk map;     printf 'on:\n  pull_request_target:\n    types: [opened]\n' > "$tmp/map/a.yml"
mk inline;  printf 'on: [push, pull_request_target]\n' > "$tmp/inline/a.yml"
mk expr;    printf "concurrency:\n  x: \${{ github.event_name == 'pull_request_target' }}\n" > "$tmp/expr/a.yaml"
mk comment; printf '# pull_request_target is banned\non:\n  pull_request:\n' > "$tmp/comment/a.yml"
mk empty
mk allowed; printf 'on:\n  pull_request_target:\n' > "$tmp/allowed/closer.yml"
mk allowco; printf 'on:\n  pull_request_target:\njobs:\n  j:\n    steps:\n      - uses: actions/checkout@v4\n' > "$tmp/allowco/closer.yml"
printf 'closer.yml  # metadata only\n' > "$tmp/allow.txt"

expect clean-passes            0 "$tmp/clean"
expect map-form-fails          1 "$tmp/map"
expect inline-form-fails       1 "$tmp/inline"
expect expression-form-fails   1 "$tmp/expr"
expect comment-only-passes     0 "$tmp/comment"
expect zero-files-not-a-pass   2 "$tmp/empty"
expect missing-dir-is-usage    2 "$tmp/nope"
expect allowlisted-passes      0 "$tmp/allowed" "$tmp/allow.txt"
expect allowlisted-checkout    1 "$tmp/allowco" "$tmp/allow.txt"
expect not-allowlisted-fails   1 "$tmp/allowed"

# the repo's own workflows must be clean
repo=$(cd "$here/../.." && pwd)
if [ -d "$repo/.github/workflows" ]; then
  rc=0
  sh "$guard" "$repo/.github/workflows" "$repo/.github/pull-request-target-allowlist.txt" >/dev/null 2>&1 || rc=$?
  if [ "$rc" -ne 0 ]; then echo "FAIL repo-workflows: rc=$rc"; fail=$((fail + 1)); else echo "ok   repo-workflows"; fi
fi

[ "$fail" -eq 0 ] || { echo "$fail failure(s)"; exit 1; }
echo "all passed"

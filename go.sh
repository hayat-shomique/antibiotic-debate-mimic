#!/bin/zsh
# Resume every unfinished arm. Each pass skips what is already on disk.
#
# Every arm runs under a lock. On 19 Aug two matched_pass processes ran against
# the same output file and wrote every exposure twice, which would have doubled n
# and halved the standard errors of the headline. The lock refuses the second
# process instead of letting it interleave.
cd ~/brain_run
PY=/Users/shamzzzh/.claude-science/conda/envs/brain/bin/python
mkdir -p .locks

run_once () {
  local name=$1; shift
  local lock=.locks/$name.pid
  if [[ -f $lock ]] && kill -0 $(cat $lock) 2>/dev/null; then
    echo "  $name already running as PID $(cat $lock), skipping"
    return 0
  fi
  echo "  starting $name"
  $PY "$@" &
  local pid=$!
  echo $pid > $lock
  wait $pid
  local rc=$?
  rm -f $lock
  [[ $rc -ne 0 ]] && echo "  $name exited with code $rc"
  return 0
}

echo "=== resuming $(date +%H:%M) ==="
run_once matched     matched_pass.py --per-drug 25 --receiver A
run_once calibration calibration_pass.py
run_once fewshot     fewshot_pass.py
echo "=== all arms complete $(date +%H:%M) ==="
echo "=== rebuilding the single source of truth ==="
$PY canonical_numbers.py

# 샌드박스 안에서 실행한다: openshell sandbox exec -n rl-triage --env HOME=/tmp -- bash -c "$(cat run_entry.sh)" </dev/null
# 출력 폴더는 매번 새로 만든다(--out은 아직 없는 폴더여야 한다).
set -u
cd /sandbox/app
RUN=/tmp/n35_c03_$(date +%Y%m%dT%H%M%S)
mkdir -p "$RUN"
cat > "$RUN/task_c03.json" <<'JSON'
{"schema": "nemotron35_task_context_v1", "task": "Isaac-Velocity-Flat-Unitree-Go2-v0", "observed_problem": "Training run c03 failed its gate."}
JSON
echo "## prepare-only -> $RUN/prepare"
python -m rl_triage.nemotron35_entry_v1 --run-dir /sandbox/workspace/cases/c03 --task-context "$RUN/task_c03.json" --out "$RUN/prepare" --prepare-only
echo "## prepare exit=$?"
echo "## execute -> $RUN/execute"
python -m rl_triage.nemotron35_entry_v1 --run-dir /sandbox/workspace/cases/c03 --task-context "$RUN/task_c03.json" --out "$RUN/execute" --execute
echo "## execute exit=$?"
echo "## files"
cd "$RUN/execute" && find . -type f | sort

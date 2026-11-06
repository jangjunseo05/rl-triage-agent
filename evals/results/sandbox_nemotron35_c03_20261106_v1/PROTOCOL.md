# 사전등록: OpenShell 샌드박스 안 Nemotron 3.5 입구 실행 (사례 c03, 2026-11-06)

실행 전에 커밋한다. 이 실행은 성능 평가가 아니다. 결선 시점에 정책이 적용된 샌드박스 안에서 에이전트 한 세션이 끝까지 도는지 기록한다.

## 9/27 예선 기록과 다른 점

- 예선(`evals/results/sandbox_run_c03_prereg.json`): `configs/triage_workflow.yml`, 모델 `nvidia/nemotron-3-super-120b-a12b`, 도구 6개, 변경 목록을 주는 과제 A 입구.
- 이번: `python -m rl_triage.nemotron35_entry_v1`, `configs/triage_nemotron35_v1.yml`, 모델 `nvidia/nemotron-3.5-super-vl-120b-a12b`, grounded 도구 5개, 정상 기준 없음(`reference_status: absent`).
- 같은 사례 ID(c03)의 telemetry를 쓰지만 같은 실험이 아니다. 결과를 예선과 비교해 우열을 말하지 않는다.

## 고정하는 것

- 이미지: `docker/Dockerfile.sandbox`에 `evals/grounded_active_model_call.py` 한 파일만 더한 베이스 → `scripts/sandbox_up.sh 42`. 이미지 ID를 기록한다.
- 이미지가 바뀌었으므로 실행 전에 커널 시험 8개(`tests/sandbox`)를 다시 돌린다. 8 passed가 아니면 에이전트 실행을 하지 않는다.
- 입력: `--run-dir /sandbox/workspace/cases/c03`, task context `{"schema": "nemotron35_task_context_v1", "task": "Isaac-Velocity-Flat-Unitree-Go2-v0", "observed_problem": "Training run c03 failed its gate."}` (`sandbox_rerun_20261106_v1/nemotron35_c03_prepare.log`와 같음).
- 명령: `--prepare-only` 다음 `--execute`, 출력은 샌드박스 안 새 `/tmp` 폴더. 끝난 뒤 `entry_report.json`, `execution/record.json`, 저장된 assessment를 꺼내 이 폴더에 둔다.
- 재시도: `docs/NEMOTRON35-ENTRY.md`대로 하지 않는다. 인프라 오류(과부하·빈 응답·잘림, AGENTS.md)일 때만 새 출력 폴더로 한 번 다시 실행하고, 첫 시도도 남긴다.

## 판정

- 성공: `execution/record.json`의 상태가 `hypotheses_only`이고, LLM 호출 수가 1 이상 기록되고, assessment 파일이 저장됨.
- 그 밖(`HOLD`·`invalid`·오류)은 실패로 그대로 기록한다.
- 출력에서 키 문자열이 발견되면(entry의 검사) invalid다. 공개 사본에는 키·계정 ID를 넣지 않는다.

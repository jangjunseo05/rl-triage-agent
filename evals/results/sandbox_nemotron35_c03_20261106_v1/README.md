# OpenShell 샌드박스 안 Nemotron 3.5 입구 실행 (사례 c03, 2026-11-06)

사전등록 [PROTOCOL.md](PROTOCOL.md)는 실행 전에 커밋 `1c11463`으로 고정했다. 이미지 수정은 커밋 `d8d1c0e`이다. 이 실행은 성능 평가가 아니다. 9/27 예선 c03 실행(`configs/triage_workflow.yml`, 3 Super)과는 입구·모델·도구가 다르다.

로그 머리줄 시각은 KST, 샌드박스 안 JSON의 시각은 UTC다.

## 결과

| 단계 | 결과 | 파일 |
|---|---|---|
| 베이스 이미지 재빌드(`evals/grounded_active_model_call.py` 포함) | 성공, 498초 | `base_image_build.log` |
| `scripts/sandbox_up.sh 42` | 성공, 마지막 줄 cases 10 | `sandbox_up.log` |
| 커널 시험(이미지가 바뀌어 다시 실행) | **8 passed in 1.71s** | `sandbox_kernel_tests.txt` |
| 앱 코드 쓰기 | OpenShell 안 거부, OpenShell 없는 docker에서 허용 | `app_code_write_check.txt` |
| 3.5 입구 `--prepare-only` | 성공, `ready_for_execute: true` | `entry_run.log` |
| 3.5 입구 `--execute` | **HOLD** (`workflow_failed`). LLM 호출 4회, 토큰 46,450, 벽시계 33.6초. assessment 저장 없음 | `entry_run.log`, `execute/execution/record.json` |

사전등록 판정 기준(`hypotheses_only`, 호출 1회 이상, assessment 저장)에 따라 이 실행은 **실패**다. 인프라 오류(과부하·빈 응답·잘림)가 아니므로 다시 실행하지 않았다.

## 샌드박스 안에서 일어난 일

`execute/execution/trace.jsonl`(SHA-256 `4a5bdaef…3cb8`, `record.json`의 `trace_sha256`과 같음)의 도구 호출 12개:

1. `grounded_active_registry` 1회, `grounded_evidence_group_index` 1회
2. `grounded_evidence_group_page` 8회. 실행 검증기의 한도는 2회다(`evals/grounded_active_model_call.py`의 `TOOL_LIMITS`). `record.json`에 `budget_valid: false`로 남았다.
3. `grounded_evidence_details` 1회
4. `write_grounded_active_assessment` 1회 → 거절: `등록되지 않은 read-only next check입니다: grounded_active_v1`

거절 이유: 저장 규칙(`src/rl_triage/grounded_evidence.py` `_checked_next_check`)은 `next_check.registry_id`가 registry의 `checks` 아래 검사 키(예: `runtime_com_state`) 중 하나이기를 요구한다. 모델은 registry 전체의 ID `grounded_active_v1`을 넣었다. 설정이 `handle_tool_errors: false`라서 이 거절이 workflow 오류(`ValueError`)로 끝났고, 입구가 `HOLD`를 기록했다.

정리하면, 샌드박스 안에서 모델 호출·도구 실행·근거 선택 저장(`execute/workspace/preregistrations/evidence_selections/`)까지는 동작했다. 마지막 사전등록 저장이 등록 규칙에 걸려 거절됐다. 원인 확정·검사 승인·실행은 이 입구가 하지 않는다(`record.json`의 `claims`, `check_execution`).

## 앱 코드 쓰기 차단 (추가 관찰)

- 이미지의 `/sandbox/app` 파일은 모드 777이다(Windows 마운트에서 빌드한 결과로 보인다. 예선 이미지의 모드는 확인하지 않았다).
- OpenShell 안에서는 `/sandbox/app/src/rl_triage/triage_tools.py`에 덧붙이기가 `Permission denied`로 막혔다. 정책 `policies/triage_agent.yaml`의 `read_only`에 `/sandbox/app`이 있다.
- 같은 이미지를 OpenShell 없이 docker로 띄우면(uid 1001) 같은 쓰기가 허용된다(`app_code_write_check.txt`에는 이 docker 이미지 ID를 남기지 않았다). 파일 권한 수준에서는 OpenShell 정책만 이 쓰기를 막았다. 3.5 입구의 도구 5개에는 셸·코드 실행·앱 쓰기 경로가 없으므로(`configs/triage_nemotron35_v1.yml`) 도구 표면은 별도의 방어층이다. 확인한 것은 uid 1001의 파일 하나 덧붙이기뿐이다. 해시 전후를 잰 사전등록 측정은 `../sandbox_app_write_20261106_v1/`에 있다.
- 근본 원인은 모드 777이다. `docker/Dockerfile.sandbox`의 `chmod -R a+rX`는 쓰기 권한을 더하지도 빼지도 않는다. 빌드 때 쓰기 권한을 빼는 것은 후속 과제로 남긴다.

## 꺼낸 파일

`execute/` 아래 파일 6개는 샌드박스 안 `/tmp/n35_c03_20261106T111644/execute`에서 `cat`으로 꺼냈다. 해시는 `execute_manifest.txt`에 있다. 꺼낼 때 샌드박스 안 원본과 비교했지만 그 출력은 남기지 않았다(manifest 1행). 꺼내지 않은 파일 3개(입력 telemetry 복사본, absent reference, task context)와 그 이유도 manifest에 적었다. 유출 검색 결과는 `leak_scan.txt`(0건)다.

## 재현

```bash
# WSL, 이 폴더에서. 앞 단계는 ../sandbox_rerun_20261106_v1/README.md 따라 하기
openshell sandbox exec -n rl-triage --env HOME=/tmp -- bash -c "$(cat run_entry.sh)" </dev/null
```

## 바꾸지 않은 것

- `docs/TROUBLESHOOTING.md`. 팀원 작업과 겹치지 않게, 이 실행의 기록 연결은 결선 뒤로 미룬다. 이 README가 공개 재현 기록이다.

- 모델 지시·도구·`registry_id` 필드 이름. 이름이 registry ID와 검사 키를 혼동하게 만들 수 있지만, 바꾸면 도구 변경이라 평가 전 커밋 규칙(AGENTS.md)을 따로 따라야 한다.
- 재실행. 같은 입력을 다시 보내 성공할 때까지 고르는 것은 사전등록의 재시도 규칙에 어긋난다.

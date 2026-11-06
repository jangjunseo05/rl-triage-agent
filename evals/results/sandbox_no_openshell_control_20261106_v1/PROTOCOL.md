# 대조 실험 사전등록: OpenShell 없이 같은 이미지에서 커널 경계 시험 8개

실행 전에 커밋한다. 질문: `tests/sandbox`의 8개 시험 중 어느 것이 OpenShell(Landlock·네트워크 정책) 없이도 통과하는가.

## 조건

- 이미지: `rl-triage-ws:seed42`. `sandbox_rerun_20261106_v1`에서 `scripts/sandbox_up.sh 42`가 만든 것과 같은 이미지이고, 실행 기록에 이미지 ID를 남긴다.
- 사용자: uid 1001(`sandbox`). OpenShell 샌드박스 안 작업 프로세스와 같다(`id -u` → 1001, 2026-11-06 확인).
- 명령은 같다: `cd /sandbox/app && OPENSHELL_SANDBOX=1 python -m pytest -q -p no:cacheprovider -rA tests/sandbox`
- C1: `docker run --rm --user 1001:1001 rl-triage-ws:seed42 …` (Docker Desktop 기본 bridge 네트워크)
- C2: C1에 `--network none`을 더한다.

## 예측 (실행 전)

| 시험 | C1 | C2 | 근거 |
|---|---|---|---|
| test_cannot_write_reference_params | 통과 | 통과 | 파일이 root 소유 755라 uid 1001은 쓰지 못한다(`docker/Dockerfile.workspace`) |
| test_cannot_write_case_telemetry | 통과 | 통과 | 위와 같음 |
| test_can_write_scratch_only | 통과 | 통과 | scratch는 sandbox 소유 |
| test_can_write_diagnosis | 통과 | 통과 | preregistrations/diagnoses는 sandbox 소유 |
| test_cannot_write_workspace_root | 통과 | 통과 | `/sandbox/workspace`가 root 소유 755 |
| test_cannot_read_outside_policy | **실패** | **실패** | `/home`은 755라 일반 권한으로 읽힌다. OpenShell에서는 Landlock이 막는다 |
| test_exfiltration_host_blocked | **실패** | 통과 | bridge 네트워크에서는 huggingface.co에 접속된다. `--network none`에서는 DNS·연결 실패라 `pytest.raises(Exception)`이 통과한다 |
| test_cloud_metadata_blocked | 통과(불확실) | 통과 | Docker Desktop에는 169.254.169.254 메타데이터 서비스가 없어 연결 실패(OSError)가 예상된다 |

예측이 맞으면 C1은 6 passed·2 failed, C2는 7 passed·1 failed다. 이 결과는 "8개 통과" 가운데 파일 소유권이나 네트워크 부재만으로도 통과하는 시험이 있다는 뜻이다. OpenShell 정책을 따로 보여 주는 시험은 C1 기준으로 `/home` 읽기 차단과 외부 호스트 차단이다.

## 기록

`run_C1.txt`, `run_C2.txt`에 명령 원문, 이미지 ID, 시각, pytest `-rA` 출력을 남긴다. 예측과 다른 결과도 그대로 적는다.

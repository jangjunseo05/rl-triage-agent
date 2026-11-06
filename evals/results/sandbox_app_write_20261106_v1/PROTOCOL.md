# 사전등록: 에이전트 도구 코드 쓰기, OpenShell 안과 밖 (2026-11-06)

실행 전에 커밋한다. 질문: 같은 이미지에서 uid 1001 프로세스가 `/sandbox/app/src/rl_triage/triage_tools.py`(에이전트 도구 코드)를 고칠 수 있는가. 이 경계를 막는 것이 OpenShell 정책뿐인가.

## 배경

`../sandbox_nemotron35_c03_20261106_v1/app_code_write_check.txt`에서 이미지의 앱 파일 모드가 777이고, OpenShell 밖 docker에서는 덧붙이기가 허용되는 것을 관찰했다. 이 실험은 해시 전후 비교로 이것을 측정한다.

## 조건

- 이미지: 아래 회귀 시험 파일을 포함해 다시 만든 `rl-triage-ws:seed42`. 실행 기록에 이미지 ID를 남긴다.
- O: `openshell sandbox exec -n rl-triage -- python - < probe.py`. 샌드박스는 `policies/triage_agent.yaml`(`read_only`에 `/sandbox/app`)을 적용한 상태다.
- D: `docker run --rm -i --user 1001:1001 rl-triage-ws:seed42 python - < probe.py`(OpenShell 없음)
- D0: D 다음에 새 컨테이너로 같은 파일의 SHA-256만 계산한다. D의 쓰기가 버려지는 컨테이너 안에서만 일어났는지 확인하는 단계다.
- `probe.py`: 전 SHA-256 → `open(…, "ab")`로 한 줄 덧붙이기 시도 → 예외·errno → 후 SHA-256.

## 예측

| 조건 | append | 예외 | 해시 |
|---|---|---|---|
| O | denied | `PermissionError`, `EACCES` | 변하지 않음 |
| D | allowed | 없음 | 변함 |
| D0 | — | — | O의 전 해시와 같음(이미지 불변) |

## 회귀 시험 (별도 집계)

`tests/sandbox/test_app_code_boundary.py`를 추가한다. 파일을 덧붙이기 모드로 **열기만** 하고 쓰지는 않는다. 그런 다음 `PermissionError`와 `errno == EACCES`, 해시 불변을 확인한다.

기존 8개(`tests/sandbox/test_kernel_boundary.py`) 결과와 섞지 않고 따로 실행·집계한다. 예측: O에서 통과, D에서 실패.

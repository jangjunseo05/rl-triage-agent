# 에이전트 도구 코드 쓰기: OpenShell 안과 밖 (2026-11-06)

사전등록 [PROTOCOL.md](PROTOCOL.md)와 `probe.py`, 회귀 시험 `tests/sandbox/test_app_code_boundary.py`는 실행 전에 커밋 `9f93cd8`로 고정했다. 이미지는 그 커밋으로 다시 만들었다(`base_image_build.log`, `sandbox_up.log`). 이미지 ID는 `sha256:09c3eac1…039f`다.

## 결과 (`probe_results.txt`)

| 조건 | append | 예외 | SHA-256 전 → 후 | 예측과 |
|---|---|---|---|---|
| O: OpenShell 샌드박스(`policies/triage_agent.yaml`) | denied | `PermissionError`, `EACCES` | `c5a63aff…a9af` → 같음 | 일치 |
| D: 같은 이미지, docker, uid 1001, OpenShell 없음 | allowed | 없음 | `c5a63aff…a9af` → `bc113e41…dfb8` | 일치 |
| D0: D 다음 새 컨테이너 | — | — | `c5a63aff…a9af` | 일치(이미지 불변, D의 쓰기는 버린 컨테이너 안에서만) |

대상 파일은 `/sandbox/app/src/rl_triage/triage_tools.py`(에이전트 도구 코드)다. 이미지 안 모드는 777이다(`../sandbox_nemotron35_c03_20261106_v1/app_code_write_check.txt`).

## 회귀 시험 (별도 집계, `regression_test.txt`)

| 환경 | `tests/sandbox/test_app_code_boundary.py` |
|---|---|
| OpenShell | **1 passed** |
| docker(OpenShell 없음) | 1 failed |

이 시험은 파일을 덧붙이기 모드로 열기만 하고 쓰지 않는다. 기존 커널 시험 8개(`test_kernel_boundary.py`)와 합산하지 않는다. 다만 앞으로 `pytest tests/sandbox`를 실행하면 두 파일이 같이 돌아 9개로 집계된다.

## 해석

- 이 이미지에서는 파일 권한이 에이전트 도구 코드를 지키지 못한다(모드 777). **일반 uid 1001 프로세스**(`python -`)의 쓰기를 OpenShell 정책(`read_only: /sandbox/app`)이 막았다.
- 같은 날 OpenShell이 있어야만 막힌 경계는 셋이다. 대조 실험의 `/home` 읽기와 외부 호스트(이미지 `619efd5…`, `../sandbox_no_openshell_control_20261106_v1/`), 이 실험의 도구 코드 쓰기(이미지 `09c3eac…`)다. 도구 코드 쓰기 경계는 이 이미지의 파일이 777이기 때문에 OpenShell에만 의존한다. 빌드에서 쓰기 권한을 빼면 파일 권한으로도 막힐 것으로 보지만 확인하지 않았다.
- 범위: uid 1001, 파일 하나, 덧붙이기 한 번. 다른 쓰기 방식(이름 바꾸기, 삭제, 새 파일)과 root 실행은 시험하지 않았다.
- 에이전트가 쓴 코드가 이 쓰기를 할 수 있다는 근거는 아니다. 과제 A 설정의 `run_analysis`는 에이전트 Python을 실행하기 전에 자체 Landlock을 건다(`src/rl_triage/triage_tools.py` 184~224행, 기본 `TRIAGE_ANALYSIS_SANDBOX=auto`). 읽기는 Python 설치 경로와 시스템 경로, 쓰기는 scratch만 허용한다. 이 층은 OpenShell과 별개이고, 이번에 `run_analysis`를 거친 시도는 하지 않았다. 3.5 입구의 도구에는 코드 실행 경로가 없다(`configs/triage_nemotron35_v1.yml`).
- 근본 원인인 777 모드는 빌드 문제다. 빌드 때 쓰기 권한을 빼는 것은 후속 과제로 남기고, 이번에는 이미지를 바꾸지 않았다.

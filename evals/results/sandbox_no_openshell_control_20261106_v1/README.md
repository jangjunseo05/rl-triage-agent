# 대조 실험: OpenShell 없이 같은 이미지에서 커널 경계 시험 8개 (2026-11-06)

사전등록 [PROTOCOL.md](PROTOCOL.md)는 실행 전에 커밋 `4f2899c`로 고정했다. 비교 대상은 같은 날 OpenShell 샌드박스 안 결과 `8 passed`(`../sandbox_rerun_20261106_v1/sandbox_kernel_tests.txt`)다.

## 결과

| 시험 | OpenShell | C1 docker(bridge) | C2 docker(`--network none`) | 예측과 |
|---|---|---|---|---|
| test_cannot_write_reference_params | 통과 | 통과 | 통과 | 일치 |
| test_cannot_write_case_telemetry | 통과 | 통과 | 통과 | 일치 |
| test_can_write_scratch_only | 통과 | 통과 | 통과 | 일치 |
| test_can_write_diagnosis | 통과 | 통과 | 통과 | 일치 |
| test_cannot_write_workspace_root | 통과 | 통과 | 통과 | 일치 |
| test_cannot_read_outside_policy | 통과 | **실패** | **실패** | 일치 |
| test_exfiltration_host_blocked | 통과 | **실패** | 통과 | 일치 |
| test_cloud_metadata_blocked | 통과 | 통과 | 통과 | 일치 |
| 합계 | 8 passed | 6 passed, 2 failed | 7 passed, 1 failed | |

원문: `run_C1.txt`, `run_C2.txt`. 두 파일의 머리줄에 이미지 ID와 명령이 있다.

## 같은 동작의 예외 비교

같은 검사 스크립트 `network_detail_probe.py`를 두 환경에서 실행했다(`network_detail_openshell.txt`, `network_detail_docker.txt`).

| 동작 | OpenShell | docker(bridge) |
|---|---|---|
| `169.254.169.254:80` 연결 | `PermissionError [Errno 13]` | `ConnectionRefusedError [Errno 111]` |
| `https://huggingface.co` 요청 | `URLError … [Errno 13] Permission denied` | `HTTP 200` |
| `os.listdir("/home")` | `PermissionError [Errno 13]` | `['ubuntu', 'sandbox']` |

## 해석

- 8개 중 5개(쓰기 차단 3개, 쓰기 허용 2개)는 OpenShell 없이도 같은 결과다. 이미지의 파일 소유권(`docker/Dockerfile.workspace`: 데이터는 root 소유, scratch·사전등록만 sandbox 소유)과 uid 1001만으로 설명된다. 이 5개는 OpenShell 정책의 효과를 따로 보여 주지 않는다.
- 클라우드 메타데이터 시험은 이 PC의 docker에서도 통과한다. 메타데이터 서비스가 없어 연결이 거부되기 때문이다. OpenShell에서는 거부 이유가 정책(Errno 13)이다. 시험은 `OSError`만 확인해서 둘을 구분하지 못한다.
- 외부 호스트 시험은 `pytest.raises(Exception)`이라 네트워크가 없을 때(C2)도 통과한다.
- OpenShell이 있어야만 통과하는 시험은 C1 기준으로 2개다: 정책 밖 읽기 차단(`/home`), 외부 호스트 차단(`huggingface.co`).
- 따라서 "8 passed"는 정책 적용 환경에서 8개 경계가 기대대로 동작했다는 기록이다. 8개 모두가 OpenShell만의 효과라는 근거는 아니다.

## 시험을 강화하려면 (이번에 바꾸지 않음)

- 네트워크 두 시험은 예외 종류 대신 `errno == errno.EACCES`(Errno 13)를 확인하면 정책 차단과 연결 실패를 구분할 수 있다. 위 비교에서 OpenShell은 세 동작 모두 Errno 13을 냈다.
- 쓰기 차단 시험은 root로 실행하는 변형을 두면, 파일 소유권과 Landlock 차단을 구분할 수 있다. 이번에는 실행하지 않았다.

## 실행하지 않은 것

- root 사용자로 실행하는 변형
- 이 PC 밖(메타데이터 서비스가 있는 클라우드 VM)에서의 메타데이터 시험

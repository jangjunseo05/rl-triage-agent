# RL Triage Agent

**실패한 로봇 정책의 원인을 조사하고, 교정을 고르거나 제약된 코드 패치를 생성한 뒤, Isaac Lab에서 회복을 검증합니다.**

[리플레이 보기](https://mmporong.github.io/rl-triage-agent/replay/) · [아키텍처](https://mmporong.github.io/rl-triage-agent/?view=single-dark) · [빠른 시작](#빠른-시작) · [English](README.en.md)

| 카탈로그 항목 | 값 |
| --- | --- |
| 설명 | 승인된 검사와 고정 평가를 사용한, 근거 기반 Isaac Lab 강화학습 실패 조사. |
| 산업 분야 | Physical AI |
| 요구 사항 | Python + `uv`; 모델 호출용 NVIDIA API; 시뮬레이션용 Isaac Lab이 설치된 RTX 호스트. 샌드박스 경로에는 Docker + OpenShell. |
| OpenShell | 0.1.1 |
| 컬렉션 | Hackathon · Mollet |
| 결과 | NVIDIA Korea Agentic AI Hackathon 2026 최종 결선 TOP 5 (Team Mollet). 2026년 11월 10일 NVIDIA AI Day Seoul 2026에서 발표. [상장](https://mmporong-portfolio.vercel.app/nvidia-award) |

## 첫 교정으로 충분하지 않을 때

Go2 개발 seed 2311에서 Nemotron 3.5는 보상 좌표계(reward-frame) 결함과 PPO epoch 결함이 겹친 사례에 대해 검사를 선택했습니다. 보상 교정 뒤에도 추종 실패가 남았습니다. 두 번째 진단에서 옵티마이저 갱신 검사를 선택했고, 이 검사는 **기대 20회 대비 4회**의 갱신 단계를 측정했습니다. 호스트가 등록된 epoch 복원을 적용하고 회복을 검증했습니다.

| 정책 단계 | 추종 RMSE, m/s | Fixed26 결과 |
| --- | ---: | --- |
| 복합 결함 | 1.219 | 회복 안 됨 |
| 보상 좌표계 교정 | 1.163 | 후속 진단 필요 |
| 보상 + PPO epoch 교정 | **0.142** | **회복** |

두 번의 진단 라운드에 걸친 검사 4개는 모두 Nemotron이 골랐습니다. 호스트는 등록된 교정을 적용하고 재학습·평가했으며, 교정된 학습에서는 갱신마다 옵티마이저 단계가 20회로 기록됐습니다. [검사, 교정, 평가](docs/NEW-LINEAGE-COMPARISON.md#갱신-계측을-연결한-새-복합-사례) · [원본 결과](evals/results/runtime_observation_compound_s2311_20261031_v1/summary.json).

## 계단 내려가기: 적응 전과 후

Nemotron 3.5가 안정성 검사를 선택하고 등록된 정책 적응을 제안했습니다. 같은 0.25m/s 명령에서 원래 Go2 정책은 뒤집혔고, 적응된 정책은 등록된 30초 계단 과제를 통과했습니다.

<a href="docs/media/go2-stairs-agent-adaptation-s200-20261106-v3/comparison-15s-1080p.mp4"><img src="docs/media/go2-stairs-agent-adaptation-s200-20261106-v3/comparison-15s-preview.webp" alt="같은 명령 속도에서 에이전트가 제안한 적응 전후의 Go2 계단 내려가기" width="100%"></a>

*원래 속도의 15초, 개발 평가 seed 200. 왼쪽: 원래 정책. 오른쪽: 에이전트가 제안한 적응 후. 30초 전체 기록에서 뒤집힘 표본은 888→0, 추종 RMSE는 0.233→0.064m/s였습니다. [1080p 영상](docs/media/go2-stairs-agent-adaptation-s200-20261106-v3/comparison-15s-1080p.mp4) · [검사, 적응, 과제 평가](docs/GO2-STAIRS-AGENT-ADAPTATION.md).*

Nemotron 3.5는 PPO 설정 패치도 직접 작성했고, CPU 피드백을 받은 뒤 이를 수정했습니다. 기록된 이 수정본은 추가 개발 seed 두 개에서 고정 평가를 통과했습니다. [생성 패치와 회복](docs/GENERATED-PPO-PATCH.md) · [15초 수정본 비교](docs/media/rewritten-config-patch-s5753-20261106-v1/comparison-15s.mp4).

다른 녹화: [복합 결함 수리](docs/media/five_type_recovery_s5557_20261102_v1/comparison.mp4) · H1 사전학습 재생 [오르기](docs/media/stairs_h1_s172_20261030_v1/biped-stairs-up/video/rl-video-step-0.mp4) / [내리기](docs/media/stairs_h1_s172_20261030_v1/biped-stairs-down/video/rl-video-step-0.mp4). H1 영상은 재생 참고용입니다.

## 동작 방식

1. **관측:** 연결된 학습 기록, 과제 맥락, 사용 가능한 프레임을 읽습니다.
2. **선택:** Nemotron이 등록된 검사를 고르고 근거 ID를 인용합니다.
3. **검사:** 호스트가 승인을 확인하고 검사를 실행한 뒤 영수증(receipt)을 돌려줍니다.
4. **생성, 교정 또는 적응:** 원인이 확인되면 등록된 교정이나 모델이 작성한 PPO 어댑터 패치를 허용합니다. CPU 검사가 실패하면 패치를 한 번 수정할 수 있고, 검사가 정상이면 패치 경로를 멈춥니다. 별도의 과제 계약이 있으면 정책 적응을 허용할 수 있습니다.
5. **평가:** 호스트가 학습한 뒤, 결과 정책에 같은 고정 평가를 적용합니다.

모델은 행동을 고르고, 호스트는 실행 인자를 제공하며 권한을 확인합니다. 각 승인은 한 번만 쓰입니다. 지원하지 않는 원인이거나 모델 응답이 계속 유효하지 않으면, 현재 3.5 결함 수리 경로에서는 **HOLD**로 끝납니다. 다른 등록 버전은 규칙 기반 대체 경로를 기록할 수 있습니다. 교정 뒤에도 남은 실패는 두 번째 진단 라운드로 조사할 수 있습니다.

| 구성 요소 | 역할 |
| --- | --- |
| Nemotron 3.5 Super VL | 현재 진단, 검사 선택, 적응 및 제한된 PPO 패치 제안, 보조 프레임 관측. 동결된 실험에는 Nemotron 3 Super가 그대로 남아 있습니다. |
| NeMo Agent Toolkit 1.9 | 구성된 도구 워크플로와 평가 진입점. 일부 실험은 별도 호스트 컨트롤러를 사용합니다. |
| OpenShell 0.1.1 + prover | 파일/네트워크 제한과 키 주입. v2 분석 진입점은 범위가 제한된 도구와 타입이 지정된 검사 ID를 추가합니다. [근거](docs/BOUNDED-AGENT-SECURITY.md). |
| Isaac Lab 2.1.1 / Isaac Sim 4.5 | 시뮬레이션, 프로브, 학습, 고정 평가, 녹화. |
| NVIDIA Skills | Isaac Lab 조사·교정 체크리스트. `skills/isaaclab-rl-triage` 참고. |

## 기록된 결과

| 시험 | 관측 결과 | 근거 |
| --- | --- | --- |
| 생성 PPO 패치 루프 | CPU 피드백으로 한 번 수정한 뒤, 기록된 수정본이 개발 seed 5753/5754를 회복: 추종 RMSE **1.176→0.145 / 1.177→0.145m/s**, 갱신당 옵티마이저 단계 **4→20**. 정상 대조군 두 개는 모두 보존됐습니다. | [패치, 검사, 회복](docs/GENERATED-PPO-PATCH.md) |
| 후속 진단과 수리 | 위의 3.5 seed 2311 사례는 두 번째 진단 라운드와 등록 교정 뒤 회복했습니다. 이전의 복합 결함 seed 2120/2121도 교정 두 번 뒤 회복했습니다. | [3.5 사례](docs/NEW-LINEAGE-COMPARISON.md#갱신-계측을-연결한-새-복합-사례) · [잔여 진단](docs/RESIDUAL-DIAGNOSIS-RESULT.md) |
| 같은 명령에서의 계단 적응 | 개발 seed 200: 뒤집힘 표본 **888→0**, 추종 RMSE **0.233→0.064m/s**; 30초 과제가 실패에서 통과로 바뀜. | [계단 적응](docs/GO2-STAIRS-AGENT-ADAPTATION.md) |
| 등록된 보상·모터 결함 | 새 seed 실행 4건이 회복했습니다. 모터 사례에서는 검사 3개가 처음의 보상 가설을 뒤집고 액추에이터 원인을 확인했습니다. | [end-to-end 수리](docs/E2E-REWARD-DEMO.md) |
| 로봇·교정 범위 전이 | ANYmal-C seed 2047이 회복했습니다. 범위를 넓힌 U1 교정은 seed 2051/2062를 회복했으며, 모델이 선택한 실행과는 따로 평가했습니다. | [ANYmal-C](docs/ANYMAL-C-PORT.md) · [U1](docs/U1-SCOPE-EXTENSION.md) |

결과는 등록된 과제와 실행 단위로 보고합니다. 연결된 근거에는 프로토콜, 모델 응답, 학습 영수증, 고정 평가가 포함됩니다. [모델 비교](docs/NEMOTRON35-VALUE-COMPARISON.md), [VL 검사](docs/VISUAL-INTEGRITY-OBSERVER.md), [정상 입력 시험](docs/T2-NO-INTERVENTION.md)도 참고하세요.

## 빠른 시작

기록된 데이터 리플레이부터 시작하세요. 모델 API나 GPU를 쓰지 않으며, 새로 조사를 실행하는 대신 저장된 결과를 다시 계산합니다.

```bash
git clone https://github.com/mmporong/rl-triage-agent.git "$HOME/rl-triage-agent"
cd "$HOME/rl-triage-agent"
uv sync
uv run python evals/replay.py evals/results/blind_v1 evals/results/heldout_blind \
  evals/results/heldout_changes --traces evals/results/traces
```

기존 학습 실행이 있다면, CPU에서 Nemotron 3.5용 근거 패킷을 준비합니다.

```bash
export RUN_DIR="$HOME/isaaclab/logs/rsl_rl/<run>"
uv run python bench/extract_tb.py "$RUN_DIR" "$RUN_DIR/telemetry.json"
cat > /tmp/triage-task.json <<'JSON'
{"schema":"nemotron35_task_context_v1","task":"Isaac-Velocity-Rough-Go2-v0","observed_problem":"The trained policy does not follow velocity commands."}
JSON
uv run python -m rl_triage.nemotron35_entry_v2 \
  --run-dir "$RUN_DIR" --task-context /tmp/triage-task.json \
  --out "$PWD/workspace/nemotron35-prepare" --prepare-only
```

준비 단계에서는 모델을 호출하지 않고, 프로브나 학습도 허가하지 않습니다. 출력 디렉터리는 한 번만 쓸 수 있습니다. 등록된 조사·승인·실행·상태 명령은 [CLI 가이드](docs/REGISTERED-DIAGNOSTIC-RUNTIME.md)에 정리되어 있습니다.

<details>
<summary>모델 평가 요청하기</summary>

기존 로컬 비밀 저장소에서 NVIDIA 키를 불러온 뒤, 새 출력 디렉터리를 사용합니다.

```bash
. "$HOME/.config/nvidia/env"
uv run python -m rl_triage.nemotron35_entry_v1 \
  --run-dir "$RUN_DIR" --task-context /tmp/triage-task.json \
  --out "$PWD/workspace/nemotron35-execute" --execute
```

이 명령은 가설과 다음 검사 제안을 요청합니다. 프로브 실행, 교정, 학습, 회복 평가는 각각 기록되는 별도 단계가 필요합니다.

</details>

## 실행과 검증

검증한 환경: Windows 11 + WSL2 Ubuntu 24.04, RTX 3060 12GB, Isaac Lab 2.1.1 / Sim 4.5.0. Mollet이 관리하는 해커톤 프로토타입입니다.

호스트의 모델 호출은 텔레메트리 요약, 제공된 설정 정보, 선택적으로 샘플링한 프레임을 NVIDIA API로 보냅니다. OpenShell은 샌드박스 경로에 파일/네트워크 제한과 키 주입을 제공하고, 호스트 컨트롤러는 자체 승인 기록과 영수증을 확인합니다. [정책 파일](policies/)과 [샌드박스 설정](docs/GROUNDED-SINGLE-RUN.md)을 참고하세요.

```bash
uv run python evals/prove_policies.py
uv run python evals/correct_v2.py replay
uv run python evals/build_replay_page.py --check
```

정책 증명에는 `openshell-prover`가 필요하며, Windows에서는 WSL Ubuntu를 통해 사용합니다. prover를 쓸 수 없으면 종료 코드 1로 끝나고 저장된 증명 결과는 보존됩니다. CPU 클린 클론 검사와 사전 요구 사항은 [재현 가이드](docs/WINDOWS-CLEAN-CLONE-REPRODUCTION.md)를 참고하세요.

이 명령들은 권한 증명, 저장된 교정 기록, 공개 리플레이 데이터를 확인합니다. 새 학습을 시작하지는 않습니다. 실시간 샌드박스 커널 검사에는 샌드박스 환경이 필요합니다. [파이프라인 사전 점검](docs/PIPELINE-PREFLIGHT.md)과 [워크플로 설정](docs/AGENTIC-INVESTIGATION.md)을 참고하세요.

## 근거와 구현

| 주제 | 자세히 보기 |
| --- | --- |
| 진단과 검사 | [근거 기반 선택](docs/EVIDENCE-GUIDED-DIAGNOSIS.md) · [옵티마이저 검사와 R1 수리](docs/OPTIMIZER-OBSERVABILITY.md) · [PPO 계산 검사](docs/PPO-GRADIENT-CHECK.md) |
| 교정과 적용 범위 | [회복 모드](docs/TRAINING-CORRECTION.md) · [조합 계약](docs/COMBINATION-APPLICABILITY.md) · [외부 결함](docs/T1-EXTERNAL-FAULTS.md) |
| 모델·자원 비교 | [3.5 측정](docs/NEMOTRON35-EVIDENCE-REPORT.md) · [추론 모드](docs/NEMOTRON-REASONING-MODES.md) · [에이전트/자원 연구](docs/MECHANISM-AGENT-RESOURCE-COMPARISON.md) |
| 영상과 재현성 | [영상 계약](docs/VISION-EVIDENCE-CONTRACT.md) · [근거 스토리](docs/AGENTIC-STORY-REPLAY.md) · [문제 해결](docs/TROUBLESHOOTING.md) |

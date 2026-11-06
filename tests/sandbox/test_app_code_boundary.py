"""OpenShell 샌드박스 안에서만 실행: 에이전트가 자기 도구 코드를 고칠 수 없는지 확인한다.

이미지의 /sandbox/app 파일은 Windows 마운트에서 빌드하면 모드 777이 된다. 파일 권한으로는 막히지 않고
policies/triage_agent.yaml의 read_only(/sandbox/app)만 막는다. 기존 test_kernel_boundary.py 8개와 따로 집계한다.
파일은 덧붙이기 모드로 열기만 하고 쓰지 않는다.
"""
import errno
import hashlib
import os

import pytest

pytestmark = pytest.mark.skipif(os.environ.get("OPENSHELL_SANDBOX") != "1", reason="OpenShell 샌드박스 전용")
TOOL_CODE = "/sandbox/app/src/rl_triage/triage_tools.py"


def _sha256(path: str) -> str:
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def test_cannot_open_agent_tool_code_for_writing():
    before = _sha256(TOOL_CODE)
    with pytest.raises(PermissionError) as exc:
        open(TOOL_CODE, "ab").close()
    assert exc.value.errno == errno.EACCES
    assert _sha256(TOOL_CODE) == before

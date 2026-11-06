"""에이전트 도구 코드(/sandbox/app/src/rl_triage/triage_tools.py)에 덧붙이기를 시도하고 전후 SHA-256을 남긴다."""
import errno
import hashlib
import json

PATH = "/sandbox/app/src/rl_triage/triage_tools.py"


def sha() -> str:
    return hashlib.sha256(open(PATH, "rb").read()).hexdigest()


out = {"path": PATH, "sha256_before": sha()}
try:
    with open(PATH, "ab") as f:
        f.write(b"# probe: agent tampering attempt\n")
    out["append"] = "allowed"
except OSError as e:
    out["append"] = "denied"
    out["exception"] = type(e).__name__
    out["errno"] = errno.errorcode.get(e.errno, e.errno)
out["sha256_after"] = sha()
out["changed"] = out["sha256_before"] != out["sha256_after"]
print(json.dumps(out, ensure_ascii=False))

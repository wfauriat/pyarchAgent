import subprocess
import argparse

from dataclasses import dataclass


@dataclass(frozen=True)
class BashResult:
    returncode: int
    stdout: str
    stderr: str
    timeout: bool = False 


def _normalize(x: bytes | str | None) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    return bytes(x).decode(errors="replace")

def run_bash(command: str) -> BashResult:
    try:
        output = subprocess.run(["bash", "-c", command], shell=False,
                    capture_output=True, check=False,
                    stdin=subprocess.DEVNULL,
                    text=True, timeout=10)
        return BashResult(output.returncode, output.stdout, output.stderr)
    except subprocess.TimeoutExpired as e:
        return BashResult(-9, _normalize(e.stdout),
                          _normalize(e.stderr), timeout=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="subprocess run")
    parser.add_argument("cmd")
    args = parser.parse_args()
    result = run_bash(args.cmd)
    print("="*60)
    print(f"cmd: {args.cmd}")
    print("="*60)
    print(f"code:{result.returncode}")
    print("="*60)
    print(f"stdout:\n{result.stdout}")
    print("="*60)
    print(f"stderr:\n{result.stderr}\n")
    print(f"Timeout?{result.timeout}\n")

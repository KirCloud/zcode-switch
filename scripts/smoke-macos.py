#!/usr/bin/env python3
"""Check that the packaged GUI starts with default and custom icons."""

import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


def check_startup(app, logo):
    with tempfile.TemporaryDirectory(prefix="zswitch-smoke-") as temp:
        home = Path(temp)
        if logo is not None:
            store = home / ".zcode-switch"
            store.mkdir()
            (store / "settings.json").write_text(json.dumps({"app_logo": logo}))
        env = dict(os.environ, ZCODE_SWITCH_HOME=str(home), RUST_BACKTRACE="full")
        with tempfile.TemporaryFile() as log:
            process = subprocess.Popen(
                [str(app / "Contents/MacOS/zcode-switch")],
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
            )
            try:
                try:
                    code = process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    print("GUI stayed running with", "default icon" if logo is None else "custom icon")
                else:
                    log.seek(0)
                    print(log.read().decode(errors="replace"), file=sys.stderr)
                    raise SystemExit(f"GUI exited during startup (status {code})")
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()


if __name__ == "__main__":
    app = Path(sys.argv[1]).resolve()
    check_startup(app, None)
    icon = Path(__file__).resolve().parents[1] / "src-tauri/icons/icon.png"
    check_startup(app, "data:image/png;base64," + base64.b64encode(icon.read_bytes()).decode())

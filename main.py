"""Compatibility entry point for the Vectorloom asset pipeline."""

import subprocess
import sys

if __name__ == "__main__":
    command = "check" if "--check" in sys.argv[1:] else "build"
    subprocess.run(["vectorloom", command, "--config", "icons.json"], check=True)

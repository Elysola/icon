"""Compatibility entry point for Vectorloom validation."""

import subprocess

if __name__ == "__main__":
    subprocess.run(["vectorloom", "validate", "--config", "icons.json"], check=True)

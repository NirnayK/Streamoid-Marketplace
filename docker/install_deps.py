import tomllib
import subprocess

with open("pyproject.toml", "rb") as f:
    data = tomllib.load(f)

deps = data["project"]["dependencies"]
subprocess.check_call(["uv", "pip", "install", "--system", "--no-cache-dir", *deps])

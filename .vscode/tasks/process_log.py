from pathlib import Path

log_path = Path(__file__).joinpath("../import.log").resolve()

log_lines = []
with open(log_path) as log_file:
    for line in log_file:
        log_lines.append(line)

log_lines = (""
    .join(log_lines)
    .replace("\n", "")
    .replace("import time:", "\nimport time:")
    .split("\n")
)

with open(log_path, "w") as log_file:
    header = "import time: self [us] | cumulative | imported package"
    log_file.truncate()
    log_file.write(header)
    for line in log_lines:
        if header not in line and line.startswith("import time:  "):
            log_file.write("\n")
            log_file.writelines(line)
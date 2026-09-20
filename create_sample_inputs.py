import os
import shutil
from pathlib import Path

BASE = Path("test_inputs")
BASE.mkdir(exist_ok=True)

# 1. unixfun inputs
unix_dir = BASE / "unixfun"
unix_dir.mkdir(exist_ok=True)

src_unix = Path("Koala/unixfun/inputs")
for input_id in ["1", "2", "3"]:
    src_file = src_unix / f"{input_id}.txt"
    if src_file.exists():
        shutil.copy(src_file, unix_dir / f"{input_id}.txt")

for input_id in ["4", "5", "6", "7", "8", "9.1", "9.2", "9.3", "9.4", "9.5", "9.6", "9.7", "9.8", "9.9", "10", "11", "12"]:
    src_file = src_unix / f"{input_id}_30M.txt"
    if src_file.exists():
        with open(src_file, "r", errors="ignore") as f_in:
            lines = [f_in.readline() for _ in range(100)]
        with open(unix_dir / f"{input_id}.txt", "w") as f_out:
            f_out.writelines(lines)

# 2. covid inputs
covid_dir = BASE / "covid"
covid_dir.mkdir(exist_ok=True)
src_covid = Path("Koala/covid/min_inputs/in_min.csv")
if src_covid.exists():
    with open(src_covid, "r", errors="ignore") as f_in:
        lines = [f_in.readline() for _ in range(200)]
    with open(covid_dir / "in_min.csv", "w") as f_out:
        f_out.writelines(lines)

# 3. weather inputs
weather_dir = BASE / "weather"
weather_dir.mkdir(exist_ok=True)
src_weather = Path("Koala/weather/min_inputs/temperatures.min.txt")
if src_weather.exists():
    with open(src_weather, "r", errors="ignore") as f_in:
        lines = [f_in.readline() for _ in range(100)]
    with open(weather_dir / "temperatures.min.txt", "w") as f_out:
        f_out.writelines(lines)

# 4. oneliners inputs
oneliners_dir = BASE / "oneliners"
oneliners_dir.mkdir(exist_ok=True)

comm_dir = oneliners_dir / "comm_input"
comm_dir.mkdir(exist_ok=True)
with open(comm_dir / "file1", "w") as f:
    f.write("apple\nbanana\ncherry\ndate\nelderberry\n")
with open(comm_dir / "file2", "w") as f:
    f.write("banana\ncherry\nfig\ngrape\n")

chess_dir = oneliners_dir / "chess_input"
chess_dir.mkdir(exist_ok=True)
with open(chess_dir / "sample.pgn", "w") as f:
    f.write('[Result "1-0"]\n[Result "0-1"]\n[Result "1/2-1/2"]\n')

with open(oneliners_dir / "sample.txt", "w") as f:
    f.write("""The quick brown fox jumps over the lazy dog.
The quick brown fox is very quick and clever.
A quick fox jumps high.
No vowels rhythm fly crypt.
aabbccdd
127.0.0.1
192.168.1.1
8.8.8.8
127.0.0.1
""")

with open(oneliners_dir / "ips.txt", "w") as f:
    f.write("127.0.0.1\n192.168.1.1\n8.8.8.8\n127.0.0.1\n8.8.8.8\n10.0.0.1\n")

# 5. analytics inputs
analytics_dir = BASE / "analytics"
analytics_dir.mkdir(exist_ok=True)
rt_dir = analytics_dir / "ray_tracing_in"
rt_dir.mkdir(exist_ok=True)
with open(rt_dir / "1.INFO", "w") as f:
    f.write("""Header line
[RAY] 590432,100,200,300
[RAY] pathID 20613314,50,60
[RAY] 590432,110,210,310
""")

with open(analytics_dir / "port_scan_in.json", "w") as f:
    f.write("""{"ip": "8.8.8.8"}
{"ip": "1.1.1.1"}
{"ip": "8.8.4.4"}
{"ip": "8.8.8.8"}
""")

(analytics_dir / "routeviews.mrt").touch()


# 6. nlp inputs
nlp_dir = BASE / "nlp"
nlp_dir.mkdir(exist_ok=True)
with open(nlp_dir / "pg.txt", "w") as f:
    f.write("""The quick brown fox jumps over the lazy dog.
The quick brown fox is very quick and clever.
A quick fox jumps high.
No vowels rhythm fly crypt.
He runs quickly and loudly.
Light shines in the darkness, and light overcomes it.
Slowly and carefully they walked.
""")

print("Sample test inputs created successfully.")

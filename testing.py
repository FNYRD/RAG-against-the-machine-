import math
import re

lines = open("core_projects_files/vllm-0.10.1/docs/features/lora.md").read().splitlines()
chunks = [lines[2], lines[4], lines[15]]
docs = [re.findall(r"\w+", c.lower()) for c in chunks]

N = len(docs)
lengths = [len(d) for d in docs]
avgdl = sum(lengths) / N
print(avgdl)
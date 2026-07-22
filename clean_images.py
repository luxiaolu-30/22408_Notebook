import re

with open('408/数据结构.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start = 1253  # 0-indexed for line 1254
end = 1433

before = 0
for i in range(start, end):
    if i < len(lines):
        before += len(re.findall(r'!\[[^\]]*\]\(https?://[^\)]+\)', lines[i]))

for i in range(start, min(end, len(lines))):
    lines[i] = re.sub(r'!\[[^\]]*\]\(https?://[^\)]+\)', '', lines[i])

after = 0
for i in range(start, end):
    if i < len(lines):
        after += len(re.findall(r'!\[[^\]]*\]\(https?://[^\)]+\)', lines[i]))

with open('408/数据结构.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'Done: {before} -> {after}')

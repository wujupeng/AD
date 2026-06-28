import json, sys
d = json.load(sys.stdin)
for p in sorted(d['paths'].keys()):
    print(p)
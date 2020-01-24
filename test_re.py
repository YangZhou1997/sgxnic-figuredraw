import re

lun_q = 'Lun:\s*(\d+(?:\s+\d+)*)'
s = '''Lun: 0 1 2 3 295 296 297 298'''

r = re.search(lun_q, s)

if r:
    luns = r.group(1).split()
    print(luns)

    # optionally, also convert luns from strings to integers
    luns = [int(lun) for lun in luns]
    print(luns)

import csv
import os
import sys

PRIZES_HEADER = ['solemateId', 'blockNumber', 'recipient', 'note']

FILENAME = 'prizes.csv'

# if the file already exists, exit

if os.path.isfile(FILENAME):
    print("{} already exists, exiting".format(FILENAME))
    sys.exit(1)

with open(FILENAME, 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(PRIZES_HEADER)
    count = 5555
    # Gen 1...{count}
    for i in range(count):
      writer.writerow([str(i+1), None, None, None])

import hashlib
import sys
import csv
import urllib.request
import json

# Define order of entrants in the giveaway

prizes = []

PRIZES_HEADER = ['solemateId', 'blockNumber', 'recipient', 'note']

highestBlockSeenInPrizesDb = 0

def getJsonAtUrl(url):
    response = urllib.request.urlopen(url)
    return json.loads(response.read().decode('utf-8'))

with open('prizes.csv') as csvfile:
  reader = csv.reader(csvfile)
  # First row is header: [solemateId, blockNumber, recipient]
  header = next(reader)

  for row in reader:
    bn = int(row[1]) if row[1] else None
    prizes.append({
      'id': row[0],
      'block': bn,
      'recipient': row[2] if len(row) > 2 else '',
      'note': row[3] if len(row) > 3 else ''
    })
    if bn and bn > highestBlockSeenInPrizesDb:
      highestBlockSeenInPrizesDb = bn

class RNG:
  def __init__(self, blockHashes):
    # Create hash of blockhashes
    h = hashlib.sha256()

    for b in blockHashes:
      h.update(b.encode())

    self.seed = h.digest()

  def next(self):
    # Create hash of seed
    h = hashlib.sha256()
    h.update(self.seed)
    self.seed = h.digest()
    return int.from_bytes(self.seed, byteorder='big')


# Usage python3 raffle.py entrants.csv
# (headers of entrants csv should be raffleId,address,transactionId,amount,price,isGifted,createdAt)

if (len(sys.argv) != 3):
  print("Usage: python3 raffle.py BLOCK_NUMBER entrants.csv")
  sys.exit(1)

blockNumber = int(sys.argv[1])
filename = sys.argv[2]

readonlyMode = False

if blockNumber <= highestBlockSeenInPrizesDb:
  print("Prizes database contains bitcoin block number {}".format(highestBlockSeenInPrizesDb))
  print("Continuing to run the algorithm in read-only mode, which will not update the prizes.csv database")
  print("Due to deterministic randomness, the same output will be produced each time you run this script")
  print("")
  readonlyMode = True

with open(filename) as csvfile:
  reader = csv.reader(csvfile)
  # First row is header:
  header = next(reader)

  colAddress = header.index('address')
  colAmount = header.index('amount')

  if colAddress == -1 or colAmount == -1:
    print("Error: CSV file must have columns 'address' and 'amount'")
    sys.exit(1)

  # Create a list of all the entrants
  RaffleEntrants = []
  for row in reader:
    amount = int(row[colAmount])
    for i in range(amount):
      RaffleEntrants.append(str(i + 1) + ' - ' + row[colAddress])

# Create an array of all the unallocated prizes, as at the block number
SolmatesRemaining = []
for prize in prizes:
  if prize['block'] is None or prize['block'] >= blockNumber:
    SolmatesRemaining.append(prize)

if (len(SolmatesRemaining) == 0):
  print("No prizes to allocate")
  sys.exit(0)
  

# By default there are 200 winners each week, but this can be changed
NumberOfWinners = 200
if (NumberOfWinners > len(SolmatesRemaining)):
  NumberOfWinners = len(SolmatesRemaining)


url = "https://blockchain.info/block-height/{blockNumber}"
resData = getJsonAtUrl(url.format(blockNumber=blockNumber))

blockHash = resData['blocks'][0]['hash']
if (blockHash is None):
  print("Block number {} not found".format(blockNumber))
  sys.exit(1)

print("Block#{} (for randomness): {}".format(blockNumber, blockHash))

rng = RNG([blockHash])

print("Awarding {} prizes to {} entrant tickets, out of {} Solmates".format(NumberOfWinners, len(RaffleEntrants), len(SolmatesRemaining)))

for i in range(NumberOfWinners):
  if (len(RaffleEntrants) == 0):
    print("No entrants left to award prizes to (this means everyone is a winner)")
    break
  
  # Get a random number between 0 and number of entrants
  randomNumber = rng.next() % len(RaffleEntrants)

  # Pick out a winner from RaffleEntrants
  winner = RaffleEntrants.pop(randomNumber)

  # Pop off the first prize in the list
  prize = SolmatesRemaining.pop(rng.next() % len(SolmatesRemaining))

  # Print the winner and their prize
  print(winner + ' wins Solemate ' + prize['id'])

  if (prize['recipient'] != ''):
    if (prize['recipient'] != winner):
      print("Error: winner {} does not match recipient {}".format(winner, prize['recipient']))
      sys.exit(1)

  # Update the prizes database
  prize['recipient'] = winner
  prize['block'] = blockNumber

if not readonlyMode:
  # Update the prizes database
  with open('prizes.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(PRIZES_HEADER)
    for prize in prizes:
      writer.writerow([prize['id'], prize['block'], prize['recipient'], prize['note']])

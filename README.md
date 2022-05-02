# Solciety weekly raffle script

### Process

The bitcoin blockchain hashes are used as the source of randomness.

The script will modify the `prizes.csv` file to save winners.

Example:

```
python3 raffle.py 731000 RAFFLE_SOLD_ID_Ht51rF1p6GDANY2SqcKc_20220409052351.csv
```

Based on deterministic randomness, output should end with:
```
...
555 - 7fj139ELZVE5KSZp3dEAm83JckbEq4DE7aABKZ9RXDGy wins Solemate 3705
119 - 9sS7hyHYrYtCXr2FfiKnxZamXsyxSvfufnMyr65hBVzP wins Solemate 660
```

If you run the same block number again, it will just print out the same output again. This way you can re-run the script for verification.
import csv
import os

patha = "/Users/bencarroll/Google Drive/Python/car/new/log.csv"

# Setup logging
if not os.path.isfile(patha):
    open(patha, "w").close()

with open(patha, "w", newline="") as csvfile:
    logger = csv.writer(csvfile, delimiter=",",
                        quotechar="|", quoting=csv.QUOTE_MINIMAL)

    # Header
    logger.writerow(["Number", "Square", "Cube", "^4", "^5"])

    for i in range(120):
        logger.writerow([i,i**2, i**3, i**4, i**5])

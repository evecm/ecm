'''
Created on Aug 22, 2012

@author: diabeteman
'''

import csv

class CSVUnicodeWriter:

    def __init__(self, stream, encoding="utf-8", **kwargs):
        self.stream = stream
        self.encoding = encoding
        self.writer = csv.writer(self.stream, **kwargs)

    def writerow(self, row):
        self.writer.writerow( [ unicode(s).encode(self.encoding) for s in row ] )

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
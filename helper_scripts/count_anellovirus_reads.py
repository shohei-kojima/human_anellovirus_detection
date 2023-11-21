#!/usr/bin/env python

"""
# usage: python %prog mapped_to_virus_dedup.bam > out.tsv
# python3.7 or higher
"""

import os,sys,collections
import pysam


# file check
bam=sys.argv[1]
if os.path.exists(bam) is False:
    print('Input bam file (%s) was not found.' % bam)
    exit(1)


d={}
with pysam.AlignmentFile(bam, 'rb') as infile:
    for read in infile:
        if read.is_paired is False:
            continue
        if read.is_duplicate is True:
            continue
        chr=read.reference_name
        if chr is None:
            continue
        if not chr in d:
            d[chr]={}
        read_name=read.query_name
        if not read_name in d[chr]:
            d[chr][read_name]=[False, False]  # read1, read2
        if read.is_read1 is True:
            d[chr][read_name][0]=True
        elif read.is_read2 is True:
            d[chr][read_name][1]=True
        

counter=collections.Counter()
all=set()
for chr in d:
    for read_name in d[chr]:
        if d[chr][read_name][0] == True and d[chr][read_name][1] == True:
            counter[chr] += 1
            all.add(read_name)

out=[]
for chr in counter:
    out.append([counter[chr], chr])
out=sorted(out)

print('SEQID\tmapped_read_count\n', end='')
for l in out:
    print('%s\t%d\n' % (l[1], l[0]), end='')
print('ALL_VIRUS\t%d\n' % len(all), end='')

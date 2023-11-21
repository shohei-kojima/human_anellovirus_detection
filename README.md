# About
Here contains the scripts used for human anellovirus detection from WGS.  

# In brief
- 3,333 complete human anellovirus genomes were used as reference anelloviruses.  
- Repeats and transposons in the 3,333 anelloviruses were masked to avoid multi-mapping.  
- Using hisat2, unmapped WGS reads were re-mapped to the anelloviruses with allowing multi-mapping to multiple anellovirus sequences.  
- The reads mapping to at least one anellovirus sequence were counted.  

# Analysis details
## Preparation of human anellovirus seqeunces
- Here, we downloaded all Anelloviridae sequences in NCBI, and filtered for complete genomes of human anelloviruses.  
- We used anellovirus sequences with:  
    - `Nuc_Completeness` is `complete`  
    - `Host` is `Homo sapiens`  
- Anelloviridae sequences were downloaded on April 21, 2022.  
- In total, we used 3,333 anelloviruses for analysis.  

```
# download anelloviridae sequences
esearch -db nucleotide \
-query "Viruses[Organism] NOT cellular organisms[Organism] AND Anelloviridae[Organism] OR Anelloviridae[All Fields]" \
| efetch -format fasta > anelloviridae.220421.fa

# download metadata (manually downloaded from below and saved as 'anelloviridae_metadata.220421.csv').
# https://www.ncbi.nlm.nih.gov/labs/virus/vssi/#/virus?SeqType_s=Nucleotide&VirusLineage_ss=Anelloviridae,%20taxid:687329&utm_source=data-hub

# make fasta of complete human anellovirus
python prepare_human_anelloviruses/batch_220421_100826.py
```

- We found that some anelloviruses contain sequences similar to human transposons. Those sequences may be a mis-assembly of anelloviruses. To avoid mis-mapping of human genome-derived reads to anelloviruses, we masked the 3,333 anellovirus sequences by RepeatMasker.  
- As a result of RepeatMasker, below were masked:  
    - 1,752 simple repeats  
    - 753 low complexity regions  
    - 15 ERVs  
    - 1 LINE-1  
- We used the masked sequences for the downstream analysis.  
```
RepeatMasker \
anelloviridae.human_complete.220421.fa \
-species 9606 \
-s -no_is -a \
-dir masked_human_anelloviridae \
-pa 2

# saved the masked fasta as 'anelloviridae.human_complete.220421.masked.fa'
mv masked_human_anelloviridae/anelloviridae.human_complete.220421.fa.masked ./anelloviridae.human_complete.220421.masked.fa
```

## Mapping of unmapped WGS reads to anellovirus
- The WGS reads were mapped to either GRCh37 or GRCh38.  
- We first extracted unmapped WGS reads and mapped to the repeat-masked 3,333 human anelloviruses.  
- We used the scripts in the submodule `human_anellovirus_detection` (also available from docker://shoheikojima/anellovirus_detection:220421)  
- When mapping, we used a custom setting of hisat2 to allow multi-mapping:  
    - Specified the `--mp 2,1` option  
    - Added the `--no-spliced-alignment` flag  
    - Added the `--all` flag  
    - Added the `--secondary` flag  

```
# unmapped WGS reads
fq1=/path/to/unmapped_fastq_1.fq
fq2=/path/to/unmapped_fastq_2.fq

# hisat2 index of 'anelloviridae.human_complete.220421.masked.fa'
ht2_index=./human_anellovirus_detection/anellovirus_fa/ht2_index/anelloviridae.human_complete.220421.masked

python human_anellovirus_detection/main.py \
-vref ./human_anellovirus_detection/anellovirus_fa/anelloviridae.human_complete.220421.masked.fa \
-vrefindex ${ht2_index} \
-picard /usr/local/bin/picard.jar \
-fastqin \
-fq1 ${fq1} \
-fq2 ${fq2} \
-outdir ${outdir}
```

## Counting reads mapping to anelloviruses  
- Here we counted the reads mapping to at least one anellovirus sequence of the masked 3,333 anellovirus sequences.  
- We counted reads satisfying below:  
    - Read is not PCR duplicates.  
    - At least read 1 and the read 2 of the read pair is mapping to at least one anellovirus genome.  

```
python human_anellovirus_detection/helper_scripts/count_anellovirus_reads.py \
${outdir}/mapped_to_virus_dedup.bam \
> ${sample}.mapped_to_virus_dedup.read_cnt.tsv
```

# Software Versions
- Python 3.7  
- RepeatMasker-4.1.1  
- hisat2 2.2.1  


# LICENSE
Copyright (c) 2022 RIKEN  
All Rights Reserved.  
See file LICENSE for details.  
This tool was developed by Shohei Kojima and Nicholas F. Parrish.  

# Miscellaneous Scripts
Miscellaneous scripts not associated with any particular project

*getAllGenomeFasta.py*
Retrieves genome-level fasta files from Downloads for every organism in a EuPathDB project (e.g., PlasmoDB). Choose between genomic sequence, transcript sequences, CDS sequences (all nucleotide) or protein sequences (amino acid).  For genomic sequence, you can choose to include organisms without annotations.

*Script is written in Python3 and requires the requests library.  See requests documentation for installation instructions [here](https://2.python-requests.org "Requests Documentation") (or use pip)*

```
usage: getAllGenomeFasta.py [-h] --type {genomic,transcript,cds,protein}
                            [--includeUnannotated]
                            project

positional arguments:
  project               EuPathDB project from which you wish to download fasta
                        sequences, e.g., PlasmoDB. For downloads from multiple
                        projects, use a comma separated list, e.g,
                        CryptoDB,ToxoDB

optional arguments:
  -h, --help            show this help message and exit
  --type {genomic,transcript,cds,protein}
                        Type of sequence to download. Choose from genomic
                        sequence, transcript sequences, CDS sequences (all
                        nucleotide) or protein sequences (amino acid)
  --includeUnannotated  For genomic sequences only, include fasta from
                        organisms with no annotations
```

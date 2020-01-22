# logaspect
Datasets for aspect-based sentiment analysis in log files.

## Contents

1. All datasets are located in `logaspect/datasets`.
 
2. Aspect terms are located in `logaspect/groundtruth/aspect-terms`.

3. Sentiment terms are located in `logaspect/groundtruth/sentiment-terms`.

## Creating a new virtual environment

1. Create a conda virtual environment

   `conda create --name logaspect python=3.6`

2. Activate the environment

   `conda activate logaspect`

## Extracting the datasets and install the package

1. Clone this repository

   `git clone https://github.com/studiawan/logaspect.git`

2. Go to the project directory
    
   `cd logaspect`

3. Install this package
   
   `pip install -e .`

3. Extract the datasets   
    
   `unzip datasets/datasets.zip -d datasets/`

## Building the ground truth

1. Change the directory path in `logaspect/groundtruth/datasets.conf` in `[main]` section 

2. Run the ground truth. This procedure will take some time to run

   `python logaspect/groundtruth/groundtruth-xml.py`

3. Edit the dataset to be splitted, in `logaspect/groundtruth/split-xml.py`, line 167

   `vi logaspect/groundtruth/split-xml.py`

4. Edit data format, in `logaspect/groundtruth/split-xml.py`, line 188-189. Choose `split_all` method

   `vi logaspect/groundtruth/split-xml.py`

5. Split the dataset
  
   `python logaspect/groundtruth/split-xml.py`

6. Rename directory `datasets/data-xml/` for each dataset, where `xxx` is the dataset name

   `mv datasets/data-xml datasets/data-xml-xxx`

## References

S. Garfinkel, "nps-2009-casper-rw: An ext3 file system from a bootable USB," 2009. [Online]. Available: http://downloads.digitalcorpora.org/corpora/drives/nps-2009-casper-rw/

E. Casey and G. G. Richard III, "DFRWS Forensic Challenge 2009," 2009. [Online]. Available: http://old.dfrws.org/2009/challenge/index.shtml

G. Arcas, H. Gonzales, and J. Cheng, "Challenge 7 of the Honeynet Project Forensic Challenge 2011 - Forensic analysis of a compromised server," 2011. [Online]. Available: https://old.honeynet.org/challenges/2011_7_compromised_server
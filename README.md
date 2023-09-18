# Longitudinal Assessment of Reference Quality on Wikipedia

Please cite our work if using any data or script:

A. Baigutanova, J. Myung, D. Saez-Trumper, A.-J. Chou, M. Redi, C. Jung and M. Cha. Longitudinal Assessment of Reference Quality on Wikipedia, In proc. of the Web Conference (WWW), April 2023

Link to the publication: https://dl.acm.org/doi/10.1145/3543507.3583218


The repo is organized in the following way:

```
├── data                                 # Datasets used
│   ├── random.csv.gz                    # Random Dataset
│   ├── current.csv.gz                   # Current Dataset
│   ├── reference_history.csv.gz         # Reference History Dataset
│   ├── perennial_source_list.csv.gz     # Perennial Sources Dataset
│
└── code                                 # Code used
    ├── psm_co_editing.py                # Code used for PSM (sec 5.3.2)
    ├── psm_expertise.py                # Code used for PSM (sec 5.3.1)
```


We also add a detailed description for the datasets used.
1. **Random and Top**: Every editing revision is logged with the additional metadata. For the Top Dataset, you can access it through this link: https://drive.google.com/file/d/1xh6K2XKsYqZtqTyy7GbQwnbIyNnh5v-t/view?usp=sharing
2. **Current** consists of revision ids and the corresponding page ids used in our analysis. As we do not use the additional metadata for the Current dataset, it is not included.
3. **Reference History** consists of the history of all references listed in perennial sources list used until January 2022.
    - The "source" column is a unique id assigned to a domain listed in the perennial sources list. You can map the source id to the domain using 'perennial_source_list.csv.gz' file
    - The 'category' column is consist of numerical values in range 1~5. Each of numbers means : (5:Generally Reliable), (4:No Consensus), (3:Generally Unreliable), (2:Deprecated), (1:Blacklisted)
    - The 'rev_type' columns shows whether occurance of revision is finally removed or not.
4. **Perennial Source List** consist of the status and its classification date of all sources in "[Perennial Sources](https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources/Perennial_sources)" (Collected in May 2022). The sources in Deprecated/Blacklisted status have information about classification.

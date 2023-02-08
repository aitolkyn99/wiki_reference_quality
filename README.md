# Longitudinal Assessment of Reference Quality on Wikipedia

Please cite our work if using any data or script:

A. Baigutanova, J. Myung, D. Saez-Trumper, A.-J. Chou, M. Redi, C. Jung and M. Cha. Longitudinal Assessment of Reference Quality on Wikipedia, In proc. of the Web Conference (WWW), April 2023


The repo is organized in the following way:

```
├── data                                 # Datasets used
│   ├── random.csv.gz                    # Random Dataset
│   ├── current.csv.gz                   # Current Dataset
│   ├── reference_history.csv.gz         # Reference History Dataset
└── code                                 # Code used
    ├── psm.py                           # Code used for PSM 
```


We also add a detailed description for the datasets used.
1. **Random and Top**: Every editing revision is logged with the additional metadata. For the Top Dataset, you can access it through this link: 
2. **Current** consists of revision ids and the corresponding page ids used in our analysis. As we do not use the additional metadata for the Current dataset, it is not included.
3. **Reference History** consists of the history of all references listed in perennial sources list used until January 2022.
    - The "source" column is a unique id assigned to a domain listed in the perennial sources list. You can map the source id to the domain using 'domain_source_id_mapping.csv' file

import pandas as pd 
import numpy as np
import scipy
from scipy import stats
import matplotlib.pyplot as plt
from statistics import mean, stdev
from math import sqrt
from pymatch.Matcher import Matcher
import time

root = '../data/'


def label_by_threshold_new(expo, thr):
    """
  expo - data to label
  thr - threshold  
  """
  expo['label']=[0 if i<thr else 1 for i in expo['N']]
  return expo

def get_df(target, thr = 1):

  """
  target - one of 'top' or 'random' to read data
  thr - value to divide users into exposed and nonexposed 
  """
  
  exp_df = pd.read_csv(root + 'exposure_{0}.csv.gz'.format(target)) ### exp_df should be created prior to running this code by counting the number of collaborations for each novice editor 
  exp_df = exp_df[exp_df.expertise!=1]
  exp_df_label = label_by_threshold_new(exp_df, thr) 
  exposure_rr = exp_df_label[~exp_df_label.RR.isna()]
  exposure_rc = exp_df_label[~exp_df_label.RN.isna()]
  dfs[target] = [exposure_rc, exposure_rr]



def psm_exposure(target, mode, t_val = 'label'):
    
  """
  target - one of 'top' or 'random' 
  mode - one of 'RR" or 'RN' 
  t_val - variable to divide into test and control 
  """

    if mode == 'RR':
        result = dfs[target][1]
        result=result[result.expertise!=2]
        result = result[result.dRR!=0]
        
    elif mode == 'RN':
        result = dfs[target][0]
        result=result[result.expertise!=2]
        result = result[result.dRN!=0]

    ##PSM
    non_features = result.columns.to_list()
    non_features.remove(t_val)

    if mode == 'RR':
        result['prevRR_std'] = (result['prev_RR'] - result['prev_RR'].mean())/result['prev_RR'].std()
        result = result.dropna(subset = ['event_user_revision_count','revision_text_bytes_diff','prev_RR','topic'])
        
    elif mode == 'RN':
        result['prevRN_std'] = (result['prev_RN'] - result['prev_RN'].mean())/result['prev_RN'].std()
        result = result.dropna(subset = ['event_user_revision_count','revision_text_bytes_diff','prev_RN','topic'])
        
    result['rev_size_std'] = (result['revision_text_bytes_diff'] - result['revision_text_bytes_diff'].mean())/result['revision_text_bytes_diff'].std()
    result['experience_std'] =  (result['event_user_revision_count'] - result['event_user_revision_count'].mean())/result['event_user_revision_count'].std()
    result['topic_psm'] = result['topic']
    
    test = result[result[t_val]==1] 
    test_users = test.event_user_id.unique()
    control = result[(~result.event_user_id.isin(test_users)) & (result[t_val]==0)]
    m = Matcher(test, control, yvar=t_val, exclude=non_features)

    m.fit_scores(balance=True, nmodels=100)
    m.predict_scores()
    m.match(method="min", nmatches=1, threshold=0.0002)
    m.record_frequency()
    m.assign_weight_vector()
    # Check for balance
    categorical_results = m.compare_categorical(return_table=True)
    print(categorical_results, file=f)
    cc = m.compare_continuous(return_table=True)
    print(cc, file=f)
    
    d = m.matched_data.sort_values("match_id")
    matched_tuples = []
    for match_id in list(set(d.match_id.tolist())):
        matched_tuples.append(tuple(d[d.match_id==match_id]['revision_id'].to_list()))
    return matched_tuples

def get_exposure_dfs(target, by):

    if by =='RR':
        data = dfs[target][1]
    else:
        data = dfs[target][0]
    data = data[data.expertise != 2] 
    rev_tuples = matched[target +'_'+ by]
    exps = []
    novs = []
    for tup in rev_tuples:
        exp = data[data.revision_id==tup[0]]
        nov = data[data.revision_id==tup[1]]
        if data[data.revision_id==tup[0]].label.to_list()[0] == 0:
            tmp = exp
            exp = nov
            nov = tmp
        exps.append(exp)
        novs.append(nov)

    exposed = pd.concat(exps)
    nonexposed = pd.concat(novs)
    return exposed, nonexposed


if __name__ == '__main__':
    start = time.time()

    targets = ['random', 'top']
    matched = {}
    dfs = {}
    matched_df = {}
    f = open("output_psm.txt", "a")
    for target in targets:
        print("######", target, "######", file=f)
        get_df(target, 1)
        for i in ['RN','RR']:
            matched_tuples = psm_exposure(target, i)
            matched[target+'_'+ i] = matched_tuples
            matched_df[target+'_'+ i] = get_exposure_dfs(target, i)  
            exposed, nonexposed = matched_df[target+'_'+i]
            by = 'd' + i
            
            # test conditions
            d1 = exposed[by]
            d2 = nonexposed[by]
            print(stats.ttest_ind(d1, d2, equal_var=False), file=f)
            print(stats.f_oneway(exposed[by], nonexposed[by]), file=f)

    print('total time taken: ', time.time()-start, file=f)
    f.close()
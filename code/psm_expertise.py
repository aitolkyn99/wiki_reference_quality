import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

from datetime import datetime
from statistics import mean, stdev
from math import sqrt
from pymatch.Matcher import Matcher
from statsmodels.stats.multicomp import pairwise_tukeyhsd

root = '../data/'

if __name__ == '__main__':

    targets = ['top', 'random']
    metrics = ['RR', 'RN']

    matched = {}
    thres = 4

    for target in targets:
        """
        Choose data type in targets
        """
        # Load dataset
        result = pd.read_csv(root + '%s.csv.gz.csv' % target)
        df = result[result.event_user_revision_count.notnull()]

        # Divide users by Expertise (Default : by quartile)
        df['active'] = pd.qcut(
            df['event_user_revision_count'], thres, labels=False)
        underBound = max(df[df.active == 0].event_user_revision_count)
        upperBound = min(df[df.active == thres-1].event_user_revision_count)

        for metric in metrics:
            """
            Choose metric type in ['RN','RR']
            """

            print('Data :', target, 'Metric :', metric)
            result = result[~result[metric].isna()]

            # Set name of columns by metric
            std_metric = 'prev%s_std' % metric
            diff_metric = 'd%s_new' % metric

            # PSM Matching Start
            # Set Covariants : Previous_Score, Revision_Size, Topic
            non_features = result.columns.tolist()
            non_features.remove('topic')

            # Normailize the covariant data before matching
            result[std_metric] = (
                result[std_metric] - result[std_metric].mean())/result[std_metric].std()
            result['rev_size_std'] = (result['revision_text_bytes_diff'] -
                                      result['revision_text_bytes_diff'].mean())/result['revision_text_bytes_diff'].std()
            result = result.dropna()
            result = result[result[diff_metric] != 0]

            # Divice Test/Control Group : Experienced & Novice
            test = result[result.event_user_revision_count > upperBound]
            control = result[result.event_user_revision_count < underBound]
            test['active'] = 1
            control['active'] = 0

            # Start matching
            m = Matcher(test, control, yvar="active", exclude=non_features)
            m.fit_scores(balance=True)
            m.predict_scores()
            m.plot_scores()
            m.match(method="min", nmatches=1, threshold=0.0002)
            m.record_frequency()
            m.assign_weight_vector()
            cc1 = m.compare_continuous(return_table=True)
            cc2 = m.compare_categorical(return_table=True)

            # Load Matched Tuples : (Experienced, Novice)
            d = m.matched_data.sort_values("match_id")
            matched_tuples = []
            for match_id in list(set(d.match_id.tolist())):
                matched_tuples.append(
                    tuple(d[d.match_id == match_id]['revision_id'].to_list()))

            # Compare difference of 'metric' for matched groups
            revs = set([i for i, _ in matched_tuples] +
                       [i for _, i in matched_tuples])

            # Select d_metric of experienced user & novice users.
            exps = result[(result.revision_id.isin(revs)) & (
                result.event_user_revision_count > upperBound)][diff_metric].tolist()
            novs = result[(result.revision_id.isin(revs)) & (
                result.event_user_revision_count < underBound)][diff_metric].tolist()

            d = pd.DataFrame({'Group': ['Expert' for i in range(
                len(exps))]+['Novice' for i in range(len(novs))], diff_metric: exps+novs})

            # Calculate statistics of matched group
            F_statistic, pVal = stats.f_oneway(exps, novs)
            # print('----------------------------------------')
            print(target, len(matched_tuples))
            print('ANOVA Result: F={0:.1f}, p={1:.5f}'.format(
                F_statistic, pVal))
            if pVal < 0.05:
                print('p<0.05 : Valid!')

            posthoc = pairwise_tukeyhsd(d[diff_metric], d['Group'], alpha=0.05)
            print(posthoc)
            print(np.mean(exps), np.mean(novs))
            print(np.std(exps), np.std(novs))
            print("T-test", stats.ttest_ind(exps, novs, equal_var=False))
            print("Cohens_d", (mean(exps) - mean(novs)) /
                  (sqrt((stdev(exps) ** 2 + stdev(novs) ** 2) / 2)))

#coding:utf-8
'''
1. 学科相似性计算的结果
2. 转化率与I0的关系
3. 转化率函数拟合：转化率与学科相似性之间的关系
4. 通过转化函数计算各个领域的转化区间

'''
from basic_config import *

import statsmodels.formula.api as smf
import statsmodels.api as sm
lowess = sm.nonparametric.lowess
from statsmodels.sandbox.regression.predstd import wls_prediction_std


## 学科相似度分布
def plot_topic_rel():

    fos_name = {}
    for line in open('data/fos_level0.txt'):

        line = line.strip()

        if line.startswith('fos'):
            continue

        fos, name, level = line.split(',')

        fos_name[fos] = name

    fos1_fos2_func = json.loads(open('data/fos1_fos2_func.json').read())
    rels = ['t1,t2,rel']
    for t1 in fos1_fos2_func.keys():
        name1 = fos_name[t1]
        for t2 in fos1_fos2_func[t1].keys():
            name2 = fos_name[t2]
            num = fos1_fos2_func[t1].get(t2, 0)
            rels.append('{:},{:},{:}'.format(name1, name2, num))

    open('data/mag_topic_relevance.csv', 'w').write('\n'.join(rels))
    logging.info('topic relevance saved to data/topic_relevance.csv')

    ## 画热力图
    plot_heatmap('data/mag_topic_relevance.csv', 'correlation matrix', 'field',
                 'field', 'fig/mag_topic_rel_matrix.png')


#转化率与学科之间的关系
def cor_sim_itr():
    # 两个学科的相似度
    fos1_fos2_func = json.loads(open('data/fos1_fos2_func.json').read())

    selected_funcs = []

    new_fos1_fos2 = defaultdict(lambda: defaultdict(float))
    for fos1 in fos1_fos2_func.keys():

        self_func = fos1_fos2_func[fos1][fos1]
        if self_func > 0.5:

            selected_funcs.append(fos1)

            for fos2 in fos1_fos2_func[fos1].keys():

                new_fos1_fos2[fos1][
                    fos2] = fos1_fos2_func[fos1][fos2] / self_func

    # 相似度与转化率的关系

    fos1_fos2_itrs = defaultdict(lambda: defaultdict(list))
    for line in open('data/paper_ITR.csv'):

        line = line.strip()

        if line.startswith('pid'):
            continue

        pid, subj, osubj, func, I0, IT, ITR = line.split(',')

        ITR = float(ITR)

        fos1_fos2_itrs[subj][osubj].append(ITR)

    xs = []
    ys = []
    for fos1 in fos1_fos2_itrs.keys():

        for fos2 in fos1_fos2_itrs[fos1].keys():

            if fos1 not in selected_funcs or fos2 not in selected_funcs or fos1 == fos2:
                continue

            xs.append(new_fos1_fos2[fos1][fos2])
            ys.append(np.mean(fos1_fos2_itrs[fos1][fos2]))
    dic = {'FS': xs, 'ITR': ys}
    data = pd.DataFrame(dic)

    plt.figure(figsize=(5, 4))

    # plt.plot(xs, ys, 'o')
    sns.scatterplot(data=data, x='FS', y='ITR')

    # xs, ys = zip(*lowess(data['ITR'], data['FS'], frac=1. / 3, it=0))

    # plt.plot(xs, ys, '--', c='r')

    mod = smf.ols(formula='np.log(ITR) ~ np.log(FS)', data=data)

    res = mod.fit()

    # print(res.summary())

    prstd, iv_l, iv_u = wls_prediction_std(res)

    plt.plot(xs, np.exp(res.fittedvalues), 'b', label="OLS")
    plt.plot(xs, np.exp(iv_u), 'r')
    plt.plot(xs, np.exp(iv_l), 'r')

    plt.yscale(0.1, 10)
    plt.legend(loc='best')

    plt.xscale("log")
    plt.yscale('log')

    plt.xlabel('field similiraty')
    plt.ylabel('ITR')

    plt.tight_layout()

    plt.savefig('fig/sim_ITR.png', dpi=400)

    logging.info('fig saved to fig/sim_ITR.png')


if __name__ == '__main__':
    # plot_topic_rel()

    cor_sim_itr()
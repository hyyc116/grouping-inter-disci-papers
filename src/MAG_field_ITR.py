#coding:utf-8
'''
1. 学科相似性计算的结果
2. 转化率与I0的关系
3. 转化率函数拟合：转化率与学科相似性之间的关系
4. 通过转化函数计算各个领域的转化区间

'''
from logging import log
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
        if self_func > 0.3:

            selected_funcs.append(fos1)

            for fos2 in fos1_fos2_func[fos1].keys():

                new_fos1_fos2[fos1][
                    fos2] = fos1_fos2_func[fos1][fos2] / self_func

    # 相似度与转化率的关系
    all_sims = []
    fos1_fos2_itrs = defaultdict(lambda: defaultdict(list))
    for line in open('data/paper_ITR.csv'):

        line = line.strip()

        if line.startswith('pid'):
            continue

        pid, subj, osubj, func, I0, IT, ITR = line.split(',')

        all_sims.append(float(func))

        ITR = float(ITR)

        fos1_fos2_itrs[subj][osubj].append(ITR)

    all_sims = sorted(list(set(all_sims)))

    xs = []
    ys = []
    for fos1 in fos1_fos2_itrs.keys():

        for fos2 in fos1_fos2_itrs[fos1].keys():

            if fos1 not in selected_funcs or fos2 not in selected_funcs or fos1 == fos2:
                continue

            xs.append(new_fos1_fos2[fos1][fos2])
            ys.append(np.mean(fos1_fos2_itrs[fos1][fos2]))

    logging.info(f'{len(selected_funcs)} are selected.')
    open('data/selected_fos.txt', 'w').write('\n'.join(selected_funcs))

    dic = {'FS': xs, 'ITR': ys}
    data = pd.DataFrame(dic)

    plt.figure(figsize=(5, 4))

    # plt.plot(xs, ys, 'o')
    sns.scatterplot(data=data, x='FS', y='ITR')

    # xs, ys = zip(*lowess(data['ITR'], data['FS'], frac=1. / 3, it=0))

    # plt.plot(xs, ys, '--', c='r')

    mod = smf.ols(formula='np.log(ITR) ~ np.log(FS)', data=data)

    res = mod.fit()

    print(res.summary())

    prstd, iv_l, iv_u = wls_prediction_std(res, alpha=0.025)

    plt.plot(xs, np.exp(res.fittedvalues), 'b', label="fitted line")
    plt.plot(xs, np.exp(iv_u), 'r')
    plt.plot(xs, np.exp(iv_l), 'r')

    plt.ylim(0.01, 10)
    plt.legend(loc='best')

    plt.xscale("log")
    plt.yscale('log')

    plt.xlabel('field similiraty')
    plt.ylabel('ITR')

    plt.tight_layout()

    plt.savefig('fig/sim_ITR.png', dpi=400)

    logging.info('fig saved to fig/sim_ITR.png')

    data = {'xs': xs, 'up': list(iv_u), 'down': list(iv_l)}
    logging.info(f'{len(xs)} relations are considered.')
    open('data/up_low.json', 'w').write(json.dumps(data))
    logging.info('data saved to data/up_low.json.')


def I0_rate():

    paper_IO = {}
    paper_t = defaultdict(int)

    for line in open("data/paper_ITR.csv"):
        line = line.strip()

        if line.startswith('pid'):
            continue

        pid, subj, osubj, func, I0, It, ITR = line.split(',')

        paper_IO[pid] = int(I0)
        paper_t[pid] += int(It)

    I0_rate = defaultdict(list)
    for paper in paper_IO.keys():

        I0 = paper_IO[paper]
        t = paper_t[paper] + I0

        I0_rate[I0].append((I0 + 0.0) / t)

    xs = []
    ys = []
    ys_max = []
    ys_min = []
    for I0 in sorted(I0_rate.keys()):

        if I0 > 1000:
            continue

        xs.append(I0)
        ys.append(np.mean(I0_rate[I0]))

        ys_max.append(np.max(I0_rate[I0]))
        ys_min.append(np.min(I0_rate[I0]))

    # xs, ys = zip(*lowess(ys, xs, frac=2. / 3, it=0))
    xs, ys_min = zip(*lowess(ys_min, xs, frac=2. / 3, it=0))
    # xs, ys_max = zip(*lowess(ys_max, xs, frac=2. / 3, it=0))

    plt.figure(figsize=(5, 4))

    plt.plot(xs, ys, label='mean')
    plt.fill_between(xs, ys_min, ys_max, alpha=0.5, color='gray')

    plt.xlabel("$I_0$")
    plt.ylabel('$I_0$ Rate')

    plt.xscale('log')

    plt.tight_layout()

    plt.savefig('fig/I0_rate.png', dpi=400)

    logging.info('fig saved to fig/I0_rate.png.')

    data = {
        '10': I0_rate[10],
        '20': I0_rate[50],
        '50': I0_rate[100],
        '100': I0_rate[200]
    }

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))

    xs = ['$I_0$=10', '$I_0$=50', '$I_0$=100', '$I_0$=200']

    for i, x in enumerate(data.keys()):

        ax = axes[int(i // 2)][i % 2]

        sns.histplot(data=data,
                     x=x,
                     kde=False,
                     fill=False,
                     ax=ax,
                     stat='probability')

        ax.set_xlabel(xs[i])

    plt.tight_layout()

    plt.savefig('fig/I0_RATE_FACETS.png')
    logging.info('fig saved to fig/I0_RATE_FACETS.png')


# 计算每一篇论文的跨学科影响力类型

if __name__ == '__main__':
    # plot_topic_rel()

    cor_sim_itr()

    # I0_rate()
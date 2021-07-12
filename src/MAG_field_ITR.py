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
    plot_heatmap('data/mag_topic_relevance.csv', 'correlation matrix',
                 'Discipline', 'Discipline', 'fig/mag_topic_rel_matrix.png')


#转化率与学科之间的关系
def cor_sim_itr():

    fos_name = {}
    for line in open('data/fos_level0.txt'):

        line = line.strip()

        if line.startswith('fos'):
            continue

        fos, name, level = line.split(',')

        fos_name[fos] = name

    # 两个学科的相似度
    fos1_fos2_func = json.loads(open('data/fos1_fos2_func.json').read())

    selected_funcs = []

    new_fos1_fos2 = defaultdict(lambda: defaultdict(float))
    for fos1 in fos1_fos2_func.keys():

        self_func = fos1_fos2_func[fos1][fos1]
        if self_func > 0.3:

            selected_funcs.append(fos1)

            for fos2 in fos1_fos2_func[fos1].keys():

                new_fos1_fos2[fos1][fos2] = fos1_fos2_func[fos1][fos2]

    # 相似度与转化率的关系
    all_sims = []
    fos1_fos2_itrs = defaultdict(lambda: defaultdict(list))
    for line in open('data/paper_ITR.csv'):

        line = line.strip()

        if line.startswith('pid'):
            continue

        pid, subj, osubj, func, I0, IT, ITR = line.split(',')

        # 这里画图不需要自己的学科
        if subj == osubj:
            continue

        all_sims.append(float(func))

        ITR = float(ITR)

        fos1_fos2_itrs[subj][osubj].append(ITR)

    all_sims = sorted(list(set(all_sims)))

    xs = []
    ys = []

    outlier = (0, 0)
    outlier_labels = None

    normal = (0, 0)
    normal_labels = None

    for fos1 in fos1_fos2_itrs.keys():

        for fos2 in fos1_fos2_itrs[fos1].keys():

            if fos1 not in selected_funcs or fos2 not in selected_funcs or fos1 == fos2:
                continue

            x = new_fos1_fos2[fos1][fos2]
            y = np.mean(fos1_fos2_itrs[fos1][fos2])

            if y > 1 and x < 0.03:
                print(fos_name[fos2], fos_name[fos1])
                print(x, y)

                if y > outlier[1]:
                    outlier = (x, y)
                    outlier_labels = f'({fos_name[fos1]}, {fos_name[fos2]})'

            if x > 0.08 and x < 0.1 and y < 0.8:

                if y > normal[1]:
                    normal = (x, y)
                    normal_labels = f'({fos_name[fos1]}, {fos_name[fos2]})'

            xs.append(x)
            ys.append(y)

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

    prstd, iv_l, iv_u = wls_prediction_std(res)

    plt.plot(xs,
             np.exp(res.fittedvalues),
             'b',
             label="log(ITR) = 0.0661*log(DA)-0.1783")
    plt.plot(xs, np.exp(iv_u), 'r')
    plt.plot(xs, np.exp(iv_l), 'r')

    text_kwargs = dict(ha='center', va='bottom', color='r')

    plt.text(outlier[0], outlier[1], outlier_labels, **text_kwargs)

    plt.annotate(f'{normal_labels}',
                 xy=(normal[0], normal[1]),
                 xycoords='data',
                 xytext=(0.7, 0.2),
                 textcoords='axes fraction',
                 arrowprops=dict(arrowstyle="->"),
                 horizontalalignment='center',
                 verticalalignment='bottom')

    plt.ylim(0.01, 10)
    plt.legend(loc='best')

    plt.xscale("log")
    plt.yscale('log')

    plt.xlabel('Discipline affinity')
    plt.ylabel('$TDI_{D_0 \rightarrow D_k}$')

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
def cal_inter():

    up_low = json.loads(open('data/up_low.json').read())
    xs = up_low['xs']
    up = up_low['up']
    low = up_low['down']

    sim_up_down = {}
    for i, x in enumerate(xs):
        sim_up_down[str(x)] = [up[i], low[i]]

    selected_fos = set(
        [line.strip() for line in open('data/selected_fos.txt')])

    paper_labels = defaultdict(list)
    for line in open('data/paper_ITR.csv'):

        line = line.strip()

        if line.startswith('pid'):
            continue

        pid, subj, osubj, func, I0, IT, ITR = line.split(',')

        if subj not in selected_fos or osubj not in selected_fos:
            continue
        if sim_up_down.get(str(func), None) is None:
            paper_labels[pid].append(-1)
        else:
            up, low = sim_up_down[str(func)]

            paper_labels[pid].append(
                label_inter(np.exp(up), np.exp(low), float(ITR)))

    paper_label = {}
    label_count = defaultdict(int)
    for pid in paper_labels.keys():

        label = int(np.max(paper_labels[pid]))

        # 如果只有本学科，并且大于1 label=-1就是domain-specific
        # if len(paper_labels[pid]) == 1 and label == 1:
        #     label = -1
        paper_label[pid] = label

        label_count[label] += 1

    open('data/paper_inter_label.json', 'w').write(json.dumps(paper_label))
    logging.info(
        f'{len(paper_label)} papers saved to data/paper_inter_label.json.')

    print(label_count)


def label_inter(up, low, ITR):
    if ITR > up:
        return 1
    elif ITR < low:
        return -1
    else:
        return 0


if __name__ == '__main__':
    # plot_topic_rel()

    cor_sim_itr()

    # I0_rate()

    # cal_inter()
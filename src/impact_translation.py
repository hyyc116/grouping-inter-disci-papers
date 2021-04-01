#coding:utf-8
from basic_config import *

PCAS_PATH = 'D:\\datasets\\APS\\PCAS.txt'

PCAS_CODES = []


def select_topic(topic_list):

    reserved_pcases = []
    for pcas in topic_list:

        if len(pcas) != 2:
            continue

        if pcas[0] not in [
                '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'
        ] or pcas[1] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            continue

        if pcas.endswith("0"):
            continue

        reserved_pcases.append(pcas)

    if len(reserved_pcases) == 0:
        return None, 0

    pcas_counter = Counter(reserved_pcases)

    return sorted(pcas_counter.keys(),
                  key=lambda x: pcas_counter[x],
                  reverse=True)[0], len(set(reserved_pcases))


## 主题数量是如何随时间变化的
def topic_nums():

    ## 文章发表的年份
    paper_year = json.loads(open('data/paper_year.json').read())
    logging.info(f'{len(paper_year.keys())} papers has year labels ... ')

    ## 主题每年的数量
    pcas_year_papers = defaultdict(lambda: defaultdict(list))
    ## 主题的数量
    pcas_nums = defaultdict(list)

    num_topic_list = []

    pid_topic = {}

    ## PCAS 文件
    for line in open(PCAS_PATH, encoding='utf-8'):

        line = line.strip()

        if line.startswith('DOI'):
            continue

        try:
            doi, pcas1, pcas2, pcas3, pcas4, pcas5 = line.split(',')
        except:
            continue

        pcas1, pcas2, pcas3, pcas4, pcas5 = pcas1.strip(
        ).split('.')[0], pcas2.strip().split('.')[0], pcas3.strip().split(
            '.')[0], pcas4.strip().split('.')[0], pcas5.strip().split('.')[0]

        pcas_list = [pcas1, pcas2, pcas3, pcas4, pcas5]
        year = paper_year.get(doi, -1)
        pcas, tn = select_topic(pcas_list)

        if pcas is None:
            continue

        if tn > 0:
            num_topic_list.append(tn)

        pcas_nums[pcas].append(doi)
        pid_topic[doi] = pcas

        if year != -1:
            pcas_year_papers[pcas][year].append(doi)

    open('data/pid_topic.json', 'w').write(json.dumps(pid_topic))

    logging.info('pid totpic saved to data/pid_topic.json.')

    num_topic_counter = Counter(num_topic_list)

    plt.figure(figsize=(3.5, 2.8))

    xs = []
    ys = []

    for num in sorted(num_topic_counter.keys()):
        tn = num_topic_counter[num]
        xs.append(num)
        ys.append(tn)

    plt.bar(range(len(xs)), ys)
    plt.xlabel('number of topics')
    plt.ylabel('number of papers')
    plt.xticks(range(len(xs)), xs)
    plt.yscale('log')
    plt.tight_layout()

    plt.savefig('fig/topic_num_dis.png', dpi=800)

    open('data/topic_year_dois.json', 'w').write(json.dumps(pcas_year_papers))
    logging.info('data saved to data/topic_year_dois.json')

    ### 各个主题按照数量多少画图
    ys = []
    xs = []
    topic_nums = {}
    tn_list = []
    for pcas in sorted(pcas_nums.keys(),
                       key=lambda x: len(pcas_nums[x]),
                       reverse=True):

        tn = len(pcas_nums[pcas])
        if pcas == '' or tn < 100:
            continue

        tn_list.append(tn)
        xs.append(pcas)
        ys.append(tn)
        topic_nums[pcas] = pcas_nums[pcas]

    open('data/topic_papers.json', 'w').write(json.dumps(topic_nums))
    logging.info('data saved to data/topic_papers.json')

    open('data/selected_topics.txt', 'w').write('\n'.join(xs))
    logging.info('data saved to data/selected_topics.txt')

    ### 分别输出多少个PCAS
    logging.info(f'Num of PCAS:{len(xs)}')
    ## 画出柱状图
    plt.figure(figsize=(10, 2.8))
    plt.bar(range(len(xs)), ys)
    plt.xticks(range(len(xs)), xs, rotation=90)
    plt.ylim(1, 100000)
    plt.yscale("log")
    plt.xlabel('topic rank')
    plt.ylabel('number of papers')
    plt.tight_layout()
    plt.savefig('fig/topic_nums.png', dpi=800)
    logging.info('topic nums saved to fig/topic_nums.png')

    ### 拟合曲线
    plt.figure(figsize=(3.5, 2.8))
    expfunc = lambda t, a, b: a * np.exp(b * t)
    index_xs = np.arange(len(xs)) + 1
    fit_ys = np.array(ys) / float(np.sum(ys))
    popt, pcov = scipy.optimize.curve_fit(expfunc,
                                          index_xs,
                                          fit_ys,
                                          p0=(0.2, -2))
    plt.plot(np.array(index_xs), fit_ys)
    plt.plot(index_xs, [expfunc(x, *popt) for x in index_xs],
             '--',
             label=u'Fitted Curve: $p(n)=%.2f*e^{%.2fn}$' % (popt[0], popt[1]),
             c='r')
    plt.xlabel('field rank')
    plt.ylabel('probability')
    plt.ylim(0.0001, 0.1)
    plt.yscale('log')
    plt.legend(prop={'family': 'SimHei', 'size': 8})
    plt.tight_layout()

    fitted_xs = range(1, 101)
    fitted_ys = [expfunc(x, *popt) for x in fitted_xs]

    fitted_ys = list(np.array(fitted_ys) / np.sum(fitted_ys))

    topic_dis = {}
    topic_dis['x'] = list(fitted_xs)
    topic_dis['y'] = list(fitted_ys)

    open('data/topic_dis.json', 'w').write(json.dumps(topic_dis))
    logging.info('topic dis saved to data/topic_dis.json.')

    plt.savefig('fig/topic_nums_fit.png', dpi=800)
    logging.info('fig saved to fig/topic/topic_nums_fit.png')

    selected_topics = set(xs)
    new_pid_topic = {}
    for pid in pid_topic.keys():
        topic = pid_topic[pid]
        if topic in selected_topics:

            new_pid_topic[pid] = topic

    logging.info(f'{len(new_pid_topic.keys())} papers reserved.')

    open('data/new_pid_topic.json', 'w').write(json.dumps(new_pid_topic))
    logging.info('new pid topic saved.')


## 主题相关性
def topic_relevance():

    pid_refs = json.loads(open('data/pid_all_refs.json').read())
    pid_topic = json.loads(open('data/new_pid_topic.json').read())

    all_num = len(set(pid_refs.keys()) & set(pid_topic.keys()))

    topic_nums = json.loads(open('data/topic_nums.json').read())

    logging.info(f'{all_num} papers loaded')

    topics = sorted(topic_nums.keys(),
                    key=lambda x: len(topic_nums[x]),
                    reverse=True)[:15]

    all_topics = [line.strip() for line in open('data/selected_topics.txt')]

    t1_t2_num = defaultdict(lambda: defaultdict(int))
    t1_refnum = defaultdict(int)
    progress = 0
    for pid in pid_refs.keys():

        progress += 1

        if progress % 10000 == 0:
            logging.info(f'progress {progress} ...')

        topic = pid_topic.get(pid, '-1')

        if topic == '-1':
            continue

        refs = pid_refs[pid]

        for ref in refs:

            ref_topic = pid_topic.get(ref, '-1')

            if ref_topic == '-1':
                ref_topic = topic

            t1_t2_num[topic][ref_topic] += 1
            t1_refnum[topic] += 1

    print('number of topics:', len(all_topics))

    t1_t2_rel = defaultdict(dict)
    for t1 in all_topics:
        ## 该主题引用总次数
        refnum = t1_refnum[t1]

        row = []
        for t2 in all_topics:
            num = t1_t2_num[t1].get(t2, 0)
            ## 主题2对主题1的相关性
            rel_2_1 = num / float(refnum)
            t1_t2_rel[t1][t2] = rel_2_1

    open('data/topic_rel_matrix.json', 'w').write(json.dumps(t1_t2_rel))
    logging.info('topic relevance matrix saved to data/topic_rel_matrix.json.')

    rels = ['t1,t2,rel']
    for t1 in topics:
        ## 该主题引用总次数
        refnum = t1_refnum[t1]

        row = []
        ## 主题1引用主题2的次数
        for t2 in topics:
            num = t1_t2_num[t1].get(t2, 0)

            ## 主题2对主题1的相关性
            rel_2_1 = num / float(refnum)

            rels.append('{:},{:},{:}'.format(t1, t2, rel_2_1))

    open('data/topic_relevance.csv', 'w').write('\n'.join(rels))
    logging.info('topic relevance saved to data/topic_relevance.csv')

    ## 画热力图
    plot_heatmap('data/topic_relevance.csv', 'correlation matrix', 'field',
                 'field', 'fig/topic_rel_matrix.png')

    ## 画出前15的排序相关性
    plt.figure(figsize=(5, 4))
    all_topics = t1_t2_num.keys()
    all_num_list = []
    # all_rels =
    for t1 in all_topics:
        t2_num = t1_t2_num[t1]
        refnum = t1_refnum[t1]

        num_list = []
        for t2 in all_topics:

            num = t1_t2_num[t1].get(t2, 0)
            num_list.append(num / float(refnum))

        if t1 in topics:
            plt.plot(range(1,
                           len(all_topics) + 1),
                     sorted(num_list, reverse=True),
                     alpha=0.6)

        all_num_list.append(sorted(num_list, reverse=True))

    all_avg = [np.mean([i for i in a if i > 0]) for a in zip(*all_num_list)]

    plt.plot(range(1,
                   len(all_topics) + 1),
             all_avg,
             '--',
             linewidth=2,
             c='r',
             label=u'mean')

    # xs = []
    # ys = []
    # for num_list in all_num_list:

    #     for i, num in enumerate(sorted(num_list, reverse=True)):
    #         if num > 0:
    #             xs.append(i + 1)
    #             ys.append(num)

    # plaw = lambda t, a, b: a * t**b
    # # expfunc = lambda t,a,b:a*np.exp(b*t)
    # popt, pcov = scipy.optimize.curve_fit(plaw, xs, ys, p0=(0.2, -1))
    # plt.plot(np.linspace(1, np.max(xs), 10),
    #          [plaw(x + 1, *popt) for x in np.linspace(1, np.max(xs), 10)],
    #          '-^',
    #          label=u'$f(i)=%.2f \\times i^{%.2f} $' % (popt[0], popt[1]),
    #          c='b')

    plt.xlabel('rank')
    plt.ylabel('correlation')
    plt.yscale('log')
    # plt.xscale('log')
    plt.legend(prop={'family': 'SimHei', 'size': 8})

    plt.tight_layout()
    plt.savefig('fig/topic_rel_dis.png', dpi=800)
    logging.info('fig saved to fig/topic/topic_rel_dis.png')


if __name__ == '__main__':
    # topic_nums()

    topic_relevance()
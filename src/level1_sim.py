#coding:utf-8
from basic_config import *


def level1_sim():

    logging.info('loading paper field ...')
    paper_field = json.loads(
        open('../select-first-topic/data/pid_level1.json').read())

    logging.info('loading paper year ...')
    paper_year = json.loads(open('data/pid_pubyear.json').read())

    sql = 'select paper_id,paper_reference_id from mag_core.paper_references'

    fos1_fos2_refnum = defaultdict(lambda: defaultdict(int))

    query_op = dbop()
    process = 0
    for paper_id, paper_reference_id in query_op.query_database(sql):

        process += 1
        if process % 100000000 == 0:
            logging.info(f'progress {process} ....')

        fos1s = paper_field.get(paper_id, None)
        fos2s = paper_field.get(paper_reference_id, None)

        if fos1s is None or fos2s is None:
            continue

        year1 = int(paper_year.get(paper_id, 1900))
        year2 = int(paper_year.get(paper_reference_id, 1900))

        if year1 < 1970 or year2 < 1970:
            continue

        # 这里不能同时控制，只控制被引论文的年份
        if year2 > 2010:
            continue

        for fos1 in fos1s:

            for fos2 in fos2s:

                fos1_fos2_refnum[fos1][fos2] += 1

    open('data/level1_fos1_fos2_refnum.json',
         'w').write(json.dumps(fos1_fos2_refnum))
    logging.info('refnum data saved.')

    lines = ['fos1,fos2,func']

    fos1_fos2_func = defaultdict(dict)

    for fos1 in fos1_fos2_refnum.keys():

        fos2_refnum = fos1_fos2_refnum[fos1]

        total_refnum = float(np.sum([float(i) for i in fos2_refnum.values()]))

        for fos2 in fos2_refnum.keys():

            refnum = fos2_refnum[fos2]

            func = refnum / total_refnum

            line = f'{fos2},{fos1},{func}'

            fos1_fos2_func[fos2][fos1] = func

    open('data/level1_fos1_fos2_func.json',
         'w').write(json.dumps(fos1_fos2_func))
    logging.info('fos fos cit sim saved to data/fos1_fos2_func.json')

    open('data/level1_fos1_fos2_func.csv', 'w').write('\n'.join(lines))

    rels = ['t1,t2,rel']
    for t1 in fos1_fos2_func.keys():
        for t2 in fos1_fos2_func[t1].keys():
            num = fos1_fos2_func[t1].get(t2, 0)
            rels.append('{:},{:},{:}'.format(t1, t2, num))

    open('data/level1_mag_topic_relevance.csv', 'w').write('\n'.join(rels))
    logging.info('topic relevance saved to data/topic_relevance.csv')

    ## 画热力图
    plot_heatmap('data/mag_level1_topic_relevance.csv', 'correlation matrix',
                 'Discipline', 'Discipline', 'fig/mag_topic_rel_matrix.png')


if __name__ == '__main__':

    level1_sim()

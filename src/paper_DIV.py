#coding:utf-8
'''
计算文章的diversity

diversity = balance * variaty * diaparsity

'''
from basic_config import *

def cal_paper_div():

    subj_refnum = json.loads(open('data/fos1_fos2_refnum.json').read())

    citnum_total = defaultdict(int)
    for subj in subj_refnum.keys():
        for subj2 in subj_refnum[subj].keys():
            citnum_total[subj2] += subj_refnum[subj][subj2]


    paper_subj_citnum = defaultdict(lambda:defaultdict(int))
    total_subsjs = set([])

    for line in open("data/paper_ITR.csv"):
        line = line.strip()

        if line.startswith('pid'):
            continue

        pid, subj, osubj, func, I0, It, ITR = line.split(',')

        paper_subj_citnum[pid][osubj] = It
     
        total_subsjs.add(subj)
    
    total_num = len(total_subsjs)
    paper_DIV = {}
    # 计算每一篇论文的diversity
    for pid in paper_subj_citnum.keys():
        
        subjs = list(paper_subj_citnum[pid].keys())
        subj_num = list(paper_subj_citnum[pid].values())

        variety = len(subjs)/float(total_num)

        balance = gini(subj_num)

        disparsity = cal_disparsity(subjs, subj_refnum, citnum_total)

        diversity = balance * variety * disparsity

        paper_DIV[pid] = diversity
    
    open('data/paper_DIV.json','w').write(json.dumps(paper_DIV))
    logging.info('DONE, data saved to data/paper_DIV.json')


def cal_disparsity(subj_set, subj_refnum, citnum_total):

    all_dij = []
    for i in range(len(subj_set)):

        for j in range(i+1, len(subj_set)):

            if i == j:
                continue

            subj1 = subj_set[i]
            subj2 = subj_set[j]

            dij = 1-Sij(subj1, subj2, subj_refnum, citnum_total)

            all_dij.append(dij)

    return np.mean(all_dij)


def Rij(subj1, subj2, subj_refnum):

    return int(subj_refnum[subj1].get(subj2, 0))


def Sij(subj1, subj2, subj_refnum, citnum_total):

    return (Rij(subj1, subj2, subj_refnum)+Rij(subj2, subj1, subj_refnum))/np.sqrt((total_refnum_of_subj(subj1, subj_refnum)+total_citnum_of_subj(subj1, citnum_total))*(total_refnum_of_subj(subj2, subj_refnum)+total_citnum_of_subj(subj2, citnum_total)))


def total_refnum_of_subj(subj, subj_refnum):

    return np.sum([int(i) for i in subj_refnum[subj].values()])


def total_citnum_of_subj(subj, citnum_total):
    return citnum_total[subj]

def gini(array):
    """Calculate the Gini coefficient of a numpy array."""
    # based on bottom eq:
    # http://www.statsdirect.com/help/generatedimages/equations/equation154.svg
    # from:
    # http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
    # All values are treated equally, arrays must be 1d:
    array = np.array([float(i) for i in array])
    # array = array.flatten()
    if np.amin(array) < 0:
        # Values cannot be negative:
        array -= np.amin(array)
    # Values cannot be 0:
    array += 0.0000001
    # Values must be sorted:
    array = np.sort(array)
    # Index per array element:
    index = np.arange(1, array.shape[0] + 1)
    # Number of array elements:
    n = array.shape[0]
    # Gini coefficient:
    return ((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))


if __name__=='__main__':
    cal_paper_div()

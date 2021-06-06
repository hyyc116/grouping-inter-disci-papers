from basic_config import *


def plot_subject():
    fos_name = {}
    for line in open('data/fos_level0.txt'):

        line = line.strip()

        if line.startswith('fos'):
            continue

        fos, name, level = line.split(',')

        fos_name[fos] = name

    pid_label = json.loads(open('data/paper_inter_label.json').read())
    pid_subject = json.loads(
        open("../MAG_data_processing/data/pid_subject.json").read())

    name_labelnum = defaultdict(lambda: defaultdict(int))
    label_num = defaultdict(int)
    for pid in pid_label.keys():

        label = pid_label[pid]

        name = fos_name[pid_subject[pid]]

        name_labelnum[name][label] += 1

        label_num[label] += 1

    # 排序
    results = {}
    for name in sorted(name_labelnum.keys(),
                       key=lambda x: name_labelnum[x][-1]):
        results[name] = [
            name_labelnum[name][-1], name_labelnum[name][0],
            name_labelnum[name][1]
        ]

    results['ALL'] = [label_num[-1], label_num[0], label_num[1]]

    category_names = ['Domain Specific', 'Normal', 'Inter-disciplinary']

    survey(results, category_names)

    plt.tight_layout()

    plt.savefig('fig/subject_inter_cater.png', dpi=600)


def plot_citnum():
    pid_label = json.loads(open('data/paper_inter_label.json').read())

    pid_I0_label = {}

    for line in open('data/paper_ITR.csv'):

        if line.startswith('pid'):
            continue

        pid, subject, Os, func, I0, It, ITR = line.strip().split(',')

        pid_I0_label[pid] = num_label(int(I0))

    cn_label_num = defaultdict(lambda: defaultdict(int))
    label_num = defaultdict(int)
    for pid in pid_label.keys():

        label = pid_label[pid]

        I0_label = pid_I0_label[pid]

        cn_label_num[I0_label][label] += 1

        label_num[label] += 1

    # 排序
    results = {}
    for name in ['[1,5]', '(5,10]', '(10,20]', '(20,50]', '(50,100]', '100+']:
        results[name] = [
            cn_label_num[name][-1], cn_label_num[name][0],
            cn_label_num[name][1]
        ]

    results['ALL'] = [label_num[-1], label_num[0], label_num[1]]

    category_names = ['Domain Specific', 'Normal', 'Inter-disciplinary']

    survey(results, category_names)

    plt.tight_layout()

    plt.savefig('fig/CN_inter_cater.png', dpi=600)


# 三类随着时间的变化
def plot_year():

    fos_name = {}
    for line in open('data/fos_level0.txt'):

        line = line.strip()

        if line.startswith('fos'):
            continue

        fos, name, level = line.split(',')

        fos_name[fos] = name

    pid_pubyear = json.loads(
        open('../MAG_data_processing/data/pid_pubyear.json').read())

    pid_subject = json.loads(
        open('../MAG_data_processing/data/pid_subject.json').read())

    pid_label = json.loads(open('data/paper_inter_label.json').read())

    year_subject_label_num = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int)))

    for pid in pid_label.keys():

        label = pid_label[pid]

        pubyear = int(pid_pubyear[pid])

        subject = fos_name[pid_subject[pid]]

        year_subject_label_num[pubyear][label] += 1

    years = []
    DPapers = defaultdict(list)
    Npapers = defaultdict(list)
    Ipapers = defaultdict(list)
    for year in sorted(year_subject_label_num.keys()):

        years.append(year)

        for subject in year_subject_label_num[year].keys():
            total = float(
                np.sum([
                    i for i in year_subject_label_num[year][subject].values()
                ]))

            DPapers[subject].append(
                int(year_subject_label_num[year][subject][-1]) / total)
            Npapers[subject].append(
                int(year_subject_label_num[year][subject][0]) / total)
            Ipapers[subject].append(
                int(year_subject_label_num[year][subject][1]) / total)

    plt.figure(figsize=(7, 5))

    for subject in sorted(DPapers.keys()):
        plt.plot(years, DPapers[subject], label=subject)

    plt.xlabel('year')
    plt.ylabel('percent')

    plt.legend()

    plt.tight_layout()

    plt.savefig('fig/year_Domain_dis.png', dpi=400)

    logging.info('fig saved to fig/year_Domain_dis.png.')

    plt.figure(figsize=(7, 5))

    for subject in sorted(Npapers.keys()):
        plt.plot(years, Npapers[subject], label=subject)

    plt.xlabel('year')
    plt.ylabel('percent')

    plt.legend()

    plt.tight_layout()

    plt.savefig('fig/year_Normal_dis.png', dpi=400)
    logging.info('fig saved to fig/year_Normal_dis.png.')

    plt.figure(figsize=(7, 5))

    for subject in sorted(Ipapers.keys()):
        plt.plot(years, Ipapers[subject], label=subject)

    plt.xlabel('year')
    plt.ylabel('percent')

    plt.legend()

    plt.tight_layout()

    plt.savefig('fig/year_Inter_dis.png', dpi=400)
    logging.info('fig saved to fig/year_Inter_dis.png.')


def num_label(num):

    if num <= 5:
        return '[1,5]'
    elif num <= 10:
        return '(5,10]'
    elif num <= 20:
        return '(10,20]'
    elif num <= 50:
        return '(20,50]'
    elif num <= 100:
        return '(50,100]'
    else:
        return '100+'


def survey(results, category_names):
    """
    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """

    labels = list(results.keys())
    data = np.array(list(results.values()))

    sum_of_rows = data.sum(axis=1)
    data = data / sum_of_rows[:, np.newaxis]

    print(data)
    data_cum = data.cumsum(axis=1)
    category_colors = plt.get_cmap('RdYlGn')(np.linspace(
        0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(7, 10))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        print(widths)
        print(data_cum[:, i])
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels,
                        widths,
                        left=starts,
                        height=0.5,
                        label=colname,
                        color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        ax.bar_label(rects, label_type='center', color=text_color)
    ax.legend(ncol=len(category_names),
              bbox_to_anchor=(0, 1),
              loc='lower left',
              fontsize='small')

    return fig, ax


if __name__ == '__main__':
    # plt.show()
    # plot_subject()
    # plot_citnum()

    plot_year()
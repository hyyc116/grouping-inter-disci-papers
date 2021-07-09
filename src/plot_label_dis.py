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

    category_names = ['Domain-specific', 'Normal', 'Transdisciplinary']

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

    category_names = ['Domain-specific', 'Normal', 'Transdisciplinary']

    survey(results, category_names)

    plt.ylabel('Citation count')

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

    year_label_num = defaultdict(lambda: defaultdict(int))

    year_subject_label_num = defaultdict(
        lambda: defaultdict(lambda: defaultdict(int)))

    for pid in pid_label.keys():

        label = pid_label[pid]

        pubyear = int(pid_pubyear[pid])

        year_label_num[pubyear][label] += 1

        subject = fos_name[pid_subject[pid]]

        year_subject_label_num[pubyear][subject][label] += 1

    years = []

    DApapers = []
    NApapers = []
    IApapers = []

    DPapers = defaultdict(list)
    Npapers = defaultdict(list)
    Ipapers = defaultdict(list)
    for year in sorted(year_subject_label_num.keys()):

        years.append(year)

        DApapers.append(year_label_num[year][-1])
        NApapers.append(year_label_num[year][0])
        IApapers.append(year_label_num[year][1])

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

    plt.figure(figsize=(5, 4))

    plt.plot(years, DApapers, label='Domain-specific')
    plt.plot(years, NApapers, label='Normal')
    plt.plot(years, IApapers, label='Transdiscipline')

    plt.xlabel('Year')
    plt.ylabel('Proportion')

    plt.tight_layout()

    plt.savefig('fig/year_all.png')

    fig, axes = plt.subplots(3, 1, figsize=(9, 15))

    ax = axes[0]
    for subject in sorted(DPapers.keys()):
        ax.plot(years, DPapers[subject], label=subject)

    ax.set_xlabel('Year')
    ax.set_ylabel('Proportion')

    # plt.legend()
    # ax.legend(bbox_to_anchor=(0.5, -0.2), loc='center', ncol=4)

    # plt.tight_layout()

    # plt.savefig('fig/year_Domain_dis.png', dpi=400)

    # logging.info('fig saved to fig/year_Domain_dis.png.')

    # plt.figure(figsize=(7, 5))
    ax = axes[1]

    for subject in sorted(Npapers.keys()):
        ax.plot(years, Npapers[subject], label=subject)

    ax.set_xlabel('Year')
    ax.set_ylabel('Proportion')

    # plt.legend()
    ax.legend(bbox_to_anchor=(1.2, 0.5),
              loc='center',
              ncol=1,
              prop={'size': 8})

    # plt.tight_layout()

    # plt.savefig('fig/year_Normal_dis.png', dpi=400)
    # logging.info('fig saved to fig/year_Normal_dis.png.')

    # plt.figure(figsize=(7, 5))

    ax = axes[2]

    for subject in sorted(Ipapers.keys()):
        ax.plot(years, Ipapers[subject], label=subject)

    ax.set_xlabel('Year')
    ax.set_ylabel('Proportion')

    # ax.legend(bbox_to_anchor=(0.5, -0.2), loc='center', ncol=4)

    # plt.legend()

    plt.tight_layout()

    plt.savefig('fig/year_Inter_ALL.png', dpi=400)
    logging.info('fig saved to fig/year_Inter_ALL.png.')


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
    data_cum = data.cumsum(axis=1)

    # newdata = data
    # data = []
    # for line in newdata:
    #     newline = []
    #     for d in line:
    #         newline.append(float('{:.2f}'.format(d * 100)))
    #     data.append(newline)
    # data = np.array(data)
    # print(data)
    category_colors = plt.get_cmap('RdYlGn')(np.linspace(
        0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(7, 10))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        print('width:', widths)
        print(data_cum[:, i])
        print('labels:', labels)
        starts = data_cum[:, i] - widths
        print(starts)
        rects = ax.barh(labels,
                        widths,
                        left=starts,
                        height=0.5,
                        label=colname,
                        color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        ax.bar_label(rects,
                     labels=[float('{:.2f}'.format(i)) for i in widths * 100],
                     label_type='center',
                     color=text_color,
                     fmt='%.2f')
    ax.legend(ncol=len(category_names),
              bbox_to_anchor=(0.5, 1),
              loc='lower center',
              fontsize='large')

    return fig, ax


if __name__ == '__main__':
    # plt.show()
    plot_subject()
    # plot_citnum()

    plot_year()
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
    for name in sorted(name_labelnum.keys()):
        results[name] = [
            name_labelnum[name][-1], name_labelnum[0], name_labelnum[1]
        ]

    results['ALL'] = [label_num[-1], label_num[0], label_num[1]]

    category_names = ['Domain Specific', 'Normal', 'Inter-disciplinary']

    survey(results, category_names)

    plt.tight_layout()

    plt.savefig('fig/subject_inter_cater.png', dpi=600)


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
    plot_subject()
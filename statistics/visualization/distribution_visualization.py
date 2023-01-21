from pathlib import Path
import matplotlib.pyplot as plt
import numpy


def visualize(paths, labels):
    plt.figure("Model Comparison")
    plt.xlabel('Points')
    plt.ylabel('Number of Games')

    for index in range(len(paths)):
        path = paths[index]
        file_name = Path(path)
        with open(file_name, "r") as file:
            lines = file.readlines()[1:]

        distribution = [0] * 121
        for line in lines:
            _, points = line.split('\t')
            distribution[int(points)] += 1

        plt.plot(range(121), distribution, label=labels[index])

    plt.legend()
    plt.show()


def visualize_bar(paths, names):
    bars = []
    labels = ["0", "1 - 30", "31 - 60", "61 - 89", "90 - 119", "120"]

    x = numpy.arange(len(labels))  # the label locations
    width = 0.95 / len(paths)

    for path in paths:
        file_name = Path(path)
        with open(file_name, "r") as file:
            lines = file.readlines()[1:]

        # 0 | 1 - 30 | 31 - 60 | 61 - 89 | 90 - 119 | 120
        groups = [0] * 6
        for line in lines:
            _, reward = line.split('\t')
            points = int(reward)
            if points == 0:
                groups[0] += 1
            elif points <= 30:
                groups[1] += 1
            elif points <= 60:
                groups[2] += 1
            elif points < 90:
                groups[3] += 1
            elif points < 120:
                groups[4] += 1
            elif points == 120:
                groups[5] += 1
            else:
                raise

        bars += [groups]

    fig, ax = plt.subplots(figsize=(10, 12))
    # plt.figure("Model Comparison: Reward Steps", figsize=(1, 4))
    plt.xlabel('Points')
    plt.ylabel('Number of Games')

    rects = []
    for index in range(len(paths)):
        bar = bars[index]
        rects += [ax.bar(x + index * width - len(paths) * width / 2, bar, width, label=names[index])]

    ax.set_xticks(x, labels)
    ax.legend()

    fig.tight_layout()
    plt.show()


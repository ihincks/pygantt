#!/usr/bin/env python3

import matplotlib.pyplot as plt
from collections import OrderedDict
import argparse
import time
import os

class FileWatcher:
    def __init__(self, filepath):
        self.old_content = None
        self.filepath = os.path.abspath(filepath)

    @property
    def has_changed(self):
        try:
            with open(self.filepath, "r") as f:
                content = f.read()
        except FileNotFoundError:
            return False
        out = content != self.old_content
        self.old_content = content
        return out

def parse_csv(filepath):
    data = OrderedDict()

    def maybe_to_num(val):
        try:
            return float(val)
        except:
            return val

    with open(filepath, "r") as f:
        current_section = None
        for line in f.readlines():
            line = line.strip()
            if len(line) <= 1 or line.startswith("#"):
                pass
            elif line.startswith("*"):
                current_section = line[1:].strip()
                data[current_section] = []
            else:
                start, finish, item = line.split(",")
                data[current_section].append(
                    [maybe_to_num(start), maybe_to_num(finish), item]
                )
    return data


class Gantt(object):
    """
    Helps plot Gantt charts.

    :param data: An ordered dictionary, where keys are sections (each section)
        gets its own color) and values are lists of triples
        `[(start, stop, label), (start, stop, label), ...]`
        specifying start and stop times with given labels.
        Alternatively, this argument can specify a filepath pointing to a CSV
        file where sections are lines that start with a *:

            *Phase 1
            0, 3, This is the first task and will take forever
            3, 6, This is another task

            *Phase 2
            2, 9, This is the second task and will take even long
            1, 7, This is not a banana
    :param ax: The axis to plot on. If `None` uses current axis.
    """

    def __init__(self, data, ax=None):
        if isinstance(data, str):
            data = parse_csv(data)
        self.data = data
        self._ax = ax

        self.ytick_fontsize = 14
        self.xtick_fontsize = 14
        self.xlabel_fontsize = 14
        self.legend_fontsize = 14
        self.colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

    @property
    def ax(self):
        return plt.gca() if self._ax is None else self._ax

    def _plot_bar(self, ypos, start, finish, color):
        return self.ax.barh(
            ypos,
            finish - start,
            left=start,
            height=0.5,
            align="center",
            color=color,
            alpha=0.7,
        )

    def plot(self):
        ylabels = []
        colors = iter(self.colors)
        legend_items = OrderedDict()
        for section_title, section in self.data.items():
            color = next(colors)
            for start, finish, item in section:
                handle = self._plot_bar(len(ylabels), start, finish, color)
                ylabels.append(item)
                legend_items[section_title] = handle
        # x-axis
        self.ax.xaxis.label.set_size(self.xlabel_fontsize)
        plt.setp(self.ax.get_xticklabels(), fontsize=self.xtick_fontsize)
        self.ax.grid(which="major", axis="x", linestyle="--", alpha=0.5)

        # y-axis
        self.ax.set_yticks(range(len(ylabels)))
        self.ax.set_yticklabels(
            ylabels,
            fontdict={
                "fontsize": self.ytick_fontsize,
                "verticalalignment": "center",
                "horizontalalignment": "right",
            },
        )
        self.ax.invert_yaxis()

        # legend
        plt.legend(
            legend_items.values(), legend_items.keys(), fontsize=self.legend_fontsize
        )

        # remove frame
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        plt.tick_params(top=False, bottom=False, left=False, right=False)


parser = argparse.ArgumentParser(prog="pygantt")
parser.add_argument("file", help="Path to sectioned CSV file.")
parser.add_argument("-c", "--continuous", default=False, help="Whether to keep the program alive and look for file changes every second.", action="store_true")
parser.add_argument("-o", "--output", default="gantt.png", help="Output filename.")
parser.add_argument("--width", default=10, help="Width of output in inches.")
parser.add_argument("--height", default=4, help="Height of output in inches.")

if __name__ == "__main__":
    args = parser.parse_args()

    file_watcher = FileWatcher(args.file)

    while True:
        if file_watcher.has_changed:
            print("Parsing {}...".format(args.file))
            g = Gantt(args.file)

            print("Plotting figure...")
            fig = plt.figure(figsize=(args.width, args.height))
            g.plot()
            fig.tight_layout()

            print("Saving to {}...".format(args.output))
            fig.savefig(args.output)
            if args.continuous:
                print("Waiting for changes...")
                time.sleep(1)
            else:
                break

        

    print("Done.")

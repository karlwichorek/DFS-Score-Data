"""
This program will help determine player types. Different player types are better
for different types of games, ex: in general you want more consistent players
in your cash games and maybe some not-so-consistent players with more upside in
GPPs.

Run this program in mode 'print' or 'csv' to either print the results from the
console or write them to a csv file.
"""

import csv
import argparse
import numpy as np
from lib.DB import DB
import studies.player_histogram as player_histogram


def get_args():
    opt = argparse.ArgumentParser(prog='player_scores')

    opt.add_argument("-m", "--mode",
                     type=str,
                     required=True,
                     choices=['csv', 'print', 'plot'],
                     help='Prints or writes csv file for data on the player scores.')

    opt.add_argument("-i", "--ids",
                     type=int,
                     nargs='+',
                     help="""Enter player ids to plot point distributions for.
                     Format = ints separated by spaces.""")

    return opt.parse_args()


def get_data():
    database = DB()

    q = "SELECT first_name, last_name, rguru_id FROM player_ids WHERE rguru_id IS NOT NULL"
    ids = database.query(q)

    results = []
    for (fname, lname, id_) in ids:
        q = "SELECT dk_pts FROM rguru_hitters WHERE id=%s"
        scores = [float(x[0]) for x in database.query(q, (str(id_),)) if x[0] is not None]
        # dont count if not enough sample size.
        if len(scores) < 30:
            continue
        mean = np.mean(scores)
        # only look at players w/ avg score > 4
        if mean < 4:
            continue
        stdev = np.std(scores)
        results.append((
            fname,
            lname,
            id_,
            round(mean, 2),
            round(stdev, 2),
            round((mean/stdev), 2)
        ))

    return sorted(results, key=lambda x: x[5], reverse=True)


def print_table(data, headers=None):
    padding = 2
    col_widths = [max([len(str(field[col])) for field in data]) + padding for col in range(len(data[0]))]
    if headers:
        header_line = ''
        for n, col in enumerate(headers):
            header_line += col.ljust(col_widths[n])
        print header_line
        print ''.join(['='] * (sum(col_widths)))
    for row in data:
        line = ''
        for n, field in enumerate(row):
            if type(field) is not str:
                field = format(field, '.2f')
            line += str(field).ljust(col_widths[n])
        print line


def write_csv(data, headers=None):
    with open('scores_data.csv', 'w') as f:
        writer = csv.writer(f)
        if headers:
            writer.writerow(headers)
        for row in data:
            writer.writerow(row)


def main():
    args = get_args()
    headers = ['fname', 'lname', 'id', 'mean', 'stdev', 'ratio']
    results = get_data()
    if args.mode == 'print':
        print_table(results, headers)
    elif args.mode == 'csv':
        write_csv(results, headers)
    elif args.mode == 'plot':
        if hasattr(args, 'ids'):
            player_histogram.MakePlots(args.ids)
        else:
            print 'No player ids entered. Enter player ids (ints separated by spaces) following -i arg.'
    else:
        return


if __name__ == '__main__':
    main()
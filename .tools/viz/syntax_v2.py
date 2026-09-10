#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

import sys
import os
import argparse

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from project_root import get_project_root

root = get_project_root()

data_path = root / '.tools/target/nodes_in_scripts_v2.csv'

special_commands = ['eval', 'alias']

node_types = """
pipeline
background
subshell_command
while_command
for_command
case_command
if_command
and_command
or_command
negate_command
function_command
assignment
variable_use
file_redirection
dup_redirection
heredoc_redirection
home_tilde_control
dollar_paren_shell_control
dollar_paren_paren_arith_control
""".strip().split("\n") + special_commands

# Omitted because they do not seem to be useful:
# ---
# redirection
# raw_command
# escaped_char
# quoted_control

nodes_to_omit = [
    'redirection',
    'raw_command',
    'escaped_char',
    'quoted_control'
]

node_rename_map = {
    'home_tilde_control': 'home_tilde',
    'dollar_paren_shell_control': '$(substitution)',
    'dollar_paren_paren_arith_control': '$((arithmetic))',
    'file_redirection': 'file_redir',
    'dup_redirection': 'dup_redir',
    'heredoc_redirection': 'heredoc_redir',
}

node_order = [
    'command',
    'pipeline',
    'variable_use',
    'assignment',
    'function',
    '$(substitution)',
    #'$((arithmetic))',
    'file_redir',
    'dup_redir',
    'heredoc_redir',
    'negate',
    'or',
    'and',
    'if',
    'case',
    'for',
    'while',
]


def normalize_node_name(node):
    renamed = node_rename_map.get(node, node)
    return renamed.replace('_command', '')


def df_map(df, func):
    if hasattr(df, 'map'):
        return df.map(func)
    return df.applymap(func)


def node_heatmap(df, outdir=None):
    heatmap_data = pd.DataFrame(
        index=list(map(normalize_node_name, node_types)),
        columns=df['benchmark']
    )

    for _, row in df.iterrows():
        for node, count in row['nodes'].items():
            if node not in nodes_to_omit:
                heatmap_data.at[
                    normalize_node_name(node),
                    row['benchmark']
                ] = count

    heatmap_data = heatmap_data.fillna(0)

    limit = 5

    # Compute ALL column from original uncapped data
    all_totals = heatmap_data.sum(axis=1)

    annot_data = df_map(
        heatmap_data,
        lambda x: '*' if x > limit else ''
    )

    heatmap_data = df_map(
        heatmap_data,
        lambda x: min(x, limit)
    )

    # Order the y-axis according to node_order.
    # Any nodes not in node_order appear first.
    heatmap_data = heatmap_data.loc[
        [x for x in heatmap_data.index if x not in node_order]
        + list(reversed(node_order))
    ]

    annot_data = annot_data.loc[heatmap_data.index]

    all_totals = all_totals.loc[heatmap_data.index]

    # Sort categories alphabetically
    heatmap_data = heatmap_data[
        sorted(heatmap_data.columns)
    ]

    annot_data = annot_data[
        heatmap_data.columns
    ]

    # Add ALL column using original uncapped totals
    heatmap_data['ALL'] = all_totals

    annot_data['ALL'] = all_totals.apply(
        lambda x: '*' if x > limit else ''
    )

    # Cap ALL column for visualization
    heatmap_data = df_map(
        heatmap_data,
        lambda x: min(x, limit)
    )

    plt.figure(figsize=(7, 6.5))

    sns.heatmap(
        heatmap_data,
        cmap='Reds',
        annot=annot_data,
        fmt='',
        cbar_kws={
            'label': 'Occurrences (* denotes more than 5)',
            'location': 'top'
        }
    )

    plt.xlabel('')
    plt.xticks(rotation=45, ha='right')
    plt.ylabel('')
    plt.title('')
    plt.subplots_adjust(bottom=0.25)
    plt.tight_layout()

    if outdir:
        os.makedirs(outdir, exist_ok=True)
        out_pdf = os.path.join(outdir, 'corpus-syntax-analysis_v2.pdf')
        alt_pdf = os.path.join(outdir, 'corpus-syntax-analysis-v2.pdf')
        try:
            plt.rcParams.update({
                "text.usetex": True,
                "font.family": "serif",
                "font.serif": ["Times New Roman"],
            })
            plt.savefig(out_pdf)
        except Exception:
            plt.rcParams.update({
                "text.usetex": False,
                "font.family": "serif",
            })
            plt.savefig(out_pdf)

        try:
            import shutil
            shutil.copyfile(out_pdf, alt_pdf)
        except Exception:
            pass
    else:
        plt.show()


def extract_special_command(node):
    for sc in special_commands:
        if node == f'command({sc})':
            return sc

    return node


def merge_node_counts(series):
    merged_dict = {}

    for d in series:
        for k, v in d.items():
            merged_dict[k] = merged_dict.get(k, 0) + v

    return merged_dict


def read_data(merge_commands=True):
    target_path = data_path
    if not target_path.is_file():
        alt = Path(__file__).resolve().parent.parent / 'target' / 'nodes_in_scripts_v2.csv'
        if alt.is_file():
            target_path = alt

    df = pd.read_csv(
        target_path,
        header=None
    )

    # v2 format:
    # script,category,nodes
    df.columns = [
        'script',
        'benchmark',
        'nodes'
    ]

    # Parse node counts.
    # Empty nodes correspond to scripts that could not be parsed.
    df['nodes'] = df['nodes'].apply(
        lambda x: dict(
            [
                tuple(i.rsplit(':', 1))
                for i in x.split(';')
            ]
        )
        if isinstance(x, str) and x
        else {}
    )

    # Convert counts from strings to integers and
    # extract special commands such as eval and alias.
    df['nodes'] = df['nodes'].apply(
        lambda x: {
            extract_special_command(k): int(v)
            for k, v in x.items()
        }
    )

    if merge_commands:
        # Merge all command(...) nodes.
        # We do not care about individual commands here.
        df['nodes'] = df['nodes'].apply(
            lambda x: {
                k: v
                for k, v in x.items()
                if 'command(' not in k
            }
            | {
                'command': sum(
                    v
                    for k, v in x.items()
                    if 'command(' in k
                )
            }
        )

    # Aggregate by category
    bench_df = (
        df.groupby('benchmark')
        .agg({'nodes': merge_node_counts})
        .reset_index()
    )

    return df, bench_df


def main(outdir=None):
    _, df = read_data()
    node_heatmap(df, outdir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate node heatmap.'
    )

    parser.add_argument(
        'args',
        nargs='*',
        help='Optional arguments: [output_dir] or [corpus_path, output_dir]'
    )

    parsed = parser.parse_args()
    outdir = None
    if len(parsed.args) >= 2:
        outdir = parsed.args[1]
    elif len(parsed.args) == 1:
        outdir = parsed.args[0]

    main(outdir)
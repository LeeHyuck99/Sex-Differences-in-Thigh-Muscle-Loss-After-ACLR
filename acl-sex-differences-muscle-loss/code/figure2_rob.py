#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 2 — Risk of bias across the eight included studies (ROBINS-E, sex as exposure).

(A) 연구별 도메인 수준 합의 판정.
(B) 도메인별 판정 분포.

색만으로 구분하지 않도록 각 칸에 기호를 함께 찍는다 (+ 낮음, ? 일부 우려, − 높음).
양식은 Figure 3 (forest_paper2.py) 와 동일하게 맞춘다.
"""
import json

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

ROWS = json.load(open('/home/claude/rob_data.json'))
OVERALL = json.load(open('/home/claude/rob_overall.json'))

# 연구 순서 — Table 1 과 같은 수술 후 시점 순
STUDIES = ['Iversen 2016', 'Kandil 2023', 'Lindström 2013', 'Raymond-Pope 2021',
           'Longo 2014', 'Ito 2025', 'Morgan 2026', 'Harput 2023']
DOMS = ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']
DOM_LABEL = {
    'D1': 'Confounding',
    'D2': 'Measurement of the exposure',
    'D3': 'Selection of participants',
    'D4': 'Post-exposure interventions',
    'D5': 'Missing data',
    'D6': 'Measurement of the outcome',
    'D7': 'Selection of the reported result',
}

INK, INK2, GRID, SURFACE = '#0b0b0b', '#52514e', '#d8d7d2', '#ffffff'
COL = {'low': '#0ca30c', 'some': '#fab219', 'high': '#d03b3b', 'vhigh': '#7a1414'}
SYM = {'low': '+', 'some': '?', 'high': '−', 'vhigh': '−−'}
FG = {'low': 'white', 'some': '#3d2a00', 'high': 'white', 'vhigh': 'white'}
ORDER = ['low', 'some', 'high', 'vhigh']
NAME = {'low': 'Low risk of bias', 'some': 'Some concerns',
        'high': 'High risk of bias', 'vhigh': 'Very high risk of bias'}

mpl.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 7.6,
    'axes.linewidth': 0.8,
    'pdf.fonttype': 42, 'ps.fonttype': 42,
})

GRIDMAP = {(r['study'], r['dom']): r['cons'] for r in ROWS}
OV = {s: ('high' if 'High' in OVERALL[s] else
          'vhigh' if 'Very' in OVERALL[s] else
          'some' if 'Some' in OVERALL[s] else 'low') for s in STUDIES}


def cell(ax, x, y, kind, w=0.86, h=0.74):
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, fc=COL[kind],
                           ec=SURFACE, lw=1.1, zorder=2))
    ax.text(x, y, SYM[kind], ha='center', va='center', fontsize=7.6,
            fontweight='bold', color=FG[kind], zorder=3)


def panel_a(ax):
    ax.set_facecolor(SURFACE)
    n, m = len(STUDIES), len(DOMS)
    for i, st in enumerate(STUDIES):
        for j, d in enumerate(DOMS):
            cell(ax, j, i, GRIDMAP[(st, d)])
        cell(ax, m + 0.42, i, OV[st])
    ax.set_xlim(-0.65, m + 1.05)
    ax.set_ylim(n - 0.5, -1.35)
    ax.set_yticks(range(n))
    ax.set_yticklabels(STUDIES, fontsize=7.4, color=INK)
    ax.set_xticks(list(range(m)) + [m + 0.42])
    ax.set_xticklabels(DOMS + ['Overall'], fontsize=7.4, color=INK)
    ax.xaxis.set_ticks_position('top')
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(length=0)
    ax.annotate('A', xy=(-0.345, -1.30), xycoords=('axes fraction', 'data'),
                fontsize=10.5, fontweight='bold', color=INK,
                annotation_clip=False)


def panel_b(ax):
    ax.set_facecolor(SURFACE)
    n = len(DOMS)
    for i, d in enumerate(DOMS):
        counts = {k: 0 for k in ORDER}
        for st in STUDIES:
            counts[GRIDMAP[(st, d)]] += 1
        left = 0.0
        for k in ORDER:
            if not counts[k]:
                continue
            pct = 100 * counts[k] / len(STUDIES)
            ax.add_patch(Rectangle((left, i - 0.33), pct, 0.66, fc=COL[k],
                                   ec=SURFACE, lw=1.1, zorder=2))
            if pct >= 12:
                ax.text(left + pct / 2, i, '%d' % counts[k], ha='center',
                        va='center', fontsize=6.8, fontweight='bold',
                        color=FG[k], zorder=3)
            left += pct
    ax.set_xlim(0, 100)
    ax.set_ylim(n - 0.5, -0.9)
    ax.set_yticks(range(n))
    ax.set_yticklabels(['%s  %s' % (d, DOM_LABEL[d]) for d in DOMS],
                       fontsize=7.2, color=INK)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(['0', '25', '50', '75', '100'], color=INK2)
    for sp in ('top', 'right', 'left'):
        ax.spines[sp].set_visible(False)
    ax.spines['bottom'].set_color(GRID)
    ax.tick_params(axis='x', length=3, color=GRID, labelsize=7.0)
    ax.tick_params(axis='y', length=0)
    ax.set_xlabel('Studies (%)', fontsize=7.6, color=INK, labelpad=4)
    ax.annotate('B', xy=(-0.345, -0.86), xycoords=('axes fraction', 'data'),
                fontsize=10.5, fontweight='bold', color=INK,
                annotation_clip=False)


def main():
    fig = plt.figure(figsize=(8.6, 5.6), facecolor=SURFACE)
    axA = fig.add_axes([0.272, 0.545, 0.648, 0.385])
    axB = fig.add_axes([0.272, 0.125, 0.648, 0.330])
    panel_a(axA)
    panel_b(axB)
    used = [k for k in ORDER if any(GRIDMAP[(s, d)] == k
                                    for s in STUDIES for d in DOMS)]
    handles = [Line2D([], [], marker='s', ls='none', ms=8, mfc=COL[k],
                      mec=SURFACE, mew=1.1, label='%s  (%s)' % (NAME[k], SYM[k]))
               for k in used]
    fig.legend(handles=handles, loc='lower left', bbox_to_anchor=(0.272, 0.008),
               frameon=False, ncol=3, fontsize=6.9, labelcolor=INK2,
               handletextpad=0.5, columnspacing=1.8)
    fig.savefig('/home/claude/Figure_2.eps', format='eps', facecolor=SURFACE)
    fig.savefig('/home/claude/Figure_2.pdf', facecolor=SURFACE)
    fig.savefig('/home/claude/Figure_2.png', dpi=600, facecolor=SURFACE)
    print('saved Figure_2 (eps vector, pdf, png @600dpi)')


if __name__ == '__main__':
    main()

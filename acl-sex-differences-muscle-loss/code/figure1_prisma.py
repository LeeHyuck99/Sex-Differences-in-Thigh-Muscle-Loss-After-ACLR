#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Figure 1 — PRISMA 2020 flow diagram.

모든 수치는 up/screening.xlsx (PRISMA_flow, Exclusion_reasons 시트) 에서
읽어온 값이며, 아래 검산을 통과한다:
  24 340 + 0 - 11 479 - 0 = 12 861 ; 12 861 - 12 502 = 359
  359 - 0 = 359 ; 359 - 351 = 8 ; 제외 사유 11건 합계 = 351
양식(글꼴·색·선 두께)은 Figure 2, Figure 3 과 동일.
전체 제외 사유 문구는 Supplementary file 8 — 여기서는 축약 문구를 쓴다.
세로 좌표는 박스 높이에서 계산하므로 잘림이 생기지 않는다.
"""
import json

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow, Rectangle

D = json.load(open('/home/claude/prisma_data.json'))
F = D['flow']

INK, INK2, GRID, SURFACE = '#0b0b0b', '#52514e', '#d8d7d2', '#ffffff'
BOXFC, BAND = '#fafaf8', '#f2f1ec'

mpl.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 7.6,
    'axes.linewidth': 0.8,
    'pdf.fonttype': 42, 'ps.fonttype': 42,
})


def g(key):
    return F[key]


def sp(n):
    """British house style — thin space as the thousands separator."""
    return format(n, ',').replace(',', ' ')


# 그림용 축약 문구. 전문은 Supplementary file 8.
SHORT = {
    'E1': 'Cohort mean age outside 15–39 years',
    'E2': 'Procedure not ACL reconstruction',
    'E3': 'Arthroplasty, revision or prior index-joint surgery',
    'E4': 'Results not reported separately by sex',
    'E5': 'No effect estimate or dispersion derivable',
    'E6': 'No eligible postoperative timepoint',
    'E7': 'No eligible comparator could be constructed',
    'E10': 'No eligible control arm',
    'E11': 'Study design not eligible',
    'E15': 'No eligible measure of muscle mass',
    'E16': 'Cohort not athletic, or activity level not reported',
}

STAGE_X0, STAGE_X1 = 0.0, 6.2
MX0, MX1 = 9.6, 48.5
SX0, SX1 = 54.5, 100.0
MXC = (MX0 + MX1) / 2

LINE, TIGHT = 2.85, 2.35       # 본문 줄 높이 / 제외 사유 줄 높이
PADT, PADB = 2.6, 2.2
GAP = 8.0                      # 세로 화살표 구간


def ln(txt, lh=LINE, fs=7.4, bold=False):
    return dict(txt=txt, lh=lh, fs=fs, bold=bold)


def height(lines):
    return PADT + PADB + sum(l['lh'] for l in lines)


def box(ax, x0, x1, y0, lines):
    h = height(lines)
    ax.add_patch(Rectangle((x0, y0), x1 - x0, h, fc=BOXFC, ec=GRID,
                           lw=0.9, zorder=2))
    y = y0 + PADT
    for k, l in enumerate(lines):
        ax.text(x0 + 2.0, y, l['txt'], ha='left', va='top', zorder=3,
                fontsize=l['fs'], fontweight='bold' if l['bold'] else 'normal',
                color=INK if l['bold'] else INK2)
        y += l['lh']
    return (y0, y0 + h)


def vdown(ax, x, y0, y1):
    ax.add_patch(FancyArrow(x, y0, 0, y1 - y0 - 1.5, width=0.12,
                            head_width=1.5, head_length=1.5, fc=INK2,
                            ec=INK2, lw=0, length_includes_head=True,
                            zorder=4))


def hright(ax, y, x0, x1):
    ax.add_patch(FancyArrow(x0, y, x1 - x0 - 1.4, 0, width=0.12,
                            head_width=1.5, head_length=1.4, fc=INK2,
                            ec=INK2, lw=0, length_includes_head=True,
                            zorder=4))


def stage(ax, y0, y1, label):
    ax.add_patch(Rectangle((STAGE_X0, y0), STAGE_X1 - STAGE_X0, y1 - y0,
                           fc=BAND, ec='none', zorder=1))
    ax.text((STAGE_X0 + STAGE_X1) / 2, (y0 + y1) / 2, label, ha='center',
            va='center', rotation=90, fontsize=8.0, fontweight='bold',
            color=INK, zorder=3)


def build():
    L1 = [ln('Records identified', bold=True),
          ln('Databases (n = %s)' % sp(g('Records identified from databases'))),
          ln('Citation searching (n = %s)'
             % sp(g('Records identified from citation searching / hand search')))]
    R1 = [ln('Records removed before screening', bold=True),
          ln('Duplicate records (n = %s)'
             % sp(g('Records removed before screening: duplicates'))),
          ln('Marked ineligible by automation (n = 0)'),
          ln('Removed for other reasons (n = %s)'
             % sp(g('Records removed before screening: other reasons')))]
    L2 = [ln('Records screened', bold=True),
          ln('(n = %s)' % sp(g('Records screened (title and abstract)')))]
    R2 = [ln('Records excluded at title and abstract', bold=True),
          ln('(n = %s)' % sp(g('Records excluded (title and abstract)')))]
    L3 = [ln('Reports sought for retrieval', bold=True),
          ln('(n = %s)' % sp(g('Reports sought for retrieval')))]
    R3 = [ln('Reports not retrieved', bold=True),
          ln('(n = %s)' % sp(g('Reports not retrieved')))]
    L4 = [ln('Reports assessed for eligibility', bold=True),
          ln('(n = %s)' % sp(g('Reports assessed for eligibility (full text)')))]
    R4 = [ln('Reports excluded (n = %s)'
             % sp(g('Reports excluded, with reasons')), bold=True)]
    R4 += [ln('%s  %s (n = %d)' % (c, SHORT[c], n), lh=TIGHT, fs=6.9)
           for c, _, n in D['reasons']]
    L5 = [ln('Studies included in review', bold=True),
          ln('(n = %d)' % g('Studies included in review')),
          ln('Reports of included studies (n = %d)'
             % g('Reports of included studies'))]
    return [L1, R1, L2, R2, L3, R3, L4, R4, L5]


def main():
    L1, R1, L2, R2, L3, R3, L4, R4, L5 = build()

    y1 = 2.0
    y2 = y1 + height(L1) + GAP
    y3 = y2 + height(L2) + GAP
    y4 = y3 + height(L3) + GAP
    y5 = max(y4 + height(L4) + GAP, y4 + height(R4) + 4.6)
    total = y5 + height(L5) + 2.4

    axw, axh = 0.952, 0.978
    figw = 8.3
    units_per_in = 100.0 / (axw * figw)
    figh = total / units_per_in / axh

    fig = plt.figure(figsize=(figw, figh), facecolor=SURFACE)
    ax = fig.add_axes([(1 - axw) / 2, (1 - axh) / 2, axw, axh])
    ax.set_facecolor(SURFACE)
    ax.set_xlim(0, 100)
    ax.set_ylim(total, 0)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)

    b1 = box(ax, MX0, MX1, y1, L1); s1 = box(ax, SX0, SX1, y1, R1)
    b2 = box(ax, MX0, MX1, y2, L2); box(ax, SX0, SX1, y2, R2)
    b3 = box(ax, MX0, MX1, y3, L3); box(ax, SX0, SX1, y3, R3)
    b4 = box(ax, MX0, MX1, y4, L4); s4 = box(ax, SX0, SX1, y4, R4)
    b5 = box(ax, MX0, MX1, y5, L5)

    for a, b in ((b1, b2), (b2, b3), (b3, b4), (b4, b5)):
        vdown(ax, MXC, a[1], b[0])
    for b in (b1, b2, b3, b4):
        hright(ax, (b[0] + b[1]) / 2, MX1, SX0)

    stage(ax, y1 - 0.8, s1[1] + 0.8, 'Identification')
    stage(ax, y2 - 0.8, s4[1] + 0.8, 'Screening')
    stage(ax, b5[0] - 0.8, b5[1] + 0.8, 'Included')

    ax.text(SX0, s4[1] + 2.2,
            'Full wording of every exclusion reason is given in\n'
            'Supplementary file 8.', ha='left', va='top', fontsize=6.4,
            color=INK2, style='italic', zorder=3, linespacing=1.5)

    for ext, kw in (('png', dict(dpi=600)), ('pdf', {}),
                    ('eps', dict(format='eps'))):
        fig.savefig('/home/claude/Figure_1.%s' % ext, facecolor=SURFACE, **kw)
    print('saved Figure_1 .eps .pdf .png  (%.2f x %.2f in)' % (figw, figh))

    assert (g('Records identified from databases')
            + g('Records identified from citation searching / hand search')
            - g('Records removed before screening: duplicates')
            - g('Records removed before screening: other reasons')
            == g('Records screened (title and abstract)'))
    assert (g('Records screened (title and abstract)')
            - g('Records excluded (title and abstract)')
            == g('Reports sought for retrieval'))
    assert (g('Reports sought for retrieval') - g('Reports not retrieved')
            == g('Reports assessed for eligibility (full text)'))
    assert (g('Reports assessed for eligibility (full text)')
            - g('Reports excluded, with reasons')
            == g('Studies included in review'))
    assert sum(n for _, _, n in D['reasons']) == g('Reports excluded, with reasons')
    print('flow arithmetic and reason total verified')


if __name__ == '__main__':
    main()

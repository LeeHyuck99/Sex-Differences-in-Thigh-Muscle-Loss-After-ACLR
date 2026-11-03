#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figure 2 — forest plot (단독 실행본)
Paper 2: 성별에 따른 ACL 재건술 후 근육량 손실 · PROSPERO CRD420261498739

    python forest_paper2.py

출력:  Figure2_forest.png (600 dpi)  ·  Figure2_forest.pdf (벡터, 투고용)
필요 패키지:  matplotlib

수치에 대하여
-------------
이 파일은 meta_paper2.py 를 import 하지 않고 확정된 값을 그대로 들고 있습니다.
엑셀이나 분석 스크립트 없이도 그림이 재현되도록 하기 위함입니다.
분석을 다시 돌려 값이 바뀌면 아래 ARMS / POOLED 를 함께 고치십시오.

열 구성 (v3)
------------
Study · n and timepoint · Muscle · Measure · Comparator · 플롯 · RoM (95% CI)
  · Muscle   : 어느 근육을 쟀는가
  · Measure  : 어떤 기법으로 어떤 양을 쟀는가
  · Comparator: 수술측을 무엇에 견주었는가 (이전 'Reference' 열)
"""
from __future__ import annotations

import math

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon

# ------------------------------------------------------------------ 스타일
MALE, FEMALE, INK = '#2a78d6', '#eb6834', '#1a1a1a'
MUTED, GRID, SURFACE = '#6b6b6b', '#d8d8d6', '#fcfcfb'
COL = {'M': MALE, 'F': FEMALE, 'X': INK}

mpl.rcParams.update({
    'font.family': 'DejaVu Sans',
    'figure.facecolor': SURFACE,
    'axes.facecolor': SURFACE,
    'savefig.facecolor': SURFACE,
    'axes.edgecolor': GRID,
    'text.color': INK,
})

TICKS = [0.80, 0.85, 0.90, 0.95, 1.00, 1.05]
XLIM = (0.78, 1.07)
MS_MAX = 15.0        # 가장 무거운 arm 의 표식 지름(pt)

# ---- 11개 주 arm.
#  (연구, 성별, n, 시점, 근육, 측정, 비교자, RoM, lo, hi, 가중치%)
#  가중치 = 임의절편 메타회귀(REML)에서 해당 arm 이 받는 1/(v+tau^2) 가중치를
#           성별 층 안에서 백분율로 환산한 값. 층 안에서 합이 100.
#           출처: forest_plot_paper2.py (추출 엑셀이 있던 시점의 분석 산출물)
ARMS = [
    # 남성 — 시점 순
    ('Iversen 2016',      'M',  7, '16 d',  'Quadriceps',       'MRI · CSA',
     'preoperative',  0.878, 0.862, 0.894, 15.7),
    ('Kandil 2023',       'M', 60, '6–8 mo', 'Quadriceps (RF+VI)','US · thickness',
     'preoperative',  0.914, 0.887, 0.943, 14.0),
    ('Lindström 2013',    'M', 23, '12 mo', 'Quadriceps',       'CT · CSA',
     'contralateral', 0.957, 0.918, 0.997, 12.4),
    ('Longo 2014',        'M', 23, '2.2 yr', 'Quadriceps (RF+VI)','US · thickness',
     'contralateral', 0.869, 0.834, 0.904, 12.6),
    ('Ito 2025',          'M', 30, '2.3 yr', 'Vastus lateralis', 'MRI · volume',
     'contralateral', 0.965, 0.941, 0.989, 14.8),
    ('Morgan 2026',       'M', 14, '2.6 yr', 'Thigh muscle',     'pQCT · CSA',
     'contralateral', 0.962, 0.944, 0.980, 15.6),
    ('Harput 2023',       'M', 42, '2.7 yr', 'Vastus lateralis', 'US · thickness',
     'contralateral', 0.958, 0.936, 0.981, 15.0),
    # 여성 — 시점 순
    ('Iversen 2016',      'F',  5, '16 d',  'Quadriceps',       'MRI · CSA',
     'preoperative',  0.857, 0.815, 0.901, 13.9),
    ('Lindström 2013',    'F', 14, '12 mo', 'Quadriceps',       'CT · CSA',
     'contralateral', 0.916, 0.877, 0.958, 17.9),
    ('Raymond-Pope 2021', 'F', 12, '13 mo', 'Anterior thigh',   'DXA · lean mass',
     'contralateral', 0.925, 0.876, 0.977, 11.9),
    ('Morgan 2026',       'F', 18, '2.6 yr', 'Thigh muscle',     'pQCT · CSA',
     'contralateral', 0.923, 0.900, 0.946, 56.3),
]

POOLED = {
    # (est, lo, hi, k, 이질성 한 줄, 예측구간 or None)
    'M': (0.943, 0.900, 0.989, 7,
          'Q = 27.40, df = 5, p < 0.001  \u00b7  I\u00b2 = 81.8%',
          (0.850, 1.046)),
    'F': (0.922, 0.882, 0.964, 4,
          'Q = 0.10, df = 2, p = 0.95  \u00b7  I\u00b2 = 0%',
          None),
}
RATIOS = [
    ('All arms, model-based', '11 arms / 8 studies', 0.965, 0.938, 0.992),
    ('Within-study contrasts', '3 studies',          0.963, 0.912, 1.016),
]


# ------------------------------------------------------------------ 행 만들기
def build_rows():
    rows = []
    for sex, label in (('M', 'Men'), ('F', 'Women')):
        rows.append(dict(kind='head', text=label))
        for st, sx, n, tp, mus, meas, comp, est, lo, hi, wt in ARMS:
            if sx != sex:
                continue
            rows.append(dict(
                kind='study', sex=sex, label=st,
                meta='n = %d · %s' % (n, tp),
                muscle=mus, measure=meas, comp=comp,
                est=est, lo=lo, hi=hi, wt=wt))
        est, lo, hi, k, het, pi = POOLED[sex]
        rows.append(dict(kind='diamond', sex=sex, label='Model estimate',
                         meta='k = %d' % k, muscle='', measure='',
                         comp='at contralateral reference',
                         est=est, lo=lo, hi=hi, pi=pi))
        rows.append(dict(kind='het', sex=sex, text=het,
                         pi=('95%% prediction interval %.3f to %.3f' % pi) if pi else ''))
        rows.append(dict(kind='gap'))
    rows.append(dict(kind='rule'))
    rows.append(dict(kind='head', text='Female : male ratio of ratios'))
    for lab, note, est, lo, hi in RATIOS:
        rows.append(dict(kind='diamond', sex='X', label=lab, meta=note,
                         muscle='', measure='', comp='ratio of ratios',
                         est=est, lo=lo, hi=hi, pi=None))
    return rows


def diamond(ax, y, est, lo, hi, color, h=0.30):
    ax.add_patch(Polygon([(lo, y), (est, y - h), (hi, y), (est, y + h)],
                         closed=True, facecolor=color, edgecolor=SURFACE,
                         lw=0.8, zorder=4))


# ------------------------------------------------------------------ 그리기
def draw(out='Figure2_forest'):
    rows = build_rows()
    n = len(rows)

    fig = plt.figure(figsize=(16.0, 0.40 * n + 2.5))
    ax = fig.add_axes([0.455, 0.165, 0.345, 0.775])
    T = ax.get_yaxis_transform()        # x = 데이터, y = 축 좌표

    # 열 위치 (축 좌표). 플롯 영역이 0~1.
    X_STUDY, X_META, X_MUS, X_MEAS, X_COMP, X_CI, X_WT = \
        -1.385, -0.995, -0.745, -0.470, -0.215, 1.045, 1.690

    ax.set_xlim(*XLIM)
    ax.set_ylim(n - 0.5, -2.0)
    ax.set_yticks([])
    for s in ('left', 'right', 'top'):
        ax.spines[s].set_visible(False)
    ax.spines['bottom'].set_position(('outward', 8))
    ax.set_xticks(TICKS)
    ax.set_xticklabels(['%.2f' % t for t in TICKS], fontsize=10, color=MUTED)
    ax.tick_params(axis='x', length=3, color=GRID, labelcolor=MUTED)

    # 열 제목
    heads = ((X_STUDY, 'Study'), (X_META, 'n \u00b7 timepoint'), (X_MUS, 'Muscle'),
             (X_MEAS, 'Measure'), (X_COMP, 'Comparator'),
             (X_CI, 'Ratio of means (95% CI)'))
    ax.text(X_WT, -1.45, 'Weight', transform=T, ha='right', va='center',
            fontsize=10.5, fontweight='bold')
    for x, t in heads:
        ax.text(x, -1.45, t, transform=T, ha='left', va='center',
                fontsize=10.5, fontweight='bold')
    ax.plot([X_STUDY, X_WT], [-1.15, -1.15], transform=T,
            color=GRID, lw=0.9, clip_on=False, zorder=1)

    ax.axvline(1.0, color=INK, lw=1.0, ls=(0, (5, 4)), alpha=0.75, zorder=1)

    for i, r in enumerate(rows):
        k = r['kind']
        if k == 'gap':
            continue
        if k == 'rule':
            ax.plot([X_STUDY, X_WT], [i, i], transform=T,
                    color=GRID, lw=0.9, clip_on=False, zorder=1)
            continue
        if k == 'head':
            ax.text(X_STUDY, i, r['text'], transform=T, ha='left',
                    va='center', fontsize=11, fontweight='bold')
            continue
        if k == 'het':
            ax.text(X_META, i, r['text'], transform=T, ha='left',
                    va='center', fontsize=9, color=MUTED, style='italic')
            if r['pi']:
                ax.text(X_CI, i, r['pi'], transform=T, ha='left',
                        va='center', fontsize=9, color=MUTED, style='italic')
            continue

        c = COL[r['sex']]
        bold = (k == 'diamond')
        ax.text(X_STUDY + (0.05 if k == 'study' else 0.0), i, r['label'],
                transform=T, ha='left', va='center', fontsize=10.5,
                fontweight='bold' if bold else 'normal')
        for x, key in ((X_META, 'meta'), (X_MUS, 'muscle'),
                       (X_MEAS, 'measure'), (X_COMP, 'comp')):
            if r.get(key):
                ax.text(x, i, r[key], transform=T, ha='left', va='center',
                        fontsize=9.5, color=MUTED)

        if k == 'study':
            ax.plot([r['lo'], r['hi']], [i, i], color=c,
                    lw=2.0, solid_capstyle='butt', zorder=3)
            open_marker = r['comp'] == 'preoperative'
            # 면적 ∝ 모형 가중치이므로 지름 ∝ √가중치.
            # 가중치는 성별 층 안에서 합이 100 이므로 크기도 층 안에서 맞춥니다.
            wmax = max(x['wt'] for x in rows
                       if x['kind'] == 'study' and x['sex'] == r['sex'])
            ms = MS_MAX * (r['wt'] / wmax) ** 0.5
            ax.plot([r['est']], [i],
                    marker='s' if r['sex'] == 'M' else 'o', ms=ms,
                    mfc=SURFACE if open_marker else c, mec=c, mew=1.8,
                    ls='none', zorder=4)
        else:
            if r.get('pi'):
                plo, phi = r['pi']
                ax.plot([plo, phi], [i, i], color=c, lw=1.0, zorder=2,
                        solid_capstyle='butt')
                for xv in (plo, phi):
                    ax.plot([xv, xv], [i - 0.20, i + 0.20], color=c,
                            lw=1.0, zorder=2)
            diamond(ax, i, r['est'], r['lo'], r['hi'], c)
            for xv in (r['lo'], r['hi']):
                ax.plot([xv, xv], [i - 0.12, i + 0.12],
                        color=c, lw=1.0, zorder=3)

        ax.text(X_CI, i, '%.3f (%.3f to %.3f)' % (r['est'], r['lo'], r['hi']),
                transform=T, ha='left', va='center', fontsize=10.5,
                fontweight='bold' if bold else 'normal')
        if k == 'study':
            ax.text(X_WT, i, '%.1f%%' % r['wt'], transform=T, ha='right',
                    va='center', fontsize=10, color=MUTED)

    ax.text(0.33, -0.052, 'greater loss', transform=ax.transAxes,
            ha='center', va='top', fontsize=10, color=MUTED, clip_on=False)
    ax.text(0.765, -0.052, 'no difference', transform=ax.transAxes,
            ha='left', va='top', fontsize=10, color=MUTED, clip_on=False)
    ax.text(0.5, -0.095, 'Ratio', transform=ax.transAxes,
            ha='center', va='top', fontsize=11.5, clip_on=False)

    handles = [
        Line2D([], [], marker='s', ls='none', ms=9, mfc=MALE, mec=MALE,
               label='Men'),
        Line2D([], [], marker='o', ls='none', ms=9, mfc=FEMALE, mec=FEMALE,
               label='Women'),
        Line2D([], [], marker='o', ls='none', ms=9, mfc=SURFACE, mec=MUTED,
               mew=1.8, label='Open marker: vs preoperative'),
        Line2D([], [], marker='D', ls='none', ms=9, mfc=INK, mec=INK,
               label='Model estimate'),
    ]
    fig.legend(handles=handles, loc='lower center', ncol=4, frameon=False,
               fontsize=10.5, bbox_to_anchor=(0.5, 0.012), handletextpad=0.5,
               columnspacing=2.4)

    for ext, kw in (('png', dict(dpi=600)), ('pdf', {}),
                    ('eps', dict(format='eps'))):
        fig.savefig('%s.%s' % (out, ext), facecolor=SURFACE,
                    bbox_inches='tight', **kw)
    print('wrote %s .png .pdf .eps' % out)


if __name__ == '__main__':
    draw()

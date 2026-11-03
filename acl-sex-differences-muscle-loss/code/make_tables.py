#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""nv12 의 표 3개를 BJS 편집자 요구사항에 맞춰 다시 쓴다.

편집자 요구:
  세로(portrait), 최대 10열, a/b/c 분할 금지, 표마다 쪽을 바꾸고 짧은 제목,
  단위는 괄호 안에 (예: Age (years), median (i.q.r.)),
  값의 다수가 한 형식이면 각주에 'Values are ... unless otherwise indicated',
  성별 자료는 'Sex ratio (M:F)' 한 행으로.

같이 고친 것:
  T1  n (M/F) -> No. of patients + Sex ratio (M:F);  ± 표기 제거;
      시점을 개월로 통일(16일과 연 단위는 각주로 환산 근거를 남김).
  T2  'Operated limb' 머리글이 LSI 행에 맞지 않던 문제 -> 'Operated limb or LSI';
      시점 열 신설(각주의 '시점 순 정렬' 주장을 검증 가능하게);
      'Input' 열을 없애고 'Muscle analysed' 를 넣어 Table 1 과의 불일치를 해소
      (Ito 2025 는 38개 근육 중 vastus lateralis, Harput 2022 는 3개 중 vastus
      lateralis 가 분석에 들어갔다);  SD 1 -> 1.0.
  T3  단위를 머리글 괄호로; 반복되는 Study/Timepoint 를 빈칸 대신 다시 적는다.
"""
import json
import math

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml.ns import qn
from docx.shared import Pt, Inches

OUT = '/home/claude/Tables_BJS_nv12.docx'
ARMS = json.load(open('/home/claude/table2_data.json'))

HDR_PT, BODY_PT, NOTE_PT = 8.0, 8.0, 7.5

# ---------------------------------------------------------------- Table 1
T1_HEAD = ['Study', 'Country', 'Design', 'No. of patients', 'Sex ratio (M:F)',
           'Age (years)', 'Graft', 'Modality / muscle measured',
           'Timepoint after surgery (months)', 'Comparator']
T1_ROWS = [
    ['Iversen 2016', 'Norway', 'RCT, control arm', '12', '7:5', '29.8(9.3)',
     'NR', 'MRI / quadriceps ACSA', '0.5†', 'Within-subject'],
    ['Kandil 2023', 'Egypt', 'Prospective cohort', '60', '60:0', '27 (18–35)‡',
     'NR', 'US / quadriceps (RF + VI) thickness', '6–8', 'Within-subject'],
    ['Lindström 2013', 'Sweden', 'Prospective cohort', '37', '23:14',
     '26.5 (16–54)‡', 'STG', 'CT / quadriceps and hamstring CSA', '12',
     'Between-limb'],
    ['Raymond-Pope 2021', 'USA', 'Cross-sectional', '12', '0:12', '16.4(0.9)',
     'NR', 'DXA / upper-leg compartmental lean mass', '13.1(1.7)',
     'Between-limb'],
    ['Longo 2014', 'Italy, UK', 'Cross-sectional', '23', '23:0', '33(7.7)',
     'BPTB', 'US / quadriceps (RF + VI) thickness', '25.9(1.5)',
     'Between-limb'],
    ['Ito 2025', 'USA', 'Cross-sectional', '30', '30:0', '21.0(1.4)',
     'BPTB 25, HT 5', 'MRI / 38 lower-limb muscle volumes', '27.9(19.0)',
     'Between-limb'],
    ['Morgan 2026', 'UK', 'Cross-sectional', '32', '14:18*', '25 (21–32)§',
     'HT 78%, BPTB 22%', 'pQCT / MCSA, shank 66%, thigh 20% and 50%', '31(19)',
     'Between-limb'],
    ['Harput 2022', 'Türkiye', 'Cross-sectional', '42', '42:0', '21.4(3.4)',
     'STG', 'US / VMO, RF and VL thickness', '32.0(28.8)¶', 'Between-limb'],
]
T1_TITLE = ('Table 1 Characteristics of the eight included studies, ordered by '
            'timepoint after surgery')
T1_NOTE = (
    'Values are mean(s.d.) unless otherwise indicated. All studies examined '
    'anterior cruciate ligament reconstruction. *Morgan 2026 reports 18 female '
    ': 14 male in the main text and 14 female : 18 male in Supplementary '
    'Material 6; the main-text ratio was used and the exchange is a '
    'pre-specified sensitivity analysis. †16 days. ‡median (range). §median '
    '(i.q.r.). ¶converted from 2.67(2.40) years. Iversen 2016 randomized 24 '
    'patients; the blood flow restriction arm was an intervention arm and was '
    'not eligible, so the control arm of 12 contributed, and the age shown is '
    'that arm’s (the trial also reports 24.9(7.4) years for the excluded '
    'occlusion arm). ACSA, anatomical cross-sectional area; BPTB, '
    'bone–patellar tendon–bone autograft; CSA, cross-sectional area; CT, '
    'computed tomography; DXA, dual-energy X-ray absorptiometry; HT, hamstring '
    'tendon autograft; MCSA, muscle cross-sectional area; MRI, magnetic '
    'resonance imaging; NR, not reported; pQCT, peripheral quantitative '
    'computed tomography; RF, rectus femoris; STG, semitendinosus–gracilis; '
    'US, ultrasound; VI, vastus intermedius; VL, vastus lateralis; VMO, vastus '
    'medialis obliquus.')

# ---------------------------------------------------------------- Table 2
T2_HEAD = ['Study', 'Sex', 'n', 'Comparator', 'Timepoint (months)',
           'Muscle analysed', 'Operated limb or LSI', 'Reference limb', 'Unit',
           'RoM (s.e. of ln RoM)']
MUSCLE = {
    'Iversen 2016': 'Quadriceps ACSA',
    'Kandil 2023': 'Quadriceps (RF + VI)',
    'Lindström 2013': 'Quadriceps',
    'Longo 2014': 'Quadriceps (RF + VI)',
    'Ito 2025': 'Vastus lateralis',
    'Morgan 2026': 'Thigh MCSA',
    'Harput 2022': 'Vastus lateralis',
    'Raymond-Pope 2021': 'Upper leg, anterior compartment',
}
TP = {'Iversen 2016': '0.5†', 'Kandil 2023': '6–8', 'Lindström 2013': '12',
      'Raymond-Pope 2021': '13.1', 'Longo 2014': '25.9', 'Ito 2025': '27.9',
      'Morgan 2026': '31', 'Harput 2022': '32.0'}
T2_TITLE = ('Table 2 Extracted values and the derived ratio of means for each '
            'of the 11 primary arms')
T2_NOTE = (
    'Values are mean(s.d.) unless otherwise indicated; *mean(s.e.m.). Arms are '
    'ordered by sex and then by timepoint after surgery, as in Fig. 3. Where '
    'the reference limb cell is —, the source reported a limb symmetry index '
    'directly rather than two limb means; that index is given in the operated '
    'limb or LSI column and was used as the ratio of means without further '
    'calculation. A standard error of the mean was converted to a standard '
    'deviation by multiplying by the square root of n before the variance was '
    'calculated. The standard error of ln(RoM) follows the delta method for '
    'paired data with an assumed within-person correlation of 0.85, varied '
    'from 0 to 0.95 in sensitivity analysis (Table S7). †16 days. ACSA, '
    'anatomical cross-sectional area; F, female; LSI, limb symmetry index; M, '
    'male; MCSA, muscle cross-sectional area; RF, rectus femoris; RoM, ratio '
    'of means; s.d., standard deviation; s.e., standard error; s.e.m., '
    'standard error of the mean; VI, vastus intermedius.')

# ---------------------------------------------------------------- Table 3
T3_HEAD = ['Study', 'Timepoint (months)', 'Functional test', 'Sex', 'n',
           'Muscle size (%)', 'Function (%)', 'Difference (percentage points)']
T3_ROWS = [
    ['Lindström 2013', '12', 'Single-leg hop', 'M', '23', '95.7', '95.0', '−0.7'],
    ['Lindström 2013', '12', 'Single-leg hop', 'F', '14', '91.6', '87.0', '−4.6'],
    ['Lindström 2013', '12', 'Triple hop', 'M', '23', '95.7', '96.0', '+0.3'],
    ['Lindström 2013', '12', 'Triple hop', 'F', '14', '91.6', '89.0', '−2.6'],
    ['Lindström 2013', '12', 'Square hop', 'M', '23', '95.7', '109.0', '+13.3'],
    ['Lindström 2013', '12', 'Square hop', 'F', '14', '91.6', '87.0', '−4.6'],
    ['Lindström 2013', '12', '6-m timed hop', 'M', '23', '95.7', '97.0', '+1.3'],
    ['Lindström 2013', '12', '6-m timed hop', 'F', '14', '91.6', '90.0', '−1.6'],
    ['Raymond-Pope 2021', '13.1', 'Isokinetic peak torque, 60°/s', 'F', '12',
     '92.5', '79.5', '−13.0'],
    ['Harput 2022', '32.0', 'Isokinetic peak torque, 60°/s', 'M', '42', '95.8',
     '94.5', '−1.3'],
    ['Median, 5 pairings per sex', '', '', 'M', '', '', '', '+0.3'],
    ['Median, 5 pairings per sex', '', '', 'F', '', '', '', '−4.6'],
]
T3_TITLE = ('Table 3 Muscle size and concurrent functional performance in the '
            'same patients')
T3_NOTE = (
    'Values are percentages unless otherwise indicated. Restricted to the three '
    'studies that measured muscle size and function in the same patients. '
    'Muscle size is the ratio of means expressed as a percentage. Function is '
    'the limb symmetry index as the source reported it, except for '
    'Raymond-Pope 2021, where the ratio of means was calculated from the '
    'reported torques; the two quantities are not identical and the difference '
    'column therefore compares measures that are related but not '
    'interchangeable. Difference is function minus muscle size. Four of the '
    'five pairings in each sex come from repeated hop protocols in one cohort '
    '(Lindström 2013), so the medians rest on two independent cohorts per sex. '
    'F, female; M, male.')


def disp(mean, d):
    """분산은 출처 값 그대로. 평균에 소수가 있으면 최소 1자리로 맞춘다."""
    if float(d) == int(d) and float(mean) != int(mean):
        return '%.1f' % d
    s = ('%g' % d)
    return s


def t2_rows():
    out = []
    for a in ARMS:
        if a['kind'] == 'Raw means':
            op = '%g(%s)%s' % (a['im'], disp(a['im'], a['idp']),
                               '*' if a['idt'] == 'SEM' else '')
            rf = '%g(%s)%s' % (a['rm'], disp(a['rm'], a['rdp']),
                               '*' if a['rdt'] == 'SEM' else '')
            unit = str(a['unit'])
        else:
            op = '%g(%s)%s' % (a['lsi'], disp(a['lsi'], a['ldp']),
                               '*' if a['ldt'] == 'SEM' else '')
            rf, unit = '—', '%'
        out.append([a['study'], a['sex'], str(a['n']), a['comp'],
                    TP[a['study']], MUSCLE[a['study']], op, rf, unit,
                    '%.3f (%.4f)' % (a['rom'], a['se'])])
    return out


def shade(cell, hexcolor):
    el = cell._tc.get_or_add_tcPr()
    sh = el.makeelement(qn('w:shd'), {})
    sh.set(qn('w:val'), 'clear'); sh.set(qn('w:color'), 'auto')
    sh.set(qn('w:fill'), hexcolor)
    el.append(sh)


def borders(tbl):
    tblPr = tbl._tbl.tblPr
    b = tblPr.makeelement(qn('w:tblBorders'), {})
    for edge in ('top', 'bottom', 'insideH'):
        e = b.makeelement(qn('w:%s' % edge), {})
        e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '4')
        e.set(qn('w:color'), 'BFBFBF')
        b.append(e)
    for edge in ('left', 'right', 'insideV'):
        e = b.makeelement(qn('w:%s' % edge), {})
        e.set(qn('w:val'), 'none')
        b.append(e)
    tblPr.append(b)


def add_table(doc, title, head, rows, note, numeric_from):
    p = doc.add_paragraph()
    r = p.add_run(title)
    r.bold = True; r.font.size = Pt(9.5)
    p.paragraph_format.space_after = Pt(6)

    t = doc.add_table(rows=len(rows) + 1, cols=len(head))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.autofit = True
    borders(t)
    for j, v in enumerate(head):
        c = t.cell(0, j); c.text = ''
        run = c.paragraphs[0].add_run(v)
        run.bold = True; run.font.size = Pt(HDR_PT)
        c.paragraphs[0].paragraph_format.space_after = Pt(2)
        shade(c, 'F2F1EC')
    for i, row in enumerate(rows, start=1):
        for j, v in enumerate(row):
            c = t.cell(i, j); c.text = ''
            run = c.paragraphs[0].add_run(str(v))
            run.font.size = Pt(BODY_PT)
            pf = c.paragraphs[0].paragraph_format
            pf.space_after = Pt(1.5); pf.space_before = Pt(1.5)
            if j >= numeric_from:
                c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    np_ = doc.add_paragraph()
    np_.paragraph_format.space_before = Pt(6)
    nr = np_.add_run(note)
    nr.font.size = Pt(NOTE_PT)
    return t


def verify():
    """표에 찍히는 숫자에서 RoM 이 그대로 재현되는지 확인."""
    bad = 0
    for a in ARMS:
        if a['kind'] == 'Raw means':
            got = a['im'] / a['rm']
        else:
            got = a['lsi'] / 100.0
        if abs(got - a['rom']) > 5e-4:
            print('  !! %s %s  표시값 %.6f vs 기재 %.6f'
                  % (a['study'], a['sex'], got, a['rom'])); bad += 1
    # 시점 정렬
    for sx in ('M', 'F'):
        d = [a['days'] for a in ARMS if a['sex'] == sx]
        assert d == sorted(d), '시점 정렬 어긋남 %s' % sx
    # 성비 합
    tot = sum(int(r[3]) for r in T1_ROWS)
    fem = sum(int(r[4].rstrip('*').split(':')[1]) for r in T1_ROWS)
    mal = sum(int(r[4].split(':')[0]) for r in T1_ROWS)
    assert tot == mal + fem == 248, (tot, mal, fem)
    assert fem == 49, fem
    # Table 3 차이값
    for r in T3_ROWS:
        if r[5] and r[6]:
            d = float(r[6]) - float(r[5])
            assert abs(d - float(r[7].replace('−', '-').replace('+', ''))) < 0.051, r
    print('  검산 통과: RoM %d개 재현, 시점 오름차순, 248명(남 %d·여 %d), 차이값 10건'
          % (len(ARMS) - bad, mal, fem))
    assert bad == 0


def main():
    doc = Document()
    s = doc.sections[0]
    s.orientation = WD_ORIENT.PORTRAIT
    s.page_width, s.page_height = Inches(8.27), Inches(11.69)
    for m in ('left_margin', 'right_margin'):
        setattr(s, m, Inches(0.5))
    s.top_margin = s.bottom_margin = Inches(0.7)
    st = doc.styles['Normal']
    st.font.name = 'Arial'; st.font.size = Pt(9)

    add_table(doc, T1_TITLE, T1_HEAD, T1_ROWS, T1_NOTE, 3)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    add_table(doc, T2_TITLE, T2_HEAD, t2_rows(), T2_NOTE, 2)
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    add_table(doc, T3_TITLE, T3_HEAD, T3_ROWS, T3_NOTE, 4)

    doc.save(OUT)
    for t in Document(OUT).tables:
        print('  표 %d x %d' % (len(t.rows), len(t.columns)))
        assert len(t.columns) <= 10
    verify()
    print('saved %s' % OUT)


if __name__ == '__main__':
    main()

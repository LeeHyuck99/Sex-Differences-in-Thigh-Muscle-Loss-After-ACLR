#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Paper 2 — 성별에 따른 ACL 재건술 후 근육량 손실 메타분석
PROSPERO CRD420261498739

이 파일 하나에 계산식과 분석이 모두 들어 있습니다. 그대로 실행하면 콘솔에
전체 결과가 찍히고, forest_paper2.py 가 이 파일을 import 해서 그림을 그립니다.

    python meta_paper2.py

필요 패키지:  numpy  scipy  openpyxl
    pip install numpy scipy openpyxl


================================================================================
계 산 식
================================================================================

1. 효과크기 — 평균비 (ratio of means, RoM)

       RoM = M_index / M_ref

   M_index = 환측(건측 대비 비교) 또는 술후(전후 비교) 평균
   M_ref   = 건측 또는 술전 평균

   로그 척도에서 통합합니다.   y = ln(RoM)
   RoM 은 척도 불변이므로 연구마다 단위가 달라도(mm², cm², mL/kg/m) 환산이
   필요 없습니다. 단, 한 행 안에서 index 와 ref 의 단위는 같아야 합니다.

   원시 평균이 없고 비(LSI 등)만 보고된 경우에만  RoM = LSI / 100.
   보고된 LSI 는 "개인별 비의 평균"이고 RoM 은 "평균의 비"라 둘은 다릅니다
   (Jensen 부등식). 그래서 원시 평균이 있으면 반드시 그쪽을 씁니다.


2. ln(RoM) 의 분산 — delta method (쌍체 자료)

   같은 사람의 두 다리(또는 전후)를 비교하므로 두 평균은 독립이 아닙니다.
   상관 r 을 반영한 델타법 근사:

       Var[ln(RoM)] ≈ SD_index²/(n · M_index²)
                    + SD_ref²  /(n · M_ref²)
                    − 2r · SD_index · SD_ref /(n · M_index · M_ref)

   r = 0.85 을 기본값으로 하고 민감도 분석에서 0.75–0.95 로 바꿉니다.
   r 이 클수록 분산이 작아집니다 (쌍체 설계의 이득).

   비(ratio)만 보고된 행은 비 자체의 표준오차를 씁니다:

       SE[ln(RoM)] = SE_ratio / ratio

   SD 가 아니라 SEM 이 보고된 경우  SD = SEM × √n.


3. 주 분석 — 연구 임의절편 메타회귀 (random-intercept meta-regression)

       y_i = β₀ + β₁ · female_i + β₂ · within_i + u_{study(i)} + e_i
       u ~ N(0, τ²)          연구 간 이질성
       e_i ~ N(0, v_i)       행별 표집오차 (위 2번에서 계산한 분산)

   1차 선택 11행 전부가 들어갑니다. within_i 는 비교자 더미이며(기준 수준은
   between-limb) 7번에서 설명하는 nuisance parameter 입니다.

   한 연구가 남녀 두 행을 내면 두 행이 같은 u 를 공유합니다. 따라서 공분산은
   대각이 아니라 블록대각입니다:

       V = diag(v) + τ² · Z Zᵀ          Z = 연구 설계행렬

   τ² 는 제한최대우도(REML)로 추정합니다. REML 음의 로그우도:

       ℓ(τ²) = ½ [ ln|V| + ln|XᵀV⁻¹X| + (y−Xβ̂)ᵀ V⁻¹ (y−Xβ̂) ]

   β̂ = (XᵀV⁻¹X)⁻¹ XᵀV⁻¹y  (일반화최소제곱),  Var(β̂) = (XᵀV⁻¹X)⁻¹

   β₁ 은 ln 척도의 여성−남성 차이이므로  exp(β₁) = 여성/남성 RoM 비.


4. Hartung–Knapp–Sidik–Jonkman 보정

   연구 수가 적을 때 통상적 분산은 1종 오류를 부풀립니다. HKSJ 는 잔차로
   분산을 다시 조정하고 t 분포를 씁니다:

       q = (y−Xβ̂)ᵀ V⁻¹ (y−Xβ̂) / (k − p)
       Var_HK(β̂) = q · (XᵀV⁻¹X)⁻¹          (q < 1 이면 1 로 둠, 보수적)
       신뢰구간은 t(k − p) 사용

   q 를 1 미만으로 내리지 않는 것이 Knapp–Hartung 의 보수적 변형입니다.


5. 연구 내 성별 대비 (교란 없는 추정)

   남녀를 모두 보고한 연구에서만:

       d_s = ln(RoM_여) − ln(RoM_남)
       Var(d_s) = v_남 + v_여

   역분산 가중 통합 + HKSJ. 3번의 모형과 달리 연구 간 비교를 쓰지 않으므로
   연구 간 교란이 없습니다. 대신 k 가 작아 정밀도가 낮습니다.
   두 추정치가 일치하면 모형이 끌어온 연구 간 정보가 왜곡을 주지 않는다는
   근거가 됩니다.


6. 방향 일관성 — 정확 이항검정 (부호검정)

   연구 내 대비 k 개 중 사전 가정 방향(여성 손실이 큼)과 일치하는 개수에
   대한 단측 정확검정. 분산 가정이 전혀 들어가지 않아, 통합 추정이 부정확한
   상황에서도 방향에 대한 증거를 줍니다.


7. 비교자 — 모형에 넣되 해석하지 않습니다 (nuisance parameter)

   두 비교자는 서로 다른 양을 잽니다:
   · between-limb  : 환측 / 건측        (한 시점)
   · within-subject: 술후 / 술전        (같은 다리)

   건측도 함께 위축하므로(Kandil 에서 3.6–3.8%) between-limb 비는 절대 손실을
   과소평가합니다. 두 양의 수준은 체계적으로 다릅니다.

   그러나 우리가 보고하는 1차 결과는 손실의 절대 크기가 아니라 '여성/남성 비'
   입니다. 수준 차이가 남녀에 공통으로 걸리면 비를 낼 때 약분됩니다. 그래서
   비교자 더미를 하나 세워 수준 차이를 흡수시키고, 11행을 모두 씁니다.

   더미 계수 β₂ 자체는 해석하지 않습니다. 우리 8편에서 비교자와 술후 시점이
   거의 완전히 겹치기 때문입니다 (within = 16일·213일 / between = 365–975일,
   더미와 log(일)의 상관 r = −0.87). β₂ 는 '비교자 효과'가 아니라 비교자와
   시점이 뭉친 양이며, 둘을 분리하려고 log(일)을 함께 넣으면 공선성으로 양쪽
   다 무의미해집니다 (within p = 0.65, log(일) p = 0.57). 따라서 β₂ 는 모형에서
   수준 차이를 빨아들이는 역할만 하고, 본문에서는 보고만 하고 해석하지 않습니다.

   민감도 분석으로 between-limb 8행만 쓰는 층화 모형을 함께 보고합니다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import openpyxl
from scipy import stats

# ------------------------------------------------------------------ 설정
XLSX = 'Data_extraction_Paper2.xlsx'
R_PAIRED = 0.85          # 쌍체 상관 기본값
R_SENS = (0.0, 0.60, 0.75, 0.95)    # 민감도 범위 (0 = 대응 구조 무시)

# Outcome_muscle 열 번호 (1부터)
# 열 번호는 추출 파일의 머리글에서 직접 찾습니다.
# (추출 파일의 판이 바뀌면서 열 위치가 달라지므로 고정 번호를 쓰지 않습니다.)
_HEADERS = dict(
    rid='RowID', arm='ArmID', study='Author Year', sex='Sex', n='n',
    modality='Modality', quantity='Quantity', muscle='Muscle',
    harvested='Harvested muscle?', primary='Primary selection',
    days='Days', comparator='Comparator',
    idx_mean='Index mean', idx_disp='Index disp', idx_type='Index disp type',
    ref_mean='Ref mean', ref_disp='Ref disp', ref_type='Ref disp type',
    unit='Unit', lsi='LSI (%)', lsi_disp='LSI disp', lsi_type='LSI disp type',
    verified='Source (table/fig/page)')


def _colmap(path=None):
    ws = openpyxl.load_workbook(path or XLSX, data_only=True)['Outcome_muscle']
    hdr = {str(c.value).strip(): c.column
           for c in ws[1] if c.value is not None}
    out, miss = {}, []
    for key, name in _HEADERS.items():
        if name in hdr:
            out[key] = hdr[name]
        else:
            miss.append('%s (%r)' % (key, name))
    if miss:
        raise KeyError('Outcome_muscle 시트에서 못 찾은 열: ' + ', '.join(miss))
    return out


C = {}


@dataclass
class Row:
    rid: str
    study: str
    sex: str
    n: int
    muscle: str
    days: float
    comparator: str      # 'between' | 'within'
    primary: bool
    rom: float
    y: float             # ln(RoM)
    v: float             # Var[ln(RoM)]

    @property
    def se(self) -> float:
        return math.sqrt(self.v)

    def ci(self, level=0.95):
        z = stats.norm.ppf(0.5 + level / 2)
        return math.exp(self.y - z * self.se), math.exp(self.y + z * self.se)


# ------------------------------------------------------------------ 1-2. 효과크기
def _sd(disp, disp_type, n):
    """SEM 으로 보고된 경우 SD = SEM × √n."""
    if disp is None or disp == '':
        return None
    return disp * math.sqrt(n) if disp_type == 'SEM' else float(disp)


def rom_and_var(n, idx_mean, idx_disp, idx_type,
                ref_mean, ref_disp, ref_type,
                lsi, lsi_disp, lsi_type, r=R_PAIRED):
    """RoM 과 Var[ln(RoM)]. 원시 평균이 있으면 그것을 쓰고, 없으면 비를 씁니다."""
    if idx_mean and ref_mean:
        rom = idx_mean / ref_mean
        s1 = _sd(idx_disp, idx_type, n)
        s2 = _sd(ref_disp, ref_type, n)
        var = (s1 ** 2) / (n * idx_mean ** 2) \
            + (s2 ** 2) / (n * ref_mean ** 2) \
            - 2 * r * s1 * s2 / (n * idx_mean * ref_mean)
    elif lsi:
        rom = lsi / 100.0
        se_ratio = lsi_disp if lsi_type == 'SEM' else lsi_disp / math.sqrt(n)
        var = (se_ratio / lsi) ** 2      # SE[ln x] = SE[x] / x
    else:
        return None, None
    return rom, max(var, 1e-12)


def load(path=XLSX, r=R_PAIRED, primary_only=True) -> list[Row]:
    """추출 시트에서 행을 읽어 효과크기를 계산합니다."""
    global C
    C = _colmap(path)
    om = openpyxl.load_workbook(path, data_only=True)['Outcome_muscle']
    out = []
    for i in range(2, om.max_row + 1):
        g = lambda k: om.cell(row=i, column=C[k]).value
        if g('rid') is None:
            break
        if primary_only and g('primary') != 'Y':
            continue
        rom, var = rom_and_var(
            g('n'), g('idx_mean'), g('idx_disp'), g('idx_type'),
            g('ref_mean'), g('ref_disp'), g('ref_type'),
            g('lsi'), g('lsi_disp'), g('lsi_type'), r=r)
        if rom is None:
            continue
        out.append(Row(
            rid=g('rid'), study=g('study'), sex=g('sex'), n=g('n'),
            muscle=g('muscle'), days=g('days') or 0,
            comparator='within' if 'Within' in str(g('comparator')) else 'between',
            primary=(g('primary') == 'Y'),
            rom=rom, y=math.log(rom), v=var))
    out.sort(key=lambda x: (x.days, x.sex))
    return out


# ------------------------------------------------------------------ 3-4. REML 모형
@dataclass
class Fit:
    beta: np.ndarray
    cov: np.ndarray          # HKSJ 보정 후
    tau2: float
    df: int
    q: float
    k: int                   # 행 수
    n_study: int
    has_comp: bool = False   # within 더미가 실제로 세워졌는지

    def estimate(self, j=0, level=0.95):
        """계수 j 의 추정치, 신뢰구간, p값. 지수화한 비도 함께 돌려줍니다."""
        b = float(self.beta[j])
        se = math.sqrt(self.cov[j, j])
        t = stats.t.ppf(0.5 + level / 2, self.df)
        lo, hi = b - t * se, b + t * se
        p = 2 * stats.t.sf(abs(b / se), self.df)
        return dict(b=b, se=se, lo=lo, hi=hi, p=p,
                    ratio=math.exp(b), ratio_lo=math.exp(lo), ratio_hi=math.exp(hi))


def _design(rows: list[Row], with_sex: bool, with_comparator: bool):
    """설계행렬 [절편, (여성), (within)] 과 within 열을 실제로 세웠는지 여부."""
    X = np.ones((len(rows), 1))
    if with_sex:
        X = np.column_stack([X, [1.0 if r.sex == 'F' else 0.0 for r in rows]])
    has_comp = with_comparator and len({r.comparator for r in rows}) == 2
    if has_comp:
        X = np.column_stack([X, [1.0 if r.comparator == 'within' else 0.0
                                 for r in rows]])
    return X, has_comp


def fit_random_intercept(rows: list[Row], with_sex: bool,
                         with_comparator=True, hksj=True) -> Fit:
    """V = diag(v) + τ²·ZZᵀ 의 REML 적합 + HKSJ 보정.

    with_comparator=True 면 within-subject 더미를 넣습니다. 기준 수준은
    between-limb 이므로 절편은 '건측 대비 기준점에서의 추정치'가 됩니다.
    이 항은 nuisance parameter 입니다 — 해석하지 않습니다(docstring 7번 참조).
    두 수준이 모두 있을 때만 열을 세웁니다. 한쪽만 있으면 절편과 완전공선이라
    자동으로 빠집니다(leave-one-out 과 성별별 적합에서 실제로 일어납니다).
    """
    y = np.array([r.y for r in rows])
    v = np.array([r.v for r in rows])
    studies = sorted({r.study for r in rows})
    Z = np.zeros((len(rows), len(studies)))
    for i, r in enumerate(rows):
        Z[i, studies.index(r.study)] = 1.0
    ZZt = Z @ Z.T

    X, has_comp = _design(rows, with_sex, with_comparator)

    def neg_reml(log_tau2):
        V = np.diag(v) + math.exp(log_tau2) * ZZt
        Vi = np.linalg.inv(V)
        XtViX = X.T @ Vi @ X
        b = np.linalg.solve(XtViX, X.T @ Vi @ y)
        res = y - X @ b
        sign1, ld1 = np.linalg.slogdet(V)
        sign2, ld2 = np.linalg.slogdet(XtViX)
        return 0.5 * (ld1 + ld2 + float(res @ Vi @ res))

    # τ² 는 경계(0)에 붙는 일이 흔해 격자 탐색이 뉴턴법보다 안정적입니다.
    grid = np.linspace(-20.0, 2.0, 441)
    vals = [neg_reml(g) for g in grid]
    tau2 = math.exp(float(grid[int(np.argmin(vals))]))
    if tau2 < 1e-8:
        tau2 = 0.0

    V = np.diag(v) + tau2 * ZZt
    Vi = np.linalg.inv(V)
    XtViX = X.T @ Vi @ X
    cov = np.linalg.inv(XtViX)
    beta = cov @ (X.T @ Vi @ y)
    res = y - X @ beta
    k, p = len(rows), X.shape[1]
    q = float(res @ Vi @ res) / (k - p)
    if hksj:
        cov = cov * max(q, 1.0)          # q<1 은 1 로 — 보수적 변형
    return Fit(beta=beta, cov=cov, tau2=tau2, df=k - p, q=q,
               k=k, n_study=len(studies), has_comp=has_comp)


def pool(rows: list[Row]) -> dict:
    """한 성별의 통합 추정치. 비교자 항이 있으면 절편 = between-limb 기준점."""
    f = fit_random_intercept(rows, with_sex=False)
    out = f.estimate(0)
    out.update(tau2=f.tau2, tau=math.sqrt(f.tau2), k=f.k,
               n_study=f.n_study, df=f.df, q=f.q, has_comp=f.has_comp)
    out.update(heterogeneity(rows, f))
    return out


def heterogeneity(rows: list[Row], fit: 'Fit', with_sex=False) -> dict:
    """잔차 이질성 Q_E, I², H², 그리고 95% 예측구간.

    주의 — Q 는 절편만 가정한 Cochran Q 가 아니라 **모형과 같은 설계행렬**에
    대한 잔차 이질성 통계량(metafor 의 QE)입니다. 비교자 항이 모형에 있는데
    Q 를 절편만으로 계산하면, 비교자가 만든 수준 차이가 전부 이질성으로
    둔갑합니다. df = k − p 도 여기에 맞춥니다.

    예측구간은 모형이 실제로 쓴 REML τ² 와 HKSJ 와 같은 자유도를 씁니다.
    k ≤ 3 에서는 τ² 추정 불확실성 때문에 사실상 정보가 없으므로
    informative=False 로 표시하고 본문에서는 보고하지 않습니다.
    """
    y = np.array([x.y for x in rows])
    v = np.array([x.v for x in rows])
    X, _ = _design(rows, with_sex, fit.has_comp)
    W = np.diag(1.0 / v)
    # 고정효과 가중 최소제곱 잔차에 대한 Q_E
    b_fe = np.linalg.solve(X.T @ W @ X, X.T @ W @ y)
    res_fe = y - X @ b_fe
    Q = float(res_fe @ W @ res_fe)
    k, p = len(rows), X.shape[1]
    df_q = k - p
    I2 = max(0.0, (Q - df_q) / Q) * 100 if Q > 0 and df_q > 0 else 0.0
    H2 = Q / df_q if df_q else float('nan')
    p_q = float(stats.chi2.sf(Q, df_q)) if df_q else float('nan')

    b = float(fit.beta[0])
    se = math.sqrt(float(fit.cov[0, 0]))
    t = stats.t.ppf(0.975, max(fit.df, 1))
    se_pred = math.sqrt(se ** 2 + fit.tau2)
    return dict(Q=Q, Q_df=df_q, Q_p=p_q, I2=I2, H2=H2,
                pi_lo=math.exp(b - t * se_pred),
                pi_hi=math.exp(b + t * se_pred),
                # τ² = 0 이면 예측구간이 신뢰구간과 같아져 오독을 부릅니다.
                pi_informative=(k > 3 and fit.tau2 > 0))


# ------------------------------------------------------------------ 5-6. 연구 내 대비
def within_study_contrasts(rows: list[Row]) -> list[dict]:
    """남녀를 모두 보고한 연구의 쌍체 차이."""
    out = []
    for st in sorted({r.study for r in rows}, key=lambda s: min(x.days for x in rows if x.study == s)):
        m = [r for r in rows if r.study == st and r.sex == 'M']
        f = [r for r in rows if r.study == st and r.sex == 'F']
        if not (m and f):
            continue
        m, f = m[0], f[0]
        out.append(dict(study=st, comparator=m.comparator, days=m.days,
                        rom_m=m.rom, rom_f=f.rom,
                        pp=100 * (f.rom - m.rom),
                        d=f.y - m.y, var=m.v + f.v))
    return out


def pool_contrasts(contrasts: list[dict], level=0.95) -> dict:
    """역분산 가중 통합 + HKSJ."""
    w = np.array([1 / c['var'] for c in contrasts])
    e = np.array([c['d'] for c in contrasts])
    k = len(contrasts)
    b = float(w @ e / w.sum())
    se = math.sqrt(1 / w.sum())
    if k > 1:
        q = float((w * (e - b) ** 2).sum()) / (k - 1)
        se *= math.sqrt(max(q, 1.0))
    t = stats.t.ppf(0.5 + level / 2, max(k - 1, 1))
    lo, hi = b - t * se, b + t * se
    return dict(b=b, se=se, lo=lo, hi=hi, k=k,
                ratio=math.exp(b), ratio_lo=math.exp(lo), ratio_hi=math.exp(hi))


def sign_test(contrasts: list[dict]) -> dict:
    """사전 가정 방향(여성 손실이 큼 = d < 0)과 일치하는 비율의 단측 정확검정."""
    k = len(contrasts)
    hit = sum(1 for c in contrasts if c['d'] < 0)
    p = stats.binomtest(hit, k, 0.5, alternative='greater').pvalue
    return dict(hit=hit, k=k, p=p)


# ------------------------------------------------------------------ 7. 시간 메타회귀
def time_metareg(rows: list[Row], level=0.95) -> dict:
    """건측 대비 층에서 ln(RoM) ~ log(수술 후 일수) + 성별.

    비교자 층을 나누는 이유 — 비교자와 시점이 거의 공선(r = -0.86)이라
    두 항을 한 모형에 넣으면 둘 다 식별되지 않습니다. 건측 층 안에서는
    비교자가 상수이므로 시간 항이 식별됩니다.

    성별을 함께 넣는 이유 — 보정 없이 넣으면 시간 계수가 성별 구성의
    차이를 일부 흡수합니다. 성별이 1차 결과이므로 반드시 함께 적합합니다.

    주의 — 이 층의 시점은 1.0~2.7년에 몰려 있습니다. 시간 계수는 '시간
    효과가 없다'가 아니라 '이 자료로는 추정되지 않는다'로 읽어야 합니다.
    """
    y = np.array([x.y for x in rows])
    v = np.array([x.v for x in rows])
    X = np.column_stack([np.ones(len(rows)),
                         [math.log(x.days) for x in rows],
                         [1.0 if x.sex == 'F' else 0.0 for x in rows]])
    studies = sorted({x.study for x in rows})
    Z = np.zeros((len(rows), len(studies)))
    for i, x in enumerate(rows):
        Z[i, studies.index(x.study)] = 1.0
    ZZt = Z @ Z.T

    def neg_reml(log_tau2):
        V = np.diag(v) + math.exp(log_tau2) * ZZt
        Vi = np.linalg.inv(V)
        A = X.T @ Vi @ X
        b = np.linalg.solve(A, X.T @ Vi @ y)
        res = y - X @ b
        _, ld1 = np.linalg.slogdet(V)
        _, ld2 = np.linalg.slogdet(A)
        return 0.5 * (ld1 + ld2 + float(res @ Vi @ res))

    grid = np.linspace(-20.0, 2.0, 441)
    tau2 = math.exp(float(grid[int(np.argmin([neg_reml(g) for g in grid]))]))
    if tau2 < 1e-8:
        tau2 = 0.0

    V = np.diag(v) + tau2 * ZZt
    Vi = np.linalg.inv(V)
    cov = np.linalg.inv(X.T @ Vi @ X)
    beta = cov @ (X.T @ Vi @ y)
    res = y - X @ beta
    k, p = len(rows), X.shape[1]
    q = float(res @ Vi @ res) / (k - p)
    cov = cov * max(q, 1.0)                 # HKSJ, 주 모형과 같은 보수적 절단
    df = k - p
    t = stats.t.ppf(0.5 + level / 2, df)

    out = dict(k=k, n_study=len(studies), df=df, tau2=tau2, q=q)
    for j, nm in ((1, 'time'), (2, 'female')):
        b = float(beta[j])
        se = math.sqrt(float(cov[j, j]))
        out[nm] = dict(b=b, se=se, ratio=math.exp(b),
                       ratio_lo=math.exp(b - t * se),
                       ratio_hi=math.exp(b + t * se),
                       p=2 * float(stats.t.sf(abs(b / se), df)))
    return out


# ------------------------------------------------------------------ 결과 출력
def _fmt(d, label, width=44):
    return ('%-*s  RoM %.3f (%.3f to %.3f)  p = %.3f'
            % (width, label, d['ratio'], d['ratio_lo'], d['ratio_hi'], d['p']))


def run(path=XLSX, r=R_PAIRED, verbose=True):
    rows = load(path, r=r)
    bet = [x for x in rows if x.comparator == 'between']
    wit = [x for x in rows if x.comparator == 'within']
    res = {}

    if verbose:
        print('=' * 78)
        print('ACL 재건술 후 근육량 손실의 성별 차이 — 1차 선택 %d행 / %d연구  (r = %.2f)'
              % (len(rows), len({x.study for x in rows}), r))
        print('=' * 78)
        print('\n[행]')
        for x in rows:
            print('  %-5s %-18s %-2s n=%-3d %-8s %5.0f d  RoM %.4f  SE %.4f  %s'
                  % (x.rid, x.study, x.sex, x.n, x.comparator, x.days,
                     x.rom, x.se, x.muscle[:26]))

    # --- 주 분석: 1차 선택 11행 전부 + 비교자 nuisance 항 ---
    # 성별별 추정치는 각 성별 행을 따로 적합하되 비교자 항을 함께 넣습니다.
    # 기준 수준이 between-limb 이므로 절편 = '건측 대비 기준점에서의 추정치'.
    res['men'] = pool([x for x in rows if x.sex == 'M'])
    res['women'] = pool([x for x in rows if x.sex == 'F'])
    fit = fit_random_intercept(rows, with_sex=True)
    res['sex_coef'] = fit.estimate(1)
    res['intercept'] = fit.estimate(0)
    res['comparator'] = fit.estimate(2) if fit.has_comp else None
    res['fit'] = fit

    if verbose:
        print('\n[주 분석 — 1차 선택 11행 전부, 비교자 보정]')
        print(' ', _fmt(res['men'], '남성  (%d행 / %d연구)' % (res['men']['k'], res['men']['n_study'])))
        print(' ', _fmt(res['women'], '여성  (%d행 / %d연구)' % (res['women']['k'], res['women']['n_study'])))
        print(' ', _fmt(res['sex_coef'], '여성 / 남성 비  ← 1차 결과'))
        print('    τ² = %.6f   τ = %.4f   df = %d   HKSJ q = %.3f'
              % (fit.tau2, math.sqrt(fit.tau2), fit.df, fit.q))
        print('    성별 추정치는 between-limb 기준점에서의 값입니다.')
        c = res['comparator']
        print('    [nuisance] within 더미 %.3f (%.3f to %.3f)  p = %.3f'
              '  — 해석하지 않음 (비교자와 시점이 공선, r = %.2f)'
              % (c['ratio'], c['ratio_lo'], c['ratio_hi'], c['p'],
                 np.corrcoef([1.0 if x.comparator == 'within' else 0.0 for x in rows],
                             [math.log(x.days) for x in rows])[0, 1]))

        print('\n[이질성]')
        for key, lab in (('men', '남성 (k=%d)' % res['men']['k']),
                         ('women', '여성 (k=%d)' % res['women']['k'])):
            d = res[key]
            print('  %-12s Q = %5.2f (df = %d, p = %.3f)   I² = %4.1f%%   H² = %.2f   τ = %.4f'
                  % (lab, d['Q'], d['Q_df'], d['Q_p'], d['I2'], d['H2'], d['tau']))
            print('  %-12s 95%% 예측구간 %.3f to %.3f%s'
                  % ('', d['pi_lo'], d['pi_hi'],
                     '' if d['pi_informative']
                     else '   ← τ² = 0 또는 k ≤ 3, 보고하지 않음'))
        # τ² 가 성별을 넣은 뒤 오히려 커지므로 R² 는 0 으로 보고합니다(관례).
        # 성별 계수가 유의한 것은 연구 간 분산을 줄여서가 아니라, 임의절편이
        # 연구 간 차이를 흡수한 뒤 남는 연구 '내' 대비가 계수를 끌기 때문입니다.
        t0 = fit_random_intercept(rows, with_sex=False).tau2
        print('  %-12s τ² 성별 미보정 %.6f → 보정 후 %.6f   R² = 0%% (음수, 관례대로 0)'
              % ('메타회귀', t0, fit.tau2))
        print('  %-12s 성별은 연구 간 이질성을 설명하지 않습니다. 계수는 연구 내 대비에서 나옵니다.'
              % '')

    # --- 비교자별 기술통계: 모형에는 함께 들어가지만 수준이 다르므로 따로 보여줍니다 ---
    res['within'] = wit
    res['between'] = bet
    if verbose:
        print('\n[비교자별 행 — 모형에는 함께 들어갑니다. 수준 차이 확인용]')
        for lab, grp in (('건측 대비 (기준 수준)', bet), ('수술 전후', wit)):
            print('  %s' % lab)
            for x in grp:
                lo, hi = x.ci()
                print('    %-18s %-2s  RoM %.3f (%.3f to %.3f)   %.0f일'
                      % (x.study, x.sex, x.rom, lo, hi, x.days))

    # --- 연구 내 대비 ---
    con = within_study_contrasts(rows)
    res['contrasts'] = con
    res['contrast_pooled'] = pool_contrasts(con)
    res['sign'] = sign_test(con)
    if verbose:
        print('\n[연구 내 성별 대비 — 연구 간 교란 없음]')
        for c in con:
            print('  %-18s %-14s 남 %.3f  여 %.3f   차이 %+.1f pp'
                  % (c['study'], c['comparator'], c['rom_m'], c['rom_f'], c['pp']))
        cp = res['contrast_pooled']
        print('  통합 (k=%d):  비 %.3f (%.3f to %.3f)'
              % (cp['k'], cp['ratio'], cp['ratio_lo'], cp['ratio_hi']))
        sg = res['sign']
        print('  부호검정: %d/%d 남성 유리, 단측 정확 p = %.3f' % (sg['hit'], sg['k'], sg['p']))

    # --- 시간 메타회귀 (건측 층, 성별 보정) ---
    res['time_metareg'] = tm = time_metareg(bet)
    if verbose:
        print('\n[시간 메타회귀 — 건측 대비 %d행 / %d연구, 성별 보정]'
              % (tm['k'], tm['n_study']))
        for nm, lab in (('time', 'log 시점 1단위당'), ('female', '여성 / 남성')):
            d = tm[nm]
            print('  %-14s %.3f (%.3f to %.3f)  p = %.3f'
                  % (lab, d['ratio'], d['ratio_lo'], d['ratio_hi'], d['p']))
        print('    df = %d   τ² = %.6f' % (tm['df'], tm['tau2']))
        print('    이 층의 시점은 %.1f~%.1f년에 몰려 있습니다 — 시간 계수는'
              ' 추정 불가로 읽습니다.'
              % (min(x.days for x in bet) / 365.25,
                 max(x.days for x in bet) / 365.25))

    return res


def sensitivity(path=XLSX, verbose=True):
    """민감도 분석 — 전부 주 분석(11행, 비교자 보정)의 성별 계수."""
    out = []

    def coef(rows, label, with_comparator=True):
        if len({x.study for x in rows}) < 3 or len({x.sex for x in rows}) < 2:
            out.append((label, None))
            return
        d = fit_random_intercept(rows, with_sex=True,
                                 with_comparator=with_comparator).estimate(1)
        out.append((label, d))

    base = load(path)
    coef(base, '주 분석 (11행, r = 0.85)')

    # 가장 중요한 민감도 — 비교자 층화. 등록 프로토콜에는 없던 구분이지만
    # 추정 대상이 다르다는 지적에 대한 답으로 반드시 함께 보고합니다.
    coef([x for x in base if x.comparator == 'between'],
         '건측 대비 8행만 (비교자 층화)')
    coef(base, '비교자 항 제외 (순진한 통합)', with_comparator=False)

    for r in R_SENS:
        coef(load(path, r=r), '쌍체 상관 r = %.2f' % r)

    THICK = {'Longo 2014', 'Harput 2023', 'Kandil 2023'}   # 초음파 두께
    coef([x for x in base if x.study not in THICK], '초음파 두께 측정 제외')
    coef([x for x in base if x.study != 'Longo 2014'], 'Longo 2014 제외 (이상치)')

    import copy
    sw = copy.deepcopy(base)                   # Morgan 성비 교환
    for x in sw:
        if x.study == 'Morgan 2026':
            old, x.n = x.n, (18 if x.sex == 'M' else 14)
            x.v *= old / x.n
    coef(sw, 'Morgan 2026 성비 교환 (18M:14F)')

    for st in sorted({x.study for x in base}):
        coef([x for x in base if x.study != st], '  leave-one-out: %s 제외' % st)

    if verbose:
        print('\n[민감도 분석 — 성별 계수]')
        for label, d in out:
            if d is None:
                print('  %-34s  추정 불가' % label)
            else:
                print('  %-34s  비 %.3f (%.3f to %.3f)  p = %.3f'
                      % (label, d['ratio'], d['ratio_lo'], d['ratio_hi'], d['p']))
    return out


if __name__ == '__main__':
    run()
    sensitivity()

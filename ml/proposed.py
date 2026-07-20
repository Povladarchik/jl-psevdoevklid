"""Четыре предложенных варианта + контролируемый датасет с сигналом в q-части.

Варианты (все переиспользуют одно собственное разложение G):
  C  CLIP-ALL-P     : q'=0, весь бюджет на p-часть (= классический JL с масс-упоряд.)
  A  MASS-WATERFILL : water-filling бюджета по |lambda|, flip-топология
  B  TOPLAM-HYBRID  : top-k точных |lambda|-осей + скетч хвоста, flip
  D  HSIC-SCREEN    : супервизорный отбор осей по alignment с метками, flip

Базлайны берём из methods2 (JL, plain JL-pq, cMDS, Landmark, SMACOF, NMDS).
"""
import numpy as np
from sklearn.random_projection import GaussianRandomProjection
import methods2 as M2

gram = M2.gram
_sqdist = M2._sqdist


def _eig(Dsq):
    w, V = np.linalg.eigh(gram(Dsq))
    order = np.argsort(w)[::-1]
    return w[order], V[:, order]        # по убыванию собственного значения


def _project(Coords, k, rng):
    """Гауссова проекция набора координат в k измерений (k<=ncol)."""
    k = int(max(0, min(k, Coords.shape[1])))
    if k == 0 or Coords.shape[1] == 0:
        return np.zeros((Coords.shape[0], 0))
    if k == Coords.shape[1]:
        R = rng.standard_normal((k, k)) / np.sqrt(k)
        return Coords @ R
    return GaussianRandomProjection(n_components=k,
        random_state=int(rng.integers(1 << 30))).fit_transform(Coords)


# ------------------------------------------------------------- C: CLIP-ALL-P
def clip_all_p(Dsq, m, rng, y=None):
    w, V = _eig(Dsq)
    pos = w > 1e-10
    Yp = V[:, pos] * np.sqrt(w[pos])          # уже отсортировано по убыв. lambda
    Z = _project(Yp[:, :m] if Yp.shape[1] > m else Yp, m, rng)
    return Z, {'p0': Z.shape[1], 'flip': True, 'name': 'C:CLIP-ALL-P'}


# ------------------------------------------------------------- A: MASS-WATERFILL
def mass_waterfill(Dsq, m, rng, y=None):
    w, V = _eig(Dsq)
    absmag = np.abs(w)
    keep = np.argsort(absmag)[::-1][:m]        # m направлений с наибольшим |lambda|
    sel = np.zeros(len(w), bool); sel[keep] = True
    pos = sel & (w > 0); neg = sel & (w < 0)
    Yp = V[:, pos] * np.sqrt(np.abs(w[pos]))
    Yq = V[:, neg] * np.sqrt(np.abs(w[neg]))
    p0, q0 = int(pos.sum()), int(neg.sum())
    Zp = _project(Yp, p0, rng)
    Zq = _project(Yq, q0, rng) if q0 > 0 else np.zeros((len(w), 0))
    Z = np.hstack([Zp, Zq])                    # flip-топология
    return Z, {'p0': Zp.shape[1], 'flip': True, 'sig': (p0, q0), 'name': 'A:MASS-WATERFILL'}


# ------------------------------------------------------------- B: TOPLAM-HYBRID
def toplam_hybrid(Dsq, m, rng, y=None, k_exact=8):
    w, V = _eig(Dsq)
    absmag = np.abs(w)
    order = np.argsort(absmag)[::-1]
    k_exact = min(k_exact, m)
    ex = order[:k_exact]                       # точные ведущие оси
    E = V[:, ex] * np.sqrt(np.abs(w[ex]))      # берём как есть
    # хвост: остаток бюджета water-filling по массе
    rest = order[k_exact:]
    m_tail = m - k_exact
    tail = rest[:m_tail]
    pos = tail[w[tail] > 0]; neg = tail[w[tail] < 0]
    Yp = V[:, pos] * np.sqrt(np.abs(w[pos]))
    Yq = V[:, neg] * np.sqrt(np.abs(w[neg]))
    Zp = _project(Yp, len(pos), rng)
    Zq = _project(Yq, len(neg), rng) if len(neg) > 0 else np.zeros((len(w), 0))
    Z = np.hstack([E, Zp, Zq])
    return Z, {'p0': Z.shape[1], 'flip': True, 'name': 'B:TOPLAM-HYBRID'}


# ------------------------------------------------------------- D: HSIC-SCREEN
def hsic_screen(Dsq, m, rng, y=None):
    """Отбор осей по |corr(eigvec, one-hot(y))|; бюджет m самым выровненным.
    Если меток нет — деградирует до mass_waterfill."""
    if y is None:
        return mass_waterfill(Dsq, m, rng)
    w, V = _eig(Dsq)
    y = np.asarray(y)
    Yoh = np.zeros((len(y), len(np.unique(y))))
    Yoh[np.arange(len(y)), np.unique(y, return_inverse=True)[1]] = 1
    Yoh -= Yoh.mean(0)
    Yoh /= (np.linalg.norm(Yoh, axis=0, keepdims=True) + 1e-12)
    Vc = V - V.mean(0)
    Vc /= (np.linalg.norm(Vc, axis=0, keepdims=True) + 1e-12)
    align = (np.abs(Vc.T @ Yoh)).max(1)        # max по классам: выравнивание оси
    # взвешиваем на sqrt|lambda|, чтобы ось с сигналом, но нулевой массой не всплывала
    score = align * np.sqrt(np.abs(w))
    keep = np.argsort(score)[::-1][:m]
    sel = np.zeros(len(w), bool); sel[keep] = True
    pos = sel & (w > 0); neg = sel & (w < 0)
    Yp = V[:, pos] * np.sqrt(np.abs(w[pos]))
    Yq = V[:, neg] * np.sqrt(np.abs(w[neg]))
    Zp = _project(Yp, int(pos.sum()), rng)
    Zq = _project(Yq, int(neg.sum()), rng) if neg.sum() > 0 else np.zeros((len(w), 0))
    Z = np.hstack([Zp, Zq])
    return Z, {'p0': Zp.shape[1], 'flip': True,
               'sig': (int(pos.sum()), int(neg.sum())), 'name': 'D:HSIC-SCREEN'}


PROPOSED = {'C:CLIP-ALL-P': clip_all_p, 'A:MASS-WATERFILL': mass_waterfill,
            'B:TOPLAM-HYBRID': toplam_hybrid, 'D:HSIC-SCREEN': hsic_screen}

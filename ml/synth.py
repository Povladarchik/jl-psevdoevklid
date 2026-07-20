"""Контролируемые синтетические датасеты с ИЗВЕСТНЫМ расположением сигнала.

signal_in_q : классы разделяются ТОЛЬКО в отрицательной части спектра Грама.
              Здесь CLIP-ALL-P обязан провалиться, а HSIC-SCREEN -- выиграть.
signal_in_p : классы в положительной части (контроль: клип должен быть достаточен).

Механизм: строим точки в псевдоевклидовом R^{a,b}. Метка определяется координатами
в выбранной части. Матрица несходств = псевдоевклидова форма (индефинитна) + шум,
после чего спектр Грама заведомо имеет обе части.
"""
import numpy as np


def _pe_dissim(Xp, Xq, noise, rng):
    Dpp = ((Xp[:, None] - Xp[None]) ** 2).sum(-1)
    Dqq = ((Xq[:, None] - Xq[None]) ** 2).sum(-1)
    D = Dpp - Dqq
    D = D + noise * rng.standard_normal(D.shape)
    D = 0.5 * (D + D.T); np.fill_diagonal(D, 0.0)
    return D


def signal_in_q(n=600, cls=4, dp=15, dq=6, noise=0.15, seed=0):
    """Метки закодированы в q-координатах; p-координаты -- чистый шум того же масштаба."""
    rng = np.random.default_rng(seed)
    y = rng.integers(0, cls, n)
    # центры классов только в q-подпространстве
    cen_q = rng.standard_normal((cls, dq)) * 3.0
    Xq = cen_q[y] + rng.standard_normal((n, dq)) * 0.6
    Xp = rng.standard_normal((n, dp)) * 3.0        # шум, не связан с y
    return _pe_dissim(Xp, Xq, noise, rng), y, 'signal in q (4 класса)'


def signal_in_p(n=600, cls=4, dp=15, dq=6, noise=0.15, seed=1):
    """Метки в p-координатах; q -- шум. Контроль: клипа достаточно."""
    rng = np.random.default_rng(seed)
    y = rng.integers(0, cls, n)
    cen_p = rng.standard_normal((cls, dp)) * 3.0
    Xp = cen_p[y] + rng.standard_normal((n, dp)) * 0.6
    Xq = rng.standard_normal((n, dq)) * 3.0
    return _pe_dissim(Xp, Xq, noise, rng), y, 'signal in p (4 класса)'


SYNTH = {'signal-in-q': signal_in_q, 'signal-in-p': signal_in_p}

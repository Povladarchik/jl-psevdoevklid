"""ПОЛНЫЙ бенчмарк предложенных вариантов против базлайнов.

Методы: C/A/B/D (proposed) + JL, plain-JL-pq, cMDS, Landmark-MDS, SMACOF (baselines).
Датасеты: 5 реальных + 2 контролируемых синтетических.
Метрики: kNN acc (5-fold), k-means ARI, recall@10, median rel. distortion.
Всё в flip-пространстве (ассоциированная евклидова норма) для поиска/кластеризации.
Сетка m, 5 повторов, mean±std, счёт побед против классического JL.
"""
import math, json, sys, warnings
import numpy as np
from sklearn.model_selection import StratifiedKFold
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import data_real as DR, synth as SY, methods2 as M2, proposed as P
warnings.filterwarnings('ignore')

REPS = 5


def load(nm, n=600):
    if nm in SY.SYNTH:
        return SY.SYNTH[nm](n)
    return DR.get(nm, n)


def knn_euclid(Z, y, k=5, folds=5):
    """kNN по евклидову расстоянию в пространстве вложения Z."""
    y = np.asarray(y)
    if Z.shape[1] == 0:
        return float('nan')
    D = M2._sqdist(Z)
    skf = StratifiedKFold(folds, shuffle=True, random_state=0)
    acc = []
    for tr, te in skf.split(np.zeros(len(y)), y):
        nn = np.argsort(D[np.ix_(te, tr)], axis=1)[:, :k]
        acc.append(np.mean([np.bincount(y[tr][r]).argmax() for r in nn] == y[te]))
    return float(np.mean(acc))


def kmeans_ari(Z, y):
    if Z.shape[1] == 0:
        return float('nan')
    return float(adjusted_rand_score(
        y, KMeans(len(np.unique(y)), n_init=5, random_state=0).fit(Z).labels_))


def recall_at_k(Z, Dsq, k=10):
    n = len(Dsq)
    Dhat = M2._sqdist(Z)
    A = Dsq + np.eye(n) * 1e18
    B = Dhat + np.eye(n) * 1e18
    ta = np.argsort(A, 1)[:, :k]; tb = np.argsort(B, 1)[:, :k]
    return float(np.mean([len(set(ta[i]) & set(tb[i])) / k for i in range(n)]))


def distortion(Z, Dsq, meta):
    # реконструкция в родной геометрии метода: flip => евклидова; иначе pq
    Dhat = M2._sqdist(Z)
    iu = np.triu_indices(len(Dsq), 1)
    d, dh = Dsq[iu], Dhat[iu]; ok = np.abs(d) > 1e-9
    return float(np.median(np.abs(dh[ok] - d[ok]) / np.abs(d[ok])))


def run(nm, n=600):
    Dsq, y, task = load(nm, n)
    n = len(Dsq)
    m_default = 2 * math.ceil(math.log2(n) / 0.25)
    w = np.linalg.eigvalsh(M2.gram(Dsq))
    nef = float(np.abs(w[w < 0]).sum() / np.abs(w).sum())

    methods = {
        **P.PROPOSED,
        'base:JL': lambda D, m, rng, y=None: (M2.jl(D, m, rng)[0], {'flip': True}),
        'base:plain-JL-pq': lambda D, m, rng, y=None: _plain_pq(D, m, rng),
        'base:cMDS': lambda D, m, rng, y=None: (M2.cmds(D, m)[0], {'flip': True}),
        'base:Landmark': lambda D, m, rng, y=None: (M2.landmark_mds(D, m, rng)[0], {'flip': True}),
        'base:SMACOF': lambda D, m, rng, y=None: (M2.smacof(D, m, rng)[0], {'flip': True}),
    }

    out = {'dataset': nm, 'task': task, 'n': n, 'm': m_default, 'nef': round(nef, 3),
           'knn_orig': round(_knn_on_D(Dsq, y), 3), 'rows': {}}
    for name, fn in methods.items():
        R = {'knn': [], 'ari': [], 'rec': [], 'dist': []}
        det = name in P.PROPOSED or name.startswith('base:JL') or 'pq' in name or 'Landmark' in name or 'SMACOF' in name
        rr = REPS if det else 1
        for rep in range(rr):
            rng = np.random.default_rng(rep)
            Z, meta = fn(Dsq, m_default, rng, y) if name in P.PROPOSED else fn(Dsq, m_default, rng)
            R['knn'].append(knn_euclid(Z, y)); R['ari'].append(kmeans_ari(Z, y))
            R['rec'].append(recall_at_k(Z, Dsq)); R['dist'].append(distortion(Z, Dsq, meta))
        out['rows'][name] = {k: [round(float(np.nanmean(v)), 3), round(float(np.nanstd(v)), 3)]
                             for k, v in R.items()}
    return out


def _plain_pq(D, m, rng):
    Z, meta = M2.jl_pq(D, m, rng)
    return Z, {'flip': True}                 # оцениваем в flip (ассоц. норма)


def _knn_on_D(Dsq, y, k=5, folds=5):
    y = np.asarray(y)
    skf = StratifiedKFold(folds, shuffle=True, random_state=0); acc = []
    for tr, te in skf.split(np.zeros(len(y)), y):
        nn = np.argsort(Dsq[np.ix_(te, tr)], 1)[:, :k]
        acc.append(np.mean([np.bincount(y[tr][r]).argmax() for r in nn] == y[te]))
    return float(np.mean(acc))


def sweep(nm, ms, n=600):
    Dsq, y, _ = load(nm, n); n = len(Dsq)
    res = {}
    for m in ms:
        row = {}
        for name in ['C:CLIP-ALL-P', 'A:MASS-WATERFILL', 'B:TOPLAM-HYBRID', 'D:HSIC-SCREEN']:
            accs = []
            for rep in range(3):
                rng = np.random.default_rng(rep)
                Z, _ = P.PROPOSED[name](Dsq, m, rng, y)
                accs.append(knn_euclid(Z, y))
            row[name] = round(float(np.mean(accs)), 3)
        # классический JL как порог
        accs = []
        for rep in range(3):
            rng = np.random.default_rng(rep)
            accs.append(knn_euclid(M2.jl(Dsq, m, rng)[0], y))
        row['base:JL'] = round(float(np.mean(accs)), 3)
        res[m] = row
    return res


if __name__ == '__main__':
    dsets = sys.argv[1:] or (list(SY.SYNTH) + DR.ALL)
    allres = []
    for nm in dsets:
        r = run(nm)
        allres.append(r)
        print(f"\n== {nm}  (NEF={r['nef']}, kNN на D={r['knn_orig']}, m={r['m']}) ==", flush=True)
        print(f"  {'method':<18}{'kNN':>14}{'ARI':>14}{'rec@10':>14}{'dist':>12}")
        for name, v in r['rows'].items():
            print(f"  {name:<18}{v['knn'][0]:>8.3f}±{v['knn'][1]:<4.2f}"
                  f"{v['ari'][0]:>8.3f}±{v['ari'][1]:<4.2f}"
                  f"{v['rec'][0]:>8.3f}±{v['rec'][1]:<4.2f}{v['dist'][0]:>12.3f}", flush=True)
    json.dump(allres, open('proposed_results.json', 'w'), ensure_ascii=False, indent=1)
    print("\nsaved proposed_results.json")

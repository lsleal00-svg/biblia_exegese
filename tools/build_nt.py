#!/usr/bin/env python3
"""
Gera os livros do Novo Testamento (data/livros/<abrev>.json): Bíblia Livre + grego koiné.

Fontes (livres):
  - Grego: TAGNT (Translators Amalgamated Greek NT), STEPBible.org, CC BY 4.0 — texto NA28 com
    Strong e morfologia palavra por palavra (só as palavras que estão na NA28).
  - Léxico Strong grego (1890), domínio público; significados em português em tools/strong_pt.tsv.
  - Português: Bíblia Livre (BLIVRE), CC BY 4.0, corpus eBible (+ tools/blivre_faltantes.tsv).

Uso: python3 build_nt.py <pasta_fontes> <pasta_saida>
  pasta_fontes: tagnt.txt, vref.txt, por.txt, strongs/, pt_tokens2.pkl (cache dos tokens, opcional)
"""
import json, re, sys, os, math, pickle, unicodedata
from collections import defaultdict, Counter
import spacy, simplemma

SRC, OUT = sys.argv[1], sys.argv[2]
AQUI = os.path.dirname(os.path.abspath(__file__))
LIVROS = [('Mat','MAT','Mt','mt'),('Mrk','MRK','Mc','mc'),('Luk','LUK','Lc','lc'),('Jhn','JHN','Jo','jo'),('Act','ACT','At','at'),
  ('Rom','ROM','Rm','rm'),('1Co','1CO','1Co','1co'),('2Co','2CO','2Co','2co'),('Gal','GAL','Gl','gl'),('Eph','EPH','Ef','ef'),
  ('Php','PHP','Fp','fp'),('Col','COL','Cl','cl'),('1Th','1TH','1Ts','1ts'),('2Th','2TH','2Ts','2ts'),('1Ti','1TI','1Tm','1tm'),
  ('2Ti','2TI','2Tm','2tm'),('Tit','TIT','Tt','tt'),('Phm','PHM','Fm','fm'),('Heb','HEB','Hb','hb'),('Jas','JAS','Tg','tg'),
  ('1Pe','1PE','1Pe','1pe'),('2Pe','2PE','2Pe','2pe'),('1Jn','1JN','1Jo','1jo'),('2Jn','2JN','2Jo','2jo'),('3Jn','3JN','3Jo','3jo'),
  ('Jud','JUD','Jd','jd'),('Rev','REV','Ap','ap')]
# versículos do grego que a Bíblia Livre (numeração Almeida/KJV) junta ao vizinho
JUNTAR = {('3Jn', 1, 15): (1, 14), ('Rev', 12, 18): (13, 1)}

# ---------------------------------------------------------------- grego (TAGNT, só NA28)
def norm_strong(s):
    m = re.match(r'G0*(\d+)', s or '')
    return 'G' + m.group(1) if m else ''
GR = defaultdict(lambda: defaultdict(list))
for l in open(os.path.join(SRC, 'tagnt.txt'), encoding='utf-8-sig'):
    if not re.match(r'^[1-3]?[A-Z][a-z]{1,2}\.\d+\.\d+', l): continue
    c = l.rstrip('\n').split('\t')
    if len(c) < 6 or 'NA28' not in c[5]: continue
    m = re.match(r'^([1-3]?[A-Za-z]+)\.(\d+)\.(\d+)', c[0])
    b, cap, ver = m.group(1), int(m.group(2)), int(m.group(3))
    cap, ver = JUNTAR.get((b, cap, ver), (cap, ver))
    g = re.match(r'^(.*?)\s*\((.*?)\)\s*$', c[1])
    texto, tr = (g.group(1), g.group(2)) if g else (c[1], '')
    sg, _, morf = c[3].partition('=')
    lema, _, glosa = c[4].partition('=')
    GR[b][(cap, ver)].append({'g': unicodedata.normalize('NFC', texto.strip()), 'tr': tr, 's': norm_strong(sg), 'm': morf.strip(),
                              'lex': unicodedata.normalize('NFC', lema.strip()), 'glosa': glosa.strip()})

# morfologia (códigos do tipo Robinson) em português
TEMPO = {'P':'presente','I':'imperfeito','F':'futuro','A':'aoristo','R':'perfeito','L':'mais-que-perfeito','2A':'2º aoristo','2F':'2º futuro','2R':'2º perfeito','2L':'2º mais-que-perfeito'}
VOZ = {'A':'ativo','M':'médio','P':'passivo','E':'médio/passivo','D':'médio depoente','O':'passivo depoente','N':'médio/passivo depoente','Q':'ativo impessoal','X':'sem voz'}
MODO = {'I':'indicativo','S':'subjuntivo','O':'optativo','M':'imperativo','N':'infinitivo','P':'particípio','R':'particípio imperativo'}
CASO = {'N':'nominativo','G':'genitivo','D':'dativo','A':'acusativo','V':'vocativo'}
NUM = {'S':'sing.','P':'pl.'}
GEN = {'M':'masc.','F':'fem.','N':'neutro'}
CLASSE = {'N':'substantivo','A':'adjetivo','T':'artigo','P':'pronome pessoal','R':'pronome relativo','D':'pronome demonstrativo',
  'F':'pronome reflexivo','S':'pronome possessivo','K':'pronome correlativo','C':'pronome recíproco','Q':'pronome correlativo/interrogativo',
  'X':'pronome indefinido','I':'pronome interrogativo','CONJ':'conjunção','PREP':'preposição','ADV':'advérbio','PRT':'partícula',
  'COND':'conjunção condicional','INJ':'interjeição','ARAM':'palavra aramaica','HEB':'palavra hebraica'}
def cng(x):
    out = [CASO.get(x[0:1], ''), NUM.get(x[1:2], ''), GEN.get(x[2:3], '')]
    return ' '.join(o for o in out if o)
def morf_pt(code):
    code = code.split(' + ')[0]
    p = code.split('-')
    if not p or not p[0]: return ''
    if p[0] == 'V' and len(p) > 1:
        m = re.match(r'^(2?[PIFARL])([AMPEDONQX])([ISOMNPR])$', p[1])
        if not m: return 'verbo'
        base = f"verbo {TEMPO.get(m.group(1), m.group(1))} {VOZ.get(m.group(2), '')} {MODO.get(m.group(3), '')}"
        resto = p[2] if len(p) > 2 else ''
        if m.group(3) in 'PR' and resto: return (base + ' ' + cng(resto)).strip()
        if resto and resto[0] in '123': return f"{base} {resto[0]}ª p. {NUM.get(resto[1:2], '')}".strip()
        return base.strip()
    nome = CLASSE.get(p[0], p[0].lower())
    if p[0] == 'N' and len(p) > 2 and p[2] in ('P', 'PG', 'L', 'LG', 'T'): nome = {'P':'nome próprio','L':'nome de lugar','T':'substantivo (título)'}.get(p[2][0], nome)
    if len(p) > 1:
        x = p[1]
        if p[0] in 'PFS' and x and x[0] in '123': return f"{nome} {x[0]}ª p. " + cng(x[1:])
        if re.match(r'^[NGDAV][SP][MFN]?$', x): return (nome + ' ' + cng(x)).strip()
        if p[0] == 'A' and x in ('C', 'S'): return nome + (' comparativo' if x == 'C' else ' superlativo')
    return nome
FUNC_GR = {'T', 'CONJ', 'PREP', 'PRT', 'COND'}
classe_gr = lambda w: w['m'].split('-')[0].split(' ')[0]

# ---------------------------------------------------------------- português
vref = open(os.path.join(SRC, 'vref.txt'), encoding='utf-8').read().split('\n')
por = open(os.path.join(SRC, 'por.txt'), encoding='utf-8').read().split('\n')
CODES = {code for _, code, _, _ in LIVROS}
PT = defaultdict(dict)
for ref, txt in zip(vref, por):
    if not ref.strip() or not txt.strip(): continue
    bk, cv = ref.split(' ')
    if bk not in CODES: continue
    c, n = cv.split(':'); PT[bk][(int(c), int(n))] = txt.strip()
for l in open(os.path.join(AQUI, 'blivre_faltantes.tsv'), encoding='utf-8'):
    if l.startswith('#') or not l.strip(): continue
    bk, c, n, txt = l.rstrip('\n').split('\t', 3)
    if bk in CODES: PT[bk][(int(c), int(n))] = txt
# Onde a numeração da NA28 difere da Bíblia Livre (KJV), o português acompanha o grego:
# 2Co 13: a NA28 junta os vv. 12-13 da BL no v. 12, e a bênção (BL 13:14) é o v. 13.
# Fp 1:16-17: o corpus da BL vinha com os dois versículos trocados em relação ao grego.
if (13, 14) in PT['2CO']:
    PT['2CO'][(13, 12)] = PT['2CO'][(13, 12)] + ' ' + PT['2CO'][(13, 13)]
    PT['2CO'][(13, 13)] = PT['2CO'].pop((13, 14))
PT['PHP'][(1, 16)], PT['PHP'][(1, 17)] = PT['PHP'][(1, 17)], PT['PHP'][(1, 16)]
cache = os.path.join(SRC, 'pt_tokens2.pkl')
PTTOK = pickle.load(open(cache, 'rb')) if os.path.exists(cache) else {}
faltam = [(bk, c, n) for bk in PT for (c, n) in PT[bk] if (bk, c, n) not in PTTOK]
if faltam:
    print('lematizando', len(faltam))
    nlp = spacy.load('pt_core_news_sm', disable=['parser', 'ner'])
    for k, doc in zip(faltam, nlp.pipe((PT[k[0]][(k[1], k[2])] for k in faltam), batch_size=512)):
        toks = []
        for tk in doc:
            surf = tk.text.strip('-')
            if not re.search(r'\w', surf) or tk.pos_ == 'PUNCT': continue
            lem = surf if tk.pos_ == 'PROPN' else (tk.lemma_ or surf).lower()
            toks.append((surf, lem, tk.pos_, tk.text.startswith('-')))
        PTTOK[k] = toks
    pickle.dump(PTTOK, open(cache, 'wb'))
SURF = {x[0].lower() for k, toks in PTTOK.items() for x in toks}
TOK = {}
for (bk, c, n) in [(bk, c, n) for bk in PT for (c, n) in PT[bk]]:
    novo = []
    for surf, lem, pos, encl in PTTOK.get((bk, c, n), []):
        if pos in ('VERB', 'AUX'):
            l2 = simplemma.lemmatize(surf.lower(), lang='pt')
            if re.search(r'(ar|er|ir|or|ôr)$', l2): lem = l2
        novo.append((surf, lem, pos, encl))
    TOK[(bk, c, n)] = novo
FUNC_PT = {'DET', 'ADP', 'CCONJ', 'SCONJ', 'PRON'}

# ---------------------------------------------------------------- Modelo 1 (grego <-> português), no NT inteiro
def src_tokens(w): return [w['s'] or ('L:' + w['lex'])]
def modelo1(pares, nome, iters=6):
    arq = os.path.join(SRC, 'modelo_nt_' + nome + '.pkl')
    if os.path.exists(arq): return pickle.load(open(arq, 'rb'))
    tab = None
    for it in range(iters):
        cnt = defaultdict(float); tot = defaultdict(float)
        for src, tgt in pares:
            for e in tgt:
                probs = [1.0] * len(src) if tab is None else [tab.get((x, e), 1e-7) for x in src]
                z = sum(probs)
                for x, pr in zip(src, probs):
                    cc = pr / z; cnt[(x, e)] += cc; tot[x] += cc
        tab = {k: v / tot[k[0]] for k, v in cnt.items() if v / tot[k[0]] > 5e-4}
        print('EM', nome, it + 1, len(tab))
    pickle.dump(tab, open(arq, 'wb'))
    return tab
pares = []
for tb, code, ab, arq in LIVROS:
    for k, gw in GR[tb].items():
        toks = TOK.get((code,) + k)
        if not toks: continue
        pares.append((['NULL'] + [t for w in gw for t in src_tokens(w)], [x[1] for x in toks]))
print('pares grego-português:', len(pares))
tp = modelo1(pares, 'gr-pt')
tpr = modelo1([(['NULL'] + tgt, src[1:]) for src, tgt in pares], 'pt-gr')

def alinhar(hw, itens, tf, tr):
    """itens: lista de (lema, funcional, enclitico). Devolve, para cada item, (linha, morfema, nota).
    Todo item recebe uma linha: funcionais vão com a palavra de conteúdo vizinha e os
    que ficaram sem par vão para a linha da palavra vizinha mais próxima."""
    src = [(tk, i) for i, w in enumerate(hw) for tk in src_tokens(w)]
    W, J = len(hw), len(itens)
    if not W or not J: return [None] * J
    a = [None] * J
    for j, (lem, func, encl) in enumerate(itens):
        best, bp, btk = None, 0.004, None
        for tk, i in src:
            pr = 0.5 * (tf.get((tk, lem), 0) + tr.get((lem, tk), 0)) * math.exp(-4.0 * abs((i + .5) / W - (j + .5) / J))
            if pr > bp: bp, best, btk = pr, i, tk
        if best is not None: a[j] = (best, btk, bp)
    for j, (lem, func, encl) in enumerate(itens):
        if not func or (a[j] and a[j][1].startswith('H')): continue
        rng = range(j - 1, -1, -1) if encl else range(j + 1, J)
        for k in rng:
            if not itens[k][1] and a[k]:
                a[j] = (a[k][0], 'F', 0); break
    for j in range(J):
        if a[j]: continue
        viz = [k for k in range(J) if a[k] and a[k][1] != 'V']
        if viz:
            k = min(viz, key=lambda k: (abs(k - j), k < j if itens[j][1] else k > j))
            a[j] = (a[k][0], 'V', 0)
        else:
            a[j] = (min(W - 1, j * W // J), 'V', 0)
    # linhas de conteúdo que ficaram vazias "pegam" a palavra que mais lhes corresponde
    # numa linha vizinha que tenha mais de uma palavra
    for i in range(W):
        if any(x[0] == i for x in a): continue
        toks_i = src_tokens(hw[i])
        if 'H853' in toks_i: continue          # 'et (marcador de objeto) não tem tradução
        def lex_score(j):
            return max(0.5 * (tf.get((tk, itens[j][0]), 0) + tr.get((itens[j][0], tk), 0)) for tk in toks_i)
        moviveis = [j for j in range(J) if sum(1 for x in a if x[0] == a[j][0]) > 1]
        cand = [(lex_score(j) * math.exp(-1.5 * abs(a[j][0] - i)), j) for j in moviveis]
        cand = [c for c in cand if c[0] > max(0.02, (a[c[1]][2] if a[c[1]][1].startswith('H') else 0))]
        if cand:
            sc, j = max(cand)
            a[j] = (i, 'R', sc); continue
        if classe_heb(hw[i]) is None: continue
        for viz, borda in ((i - 1, -1), (i + 1, 0)):
            js = [j for j in range(J) if a[j][0] == viz and not itens[j][1]]
            if len(js) >= 2:
                j = js[borda]
                a[j] = (i, 'R', 0)
                # funcionais colados a ela vão junto
                k = j - 1
                while borda == 0 and k >= 0 and itens[k][1] and a[k][0] == viz:
                    a[k] = (i, 'R', 0); k -= 1
                break
    return a


def classe_heb(w):   # classe "de conteúdo" do grego, no formato usado acima
    c = classe_gr(w)
    return {'N': 'N', 'V': 'V', 'A': 'A', 'ADV': 'D'}.get(c)
COMPAT = {'N': {'NOUN', 'PROPN', 'ADJ'}, 'V': {'VERB', 'AUX'}, 'A': {'ADJ', 'NOUN', 'NUM'}, 'D': {'ADV', 'ADJ'}}
def lema_valido(lem, pos):
    if pos in ('VERB', 'AUX'): return bool(re.search(r'(ar|er|ir|or|ôr)$', lem)) and lem in SURF
    return len(lem) > 1
def pt_por_linha(gw, toks):
    a = alinhar(gw, [(x[1], x[2] in FUNC_PT, x[3]) for x in toks], tp, tpr)
    linhas = [[] for _ in gw]
    for j, x in enumerate(a):
        if x: linhas[x[0]].append(j)
    return linhas, a

# ---------------------------------------------------------------- traduções (Strong em PT + Bíblia Livre)
def load_js_dict(path):
    s = open(path, encoding='utf-8').read(); return json.loads(s[s.index('{'): s.rindex('}') + 1])
GRK = load_js_dict(os.path.join(SRC, 'strongs/greek/strongs-greek-dictionary.js'))
STRONG_PT = {}
for l in open(os.path.join(AQUI, 'strong_pt.tsv'), encoding='utf-8'):
    if '\t' in l:
        k, v = l.rstrip('\n').split('\t', 1)
        STRONG_PT[k] = [x.strip() for x in re.split(r',(?![^(]*\))', v) if x.strip()]
def juntar(*listas, n=14):
    vistos, out = set(), []
    for lst in listas:
        for x in lst:
            if x.lower() in vistos: continue
            vistos.add(x.lower()); out.append(x)
    return out[:n]
def traducoes(counter, n=12, minimo=2, fatia=0.01):
    tot = sum(counter.values())
    if not tot: return []
    return [w for w, c in counter.most_common(n * 2) if c >= minimo and c / tot >= fatia][:n]
def combinar(s, counter):
    base = STRONG_PT.get(s, [])
    return juntar(base, traducoes(counter, 6, 4, 0.06)) if base else traducoes(counter)

MEAN = defaultdict(Counter)
count_nt = Counter(); count_book = defaultdict(Counter)
ALINH = {}
for tb, code, ab, arq in LIVROS:
    for k, gw in GR[tb].items():
        for w in gw: count_nt[w['s']] += 1; count_book[tb][w['s']] += 1
        toks = TOK.get((code,) + k, [])
        if not toks: continue
        linhas, a = pt_por_linha(gw, toks)
        ALINH[(tb,) + k] = linhas
        for i, js in enumerate(linhas):
            cl = classe_heb(gw[i])
            if not cl or not gw[i]['s']: continue
            for j in js:
                surf, lem, pos, encl = toks[j]
                if a[j][1] != gw[i]['s'] or pos not in COMPAT[cl] or not lema_valido(lem, pos): continue
                MEAN[gw[i]['s']][lem] += 1

# ---------------------------------------------------------------- saída
os.makedirs(OUT, exist_ok=True)
for tb, code, ab, arq in LIVROS:
    verses, lex = {}, {}
    caps = defaultdict(int)
    for (c, n), txt in sorted(PT[code].items()):
        caps[c] = max(caps[c], n)
        gw = GR[tb].get((c, n), [])
        toks = TOK.get((code, c, n), [])
        linhas = ALINH.get((tb, c, n)) or [[] for _ in gw]
        rows = []
        for i, w in enumerate(gw):
            s = w['s']
            if s and s not in lex:
                e = GRK.get(s, {})
                lex[s] = [e.get('lemma', w['lex']), e.get('translit', ''), e.get('strongs_def', ''), e.get('kjv_def', ''),
                          combinar(s, MEAN[s]), traducoes(MEAN[s]), e.get('derivation', '')]
            pt = ' '.join(('-' if toks[j][3] else '') + toks[j][0] for j in linhas[i]).replace(' -', '-')
            rows.append([w['g'], w['tr'], s, w['lex'], morf_pt(w['m']), count_book[tb].get(s, 0), count_nt.get(s, 0), pt, w['glosa']])
        verses[f'{c}:{n}'] = {'pt': txt, 'gr': rows}
    data = {'livro': tb, 'testamento': 'nt', 'abrev': ab, 'capitulos': [caps[c] for c in sorted(caps)], 'versiculos': verses, 'lex_gr': lex,
            'colunas_gr': ['texto', 'translit', 'strong', 'lema', 'morfologia', 'ocorr_livro', 'ocorr_nt', 'pt', 'glosa_en'],
            'lex_campos': ['lema', 'translit', 'def_strong', 'kjv', 'traducoes (Strong em PT + Bíblia Livre)', 'traducoes so na Biblia Livre', 'derivacao']}
    path = os.path.join(OUT, arq + '.json')
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('ok', path, os.path.getsize(path) // 1024, 'KB', len(verses), 'versículos', sum(1 for v in verses.values() if not v['gr']), 'sem grego')

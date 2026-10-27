#!/usr/bin/env python3
"""
Gera os arquivos de dados do app Bíblia & Exegese (data/livros/<abrev>.json).

Fontes (todas livres):
  - Hebraico: OpenScriptures Hebrew Bible (morphhb) - WLC domínio público; lemas e morfologia CC BY 4.0
  - Léxico Strong (hebraico e grego): openscriptures/strongs - domínio público
  - Septuaginta: CenterBLC/LXX (Rahlfs 1935) - MIT
  - Português: Bíblia Livre (BLIVRE), Diego Santos, Mario Sérgio e Marco Teles - CC BY 4.0
    (texto obtido do corpus eBible, porbr2018)

Uso:
  python3 build_data.py <pasta_fontes> <pasta_saida> Gen [Exod ...]
  pasta_fontes deve conter: morphhb/, strongs/, LXX/, vref.txt, por.txt
"""
import json, re, sys, os, unicodedata
from collections import defaultdict, Counter
import xml.etree.ElementTree as ET

SRC, OUT = sys.argv[1], sys.argv[2]
WANT = sys.argv[3:] or ['Gen']

OSHB_BOOKS = ['Gen','Exod','Lev','Num','Deut','Josh','Judg','1Sam','2Sam','1Kgs','2Kgs','Isa','Jer','Ezek',
  'Hos','Joel','Amos','Obad','Jonah','Mic','Nah','Hab','Zeph','Hag','Zech','Mal','Ps','Prov','Job','Song',
  'Ruth','Lam','Eccl','Esth','Dan','Ezra','Neh','1Chr','2Chr']
LXX_NAME = {b: b for b in OSHB_BOOKS}
LXX_NAME.update({'Eccl': 'Qoh', 'Song': 'Cant', 'Dan': 'DanTh', 'Ezra': None, 'Neh': None})
VREF_NAME = {'Gen':'GEN','Exod':'EXO','Lev':'LEV','Num':'NUM','Deut':'DEU','Josh':'JOS','Judg':'JDG','Ruth':'RUT',
  '1Sam':'1SA','2Sam':'2SA','1Kgs':'1KI','2Kgs':'2KI','1Chr':'1CH','2Chr':'2CH','Ezra':'EZR','Neh':'NEH','Esth':'EST',
  'Job':'JOB','Ps':'PSA','Prov':'PRO','Eccl':'ECC','Song':'SNG','Isa':'ISA','Jer':'JER','Lam':'LAM','Ezek':'EZK',
  'Dan':'DAN','Hos':'HOS','Joel':'JOL','Amos':'AMO','Obad':'OBA','Jonah':'JON','Mic':'MIC','Nah':'NAM','Hab':'HAB',
  'Zeph':'ZEP','Hag':'HAG','Zech':'ZEC','Mal':'MAL'}
APP_ABBR = {'Gen':'Gn','Exod':'Ex','Lev':'Lv','Num':'Nm','Deut':'Dt'}

# ---------------------------------------------------------------- hebraico
NS = {'o': 'http://www.bibletechnologies.net/2003/OSIS/namespace'}

def main_strong(lemma):
    """'b/7225' -> 'H7225'; '1254 a' -> 'H1254'"""
    parts = [p.strip() for p in lemma.split('/')]
    nums = [re.match(r'(\d+)', p) for p in parts]
    nums = [m.group(1) for m in nums if m]
    return 'H' + nums[-1] if nums else None

def load_oshb(book):
    tree = ET.parse(os.path.join(SRC, 'morphhb/wlc', book + '.xml'))
    verses = {}
    for v in tree.iter('{%s}verse' % NS['o']):
        _, c, n = v.get('osisID').split('.')
        words = []
        for w in v.iter('{%s}w' % NS['o']):
            words.append({'t': w.text or '', 'lemma': w.get('lemma', ''), 'morph': w.get('morph', '')})
        verses[(int(c), int(n))] = words
    return verses

# transliteração acadêmica simplificada
CONS = {'א':'ʾ','ב':'b','ג':'g','ד':'d','ה':'h','ו':'w','ז':'z','ח':'ḥ','ט':'ṭ','י':'y','כ':'k','ך':'k','ל':'l',
  'מ':'m','ם':'m','נ':'n','ן':'n','ס':'s','ע':'ʿ','פ':'p','ף':'p','צ':'ṣ','ץ':'ṣ','ק':'q','ר':'r','ש':'š','ת':'t'}
V = {'ַ':'a','ָ':'ā','ֵ':'ē','ֶ':'e','ִ':'i','ֹ':'ō','ֺ':'ō','ֻ':'u',
  'ֱ':'ĕ','ֲ':'ă','ֳ':'ŏ','ׇ':'o'}
SHEVA, DAGESH, SHIN, SIN = 'ְ', 'ּ', 'ׁ', 'ׂ'

def translit(word):
    word = word.replace('/', '').replace('־', '-')
    word = ''.join(ch for ch in word if not ('֑' <= ch <= '֯' or ch in 'ֽ׀׃ֿׅׄ'))
    # agrupa: letra + diacríticos
    clusters = []
    for ch in word:
        if ch in CONS or ch == '-':
            clusters.append([ch, ''])
        elif clusters:
            clusters[-1][1] += ch
    out = []
    prev_vowel = False
    n = len(clusters)
    for i, (c, marks) in enumerate(clusters):
        if c == '-':
            out.append('-'); prev_vowel = False; continue
        nxt = clusters[i+1] if i + 1 < n else None
        last = (i == n - 1) or (nxt and nxt[0] == '-')
        # matres lectionis
        if c == 'ו' and marks == DAGESH and (i == 0 or not any(m in V for m in clusters[i-1][1])):
            out.append('û'); prev_vowel = True; continue
        if c == 'ו' and marks == 'ֹ' and i > 0:
            out.append('ô'); prev_vowel = True; continue
        if c == 'י' and marks == '' and i > 0 and clusters[i-1][1] and clusters[i-1][1][-1] in 'ִֵֶ':
            pv = clusters[i-1][1][-1]
            out[-1] = out[-1][:-1] + {'ִ':'î','ֵ':'ê','ֶ':'ê'}[pv]
            prev_vowel = True; continue
        if c == 'ה' and last and DAGESH not in marks and not marks:
            if out and out[-1] and out[-1][-1] in 'āeē':
                out[-1] = out[-1][:-1] + {'ā':'â','e':'ê','ē':'ê'}[out[-1][-1]]
                continue
        if c == 'א' and not marks and i > 0 and not last:
            pass
        cons = CONS[c]
        if c == 'ש':
            cons = 'ś' if SIN in marks else 'š'
        if DAGESH in marks and prev_vowel and c not in 'ה':
            cons = cons + cons
        vow = ''
        for m in marks:
            if m in V:
                vow = V[m]
        furtive = last and c in 'חעה' and marks.endswith('ַ') and i > 0 and clusters[i-1][1]
        if SHEVA in marks and not vow:
            vocal = (i == 0) or (i > 0 and SHEVA in clusters[i-1][1]) or (DAGESH in marks and prev_vowel)
            vow = 'ᵊ' if vocal and not last else ''
        if furtive:
            out.append('a' + cons)
        else:
            out.append(cons + vow)
        prev_vowel = bool(vow) and vow != 'ᵊ'
    s = ''.join(out)
    if s in ('yᵊhwâ', 'yᵊhwih', 'yᵊhōwâ', 'yhwh'):
        s = 'YHWH'
    return s

# ---------------------------------------------------------------- morfologia em português
H_STEM = {'q':'Qal','N':'Nifal','p':'Piel','P':'Pual','h':'Hifil','H':'Hofal','t':'Hitpael','o':'Polel','O':'Polal',
  'r':'Hitpolel','m':'Poel','M':'Poal','k':'Palel','K':'Pulal','Q':'Qal passivo','l':'Pilpel','L':'Polpal',
  'f':'Hitpalpel','D':'Nitpael','j':'Pealal','i':'Pilel','u':'Hotpaal','c':'Tiftil','v':'Hishtafel','w':'Nitpaal',
  'y':'Nitpoel','z':'Hitpoel'}
A_STEM = {'q':'Peal','Q':'Peil','u':'Hitpeel','N':'Nifal','p':'Pael','P':'Ithpaal','M':'Hitpaal','a':'Afel',
  'h':'Hafel','s':'Safel','e':'Shafel','H':'Hofal','i':'Itpeel','t':'Hishtafal','v':'Ishtafal','w':'Hitafal',
  'o':'Polel','z':'Ithpoel','m':'Poel','r':'Hitpolel','f':'Hitpalpel','b':'Hafel passivo','c':'Tiftil','x':'Ithpeel'}
H_TYPE = {'p':'perfeito','q':'perfeito consecutivo (weqatal)','i':'imperfeito','w':'imperfeito consecutivo (wayyiqtol)',
  'h':'coortativo','j':'jussivo','v':'imperativo','r':'particípio ativo','s':'particípio passivo',
  'a':'infinitivo absoluto','c':'infinitivo construto'}
GEN = {'m':'masc.','f':'fem.','b':'ambos os gêneros','c':'comum'}
NUM = {'s':'sing.','p':'pl.','d':'dual'}
STATE = {'a':'absoluto','c':'construto','d':'determinado'}
PERS = {'1':'1ª p.','2':'2ª p.','3':'3ª p.'}

def gns(code):
    out = []
    for ch, tab in zip(code, (GEN, NUM, STATE)):
        if ch in tab: out.append(tab[ch])
    return ' '.join(out)

def pgn(code):
    out = []
    for ch, tab in zip(code, (PERS, GEN, NUM)):
        if ch in tab: out.append(tab[ch])
    return ' '.join(out)

def heb_seg(seg, aram=False):
    if not seg: return ''
    p, r = seg[0], seg[1:]
    if p == 'N':
        kind = {'c':'substantivo comum','g':'substantivo gentílico','p':'nome próprio'}.get(r[:1], 'substantivo')
        return (kind + ' ' + gns(r[1:])).strip()
    if p == 'V':
        stem = (A_STEM if aram else H_STEM).get(r[:1], r[:1])
        t = r[1:2]
        typ = H_TYPE.get(t, t)
        rest = r[2:]
        if t in 'rs':
            return f'verbo {stem} {typ} {gns(rest)}'.strip()
        if t in 'ac':
            return f'verbo {stem} {typ}'
        return f'verbo {stem} {typ} {pgn(rest)}'.strip()
    if p == 'A':
        kind = {'a':'adjetivo','c':'numeral cardinal','g':'adjetivo gentílico','o':'numeral ordinal'}.get(r[:1], 'adjetivo')
        return (kind + ' ' + gns(r[1:])).strip()
    if p == 'P':
        kind = {'d':'pronome demonstrativo','f':'pronome indefinido','i':'pronome interrogativo','p':'pronome pessoal','r':'pronome relativo'}.get(r[:1], 'pronome')
        return (kind + ' ' + pgn(r[1:])).strip()
    if p == 'R':
        return 'preposição' + (' + artigo' if r[:1] == 'd' else '')
    if p == 'C': return 'conjunção'
    if p == 'D': return 'advérbio'
    if p == 'T':
        return {'a':'partícula afirmativa','d':'artigo definido','e':'partícula exortativa','i':'partícula interrogativa',
          'j':'interjeição','m':'partícula demonstrativa','n':'partícula negativa','o':'marcador de objeto direto',
          'r':'partícula relativa'}.get(r[:1], 'partícula')
    if p == 'S':
        if r[:1] == 'p': return 'sufixo pronominal ' + pgn(r[1:])
        return {'d':'sufixo direcional','h':'he paragógico','n':'nun paragógico'}.get(r[:1], 'sufixo')
    return seg

def heb_morph(code):
    if not code: return ''
    aram = code[0] == 'A'
    segs = code[1:].split('/')
    return ' + '.join(heb_seg(s, aram) for s in segs if s)

G_TENSE = {'P':'presente','I':'imperfeito','F':'futuro','A':'aoristo','X':'perfeito','Y':'mais-que-perfeito'}
G_VOICE = {'A':'ativo','M':'médio','P':'passivo'}
G_MOOD = {'I':'indicativo','D':'imperativo','S':'subjuntivo','O':'optativo','N':'infinitivo','P':'particípio'}
G_CASE = {'N':'nominativo','G':'genitivo','D':'dativo','A':'acusativo','V':'vocativo'}
G_NUM = {'S':'sing.','P':'pl.','D':'dual'}
G_GEN = {'M':'masc.','F':'fem.','N':'neutro'}

def cng(code):
    out = []
    for ch, tab in zip(code, (G_CASE, G_NUM, G_GEN)):
        if ch in tab: out.append(tab[ch])
    return ' '.join(out)

def greek_morph(code):
    if not code: return ''
    pos, _, rest = code.partition('.')
    if pos == 'V':
        t, v, m = rest[:1], rest[1:2], rest[2:3]
        base = f'verbo {G_TENSE.get(t,t)} {G_VOICE.get(v,v)} {G_MOOD.get(m,m)}'
        tail = rest[3:]
        if m == 'P': return base + ' ' + cng(tail)
        if m == 'N': return base
        pers = {'1':'1ª p.','2':'2ª p.','3':'3ª p.'}.get(tail[:1], '')
        return (base + ' ' + pers + ' ' + G_NUM.get(tail[1:2], '')).strip()
    name = {'N':'substantivo','A':'adjetivo','RA':'artigo','RP':'pronome pessoal','RD':'pronome demonstrativo',
      'RR':'pronome relativo','RI':'pronome interrogativo/indefinido','RX':'pronome','C':'conjunção','D':'advérbio',
      'P':'preposição','X':'partícula','I':'interjeição','M':'numeral'}.get(pos, pos)
    return (name + ' ' + cng(rest)).strip()

# ---------------------------------------------------------------- Strong
def load_js_dict(path):
    s = open(path, encoding='utf-8').read()
    s = s[s.index('{'): s.rindex('}') + 1]
    return json.loads(s)

HEB = load_js_dict(os.path.join(SRC, 'strongs/hebrew/strongs-hebrew-dictionary.js'))
GRK = load_js_dict(os.path.join(SRC, 'strongs/greek/strongs-greek-dictionary.js'))

def root_of(h):
    e = HEB.get(h)
    if not e: return None
    d = e.get('derivation', '') or ''
    if 'primitive root' in d or 'primitive word' in d: return h
    m = re.search(r'H(\d+)', d)
    return 'H' + m.group(1) if m else None

# ---------------------------------------------------------------- LXX
from tf.fabric import Fabric
TF = Fabric(locations=os.path.join(SRC, 'LXX/tf/1935'), silent='deep')
api = TF.load('book chapter verse word translit_SBL lex_utf8 strongs morphology', silent='deep')
F, L, T = api.F, api.L, api.T
LXX = defaultdict(dict)
for v in F.otype.s('verse'):
    b, c, n = T.sectionFromNode(v)
    ws = []
    for w in L.d(v, 'word'):
        ws.append({'g': F.word.v(w), 'tr': F.translit_SBL.v(w), 'lex': unicodedata.normalize('NFC', F.lex_utf8.v(w) or ''),
                   's': F.strongs.v(w) or '', 'm': F.morphology.v(w) or ''})
    LXX[b][(int(c), int(n))] = ws

# ---------------------------------------------------------------- AT inteiro: contagens e Modelo 1 (hebraico -> grego)
print('lendo AT hebraico...')
ALL = {b: load_oshb(b) for b in OSHB_BOOKS}
count_ot = Counter()
count_book = defaultdict(Counter)
for b, vs in ALL.items():
    for ws in vs.values():
        for w in ws:
            s = main_strong(w['lemma'])
            if s:
                count_ot[s] += 1
                count_book[b][s] += 1


# ---------------------------------------------------------------- versificação portuguesa
vref = open(os.path.join(SRC, 'vref.txt'), encoding='utf-8').read().split('\n')
por = open(os.path.join(SRC, 'por.txt'), encoding='utf-8').read().split('\n')
PT = defaultdict(dict)
for ref, txt in zip(vref, por):
    if not ref.strip() or not txt.strip(): continue
    bk, cv = ref.split(' ')
    c, n = cv.split(':')
    PT[bk][(int(c), int(n))] = txt.strip()

# O corpus traz a numeração portuguesa (Almeida/KJV), mas encaixada nas casas da numeração
# hebraica: os versículos que sobravam no fim de um capítulo se perderam (Gn 31:55, Êx 8:29-32,
# Lv 6:24-30, Nm 16:36-50 etc.). Eles voltam de tools/blivre_faltantes.tsv.
FALTANTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'blivre_faltantes.tsv')
for l in open(FALTANTES, encoding='utf-8'):
    if l.startswith('#') or not l.strip(): continue
    bk, c, n, txt = l.rstrip('\n').split('\t', 3)
    PT[bk][(int(c), int(n))] = txt

# mapa versificação portuguesa/KJV -> hebraica (WLC), do VerseMap do morphhb
KJV2WLC = {}
vm = open(os.path.join(SRC, 'morphhb/wlc/VerseMap.xml'), encoding='utf-8').read()
for w, k in re.findall(r'wlc="([^"]+)" kjv="([^"]+)"', vm):
    wb, wc, wn = w.split('.'); kb, kc, kn = k.split('.')
    if not (wn.isdigit() and kn.isdigit() and wc.isdigit() and kc.isdigit()): continue
    KJV2WLC[(kb, int(kc), int(kn))] = (int(wc), int(wn))
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------- alinhamento por morfemas (Modelo 1 nas duas direções)
# Cada palavra hebraica vira morfemas: prefixos (P:b, P:c, P:d...), lema (H7225) e sufixo pronominal (S:3ms).
import math, pickle, spacy, simplemma

def src_tokens(w):
    toks = []
    for p in [x.strip() for x in w['lemma'].split('/')]:
        m = re.match(r'(\d+)', p)
        if m: toks.append('H' + m.group(1))
        elif p: toks.append('P:' + p)
    for seg in (w['morph'][1:].split('/') if w['morph'] else []):
        if seg.startswith('Sp'): toks.append('S:' + seg[2:])
    return toks

def modelo1(pares, nome, iters=5):
    arq = os.path.join(SRC, 'modelo_' + nome.replace('>', '') + '.pkl')
    if os.path.exists(arq): return pickle.load(open(arq, 'rb'))
    tab = None
    for it in range(iters):
        cnt = defaultdict(float); tot = defaultdict(float)
        for src, tgt in pares:
            for e in tgt:
                probs = [1.0] * len(src) if tab is None else [tab.get((x, e), 1e-7) for x in src]
                z = sum(probs)
                for x, pr in zip(src, probs):
                    c = pr / z; cnt[(x, e)] += c; tot[x] += c
        tab = {k: v / tot[k[0]] for k, v in cnt.items() if v / tot[k[0]] > 5e-4}
        del cnt
        print('EM', nome, it + 1, len(tab))
    pickle.dump(tab, open(arq, 'wb'))
    return tab

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
        if classe_heb(hw[i]['morph']) is None: continue
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

# ---------------------------------------------------------------- português (Bíblia Livre)
cache = os.path.join(SRC, 'pt_tokens2.pkl')
PTTOK = pickle.load(open(cache, 'rb')) if os.path.exists(cache) else {}
keys = [(bk, c, n) for bk in PT for (c, n) in PT[bk] if (bk, c, n) not in PTTOK]
if keys:
    print('lematizando a Bíblia Livre...', len(keys))
    nlp = spacy.load('pt_core_news_sm', disable=['parser', 'ner'])
    for k, doc in zip(keys, nlp.pipe((PT[k[0]][(k[1], k[2])] for k in keys), batch_size=512)):
        toks = []
        for tk in doc:
            surf = tk.text.strip('-')
            if not re.search(r'\w', surf) or tk.pos_ == 'PUNCT': continue
            lem = surf if tk.pos_ == 'PROPN' else (tk.lemma_ or surf).lower()
            toks.append((surf, lem, tk.pos_, tk.text.startswith('-')))
        PTTOK[k] = toks
    pickle.dump(PTTOK, open(cache, 'wb'))
# verbos: lematizador de dicionário (simplemma) é mais confiável que o do spaCy
SURF = {x[0].lower() for toks in PTTOK.values() for x in toks}
for k, toks in PTTOK.items():
    novo = []
    for surf, lem, pos, encl in toks:
        if pos in ('VERB', 'AUX'):
            l2 = simplemma.lemmatize(surf.lower(), lang='pt')
            if re.search(r'(ar|er|ir|or|ôr)$', l2): lem = l2
        novo.append((surf, lem, pos, encl))
    PTTOK[k] = novo

FUNC_PT = {'DET', 'ADP', 'CCONJ', 'SCONJ', 'PRON'}
CODE2B = {v: k for k, v in VREF_NAME.items()}
ppairs = []
for (bk, c, n), toks in PTTOK.items():
    b = CODE2B.get(bk)
    if not b or not toks: continue
    hk = KJV2WLC.get((b, c, n), (c, n))
    hw = ALL[b].get(hk)
    if not hw: continue
    src = ['NULL'] + [tk for w in hw for tk in src_tokens(w)]
    ppairs.append((src, [x[1] for x in toks], hw, toks, b, hk, (c, n)))
print('pares hebraico-português:', len(ppairs))
tp = modelo1([(src, tgt) for src, tgt, *_ in ppairs], 'he->pt')
tpr = modelo1([(['NULL'] + tgt, src[1:]) for src, tgt, *_ in ppairs], 'pt->he')

# ---------------------------------------------------------------- grego (LXX): todas as palavras do versículo
FUNC_GR = {'RA', 'C', 'P', 'X'}
def gr_itens(gw):
    return [(g['lex'], g['m'].split('.')[0] in FUNC_GR, False) for g in gw]
gpairs = []
for b, vs in ALL.items():
    lb = LXX_NAME.get(b)
    if not lb or lb not in LXX: continue
    for k, hw in vs.items():
        gw = LXX[lb].get(k)
        if not gw: continue
        src = ['NULL'] + [tk for w in hw for tk in src_tokens(w)]
        gpairs.append((src, [g['lex'] for g in gw]))
print('pares hebraico-grego:', len(gpairs))
tg = modelo1(gpairs, 'he->gr')
tgr = modelo1([(['NULL'] + tgt, src[1:]) for src, tgt in gpairs], 'gr->he')

# ---------------------------------------------------------------- LXX: versículo correspondente
# A LXX de Rahlfs reordena trechos (Êx 35-40, Nm 1, 6, 10, 26...). O mapa vem da tabela TVTMS do
# STEPBible (CC BY); cada candidato é conferido pelo alinhamento, e fica o que mais corresponde.
def _tvtms_refs(expr):
    expr = expr.strip()
    if not expr or expr.startswith('Absent'):
        m = re.search(r'\[=\s*([^\]]+)\]', expr)
        if not m: return None
        expr = m.group(1)
    expr = re.sub(r'\[.*?\]', '', expr).strip()
    out, ch = [], None
    for part in re.split(r'[;,]', expr):
        part = re.sub(r'^[A-Za-z0-9]+\.', '', part.strip())
        m = re.match(r'(?:(\d+):)?(\d+)(\.\d+)?(?:-(?:(\d+):)?(\d+)(?:\.\d+)?)?$', part)
        if not m: continue
        if m.group(1): ch = int(m.group(1))
        elif ch is None: continue
        a = int(m.group(2))
        if m.group(3) and m.group(5) and not m.group(4): out.append((ch, a)); continue
        if m.group(5):
            ch2 = int(m.group(4)) if m.group(4) else ch; b = int(m.group(5))
            out += [(ch, x) for x in range(a, b + 1)] if ch2 == ch else [(ch, a), (ch2, b)]
        else: out.append((ch, a))
    return out

def carregar_tvtms(path):
    TV = {'Gen': 'Gen', 'Exo': 'Exod', 'Lev': 'Lev', 'Num': 'Num', 'Deu': 'Deut', 'Jos': 'Josh', 'Jdg': 'Judg', 'Rut': 'Ruth'}
    M = {}
    if not os.path.exists(path): return M
    linhas = open(path, encoding='utf-8-sig').read().split('\n')
    i0 = next(i for i, l in enumerate(linhas) if l.startswith('#DataStart(Condensed)'))
    i1 = next(i for i, l in enumerate(linhas) if l.startswith('#DataEnd(Condensed)'))
    book = gi = None
    for l in linhas[i0:i1]:
        c = l.rstrip('\t').split('\t')
        if l.startswith('$'):
            book = TV.get(c[0][1:4]); gi = next((k for k, x in enumerate(c) if x.strip().startswith('Greek')), None); continue
        if not book or gi is None or len(c) <= gi or c[0].startswith('TEST') or not c[1].strip(): continue
        k, g = _tvtms_refs(c[1]), _tvtms_refs(c[gi])
        if not k or g is None: continue
        k, g = list(dict.fromkeys(k)), list(dict.fromkeys(g))
        if len(k) == len(g):
            for x, y in zip(k, g): M.setdefault((book,) + x, []).append(y)
        else:
            for x in k: M.setdefault((book,) + x, []).extend(g)
    return M
TVTMS = carregar_tvtms(os.path.join(SRC, 'tvtms.txt'))

def nota_lxx(hw, gw):
    hs = {tk for w in hw for tk in src_tokens(w) if tk.startswith('H')}
    its = [g['lex'] for g in gw if g['m'].split('.')[0] not in FUNC_GR]
    if not hs or not its: return 0
    s = sum(max(0.5 * (tg.get((x, l), 0) + tgr.get((l, x), 0)) for x in hs) for l in its) / len(its)
    return s * min(1, len(its) / len(hs)) ** 0.3 * min(1, len(hs) / len(its)) ** 0.3

def lxx_do_versiculo(b, kjv, hk, hw):
    """Devolve (palavras gregas, lista de versículos da LXX usados)."""
    lb = LXX_NAME.get(b)
    if not lb or lb not in LXX: return [], []
    G = LXX[lb]
    cands = [[hk]]
    # onde a numeração hebraica já difere da portuguesa (Êx 8, Lv 6, Nm 17, Dt 13, 23...), o
    # CenterBLC segue a hebraica; a TVTMS só entra nos trechos que a LXX reordena.
    t = TVTMS.get((b,) + kjv) if hk == kjv else None
    if t: cands.append(list(dict.fromkeys(t)))
    melhor, nm = None, -1
    for cand in cands:
        gw = [w for k in cand for w in G.get(k, [])]
        if not gw: continue
        sc = nota_lxx(hw, gw) + (0 if cand == [hk] else 0.08)   # a tabela TVTMS tem a preferência; o alinhamento só a corrige quando ela não confere
        if sc > nm: melhor, nm = cand, sc
    if not melhor: return [], []
    return [w for k in melhor for w in G.get(k, [])], melhor

def grego_por_linha(hw, gw):
    a = alinhar(hw, gr_itens(gw), tg, tgr)
    linhas = [[] for _ in hw]
    for j, x in enumerate(a):
        if x: linhas[x[0]].append(j)
    principal = []
    for i, js in enumerate(linhas):
        if not js: principal.append(-1); continue
        cand = [j for j in js if a[j][1].startswith('H')] or [j for j in js if not gr_itens([gw[j]])[0][1]] or js
        principal.append(max(cand, key=lambda j: a[j][2]))
    return linhas, principal

def pt_por_linha(hw, toks):
    a = alinhar(hw, [(x[1], x[2] in FUNC_PT, x[3]) for x in toks], tp, tpr)
    linhas = [[] for _ in hw]
    for j, x in enumerate(a):
        if x: linhas[x[0]].append(j)
    return linhas, a

# ---------------------------------------------------------------- traduções (como a Bíblia Livre verte cada termo)
COMPAT = {'N': {'NOUN', 'PROPN', 'ADJ'}, 'V': {'VERB', 'AUX'}, 'P': {'VERB', 'AUX', 'NOUN', 'ADJ'},
          'A': {'ADJ', 'NOUN', 'NUM'}, 'D': {'ADV', 'ADJ'}}
def classe_heb(morph):
    for seg in (morph[1:].split('/') if morph else []):
        if seg[:1] == 'V': return 'P' if seg[2:3] in ('r', 's') else 'V'
        if seg[:1] in 'NAD': return seg[:1]
    return None
def lema_valido(lem, pos):
    if pos in ('VERB', 'AUX'): return bool(re.search(r'(ar|er|ir|or|ôr)$', lem)) and lem in SURF
    return len(lem) > 1

MEAN_H = defaultdict(Counter)
MEAN_G = defaultdict(Counter)
for src, tgt, hw, toks, b, hk, (c, n) in ppairs:
    linhas, a = pt_por_linha(hw, toks)
    gw = lxx_do_versiculo(b, (c, n), hk, hw)[0]
    gprinc = grego_por_linha(hw, gw)[1] if gw else [-1] * len(hw)
    for i, js in enumerate(linhas):
        h = main_strong(hw[i]['lemma'])
        cl = classe_heb(hw[i]['morph'])
        if not cl or not h: continue
        for j in js:
            surf, lem, pos, encl = toks[j]
            if a[j][1] != h or pos not in COMPAT[cl] or not lema_valido(lem, pos): continue
            MEAN_H[h][lem] += 1
            if gprinc[i] >= 0:
                g = gw[gprinc[i]]
                MEAN_G[g['s'] or ('L:' + g['lex'])][lem] += 1

# família de cada raiz: todos os lemas que o Strong deriva dela
FAMILIA = defaultdict(Counter)
for h, cnt in list(MEAN_H.items()):
    r = root_of(h)
    if r: FAMILIA[r].update(cnt)
    if r != h: FAMILIA[h].update(cnt)   # a própria palavra conta na sua "família"

# Significados de Strong traduzidos para o português (tools/strong_pt.tsv; tradução do
# Strong's Concordance de 1890, domínio público). Somados às traduções usadas pela Bíblia Livre.
STRONG_PT = {}
for l in open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'strong_pt.tsv'), encoding='utf-8'):
    if '\t' in l:
        k, v = l.rstrip('\n').split('\t', 1)
        STRONG_PT[k] = [x.strip() for x in re.split(r',(?![^(]*\))', v) if x.strip()]

def juntar(*listas, n=14):
    vistos, out = set(), []
    for lst in listas:
        for x in lst:
            k = x.lower()
            if k in vistos: continue
            vistos.add(k); out.append(x)
    return out[:n]

def traducoes(counter, n=12, minimo=2, fatia=0.01):
    tot = sum(counter.values())
    if not tot: return []
    return [w for w, c in counter.most_common(n * 2) if c >= minimo and c / tot >= fatia][:n]

def combinar(chave_strong, counter, extras=True):
    # com verbete traduzido: só acrescenta usos bem frequentes da Bíblia Livre
    base = STRONG_PT.get(chave_strong, []) if chave_strong else []
    if base:
        return juntar(base, traducoes(counter, 6, 4, 0.06)) if extras else base
    return traducoes(counter)

# ---------------------------------------------------------------- saída por livro
for b in WANT:
    vs = ALL[b]; lb = LXX_NAME.get(b); code = VREF_NAME[b]
    lex_h, lex_g = {}, {}
    verses = {}
    for (c, n), txt in sorted(PT[code].items()):
        hk = KJV2WLC.get((b, c, n), (c, n))
        hw = vs.get(hk, [])
        gw, gks = lxx_do_versiculo(b, (c, n), hk, hw) if hw else ([], [])
        toks_v = PTTOK.get((code, c, n), [])
        glinhas, gprinc = grego_por_linha(hw, gw) if (hw and gw) else ([[] for _ in hw], [-1] * len(hw))
        plinhas = pt_por_linha(hw, toks_v)[0] if (hw and toks_v) else [[] for _ in hw]
        rows = []
        for i, w in enumerate(hw):
            h = main_strong(w['lemma'])
            r = root_of(h) if h else None
            for x in (h, r):
                if x and x in HEB and x not in lex_h:
                    e = HEB[x]
                    lex_h[x] = [e.get('lemma',''), e.get('xlit',''), e.get('strongs_def',''), e.get('kjv_def',''),
                                combinar(x, MEAN_H[x]), traducoes(MEAN_H[x])]
            pt = ' '.join(('-' if toks_v[j][3] else '') + toks_v[j][0] for j in plinhas[i]).replace(' -', '-')
            rows.append([w['t'].replace('/', ''), translit(w['t']), h or '', r or '', heb_morph(w['morph']),
                         count_book[b].get(h, 0), count_ot.get(h, 0), glinhas[i], pt, gprinc[i]])
        g_rows = []
        for g in gw:
            s = g['s']
            k = s or ('L:' + g['lex'])
            if k not in lex_g:
                e = GRK.get(s, {})
                lex_g[k] = [e.get('lemma', g['lex']), e.get('translit',''), e.get('strongs_def',''), e.get('kjv_def',''),
                            combinar(s, MEAN_G[k], extras=False), traducoes(MEAN_G[k])]
            g_rows.append([g['g'], g['tr'], g['lex'], s, greek_morph(g['m'])])
        verses[f'{c}:{n}'] = {'pt': txt, 'he': rows, 'gr': g_rows}
        if hk != (c, n):
            verses[f'{c}:{n}']['heb_ref'] = f'{hk[0]}:{hk[1]}'
        if gks and gks != [hk]:
            verses[f'{c}:{n}']['lxx_ref'] = '; '.join(f'{x}:{y}' for x, y in gks)
    caps = defaultdict(int)
    for (c, n) in PT[code]:
        caps[c] = max(caps[c], n)
    data = {'livro': b, 'capitulos': [caps[c] for c in sorted(caps)], 'abrev': APP_ABBR.get(b, b), 'versiculos': verses,
            'lex_he': lex_h, 'lex_gr': lex_g,
            'colunas_he': ['texto','translit','strong','raiz','morfologia','ocorr_livro','ocorr_at','lxx_indices','pt','lxx_principal'],
            'lex_campos': ['lema','translit','def_strong','kjv','traducoes (Strong em PT + Bíblia Livre)','traducoes so na Biblia Livre'],
            'colunas_gr': ['texto','translit','lema','strong','morfologia']}
    path = os.path.join(OUT, APP_ABBR.get(b, b).lower() + '.json')
    json.dump(data, open(path, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('ok', path, os.path.getsize(path) // 1024, 'KB', len(verses), 'versículos')

if os.environ.get('DEBUG_ALIGN'):
    hw = ALL['Gen'][(1, 1)]; gw = LXX['Gen'][(1, 1)]
    for j, it in enumerate(gr_itens(gw)):
        print(gw[j]['g'], it, [(tk, round(tg.get((tk, it[0]), 0), 3), round(tgr.get((it[0], tk), 0), 3)) for w in hw for tk in src_tokens(w)][:9])
    print(alinhar(hw, gr_itens(gw), tg, tgr))

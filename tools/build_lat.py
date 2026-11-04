#!/usr/bin/env python3
"""
Acrescenta a Vulgata latina aos livros do Antigo Testamento (data/livros/<livro>.json).

Fontes (livres):
  - Latim: "Latin Vulgate" (texto de Jerônimo, módulo do projeto SWORD/CrossWire, domínio público),
    via scrollmapper/bible_databases (sources/la/Vulgate/Vulgate.json). Nos Salmos esse arquivo traz,
    em cada versículo, o Saltério Galicano seguido do Saltério iuxta Hebraeos; aqui fica só o
    iuxta Hebraeos (a separação usa a Vulgata Clementina, que traz só o Galicano, como referência).
  - Numeração: tabela TVTMS do STEPBible (CC BY), coluna "Latin" (Vulgata).
  - Léxico: Lewis & Short, A Latin Dictionary (1879), domínio público, edição XML do Perseus (CC BY-SA).
    Significados em português: tools/latim_pt.tsv.
  - Lemas: simplemma (MIT).

Uso: python3 build_lat.py <pasta_fontes> <pasta_livros>
  pasta_fontes: VulgateSrc.json, VulgClementine.txt, lat.ls.perseus-eng1.xml, tvtms.txt
  pasta_livros: data/livros (os arquivos do AT são reescritos com a Vulgata acrescentada)
"""
import json, re, sys, os, math, difflib, unicodedata
from collections import defaultdict, Counter
import xml.etree.ElementTree as ET
import simplemma

SRC, LIV = sys.argv[1], sys.argv[2]
AQUI = os.path.dirname(os.path.abspath(__file__))

VULG_NOME = {'Gen': 'Genesis', 'Exod': 'Exodus', 'Lev': 'Leviticus', 'Num': 'Numbers', 'Deut': 'Deuteronomy',
  'Josh': 'Joshua', 'Judg': 'Judges', 'Ruth': 'Ruth', '1Sam': 'I Samuel', '2Sam': 'II Samuel', '1Kgs': 'I Kings',
  '2Kgs': 'II Kings', '1Chr': 'I Chronicles', '2Chr': 'II Chronicles', 'Ezra': 'Ezra', 'Neh': 'Nehemiah',
  'Esth': 'Esther', 'Job': 'Job', 'Ps': 'Psalms', 'Prov': 'Proverbs', 'Eccl': 'Ecclesiastes', 'Song': 'Song of Solomon',
  'Isa': 'Isaiah', 'Jer': 'Jeremiah', 'Lam': 'Lamentations', 'Ezek': 'Ezekiel', 'Dan': 'Daniel', 'Hos': 'Hosea',
  'Joel': 'Joel', 'Amos': 'Amos', 'Obad': 'Obadiah', 'Jonah': 'Jonah', 'Mic': 'Micah', 'Nah': 'Nahum', 'Hab': 'Habakkuk',
  'Zeph': 'Zephaniah', 'Hag': 'Haggai', 'Zech': 'Zechariah', 'Mal': 'Malachi'}

def limpa(t):
    t = re.sub(r'[\[\]()*;0-9]', ' ', t)
    return ' '.join(t.split())

# ---------------------------------------------------------------- texto latino
VG = json.load(open(os.path.join(SRC, 'VulgateSrc.json'), encoding='utf-8'))
LAT = {}
for b in VG['books']:
    LAT[b['name']] = {(v['chapter'], v['verse']): limpa(v['text']) for c in b['chapters'] for v in c['verses']}

# ------------------------------------------- Salmos: separar o Galicano do iuxta Hebraeos
def nlat(w):
    w = w.lower().replace('æ', 'ae').replace('œ', 'oe').replace('j', 'i')
    w = unicodedata.normalize('NFD', w); w = ''.join(c for c in w if not unicodedata.combining(c))
    w = re.sub(r'[^a-z]', '', w)
    for a, b in [('adol', 'adul'), ('inp', 'imp'), ('adc', 'acc'), ('conl', 'coll'), ('inl', 'ill'), ('inm', 'imm'),
                 ('adp', 'app'), ('ads', 'ass'), ('conp', 'comp'), ('quum', 'cum'), ('mihi', 'mi')]:
        w = w.replace(a, b)
    return w
CLEM = {}
_cur = None
for l in open(os.path.join(SRC, 'VulgClementine.txt'), encoding='utf-8'):
    if l.startswith('### '): _cur = l[4:].strip(); continue
    m = re.match(r'\[(\d+):(\d+)\]\s*(.*)', l)
    if m and _cur == 'Psalms': CLEM[(int(m[1]), int(m[2]))] = m[3]
# conferidos à mão (a fonte junta, corta ou não traz a parte iuxta Hebraeos)
PS_HIE_INICIO = {(13, 3): 'omnes recesserunt', (42, 5): 'quare incurvaris', (51, 2): 'cum venisset',
  (51, 6): 'dilexisti omnia verba ad', (67, 1): 'victori David', (77, 71): 'ut pasceret', (88, 1): 'eruditionis',
  (88, 37): 'semen eius in sempiternum', (138, 1): 'pro victoria', (145, 1): 'alleluia'}
PS_HIE_TEXTO = {(15, 10): 'non enim derelinques animam meam in inferno nec dabis sanctum tuum videre corruptionem',
  (15, 11): 'ostendes mihi semitam vitae plenitudinem laetitiarum ante vultum tuum decores in dextera tua aeternos',
  (34, 20): None, (135, 27): None}
def separar_salmo(key, txt):
    if key in PS_HIE_TEXTO: return PS_HIE_TEXTO[key]
    ws = txt.split()
    if not ws: return None
    if key in PS_HIE_INICIO:
        alvo = PS_HIE_INICIO[key].split()
        for k in range(len(ws) - 1, 0, -1):   # última ocorrência (a frase pode aparecer também no Galicano)
            if ws[k:k + len(alvo)] == alvo: return ' '.join(ws[k:])
    g = [x for x in (nlat(w) for w in CLEM.get(key, '').split()) if x]
    nw = [nlat(x) for x in ws]
    if not g: return ' '.join(ws)
    melhor = (-1, None)
    for k in range(1, len(ws)):
        s = difflib.SequenceMatcher(None, nw[:k], g, autojunk=False).ratio() + (0.05 if nw[k] == nw[0] else 0)
        if s > melhor[0]: melhor = (s, k)
    k = melhor[1]
    while k < len(ws) and nw[k] == 'diapsalma': k += 1      # "diapsalma" é do Galicano (o iuxta Hebraeos diz "semper")
    return ' '.join(ws[k:]) or None
LAT['Psalms'] = {k: separar_salmo(k, t) for k, t in LAT['Psalms'].items()}
# Ps 15:10 da fonte traz também o v. 11 do iuxta Hebraeos; o v. 11 da fonte é só o Galicano.

# ---------------------------------------------------------------- numeração (TVTMS, coluna Latin)
_src = open(os.path.join(AQUI, 'build_data.py'), encoding='utf-8').read()
_i, _j = _src.index('def _tvtms_refs'), _src.index('TVTMS = carregar_tvtms')
_g = {'re': re, 'os': os}
# (as linhas "Absent [= Sus 1:1]" dos acréscimos de Daniel não podem virar chave de Daniel 1)
exec(_src[_i:_j].replace("startswith('Greek')", "startswith('Latin')")
     .replace("k = _tvtms_refs(c[1])", "k = None if re.match(r'(Absent|Sus|Bel|Aza|S3Y|Man|1Es|2Es|Pra)', c[1].strip()) else _tvtms_refs(c[1])"), _g)
TVL = _g['carregar_tvtms'](os.path.join(SRC, 'tvtms.txt'))

# ---------------------------------------------------------------- Lewis & Short
def chave(s):
    s = unicodedata.normalize('NFD', s.lower()); s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z]', '', s.replace('j', 'i').replace('v', 'u'))
def texto(el):
    return ''.join(el.itertext()) if el is not None else ''
# abreviações gramaticais do Lewis & Short que não são definição
ABREV = {'gen', 'dat', 'acc', 'abl', 'voc', 'nom', 'plur', 'sing', 'init', 'fin', 'perf', 'fut', 'inf', 'imperf', 'pass', 'subj',
  'n', 'cr', 'adv', 'prep', 'conj', 'pron', 'masc', 'fem', 'neutr', 'comp', 'sup', 'posit', 'act', 'med', 'pres', 'imper',
  'indic', 'part', 'sync', 'redupl', 'parag', 'plqpf', 'tempp', 'perff', 'press', 'gerund', 'impers', 'dep', 'v', 'a', 'd',
  'pers', 'st', 'f', 'm', 'interrog', 'demonstr', 'poss', 'possess', 'obj', 'rel', 'indef', 'num', 'card', 'ord', 'irreg',
  'defect', 'l', 'ext', 'no', 'ph', 'do', 'to', 'th', 'pl', 'cf', 'al', 'id', 'ib', 'sq', 'sqq', 'e', 'i', 'ii', 'o', 'u',
  'praep', 'interj', 'freq', 'class', 'p', 'and', 'with', 'of', 'in', 'sc', 'gov', 'unt', 'futur', 'ap', 'af', 'ab', 'au', 'ex', 'si', 'ne', 'quidem'}
LS = {}
for ev, el in ET.iterparse(os.path.join(SRC, 'lat.ls.perseus-eng1.xml')):
    if el.tag != 'entryFree': continue
    key = re.sub(r'\d+$', '', el.get('key', ''))
    orth = el.find('orth')
    itype, pos, gen = el.find('itype'), el.find('pos'), el.find('gen')
    gl = []
    for s in el.iter('sense'):
        for hi in s.findall('hi'):
            t = texto(hi).strip(' ,;.:')
            if t and len(t) < 80 and t not in gl and not re.match(r'^(lit|trop|transf|fig|absol|in gen|in partic|subst|part|adj|sc|i\. e|esp|freq)\b', t) \
               and not all(x.lower().strip('.') in ABREV for x in re.split(r'[\s.]+', t) if x): gl.append(t)
        if len(gl) >= 4: break
    k = chave(key)
    e = {'key': key.replace('j', 'i'), 'orth': texto(orth).strip() or key, 'itype': texto(itype).strip(), 'pos': texto(pos).strip(),
         'gen': texto(gen).strip(), 'en': '; '.join(gl[:4])}
    if k:
        if k not in LS: LS[k] = e
        elif chave(e['orth']) == k and len(LS[k].get('homs', [1])) < 3:   # homógrafo (caro "cardar" / caro "carne")
            x = LS[k]; x.setdefault('homs', [dict(x)]); x['homs'].append(e)
            x['en'] = ' | '.join(f"{i + 1}) {h['en']}" for i, h in enumerate(x['homs']) if h['en'])
            x['pos'] = ' / '.join(dict.fromkeys(h['pos'] or h['gen'] for h in x['homs'] if h['pos'] or h['gen']))
            x['gen'] = ''
    el.clear()
print('Lewis & Short:', len(LS), 'verbetes')

PT = {}
_f = os.path.join(AQUI, 'latim_pt.tsv')
if os.path.exists(_f):
    for l in open(_f, encoding='utf-8'):
        p = l.rstrip('\n').split('\t')
        if len(p) >= 2 and p[1].strip(): PT[p[0]] = [x.strip() for x in p[1].split(',') if x.strip()]

# ---------------------------------------------------------------- lematização
# A Vulgata de Jerônimo escreve sem assimilar os prefixos (adfligo, conpleo, inmundus) e com "e" por "ae";
# o Lewis & Short usa a grafia clássica. Cada lema é procurado também nessas variantes.
PREF = [('adf', 'aff'), ('adn', 'ann'), ('adp', 'app'), ('ads', 'ass'), ('adt', 'att'), ('adc', 'acc'), ('adg', 'agg'),
  ('adl', 'all'), ('adr', 'arr'), ('adq', 'acq'), ('conp', 'comp'), ('conb', 'comb'), ('conm', 'comm'), ('conl', 'coll'),
  ('conr', 'corr'), ('inp', 'imp'), ('inb', 'imb'), ('inm', 'imm'), ('inl', 'ill'), ('inr', 'irr'), ('obp', 'opp'),
  ('subp', 'supp'), ('subf', 'suff'), ('subc', 'succ'), ('subg', 'sugg'), ('subm', 'summ'), ('exp', 'exsp'), ('ext', 'exst'),
  ('exs', 'exs'), ('ads', 'as')]
MEIO = [('', ''), ('e', 'ae'), ('ch', 'c'), ('f', 'ph'), ('i', 'y'), ('br', 'bbr'), ('br', 'ccbr'), ('ach', 'acch'), ('mn', 'mpn'), ('h', '')]
SUF = [('', ''), ('or', 'o'), ('o', 'or'), ('i', 'io'), ('us', 'um'), ('e', 'ia'), ('a', 'ae'), ('a', 'us'), ('um', 'us'), ('us', 'a'),
  ('ns', 'o'), ('ens', 'o'), ('ens', 'eo'), ('iens', 'io'), ('iens', 'ior'), ('ens', 'or'), ('ans', 'o'), ('ans', 'or'), ('tus', 'o'), ('itus', 'o'), ('atus', 'or'),
  ('atus', 'o'), ('sus', 'do'), ('ctus', 'co'), ('issimus', 'is'), ('issimus', 'us'), ('ior', 'us'), ('ior', 'is'), ('ius', 'us')]
LEMA_FIX = {'adips': 'adeps', 'gazofilacium': 'gazophylacium', 'benedictum': 'benedico', 'benedictus': 'benedico'}
def busca_ls(l):
    l = LEMA_FIX.get(l, l)
    k0 = chave(l)
    if k0 in LS: return k0
    for a, b in PREF + [('', '')]:
        k1 = b + k0[len(a):] if a and k0.startswith(a) else (k0 if not a else None)
        if k1 is None: continue
        for c, d in MEIO:
            k2s = [k1] if not c else ([k1.replace(c, d, 1)] if c in k1 else [])
            for k2 in k2s:
                for e, f in SUF:
                    if e and not k2.endswith(e): continue
                    k3 = (k2[:-len(e)] if e else k2) + f
                    if k3 in LS: return k3
    return None

# lemas errados do simplemma (conferidos)
FORMA = {'ducenti': 'ducenti', 'ducentos': 'ducenti', 'ducentae': 'ducenti', 'ducenta': 'ducenti', 'ducentis': 'ducenti',
  'ducentas': 'ducenti', 'adversus': 'adversus', 'adversum': 'adversus', 'da': 'do', 'date': 'do', 'amplius': 'amplius',
  'prius': 'prius', 'priusquam': 'priusquam', 'sibi': 'sui', 'se': 'sui', 'sese': 'sui', 'vobiscum': 'vos', 'nobiscum': 'nos',
  'mecum': 'ego', 'tecum': 'tu', 'secum': 'sui', 'usquequo': 'usque', 'foedus': 'foedus', 'foederis': 'foedus',
  'foedere': 'foedus', 'foedera': 'foedus', 'quoque': 'quoque', 'post': 'post', 'ante': 'ante', 'contra': 'contra',
  'super': 'super', 'iuxta': 'iuxta', 'coram': 'coram', 'propter': 'propter', 'dixit': 'dico', 'ait': 'aio', 'inquit': 'inquam',
  'regis': 'rex', 'regi': 'rex', 'ibi': 'ibi', 'sui': 'suus', 'vero': 'vero', 'vocem': 'vox', 'altare': 'altare',
  'altaris': 'altare', 'altari': 'altare', 'altaria': 'altare', 'altarium': 'altare', 'tribus': 'tribus', 'e': 'ex',
  'pactum': 'pactum', 'pacti': 'pactum', 'pacto': 'pactum', 'desertum': 'desertum', 'deserto': 'desertum', 'deserti': 'desertum',
  'servis': 'servus', 'viris': 'vir', 'mi': 'meus', 'forte': 'forte'}
DIVINOS = {'dominus', 'deus', 'spiritus', 'altissimus', 'omnipotens', 'sanctus', 'pater', 'dominator', 'salvator', 'rex', 'filius', 'creator'}
ENCL = ('que', 'ne', 've')
SEM_ENCL = {'quoque', 'atque', 'neque', 'itaque', 'quisque', 'usque', 'undique', 'utique', 'denique', 'plerumque',
  'ubique', 'namque', 'absque', 'uterque', 'utrumque', 'utraque', 'quicumque', 'quaecumque', 'quodcumque', 'quacumque',
  'quocumque', 'utrimque', 'cumque', 'quandoque', 'unusquisque', 'unaquaeque', 'unumquodque', 'quidque', 'quemque',
  'quaeque', 'cuiusque', 'cuique', 'bene', 'ne', 'pone', 'paene', 'sine', 'nonne', 'ive', 'sive', 'neve', 'seu', 'deinde',
  'inde', 'unde', 'aliunde', 'peraeque', 'quinque', 'utroque', 'utriusque'}
# formas que aparecem em minúscula em algum lugar do AT (as outras, com maiúscula, são nomes próprios)
_cnt = Counter()
for _b in VULG_NOME.values():
    for _t in LAT[_b].values():
        if _t: _cnt.update(_t.split())
# forma com maiúscula que quase nunca aparece em minúscula = nome próprio (Levi x levi "leve")
MINUSC = {w for w, n in _cnt.items() if w[:1].islower() and n * 3 >= _cnt.get(w[:1].upper() + w[1:], 0)}
PROPRIO = '@'
_lcache = {}
def lema(w):
    """devolve (lema, enclítico); nome próprio: ('@Nome', '')"""
    if w in _lcache: return _lcache[w]
    lw = w.lower()
    res = None
    if w[:1].isupper() and lw not in MINUSC:
        l = simplemma.lemmatize(lw, lang='la')
        if chave(l) not in DIVINOS:
            res = (PROPRIO + (w if not w.isupper() else w.title()), '')
    if res is None:
        cands = [(FORMA.get(lw) or simplemma.lemmatize(lw, lang='la'), '')]
        if lw not in SEM_ENCL:
            for e in ENCL:
                if lw.endswith(e) and len(lw) > len(e) + 2:
                    x = lw[:-len(e)]
                    cands.append((FORMA.get(x) or simplemma.lemmatize(x, lang='la'), e))
        res = None
        for l, e in cands:
            k = busca_ls(l)
            if k: res = (LS[k]['key'], e); break
        if res is None: res = (cands[0][0], '')
    _lcache[w] = res
    return res

# ---------------------------------------------------------------- livros do AT
LIVROS = {}
for f in sorted(os.listdir(LIV)):
    if not f.endswith('.json'): continue
    d = json.load(open(os.path.join(LIV, f), encoding='utf-8'))
    if d.get('testamento') == 'nt' or d.get('livro') not in VULG_NOME: continue
    LIVROS[f] = d
print('livros do AT:', len(LIVROS))

def refs_de(r):
    out = []
    for x in r.split(';'):
        m = re.match(r'\s*(\d+):(\d+)(?:-(\d+))?\s*$', x)
        if m: out += [(int(m[1]), k) for k in range(int(m[2]), int(m[3] or m[2]) + 1)]
    return out
def refs_lxx(v, c, n):
    r = v.get('lxx_ref') or v.get('heb_ref')
    if r and r != '—' and refs_de(r): return refs_de(r)
    return [(c, n)]
def candidatos(b, c, n, v):
    """referências latinas possíveis; a primeira é a preferida"""
    out = []
    if b == 'Ps':
        out.append(tuple(refs_lxx(v, c, n)))
    t = TVL.get((b, c, n))
    if t:
        for col in t.values(): out.append(tuple(dict.fromkeys(col)))
    out.append(((c, n),))
    if v.get('heb_ref') and v['heb_ref'] != '—' and refs_de(v['heb_ref']): out.append(tuple(refs_de(v['heb_ref'])))
    return list(dict.fromkeys(out))
def palavras(b, refs):
    ws = []
    for r in refs:
        t = LAT[VULG_NOME[b]].get(r)
        if t: ws += t.split()
    return ws

# tokens hebraicos de cada linha: número Strong + prefixos (conjunção, preposição, artigo)
def toks_he(r):
    t = [r[2] or ('?' + r[0])]
    pref = ' '.join((r[4] or '').split(' + ')[:-1])
    for p, tag in (('conjunção', '+conj'), ('preposição', '+prep'), ('artigo', '+art')):
        if p in pref: t.append(tag)
    return t

# ---------------------------------------------------------------- Modelo 1 (IBM), nos dois sentidos
def modelo1(pares, iters=6):
    t = defaultdict(lambda: 1e-3)
    for _ in range(iters):
        cnt = defaultdict(float); tot = defaultdict(float)
        for src, tgt in pares:
            for w in tgt:
                z = sum(t[(w, s)] for s in src) or 1e-9
                for s in src:
                    p = t[(w, s)] / z; cnt[(w, s)] += p; tot[s] += p
        t = defaultdict(lambda: 1e-6, {k: v / tot[k[1]] for k, v in cnt.items()})
    return t

def montar_pares(escolha):
    pares = []
    for f, d in LIVROS.items():
        b = d['livro']
        for k, v in d['versiculos'].items():
            refs = escolha.get((f, k))
            if refs is None: continue
            lw = palavras(b, refs)
            if not lw: continue
            hs = [x for r in v['he'] for x in toks_he(r)] + ['NULL']
            ls = [lema(w)[0] for w in lw]
            pares.append((hs, ls))
    return pares

# 1ª passada: referência preferida; treina; 2ª: confere os candidatos pelo conteúdo
escolha = {}
for f, d in LIVROS.items():
    b = d['livro']
    for k, v in d['versiculos'].items():
        c, n = map(int, k.split(':'))
        cs = candidatos(b, c, n, v)
        escolha[(f, k)] = next((x for x in cs if palavras(b, x)), None)
print('treinando hebraico -> latim…')
P = montar_pares(escolha)
t_lh = modelo1(P)
t_hl = modelo1([(l + ['NULL'], h[:-1]) for h, l in P])

def pontua(hs, ls):
    if not ls: return -99
    return sum(math.log(max(t_lh[(l, h)] for h in hs)) for l in ls) / len(ls)

trocas = []
for f, d in LIVROS.items():
    b = d['livro']
    for k, v in d['versiculos'].items():
        c, n = map(int, k.split(':'))
        cs = [x for x in candidatos(b, c, n, v) if palavras(b, x)]
        if not cs: escolha[(f, k)] = None; continue
        hs = [x for r in v['he'] for x in toks_he(r)] + ['NULL']
        # vizinhos da preferida também entram (com desconto), para pegar deslocamentos que a tabela não cobre
        viz = []
        for (cc, nn) in cs[0][:1]:
            for dn in (-1, 1): viz.append(((cc, nn + dn),))
        viz = [x for x in viz if palavras(b, x) and x not in cs]
        sc = [(pontua(hs, [lema(w)[0] for w in palavras(b, x)]) + (0.4 if i == 0 else 0), x) for i, x in enumerate(cs)]
        sc += [(pontua(hs, [lema(w)[0] for w in palavras(b, x)]) - 1.2, x) for x in viz]
        sc.sort(key=lambda z: -z[0])
        if sc[0][1] != cs[0] and sc[0][0] < -2.0:     # correspondência fraca: fica a referência da tabela
            sc.insert(0, (None, cs[0]))
        if sc[0][1] != cs[0]: trocas.append((d['abrev'], k, cs[0], sc[0][1], round(sc[0][0], 2)))
        escolha[(f, k)] = sc[0][1]
print('trocas pelo conteúdo:', len(trocas))
for x in trocas[:60]: print('  ', x)
P = montar_pares(escolha)
t_lh = modelo1(P)
t_hl = modelo1([(l + ['NULL'], h[:-1]) for h, l in P])

# ---------------------------------------------------------------- alinhamento por linha
FUNC = {'et', 'in', 'ad', 'de', 'ex', 'e', 'a', 'ab', 'cum', 'qui', 'quae', 'quod', 'non', 'sum', 'is', 'ut', 'enim',
  'autem', 'vero', 'super', 'sed', 'per', 'pro', 'ne', 'nec', 'neque', 'que', 'quia', 'quoniam', 'ac', 'atque', 'sicut', 'hic', 'ille'}
def alinhar(he, lw):
    n, m = len(he), len(lw)
    hs = [toks_he(r) for r in he]
    ls = [lema(w)[0] for w in lw]
    lin = []
    for j, l in enumerate(ls):
        best = None
        for i in range(n):
            lex = max(t_lh[(l, h)] * t_hl[(h, l)] for h in hs[i])
            s = math.log(lex + 1e-12) - 4.0 * abs((i + 0.5) / n - (j + 0.5) / m)
            if best is None or s > best[0]: best = (s, i, lex)
        lin.append(best)
    por = [[] for _ in range(n)]
    for j, (s, i, lex) in enumerate(lin): por[i].append(j)
    princ = []
    for i in range(n):
        js = por[i]
        if not js: princ.append(-1); continue
        cont = [j for j in js if ls[j] not in FUNC] or js
        princ.append(max(cont, key=lambda j: lin[j][2]))
    return por, princ

# ---------------------------------------------------------------- saída
oc_at = Counter(); oc_liv = defaultdict(Counter)
for f, d in LIVROS.items():
    for k, v in d['versiculos'].items():
        refs = escolha.get((f, k))
        for w in (palavras(d['livro'], refs) if refs else []):
            l = lema(w)[0]; oc_at[l] += 1; oc_liv[f][l] += 1

STOP_PT = {'o', 'a', 'os', 'as', 'de', 'do', 'da', 'dos', 'das', 'e', 'que', 'em', 'no', 'na', 'nos', 'nas', 'um', 'uma',
  'para', 'por', 'com', 'se', 'ao', 'aos', 'à', 'às', 'pelo', 'pela', 'pelos', 'pelas', 'lhe', 'lhes', 'seu', 'sua', 'seus',
  'suas', 'meu', 'minha', 'teu', 'tua', 'eu', 'tu', 'ele', 'ela', 'eles', 'elas', 'me', 'te', 'nós', 'vós', 'não', 'é', 'ser',
  'nosso', 'nossa', 'vosso', 'vossa', 'desde', 'como', 'haver', 'ter', 'estar', 'então', 'este', 'esta', 'esse', 'essa', 'aquele',
  'aquela', 'isto', 'isso', 'aquilo', 'mas', 'porque', 'quando', 'onde', 'mais', 'já', 'também', 'assim', 'eis', 'pois', 'qual',
  'quem', 'nem', 'ou', 'sobre', 'até', 'entre', 'contra', 'sem', 'diante', 'dele', 'dela', 'deles', 'delas', 'nele', 'nela', 'si',
  'lo', 'la', 'los', 'las', 'vos', 'nos', 'mim', 'ti', 'todo', 'toda', 'todos', 'todas', 'muito', 'fazer'}
pt_de = defaultdict(Counter)

def lema_pt(w):
    w = w.lower().strip('.,;:!?“”"\'()')
    return simplemma.lemmatize(w, lang='pt') if w else ''

saida = {}
for f, d in LIVROS.items():
    b = d['livro']; usados = set()
    for k, v in d['versiculos'].items():
        refs = escolha.get((f, k))
        lw = palavras(b, refs) if refs else []
        c, n = map(int, k.split(':'))
        v['la'] = [[w, lema(w)[0], lema(w)[1], oc_liv[f][lema(w)[0]], oc_at[lema(w)[0]]] for w in lw]
        lr = '; '.join(f'{a}:{bb}' for a, bb in refs) if refs else None
        if lr and lr != f'{c}:{n}': v['la_ref'] = lr
        else: v.pop('la_ref', None)
        por, princ = alinhar(v['he'], lw) if lw and v['he'] else ([[] for _ in v['he']], [-1] * len(v['he']))
        for i, r in enumerate(v['he']):
            del r[10:]
            r += [por[i], princ[i]]
            if princ[i] >= 0:
                l = v['la'][princ[i]][1]
                for p in (r[8] or '').split():
                    lp = lema_pt(p)
                    if lp and lp not in STOP_PT: pt_de[l][lp] += 1
        usados.update(x[1] for x in v['la'])
    saida[f] = (d, usados)

def trad_bl(l):
    c = pt_de.get(l)
    if not c: return []
    tot = sum(c.values())
    return [w for w, n in c.most_common(8) if n >= 2 and n / tot >= 0.07][:5]

sem_ls = Counter()
for f, (d, usados) in saida.items():
    lex = {}
    for l in sorted(usados):
        e = None if l.startswith(PROPRIO) else LS.get(chave(l))
        if not e and not l.startswith(PROPRIO): sem_ls[l] += oc_liv[f][l]
        if l.startswith(PROPRIO):
            lex[l] = [l[1:], '', 'nome próprio', '', [], trad_bl(l)]
        else:
            lex[l] = [e['orth'] if e else l, e['itype'] if e else '', ' '.join(x for x in (e['pos'], e['gen']) if x) if e else '',
                      e['en'] if e else '', PT.get(chave(l), []), trad_bl(l)]
    d['lex_la'] = lex
    d['colunas_he'] = d['colunas_he'][:10] + ['latim_indices', 'latim_principal']
    d['lex_la_campos'] = ['lema (Lewis & Short)', 'formas', 'classe', 'definição em inglês', 'significados em português', 'traduções na Bíblia Livre']
    json.dump(d, open(os.path.join(LIV, f), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('ok', f, os.path.getsize(os.path.join(LIV, f)) // 1024, 'KB', sum(1 for v in d['versiculos'].values() if not v['la']), 'sem latim')

# lista para tradução: lemas do Lewis & Short usados no AT, por frequência
with open(os.path.join(SRC, 'lat_para_traduzir.tsv'), 'w', encoding='utf-8') as fo:
    vistos = set()
    for l, n in oc_at.most_common():
        k = chave(l); e = LS.get(k)
        if l.startswith(PROPRIO) or not e or k in vistos or k in PT: continue
        vistos.add(k)
        fo.write(f"{k}\t{e['orth']}\t{e['pos']} {e['gen']}\t{e['en']}\t{n}\n")
tot = sum(oc_at.values())
print('ocorrências sem verbete no Lewis & Short:', sum(sem_ls.values()), 'de', tot, '| exemplos:', sem_ls.most_common(25))

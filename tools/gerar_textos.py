#!/usr/bin/env python3
"""Gera data/texto/<livro>.json (só o texto da Bíblia Livre, para a Concordância) a partir de data/livros/<livro>.json.
Uso: python3 tools/gerar_textos.py data/livros data/texto"""
import json, os, sys
ent, sai = sys.argv[1], sys.argv[2]
os.makedirs(sai, exist_ok=True)
for f in sorted(os.listdir(ent)):
    if not f.endswith('.json'): continue
    d = json.load(open(os.path.join(ent, f), encoding='utf-8'))
    out = {'livro': d.get('abrev'), 'capitulos': d['capitulos'], 'v': {k: v['pt'] for k, v in d['versiculos'].items()}}
    json.dump(out, open(os.path.join(sai, f), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f, os.path.getsize(os.path.join(sai, f)) // 1024, 'KB')

// Livros do Antigo Testamento na ordem e divisão da Bíblia Hebraica (Tanakh).
// "ativo": livros já disponíveis para exegese nesta etapa.
window.CANON = [
  {
    id: 'tora', testamento: 'at', nome: 'Torá', hebraico: 'תּוֹרָה', subtitulo: 'A Lei · Pentateuco', cor: 'tora',
    grupos: [{ cor: 'tora', livros: [
      { abrev: 'Gn', nome: 'Gênesis', heb: 'בְּרֵאשִׁית', arquivo: 'gn', ativo: true },
      { abrev: 'Êx', nome: 'Êxodo', heb: 'שְׁמוֹת', arquivo: 'ex', ativo: true },
      { abrev: 'Lv', nome: 'Levítico', heb: 'וַיִּקְרָא', arquivo: 'lv', ativo: true },
      { abrev: 'Nm', nome: 'Números', heb: 'בְּמִדְבַּר', arquivo: 'nm', ativo: true },
      { abrev: 'Dt', nome: 'Deuteronômio', heb: 'דְּבָרִים', arquivo: 'dt', ativo: true }
    ]}]
  },
  {
    id: 'neviim', testamento: 'at', nome: 'Nevi’im', hebraico: 'נְבִיאִים', subtitulo: 'Os Profetas', cor: 'neviim',
    grupos: [
      { titulo: 'Profetas Anteriores', cor: 'anteriores', livros: [
        { abrev: 'Js', nome: 'Josué', heb: 'יְהוֹשֻׁעַ', arquivo: 'js', ativo: true },
        { abrev: 'Jz', nome: 'Juízes', heb: 'שׁוֹפְטִים', arquivo: 'jz', ativo: true },
        { abrev: '1Sm', nome: '1 Samuel', heb: 'שְׁמוּאֵל א', arquivo: '1sm', ativo: true },
        { abrev: '2Sm', nome: '2 Samuel', heb: 'שְׁמוּאֵל ב', arquivo: '2sm', ativo: true },
        { abrev: '1Rs', nome: '1 Reis', heb: 'מְלָכִים א', arquivo: '1rs', ativo: true },
        { abrev: '2Rs', nome: '2 Reis', heb: 'מְלָכִים ב', arquivo: '2rs', ativo: true }
      ]},
      { titulo: 'Profetas Posteriores', cor: 'posteriores', livros: [
        { abrev: 'Is', nome: 'Isaías', heb: 'יְשַׁעְיָהוּ', arquivo: 'is', ativo: true },
        { abrev: 'Jr', nome: 'Jeremias', heb: 'יִרְמְיָהוּ', arquivo: 'jr', ativo: true },
        { abrev: 'Ez', nome: 'Ezequiel', heb: 'יְחֶזְקֵאל', arquivo: 'ez', ativo: true }
      ]},
      { titulo: 'Os Doze', cor: 'doze', livros: [
        { abrev: 'Os', nome: 'Oseias', heb: 'הוֹשֵׁעַ', arquivo: 'os', ativo: true },
        { abrev: 'Jl', nome: 'Joel', heb: 'יוֹאֵל', arquivo: 'jl', ativo: true },
        { abrev: 'Am', nome: 'Amós', heb: 'עָמוֹס', arquivo: 'am', ativo: true },
        { abrev: 'Ob', nome: 'Obadias', heb: 'עֹבַדְיָה', arquivo: 'ob', ativo: true },
        { abrev: 'Jn', nome: 'Jonas', heb: 'יוֹנָה', arquivo: 'jn', ativo: true },
        { abrev: 'Mq', nome: 'Miqueias', heb: 'מִיכָה', arquivo: 'mq', ativo: true },
        { abrev: 'Na', nome: 'Naum', heb: 'נַחוּם', arquivo: 'na', ativo: true },
        { abrev: 'Hc', nome: 'Habacuque', heb: 'חֲבַקּוּק', arquivo: 'hc', ativo: true },
        { abrev: 'Sf', nome: 'Sofonias', heb: 'צְפַנְיָה', arquivo: 'sf', ativo: true },
        { abrev: 'Ag', nome: 'Ageu', heb: 'חַגַּי', arquivo: 'ag', ativo: true },
        { abrev: 'Zc', nome: 'Zacarias', heb: 'זְכַרְיָה', arquivo: 'zc', ativo: true },
        { abrev: 'Ml', nome: 'Malaquias', heb: 'מַלְאָכִי', arquivo: 'ml', ativo: true }
      ]}
    ]
  },
  {
    id: 'ketuvim', testamento: 'at', nome: 'Ketuvim', hebraico: 'כְּתוּבִים', subtitulo: 'Os Escritos', cor: 'ketuvim',
    grupos: [
      { titulo: 'Livros poéticos', cor: 'poeticos', livros: [
        { abrev: 'Sl', nome: 'Salmos', heb: 'תְּהִלִּים' },
        { abrev: 'Pv', nome: 'Provérbios', heb: 'מִשְׁלֵי' },
        { abrev: 'Jó', nome: 'Jó', heb: 'אִיּוֹב' }
      ]},
      { titulo: 'Cinco Rolos (Megillot)', cor: 'megillot', livros: [
        { abrev: 'Ct', nome: 'Cântico dos Cânticos', heb: 'שִׁיר הַשִּׁירִים' },
        { abrev: 'Rt', nome: 'Rute', heb: 'רוּת' },
        { abrev: 'Lm', nome: 'Lamentações', heb: 'אֵיכָה' },
        { abrev: 'Ec', nome: 'Eclesiastes', heb: 'קֹהֶלֶת' },
        { abrev: 'Et', nome: 'Ester', heb: 'אֶסְתֵּר' }
      ]},
      { titulo: 'Demais Escritos', cor: 'escritos', livros: [
        { abrev: 'Dn', nome: 'Daniel', heb: 'דָּנִיֵּאל' },
        { abrev: 'Ed', nome: 'Esdras', heb: 'עֶזְרָא' },
        { abrev: 'Ne', nome: 'Neemias', heb: 'נְחֶמְיָה' },
        { abrev: '1Cr', nome: '1 Crônicas', heb: 'דִּבְרֵי הַיָּמִים א' },
        { abrev: '2Cr', nome: '2 Crônicas', heb: 'דִּבְרֵי הַיָּמִים ב' }
      ]}
    ]
  }
];

// Ordem das Bíblias protestantes (de Gênesis a Malaquias), usada na Concordância.
window.ORDEM_AT = ['Gn','Êx','Lv','Nm','Dt','Js','Jz','Rt','1Sm','2Sm','1Rs','2Rs','1Cr','2Cr','Ed','Ne','Et','Jó','Sl','Pv','Ec','Ct',
  'Is','Jr','Lm','Ez','Dn','Os','Jl','Am','Ob','Jn','Mq','Na','Hc','Sf','Ag','Zc','Ml'];

// Novo Testamento, na ordem das Bíblias tradicionais (textos ainda não incluídos).
window.CANON.push(
  {
    id: 'historicos-nt', testamento: 'nt', nome: 'Evangelhos e Atos', hebraico: 'Εὐαγγέλια', lang: 'grc', subtitulo: 'Livros históricos', cor: 'evangelhos',
    grupos: [
      { titulo: 'Evangelhos', cor: 'evangelhos', livros: [
        { abrev: 'Mt', nome: 'Mateus', heb: 'Κατὰ Μαθθαῖον' },
        { abrev: 'Mc', nome: 'Marcos', heb: 'Κατὰ Μᾶρκον' },
        { abrev: 'Lc', nome: 'Lucas', heb: 'Κατὰ Λουκᾶν' },
        { abrev: 'Jo', nome: 'João', heb: 'Κατὰ Ἰωάννην' }
      ]},
      { titulo: 'Histórico', cor: 'atos', livros: [
        { abrev: 'At', nome: 'Atos', heb: 'Πράξεις Ἀποστόλων' }
      ]}
    ]
  },
  {
    id: 'cartas', testamento: 'nt', nome: 'Cartas', hebraico: 'Ἐπιστολαί', lang: 'grc', subtitulo: 'Epístolas paulinas e gerais', cor: 'paulo',
    grupos: [
      { titulo: 'Cartas de Paulo', cor: 'paulo', livros: [
        { abrev: 'Rm', nome: 'Romanos', heb: 'Πρὸς Ῥωμαίους' },
        { abrev: '1Co', nome: '1 Coríntios', heb: 'Πρὸς Κορινθίους Α' },
        { abrev: '2Co', nome: '2 Coríntios', heb: 'Πρὸς Κορινθίους Β' },
        { abrev: 'Gl', nome: 'Gálatas', heb: 'Πρὸς Γαλάτας' },
        { abrev: 'Ef', nome: 'Efésios', heb: 'Πρὸς Ἐφεσίους' },
        { abrev: 'Fp', nome: 'Filipenses', heb: 'Πρὸς Φιλιππησίους' },
        { abrev: 'Cl', nome: 'Colossenses', heb: 'Πρὸς Κολοσσαεῖς' },
        { abrev: '1Ts', nome: '1 Tessalonicenses', heb: 'Πρὸς Θεσσαλονικεῖς Α' },
        { abrev: '2Ts', nome: '2 Tessalonicenses', heb: 'Πρὸς Θεσσαλονικεῖς Β' },
        { abrev: '1Tm', nome: '1 Timóteo', heb: 'Πρὸς Τιμόθεον Α' },
        { abrev: '2Tm', nome: '2 Timóteo', heb: 'Πρὸς Τιμόθεον Β' },
        { abrev: 'Tt', nome: 'Tito', heb: 'Πρὸς Τίτον' },
        { abrev: 'Fm', nome: 'Filemom', heb: 'Πρὸς Φιλήμονα' }
      ]},
      { titulo: 'Cartas gerais', cor: 'gerais', livros: [
        { abrev: 'Hb', nome: 'Hebreus', heb: 'Πρὸς Ἑβραίους' },
        { abrev: 'Tg', nome: 'Tiago', heb: 'Ἰακώβου' },
        { abrev: '1Pe', nome: '1 Pedro', heb: 'Πέτρου Α' },
        { abrev: '2Pe', nome: '2 Pedro', heb: 'Πέτρου Β' },
        { abrev: '1Jo', nome: '1 João', heb: 'Ἰωάννου Α' },
        { abrev: '2Jo', nome: '2 João', heb: 'Ἰωάννου Β' },
        { abrev: '3Jo', nome: '3 João', heb: 'Ἰωάννου Γ' },
        { abrev: 'Jd', nome: 'Judas', heb: 'Ἰούδα' }
      ]}
    ]
  },
  {
    id: 'profetico-nt', testamento: 'nt', nome: 'Profético', hebraico: 'Ἀποκάλυψις', lang: 'grc', subtitulo: 'Revelação de Jesus Cristo', cor: 'apocalipse',
    grupos: [{ cor: 'apocalipse', livros: [
      { abrev: 'Ap', nome: 'Apocalipse', heb: 'Ἀποκάλυψις Ἰωάννου' }
    ]}]
  }
);
window.ORDEM_NT = ['Mt','Mc','Lc','Jo','At','Rm','1Co','2Co','Gl','Ef','Fp','Cl','1Ts','2Ts','1Tm','2Tm','Tt','Fm','Hb','Tg','1Pe','2Pe','1Jo','2Jo','3Jo','Jd','Ap'];

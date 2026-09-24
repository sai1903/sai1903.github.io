"""Build the services catalogue page.

Tool chips come in two flavours:
  "slug"            -> a real brand mark from simple-icons
  ("Label", "#hex") -> a monogram tile, for brands simple-icons does not carry
                       (Microsoft family, Workday, IBM, SAS ... are excluded
                       there on trademark grounds)

Run from the project root:  python build/make-services.py
"""
import json, os, re, sys, urllib.request, html

sys.path.insert(0, 'build')
from slugs import load as load_index

INDEX = load_index()
CDN = 'https://cdn.jsdelivr.net/npm/simple-icons@13/icons/%s.svg'

# --------------------------------------------------------------------------
# monogram fallbacks: label -> (short text, brand colour)
# --------------------------------------------------------------------------
MONO = {
    'Power BI': ('BI', '#F2C811'), 'Excel': ('XL', '#217346'),
    'Azure': ('AZ', '#0078D4'), 'MS Teams': ('T', '#6264A7'),
    'Outlook': ('OL', '#0078D4'), 'SharePoint': ('SP', '#038387'),
    'Dynamics 365': ('D365', '#002050'), 'MS Project': ('PR', '#31752F'),
    'SQL Server': ('SQL', '#CC2927'), 'SSIS': ('SS', '#CC2927'),
    'Workday': ('WD', '#F38B00'), 'BambooHR': ('BH', '#73C41D'),
    'Darwinbox': ('DB', '#FF5A5F'), 'Keka': ('KK', '#FF5C35'),
    'greytHR': ('GH', '#E4002B'), 'Naukri': ('NK', '#4A90E2'),
    'Lever': ('LV', '#0F6DFF'), 'Rippling': ('RP', '#1F2937'),
    'IBM Quantum': ('IBM', '#1F70C1'), 'Cirq': ('CQ', '#4285F4'),
    'PennyLane': ('PL', '#01B6D6'), 'D-Wave': ('DW', '#0D3B66'),
    'Azure Quantum': ('AQ', '#0078D4'), 'Braket': ('BK', '#FF9900'),
    'SAS': ('SAS', '#0766D1'), 'SPSS': ('SP', '#052FAD'),
    'Ahrefs': ('AH', '#FF8800'), 'Moz': ('MZ', '#0DAFEC'),
    'Klaviyo': ('KL', '#232426'), 'Amplitude': ('AM', '#1F8EFA'),
    'NetSuite': ('NS', '#0070D2'), 'Tally': ('TL', '#1B69B6'),
    'Anaplan': ('AP', '#1B1B1B'), 'BlackLine': ('BL', '#0B0B45'),
    'Concur': ('CN', '#0FAAFF'), 'Coupa': ('CP', '#0468B1'),
    'Workiva': ('WK', '#4A56E2'), 'Bloomberg': ('BB', '#000000'),
    'erwin': ('ER', '#005CB9'), 'PowerDesigner': ('PD', '#1D6FB8'),
    'Teradata': ('TD', '#F37440'), 'Collibra': ('CO', '#3C2A87'),
    'Alation': ('AL', '#1F3A93'), 'Apache Atlas': ('AT', '#D22128'),
    'LlamaIndex': ('LI', '#3B82F6'), 'Pinecone': ('PC', '#0B7285'),
    'LangGraph': ('LG', '#1C3C3C'), 'CrewAI': ('CA', '#FF5A1F'),
    'AutoGen': ('AG', '#2F6FED'), 'MCP': ('MCP', '#C0452A'),
    'Weights & Biases': ('WB', '#FFBE00'), 'XGBoost': ('XG', '#337AB7'),
    'Pipedrive': ('PD', '#017737'), 'monday.com': ('MD', '#FF3D57'),
    'Playwright': ('PW', '#2EAD33'), 'JMeter': ('JM', '#D22128'),
    'BrowserStack': ('BS', '#FF6B00'), 'Burp Suite': ('BP', '#FF6633'),
    'Nessus': ('NS', '#00A4E4'), 'Kinaxis': ('KX', '#0B7DBD'),
    'Blue Yonder': ('BY', '#0033A0'), 'Adobe XD': ('XD', '#FF61F6'),
    'Apache Iceberg': ('IC', '#1B7FCB'), 'Gradio': ('GR', '#FF7C00'),
    'Mistral AI': ('MS', '#FA520F'), 'Qdrant': ('QD', '#DC244C'),
}


import colorsys

def _lum(hx):
    r, g, b = (int(hx[i:i+2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)

def _shift(hx, light):
    """Push a brand colour to a lightness that reads on the given background."""
    r, g, b = (int(hx[i:i+2], 16) / 255 for i in (1, 3, 5))
    h, l, sat = colorsys.rgb_to_hls(r, g, b)
    l = light
    if sat < .12:                      # greyscale marks get a warm neutral
        sat = .06
    r, g, b = colorsys.hls_to_rgb(h, l, sat)
    return '#%02x%02x%02x' % (round(r * 255), round(g * 255), round(b * 255))

def safe(hx):
    """(light-mode colour, dark-mode colour) for a brand hex."""
    L = _lum(hx)
    lightbg = _shift(hx, .42) if L > .62 else hx   # too pale on cream
    darkbg  = _shift(hx, .78) if L < .16 else hx   # too dark on charcoal
    return lightbg, darkbg

def tool(x):
    """Normalise an entry into (kind, label, colour, slug_or_text)."""
    if isinstance(x, tuple):
        label, slug = x
    else:
        label, slug = None, x
    if slug in INDEX:
        meta = INDEX[slug]
        return ('logo', label or meta['title'], meta['hex'], slug)
    name = label or slug
    if name in MONO:
        text, hexc = MONO[name]
        return ('mono', name, hexc, text)
    return ('mono', name, '#6c7077', re.sub(r'[^A-Za-z]', '', name)[:2].upper())

# --------------------------------------------------------------------------
# catalogue data
# --------------------------------------------------------------------------
TECH = [
 ('Full-Stack Development', 'code', 'brand',
  'Browser to database to pipeline, built as one system rather than three courses stapled together.',
  ['html5','css3','javascript','typescript','react','angular','vuedotjs','nextdotjs','nodedotjs',
   'express','django','flask','spring','dotnet','php','laravel','python','go','mysql','postgresql',
   'redis','graphql','tailwindcss','git','github','docker','postman','jira','figma']),

 ('MERN Stack', 'layers', 'pine',
  'MongoDB, Express, React and Node taught as a working product, including auth, state and deployment.',
  ['mongodb','express','react','nodedotjs','redux','socketdotio','javascript','typescript',
   'tailwindcss','vite','npm','jsonwebtokens','vercel','netlify','postman','github']),

 ('Data Analysis', 'chart', 'indigo',
  'SQL that survives review, then BI and Python for the questions a dashboard cannot answer.',
  ['mysql','postgresql','googlesheets',('Excel','excel'),('Power BI','powerbi'),'tableau','looker',
   'qlik','metabase','apachesuperset','python','pandas','numpy','plotly','r',('SAS','sas'),
   ('SPSS','spss'),'alteryx']),

 ('Data Engineering', 'pipe', 'ocean',
  'Batch and streaming pipelines, the lakehouse pattern, orchestration and the tests that keep them honest.',
  ['apachespark','apachekafka','apacheairflow','dbt','snowflake','databricks',('Apache Iceberg','apacheiceberg'),
   'apachehadoop','apachehive','apacheflink','apachenifi','informatica','talend','amazonwebservices',
   ('Azure','azure'),'googlecloud','postgresql','elasticsearch','apachecassandra','redis']),

 ('Data Science & ML', 'flask', 'plum',
  'From feature engineering to a model someone will actually deploy — and an evaluation you can defend.',
  ['python','jupyter','anaconda','scikitlearn','tensorflow','pytorch','keras','pandas','numpy',
   'scipy','plotly','opencv','huggingface','mlflow','weightsandbiases',
   ('XGBoost','xgboost'),'streamlit',('Gradio','gradio')]),

 ('Data Modelling', 'cube', 'gold',
  'Dimensional and normalised modelling, slowly changing dimensions, and semantic layers people self-serve from.',
  [('erwin','erwin'),('PowerDesigner','powerdesigner'),'dbt','snowflake','databricks','oracle',
   'postgresql',('SQL Server','sqlserver'),('Teradata','teradata'),'lucid','miro']),

 ('Data Architecture', 'blueprint', 'brand',
  'Platform decisions and their bill: storage layout, governance, lineage, cost attribution, migration paths.',
  ['amazonwebservices',('Azure','azure'),'googlecloud','snowflake','databricks','terraform',
   'kubernetes','apachekafka','dbt',('Collibra','collibra'),('Alation','alation'),
   ('Apache Atlas','apacheatlas'),'informatica']),

 ('AI — foundations to AGI/ASI', 'brain', 'plum',
  'How models behave: training basics, prompting, retrieval, alignment, and where the research frontier actually is.',
  ['openai','claude','huggingface','tensorflow','pytorch','langchain',
   ('LlamaIndex','llamaindex'),'ollama',('Mistral AI','mistralai'),'googlegemini','python','jupyter']),

 ('Agentic AI', 'agent', 'ocean',
  'Agents that do real work: tool use, planning loops, memory, orchestration and production guardrails.',
  ['claude','openai','langchain',('LangGraph','langgraph'),('CrewAI','crewai'),
   ('AutoGen','autogen'),('MCP','mcp'),'n8n','ollama',('Pinecone','pinecone'),('Qdrant','qdrant'),'zapier']),

 ('Quantum Computing', 'atom', 'indigo',
  'Circuits, algorithms and the honest classical baseline — the part most quantum courses skip.',
  ['qiskit',('IBM Quantum','ibmquantum'),('Cirq','cirq'),('PennyLane','pennylane'),
   ('D-Wave','dwave'),('Azure Quantum','azurequantum'),('Braket','braket'),'python','jupyter']),

 ('Cloud Computing', 'cloud', 'pine',
  'Core services, identity and networking, then infrastructure as code so environments stop drifting.',
  ['amazonwebservices',('Azure','azure'),'googlecloud','terraform','kubernetes','docker','linux',
   'ansible','prometheus','grafana','cloudflare','nginx','jenkins','githubactions']),

 ('DevOps & Platform', 'infinity', 'gold',
  'CI/CD, observability and the operational habits that keep a platform boring in the best way.',
  ['docker','kubernetes','jenkins','githubactions','gitlab','terraform','ansible','prometheus',
   'grafana','sonarqube','argo','helm','linux','git']),
]

DOMAIN = [
 ('Finance', 'coins', 'gold',
  'Accounting and FP&A on the systems finance teams actually run, plus the reporting an auditor will read.',
  ['GL &amp; sub-ledgers','AP / AR cycles','FP&amp;A and budgeting','Reconciliation','Taxation &amp; GST',
   'IFRS / GAAP basics','Audit trails','Treasury basics'],
  ['sap','oracle',('NetSuite','netsuite'),'quickbooks','xero','zoho',('Tally','tally'),'odoo','sage',
   ('Excel','excel'),('Power BI','powerbi'),'stripe','razorpay',('Anaplan','anaplan'),
   ('BlackLine','blackline'),('Concur','concur'),('Coupa','coupa'),('Workiva','workiva'),
   ('Bloomberg','bloomberg')]),

 ('Human Resources & HCM', 'people', 'brand',
  'The full employee lifecycle on real HR systems — the same ground Commbricks People covers in product form.',
  ['Core HR &amp; records','Talent acquisition','Onboarding / offboarding','Payroll operations',
   'Performance &amp; reviews','Learning &amp; development','Comp &amp; benefits','HR analytics'],
  [('Workday','workday'),'sap','oracle',('BambooHR','bamboohr'),'zoho',('Darwinbox','darwinbox'),
   ('Keka','keka'),('greytHR','greythr'),'greenhouse',('Lever','lever'),'linkedin',('Naukri','naukri'),
   'adp','gusto',('Rippling','rippling'),'slack',('MS Teams','msteams'),('Excel','excel'),
   ('Power BI','powerbi')]),

 ('Marketing', 'megaphone', 'plum',
  'The measurable half of marketing: search, campaigns, analytics and attribution that survives finance review.',
  ['SEO &amp; content','Paid search &amp; social','Marketing automation','Email &amp; lifecycle',
   'Web analytics','Attribution modelling','CRO &amp; experimentation','Brand &amp; creative ops'],
  ['googleanalytics','googleads','googletagmanager','meta','instagram','linkedin','hubspot','mailchimp',
   'salesforce','semrush',('Ahrefs','ahrefs'),('Moz','moz'),'canva','figma','wordpress','shopify',
   'hootsuite','buffer',('Klaviyo','klaviyo'),'marketo','matomo','mixpanel','hotjar','sendgrid',
   'webflow','wix']),

 ('Sales & CRM', 'handshake', 'ocean',
  'Pipeline hygiene, forecasting and the CRM configuration that makes both possible.',
  ['Pipeline &amp; stages','Forecasting','Lead scoring','Territory design','Sales analytics'],
  ['salesforce','hubspot','zoho',('Pipedrive','pipedrive'),('Dynamics 365','dynamics365'),'linkedin',
   'zendesk','intercom',('Excel','excel'),('Power BI','powerbi')]),

 ('Operations & Supply Chain', 'truck', 'pine',
  'Planning, procurement and inventory on ERP, with the analytics layer that makes them visible.',
  ['Demand planning','Procurement','Inventory &amp; WMS','S&amp;OP cycles','Ops analytics'],
  ['sap','oracle','odoo',('Kinaxis','kinaxis'),('Blue Yonder','blueyonder'),('Excel','excel'),
   ('Power BI','powerbi'),('Anaplan','anaplan')]),

 ('Project & Delivery Management', 'kanban', 'indigo',
  'Agile and traditional delivery, estimation, and reporting that tells the truth about status.',
  ['Agile &amp; Scrum','Kanban &amp; flow','Estimation','Risk &amp; RAID','Stakeholder reporting'],
  ['jira','confluence','asana','trello','notion','clickup',('monday.com','mondaycom'),
   ('MS Project','msproject'),'slack','miro']),

 ('Design & Product', 'pen', 'gold',
  'Product thinking, research and interface craft — enough to brief and judge design work properly.',
  ['Discovery &amp; research','Wireframing','Design systems','Prototyping','Usability testing'],
  ['figma','canva','adobe',('Adobe XD','adobexd'),'sketch','framer','miro','notion']),

 ('QA & Test Engineering', 'bug', 'brand',
  'Test strategy, automation and the discipline of making failures reproducible.',
  ['Test strategy','UI automation','API testing','Performance testing','CI integration'],
  ['selenium','cypress',('Playwright','playwright'),'jest','postman',('JMeter','jmeter'),'appium',
   'sonarqube',('BrowserStack','browserstack'),'github']),

 ('Cybersecurity', 'shield', 'ocean',
  'Defensive fundamentals: threat modelling, secure SDLC, monitoring and incident response basics.',
  ['Threat modelling','Secure SDLC','Network basics','SIEM &amp; monitoring','Incident response'],
  ['kalilinux','wireshark',('Burp Suite','burpsuite'),'splunk',('Nessus','nessus'),'owasp','okta',
   'linux']),
]

# --------------------------------------------------------------------------
# fetch the icons we actually reference
# --------------------------------------------------------------------------
needed, missing = set(), set()
for _, _, _, _, tools in TECH:
    for t in tools:
        k, lbl, col, val = tool(t)
        (needed if k == 'logo' else missing).add(val if k == 'logo' else lbl)
for _, _, _, _, _, tools in DOMAIN:
    for t in tools:
        k, lbl, col, val = tool(t)
        (needed if k == 'logo' else missing).add(val if k == 'logo' else lbl)

os.makedirs('assets/logos', exist_ok=True)
syms = []
for slug in sorted(needed):
    path = f'assets/logos/{slug}.svg'
    if not os.path.exists(path):
        try:
            with urllib.request.urlopen(CDN % slug, timeout=25) as r:
                open(path, 'wb').write(r.read())
        except Exception as e:
            print('  FETCH FAIL', slug, e); continue
    s = open(path, encoding='utf-8').read()
    d = re.search(r'<path[^>]*\sd="([^"]+)"', s)
    vb = re.search(r'viewBox="([^"]+)"', s)
    if d:
        syms.append(f'<symbol id="li-{slug}" viewBox="{vb.group(1) if vb else "0 0 24 24"}">'
                    f'<path d="{d.group(1)}"/></symbol>')

sprite = ('<svg class="logo-sprite" aria-hidden="true" focusable="false" '
          'style="position:absolute;width:0;height:0;overflow:hidden">' + ''.join(syms) + '</svg>')
open('build/services-sprite.html', 'w', encoding='utf-8').write(sprite)
open('assets/logos/services-sprite.svg', 'w', encoding='utf-8').write(
    '<svg xmlns="http://www.w3.org/2000/svg">' + ''.join(syms) + '</svg>')

print(f'logos: {len(syms)} | monogram tiles: {len(missing)} | sprite: {len(sprite)/1024:.0f} KB')
print('monograms used:', ', '.join(sorted(missing)))

# --------------------------------------------------------------------------
# section glyphs (stroke icons, matching the rest of the site)
# --------------------------------------------------------------------------
S = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
     'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>')

GLYPH = {
 'code':      S % '<path d="M8.5 17L3.5 12l5-5M15.5 7l5 5-5 5M13.5 4l-3 16"/>',
 'layers':    S % '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 13l9 5 9-5M3 17.5l9 5 9-5"/>',
 'chart':     S % '<path d="M4 19V9M10 19V4M16 19v-7M22 19H2"/>',
 'pipe':      S % '<path d="M2.5 7h5.5a3.5 3.5 0 013.5 3.5v3A3.5 3.5 0 0015 17h6.5"/><circle cx="2.6" cy="7" r="1.6" fill="currentColor" stroke="none"/><circle cx="21.4" cy="17" r="1.6" fill="currentColor" stroke="none"/>',
 'flask':     S % '<path d="M9.5 3v6.2L4.4 18a2 2 0 001.7 3h11.8a2 2 0 001.7-3l-5.1-8.8V3M8 3h8M7.4 14h9.2"/>',
 'cube':      S % '<path d="M12 2.5l8.5 4.8v9.4L12 21.5l-8.5-4.8V7.3L12 2.5z"/><path d="M3.5 7.3L12 12l8.5-4.7M12 12v9.5"/>',
 'blueprint': S % '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M9 9v11M13 13h8M13 17h5"/>',
 'brain':     S % '<path d="M9.5 3.5a3 3 0 00-3 3 3 3 0 00-2 5.2A3 3 0 006 17a3 3 0 003.5 3V3.5zM14.5 3.5a3 3 0 013 3 3 3 0 012 5.2A3 3 0 0118 17a3 3 0 01-3.5 3V3.5z"/>',
 'agent':     S % '<rect x="4" y="8.5" width="16" height="11.5" rx="3.2"/><path d="M12 8.5V5.6"/><circle cx="12" cy="4.2" r="1.4"/><path d="M9.2 13.4h.01M14.8 13.4h.01M9.8 16.8h4.4"/>',
 'atom':      S % '<circle cx="12" cy="12" r="1.9" fill="currentColor" stroke="none"/><ellipse cx="12" cy="12" rx="10" ry="4.4"/><ellipse cx="12" cy="12" rx="10" ry="4.4" transform="rotate(60 12 12)"/><ellipse cx="12" cy="12" rx="10" ry="4.4" transform="rotate(120 12 12)"/>',
 'cloud':     S % '<path d="M7 18h10.5a3.5 3.5 0 000-7 5.5 5.5 0 00-10.6-1.4A4 4 0 007 18z"/>',
 'infinity':  S % '<path d="M7.5 9a3 3 0 100 6c2.5 0 4-6 9-6a3 3 0 110 6c-5 0-6.5-6-9-6z"/>',
 'coins':     S % '<ellipse cx="12" cy="6.5" rx="7.5" ry="3"/><path d="M4.5 6.5v5c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3v-5"/><path d="M4.5 11.5v5c0 1.7 3.4 3 7.5 3s7.5-1.3 7.5-3v-5"/>',
 'people':    S % '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c0-3.3 2.7-5.5 6-5.5s6 2.2 6 5.5"/><path d="M16 4.6a3.2 3.2 0 010 6.8M18 14.9c2 .8 3 2.5 3 5.1"/>',
 'megaphone': S % '<path d="M3.5 10.5v3a1.5 1.5 0 001.5 1.5h2l7 4.5V4.5l-7 4.5H5a1.5 1.5 0 00-1.5 1.5z"/><path d="M17.5 9.5a4 4 0 010 5M20 7a7.5 7.5 0 010 10"/>',
 'handshake': S % '<path d="M8 12.5l2.5 2.5 2-2 2.5 2.5"/><path d="M2.5 9.5L6 6h4l2 2 2-2h4l3.5 3.5"/><path d="M2.5 9.5V15l4 3.5M21.5 9.5V15l-4 3.5"/>',
 'truck':     S % '<path d="M2.5 6.5h11v10h-11z"/><path d="M13.5 10h3.8l3.2 3v3.5h-7"/><circle cx="6.5" cy="18.5" r="1.9"/><circle cx="17" cy="18.5" r="1.9"/>',
 'kanban':    S % '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M8.5 8v8M15.5 8v5"/>',
 'pen':       S % '<path d="M4 20l4.5-1 10-10a2.5 2.5 0 10-3.5-3.5l-10 10L4 20z"/><path d="M13.5 7l3.5 3.5"/>',
 'bug':       S % '<rect x="7.5" y="7.5" width="9" height="12" rx="4.5"/><path d="M9.5 5.5l1.5 2M14.5 5.5L13 7.5M3.5 11h4M16.5 11h4M3.5 15.5h4M16.5 15.5h4M7.5 19l-3 2M16.5 19l3 2"/>',
 'shield':    S % '<path d="M12 3l8 3.5v5.5c0 4.5-3.2 7.4-8 9-4.8-1.6-8-4.5-8-9V6.5L12 3z"/><path d="M9.3 12l1.9 1.9 3.6-3.6"/>',
 'teach':     S % '<path d="M3 6.5h8a2 2 0 012 2V20a2.6 2.6 0 00-2-1H3V6.5zM21 6.5h-8a2 2 0 00-2 2V20a2.6 2.6 0 012-1h8V6.5z"/>',
 'campus':    S % '<path d="M12 3.5l9.5 4.8-9.5 4.7-9.5-4.7L12 3.5z"/><path d="M6.5 11v5c0 1.6 2.5 3 5.5 3s5.5-1.4 5.5-3v-5M21.5 8.3v5.2"/>',
 'compass':   S % '<circle cx="12" cy="12" r="9"/><path d="M15.2 8.8l-2 5.2-5.2 2 2-5.2 5.2-2z"/>',
 'brief':     S % '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8.5 7V5.4A1.4 1.4 0 019.9 4h4.2a1.4 1.4 0 011.4 1.4V7M3 12h18"/>',
 'target':    S % '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/><circle cx="12" cy="12" r="1.2" fill="currentColor" stroke="none"/>',
 'map':       S % '<path d="M3 6.5l6-2.5 6 2.5 6-2.5v13l-6 2.5-6-2.5-6 2.5v-13z"/><path d="M9 4v13M15 6.5v13"/>',
 'gauge':     S % '<path d="M4 17a9 9 0 1116 0"/><path d="M12 17l4-5"/><circle cx="12" cy="17" r="1.4" fill="currentColor" stroke="none"/>',
 'lock':      S % '<rect x="4.5" y="10.5" width="15" height="10" rx="2"/><path d="M8 10.5V7.8a4 4 0 118 0v2.7"/>',
 'spark':     S % '<path d="M12 3l1.9 5.4L19.5 10l-5.6 1.6L12 17l-1.9-5.4L4.5 10l5.6-1.6L12 3z"/>',
 'users':     S % '<circle cx="8.5" cy="8" r="3"/><circle cx="16" cy="9.5" r="2.4"/><path d="M2.5 19c0-3.2 2.7-5.2 6-5.2s6 2 6 5.2M16 14.2c2.9 0 5.5 1.6 5.5 4.8"/>',
 'rocket':    S % '<path d="M12 3c3.5 2 5.5 5.5 5.5 9.5L14 16h-4l-3.5-3.5C6.5 8.5 8.5 5 12 3z"/><circle cx="12" cy="10" r="1.7"/><path d="M9 16.5c-1.5 1-2 2.5-2 4.5 2 0 3.5-.5 4.5-2M15 16.5c1.5 1 2 2.5 2 4.5-2 0-3.5-.5-4.5-2"/>',
}

def chip(entry):
    kind, label, col, val = tool(entry)
    lc, dc = safe(col)
    esc = html.escape(label)
    style = f'--tc:{lc}' + (f';--tcd:{dc}' if dc != lc else '')
    if kind == 'logo':
        inner = f'<svg aria-hidden="true"><use href="assets/logos/services-sprite.svg#li-{val}"/></svg>'
    else:
        inner = f'<i class="tchip__mono" aria-hidden="true">{html.escape(val)}</i>'
    return f'<span class="tchip" style="{style}">{inner}{esc}</span>'

def tool_wall(entries, cap='Tools &amp; platforms covered'):
    chips = ''.join(chip(e) for e in entries)
    return (f'<div class="trk__tools"><p class="trk__cap">{cap}</p>'
            f'<div class="tools">{chips}</div></div>')

# --------------------------------------------------------------------------
# non-tool content
# --------------------------------------------------------------------------
PILLARS = [
 ('teach', 'Corporate training',
  'Cohort programmes for engineering, data and business teams, built on your codebase and your data.',
  ['Freshers and lateral hires', 'Team upskilling &amp; reskilling', 'Role-based learning paths', 'Ends with a shipped project']),
 ('campus', 'University &amp; campus',
  'Semester modules, bootcamps and placement readiness delivered with the department, not around it.',
  ['Faculty development', 'Semester &amp; elective modules', 'Placement &amp; interview prep', 'Capstone mentoring']),
 ('compass', 'Advisory',
  'A senior second opinion on architecture, hiring and roadmap — retained, part-time, no delivery headcount.',
  ['Architecture review', 'Data &amp; AI strategy', 'Build vs buy calls', 'Hiring &amp; team design']),
 ('brief', 'Consulting',
  'Scoped delivery where I am accountable for an outcome, not just the recommendation.',
  ['Platform builds &amp; migrations', 'AI/agent implementations', 'Cost &amp; performance work', 'Fractional data lead']),
]

AUDIENCE = [
 ('users', 'Freshers', 'Zero to employable',
  'Fundamentals taught in the order you actually use them, with daily labs and code review rather than slide decks.',
  [('Duration', '8&ndash;16 weeks'), ('Format', 'Cohort, full-time'), ('Output', 'Portfolio + 2 projects')]),
 ('rocket', 'Laterals', 'Working engineers, new stack',
  'For people with shipping experience moving into data, cloud or AI. Short, dense, and built around migration reality.',
  [('Duration', '4&ndash;8 weeks'), ('Format', 'Part-time, evenings'), ('Output', 'Production-shaped build')]),
 ('campus', 'University programmes', 'Semester &amp; bootcamp',
  'Delivered with the department: syllabus mapping, lab design, faculty enablement and capstone supervision.',
  [('Duration', 'Semester or 2&ndash;6 wk', ), ('Format', 'On-campus / hybrid'), ('Output', 'Graded capstone')]),
 ('target', 'Placement readiness', 'Interview to offer',
  'DSA and system design drilling, mock interviews with written feedback, resume and portfolio rework, offer negotiation.',
  [('Duration', '4&ndash;10 weeks'), ('Format', 'Cohort + 1:1'), ('Output', 'Interview-ready profile')]),
]

ADVISORY = [
 ('blueprint', 'Architecture review', 'A written assessment of your data or application architecture, with the three changes that matter most and what each one costs.'),
 ('map', 'Data &amp; AI strategy', 'What to build, what to buy, and in what order — grounded in the team and budget you actually have.'),
 ('gauge', 'Cost &amp; performance audit', 'Where the cloud and warehouse bill is going, which pipelines nobody reads, and what to switch off first.'),
 ('users', 'Hiring &amp; team design', 'Role definitions, interview loops and scorecards for data, platform and AI roles. I will sit on panels.'),
 ('spark', 'AI readiness', 'An honest read on which use cases will survive contact with production, and which are demos.'),
 ('lock', 'Governance &amp; compliance', 'Lineage, PII handling, access review and audit trails designed in rather than retrofitted.'),
]

CONSULTING = [
 ('pipe', 'Platform build or migration', 'Lakehouse, warehouse or streaming platform delivered end to end, with your team alongside so it survives handover.'),
 ('agent', 'AI &amp; agent implementation', 'RAG systems, agent workflows and evaluation harnesses built to a defined outcome, not a proof of concept that stalls.'),
 ('chart', 'Analytics &amp; BI delivery', 'Semantic layer, models and dashboards that finance and ops will actually trust and use.'),
 ('brief', 'Fractional data lead', 'Part-time ownership of the data function: roadmap, standards, vendor calls and team mentoring.'),
 ('cube', 'Product engineering', 'Full-stack delivery on the Commbricks stack — chat, mail, admin and HRMS patterns already built once.'),
 ('shield', 'Rescue &amp; stabilisation', 'For platforms that are late, expensive or unreliable. Diagnosis first, then a plan with dates.'),
]

ENGAGE = [
 ('Training cohort', 'Fixed fee per cohort', '2&ndash;16 weeks', 'On-site, remote or hybrid', '8&ndash;40 people'),
 ('University programme', 'Per semester or module', 'Semester or short course', 'On-campus / hybrid', 'Department scale'),
 ('Advisory retainer', 'Monthly retainer', 'Rolling, 3-month minimum', 'Remote, periodic on-site', 'Leadership team'),
 ('Consulting project', 'Fixed scope or T&amp;M', '4 weeks&ndash;6 months', 'Embedded with your team', 'Project team'),
 ('Fractional lead', 'Days per month', 'Rolling', 'Hybrid', 'Whole data function'),
]

# --------------------------------------------------------------------------
# render
# --------------------------------------------------------------------------
def esc(t): return t  # content above already carries intentional entities

pillars_html = ''.join(
    f'<article class="pillar reveal" data-reveal-index="{i}">'
    f'<span class="pillar__n">{i+1:02d}</span>'
    f'<span class="pillar__ico">{GLYPH[g]}</span>'
    f'<h3>{t}</h3><p>{d}</p><ul>{"".join(f"<li>{b}</li>" for b in bul)}</ul></article>'
    for i, (g, t, d, bul) in enumerate(PILLARS))

aud_html = ''.join(
    f'<article class="aud reveal" data-reveal-index="{i}">'
    f'<span class="aud__k">{GLYPH[g]}{k}</span>'
    f'<h3>{t}</h3><p>{d}</p>'
    f'<dl>{"".join(f"<div><dt>{a}</dt><dd>{b}</dd></div>" for a, b in rows)}</dl></article>'
    for i, (g, k, t, d, rows) in enumerate(AUDIENCE))

def track_block(name, glyph, tone, blurb, tools, anchor):
    return (f'<article class="trk trk--{tone} reveal" id="{anchor}">'
            f'<div class="trk__head"><span class="trk__ico">{GLYPH[glyph]}</span>'
            f'<div><h3>{name}</h3><p>{blurb}</p></div></div>'
            f'{tool_wall(tools)}</article>')

def slugify(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

tech_html = ''.join(
    track_block(n, g, tone, b, tools, 't-' + slugify(n))
    for n, g, tone, b, tools in TECH)

dom_html = ''.join(
    f'<article class="trk trk--{tone} reveal" id="d-{slugify(n)}">'
    f'<div class="trk__head"><span class="trk__ico">{GLYPH[g]}</span>'
    f'<div><h3>{n}</h3><p>{b}</p></div></div>'
    f'<div class="dom__split">'
    f'<ul class="dom__mods">{"".join(f"<li>{m}</li>" for m in mods)}</ul>'
    f'<div><p class="trk__cap">Software &amp; tools covered</p>'
    f'<div class="tools">{"".join(chip(t) for t in tools)}</div></div>'
    f'</div></article>'
    for n, g, tone, b, mods, tools in DOMAIN)

adv_html = ''.join(
    f'<article class="offer"><span class="offer__ico">{GLYPH[g]}</span>'
    f'<h3>{t}</h3><p>{d}</p></article>' for g, t, d in ADVISORY)

cons_html = ''.join(
    f'<article class="offer"><span class="offer__ico">{GLYPH[g]}</span>'
    f'<h3>{t}</h3><p>{d}</p></article>' for g, t, d in CONSULTING)

engage_html = ''.join(
    f'<tr><th scope="row">{a}</th><td>{b}</td><td>{c}</td><td>{d}</td><td>{e}</td></tr>'
    for a, b, c, d, e in ENGAGE)

jump_html = ''.join(
    f'<a href="#t-{slugify(n)}">{GLYPH[g]}{n}</a>' for n, g, _, _, _ in TECH) + \
    ''.join(f'<a href="#d-{slugify(n)}">{GLYPH[g]}{n}</a>' for n, g, _, _, _, _ in DOMAIN)

n_tools = len({tool(t)[1] for _, _, _, _, ts in TECH for t in ts} |
              {tool(t)[1] for _, _, _, _, _, ts in DOMAIN for t in ts})
n_tracks = len(TECH) + len(DOMAIN)

TPL = open('build/services-template.html', encoding='utf-8').read()
out = (TPL.replace('<!--PILLARS-->', pillars_html)
          .replace('<!--AUDIENCE-->', aud_html)
          .replace('<!--TECH-->', tech_html)
          .replace('<!--DOMAIN-->', dom_html)
          .replace('<!--ADVISORY-->', adv_html)
          .replace('<!--CONSULTING-->', cons_html)
          .replace('<!--ENGAGE-->', engage_html)
          .replace('<!--JUMP-->', jump_html)
          .replace('{{NTOOLS}}', str(n_tools))
          .replace('{{NTRACKS}}', str(n_tracks)))
open('services.html', 'w', encoding='utf-8').write(out)
print(f'services.html written — {len(out)/1024:.0f} KB | {n_tracks} tracks | {n_tools} distinct tools')

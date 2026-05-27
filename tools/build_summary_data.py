#!/usr/bin/env python3
"""
Fetch key summary fields for ALL countries from factbook.json and output
a JS-embeddable data object. Run this to regenerate website/summary_data.js.
"""

import json
import sys
import re
import concurrent.futures
import urllib.request

COUNTRIES = [
    ["Algeria","africa","ag"],["Angola","africa","ao"],["Benin","africa","bn"],
    ["Botswana","africa","bc"],["Burkina Faso","africa","uv"],["Burundi","africa","by"],
    ["Cabo Verde","africa","cv"],["Cameroon","africa","cm"],
    ["Central African Republic","africa","ct"],["Chad","africa","cd"],
    ["Comoros","africa","cn"],["Congo, DR","africa","cg"],
    ["Congo, Republic","africa","cf"],["Cote d'Ivoire","africa","iv"],
    ["Djibouti","africa","dj"],["Egypt","africa","eg"],
    ["Equatorial Guinea","africa","ek"],["Eritrea","africa","er"],
    ["Eswatini","africa","wz"],["Ethiopia","africa","et"],["Gabon","africa","gb"],
    ["Gambia, The","africa","ga"],["Ghana","africa","gh"],["Guinea","africa","gv"],
    ["Guinea-Bissau","africa","pu"],["Kenya","africa","ke"],["Lesotho","africa","lt"],
    ["Liberia","africa","li"],["Libya","africa","ly"],["Madagascar","africa","ma"],
    ["Malawi","africa","mi"],["Mali","africa","ml"],["Mauritania","africa","mr"],
    ["Mauritius","africa","mp"],["Morocco","africa","mo"],["Mozambique","africa","mz"],
    ["Namibia","africa","wa"],["Niger","africa","ng"],["Nigeria","africa","ni"],
    ["Rwanda","africa","rw"],["Saint Helena","africa","sh"],
    ["Sao Tome and Principe","africa","tp"],["Senegal","africa","sg"],
    ["Seychelles","africa","se"],["Sierra Leone","africa","sl"],
    ["Somalia","africa","so"],["South Africa","africa","sf"],
    ["South Sudan","africa","od"],["Sudan","africa","su"],["Tanzania","africa","tz"],
    ["Togo","africa","to"],["Tunisia","africa","ts"],["Uganda","africa","ug"],
    ["Western Sahara","africa","wi"],["Zambia","africa","za"],
    ["Zimbabwe","africa","zi"],
    ["American Samoa","australia-oceania","aq"],["Australia","australia-oceania","as"],
    ["Cook Islands","australia-oceania","cw"],["Fiji","australia-oceania","fj"],
    ["French Polynesia","australia-oceania","fp"],["Guam","australia-oceania","gq"],
    ["Kiribati","australia-oceania","kr"],["Marshall Islands","australia-oceania","rm"],
    ["Micronesia","australia-oceania","fm"],["Nauru","australia-oceania","nr"],
    ["New Caledonia","australia-oceania","nc"],["New Zealand","australia-oceania","nz"],
    ["Niue","australia-oceania","ne"],
    ["Northern Mariana Islands","australia-oceania","cq"],
    ["Palau","australia-oceania","ps"],["Samoa","australia-oceania","ws"],
    ["Solomon Islands","australia-oceania","bp"],["Tonga","australia-oceania","tn"],
    ["Tuvalu","australia-oceania","tv"],["Vanuatu","australia-oceania","nh"],
    ["Wallis and Futuna","australia-oceania","wf"],
    ["Anguilla","central-america-n-caribbean","av"],
    ["Antigua and Barbuda","central-america-n-caribbean","ac"],
    ["Aruba","central-america-n-caribbean","aa"],
    ["Bahamas, The","central-america-n-caribbean","bf"],
    ["Barbados","central-america-n-caribbean","bb"],
    ["Belize","central-america-n-caribbean","bh"],
    ["British Virgin Islands","central-america-n-caribbean","vi"],
    ["Cayman Islands","central-america-n-caribbean","cj"],
    ["Costa Rica","central-america-n-caribbean","cs"],
    ["Cuba","central-america-n-caribbean","cu"],
    ["Curacao","central-america-n-caribbean","uc"],
    ["Dominica","central-america-n-caribbean","do"],
    ["Dominican Republic","central-america-n-caribbean","dr"],
    ["El Salvador","central-america-n-caribbean","es"],
    ["Grenada","central-america-n-caribbean","gj"],
    ["Guatemala","central-america-n-caribbean","gt"],
    ["Haiti","central-america-n-caribbean","ha"],
    ["Honduras","central-america-n-caribbean","ho"],
    ["Jamaica","central-america-n-caribbean","jm"],
    ["Montserrat","central-america-n-caribbean","mh"],
    ["Nicaragua","central-america-n-caribbean","nu"],
    ["Panama","central-america-n-caribbean","pm"],
    ["Puerto Rico","central-america-n-caribbean","rq"],
    ["Saint Barthelemy","central-america-n-caribbean","tb"],
    ["Saint Kitts and Nevis","central-america-n-caribbean","sc"],
    ["Saint Lucia","central-america-n-caribbean","st"],
    ["Saint Martin","central-america-n-caribbean","rn"],
    ["Saint Vincent and the Grenadines","central-america-n-caribbean","vc"],
    ["Sint Maarten","central-america-n-caribbean","nn"],
    ["Trinidad and Tobago","central-america-n-caribbean","td"],
    ["Turks and Caicos Islands","central-america-n-caribbean","tk"],
    ["US Virgin Islands","central-america-n-caribbean","vq"],
    ["Armenia","central-asia","am"],["Azerbaijan","central-asia","aj"],
    ["Georgia","central-asia","gg"],["Kazakhstan","central-asia","kz"],
    ["Kyrgyzstan","central-asia","kg"],["Russia","central-asia","rs"],
    ["Tajikistan","central-asia","ti"],["Turkmenistan","central-asia","tx"],
    ["Uzbekistan","central-asia","uz"],
    ["Brunei","east-n-southeast-asia","bx"],
    ["Burma (Myanmar)","east-n-southeast-asia","bm"],
    ["Cambodia","east-n-southeast-asia","cb"],["China","east-n-southeast-asia","ch"],
    ["Hong Kong","east-n-southeast-asia","hk"],
    ["Indonesia","east-n-southeast-asia","id"],["Japan","east-n-southeast-asia","ja"],
    ["Laos","east-n-southeast-asia","la"],["Macau","east-n-southeast-asia","mc"],
    ["Malaysia","east-n-southeast-asia","my"],
    ["Mongolia","east-n-southeast-asia","mg"],
    ["North Korea","east-n-southeast-asia","kn"],
    ["Papua New Guinea","east-n-southeast-asia","pp"],
    ["Philippines","east-n-southeast-asia","rp"],
    ["Singapore","east-n-southeast-asia","sn"],
    ["South Korea","east-n-southeast-asia","ks"],
    ["Taiwan","east-n-southeast-asia","tw"],["Thailand","east-n-southeast-asia","th"],
    ["Timor-Leste","east-n-southeast-asia","tt"],
    ["Vietnam","east-n-southeast-asia","vm"],
    ["Albania","europe","al"],["Andorra","europe","an"],["Austria","europe","au"],
    ["Belarus","europe","bo"],["Belgium","europe","be"],
    ["Bosnia and Herzegovina","europe","bk"],["Bulgaria","europe","bu"],
    ["Croatia","europe","hr"],["Cyprus","europe","cy"],["Czechia","europe","ez"],
    ["Denmark","europe","da"],["Estonia","europe","en"],
    ["Faroe Islands","europe","fo"],["Finland","europe","fi"],
    ["France","europe","fr"],["Germany","europe","gm"],["Gibraltar","europe","gi"],
    ["Greece","europe","gr"],["Guernsey","europe","gk"],["Hungary","europe","hu"],
    ["Iceland","europe","ic"],["Ireland","europe","ei"],
    ["Isle of Man","europe","im"],["Italy","europe","it"],["Jersey","europe","je"],
    ["Kosovo","europe","kv"],["Latvia","europe","lg"],
    ["Liechtenstein","europe","ls"],["Lithuania","europe","lh"],
    ["Luxembourg","europe","lu"],["Malta","europe","mt"],["Moldova","europe","md"],
    ["Monaco","europe","mn"],["Montenegro","europe","mj"],
    ["Netherlands","europe","nl"],["North Macedonia","europe","mk"],
    ["Norway","europe","no"],["Poland","europe","pl"],["Portugal","europe","po"],
    ["Romania","europe","ro"],["San Marino","europe","sm"],["Serbia","europe","ri"],
    ["Slovakia","europe","lo"],["Slovenia","europe","si"],["Spain","europe","sp"],
    ["Sweden","europe","sw"],["Switzerland","europe","sz"],["Ukraine","europe","up"],
    ["United Kingdom","europe","uk"],["Vatican City","europe","vt"],
    ["Bahrain","middle-east","ba"],["Iran","middle-east","ir"],
    ["Iraq","middle-east","iz"],["Israel","middle-east","is"],
    ["Jordan","middle-east","jo"],["Kuwait","middle-east","ku"],
    ["Lebanon","middle-east","le"],["Oman","middle-east","mu"],
    ["Qatar","middle-east","qa"],["Saudi Arabia","middle-east","sa"],
    ["Syria","middle-east","sy"],["Turkey","middle-east","tu"],
    ["United Arab Emirates","middle-east","ae"],
    ["Palestine (West Bank)","middle-east","we"],["Yemen","middle-east","ym"],
    ["Bermuda","north-america","bd"],["Canada","north-america","ca"],
    ["Greenland","north-america","gl"],["Mexico","north-america","mx"],
    ["Saint Pierre and Miquelon","north-america","sb"],
    ["United States","north-america","us"],
    ["Argentina","south-america","ar"],["Bolivia","south-america","bl"],
    ["Brazil","south-america","br"],["Chile","south-america","ci"],
    ["Colombia","south-america","co"],["Ecuador","south-america","ec"],
    ["Falkland Islands","south-america","fk"],["Guyana","south-america","gy"],
    ["Paraguay","south-america","pa"],["Peru","south-america","pe"],
    ["Suriname","south-america","ns"],["Uruguay","south-america","uy"],
    ["Venezuela","south-america","ve"],
    ["Afghanistan","south-asia","af"],["Bangladesh","south-asia","bg"],
    ["Bhutan","south-asia","bt"],["India","south-asia","in"],
    ["Maldives","south-asia","mv"],["Nepal","south-asia","np"],
    ["Pakistan","south-asia","pk"],["Sri Lanka","south-asia","ce"],
]

HDI = {
    "switzerland":0.967,"norway":0.966,"iceland":0.959,"denmark":0.952,"sweden":0.952,
    "germany":0.950,"ireland":0.950,"singapore":0.949,"netherlands":0.946,"australia":0.946,
    "liechtenstein":0.945,"belgium":0.942,"finland":0.942,"united kingdom":0.940,"japan":0.940,
    "new zealand":0.939,"canada":0.938,"south korea":0.929,"united states":0.927,"austria":0.926,
    "israel":0.926,"malta":0.918,"luxembourg":0.916,"france":0.914,"slovenia":0.909,
    "spain":0.911,"italy":0.906,"czechia":0.905,"estonia":0.899,"greece":0.893,
    "cyprus":0.896,"poland":0.881,"lithuania":0.879,"united arab emirates":0.937,
    "saudi arabia":0.875,"chile":0.860,"croatia":0.858,"latvia":0.863,"portugal":0.874,
    "hungary":0.856,"argentina":0.849,"turkey":0.855,"montenegro":0.844,"qatar":0.875,
    "bahrain":0.888,"romania":0.828,"kuwait":0.847,"russia":0.822,"belarus":0.801,
    "oman":0.821,"uruguay":0.830,"costa rica":0.806,"panama":0.805,"malaysia":0.807,
    "georgia":0.814,"serbia":0.805,"thailand":0.803,"albania":0.796,"china":0.788,
    "mexico":0.781,"brazil":0.760,"colombia":0.758,"ecuador":0.765,"peru":0.762,
    "ukraine":0.734,"south africa":0.717,"egypt":0.728,"indonesia":0.713,"vietnam":0.726,
    "philippines":0.710,"bolivia":0.698,"india":0.644,"ghana":0.602,"kenya":0.601,
    "cambodia":0.600,"bangladesh":0.670,"pakistan":0.544,"nigeria":0.548,"myanmar":0.585,
    "ethiopia":0.492,"congo, dr":0.479,"afghanistan":0.462,"sudan":0.516,"haiti":0.535,
    "yemen":0.424,"chad":0.394,"niger":0.394,"south sudan":0.381,
    "central african republic":0.387,"somalia":0.380,"sierra leone":0.477,"mali":0.410,
    "burkina faso":0.438,"mozambique":0.461,"madagascar":0.421,"malawi":0.508,
    "tanzania":0.532,"uganda":0.550,"rwanda":0.548,"senegal":0.517,"nepal":0.601,
    "iraq":0.686,"iran":0.780,"jordan":0.736,"lebanon":0.723,"jamaica":0.709,
    "cuba":0.764,"dominican republic":0.766,"guatemala":0.627,"honduras":0.621,
    "el salvador":0.675,"nicaragua":0.667,"paraguay":0.717,"venezuela":0.699,
    "libya":0.718,"algeria":0.745,"morocco":0.698,"tunisia":0.740,"botswana":0.693,
    "namibia":0.610,"zambia":0.565,"zimbabwe":0.550,"angola":0.586,"cameroon":0.576,
    "hong kong":0.956,"taiwan":0.926,"brunei":0.829,"trinidad and tobago":0.814,
    "barbados":0.809,"antigua and barbuda":0.794,"seychelles":0.802,
    "sri lanka":0.782,"maldives":0.762,"mongolia":0.741,"azerbaijan":0.760,
    "armenia":0.786,"kazakhstan":0.802,"uzbekistan":0.727,"kyrgyzstan":0.701,
    "tajikistan":0.679,"turkmenistan":0.744,"bhutan":0.681,"laos":0.620,
    "timor-leste":0.606,"fiji":0.729,"tonga":0.745,"samoa":0.702,
}


def get_text(obj):
    """Extract text from factbook field."""
    if obj is None:
        return None
    if isinstance(obj, str):
        return obj
    if isinstance(obj, (int, float)):
        return str(obj)
    if isinstance(obj, dict):
        if "text" in obj:
            return str(obj["text"])
        parts = []
        for k, v in obj.items():
            val = get_text(v)
            if val:
                parts.append(val)
        return "; ".join(parts) if parts else None
    if isinstance(obj, list):
        return "; ".join(filter(None, (get_text(i) for i in obj)))
    return str(obj)


def extract_number(text, pattern=r'[\d,.]+'):
    """Extract first number from text."""
    if not text:
        return None
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    m = re.search(pattern, text)
    if m:
        return m.group().replace(',', '')
    return None


def safe_float(text):
    """Try to parse a float from text."""
    if not text:
        return None
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def safe_get(data, *keys):
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return None
        if current is None:
            return None
    return current


def fetch_country(entry):
    """Fetch and extract summary data for one country."""
    name, region, code = entry
    url = f"https://raw.githubusercontent.com/factbook/factbook.json/master/{region}/{code}.json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=15)
        raw = json.loads(resp.read())
    except Exception as e:
        print(f"  FAIL: {name} ({e})", file=sys.stderr)
        return None

    people = raw.get("People and Society", {})
    econ = raw.get("Economy", {})
    mil = raw.get("Military and Security", {})
    gov = raw.get("Government", {})

    # Population
    pop_text = get_text(safe_get(people, "Population", "total"))
    pop_num = extract_number(pop_text)

    # Life expectancy (skip year-like numbers at start, look for XX.X pattern)
    le_text = get_text(safe_get(people, "Life expectancy at birth", "total population"))
    le_num = None
    if le_text:
        # Remove parenthesized year estimates like "(2017 est.)"
        le_clean = re.sub(r'\(\d{4}\s*est\.?\)', '', le_text)
        le_m = re.search(r'(\d{1,2}\.\d)', le_clean)
        if le_m:
            le_num = le_m.group(1)
        else:
            # Fallback: find a number that's plausibly a life expectancy (30-100)
            for m in re.finditer(r'[\d.]+', le_clean):
                val = float(m.group())
                if 30 <= val <= 100:
                    le_num = m.group()
                    break

    # GDP per capita - get most recent year
    gdpc_obj = safe_get(econ, "Real GDP per capita")
    gdpc_text = None
    if isinstance(gdpc_obj, dict):
        for k, v in gdpc_obj.items():
            if 'note' not in k.lower():
                gdpc_text = get_text(v)
                break
    gdpc_num = extract_number(gdpc_text, r'\$[\d,.]+')
    if gdpc_num:
        gdpc_num = gdpc_num.replace('$', '')

    # GDP growth
    gdpg_obj = safe_get(econ, "Real GDP growth rate")
    gdpg_text = None
    if isinstance(gdpg_obj, dict):
        for k, v in gdpg_obj.items():
            if 'note' not in k.lower():
                gdpg_text = get_text(v)
                break
    gdpg_num = extract_number(gdpg_text, r'-?[\d.]+')

    # Inflation
    inf_obj = safe_get(econ, "Inflation rate (consumer prices)")
    inf_text = None
    if isinstance(inf_obj, dict):
        for k, v in inf_obj.items():
            if 'note' not in k.lower():
                inf_text = get_text(v)
                break
    inf_num = extract_number(inf_text, r'-?[\d.]+')

    # Unemployment
    unemp_obj = safe_get(econ, "Unemployment rate")
    unemp_text = None
    if isinstance(unemp_obj, dict):
        for k, v in unemp_obj.items():
            if 'note' not in k.lower():
                unemp_text = get_text(v)
                break
    unemp_num = extract_number(unemp_text, r'[\d.]+')

    # Poverty
    pov_text = get_text(safe_get(econ, "Population below poverty line"))
    pov_num = extract_number(pov_text, r'[\d.]+')

    # GINI
    gini_text = get_text(safe_get(econ, "Gini Index coefficient - distribution of family income"))
    gini_num = None
    if isinstance(safe_get(econ, "Gini Index coefficient - distribution of family income"), dict):
        for k, v in safe_get(econ, "Gini Index coefficient - distribution of family income").items():
            if 'note' not in k.lower():
                t = get_text(v)
                gini_num = extract_number(t, r'[\d.]+')
                break

    # Infant mortality
    im_text = get_text(safe_get(people, "Infant mortality rate", "total"))
    im_num = extract_number(im_text, r'[\d.]+')

    # Maternal mortality
    mm_text = get_text(safe_get(people, "Maternal mortality ratio"))
    mm_num = extract_number(mm_text, r'[\d,.]+')

    # Physicians
    phys_text = get_text(safe_get(people, "Physician density"))
    phys_num = extract_number(phys_text, r'[\d.]+')

    # Education spending (try multiple key patterns)
    edu_num = None
    edu_obj = safe_get(people, "Education expenditure")
    if isinstance(edu_obj, dict):
        for k, v in edu_obj.items():
            if '% GDP' in k or '% of GDP' in k:
                edu_text = get_text(v)
                edu_num = extract_number(edu_text, r'[\d.]+')
                break
    if edu_num is None:
        edu_text = get_text(safe_get(people, "Education expenditures"))
        edu_num = extract_number(edu_text, r'[\d.]+')

    # School life expectancy
    sle_text = get_text(safe_get(people, "School life expectancy (primary to tertiary education)", "total"))
    sle_num = extract_number(sle_text, r'[\d]+')

    # Military expenditure (look for "X% of GDP" pattern, skip narrative text)
    mil_obj = safe_get(mil, "Military expenditures")
    mil_num = None
    if isinstance(mil_obj, dict):
        # Try structured multi-year entries first (e.g. "Military Expenditures 2024": {...})
        for k, v in mil_obj.items():
            if 'note' in k.lower() or k == 'text':
                continue
            t = get_text(v)
            mm = re.search(r'([\d.]+)%\s*of\s*GDP', t or '')
            if mm:
                mil_num = mm.group(1)
                break
        # If still None, try the top-level text for "X% of GDP" or "X-Y% of GDP"
        if mil_num is None:
            t = get_text(mil_obj)
            mm = re.search(r'(\d{1,2}(?:\.\d+)?)[-%]\s*(?:of\s*)?GDP', t or '', re.IGNORECASE)
            if not mm:
                # Try "XX-YY% of GDP" and take midpoint or "estimated XX%" patterns
                mm2 = re.search(r'(\d{1,2})-(\d{1,2})%\s*of\s*(?:.*?\s)?GDP', t or '', re.IGNORECASE)
                if mm2:
                    mil_num = str((float(mm2.group(1)) + float(mm2.group(2))) / 2)
            else:
                mil_num = mm.group(1)

    # Government type
    gov_text = get_text(safe_get(gov, "Government type"))
    if gov_text:
        gov_text = re.sub(r'<[^>]+>', '', gov_text).strip()

    # Helper: extract first year dollar amount from multi-year dict (billions)
    def first_year_billions(obj):
        if not isinstance(obj, dict):
            return None
        for k, v in obj.items():
            if 'note' in k.lower():
                continue
            t = get_text(v)
            m = re.search(r'\$([\d,.]+)\s*(trillion|billion|million)?', t, re.IGNORECASE)
            if m:
                num = float(m.group(1).replace(',', ''))
                unit = (m.group(2) or '').lower()
                if unit == 'trillion':
                    num *= 1000
                elif unit == 'million':
                    num /= 1000
                # default is already billions
                return round(num, 2)
            # plain number (already in dollars)
            m2 = re.search(r'[\d,.]+', t)
            if m2:
                return round(float(m2.group().replace(',', '')) / 1e9, 2)
            break
        return None

    # Exports $
    exp_val = first_year_billions(safe_get(econ, "Exports"))

    # Imports $
    imp_val = first_year_billions(safe_get(econ, "Imports"))

    # Export partners
    exp_part = get_text(safe_get(econ, "Exports - partners"))
    if exp_part:
        exp_part = re.sub(r'<[^>]+>', '', exp_part).strip()

    # Export commodities
    exp_comm = get_text(safe_get(econ, "Exports - commodities"))
    if exp_comm:
        exp_comm = re.sub(r'<[^>]+>', '', exp_comm).strip()

    # Import partners
    imp_part = get_text(safe_get(econ, "Imports - partners"))
    if imp_part:
        imp_part = re.sub(r'<[^>]+>', '', imp_part).strip()

    # Import commodities
    imp_comm = get_text(safe_get(econ, "Imports - commodities"))
    if imp_comm:
        imp_comm = re.sub(r'<[^>]+>', '', imp_comm).strip()

    # Budget surplus/deficit (calculate from revenues - expenditures)
    budget_num = None
    budget_obj = safe_get(econ, "Budget")
    if isinstance(budget_obj, dict):
        rev_text = get_text(safe_get(budget_obj, "revenues"))
        exp_text = get_text(safe_get(budget_obj, "expenditures"))
        def parse_dollars_b(t):
            if not t:
                return None
            m = re.search(r'\$([\d,.]+)\s*(trillion|billion|million)?', t, re.IGNORECASE)
            if not m:
                return None
            n = float(m.group(1).replace(',', ''))
            u = (m.group(2) or 'billion').lower()
            if u == 'trillion': n *= 1000
            elif u == 'million': n /= 1000
            return n
        rev_b = parse_dollars_b(rev_text)
        exp_b = parse_dollars_b(exp_text)
        if rev_b is not None and exp_b is not None:
            budget_num = round(rev_b - exp_b, 1)  # positive = surplus, negative = deficit

    # Current account balance (can be negative)
    cab_val = None
    cab_obj = safe_get(econ, "Current account balance")
    if isinstance(cab_obj, dict):
        for k, v in cab_obj.items():
            if 'note' in k.lower():
                continue
            t = get_text(v)
            negative = '-' in t.split('$')[0] if '$' in t else False
            m = re.search(r'\$([\d,.]+)\s*(trillion|billion|million)?', t, re.IGNORECASE)
            if m:
                num = float(m.group(1).replace(',', ''))
                unit = (m.group(2) or 'billion').lower()
                if unit == 'trillion': num *= 1000
                elif unit == 'million': num /= 1000
                cab_val = round(-num if negative else num, 2)
            break

    # Labor force (handle "174.174 million" style)
    labor_text = get_text(safe_get(econ, "Labor force"))
    labor_num = None
    if labor_text:
        lm = re.search(r'([\d,.]+)\s*(million|billion|thousand)?', labor_text, re.IGNORECASE)
        if lm:
            lval = float(lm.group(1).replace(',', ''))
            lunit = (lm.group(2) or '').lower()
            if lunit == 'billion': lval *= 1e9
            elif lunit == 'million': lval *= 1e6
            elif lunit == 'thousand': lval *= 1e3
            labor_num = int(lval)

    # GDP by sector
    sector_obj = safe_get(econ, "GDP - composition, by sector of origin")
    sector = {}
    if isinstance(sector_obj, dict):
        for sk in ['agriculture', 'industry', 'services']:
            sv = get_text(safe_get(sector_obj, sk))
            sm = re.search(r'[\d.]+', sv or '')
            if sm:
                sector[sk] = float(sm.group())

    # GDP composition by end use
    enduse_obj = safe_get(econ, "GDP - composition, by end use")
    enduse = {}
    if isinstance(enduse_obj, dict):
        eu_map = {
            'household consumption': 'hh',
            'government consumption': 'govt',
            'investment in fixed capital': 'inv',
            'exports of goods and services': 'exp',
            'imports of goods and services': 'imp',
        }
        for ek, short in eu_map.items():
            ev = get_text(safe_get(enduse_obj, ek))
            em = re.search(r'-?[\d.]+', ev or '')
            if em:
                enduse[short] = float(em.group())

    # HDI
    hdi_key = name.lower().replace(' (myanmar)', '').replace('bahamas, the', 'bahamas').replace('gambia, the', 'gambia')
    hdi = HDI.get(hdi_key)

    row = {
        "n": name,
        "r": region,
        "c": code,
        "pop": safe_float(pop_num),
        "le": safe_float(le_num),
        "gdpc": safe_float(gdpc_num),
        "gdpg": safe_float(gdpg_num),
        "inf": safe_float(inf_num),
        "unemp": safe_float(unemp_num),
        "pov": safe_float(pov_num),
        "gini": safe_float(gini_num),
        "hdi": hdi,
        "im": safe_float(im_num),
        "mm": safe_float(mm_num),
        "phys": safe_float(phys_num),
        "edu": safe_float(edu_num),
        "sle": safe_float(sle_num),
        "mil": safe_float(mil_num),
        "gov": gov_text,
        "exp": exp_val,
        "imp": imp_val,
        "expP": exp_part or None,
        "expC": exp_comm or None,
        "impP": imp_part or None,
        "impC": imp_comm or None,
        "budget": budget_num,
        "cab": cab_val,
        "labor": safe_float(labor_num),
        "sector": sector or None,
        "enduse": enduse or None,
    }

    print(f"  OK: {name}", file=sys.stderr)
    return row


def main():
    print(f"Fetching {len(COUNTRIES)} countries...", file=sys.stderr)

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(fetch_country, c): c for c in COUNTRIES}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                results.append(result)

    # Sort by name
    results.sort(key=lambda x: x["n"])

    print(f"\nSuccessfully fetched {len(results)}/{len(COUNTRIES)} countries", file=sys.stderr)

    # Output as JS
    js = "const SUMMARY_DATA = " + json.dumps(results, separators=(',', ':')) + ";\n"

    out_path = "website/summary_data.js"
    with open(out_path, "w") as f:
        f.write(js)
    print(f"Written to {out_path} ({len(js)} bytes)", file=sys.stderr)


if __name__ == "__main__":
    main()

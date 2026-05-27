#!/usr/bin/env python3
"""
Fetch country data from the CIA World Factbook (via factbook.json on GitHub)
and include HDI from UNDP.

Usage: python3 tools/fetch_country_data.py "Norway"
Output: JSON file saved to .tmp/{country}_data.json
"""

import json
import os
import re
import sys
import requests

# FIPS country codes used by factbook.json + region folders
COUNTRY_MAP = {
    "afghanistan": ("south-asia", "af"),
    "albania": ("europe", "al"),
    "algeria": ("africa", "ag"),
    "andorra": ("europe", "an"),
    "angola": ("africa", "ao"),
    "antigua and barbuda": ("central-america-n-caribbean", "ac"),
    "argentina": ("south-america", "ar"),
    "armenia": ("middle-east", "am"),
    "australia": ("australia-oceania", "as"),
    "austria": ("europe", "au"),
    "azerbaijan": ("middle-east", "aj"),
    "bahamas": ("central-america-n-caribbean", "bf"),
    "the bahamas": ("central-america-n-caribbean", "bf"),
    "bahrain": ("middle-east", "ba"),
    "bangladesh": ("south-asia", "bg"),
    "barbados": ("central-america-n-caribbean", "bb"),
    "belarus": ("europe", "bo"),
    "belgium": ("europe", "be"),
    "belize": ("central-america-n-caribbean", "bh"),
    "benin": ("africa", "bn"),
    "bhutan": ("south-asia", "bt"),
    "bolivia": ("south-america", "bl"),
    "bosnia and herzegovina": ("europe", "bk"),
    "botswana": ("africa", "bc"),
    "brazil": ("south-america", "br"),
    "brunei": ("east-n-southeast-asia", "bx"),
    "bulgaria": ("europe", "bu"),
    "burkina faso": ("africa", "uv"),
    "burma": ("east-n-southeast-asia", "bm"),
    "myanmar": ("east-n-southeast-asia", "bm"),
    "burundi": ("africa", "by"),
    "cambodia": ("east-n-southeast-asia", "cb"),
    "cameroon": ("africa", "cm"),
    "canada": ("north-america", "ca"),
    "cape verde": ("africa", "cv"),
    "cabo verde": ("africa", "cv"),
    "central african republic": ("africa", "ct"),
    "chad": ("africa", "cd"),
    "chile": ("south-america", "ci"),
    "china": ("east-n-southeast-asia", "ch"),
    "colombia": ("south-america", "co"),
    "comoros": ("africa", "cn"),
    "congo democratic republic": ("africa", "cg"),
    "congo republic": ("africa", "cf"),
    "congo dr": ("africa", "cg"),
    "costa rica": ("central-america-n-caribbean", "cs"),
    "cote d'ivoire": ("africa", "iv"),
    "ivory coast": ("africa", "iv"),
    "croatia": ("europe", "hr"),
    "cuba": ("central-america-n-caribbean", "cu"),
    "cyprus": ("europe", "cy"),
    "czech republic": ("europe", "ez"),
    "czechia": ("europe", "ez"),
    "denmark": ("europe", "da"),
    "djibouti": ("africa", "dj"),
    "dominica": ("central-america-n-caribbean", "do"),
    "dominican republic": ("central-america-n-caribbean", "dr"),
    "ecuador": ("south-america", "ec"),
    "egypt": ("africa", "eg"),
    "el salvador": ("central-america-n-caribbean", "es"),
    "equatorial guinea": ("africa", "ek"),
    "eritrea": ("africa", "er"),
    "estonia": ("europe", "en"),
    "eswatini": ("africa", "wz"),
    "swaziland": ("africa", "wz"),
    "ethiopia": ("africa", "et"),
    "fiji": ("australia-oceania", "fj"),
    "finland": ("europe", "fi"),
    "france": ("europe", "fr"),
    "gabon": ("africa", "gb"),
    "gambia": ("africa", "ga"),
    "the gambia": ("africa", "ga"),
    "georgia": ("middle-east", "gg"),
    "germany": ("europe", "gm"),
    "ghana": ("africa", "gh"),
    "greece": ("europe", "gr"),
    "grenada": ("central-america-n-caribbean", "gj"),
    "guatemala": ("central-america-n-caribbean", "gt"),
    "guinea": ("africa", "gv"),
    "guinea-bissau": ("africa", "pu"),
    "guyana": ("south-america", "gy"),
    "haiti": ("central-america-n-caribbean", "ha"),
    "honduras": ("central-america-n-caribbean", "ho"),
    "hungary": ("europe", "hu"),
    "iceland": ("europe", "ic"),
    "india": ("south-asia", "in"),
    "indonesia": ("east-n-southeast-asia", "id"),
    "iran": ("middle-east", "ir"),
    "iraq": ("middle-east", "iz"),
    "ireland": ("europe", "ei"),
    "israel": ("middle-east", "is"),
    "italy": ("europe", "it"),
    "jamaica": ("central-america-n-caribbean", "jm"),
    "japan": ("east-n-southeast-asia", "ja"),
    "jordan": ("middle-east", "jo"),
    "kazakhstan": ("central-asia", "kz"),
    "kenya": ("africa", "ke"),
    "kiribati": ("australia-oceania", "kr"),
    "north korea": ("east-n-southeast-asia", "kn"),
    "south korea": ("east-n-southeast-asia", "ks"),
    "korea south": ("east-n-southeast-asia", "ks"),
    "kosovo": ("europe", "kv"),
    "kuwait": ("middle-east", "ku"),
    "kyrgyzstan": ("central-asia", "kg"),
    "laos": ("east-n-southeast-asia", "la"),
    "latvia": ("europe", "lg"),
    "lebanon": ("middle-east", "le"),
    "lesotho": ("africa", "lt"),
    "liberia": ("africa", "li"),
    "libya": ("africa", "ly"),
    "liechtenstein": ("europe", "ls"),
    "lithuania": ("europe", "lh"),
    "luxembourg": ("europe", "lu"),
    "madagascar": ("africa", "ma"),
    "malawi": ("africa", "mi"),
    "malaysia": ("east-n-southeast-asia", "my"),
    "maldives": ("south-asia", "mv"),
    "mali": ("africa", "ml"),
    "malta": ("europe", "mt"),
    "marshall islands": ("australia-oceania", "rm"),
    "mauritania": ("africa", "mr"),
    "mauritius": ("africa", "mp"),
    "mexico": ("north-america", "mx"),
    "micronesia": ("australia-oceania", "fm"),
    "moldova": ("europe", "md"),
    "monaco": ("europe", "mn"),
    "mongolia": ("east-n-southeast-asia", "mg"),
    "montenegro": ("europe", "mj"),
    "morocco": ("africa", "mo"),
    "mozambique": ("africa", "mz"),
    "namibia": ("africa", "wa"),
    "nauru": ("australia-oceania", "nr"),
    "nepal": ("south-asia", "np"),
    "netherlands": ("europe", "nl"),
    "new zealand": ("australia-oceania", "nz"),
    "nicaragua": ("central-america-n-caribbean", "nu"),
    "niger": ("africa", "ng"),
    "nigeria": ("africa", "ni"),
    "north macedonia": ("europe", "mk"),
    "norway": ("europe", "no"),
    "oman": ("middle-east", "mu"),
    "pakistan": ("south-asia", "pk"),
    "palau": ("australia-oceania", "ps"),
    "panama": ("central-america-n-caribbean", "pm"),
    "papua new guinea": ("australia-oceania", "pp"),
    "paraguay": ("south-america", "pa"),
    "peru": ("south-america", "pe"),
    "philippines": ("east-n-southeast-asia", "rp"),
    "poland": ("europe", "pl"),
    "portugal": ("europe", "po"),
    "qatar": ("middle-east", "qa"),
    "romania": ("europe", "ro"),
    "russia": ("europe", "rs"),
    "rwanda": ("africa", "rw"),
    "samoa": ("australia-oceania", "ws"),
    "san marino": ("europe", "sm"),
    "sao tome and principe": ("africa", "tp"),
    "saudi arabia": ("middle-east", "sa"),
    "senegal": ("africa", "sg"),
    "serbia": ("europe", "ri"),
    "seychelles": ("africa", "se"),
    "sierra leone": ("africa", "sl"),
    "singapore": ("east-n-southeast-asia", "sn"),
    "slovakia": ("europe", "lo"),
    "slovenia": ("europe", "si"),
    "solomon islands": ("australia-oceania", "bp"),
    "somalia": ("africa", "so"),
    "south africa": ("africa", "sf"),
    "south sudan": ("africa", "od"),
    "spain": ("europe", "sp"),
    "sri lanka": ("south-asia", "ce"),
    "sudan": ("africa", "su"),
    "suriname": ("south-america", "ns"),
    "sweden": ("europe", "sw"),
    "switzerland": ("europe", "sz"),
    "syria": ("middle-east", "sy"),
    "tajikistan": ("central-asia", "ti"),
    "tanzania": ("africa", "tz"),
    "thailand": ("east-n-southeast-asia", "th"),
    "timor-leste": ("east-n-southeast-asia", "tt"),
    "east timor": ("east-n-southeast-asia", "tt"),
    "togo": ("africa", "to"),
    "tonga": ("australia-oceania", "tn"),
    "trinidad and tobago": ("central-america-n-caribbean", "td"),
    "tunisia": ("africa", "ts"),
    "turkey": ("middle-east", "tu"),
    "turkiye": ("middle-east", "tu"),
    "turkmenistan": ("central-asia", "tx"),
    "tuvalu": ("australia-oceania", "tv"),
    "uganda": ("africa", "ug"),
    "ukraine": ("europe", "up"),
    "united arab emirates": ("middle-east", "ae"),
    "uae": ("middle-east", "ae"),
    "united kingdom": ("europe", "uk"),
    "uk": ("europe", "uk"),
    "united states": ("north-america", "us"),
    "usa": ("north-america", "us"),
    "uruguay": ("south-america", "uy"),
    "uzbekistan": ("central-asia", "uz"),
    "vanuatu": ("australia-oceania", "nh"),
    "vatican city": ("europe", "vt"),
    "venezuela": ("south-america", "ve"),
    "vietnam": ("east-n-southeast-asia", "vm"),
    "yemen": ("middle-east", "ym"),
    "zambia": ("africa", "za"),
    "zimbabwe": ("africa", "zi"),
}

# HDI values from UNDP Human Development Report 2025 (based on 2023 data)
HDI_VALUES = {
    "switzerland": 0.967, "norway": 0.966, "iceland": 0.959,
    "hong kong": 0.956, "denmark": 0.952, "sweden": 0.952,
    "germany": 0.950, "ireland": 0.950, "singapore": 0.949,
    "netherlands": 0.946, "australia": 0.946, "liechtenstein": 0.945,
    "belgium": 0.942, "finland": 0.942, "united kingdom": 0.940,
    "japan": 0.940, "new zealand": 0.939, "canada": 0.938,
    "south korea": 0.929, "united states": 0.927, "austria": 0.926,
    "israel": 0.926, "malta": 0.918, "luxembourg": 0.916,
    "france": 0.914, "slovenia": 0.909, "spain": 0.911,
    "italy": 0.906, "czech republic": 0.905, "czechia": 0.905,
    "estonia": 0.899, "greece": 0.893, "cyprus": 0.896,
    "poland": 0.881, "lithuania": 0.879, "united arab emirates": 0.937,
    "uae": 0.937, "saudi arabia": 0.875, "chile": 0.860,
    "croatia": 0.858, "latvia": 0.863, "portugal": 0.874,
    "hungary": 0.856, "argentina": 0.849, "turkey": 0.855,
    "turkiye": 0.855, "montenegro": 0.844, "qatar": 0.875,
    "bahrain": 0.888, "romania": 0.828, "kuwait": 0.847,
    "russia": 0.822, "belarus": 0.801, "oman": 0.821,
    "uruguay": 0.830, "costa rica": 0.806, "panama": 0.805,
    "malaysia": 0.807, "georgia": 0.814, "serbia": 0.805,
    "thailand": 0.803, "albania": 0.796, "china": 0.788,
    "mexico": 0.781, "brazil": 0.760, "colombia": 0.758,
    "ecuador": 0.765, "peru": 0.762, "ukraine": 0.734,
    "south africa": 0.717, "egypt": 0.728, "indonesia": 0.713,
    "vietnam": 0.726, "philippines": 0.710, "bolivia": 0.698,
    "india": 0.644, "ghana": 0.602, "kenya": 0.601,
    "cambodia": 0.600, "bangladesh": 0.670, "pakistan": 0.544,
    "nigeria": 0.548, "myanmar": 0.585, "burma": 0.585,
    "ethiopia": 0.492, "congo dr": 0.479, "afghanistan": 0.462,
    "sudan": 0.516, "haiti": 0.535, "yemen": 0.424,
    "chad": 0.394, "niger": 0.394, "south sudan": 0.381,
    "central african republic": 0.387, "somalia": 0.380,
    "sierra leone": 0.477, "mali": 0.410, "burkina faso": 0.438,
    "mozambique": 0.461, "madagascar": 0.421, "malawi": 0.508,
    "tanzania": 0.532, "uganda": 0.550, "rwanda": 0.548,
    "senegal": 0.517, "nepal": 0.601, "iraq": 0.686,
    "iran": 0.780, "jordan": 0.736, "lebanon": 0.723,
    "jamaica": 0.709, "cuba": 0.764, "dominican republic": 0.766,
    "guatemala": 0.627, "honduras": 0.621, "el salvador": 0.675,
    "nicaragua": 0.667, "paraguay": 0.717, "venezuela": 0.699,
    "north korea": None, "libya": 0.718, "algeria": 0.745,
    "morocco": 0.698, "tunisia": 0.740, "botswana": 0.693,
    "namibia": 0.610, "zambia": 0.565, "zimbabwe": 0.550,
    "angola": 0.586, "cameroon": 0.576,
}


def safe_get(data, *keys):
    """Navigate nested dict/list safely."""
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        elif isinstance(current, list) and isinstance(key, int) and key < len(current):
            current = current[key]
        else:
            return None
        if current is None:
            return None
    return current


def extract_text(obj):
    """Extract text from a factbook field which may be a dict with 'text' key or nested."""
    if obj is None:
        return "N/A"
    if isinstance(obj, str):
        return obj
    if isinstance(obj, (int, float)):
        return str(obj)
    if isinstance(obj, dict):
        if "text" in obj:
            return str(obj["text"])
        parts = []
        for k, v in obj.items():
            val = extract_text(v)
            if val != "N/A":
                parts.append(f"{k}: {val}")
        return "; ".join(parts) if parts else "N/A"
    if isinstance(obj, list):
        return "; ".join(extract_text(item) for item in obj)
    return str(obj)


def fetch_country_data(country_name):
    """Fetch all worksheet fields for a given country."""
    key = country_name.lower().strip()
    if key not in COUNTRY_MAP:
        # Try partial match
        matches = [k for k in COUNTRY_MAP if key in k or k in key]
        if matches:
            key = matches[0]
        else:
            print(f"ERROR: Country '{country_name}' not found in mapping.")
            print(f"Available countries (partial): {', '.join(sorted(list(COUNTRY_MAP.keys())[:20]))}...")
            sys.exit(1)

    region, code = COUNTRY_MAP[key]
    url = f"https://raw.githubusercontent.com/factbook/factbook.json/master/{region}/{code}.json"
    print(f"Fetching data from: {url}")

    resp = requests.get(url, timeout=30)
    if resp.status_code != 200:
        print(f"ERROR: Failed to fetch data (HTTP {resp.status_code})")
        sys.exit(1)

    raw = resp.json()

    geo = raw.get("Geography", {})
    people = raw.get("People and Society", {})
    gov = raw.get("Government", {})
    econ = raw.get("Economy", {})
    mil = raw.get("Military and Security", {})

    result = {
        "country": country_name.title(),
        "category_geography": {
            "Natural Resources": extract_text(safe_get(geo, "Natural resources")),
            "Land Use": extract_text(safe_get(geo, "Land use")),
        },
        "category_people": {
            "Population": extract_text(safe_get(people, "Population", "total")),
            "Ethnic Groups": extract_text(safe_get(people, "Ethnic groups")),
            "Population Pyramid (Age Structure)": extract_text(safe_get(people, "Age structure")),
            "Population Growth": extract_text(safe_get(people, "Population growth rate")),
            "Maternal Mortality Rate": extract_text(safe_get(people, "Maternal mortality ratio")),
            "Infant Mortality Rate": extract_text(safe_get(people, "Infant mortality rate")),
            "Life Expectancy at Birth": extract_text(safe_get(people, "Life expectancy at birth")),
            "Physician Density": extract_text(safe_get(people, "Physician density")),
            "Educational Expenditures": extract_text(safe_get(people, "Education expenditures")),
            "School Life Expectancy": extract_text(safe_get(people, "School life expectancy (primary to tertiary education)")),
        },
        "category_government": {
            "Type": extract_text(safe_get(gov, "Government type")),
            "Suffrage": extract_text(safe_get(gov, "Suffrage")),
        },
        "category_economy": {
            "Real GDP": extract_text(safe_get(econ, "Real GDP (purchasing power parity)")),
            "Real GDP Growth Rate": extract_text(safe_get(econ, "Real GDP growth rate")),
            "Real GDP per Capita": extract_text(safe_get(econ, "Real GDP per capita")),
            "Inflation Rate": extract_text(safe_get(econ, "Inflation rate (consumer prices)")),
            "GDP by Sector": extract_text(safe_get(econ, "GDP - composition, by sector of origin")),
            "GDP Composition by End Use": extract_text(safe_get(econ, "GDP - composition, by end use")),
            "Labor Force": extract_text(safe_get(econ, "Labor force")),
            "Unemployment %": extract_text(safe_get(econ, "Unemployment rate")),
            "Population below the Poverty Line": extract_text(safe_get(econ, "Population below poverty line")),
            "GINI Index": extract_text(safe_get(econ, "Gini Index coefficient - distribution of family income")),
            "Budget Surplus/Deficit": extract_text(safe_get(econ, "Budget surplus (+) or deficit (-)")),
            "Current Account Balance": extract_text(safe_get(econ, "Current account balance")),
            "Export $$$": extract_text(safe_get(econ, "Exports")),
            "Export Partners": extract_text(safe_get(econ, "Exports - partners")),
            "Export Commodities": extract_text(safe_get(econ, "Exports - commodities")),
            "Import $$$": extract_text(safe_get(econ, "Imports")),
            "Import Partners": extract_text(safe_get(econ, "Imports - partners")),
            "Import Commodities": extract_text(safe_get(econ, "Imports - commodities")),
            "Exchange Rate with USA": extract_text(safe_get(econ, "Exchange rates")),
        },
        "category_military": {
            "Military Expenditure": extract_text(safe_get(mil, "Military expenditures")),
        },
        "category_different_source": {
            "HDI: Human Development Index": HDI_VALUES.get(key, "N/A"),
            "HDI Source": "https://hdr.undp.org",
        },
    }

    # Save to .tmp
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tmp_dir = os.path.join(base_dir, ".tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    safe_name = re.sub(r'[^a-z0-9]', '_', country_name.lower().strip())
    out_path = os.path.join(tmp_dir, f"{safe_name}_data.json")

    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)

    print(f"SUCCESS: Data saved to {out_path}")
    return out_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 tools/fetch_country_data.py \"Country Name\"")
        sys.exit(1)
    fetch_country_data(sys.argv[1])

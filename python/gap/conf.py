VIZMAXDROP = 1

CHES2023DEFAULTATTVIZ = {
  'cbar_rect': [0.15, 0.6, 0.02, 0.3],
  'legend_loc': 'lower center',
  'limits': [-2, 12],
  'nudges': []
}

CHES2019DEFAULTATTVIZ = {
  'cbar_rect': [0.15, 0.6, 0.02, 0.3],
  'legend_loc': 'lower center',
  'limits': [-2, 12],
  'nudges': []
}

GPS2019DEFAULTATTVIZ = {
  'cbar_rect': [0.15, 0.6, 0.02, 0.3],
  'legend_loc': 'lower center',
  'limits': [-2, 12],
  'nudges': []
}

ATTDICT = {
    'ches2023': {
        'antielite_salience': 'Anti-elite salience',
        'energy_costs': 'energy_costs',
        'eu_position': 'EU',
        'EU_Russia': 'EU_Russia',
        'galtan': 'GAL – TAN',
        'lrecon': 'Left – Right (economic)',
        'supportUA': 'supportUA',
        'UA_EU': 'UA_EU',
        'weapons': 'weapons',
        'refugees': 'refugees',
        'Kremlin_ties': 'Kremlin_ties'
    },
    'ches2019': {
        'eu_position': 'EU',
        'eu_position_sd': 'EU (std)',
        'eu_salience': 'EU (salience)',
        'eu_dissent': 'EU (dissent)',
        'eu_blur': 'EU (blur)',
        'eu_cohesion': ' EU cohesion',
        'eu_foreign': 'EU foreign policy',
        'eu_intmark': 'EU internal market',
        'eu_budgets': 'EU economic policy',
        'eu_asylum': 'EU asylum policy',
        'lrgen': 'Left – Right',
        'lrecon': 'Left – Right (economic)',
        'lrecon_sd': 'Left – Right (economic, std)',
        'lrecon_salience': 'Left – Right (economic, salience)',
        'lrecon_dissent': 'Left – Right (economic, dissent)',
        'lrecon_blur': 'Left – Right (economic, blur)',
        'galtan': 'GAL – TAN',
        'galtan_sd': 'GAL – TAN (std)',
        'galtan_salience': 'GAL – TAN (salience)',
        'galtan_dissent': 'GAL – TAN (dissent)',
        'galtan_blur': 'GAL – TAN (blur)',
        'immigrate_policy': 'Opposition to immigration',
        'immigrate_salience': 'Immigration (salience)',
        'immigrate_dissent': 'Immigration (dissent)',
        'multiculturalism': 'Opposition to multiculturalism',
        'multicult_salience': 'Multiculturalism (salience)',
        'multicult_dissent': 'Multiculturalism (dissent)',
        'redistribution': 'Opposition to redistribution',
        'redist_salience': 'Redistribution (salience)',
        'environment': 'Economy over environment',
        'enviro_salience': 'Environment (salience)',
        'spendvtax': 'Opposition to taxation',
        'deregulation': 'Market deregulation',
        'econ_interven': 'Opposition to econ. intervention',
        'civlib_laworder': 'Order over civil liberties',
        'sociallifestyle': 'Conservative',
        'religious_principles': 'Religion',
        'ethnic_minorities': 'Opposition to rights for ethnic minorities',
        'nationalism': 'Nationalism',
        'urban_rural': 'Urban – Rural',
        'protectionism': 'Trade protectionism',
        'regions': 'Opposition to decentralization',
        'russian_interference': 'Importance of Russian interference',
        'anti_islam_rhetoric': 'Anti-Islam',
        'people_vs_elite': 'Elite – People',
        'antielite_salience': 'Anti-elite salience',
        'corrupt_salience': 'Importance of corruption',
        'members_vs_leadership': 'Members – Leadership',
    },
    'gps2019': {
        'V1': 'Expert familiarity',
        'V2': 'Party unity',
        'V3': 'Policy program specification',
        'V4_Scale': 'Left – Right',
        'V5': 'Left – Right (salience)',
        'V6_Scale': 'GAL – TAN',
        'V7': 'GAL – TAN (salience)',
        'V8_Scale': 'Populism',
        'V9': 'Populism (salience)',
        'V10': 'Opposition to immigration',
        'V11': 'Opposition to taxation',
        'V12': 'Opposition to environmental protection',
        'V13': 'Opposition to nationalism',
        'V14': 'Opposition to women’s rights',
        'V15': 'Opposition to rights for ethnic minorities',
        'V16': 'Opposition to liberal democracy',
        'V17': 'Clientelism',
        'V18': 'Politicians over people', # difficult to name
        'V19': 'Elite – People',
        'V20': 'Importance of corruption',
        'V21': 'Strongman rule',
    }
}

LOGISTICREGRESSIONS = [
    {
        'ches2019': ['lrgen', 'lrecon'],
        'gps2019': ['V4_Scale'],
        'ches2023': ['lrecon'],
        'group1': 'right',
        'group2': 'left',
    },
    {
        'ches2019': ['eu_position'],
        'gps2019': [],
        'ches2023': ['eu_position'],
        'group1': 'eurosceptic',
        'group2': 'pro_european',
    },
    {
        'ches2019': ['antielite_salience', 'people_vs_elite', 'corrupt_salience'],
        'gps2019': ['V8_Scale', 'V9', 'V18', 'V19', 'V20', 'V21'],
        'ches2023': ['antielite_salience'],
        'group1': 'populist',
        'group2': 'elite',
    },
    {
        'ches2019': ['sociallifestyle', 'galtan'],
        'gps2019': ['V6_Scale', 'V14'],
        'ches2023': ['galtan'],
        'group1': 'liberal',
        'group2': 'conservative',
    },
    {
        'ches2019': ['immigrate_policy'],
        'gps2019': ['V10'],
        'ches2023': ['refugees'],
        'group1': 'liberal_immigration',
        'group2': 'restrictive_immigration',
    },
    {
        'ches2019': ['environment', 'enviro_salience'],
        'gps2019': ['V12'],
        'ches2023': [],
        'group1': 'pro_environment',
        'group2': 'economic_focus',
    },
    {
        'ches2019': ['environment', 'enviro_salience'],
        'gps2019': ['V12'],
        'ches2023': [],
        'group1': 'pro_environment',
        'group2': 'climate_denialist',
    },
    {
        'ches2019': ['nationalism'],
        'gps2019': ['V13'],
        'ches2023': [],
        'group1': 'cosmopolitan',
        'group2': 'nationalist',
    }
]

LANGUAGES = {
    'Australia':{'languages':['en'],'marpor2020_countryname': 'Australia'},
    'Austria':{'languages':['de'],'ches2019_country': 'aus','marpor2020_countryname': 'Austria'},
    'belgium':{'languages':['de','fr','nl'],'ches2019_country': 'be','marpor2020_countryname': 'Belgium'},
    'Canada':{'languages':['en','fr'],'marpor2020_countryname': 'Canada'},
    'Denmark':{'languages':['da','de',],'ches2019_country': 'dk','marpor2020_countryname': 'Denmark'},
    'EuropeanParliament':{'languages':['ca', 'en', 'es', 'el', 'el-Latn', 'eu', 'de', 'fi', 'fr', 'ga', 'gl', 'is', 'it', 'lv', 'lb', 'nl', 'no', 'pl', 'pt', 'sv', 'sl', 'tr']},
    'Finland':{'languages':['fi','sv'],'ches2019_country': 'fin','marpor2020_countryname': 'Finland'},
    'france':{'languages':['fr'],'ches2019_country': 'fr','marpor2020_countryname': 'France'},
    'germany':{'languages':['de'],'ches2019_country': 'ge','marpor2020_countryname': 'Germany'},
    'Greece':{'languages':['el','el-Latn'],'ches2019_country': 'gr','marpor2020_countryname': 'Greece'},
    'Iceland':{'languages':['is'],'ches2019_country': 'ice','marpor2020_countryname': 'Iceland'},
    'Ireland':{'languages':['en','ga'],'ches2019_country': 'irl','marpor2020_countryname': 'Ireland'},
    'italy':{'languages':['it'],'ches2019_country': 'it','marpor2020_countryname': 'Italy'},
    'Latvia':{'languages':['lv'],'ches2019_country': 'lat','marpor2020_countryname': 'Latvia'},
    'Luxembourg':{'languages':['fr','de','lb'],'ches2019_country': 'lux','marpor2020_countryname': 'Luxembourg'},
    'Malta':{'languages':['mt','en','it'],'ches2019_country': 'mal','marpor2020_countryname': 'Malta'},
    'netherlands':{'languages':['nl','en'],'ches2019_country': 'nl','marpor2020_countryname': 'Netherlands'},
    'NewZealand':{'languages':['en'],'marpor2020_countryname': 'New Zealand'},
    'Norway':{'languages':['no'],'ches2019_country': 'nor','marpor2020_countryname': 'Norway'},
    'poland':{'languages':['pl'],'ches2019_country': 'pol','marpor2020_countryname': 'Poland'},
    'romania':{'languages':['ro']},
    'slovenia':{'languages':['sl'],'ches2019_country': 'sle','marpor2020_countryname': 'Slovenia'},
    'spain':{'languages':['es','ca','eu','gl'],'ches2019_country': 'esp','marpor2020_countryname': 'Spain'},
    'Sweden':{'languages':['sv'],'ches2019_country': 'sv','marpor2020_countryname': 'Sweden'},
    'Switzerland':{'languages':['it','fr','de'],'ches2019_country': 'swi','marpor2020_countryname': 'Switzerland'},
    'Turkey':{'languages':['tr'],'ches2019_country': 'tur','marpor2020_countryname': 'Turkey'},
    'UnitedKingdom':{'languages':['en'],'ches2019_country': 'uk','marpor2020_countryname': 'United Kingdom'},
    'UnitedStates':{'languages':['en'],'marpor2020_countryname': 'United States'},
    # Own collection
    'AustriaOwn':{'languages':['de'],'ches2019_country': 'aus','marpor2020_countryname': 'Austria'},
    'BrazilOwn':{'languages':['pt'],'marporLA2020_countryname': 'Brazil'},
    'ChileOwn':{'languages':['es'],'marporLA2020_countryname': 'Chile'},
    'FranceOwn':{'languages':['fr'],'ches2019_country': 'fr','marpor2020_countryname': 'France'},
    'GermanyOwn':{'languages':['de'],'ches2019_country': 'ge','marpor2020_countryname': 'Germany'},
    'ItalyOwn':{'languages':['it'],'ches2019_country': 'it','marpor2020_countryname': 'Italy'},
    'UKOwn':{'languages':['en'],'ches2019_country': 'uk','marpor2020_countryname': 'United Kingdom'},
    'USOwn':{'languages':['en'],'marpor2020_countryname': 'United States'},
    }
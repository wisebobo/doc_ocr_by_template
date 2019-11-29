# -*- coding:utf-8 -*-

# Default HTTP Header
HTTP_HEADERS = {
    'Content-Type': 'application/json',
    'Content-Security-Policy': "default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self'",
    'server_tokens': 'off',
    'X-Frame-Options': 'SAMEORIGIN',
    'X-Content-Type-Options': 'nosniff',
    'X-XSS-Protection': '1; mode=block',
    'charset': 'UTF-8',
    'Server': '',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'X-Requested-With, Content-Type, User-Agent',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
}

# Tencent API ID & Key (PROD)
# TENCENT_APP_ID = '2107861360'
# TENCENT_APP_KEY = 'G41slDbZ8Fl5nYHU'

# Tencent API ID & Key (DEV)
TENCENT_APP_ID = '1106852281'
TENCENT_APP_KEY = 'L9bpjMudBz6Ttmtm'

# Baidu API ID & Key (PROD)
# BAIDU_APP_ID = '11679966'
# BAIDU_API_KEY = '5Gat7D3H675YDrN1dR9Efexb'
# BAIDU_SECRET_KEY = 'GSLIKKMNhjiQhOT5jrqy2OhR6OkHwRBu'

# Baidu API ID & Key (DEV)
BAIDU_APP_ID = '11343380'
BAIDU_API_KEY = 'yVinrzkVTxoOrF2EjkvX6507'
BAIDU_SECRET_KEY = 'nTW0dApPb77pqCZTHjGCsvllXRrkpPYS'

# JD API ID & Key (DEV)
JD_APP_ID = 'd3e558705a1c093a369e9671065483bd'
JD_APP_KEY = '3e7867f567fbbbca1ec4082e6146e935'

# Face++ API ID & Key (DEV)
FACEPLUSPLUS_API_Key = '53pZ3_8e_rqi9k1_8CLFr-DDHkUaTI_o'
FACEPLUSPLUS_API_Secret = '34CHt57mkuNORei8FGf5rMMUFjzRczCX'

# Netease API ID & Key (DEV)
NETEASE_APP_ID = '100000000357'
NETEASE_API_KEY = 'Wko0J3GuV9O7Myds'

FACEPLUSPLUS_TEMPLATE = {
    '1': '1573523282', # CHN ID
    '2': '1573522004', # HK ID (New)
    '3': '1573522986', # HK ID (Old)
    '4': '1573524413', # Macau ID (New)
    '5': '1573545102', # Macau ID (Old)
    '6': '1573525004', # Macau ID Backend (MRZ)
    '7': '1573463113', # CHN TO HK/MACAU Entry CARD
    '8': '1573525290', # CHN TO HK/MACAU Entry Book
    '9': '1573525867', # CHN TO TW Entry CARD
    '10': '1573526355', # HK/MACAU TO CHN CARD (New)
    '11': '1573527072', # HK/MACAU TO CHN CARD (Old)
    '12': '1573527333', # TW TO CHN CARD (New)
    '13': '1573547758', # TW TO CHN Book (Old)
    '14': '1573549331', # AU Driver - NSW
    '15': '1573549008', # AU Driver - VIC
    '16': '1573550869', # AU Driver - ACT
    '17': '1573549818', # AU Driver - QLD
    '18': '1573549962', # AU Driver - WA
    '19': '1573550065', # AU Driver - NT
    '20': '1573550155', # AU Driver - TAS
    '21': '1573550300', # AU Driver - SA
    '22': '1573550441', # NZ Driver Licence
}

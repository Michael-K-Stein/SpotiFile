import random

__keys = [
    ('913e0bdf-1edd-47c7-87a9-a35220b6e5d0', 'AQBRFGQJBQtClUTyq7LHR77hf_cRwFjKVhisQVcHMWb7TQmkJso5xbcrIyHlDzA-qqoNhY3SSfFhPaPMRR7sCJW-KX0YSiyw8qw5kmbtsSTWasYb_-HDp40rAzlR2b2eAS32SJBRB4bna7k_CcgilB3tj4ZBNJqC'),
    ('79d7e532-9bd5-4a61-9122-6b1c9b482efe', 'AQBSvqnDCT2HcOTC0V4yGgdGAjv2elnnTDqLMZmt7pzlimjtmGtwJ0-0n5hyrC3cuYsFaxClVg6ki02r8tMo_7PD6G2Jtx8uGSyL8xWg6TrLqm-XwtKAimut1qdMwVtPVZ8cO5T-MWxI-PduZ975AB17EO0vHbj4'),
    ('1541e9bc-fa60-4c0b-86fa-452e0fba304f', 'AQAda5eiTbKYEwNvHWq7afCWlfuN8eMN_vyIiTgd_28Jde7LtqBArq8ADDYivY2_39LgNfegFWQj21bURknirP3KAuiiVHpnotbmwSxhrbLQBOmjaSx1S_PEKpaPkFwvl288XY-W9It3PtFNve3RnnV-VnFji_Y'),
]

pepper = random.randint(0, len(__keys) - 1)

def get_sp_key():
    return __keys[pepper][0]


def get_sp_dc():
    return __keys[pepper][1]

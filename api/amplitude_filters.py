"""
Módulo que contiene funciones para generar filtros de Amplitude.
Proporciona utilidades para generar filtros por país, tipo de tráfico, dispositivo y otros parámetros
necesarios para consultas en Amplitude.
"""

def get_culture_digital_filter(country_code):
    switch = {
        "CL": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["cl", "CL", "cL", "Cl", "es-CL", "CHILE", "es-cl"]
        },
        "AR": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["ar", "AR", "aR", "Ar", "es-AR", "ARGENTINA", "es-ar"]
        },
        "PE": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["pe", "PE", "pE", "Pe", "es-PE", "PERU", "es-pe"]
        },
        "CO": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["co", "CO", "cO", "Co", "es-CO", "COLOMBIA", "es-co"]
        },
        "BR": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["br", "BR", "bR", "Br", "pt-BR", "BRAZIL", "pt-br"]
        },
        "UY": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["uy", "UY", "uY", "Uy", "es-UY", "URUGUAY", "es-uy"]
        },
        "PY": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["py", "PY", "pY", "Py", "es-PY", "PARAGUAY", "es-py"]
        },
        "EC": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["ec", "EC", "eC", "Ec", "es-EC", "ECUADOR", "es-ec"]
        },
        "US": {
            "subprop_type": "event",
            "subprop_key": "culture",
            "subprop_op": "is",
            "subprop_value": ["us", "US", "uS", "Us", "en-US", "UNITED STATES", "en-us"]
        },
        
        # "Others": {
        #     "subprop_type": "event",
        #     "subprop_key": "culture",
        #     "subprop_op": "is not",
        #     "subprop_value": ["cl", "CL", "cL", "Cl", "es-CL", "CHILE", "es-cl", "ar", "AR", "aR", "Ar", "es-AR", "ARGENTINA", "es-ar", "pe", "PE", "pE", "Pe", "es-PE", "PERU", "es-pe", "co", "CO", "cO", "Co", "es-CO", "COLOMBIA", "es-co", "br", "BR", "bR", "Br", "pt-BR", "BRAZIL", "pt-br", "uy", "UY", "uY", "Uy", "es-UY", "URUGUAY", "es-uy", "py", "PY", "pY", "Py", "es-PY", "PARAGUAY", "es-py", "ec", "EC", "eC", "Ec", "es-EC", "ECUADOR", "es-ec", "us", "US", "uS", "Us", "en-US", "UNITED STATES", "en-us"]
        # }
    }
    return switch.get(country_code, "")


def get_traffic_type(traffic_type):    
    switch = {
        'Pagado': {
                'group_type': 'User',
                'subprop_key': 'acce9394-0a0d-4285-95a8-c5c1678ddc86',
                'subprop_op': 'is',
                'subprop_value': [
                        'Display',
                        'Paid Search',
                ],
                'subprop_type': 'derivedV2',
                'subfilters': [],
        },
        'Promoted': {
                'group_type': 'User',
                'subprop_key': 'acce9394-0a0d-4285-95a8-c5c1678ddc86',
                'subprop_op': 'is',
                'subprop_value': [
                    "Affiliates",
                    "Email",
                    "Metasearch",
                    "Social",
                    "Web Push"
                ],
                'subprop_type': 'derivedV2',
                'subfilters': [],
        },        
        'Organico': {
                'group_type': 'User',
                'subprop_key': 'acce9394-0a0d-4285-95a8-c5c1678ddc86',
                'subprop_op': 'is',
                'subprop_value': [
                    "Direct", 
                    "Organic Search",
                    "Referral"
                ],
                'subprop_type': 'derivedV2',
                'subfilters': [],
        },
    }
    return switch.get(traffic_type, [])

def get_DB_filter():    
    return {
        "subprop_type": "event",
        "subprop_key": "flow_type",
        "subprop_op": "is",
        "subprop_value": ["DB"]
    }

def get_device_type(device):    
    switch = {
        'mobile': {
            'group_type': 'User',
            'subprop_key': 'device_type',
            'subprop_op': 'is',
            'subprop_value': [
                'Android',
                'Apple iPhone',
            ],
            'subprop_type': 'user',
            'subfilters': [],
        },
        'desktop': {
            'group_type': 'User',
            'subprop_key': 'device_type',
            'subprop_op': 'is not',
            'subprop_value': [
                'Android',
                'Apple iPhone',
            ],
            'subprop_type': 'user',
            'subfilters': [],
        },
    }
    return switch.get(device, [])

def get_filters_culture_device():
    cultures = [
        "CL", "AR", "PE", "CO", "BR", 
        "UY", "PY", "EC", "US"
    ]
    devices = ['desktop', 'mobile']
    return [(culture, device) for culture in cultures for device in devices]

def get_filters_culture_device_traffic_type():
    cultures = [
        "CL", "AR", "PE", "CO", "BR", 
        "UY", "PY", "EC", "US", # quitamos others
    ]
    devices = ['desktop', 'mobile']
    traffic_types = ['Pagado', 'Organico', 'Promoted']
    return [(culture, device, traffic_type) 
            for culture in cultures 
            for device in devices 
            for traffic_type in traffic_types] 
    
def get_cultures():
    return [
        "CL", "AR", "PE", "CO", "BR", 
        "UY", "PY", "EC", "US", # quitamos others
    ]
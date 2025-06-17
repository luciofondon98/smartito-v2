"""
Módulo que contiene funciones para obtener eventos de Amplitude.
Proporciona utilidades para consultar diferentes tipos de eventos y métricas
a través de la API de Amplitude.
"""
import pandas as pd
import json
import requests
from requests.auth import HTTPBasicAuth
from amplitude_filters import (
    get_device_type,
    get_traffic_type,
    get_culture_digital_filter,
    get_DB_filter
)

# Obtener el tiempo de compra de un funnel (la convención ahora es tener desde el Home o Flights)
def get_TTC_client_journey(api_key, secret_key, start_date, end_date, culture, device, conversion_window_seconds=86400):
    url = 'https://amplitude.com/api/2/funnels'

    # Define event filters based on culture, device, and traffic type
    events_filters = {
        'ce:Sum Homepage + Promo + Everymundo': [
            get_culture_digital_filter(culture),
            get_device_type(device),
        ],
        'flight_dom_loaded_flight': [
            get_culture_digital_filter(culture),
            get_device_type(device),
        ],
        'payment_confirmation_loaded': [
            # get_country_name(culture), 
            get_culture_digital_filter(culture), get_device_type(device)],
    }

    # Create JSON payload for events
    event_filters_grouped = [
        {"event_type": "ce:Sum Homepage + Promo + Everymundo", 'filters': events_filters['ce:Sum Homepage + Promo + Everymundo'], 'group_by': []},
        {"event_type": "flight_dom_loaded_flight", 'filters': events_filters['flight_dom_loaded_flight'], 'group_by': []},
        {"event_type": "payment_confirmation_loaded", 'filters': events_filters['payment_confirmation_loaded'], 'group_by': []}
    ]

    # Define request parameters
    params = {
        'e': [json.dumps(event) for event in event_filters_grouped],
        'start': start_date.replace('-', ''),
        'end': end_date.replace('-', ''),
        'cs': conversion_window_seconds  # Optional. The conversion window in seconds. Defaults to 2,592,000 (30 days).
    }

    # Define request headers
    headers = {
        'Authorization': f'Basic {api_key}:{secret_key}'
    }

    # Make the HTTP request
    response = requests.get(url, headers=headers, params=params, auth=HTTPBasicAuth(api_key, secret_key))

    # Check for errors in the response
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")

    # Return the JSON response
    return response.json()



def get_api_events_segment_data(start_date, end_date, api_key, secret_key):
    """
    Realiza una llamada a la API de Amplitude para obtener datos de eventos
    
    Parameters
    ----------
    start_date : str
        La fecha de inicio en formato YYYY-MM-DD.
    end_date : str
        La fecha de fin en formato YYYY-MM-DD.
    api_key : str
        La clave de API para la autenticación en la API de Amplitude.
    secret_key : str
        La clave secreta para la autenticación en la API de Amplitude.
         
    Returns
    -------
    dict
        Un diccionario que representa los datos obtenidos de la API de Amplitude.
    """
    url = 'https://amplitude.com/api/2/events/segmentation'

    event_filter = {
        "event_type": "flight_dom_loaded_flight",
        "group_by": [{"type": "event", "value": "route"}] 

    }

    
    params = {
        'e': json.dumps(event_filter),
        'start': str(start_date).replace('-',''),
        'end': str(end_date).replace('-',''),
        'limit': 20000,
        'i': -3600000 # -> esto es para sacar la data por hora
    }

    headers = {'Content-Type': 'application/json'}
    auth = (api_key, secret_key)

    response = requests.get(url, headers=headers, params=params, auth=auth, verify=False)

    return json.loads(response.text)

def get_data_looks_per_route(dates_list, hour_filter=23, return_per_hour=False):  #el hour filter debe ser HASTA la hora X, ej hour_filter=23 filtra todo el día
    """
    Obtiene los datos de la API de Amplitude usando la función get_api_events_segment_data() y luego 
    procesa los datos para entregarlos en un formato adecuado para el reporte de Looks por ruta
    
    Parameters
    ----------
    dates_list : list
        Una lista con las fechas que se quieren obtener en el reporte.
    hour_filter (optional) : int
        Parámetro opcional. La hora de filtro hasta la que se quiere sacar el reporte. Toma valores desde 0 a 23 incluyendo el 23. El filtro de hora se hace desde el hour_filter + 1.
        Por ejemplo, si hour_filter = 2, entonces se filtra la data hasta las 3 de la mañana dado que se obtienen las horas de las 00:00 - 00:59, 01:00 - 01:59 y 02:00 - 02:59.
    return_per_hour : bool
        Parámetro opcional. Indica si es que, además de retornarse el dataframe con las looks por RTMarket por día, 
        además se entregue un dataframe adicional que entrega esta data pero aperturada por hora.

    NOTA: Todas las horas a las que se filtran son en hora Chile.
         
    Returns
    -------
    df
        Un dataframe en donde cada registro indica las looks del RTMarket de todas las rutas
        que se han cotizado según las fechas y horas especificadas
    """
    df = pd.DataFrame(columns=['Date', 'Origin', 'Destination', 'Looks'])

    for date in dates_list:
        data = get_api_events_segment_data(date,
                                               str(date).replace('-',''),
                                               api_key,
                                               secret_key)
        
        looks_per_hour = data['data']['series']
        dates_per_hour = data['data']['xValues']
        routes = [element[1] for element in data['data']['seriesLabels']]
        
        for looks, route in zip(looks_per_hour, routes):
            if 'n/a' not in route:
                i = 0
                for date, look in zip(dates_per_hour, looks):
                    if i > hour_filter:
                        break
                    else:
                        origin = route.split('-')[0]
                        destination  = route.split('-')[1]
                        df = df._append({'Date': date, 
                                        'Origin': origin, 
                                        'Destination': destination,
                                        'Looks': look
                                    }, ignore_index=True)
                    i += 1
    
    # Se deja a nivel RT_Market (agrega la idea y vuelta 1 sola -> ANF-SCL y SCL-ANF queda ANFSCL)
    df['Origin'] = df['Origin'].replace({'AEP': 'BUE', 'EZE': 'BUE', 'GIG': 'RIO'}, regex=True)
    df['Destination'] = df['Destination'].replace({'AEP': 'BUE', 'EZE': 'BUE', 'GIG': 'RIO'}, regex=True)

    # Creamos el RTMarket de manera vectorizada
    df['RTMarket'] = np.where(df['Origin'] < df['Destination'],
                                     df['Origin'] + df['Destination'],
                                     df['Destination'] + df['Origin'])
 
    # preguntamos si se quiere retornar por hora o no
    if return_per_hour:
        df_per_hour = df.copy()
    
        # Transformamos a YYYY-MM-DD
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        
        df_final = df.groupby(['Date', 'RTMarket']).sum()
        df_final = df_final.reset_index()
        # df_final = df_final[['Date', 'RTMarket', 'Looks']]

        return df_final, df_per_hour
    else:
        # Transformamos a YYYY-MM-DD
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')

        # agrupamos las looks
        df_final = df.groupby(['Date', 'RTMarket']).sum()
        df_final = df_final.reset_index()
        # df_final = df_final[['Date', 'RTMarket', 'Looks']]

        return df_final


# # Ejemplo de uso
# Agregar las fechas que se quieren sacar en la variable dates_list en formato YYYY-MM-DD y cambiar la hora en la variable hour_filter. 
# La variable puede tomar valores de 0 a 23. Por ejemplo, si deja como valor el 0, tomará solo las horas de las 00:00 a las 01:00 hora CL. 
# Está 23 por defecto en la función, para que tome siempre todo el día si es que no se le entrega un parámetro


# # Generate a list of dates between start and end date
# start_date = '2025-04-08'
# end_date = '2025-04-08'

# dates_list = pd.date_range(start=start_date, end=end_date, freq='D').strftime('%Y-%m-%d').tolist()

# df_looks, df_looks_per_hour = get_data_looks_per_route(dates_list, return_per_hour=True)




from pprint import pprint

import requests

PROPERTIES_NAMES = (
    'Temperature (K)',
    'Pressure (bar)',
    'Density (kg/m3)',
    'Volume (m3/kg)',
    'Internal Energy (kJ/kg)',
    'Enthalpy (kJ/kg)',
    'Entropy (kJ/(kg*K))',
    'Cv (kJ/(kg*K))',
    'Cp (kJ/(kg*K))',
    'Sound_speed m/s',
    'Joule_Thomson (K/bar)',
    'Viscosity (uPa*s)',
    'Thermal Conductivity (W/(m*k))',
    'Phase',
)


def get_fluid_properties(cas_number, pressure, temperature):
    url = (
        f'https://webbook.nist.gov/cgi/fluid.cgi?Action=Data&Wide=on&ID='
        f'{cas_number}&Type=IsoTherm&Digits=12&PLow={pressure}'
        f'&PHigh={pressure}&PInc=1&T={temperature}'
        '&RefState=DEF&TUnit=K&PUnit=bar&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit='
        'm%2Fs&VisUnit=uPa*s&STUnit=N%2Fm'
    )
    response = requests.get(url).text.split()
    thermodynamic_properties = dict()
    property_values = []
    for index in range(30, len(response)):
        if response[index][0].isdigit():
            property_values.append(float(response[index]))
        else:
            property_values.append(response[index])
    for index in range(len(PROPERTIES_NAMES)):
        thermodynamic_properties.update(
            {PROPERTIES_NAMES[index]: property_values[index]}
        )
    return thermodynamic_properties


cas_number = 'C7732185'
pressure = '1.013'
temperature = '273.15'

url = (
        f'https://webbook.nist.gov/cgi/fluid.cgi?Action=Data&Wide=on&ID='
        f'{cas_number}&Type=IsoTherm&Digits=12&PLow={pressure}'
        f'&PHigh={pressure}&PInc=1&T={temperature}'
        '&RefState=DEF&TUnit=K&PUnit=bar&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit='
        'm%2Fs&VisUnit=uPa*s&STUnit=N%2Fm'
    )

response = requests.get(url).text.split()
pprint(response)

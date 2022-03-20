from pprint import pprint

import requests

PROPERTY_NAMES = (
    'Temperature',
    'Pressure',
    'Density',
    'Volume',
    'Internal Energy',
    'Enthalpy',
    'Entropy',
    'Cv',
    'Cp',
    'Sound_speed',
    'Joule_Thomson',
    'Viscosity',
    'Thermal Conductivity',
    'Phase',
)

gas_case = "C7727379"
pressure = input('Введите значение давления в барах:\n')
Temperature = input('Введите значение температуры в кельвинах:\n')

url = (
    f'https://webbook.nist.gov/cgi/fluid.cgi?Action=Data&Wide=on&ID='
    f'{gas_case}&Type=IsoTherm&Digits=12&PLow={pressure}'
    f'&PHigh={pressure}&PInc=1&T={Temperature}'
    '&RefState=DEF&TUnit=K&PUnit=bar&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit='
    'm%2Fs&VisUnit=uPa*s&STUnit=N%2Fm'
)

response = requests.get(url).text
response_list = response.split()

property_values = []
for index in range(30, len(response_list)):
    if response_list[index][0].isdigit():
        property_values.append(float(response_list[index]))
    else:
        property_values.append(response_list[index])


thermodynamic_properties = dict()

for index in range(len(PROPERTY_NAMES)):
    thermodynamic_properties.update(
        {PROPERTY_NAMES[index]: property_values[index]}
    )

pprint(thermodynamic_properties)

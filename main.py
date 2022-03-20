import sys

import requests

CAS_REGISTRY_NUMBERS = {
    'азот': 'C7727379',
    'кислород': 'C7782447',
    'аргон': 'C7440371',
    'метан': 'C74828',
    'углекислота': 'C124389',
    'водород': 'C1333740',
    'вода': 'C7732185',
    'пропан': 'C74986',
    'бутан': 'C106978',
    'гелий': 'C7440597',
}

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


def get_fluid_cas_number(fluid):
    fluid_cas_number = CAS_REGISTRY_NUMBERS.get(fluid)
    if not fluid_cas_number:
        print('Рабочая среда не найдена. Программа принудительно остановлена.')
        sys.exit()
    return fluid_cas_number


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


def get_normal_properties(cas_number):
    normal_pressure = 1.013
    normal_temperature = 273.15
    return get_fluid_properties(cas_number, normal_pressure, normal_temperature)


def main():
    print(f'Вот какие рабочие среды я знаю:', end=' ')
    for key in CAS_REGISTRY_NUMBERS.keys():
        print(key, end=', ')
    print()
    fluid = input('Введите название рабочей среды: ').lower()
    cas_number = get_fluid_cas_number(fluid)
    pressure = input('Введите значение давления (бар): ')
    temperature_inlet = input('Введите значение температуры на входе (K): ')
    temperature_outlet = input('Введите значение температуры на выходе (K): ')
    normal_flow_rate = float(
        input('Введите расход при нормальных условиях (нм3/ч): ')
    )
    properties_inlet = get_fluid_properties(
        cas_number,
        pressure,
        temperature_inlet,
    )
    properties_outlet = get_fluid_properties(
        cas_number,
        pressure,
        temperature_outlet,
    )
    enthalpy_inlet = properties_inlet.get('Enthalpy (kJ/kg)')
    enthalpy_outlet = properties_outlet.get('Enthalpy (kJ/kg)')
    normal_density = get_normal_properties(cas_number).get('Density (kg/m3)')
    mass_flow_rate = normal_flow_rate * normal_density
    electric_power = round(
        (mass_flow_rate * (enthalpy_outlet - enthalpy_inlet)) / (3.6 * 1000), 1
    )
    print(f'Необходимая мощность равна {electric_power} кВт.')
    print(f'Мощность с запасом 1.3 равна {round(electric_power * 1.3, 1)} кВт.')


if __name__ == '__main__':
    main()

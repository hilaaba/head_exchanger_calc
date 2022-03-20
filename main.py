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

NORMAL_PRESSURE = 1.013
NORMAL_TEMPERATURE = 273.15


def get_fluid_cas_number():
    fluid = input('Введите название рабочей среды: ').lower()
    fluid_cas_number = CAS_REGISTRY_NUMBERS.get(fluid)
    while fluid_cas_number is None:
        fluid = input('Рабочая среда не найдена. Повторите ввод: ').lower()
        fluid_cas_number = CAS_REGISTRY_NUMBERS.get(fluid)
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


def calculate_enthalpy_difference(cas_number, pressure, temperature_inlet,
                                  temperature_outlet):
    enthalpy_inlet = get_fluid_properties(
        cas_number,
        pressure,
        temperature_inlet,
    ).get('Enthalpy')
    enthalpy_outlet = get_fluid_properties(
        cas_number,
        pressure,
        temperature_outlet,
    ).get('Enthalpy')
    return enthalpy_outlet - enthalpy_inlet


def main():
    print(f'Вот какие рабочие среды я знаю:', end=' ')
    print(*CAS_REGISTRY_NUMBERS.keys(), sep=', ')
    cas_number = get_fluid_cas_number()
    pressure = input('Введите значение давления (бар): ')
    temperature_inlet = input('Введите значение температуры на входе (K): ')
    temperature_outlet = input('Введите значение температуры на выходе (K): ')
    normal_flow_rate = float(
        input('Введите расход при нормальных условиях (нм3/ч): ')
    )
    normal_density = get_fluid_properties(
        cas_number,
        NORMAL_PRESSURE,
        NORMAL_TEMPERATURE,
    ).get('Density')
    mass_flow_rate = normal_flow_rate * normal_density
    enthalpy_difference = calculate_enthalpy_difference(
        cas_number,
        pressure,
        temperature_inlet,
        temperature_outlet
    )
    electric_power = round(
        mass_flow_rate * enthalpy_difference / 3600, 1
    )
    print(f'Необходимая мощность нагревателя равна {electric_power} кВт.')
    print(f'Мощность с запасом 30% равна {round(electric_power * 1.3, 1)} кВт.')


if __name__ == '__main__':
    main()

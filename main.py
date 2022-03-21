import requests
from math import pi

CAS_REGISTRY_NUMBERS = {
    'азот': 'C7727379',
    'кислород': 'C7782447',
    'аргон': 'C7440371',
    'метан': 'C74828',
    'углекислота': 'C124389',
    'водород': 'C1333740',
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

DIAMETER_NOMINAL = (
    2.5, 3, 4, 5, 6, 10, 15, 20, 25, 32, 40, 50, 63, 80, 100,
    125, 150, 200, 250, 300, 350, 400, 450, 500, 600, 700, 800, 900, 1000,
    1200, 1400, 1600, 1800, 2000, 2200, 2400, 2800, 3000, 3400, 4000,
)

LIQUID_VELOCITY = 3
GAS_VELOCITY = 20

NORMAL_PRESSURE = 1.013
NORMAL_TEMPERATURE = 273.15
SECOND_IN_HOUR = 3600
MM_IN_M = 1000


def is_number(number):
    """
    Проверка на число.
    """
    while True:
        try:
            float(number)
            return number
        except ValueError:
            number = input('Неправильный ввод. Введите заново: ')


def is_true(answer):
    """
    Булево значение ответа.
    """
    while True:
        if answer.lower() in ('да', 'yes'):
            return True
        elif answer.lower() in ('нет', 'no'):
            return False
        else:
            answer = input('Неправильный ввод. Введите заново: ')


def get_fluid_cas_number(fluid):
    """
    Получение уникального численного идентификатора
    химических соединений (СAS).
    """
    fluid_cas_number = CAS_REGISTRY_NUMBERS.get(fluid)
    while fluid_cas_number is None:
        fluid = input('Рабочая среда не найдена. Повторите ввод: ').lower()
        fluid_cas_number = CAS_REGISTRY_NUMBERS.get(fluid)
    return fluid_cas_number


def get_fluid_properties(cas_number, pressure, temperature):
    """
    Получение термодинамических свойств рабочей жидкости.
    """
    url = (
        f'https://webbook.nist.gov/cgi/fluid.cgi?Action=Data&Wide=on&ID='
        f'{cas_number}&Type=IsoTherm&Digits=12&PLow={pressure}'
        f'&PHigh={pressure}&PInc=1&T={temperature}'
        '&RefState=DEF&TUnit=K&PUnit=bar&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit='
        'm%2Fs&VisUnit=uPa*s&STUnit=N%2Fm'
    )
    try:
        # Запрос сразу преобразуем в список из строк.
        response = requests.get(url).text.split()
        # В запросе значения параметров начинаются с 30.
        # добавим все значения в property_values.
        property_values = list(map(float, response[30:-1:1]))
        # Последним в списке идет фазовое состояние. Просто добавим его.
        property_values.append(response[-1])
        # Создадим словарь с термодинамическими свойствами.
        thermodynamic_properties = dict()
        for index in range(len(PROPERTIES_NAMES)):
            thermodynamic_properties.update({PROPERTIES_NAMES[index]: property_values[index]})
        return thermodynamic_properties
    except Exception as error:
        print(f'Произошла следующая ошибка: {error}')


def get_mass_flow_rate(normal_density, flag):
    """
    Получение значения массового расхода в зависимости от ответа.
    """
    if flag:
        normal_flow_rate = float(is_number(input('Введите расход при нормальных условиях (нм3/ч): ')))
        return normal_flow_rate * normal_density
    return float(is_number(input('Введите массовый расход (кг/ч): ')))


def get_temperature(flag, pipe_branch):
    """
    Получение значения температуры в зависимости от ответа.
    """
    if flag:
        return str(
            float(is_number(input(f'Введите значение температуры на {pipe_branch}е (°С): '))) + NORMAL_TEMPERATURE
        )
    return is_number(input(f'Введите значение температуры на {pipe_branch}е (K): '))


def calc_electric_power(mass_flow_rate, enthalpy_difference):
    """
    Расчет электрической мощности нагревателя.
    """
    return round(mass_flow_rate * enthalpy_difference / SECOND_IN_HOUR, 1)


def get_nominal_diameter(mass_flow_rate, density, phase):
    """
    Получение значения номинального диаметра для патрубка нагревателя.
    """
    velocity = LIQUID_VELOCITY if phase == 'liquid' else GAS_VELOCITY
    cross_sectional_area = mass_flow_rate / (velocity * density) * MM_IN_M ** 2 / SECOND_IN_HOUR
    diameter = (4 * cross_sectional_area / pi) ** 0.5
    for index in range(len(DIAMETER_NOMINAL)):
        if DIAMETER_NOMINAL[index] < diameter < DIAMETER_NOMINAL[index + 1]:
            return DIAMETER_NOMINAL[index + 1]


def calc_velocity(diameter, mass_flow_rate, density):
    """
    Расчет скорости потока.
    """
    cross_sectional_area = pi * diameter ** 2 / 4 / MM_IN_M ** 2
    volumetric_flow_rate = mass_flow_rate / density
    velocity = volumetric_flow_rate / (cross_sectional_area * SECOND_IN_HOUR)
    return round(velocity, 1)


def main():
    """
    Главная функция.
    """
    print(f'Вот какие рабочие среды я знаю:', end=' ')
    print(*CAS_REGISTRY_NUMBERS.keys(), sep=', ')

    fluid = input('Введите название рабочей среды: ').lower()
    cas_number = get_fluid_cas_number(fluid)

    normal_thermodynamic_properties = get_fluid_properties(cas_number, NORMAL_PRESSURE, NORMAL_TEMPERATURE)
    normal_density = normal_thermodynamic_properties.get('Density')

    pressure = is_number(input('Введите значение давления (бар): '))

    flag = is_true(input('Температура в Цельсиях? (да/нет): '))
    temperature_inlet = get_temperature(flag, 'вход')
    thermodynamic_properties_inlet = get_fluid_properties(cas_number, pressure, temperature_inlet)
    temperature_outlet = get_temperature(flag, 'выход')
    thermodynamic_properties_outlet = get_fluid_properties(cas_number, pressure, temperature_outlet)
    density_outlet = thermodynamic_properties_outlet.get('Density')
    phase_outlet = thermodynamic_properties_outlet.get('Phase')

    flag = is_true(input('Значение расхода при нормальных условиях? (да/нет): '))
    mass_flow_rate = get_mass_flow_rate(normal_density, flag)

    enthalpy_inlet = thermodynamic_properties_inlet.get('Enthalpy')
    enthalpy_outlet = thermodynamic_properties_outlet.get('Enthalpy')
    enthalpy_difference = enthalpy_outlet - enthalpy_inlet

    electric_power = calc_electric_power(mass_flow_rate, enthalpy_difference)
    electric_power_30 = round(electric_power * 1.3, 1)
    nominal_diameter = get_nominal_diameter(mass_flow_rate, density_outlet, phase_outlet)
    velocity = calc_velocity(nominal_diameter, mass_flow_rate, density_outlet)
    print(f'Необходимая мощность нагревателя равна: {electric_power} кВт.')
    print(f'Мощность с запасом 30% равна: {electric_power_30} кВт.')
    print(f'Номинальный диаметр патрубка: DN{nominal_diameter}')
    print(f'Скорость газа на выходе: {velocity} м/с.')
    input('Чтобы выйти нажмите Enter')


if __name__ == '__main__':
    main()

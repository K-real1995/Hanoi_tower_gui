import PySimpleGUI as sg
import copy
import re
import math

HOME_RODS = {1, 8}

CANVAS_HEIGHT = 300
CANVAS_WIDTH = 1000


class Disk:
    def __init__(self, width, color):
        self.width = width
        self.color = color


# метод находит оптимальный временный штевень для данного перемещения
def findOptimalTmpRod(start_rod, goal_rod):
    direction = int(goal_rod - start_rod) / (math.fabs(goal_rod - start_rod))
    if start_rod in HOME_RODS:
        if math.fabs(goal_rod - start_rod) > 1:
            return start_rod + direction
        else:
            return start_rod + 2 * direction
    return start_rod - direction


# создает инструкцию для одного простого одиночного перемещения
def createSingleInstruction(start_rod, goal_rod):
    return int(start_rod), int(goal_rod)


# создает инструкцию из одного или нескольких последовательных ходов
def createSimpleInstruction(start_rod, goal_rod):
    instruction = list()
    # определение знака направления. Слева направо: +; Справа налево -;
    direction = int((goal_rod - start_rod) / math.fabs(goal_rod - start_rod))
    if start_rod in HOME_RODS and math.fabs(goal_rod - start_rod) != 1:
        tmp_goal_rod = start_rod + (2 * direction)
        instruction.append(createSingleInstruction(start_rod, tmp_goal_rod))
        start_rod = tmp_goal_rod
    while start_rod != goal_rod:
        tmp_goal_rod = start_rod + direction
        instruction.append(createSingleInstruction(start_rod, tmp_goal_rod))
        start_rod = tmp_goal_rod
    return instruction


# запуск алгоритма
def generate_instruction_for_one_tower(count, start_rod, goal_rod):
    instruction = list()
    if count == 1:
        instruction = instruction + createSimpleInstruction(start_rod, goal_rod)
        return instruction
    tmp = findOptimalTmpRod(start_rod, goal_rod)
    instruction = instruction + generate_instruction_for_one_tower(count - 1, start_rod, tmp)
    instruction = instruction + generate_instruction_for_one_tower(1, start_rod, goal_rod)
    instruction = instruction + generate_instruction_for_one_tower(count - 1, tmp, goal_rod)
    return instruction


# Рисует основание и штевни, возвращает словарь с координатами штевней
# indent - отступ от краев холста
def printShafts(graph, indent=20, shaft_thickness=5, shaft_amount=8, shaft_height=200, base_color="brown"):
    w, h = graph.get_size()

    # максимальный размер секции исходя из размеров холста
    # (а также максимальный размер обруча)
    section_size = (w - indent * 2) / 8

    # рисуем основу
    graph.DrawRectangle(
        (indent, indent),
        (w - indent, shaft_thickness + indent),
        fill_color=base_color,
        line_color=base_color,
        line_width=2
    )

    # словарь с координатами центра шпинделей по оси x
    shaft_dict = dict()

    # рисуем шпиндели
    for i in range(shaft_amount):
        shaft_dict[i + 1] = i * section_size + indent + section_size / 2
        graph.DrawRectangle(
            (i * section_size + indent + section_size / 2 - shaft_thickness / 2, indent),
            (i * section_size + indent + section_size / 2 + shaft_thickness / 2,
             shaft_height + indent + shaft_thickness),
            fill_color=base_color,
            line_color=base_color,
            line_width=2
        )
    return shaft_dict


# генерирует список дисков (толщину дисков) исходя из номера штевня и количеству дисков
# по формуле M * 10 + N, где M - номер штевня, N - номер диска сверху вниз
def generate_disks(shaft_num, disk_count):
    disks = list()
    for i in range(disk_count):
        disk_width = (shaft_num * 10) + i + 1
        disks.insert(0, Disk(disk_width, randomColor()))
    return disks


# Генерирует и возвращает словарь с номером штевня и списком дисков, последний диск в списке - верхний диск
def generateStartedDisksPositionData(integer_code):
    shaft_store_dict = dict()
    integer_code = [int(x) for x in str(integer_code)]
    for index, i in enumerate(integer_code):
        shaft_store_dict[index + 1] = generate_disks(index + 1, i)
    return shaft_store_dict


# изменяет данные о позиции дисков в соответствии с переданной инструкцией
def modify_data(position_data, instructions_list):
    modified_data = copy.deepcopy(position_data)
    for startRod, goalRod in instructions_list:
        current_disk = modified_data[startRod].pop(-1)
        modified_data[goalRod].append(current_disk)
    return modified_data


# рисует диски исходя из словаря хранилища дисков и штевней и словаря с координатами штевней
def render(disk_store_dict, graph, disk_height=10, shaft_bottom=25):
    graph.erase()
    shaft_coord_dict = printShafts(graph)
    for shaftI in range(len(disk_store_dict)):
        current_shaft_coord = int(shaft_coord_dict[shaftI + 1])
        for diskI in range(len(disk_store_dict[shaftI + 1])):
            disk_width = int(disk_store_dict[shaftI + 1][diskI].width) * 1.5
            first_coord = ((current_shaft_coord - (disk_width / 2)), shaft_bottom + diskI * disk_height)
            second_coord = ((current_shaft_coord + (disk_width / 2)), shaft_bottom + diskI * disk_height + disk_height)
            graph.draw_oval(
                first_coord,
                second_coord,
                fill_color=disk_store_dict[shaftI + 1][diskI].color,
                line_color="black",
                line_width=1)


def randomColor():
    import random
    rand = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (rand(), rand(), rand())


def main():
    sg.theme("DarkAmber")

    positions_data = generateStartedDisksPositionData("00000000")
    instructions_list = generate_instruction_for_one_tower(8, 1, 8)

    layout = [
        [sg.Text('Дисков в пирамиде: '), sg.Input("0", do_not_clear=True, key='-DISK_COUNT-'), sg.Button('Применить')],
        [sg.Text('', key='-ERROR_MSG-', text_color='red')],
        [sg.Graph(canvas_size=(CANVAS_WIDTH, CANVAS_HEIGHT), graph_top_right=(CANVAS_WIDTH, CANVAS_HEIGHT),
                  graph_bottom_left=(0, 0),
                  background_color="white", key='-GRAPH-')],
        [sg.Text("Ход: 0 из 0", key="-STEP_INFO-")],

        [sg.Slider(key='-STEP_SLIDER-', range=(0, 0), default_value=0, size=(90, 15), orientation='horizontal',
                   font=('Helvetica', 12), enable_events=True)],
        [sg.Button('Начало'), sg.Input("70", do_not_clear=True, key='-DISK_P1-', size=(10, 10)),
         sg.Input("16", do_not_clear=True, key='-DISK_P2-', size=(10, 10)),
         sg.Input("64", do_not_clear=True, key='-DISK_P3-', size=(10, 10)),
         sg.Input("20", do_not_clear=True, key='-DISK_P4-', size=(10, 10)), sg.Button('Окончание')],
        [sg.Button('П.1', border_width=4, pad=((90, 2), 3)), sg.Button('П.2', border_width=4, pad=((25, 2), 3)),
         sg.Button('П.3', border_width=4, pad=((25, 2), 3)), sg.Button('П.4', border_width=4, pad=((25, 2), 3))]
    ]

    window = sg.Window("Drawing GUI", layout, finalize=True)

    graph = window["-GRAPH-"]

    modify_data(positions_data, instructions_list[:0])
    render(positions_data, graph)

    # Функция перемещает слайдер на определенный процент
    def calculate_percent(value: str) -> None:
        result = round((int(value) / 100) * len(instructions_list))
        window["-STEP_SLIDER-"].Update(result, range=(0, len(instructions_list)))
        window["-STEP_INFO-"].update("Ход: " + str(result) + " из " + str(len(instructions_list)))
        modified_position_data = modify_data(positions_data, instructions_list[:result])
        render(modified_position_data, graph)

    while True:
        event, values = window.read()
        if event == "-STEP_SLIDER-":
            step = int(values["-STEP_SLIDER-"])
            window["-STEP_INFO-"].update("Ход: " + str(step) + " из " + str(len(instructions_list)))
            modified_position_data = modify_data(positions_data, instructions_list[:step])
            render(modified_position_data, graph)

        if event == "Применить":
            disk_count = str(values["-DISK_COUNT-"])
            if re.fullmatch('\d+', disk_count):
                disk_count = str(int(disk_count))
            if re.fullmatch('\d', disk_count):
                window["-ERROR_MSG-"].Update("")
            else:
                disk_count = str(0)
                window.FindElement("-ERROR_MSG-").Update("Количество дисков должно быть в пределах от 0 - 9")

            positions_data = generateStartedDisksPositionData(disk_count + "0000000")
            instructions_list = []
            if int(disk_count) > 0:
                instructions_list = generate_instruction_for_one_tower(int(disk_count), 1, 8)
            window["-STEP_SLIDER-"].Update(0, range=(0, len(instructions_list)))
            window["-STEP_INFO-"].update("Ход: " + str(0) + " из " + str(len(instructions_list)))
            render(modify_data(positions_data, instructions_list[:0]), graph)

        elif event == "Начало":
            window["-STEP_SLIDER-"].Update(0, range=(0, len(instructions_list)))
            window["-STEP_INFO-"].update("Ход: " + str(0) + " из " + str(len(instructions_list)))
            modified_position_data = modify_data(positions_data, instructions_list[:0])
            render(modified_position_data, graph)

        elif event == "П.1":
            calculate_percent(values["-DISK_P1-"])

        elif event == "П.2":
            calculate_percent(values["-DISK_P2-"])

        elif event == "П.3":
            calculate_percent(values["-DISK_P3-"])

        elif event == "П.4":
            calculate_percent(values["-DISK_P4-"])

        elif event == "Окончание":
            window["-STEP_SLIDER-"].Update(len(instructions_list), range=(0, len(instructions_list)))
            window["-STEP_INFO-"].update("Ход: " + str(len(instructions_list)) + " из " + str(len(instructions_list)))
            modified_position_data = modify_data(positions_data, instructions_list[:])
            render(modified_position_data, graph)

        elif event == sg.WIN_CLOSED:
            break
            window.close()


main()

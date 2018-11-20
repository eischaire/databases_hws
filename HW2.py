import postgresql as pl

# До начала работы программы предполагается, что созданы следующие таблицы:

# CREATE TABLE teachers (id_teacher SERIAL PRIMARY KEY, name_teacher TEXT, section TEXT),
#              groups (id_group TEXT PRIMARY KEY, section TEXT, n_students INT, entrance_year INT),
#              rooms (id_room SERIAL PRIMARY KEY, r_address TEXT, r_number TEXT,
#                     capacity INT, is_free TEXT),
#              subjects (id_subj SERIAL PRIMARY KEY, subj_name TEXT, section TEXT, study_year INT),
#              schedule (id_lesson SERIAL PRIMARY KEY,
#                        l_date TEXT, l_time TEXT, id_subj INT, id_room INT,
#                        id_group TEXT, id_teacher INT, n_people INT)

# я не успела заполнить БД хоть какими-то данными :(

db = pl.open('pq://postgres:postgres@localhost:5432/timetable')


def check_info(info_dictionary, table_name):
    where_condition = ' AND '.join(['{0} = {1}'.format(item, info_dictionary[item]) for item in info_dictionary])
    for item in db.query('SELECT {0} FROM {1} WHERE '.format(', '.join(info_dictionary.keys()),
                                                             table_name) + where_condition):
        for inst in item:
            print(inst)


def append_teacher():
    new_teacher = db.prepare('INSERT INTO teachers ' +
                             '(name_teacher, section) VALUES ($1, $2)')
    t_name = input('ФИО преподавателя: ')
    t_section = input('Подразделение: ')
    new_teacher(t_name, t_section)
    print('You inserted: ', check_info({'name_teacher': '\'{}\''.format(t_name),
                                        'section': '\'{}\''.format(t_section)},
                                       'teachers'), sep='\n')


def append_group():
    new_group = db.prepare('INSERT INTO groups (id_group, section, n_students, entrance_year) VALUES ($1, $2)')
    g_name = input('ID группы: ')
    g_section = input('Подразделение: ')
    g_number = int(input('Число студентов: '))
    g_entrance = int(input('Год поступления: '))
    new_group(g_name, g_section, g_number, g_entrance)
    check_info({'id_group': '\'{}\''.format(g_name),
                'section': '\'{}\''.format(g_section),
                'n_students': g_number, 'entrance_year': g_entrance}, 'groups')


def append_subject():
    new_subj = db.prepare('INSERT INTO subjects (subj_name, ' +
                          'section, study_year) VALUES ($1, $2, $3)')
    s_name = input('Название предмета: ')
    s_section = input('Подразделение: ')
    s_year = int(input('Курс: '))
    new_subj(s_name, s_section, s_year)
    check_info({'subj_name': '\'{}\''.format(s_name),
                'section': '\'{}\''.format(s_section),
                'study_year': s_year}, 'subjects')


def append_room():
    new_room = db.prepare('INSERT INTO rooms (r_address, r_number, ' +
                          'capacity, is_free) VALUES ($1, $2, $3, \'YES\')')
    r_addr = input('ID группы: ')
    r_num = input('Подразделение: ')
    r_capacity = int(input('Число студентов: '))
    new_room(r_addr, r_num, r_capacity)
    check_info({'r_address': '\'{}\''.format(r_addr),
                'r_number': '\'{}\''.format(r_num),
                'capacity': r_capacity}, 'rooms')


def append_class():
    new_class = db.prepare('INSERT INTO schedule (l_date, ' +
                           'l_time, id_subj, id_room, ' +
                           'id_group, id_teacher, n_people)) ' +
                           'VALUES ($1, $2, $3, $4, $5, $6, $7')
    import re
    l_date = input('Дата в формате ДДММГГГГ: ')
    l_time = re.sub(':', '', input('Время в 24-часовом формате: '))
    g_index = input('Enter group ID: ')
    id_subj = db.query('SELECT id_subj FROM subjects, groups WHERE subj_name = {} '.format(input('Subject name: ')) +
                       'AND subjects.year = 2018 - (SELECT DISTINCT year ' +
                       'FROM groups WHERE group_id = {})'.format(g_index))

    id_room = db.query('SELECT DISTINCT id_room FROM rooms WHERE r_address = {} '.format(input('Address: ')) +
                       'AND r_number = {}'.format(input('Room Number: ')))
    db.execute('UPDATE TABLE rooms SET is_free = \'NO\' WHERE id_room = {}'.format(id_room))
    id_teacher = db.query('SELECT DISTINCT id_teacher FROM ' +
                          'teachers WHERE teacher_name = {} '.format(input('Teacher\'s name: ')) +
                          'AND section = {}'.format(input('Section: ')))
    n_people = int(db.query('SELECT DISTINCT capacity FROM rooms WHERE id_room = {}'.format(id_room)))

    new_class(l_date, l_time, id_subj, id_room, g_index, id_teacher, n_people)
    check_info({'l_date': '\'{}\''.format(l_date), 'l_time': '\'{}\''.format(l_time),
                'id_subj': '\'{}\''.format(id_subj), 'id_room': '\'{}\''.format(id_room),
                'id_group': '\'{}\''.format(g_index),
                'id_teacher': id_teacher, 'n_people': n_people}, 'schedule')


def search_groups():
    find_schedule = db.prepare('SELECT schedule.l_time, subjects.subj_name, ' +
                               'teachers.name_teacher FROM ' +
                               '((schedule INNER JOIN subjects ON schedule.id_subj = subjects.id_subj) ' +
                               'INNER JOIN teachers ON schedule.id_teacher = teachers.id_teacher) ' +
                               'INNER JOIN groups ON schedule.id_group = groups.id_group ' +
                               'WHERE schedule.id_group = $1' +
                               'AND schedule.l_date = $2' +
                               'GROUP BY schedule.l_time ORDER BY schedule.l_time')
    find_schedule(input('Enter group ID: '), input('Enter date in format DDMMYYYY: '))


def main():
    first_choice = input('Вы хотите добавить данные в базу или посмотреть расписание? \n' +
                         'Если Вы хотите добавить данные в базу, введите 1. \n' +
                         'Если Вы хоите ввести расписание группы, введите 2. \n' +
                         'Если Вы хотите посмотреть расписание группы, введите 3.')
    if first_choice == '1':
        second_choice = input('11 - добавить преподавателя, 12 - добавить предмет, 13 - добавить аудиторию, 14 - добавить группу')
        if second_choice == '11':
            append_teacher()
            main()
        elif second_choice == '12':
            append_subject()
            main()
        elif second_choice == '13':
            append_room()
            main()
        else:
            append_group()
            main()
    elif first_choice == '2':
        append_class()
        main()
    else:
        search_groups()
        main()


main()

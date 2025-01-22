import pymysql
import config
from queries import general_queries
from queries import chairman_queries
from chairman_moves import check_list_judges
import re
import datetime
from datetime import date

async def pull_to_crew_group(user_id, groupNumber, area):
    active_comp = await general_queries.get_CompId(user_id)
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            sql = "INSERT INTO competition_group_crew (`compId`, `groupNumber`, `roundName`) VALUES (%s, %s, %s)"
            cur.execute(sql, (
                active_comp, groupNumber, area))
            conn.commit()
            return cur.lastrowid
    except:
        return -1

async def name_to_jud_id(last_name, name, compId):
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            cur.execute(f"select id, skateId from competition_judges where compId = {compId} and (lastName = '{last_name}' and firstName = '{name}')")
            ans = cur.fetchone()
            if ans is None:
                return {'id': -100, 'skateId': -100}
            else:
                if ans is None:
                    return {'id': -100, 'skateId': -100}
                else:
                    return ans
    except:
        return -1

async def pull_to_comp_group_jud(user_id, crew_id, area, have):
    gs, zgs, lin = have
    active_comp = await general_queries.get_CompId(user_id)
    ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            for judIndex in range(len(gs)):
                i = gs[judIndex].split()
                if len(i) == 2:
                    lastname, firstname = i
                else:
                    lastname = i[0]
                    firstname = ' '.join(i[1::])
                ans = await name_to_jud_id(lastname, firstname, active_comp)
                judge_id = ans['id']
                skateId = ans['skateId']
                ident = f'Гл. судья'
                sql = "INSERT INTO competition_group_judges (`crewId`, `typeId`, `ident`, `lastName`, `firstName`, `judgeId`, `skateId`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cur.execute(sql, (crew_id, 2, ident, lastname, firstname, judge_id, skateId))
                conn.commit()

            for judIndex in range(len(zgs)):
                i = zgs[judIndex].split()
                if len(i) == 2:
                    lastname, firstname = i
                else:
                    lastname = i[0]
                    firstname = ' '.join(i[1::])
                ans = await name_to_jud_id(lastname, firstname, active_comp)
                judge_id = ans['id']
                skateId = ans['skateId']
                ident = f'ЗГС'
                sql = "INSERT INTO competition_group_judges (`crewId`, `typeId`, `ident`, `lastName`, `firstName`, `judgeId`, `skateId`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cur.execute(sql, (crew_id, 1, ident, lastname, firstname, judge_id, skateId))
                conn.commit()


            for judIndex in range(len(lin)):
                i = lin[judIndex].split()
                if len(i) == 2:
                    lastname, firstname = i
                else:
                    lastname = i[0]
                    firstname = ' '.join(i[1::])
                ans = await name_to_jud_id(lastname, firstname, active_comp)
                judge_id = ans['id']
                skateId = ans['skateId']
                ident = f'{ALPHABET[judIndex]}({judIndex + 1})'
                sql = "INSERT INTO competition_group_judges (`crewId`, `typeId`, `ident`, `lastName`, `firstName`, `judgeId`, `skateId`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cur.execute(sql, (crew_id, 0, ident, lastname, firstname, judge_id, skateId))
                conn.commit()
            return 1
    except Exception as e:
        print(e)
        return -1

async def set_sex_for_judges(user_id):
    active_comp = await general_queries.get_CompId(user_id)
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            cur.execute(f"select id, firstName, lastName, SecondName from competition_judges where compId = {active_comp} and gender is NULL")
            judges = cur.fetchall()


            for jud in judges:
                name = jud['firstName'].strip()
                sex = await get_gender(name)
                if sex is not None:
                    cur.execute(f"update competition_judges set gender = {sex} where id = {jud['id']}")
                    conn.commit()
                else:
                    sql = "INSERT INTO gender_unknown (`lastName`, `firstName`, `secondName`) VALUES (%s, %s, %s)"
                    cur.execute(sql,
                                (jud['lastName'], jud['firstName'], jud['SecondName']))
                    conn.commit()
    except Exception as e:
        print(e, 2)
        return -1


async def check_gender_zgs(user_id, zgs):
    active_comp = await general_queries.get_CompId(user_id)
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            genders = []
            for jud in zgs:
                i = jud.split()
                if len(i) == 2:
                    lastname, firstname = i
                else:
                    lastname = i[0]
                    firstname = ' '.join(i[1::])
                cur.execute(f"select gender from competition_judges where compId = {active_comp} and ((firstName = '{firstname}' and lastName = '{lastname}') or (firstName2 = '{firstname}' and lastName2 = '{lastname}'))")
                ans = cur.fetchone()
                if ans is not None:
                    if ans['gender'] is not None:
                        genders.append(ans['gender'])
            genders = set(genders)
            if 0 not in genders:
                return 1, 'гендерное распределение среди згс нарушает регламент'
            else:
                return 0, ''


    except Exception as e:
        print(e)
        return -1

async def judgeId_to_name(judge_id):
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            cur.execute(f"select lastName, firstName, workCode, skateId from competition_judges where id = {judge_id}")
            ans = cur.fetchone()
            return ans


    except Exception as e:
        print(e)
        return -1


async def save_generate_result_to_new_tables(user_id, data):
    active_comp = await general_queries.get_CompId(user_id)
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            for groupnumber in data:
                if data[groupnumber]['status'] != 'success':
                    continue

                #Создаем запись в competition_group_crew
                cur.execute(f"select * from competition_group where compId = {active_comp} and groupNumber = {groupnumber}")
                ans = cur.fetchone()
                groupName = ans['groupName']
                sql = "INSERT INTO competition_group_crew (`compId`, `groupNumber`, `roundName`) VALUES (%s, %s, %s)"
                cur.execute(sql, (
                    active_comp, groupnumber, groupName))
                conn.commit()
                crew_id = cur.lastrowid
                #Докидываем судей в competition_group_judges
                ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                lin_id = data[groupnumber]['lin_id']
                zgs_id = data[groupnumber]['zgs_id']
                zgs_data = []
                lin_data = []

                for judIdIndex in range(len(zgs_id)):
                    info = await judgeId_to_name(zgs_id[judIdIndex])
                    lastname = info['lastName']
                    firstname = info['firstName']
                    skateId = info['skateId']
                    zgs_data.append({'judgeId': zgs_id[judIdIndex], 'lastname':lastname, 'firstname':firstname, 'skateId': skateId})

                zgs_data.sort(key=lambda x: x['lastname'])
                for jud in zgs_data:
                    ident = 'ЗГС'
                    lastname = jud['lastname']
                    firstname = jud['firstname']
                    skateId = jud['skateId']
                    judgeid = jud['judgeId']
                    sql = "INSERT INTO competition_group_judges (`crewId`, `typeId`, `ident`, `lastName`, `firstName`, `judgeId`, `skateId`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    cur.execute(sql, (crew_id, 1, ident, lastname, firstname, judgeid, skateId))
                    conn.commit()

                for judIdIndex in range(len(lin_id)):
                    info = await judgeId_to_name(lin_id[judIdIndex])
                    lastname = info['lastName']
                    firstname = info['firstName']
                    skateId = info['skateId']
                    lin_data.append({'judgeId': lin_id[judIdIndex], 'lastname':lastname, 'firstname':firstname, 'skateId': skateId})

                lin_data.sort(key=lambda x: x['lastname'])
                for i in range(len(lin_data)):
                    ident = f'{ALPHABET[i]}({i + 1})'
                    lastname = lin_data[i]['lastname']
                    firstname = lin_data[i]['firstname']
                    skateId = lin_data[i]['skateId']
                    judgeid = lin_data[i]['judgeId']
                    sql = "INSERT INTO competition_group_judges (`crewId`, `typeId`, `ident`, `lastName`, `firstName`, `judgeId`, `skateId`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    cur.execute(sql, (crew_id, 0, ident, lastname, firstname, judgeid, skateId))
                    conn.commit()

                '''
                for judIdIndex in range(len(lin_id)):
                    info = await judgeId_to_name(lin_id[judIdIndex])
                    lastname = info['lastName']
                    firstname = info['firstName']
                    skateId = info['skateId']
                    ident = f'{ALPHABET[judIdIndex]}({judIdIndex + 1})'
                    sql = "INSERT INTO competition_group_judges (`crewId`, `typeId`, `ident`, `lastName`, `firstName`, `judgeId`, `skateId`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    cur.execute(sql, (crew_id, 0, ident, lastname, firstname, lin_id[judIdIndex], skateId))
                    conn.commit()
                    
                '''
    except Exception as e:
        print(e)
        return -1


async def get_gender(firstName):
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            cur.execute(f"select gender from gender_encoder where firstName = '{firstName}'")
            ans = cur.fetchone()
            if ans is None:
                return None
            else:
                return ans['gender']
    except Exception as e:
        print(e)
        return None

async def active_group(compId, groupNumber):
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            cur.execute(f"select isActive from competition_group where compId = {compId} and groupNumber = {groupNumber}")
            ans = cur.fetchone()
            if ans is None:
                return 0
            else:
                r = ans['isActive']
                if r is None:
                    return 0
                else:
                    return r

    except Exception as e:
        print(e)
        return 0


async def get_message_about_age(user_id, judges, code):
    msg = ''
    try:
        if not(code == 0 or code == 1):
            return -1

        compid = await general_queries.get_CompId(user_id)
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            for jud in judges:
                last_name, name = jud
                cur.execute(f"select Birth from competition_judges where compId = {compid} and ((lastName2 = '{last_name}' and firstName2 = '{name}') OR (lastName = '{last_name}' and firstName = '{name}'))")
                date = cur.fetchone()

                cur.execute(f"SELECT date1, date2 FROM competition WHERE compId = {compid}")
                ans = cur.fetchone()
                date1, date2 = ans['date1'], ans['date2']
                if date is None:
                    continue
                else:
                    date = date['Birth']
                    if date is None or type(date) == str:
                        continue

                if code == 1 or code == 2 or code == 0:

                    age = date2.year - date.year
                    if not (28 <= age <= 75):
                        msg += f"🤔{last_name} {name} не попадает в возрастную категорию 28 - 75 лет.\n\n"
            if msg == '':
                return 0
            return msg

    except Exception as e:
        print(e)
        return 0



async def check_age_cat(user_id, lin, zgs, gs):
    try:
        compid = await general_queries.get_CompId(user_id)
        msg = ''
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            for jud in lin + zgs + [gs]:
                i = jud.split()
                if len(i) == 2:
                    last_name, name = i
                else:
                    last_name = i[1]
                    name = ' '.join(i[1::])

                cur.execute(f"select Birth from competition_judges where compId = {compid} and ((lastName2 = '{last_name}' and firstName2 = '{name}') OR (lastName = '{last_name}' and firstName = '{name}'))")
                date = cur.fetchone()

                cur.execute(f"SELECT date1, date2 FROM competition WHERE compId = {compid}")
                ans = cur.fetchone()
                date1, date2 = ans['date1'], ans['date2']
                if date is None:
                    continue
                else:
                    date = date['Birth']
                    if date is None or type(date) == str:
                        continue

                age = date2.year - date.year

                if jud == gs:
                    if not (30 <= age <= 75):
                        msg += f"-{last_name} {name} не попадает в возрастную категорию 28 - 75 лет.\n\n"
                else:
                    if not (28 <= age <= 75):
                        msg += f"-{last_name} {name} не попадает в возрастную категорию 28 - 75 лет.\n\n"

            if msg != '':
                return 1, msg

            return 0, ''
    except:
        return 0, ''


async def age_filter(all_judges, compId):
    try:
        all_judges_01 = []
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            cur.execute(f"SELECT date1, date2 FROM competition WHERE compId = {compId}")
            ans = cur.fetchone()
            date1, date2 = ans['date1'], ans['date2']
            if date2 is None:
                return all_judges

        for jud in all_judges:
            date = jud['Birth']
            if date is None or type(date) == str:
                continue

            age = date2.year - date.year
            if 28 <= age <= 75:
                all_judges_01.append(jud)


        return all_judges_01
    except Exception as e:
        print(e)
        return all_judges


async def sort_generate_list(json, user_id):
    try:
        compid = await general_queries.get_CompId(user_id)
        text = []
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            for groupNumber in json:
                cur.execute(f"select groupName from competition_group where compId = {compid} and groupNumber = {groupNumber}")
                groupName = cur.fetchone()
                if groupName is None:
                    groupName = 'Группа'
                else:
                    groupName = groupName['groupName']
                info = json[groupNumber]

                text_01 = ''
                text_02 = []
                text_03 = []
                for lin in info['lin_id']:
                    cur.execute(f"select firstName, lastName from competition_judges where id = {lin}")
                    names = cur.fetchone()
                    if names is None:
                        text_02.append("Фамилия Имя")
                    else:
                        text_02.append(f"{names['lastName']} {names['firstName']}")

                if info['zgs_id'] != []:
                    for zgs in info['zgs_id']:
                        cur.execute(f"select firstName, lastName from competition_judges where id = {zgs}")
                        names = cur.fetchone()
                        if names is None:
                            text_03.append("Фамилия Имя")
                        else:
                            text_03.append(f"{names['lastName']} {names['firstName']}")

                text_02.sort()
                text_03.sort()
                if len(text_03) != 0:
                    text_01 = groupName + '.' + '\n' + f'Згс. {", ".join(text_03)}'+ "\n" + f'Линейные судьи: {", ".join(text_02)}'
                else:
                    text_01 = groupName + '.' + '\n' + f'Линейные судьи: {", ".join(text_02)}'
                text.append(text_01)

            r =  "\n\n".join(text)
            return r


    except Exception as e:
        print(e)
        return -1


async def getSportCategoryEncoder():
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            cur.execute(f"select * from judges_category_sport")
            ans = cur.fetchall()
            ans_01 = {}
            for cat in ans:
                ans_01[cat["categoryName"]] = cat["categoryId"]
            return ans_01
    except:
        return -1


async def checkSportCategoryFilter(lin, zgs, gs, user_id, group_num):
    try:
        msg = ''
        compid = await general_queries.get_CompId(user_id)
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            cur.execute(f"select minCategorySportId from competition_group where groupNumber = {group_num} and compId = {compid}")
            catfilter = cur.fetchone()
            if catfilter is None:
                return 0, ''

            catfilter = catfilter['minCategorySportId']
            if catfilter is None:
                return 0, ''

            encoder = await getSportCategoryEncoder()
            if len(gs) == 0:
                judges = lin + zgs
            else:
                judges = lin + zgs + [gs]

            for jud in judges:


                i = jud.split()
                if len(i) == 2:
                    last_name, name = i
                else:
                    last_name = i[0]
                    name = ' '.join(i[1::])


                cur.execute(f"SELECT * from competition_judges WHERE compId = {compid} and ((lastName2 = '{last_name}' and firstName2 = '{name}') OR (lastName = '{last_name}' and firstName = '{name}'))")
                ans = cur.fetchone()

                if ans is None:
                    continue

                sportCat = ans['SPORT_Category_Id']


                if sportCat is None:
                    continue

                if sportCat < catfilter:
                    msg += f"{last_name} {name} - спортивная категория не соответствует минимально установленной для работы в группе\n\n"

            if msg == '':
                return 0, ''
            else:
                return 1, msg
    except Exception as e:
        print(e)
        return 0, ''
        pass

async def set_min_sport_cat(compId, group_num, cat):
    try:
        conn = pymysql.connect(
            host=config.host,
            port=3306,
            user=config.user,
            password=config.password,
            database=config.db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn:
            cur = conn.cursor()
            cur.execute(f"update competition_group set minCategorySportId = {cat} where compId = {compId} and groupNumber = {group_num}")
            conn.commit()
            return 1
    except Exception as e:
        print(e)
        return 0
import scrapy
from urllib.parse import urlparse, urljoin
import re


class VyatsuShcheduleSpider(scrapy.Spider):
    name = 'vyatsuspider'
    start_urls = ['https://www.vyatsu.ru/studentu-1/spravochnaya-informatsiya/raspisanie-zanyatiy-dlya-studentov.html']  # Ссылка на таблицу с расписанием, оттуда загружаем названия групп и соответствующие им ссылки на расписания.

    def parse(self, response):
        for url in response.xpath('//div[@class="column-center_rasp"]//a[@target="_blank"]/@href').extract():  # Вытаскиваем URL на группу
            yield scrapy.Request(url, self.parse_group_schedule)  # Включаем парсер для выбранного URL

    def parse_group_schedule(self, response):
        group = response.xpath('////tr[2]/td[3]//text()').extract()[0]  # Вытаскиваем название группы, которую сейчас парсим
        day_schedule = []
        day_of_week = 0
        for lesson_schedule in response.xpath('////tr[position()>2]'):  # Вытаскиваем день, который парсим
            day_schedule.append(lesson_schedule)  # заполняем массив семью парами конкретного дня
            if (day_schedule.__len__() == 7):
                day_of_week += 1
                for item in self.parse_day_schedule(group, day_schedule,day_of_week):  # Включаем парсер для выбранного дня
                    yield item
                day_schedule.clear()  # очистка списка и счетчика дней
        day_of_week = 0

    def parse_day_schedule(self, group, day_schedule, day_of_week):
        day_schedules_week = 1
        if (((day_schedule[0].xpath('./td/div/span/text()')).extract()[0]).find('2') == -1):  # Номер недели
            day_schedules_week = 1 or 2

        day_count = 0  # Счётчик дней

        pair_number = 0  # Cчётчик занятий
        for lessons in day_schedule:
            lesson = lessons.xpath('.//td[3]/text()').extract()
            if not lesson: lesson = lessons.xpath('.//td[2]/text()').extract()
            pair_number += 1
            if not lesson:  # Пропуск пустых ячеек расписания, если пары в это время нет
                continue
            parsed = self.parse_lesson(lesson, group, day_of_week, pair_number,day_schedules_week)  # Обращение к парсеру непосредственно урока и сборка всех данных о занятии в один файл
            if parsed is not None:
                for item in parsed:  # Запись занятия в базу
                    yield item
        day_count += 1

    def parse_lesson(self, lesson, group, day_of_week, pair_number, day_schedules_week):  # Парсер ячейки с занятием
        typeRule='(Чтение л\w+\s)|(Проведение лабораторных з\w+\s)|(Проведение практических занятий, с\w+\s)|(Проведение практических занятий в п\w+\s)|(Проведение практических з\w+\s)|(Пр\.)|(Лб\.)|(Проведение)'
        auditoryRule = '\s\d{1}-\d{3}|\s\d{2}-\d{3}|\s\d{2}-\d{2}'
        teacherRule = '([А-Я]\w+\s[А-Я]\.[А-Я]\.)|([А-Я]\w+\s[А-Я]\.\.)|([А-Я]\w+\s\.[А-Я]\.)|([А-Я]\w+\_[А-Я]\.[А-Я]\.)|(\s[А-Я]\.[А-Я]\.)|(Юфе\w?\s)'
        try:
            if not self.has_subgroups(lesson):  # Проверка, есть ли на данной паре деление на подгруппы
                l = Lesson()  # l становится классом типа Lesson
                l.group = group  # Присвоение того ,что уже спарсили
                l.dayOfWeek = day_of_week % 6
                l.timeSlot = pair_number
                l.weekNumber = day_schedules_week
                # Вытаскиваем из всего текста ячейки номер аудитории
                l.auditory = re.search(r'' + auditoryRule, lesson[0]).group(0)
                l.teacher = re.search(r'' + teacherRule, lesson[0]).group(0)
                if (re.search(r'' + typeRule, lesson[0]) !=None):
                    l.type = re.search(r'' + typeRule, lesson[0]).group(0)
                    subString = re.split(l.type, lesson[0])
                    l.discipline = subString[0]

                else:
                    l.discipline = re.split(l.teacher, lesson[0])[0]

                return [l.__dict__]  # Запись занятия в нашу базу

                #print('No subgroups')       #Recording all simple strings, disabled for better performance (srsly, it will create very big txt file, don't even try use this)
               # f = open('nosubgroups', 'a')
                #f.write(group.encode('utf-8'))
                #f.write(lesson.encode('utf-8'))
                #f.write('\n')
                #f.close()

            else:  # Если в ячейке пара с разделением на подгруппы
                #Todo subgroups

                if (lesson.__len__() == 1):
                    l1 = Lesson()  # l становится классом типа Lesson
                    l1.group = group
                    l1.dayOfWeek = day_of_week % 6
                    l1.timeSlot = pair_number
                    l1.weekNumber = day_schedules_week
                    l1.auditory = re.search(r'' + auditoryRule, lesson[0]).group(0)
                    l1.type = re.search(r'' + typeRule, lesson[0]).group(0)
                    subString = re.split(l1.type, lesson[0])
                    l1.teacher = re.search(r'' + teacherRule, lesson[0]).group(0)
                    subString2 = re.split(l1.group+', ', subString[0])
                    if (subString2.__len__() ==2):
                        subString3 = re.split('подгруппа', subString2[1])
                    else: subString3 = re.split('подгруппа', subString2[0])
                    l1.subgroup = subString3[0]
                    l1.discipline = subString3[1]

                    return [l1.__dict__]
                elif (lesson.__len__() == 2):
                    l1 = Lesson()  # l становится классом типа Lesson
                    l2 = Lesson()
                    l1.group = group
                    l2.group = group  # Присвоение того ,что уже спарсили
                    l1.dayOfWeek = day_of_week % 6
                    l2.dayOfWeek = day_of_week % 6
                    l1.timeSlot = pair_number
                    l2.timeSlot = pair_number
                    l1.weekNumber = day_schedules_week
                    l2.weekNumber = day_schedules_week

                    l1.auditory = re.search(r'' + auditoryRule, lesson[0]).group(0)
                    l1.type = re.search(r'' + typeRule, lesson[0]).group(0)
                    l1.teacher = re.search(r'' + teacherRule, lesson[0]).group(0)
                    subString = re.split(l1.type, lesson[0])
                    subString2 = re.split(l1.group + ', ', subString[0])
                    if (subString2.__len__() ==2):
                        subString3 = re.split('подгруппа', subString2[1])
                    else: subString3 = re.split('подгруппа', subString2[0])
                    l1.subgroup = subString3[0]
                    l1.discipline = subString3[1]

                    l2.auditory = re.search(r'' + auditoryRule, lesson[1]).group(0)
                    l2.type = re.search(r'' + typeRule,lesson[1]).group(0)
                    subString = re.split(l2.type, lesson[1])
                    l2.teacher = re.search(r'' + teacherRule, lesson[1]).group(0)
                    subString2 = re.split(l2.group + ', ', subString[0])
                    if (subString2.__len__() ==2):
                        subString3 = re.split('подгруппа', subString2[1])
                    else: subString3 = re.split('подгруппа', subString2[0])
                    l2.subgroup = subString3[0]
                    l2.discipline = subString3[1]

                    return [l1.__dict__, l2.__dict__]
                #if (lesson.xpath('./br').extract() ==''):

                # Вытаскиваем из всего текста ячейки номер аудитории

                #return [l1.__dict__, l2.__dict__]  # Сразу 2 записи в базу, для двух подгрупп

                #            print('Has subgroups')      #Recording all subgroup-contained strings, disabled for better performance
                #            f = open('subgroups', 'a')
                #            f.write(group.encode('utf-8'))
                #            f.write(lesson.encode('utf-8'))
                #            f.write('\n')
                #            f.close()
        except Exception:  # Поиск исключений и запись их всех в файл bugs.txt, ведь наше расписание поражает своим разнообразием

            f = open('bugs', 'a')
            f.write(group+' ')
            f.write(lesson[0]+' ')
            f.write('\n\n')
            f.close()

    def has_subgroups(self, lesson):  # Сама непосредственно проверка, есть в ячейке расписания подгруппы или нет
        if (lesson.__len__ != 0):
            if (lesson[0].find('подгруппа ') != -1):
                return True
            else:
                return False
        else:
            return False


class Lesson:
    def __init__(self):
        self.group = None
        self.subgroup = None
        self.timeSlot = None
        self.dayOfWeek = None
        self.weekNumber = None
        self.teacher = None
        self.discipline = None
        self.auditory = None
        self.type = None

    def __str__(self):
        return ""

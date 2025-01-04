import os
import pandas as pd

pd.options.display.max_rows = 999


class PriceMachine:

    def __init__(self):
        self.data = self.load_prices()  # Инициирует таблицу со всеми данными сразу при создании объекта
        self.result = ''

    @staticmethod
    def load_prices(file_path=os.getcwd()):
        """
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт

            Допустимые названия для столбца с ценой:
                розница
                цена

            Допустимые названия для столбца с весом (в кг.)
                вес
                масса
                фасовка
        """

        # Поиск файлов с нужными названиями в текущей папке (не было указаний, как делать - можно и улучшить)
        files = [file for file in os.listdir(file_path) if 'price' in file.lower() and file.lower().endswith('.csv')]
        df_list = []  # Добавляем dataframe после парсинга каждого файла в этот список
        # Список достустимых названий для столбцов
        final_table_cols = ["название", "продукт", "товар", "наименование", "цена", "розница", "фасовка", "масса",
                            "вес"]
        for file in files:
            df = pd.read_csv(os.path.join(os.getcwd(), file))
            # Удаляются лишние столбцы, которые не в списке final_table_cols
            df = df.drop(columns=[col for col in df if col not in final_table_cols])
            df['файл'] = file
            columns_list = df.columns.to_list()
            name_index = price_index = mass_index = 0
            # Индексы задаются в блоках ниже, чтобы была возможно упорядочить столбцы в конечной таблице

            if "название" in columns_list:
                name_index = columns_list.index("название")
            elif "продукт" in columns_list:
                name_index = columns_list.index("продукт")
            elif "товар" in columns_list:
                name_index = columns_list.index("товар")
            elif "наименование" in columns_list:
                name_index = columns_list.index("наименование")

            if "цена" in columns_list:
                price_index = columns_list.index("цена")
            elif "розница" in columns_list:
                price_index = columns_list.index("розница")

            if "фасовка" in columns_list:
                mass_index = columns_list.index("фасовка")
            elif "масса" in columns_list:
                mass_index = columns_list.index("масса")
            elif "вес" in columns_list:
                mass_index = columns_list.index("вес")

            df = df.iloc[:, [name_index, price_index, mass_index, 3]]  # Делается порядок
            df = df.set_axis(['название', 'цена', 'вес', 'файл'], axis=1)  # Ставятся одинаковые названия столбцов
            df['цена за кг.'] = round(df['цена'] / df['вес'], 1)
            df_list.append(df)  # Соединяются все таблицы

        data = pd.concat(df_list).sort_values('цена за кг.').reset_index(drop=True)
        return data

    def export_to_html(self, fname='output.html'):
        """
        Экспортируется результат поиска или все доступные данные (если поиска еще не было) в файл HTML с названием
        output.html - файл будет находится в текущей "рабочей" папке
        """
        std_html_1 = '''<!DOCTYPE html>\n<html>\n<head>\n<title>Позиции продуктов</title>\n</head>\n<body>'''
        std_html_2 = '</body>\n</html>'
        try:
            html = self.result.to_html()
        except AttributeError:
            html = self.data.to_html()
        with open(fname, 'w', encoding='utf8') as html_file:
            html_file.write('{}\n{}\n{}'.format(std_html_1, html, std_html_2))

    def find_text(self, text):
        """
        Ищется предлагаемся текст в столбце "название" таблицы со всеми данными изначально, далее результат
        устанавливается в качестве исходных данных для более точного поиска
        """
        self.result = self.data[(self.data['название']).str.contains(text, case=False)]
        self.data = self.result
        return self.result


if __name__ == '__main__':
    pm = PriceMachine()
    # Логика работы программы
    # При повторном поиске ищется в результате предыдущего запроса - если необходимо искать везде, то надо писать reset
    while True:
        search = input('Waiting for search query\n')
        if search.lower() == 'exit':
            print('Exiting program')
            break
        elif search.lower() == 'export':
            pm.export_to_html()
            print('Export to HTML successful')
            continue
        elif search.lower() == 'reset':
            pm.load_prices()
            print('Dataset reset to default')
            continue

        print(pm.find_text(search))

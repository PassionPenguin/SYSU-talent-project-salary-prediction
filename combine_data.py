import re
import os

# folder = os.walk("stats_files")
# files = []

# for path,dir_list,file_list in folder:
#     for file_name in file_list:
#         files.append(file_name)

# for file_name in files:
lines = open("./stats_files/出口总额数据.txt", "r", encoding='utf-8').readlines()


class Category:
    def __init__(self, title, unit, yearbooks):
        self.title = title
        self.unit = unit
        self.yearbooks = yearbooks

    def __str__(self) -> str:
        content = "["
        for i in range(0, len(self.yearbooks)-1):
            content += str(self.yearbooks[i])+","

        content += str(self.yearbooks[len(self.yearbooks)-1])+"]"
        return "{\"title\":\""+self.title+"\",\"unit\":\""+self.unit+"\",\"yearbooks\":"+content+"}"


class Yearbook:
    def __init__(self, name, data_map):
        self.name = name
        self.data_map = data_map  # [yr: value, yr: value], [1950, 2020]

    def __str__(self) -> str:
        content = "{"
        for i in range(0, len(self.data_map)-1):
            content += "\""+str(1950+i) + "\":"+(self.data_map[i] if self.data_map[i] is not None else '-1')+","
        content += "\"2020\":"+(self.data_map[70] if self.data_map[70] is not None else '-1')+"}"
        return "{\"name\":\""+self.name+"\",\"data_map\":"+content+"}"


categorys = []
tmp_books = []
tmp_title = ""
tmp_unit = ""
for i in range(0, len(lines)):
    if "**************************************************【开始】**************************************************" in lines[i]:
        tmp_title = re.search(r"^【(.+?)】$", lines[i+2]).group(1)
        tmp_unit = re.search(r"^【单位】：(.+?)$", lines[i+3]).group(1)
        tmp_books = []

    if "------------------start----------------" in lines[i]:
        tmp_book = Yearbook(name=lines[i+1][1:-2], data_map=[None]*71)
        for j in range(i, len(lines)):
            if "------------------end------------------" not in lines[j]:
                match = re.search(r"^(.+?)-(\d+?)年:(\d*\.?\d*)$", lines[j])
                if match is not None:
                    tmp_book.data_map[int(match.group(2)) -
                                      1950] = match.group(3)
            if "------------------end------------------" in lines[j]:
                tmp_books.append(tmp_book)
                i=j
                break

    if "**************************************************【结束】**************************************************" in lines[i]:
        categorys.append(Category(tmp_title, tmp_unit, tmp_books))

open("tmp.json","w",encoding="utf-8").write(str(categorys[0]))

for category in categorys:
    books = category.yearbooks
    books_len = len(books)

    output = open("./stats_files/output/"+category.title + ".csv", "w", encoding="gbk")
    output.write("title:"+category.title+",unit:"+category.unit+",,year")

    for yr_book in books:
        output.write(','+yr_book.name)

    tmp_frame = []

    for j in range(0, books_len):
        tmp_frame.append(books[j].data_map)

    result_frames=[ ['' if row[col] is None else row[col] for row in tmp_frame] for col in range(len(tmp_frame[0]))]

    for i in range(0, 70):
        output.write("\n,,,"+str(1950+i)+","+','.join(result_frames[i]))

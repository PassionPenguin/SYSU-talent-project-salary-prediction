import re
import os

# folder = os.walk("stats_files")
# files = []

# for path,dir_list,file_list in folder:
#     for file_name in file_list:
#         files.append(file_name)

# for file_name in files:
lines = open("./stats_files/出口总额数据.txt", "r").readlines()


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
        return "{'title':'"+self.title+"','unit':'"+self.unit+"','yearbook':"+content+"}"


class Yearbook:
    def __init__(self, name="", data_map=[None]*71):
        self.name = name
        self.data_map = data_map  # [yr: value, yr: value], [1950, 2020]

    def __str__(self) -> str:
        content = "["
        for i in range(0, len(self.data_map)-1):
            content += str(1950+i) + ":"+(self.data_map[i] if self.data_map[i] is not None else '')+","
        content += "2020:"+self.data_map[70]+"]"
        return "{'name':'"+self.name+"','data_map':'"+content+"'}"


categorys = []
tmp_books = []
tmp_title = ""
tmp_unit = ""
for i in range(0, len(lines)):
    tmp_book = Yearbook()
    if "**************************************************【开始】**************************************************" in lines[i]:
        tmp_title = re.search(r"^【(.+?)】$", lines[i+2]).group(1)
        tmp_unit = re.search(r"^【单位】：(.+?)$", lines[i+3]).group(1)
        tmp_books = []
        tmp_book = Yearbook()

    if "------------------start----------------" in lines[i]:
        tmp_book.name = lines[i+1][1:-2]
        for j in range(i, len(lines)):
            if "------------------end------------------" not in lines[j]:
                match = re.search(r"^(.+?)-(\d+?)年:(\d*\.?\d*)$", lines[j])
                if match is not None:
                    tmp_book.data_map[int(match.group(2)) -
                                      1950] = match.group(3)
            else:
                tmp_books.append(tmp_book)

    if "**************************************************【结束】**************************************************" in lines[i]:
        categorys.append(Category(tmp_title, tmp_unit, tmp_books))

open("tmp.txt","w").write(str(categorys[0]))
# print(categorys[0])

# for category in categorys:
#     boos_len = len(category.yearbooks)

#     output = open("./stats_files/output/"+category.title + ".csv", "w")
#     output.write("title:"+category.title+",unit:"+category.unit+",,year")
#     for yr_book in category.yearbooks:
#         output.write(','+yr_book.name)

#     result_frames = [[None] * boos_len] * 71

#     for i in range(0, boos_len):
#         book = category.yearbooks[i]
#         for j in range(0,len(book.data_map)):
#             result_frames[j][i]=book.data_map[j]

#     for i in range(0, len(result_frames)):
#         frame=result_frames[i]
#         output.write("\n,,,"+str(1950+i))
#         for j in frame:
#             output.write(','+str(j))

# -*- coding: utf-8 -*-

import pandas as pd
import re


df = pd.read_csv('jobs-exported.csv',encoding="utf-8",sep=",")

def delete_null(df):
    print("Drop "+str(df.isnull().values.sum())+" Rows with Null Value")
    df = df.dropna(how='any',axis=0)
    df.to_csv("jobs-exported.csv",index=False)
    return df

def drop_duplicates(df):
    if 'Title' not in df.columns:
        return df

    print("Drop "+str(df.duplicated().sum())+" Duplicated Rows")
    df = df.drop_duplicates()
    df.to_csv("jobs-exported.csv",index=False)
    return df

def normalize_zone(df):
    if 'Title' not in df.columns:
        return df

    normal_zones = ["北京市","上海市","重庆市","天津市","西安市","成都市","昆明市","长春市","合肥市","郑州市","南京市","苏州市","哈尔滨市","广州市","深圳市","东莞市","长沙市","福州市","武汉市","济南市","青岛市","杭州市","宁波市","大连市","沈阳市"]
    
    original_len = len(df.index)
    for index, row in df.iterrows():
        zone = row[1].split('-')[0]
        state=False
        for normal_zone in normal_zones:
            if zone in normal_zone:
                state=True
                df.at[index, "Zone"]=normal_zone
        if  state==False:
            df = df.drop(index)

    print("Drop "+str(original_len - len(df.index))+" Rows with invalidated zone")
    df.to_csv("jobs-exported.csv",index=False)
    return df

def normalize_salary(df):
    if 'Title' not in df.columns:
        return df

    df['Min Salary'] = 0
    df['Max Salary'] = 0
    df['Avg Salary'] = 0
    for index, row in df.iterrows():
        value = str(row[2])
        avg_base = 1
        if "千" in value:
            avg_base = 1000
        elif "万" in value:
            avg_base = 10000
        if "年" in value:
            avg_base /= 12
        elif "天" in value:
            avg_base *= 30
        
        min_base = max_base = avg_base
            
        expression_1 = re.compile(r"([0-9]{2})-([0-9]{2})薪")
        expression_2 = re.compile(r"([0-9]{2})薪")
        if expression_1.search(row['Description']) is not None:
            match = expression_1.search(row['Description'])
            min_base *= int(match.group(1))/12
            max_base *= int(match.group(2))/12
        elif expression_2.search(row['Description']) is not None:
            match=expression_2.search(row['Description'])
            min_base = max_base = avg_base = avg_base * int(match.group(1))/12
        elif expression_1.search(row['Title']) is not None:
            match = expression_1.search(row['Title'])
            min_base *= int(match.group(1))/12
            max_base *= int(match.group(2))/12
        elif expression_2.search(row['Title']) is not None:
            match=expression_2.search(row['Title'])
            min_base = max_base = avg_base = avg_base * int(match.group(1))/12
        
            
        min = max = 0.0

        range_match = re.match(r"(\d+|\d*[\.]\d+)?-(\d+|\d*[\.]\d+)?[^0-9.]", value)
        if range_match is not None:
            min = float(range_match.group(1)) * min_base
            max = float(range_match.group(2)) * max_base
        else:
            max = min = float(re.match(r"(\d+|\d*[\.]\d+)?[^0-9.]", value).group(1)) * avg_base
        
        
        df.at[index,'Min Salary']=min
        df.at[index,'Max Salary']=max
        df.at[index,'Avg Salary']=(max+min)/2

    df.to_csv("jobs-exported.csv",index=False)
    print(df.describe())
    return df

def normalize_company_type(df):
    if 'Title' not in df.columns:
        return df

    for index,row in df.iterrows():
        val = row['Company Type']
        if "外资" in val or "合资" in val:
            df.at[index, 'Company Type'] = '外资/合资'
        else:
            df.at[index, 'Company Type'] = '非外资/合资'

    df.to_csv("jobs-exported.csv",index=False)
    return df

def extract_experience(df):
    if 'Title' not in df.columns:
        return df

    df['Experience']="无需经验"
    df['In School'] = 0
    for index,row in df.iterrows():
        val = row['Degree And Experience']
        normal_experience = ['在校生/应届生', '1-3年', '3-5年', '5-10年', '10年以上', '无需经验']
        for exp in normal_experience:
            if exp in val:
                df.at[index, 'Experience']=exp

        if "无需经验" not in val and df.at[index, 'Experience'] is "无需经验":
            match_1 = re.search(r"(\d+?)-(\d+?)年", val)
            match_2 = re.search(r"(\d+?)年", val)
            if not match_1 is  None:
                min_yr = match_1.group(1)
                max_yr = match_1.group(2)
                avg = (int(min_yr)+int(max_yr))/2
            elif not match_2 is  None:
                avg = int(match_2.group(1))
                
            if avg <= 3:
                df.at[index, 'Experience']="1-3年"
            elif avg <= 5:
                df.at[index, 'Experience']="3-5年"
            elif avg <= 10:
                df.at[index, 'Experience']="5-10年"
            else:
                df.at[index, 'Experience']="10年以上"

    df.to_csv("jobs-exported.csv",index=False)
    return df

def extract_degree(df):
    if 'Title' not in df.columns:
        return df

    df['Degree']="无学历要求"
    for index,row in df.iterrows():
        val = row['Degree And Experience']
        normal_experience = ['初中及以下', '高中/中技/中专', '大专', '本科', '硕士', '博士', '无学历要求']
        for deg in normal_experience:
            if deg in val:
                df.at[index, 'Degree']=deg
            if "在校生/应届生" in val:
                df.at[index, 'In School'] = 1
                
    df.to_csv("jobs-exported.csv",index=False)
    return df

def classification(df):
    if 'Title' not in df.columns:
        return df

    df['Type'] = "数据分析师"
    for index,row in df.iterrows():
        if "高级" in row['Title']:
            df.at[index, 'Type'] = "高级分析师"
        elif "工程" in row['Title']:
            df.at[index, 'Type'] = "数据工程师"

    df.to_csv("jobs-exported.csv",index=False)
    return df

def preprocess_column_name(df):
    if 'Title' not in df.columns:
        return df

    df = df.drop(['Title', 'Salary', 'Degree And Experience', 'Company', 'Publish Date', 'Description'], axis=1)
    df.to_csv("jobs-exported.csv",index=False)
   
    return df

def convert_continuous_features(df):
    for index,row in df.iterrows():
        exp = row['Experience']
        stdexp = ['1-3年', '3-5年', '5-10年', '10年以上']
        df.at[index, 'Experience'] = (stdexp.index(exp) if exp in stdexp else -1)+1
        deg = row['Degree']
        stddeg = ['大专', '本科', '硕士', '博士']
        df.at[index, 'Degree'] = (stddeg.index(deg) if deg in stddeg else -1)+1
        ctype = row['Company Type']
        df.at[index, 'Company Type'] = 0 if ctype is '外资/合资' else 1

    df.to_csv("jobs-exported.csv",index=False)
    
if __name__ == '__main__':    
    df = delete_null(df)
    df = drop_duplicates(df)
    df = normalize_zone(df)
    df = normalize_salary(df)
    df = normalize_company_type(df)
    df = extract_experience(df)
    df = extract_degree(df)
    df = classification(df)
    df = preprocess_column_name(df)
    df = convert_continuous_features(df)
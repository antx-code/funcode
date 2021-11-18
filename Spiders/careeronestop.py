import requests
import json
import pandas as pd
import time
import csv
import os
from random import randint as rd

TOKEN = ''
USER_ID = ''
LOC = 'US'
DAYS = 0
RADIUS = '25'
SORT_COLUMNS = '0'
START_ROW = 1
PAGE_SIZE = 500
SORT_ODRER = '0'
START_RECORD = '1'

today_date = time.strftime('%Y-%m-%d',time.localtime(time.time()))

BASE_API = 'https://api.careeronestop.org/v1/jobsearch'
header = {'Authorization':f'Bearer {TOKEN}','Content-Type':'application/json','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}

class Counter(object):
    def __init__(self, start=0):
        self.num = start
    def count(self):
        self.num += 1
        return self.num

def get_keyword(xl_name):
    frame = pd.read_excel(xl_name)
    keywords = frame['keywords']
    return keywords

def write_list_jobs_csv(Jobcount,JvID,JobTitle,Company,AccquisitionDate,URL,JobLocation,Fc,LocationName,LocationCount,CompanyName,JobCount,CompanyId,
                        Keyword,RequestLocation,IsValidLocation,Radius,StartRow,EndRow,IsCode,Title,LocationState):
    with open(f'{today_date}_list_jobs.csv','a') as f:
        filednames = ['Jobcount','JvID','JobTitle','Company','AccquisitionDate','URL','JobLocation','Fc','LocationName','LocationCount','CompanyName','JobCount','CompanyId',
                      'Keyword','RequestLocation','IsValidLocation','Radius','StartRow','EndRow','IsCode','Title','LocationState']
        writer = csv.DictWriter(f,fieldnames=filednames)
        if os.path.getsize(f'{today_date}_list_jobs.csv') == 0:
            writer.writeheader()
        writer.writerow({'Jobcount':Jobcount,'JvID':JvID,'JobTitle':JobTitle,'Company':Company,'AccquisitionDate':AccquisitionDate,'URL':URL,'JobLocation':JobLocation,'Fc':Fc,'LocationName':LocationName,'LocationCount':LocationCount,'CompanyName':CompanyName,'JobCount':JobCount,'CompanyId':CompanyId,
                      'Keyword':Keyword,'RequestLocation':RequestLocation,'IsValidLocation':IsValidLocation,'Radius':Radius,'StartRow':StartRow,'EndRow':EndRow,'IsCode':IsCode,'Title':Title,'LocationState':LocationState})
        f.close()

def write_job_detail_csv(JobTitle,URL,Company,Location,DatePosted,Description,OnetCodes:list,Publisher,Sponsor,LastAccessDate,CitationSuggested,DataName,DataSourceName,DataSourceUrl,DataLastUpdate,DataVintageOrVersion,DataDescription,DataSourceCitation):
    with open(f'{today_date}_job_detail.csv','a') as f:
        filednames = ['JobTitle', 'URL','Company','Location','DatePosted','Description','OnetCodes','Publisher','Sponsor','LastAccessDate','CitationSuggested','DataName','DataSourceName','DataSourceUrl','DataLastUpdate','DataVintageOrVersion','DataDescription','DataSourceCitation']
        writer = csv.DictWriter(f, fieldnames=filednames)
        if os.path.getsize(f'{today_date}_job_detail.csv') == 0:
            writer.writeheader()
        writer.writerow({'JobTitle':JobTitle, 'URL':URL,'Company':Company,'Location':Location,'DatePosted':DatePosted,'Description':Description,'OnetCodes':OnetCodes,'Publisher':Publisher,'Sponsor':Sponsor,'LastAccessDate':LastAccessDate,'CitationSuggested':CitationSuggested,'DataName':DataName,'DataSourceName':DataSourceName,'DataSourceUrl':DataSourceUrl,'DataLastUpdate':DataLastUpdate,'DataVintageOrVersion':DataVintageOrVersion,'DataDescription':DataDescription,'DataSourceCitation':DataSourceCitation})
        f.close()

def write_all_csv(Jobcount,JvID,JobTitle,Company,AccquisitionDate,URL,JobLocation,Fc,LocationName,LocationCount,CompanyName,JobCount,CompanyId,
                        Keyword,RequestLocation,IsValidLocation,Radius,StartRow,EndRow,IsCode,Title,LocationState,DatePosted,Description,OnetCodes,Publisher,Sponsor,LastAccessDate,CitationSuggested,DataName,DataSourceName,DataSourceUrl,DataLastUpdate,DataVintageOrVersion,DataDescription,DataSourceCitation):
    with open(f'{today_date}_all.csv', 'a') as f:
        filednames = ['Jobcount','JvID','JobTitle','Company','AccquisitionDate','URL','JobLocation','Fc','LocationName','LocationCount','CompanyName','JobCount','CompanyId',
                      'Keyword','RequestLocation','IsValidLocation','Radius','StartRow','EndRow','IsCode','Title','LocationState','DatePosted','Description','OnetCodes','Publisher','Sponsor','LastAccessDate','CitationSuggested','DataName','DataSourceName','DataSourceUrl','DataLastUpdate','DataVintageOrVersion','DataDescription','DataSourceCitation']
        writer = csv.DictWriter(f, fieldnames=filednames)
        if os.path.getsize(f'{today_date}_all.csv') == 0:
            writer.writeheader()
        writer.writerow({'Jobcount':Jobcount,'JvID':JvID,'JobTitle':JobTitle,'Company':Company,'AccquisitionDate':AccquisitionDate,'URL':URL,'JobLocation':JobLocation,'Fc':Fc,'LocationName':LocationName,'LocationCount':LocationCount,'CompanyName':CompanyName,'JobCount':JobCount,'CompanyId':CompanyId,
                      'Keyword':Keyword,'RequestLocation':RequestLocation,'IsValidLocation':IsValidLocation,'Radius':Radius,'StartRow':StartRow,'EndRow':EndRow,'IsCode':IsCode,'Title':Title,'LocationState':LocationState,'DatePosted':DatePosted,'Description':Description,'OnetCodes':OnetCodes,'Publisher':Publisher,'Sponsor':Sponsor,'LastAccessDate':LastAccessDate,'CitationSuggested':CitationSuggested,'DataName':DataName,'DataSourceName':DataSourceName,'DataSourceUrl':DataSourceUrl,'DataLastUpdate':DataLastUpdate,'DataVintageOrVersion':DataVintageOrVersion,'DataDescription':DataDescription,'DataSourceCitation':DataSourceCitation})
        f.close()

def csv_to_xlsx(filename):
    csvf = pd.read_csv(f'{filename}.csv')
    csvf.to_excel(f'{filename}.xlsx',sheet_name='data')

def jobs_query_id(keyword):
    """

    通过keyword搜索并返回jobs API.

    :param keyword:
    :return:
    """
    url = f'{BASE_API}/{USER_ID}/{keyword}/{LOC}/{RADIUS}/{SORT_COLUMNS}/{SORT_ODRER}/{START_RECORD}/{PAGE_SIZE}/{DAYS}'
    resp = requests.get(url,headers=header).text
    return resp

def get_job_detail(job_id):
    """

    通过job id搜索并返回job description API.

    :param job_id:
    :return:
    """
    url = f'{BASE_API}/{USER_ID}/{job_id}'
    resp = requests.get(url,headers=header).text
    return resp


if __name__ == '__main__':
    keywords = get_keyword('All_Occupations.xls')
    c1 = Counter()
    for keyword in keywords:
        cp1 = c1.count()
        if cp1 == 2000:
            time.sleep(300)
        time.sleep(rd(1,9))
        query_resp = jobs_query_id(keyword)
        list_jobs = json.loads(query_resp)
        print(f'准备提取list_jobs,list_jobs--{list_jobs}')
        Jobcount = list_jobs['Jobcount']
        Jobs = list_jobs['Jobs']    # ListObject
        Locations = list_jobs['Locations']  # ListObject
        Companies = list_jobs['Companies']  # ListObject
        JobsKeywordLocations = list_jobs['JobsKeywordLocations']    # Object
        Keyword = JobsKeywordLocations['Keyword']
        RequestLocation = JobsKeywordLocations['Location']
        IsValidLocation = JobsKeywordLocations['IsValidLocation']
        Radius = JobsKeywordLocations['Radius']
        StartRow = JobsKeywordLocations['StartRow']
        EndRow = JobsKeywordLocations['EndRow']
        if JobsKeywordLocations['IsCode']:
            IsCode = 'True'
            print(f'IsCode is {IsCode}')
        else:
            IsCode = 'Flase'
        Title = JobsKeywordLocations['Title']
        LocationState = JobsKeywordLocations['LocationState']
        if LocationState == '':
            LocationState = 'None'
        if Locations is None:
            LocationName = 'None'
            LocationCount = 'None'
            print(f'Locations is None')
        if Companies is None:
            CompanyName = 'None'
            JobCount = 'None'
            CompanyId = 'None'
            print(f'Companies is None')
        c2 = Counter()
        for num in range(len(Jobs)):
            JvId = Jobs[num]['JvId']
            JobTitle = Jobs[num]['JobTitle']
            Company = Jobs[num]['Company']
            AccquisitionDate = Jobs[num]['AccquisitionDate']
            URL = Jobs[num]['URL']
            JobLocation = Jobs[num]['Location']
            Fc = Jobs[num]['Fc']
            if Locations is None:
                pass
            else:
                if num > len(Locations)-1:
                    LocationName = 'None'
                    LocationCount = 'None'
                    print(f'Locations length is {len(Locations)}')
                else:
                    LocationName = Locations['LocationName']
                    LocationCount = Locations['LocationCount']
            if Companies is None:
                pass
            else:
                if num > len(Companies)-2:
                    CompanyName = 'None'
                    JobCount = 'None'
                    CompanyId = 'None'
                    print(f'Companies length is {len(Companies)}')
                else:
                    CompanyName = Companies['CompanyName']
                    JobCount = Companies['JobCount']
                    CompanyId = Companies['CompanyId']
            write_list_jobs_csv(Jobcount,JvId,JobTitle,Company,AccquisitionDate,URL,JobLocation,Fc,LocationName,LocationCount,CompanyName,JobCount,CompanyId,Keyword,RequestLocation,IsValidLocation,Radius,StartRow,EndRow,IsCode,Title,LocationState)
            print('*********写入list_jobs数据成功*********')
            cp2 = c2.count()
            if cp2 == 1500:
                time.sleep(500)
            time.sleep(rd(1,6))
            DescResp = get_job_detail(JvId)
            JobDescApi = json.loads(DescResp)
            print(f'准备提取job_detail,job_detail--{JobDescApi}')
            try:
                if JobDescApi[0]['Error']:
                    DatePosted = 'None'
                    Description = 'Job No Longer Available'
                    OnetCodes = ['None']
                    Publisher = 'None'
                    Sponsor = 'None'
                    LastAccessDate = 'None'
                    CitationSuggested = 'None'
                    DataName = 'None'
                    DataSourceName = 'None'
                    DataSourceUrl = 'None'
                    DataLastUpdate = 'None'
                    DataVintageOrVersion = 'None'
                    DataDescription = 'None'
                    DataSourceCitation = 'None'
                    write_job_detail_csv(JobTitle, URL, Company, JobLocation, DatePosted, Description, OnetCodes,
                                         Publisher, Sponsor, LastAccessDate, CitationSuggested, DataName,
                                         DataSourceName, DataSourceUrl, DataLastUpdate, DataVintageOrVersion,
                                         DataDescription, DataSourceCitation)
                    print('*********写入jobs_description数据成功*********')
                    write_all_csv(Jobcount, JvId, JobTitle, Company, AccquisitionDate, URL, JobLocation, Fc,
                                  LocationName, LocationCount, CompanyName, JobCount, CompanyId, Keyword,
                                  RequestLocation, IsValidLocation, Radius, StartRow, EndRow, IsCode, Title,
                                  LocationState, DatePosted, Description, OnetCodes,
                                  Publisher, Sponsor, LastAccessDate, CitationSuggested, DataName, DataSourceName,
                                  DataSourceUrl, DataLastUpdate, DataVintageOrVersion, DataDescription,
                                  DataSourceCitation)
                    print('*********合并所有数据成功*********')
            except Exception as e:
                DatePosted = JobDescApi['DatePosted']
                Description = JobDescApi['Description']
                OnetCodes = JobDescApi['OnetCodes'] # List
                print(f'OnetCodes is {OnetCodes}')
                MetaData = JobDescApi['MetaData']   # Object  不写入表格
                Publisher = MetaData['Publisher']
                Sponsor = MetaData['Sponsor']
                LastAccessDate = MetaData['LastAccessDate']
                CitationSuggested = MetaData['CitationSuggested']
                DataSource = MetaData['DataSource'] # 不写入表格
                print(f'DataSource length is {len(DataSource)}')
                for i in range(len(DataSource)):
                    DataName = DataSource[i]['DataName']
                    DataSourceName = DataSource[i]['DataSourceName']
                    DataSourceUrl = DataSource[i]['DataSourceUrl']
                    DataLastUpdate = DataSource[i]['DataLastUpdate']
                    DataVintageOrVersion = DataSource[i]['DataVintageOrVersion']
                    DataDescription = DataSource[i]['DataDescription']
                    DataSourceCitation = DataSource[i]['DataSourceCitation']
                    write_job_detail_csv(JobTitle,URL,Company,JobLocation,DatePosted,Description,OnetCodes,Publisher,Sponsor,LastAccessDate,CitationSuggested,DataName,DataSourceName,DataSourceUrl,DataLastUpdate,DataVintageOrVersion,DataDescription,DataSourceCitation)
                    print('*********写入jobs_description数据成功*********')
                    write_all_csv(Jobcount,JvId,JobTitle,Company,AccquisitionDate,URL,JobLocation,Fc,LocationName,LocationCount,CompanyName,JobCount,CompanyId,Keyword,RequestLocation,IsValidLocation,Radius,StartRow,EndRow,IsCode,Title,LocationState, DatePosted, Description, OnetCodes,
                                  Publisher, Sponsor, LastAccessDate, CitationSuggested, DataName, DataSourceName,
                                  DataSourceUrl, DataLastUpdate, DataVintageOrVersion, DataDescription, DataSourceCitation)
                    print('*********合并所有数据成功*********')

    print(f'*********准备转换excel*********')
    csv_to_xlsx(f'{today_date}_list_jobs')
    csv_to_xlsx(f'{today_date}_job_detail')
    csv_to_xlsx(f'{today_date}_all')
    # csv_to_xlsx('2020-05-30_list_jobs')
    # csv_to_xlsx('2020-05-30_job_detail')
    # csv_to_xlsx('2020-05-30_all')
    print('*********All Done*********')

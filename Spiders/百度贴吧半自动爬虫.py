import re
import requests
import csv

Html = 'http://tieba.baidu.com/p/5018226353'
SourceCode = requests.get(Html)
f = SourceCode.text

class semispider:
    AllPara = {'Username':'','Content':'','PubTime':''}
    def __init__(self):
        self.GetUsername()
        self.GetContent()
        self.GetPubtime()
        print(self.AllPara)


    def GetUsername(self):
        all_name = re.findall('-8" target="_blank">(.*?)</a>',f)
        # for eacha in all_name:
        self.AllPara['Username'] = all_name

    def GetContent(self):
        all_content = re.findall('j_d_post_content  clearfix">            (.*?)</div>',f)
        self.AllPara['Content'] = all_content
    #
    def GetPubtime(self):
        pub_time = re.findall('date&quot;:&quot;(.*?)&quot;,&quot;vote_crypt&quot;',f)
        self.AllPara['PubTime'] = pub_time

if __name__ == '__main__':
    SemiSpider = semispider()

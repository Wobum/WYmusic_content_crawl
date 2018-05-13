#-*- coding:utf-8 -*-

from Crypto.Cipher import AES
import base64
import requests
import json
import time
import sys
import random
import os
import math

class CommentCrawl:

    headers = {
        'Host':'music.163.com',
        'Origin':'https://music.163.com',
        'Referer':'https://music.163.com/song?id=28793052',
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }

    '''
    除了第一个参数，其他参数为固定参数，可以直接套用
    offset的取值为:(评论页数-1)*20,total第一页为true，其余页为false
    第一个参数
    first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
    '''
    # 第二个参数,在程序中并没有用到......
    second_param = "010001"
    # 第三个参数
    third_param = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
    # 第四个参数，在程序中也没有用到......
    forth_param = "0CoJUm6Qyw8W8jud"

    def __init__(self,url):
        self.url = url

    # 通过传入页数获取每页的params参数
    def get_params(self,page): # page为传入页数
        iv = "0102030405060708"
        first_key = self.forth_param
        second_key = 16 * 'F'
        if(page == 1): # 如果为第一页
            first_param = '{rid:"", offset:"0", total:"true", limit:"20", csrf_token:""}'
            h_encText = self.AES_encrypt(first_param, first_key, iv)
        else:
            offset = str((page-1)*20)
            first_param = '{rid:"", offset:"%s", total:"%s", limit:"20", csrf_token:""}' %(offset,'false')
            h_encText = self.AES_encrypt(first_param, first_key, iv)
        h_encText = self.AES_encrypt(h_encText, second_key, iv)
        return h_encText

    # 获取 encSecKey
    def get_encSecKey(self):
        encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
        return encSecKey

    # 加密过程
    def AES_encrypt(self,text, key, iv):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        encrypt_text = encryptor.encrypt(text)
        encrypt_text = base64.b64encode(encrypt_text)
        encrypt_text = str(encrypt_text, encoding="utf-8") #注意一定要加上这一句，没有这一句则出现错误
        return encrypt_text

    # 获得评论json数据
    def get_json(self, params, encSecKey):
        data = {
             "params": params,
             "encSecKey": encSecKey
        }
        try:
            response = requests.post(self.url, headers=self.headers, data=data)
            response.raise_for_status
            return response.content
        except:
            print("爬取链接失败！")

    #获取歌曲下评论的总页数，通过第一页的total参数进行查看
    def get_page(self):
        params = self.get_params(1)
        encSecKey = self.get_encSecKey()
        json_text = self.get_json(params,encSecKey)
        json_dict = json.loads(json_text)
        total = json_dict['total']
        page = math.ceil(total/20)
        return page

    #获取歌曲下面的所有评论内容
    def get_all_comments(self):
        all_comments_list = [] # 存放所有评论
        page = self.get_page()
        for i in range(page):  # 逐页抓取
            print('正在抓取第%d页评论，请稍等...'%(i+1))
            params = self.get_params(i+1)
            encSecKey = self.get_encSecKey()
            json_text = self.get_json(params,encSecKey)
            json_dict = json.loads(json_text)
            #如果是第一页，会有精选评论
            if i == 0:
                for item in json_dict['hotComments']:
                    '''
                    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
                    print('评论id：',item['user']['nickname'].translate(non_bmp_map))
                    print('评论内容：',item['content'].translate(non_bmp_map))
                    '''
                    content_name = str(item['user']['nickname']) #评论人昵称
                    content_info = str(item['content'])          #评论内容
                    star = str(item['likedCount'])               #评论点赞数
                    contetn_dict = {
                    '评论人昵称':content_name,
                    '评论内容':content_info,
                    '评论点赞数':star
                    }
                    all_comments_list.append(contetn_dict)

            for item in json_dict['comments']:
                '''
                由于评论中有的字符在python中无法显示，如果需要输出，可以使用翻译表将处于BMP外的所有内容映射到替换字符
                non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
                print('评论id：',item['user']['nickname'].translate(non_bmp_map))
                print('评论内容：',item['content'].translate(non_bmp_map))
                '''
                content_name = str(item['user']['nickname']) #评论人昵称
                content_info = str(item['content'])          #评论内容
                star = str(item['likedCount'])               #评论点赞数
                contetn_dict = {
                '评论人昵称':content_name,
                '评论内容':content_info,
                '评论点赞数':star
                }
                all_comments_list.append(contetn_dict)
            print('第%d页抓取完毕!' % (i+1))
            if i == page-1:
                print('抓取完毕！！！')
            #每个30页休眠一段时间
            if i % 30 == 0:
                time.sleep(random.choice(range(3,5)))  #爬取过快的话，设置休眠时间，跑慢点，减轻服务器负担
        return all_comments_list

    def saveContent(self):
        content_list = self.get_all_comments()
        root = 'E:\\程序\\python\\网易云音乐评论爬取\\'
        path = root + 'See You Again网易云评论.txt'
        if not os.path.exists(root):
            os.mkdir(root)
        if not os.path.exists(path):
            try:
                 with open(path,'a',encoding = 'utf-8') as f:
                    for i in content_list:                        
                        f.write('评论人昵称: '+i['评论人昵称']+'\r\n')
                        f.write('评论内容: '+i['评论内容']+'\r\n')
                        f.write('评论点赞数: '+i['评论点赞数']+'\r\n')
                        f.write('\r\n')
                    
            except:
                print('保存评论信息出错！')
        else:
            print('评论信息已存在！')
                
def main():
    start_time = time.time()  # 开始时间
    url = "https://music.163.com/weapi/v1/resource/comments/R_SO_4_30953009?csrf_token="  # 替换为你想下载的歌曲R_SO的链接
    obj = CommentCrawl(url)
    obj.saveContent()
    end_time = time.time()  # 结束时间
    print('程序耗时%f秒.' % (end_time - start_time))

if __name__ == '__main__':
    main()

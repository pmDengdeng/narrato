import requests
import pandas as pd
import json

class NaAPI:
    def __init__(self, api_key):
        self.headers = {
        'app-key': api_key
    }
        
    # 获取任务列表
    def get_task_list(self,limit=10,page=None,status=None):
        url = 'https://openapi.jieshuo.cn/api/v1/task?'
        params = {'limit': limit,'page': page,'status': status}
        response = requests.get(url, params=params, headers=self.headers)
        return pd.DataFrame(response.json()['data'])
    # 获取单个任务详情
    def get_single_task_detail(self, task_num):
        url = f'https://openapi.jieshuo.cn/api/v1/task/{task_num}'
        response = requests.get(url, headers=self.headers)
        data = response.json()
        return data

    
    # 获取素材列表
    def get_materials(self,limit=10,page=None,name=None):
        url = f'https://openapi.jieshuo.cn/api/v1/materials?'
        params = {'limit': limit,'page': page,'name': name}
        response = requests.get(url,params=params, headers=self.headers)
        return pd.DataFrame(response.json()['data'])
    # 获取单个素材详情
    def get_single_materials_detail(self, video_id):
        url = f'https://openapi.jieshuo.cn/api/v1/materials/{video_id}'
        response = requests.get(url, headers=self.headers)
        return response.json()
    
    #获取剪辑参数
    def get_options(self,):
        url = f'https://openapi.jieshuo.cn/api/v1/material/options'
        headers = self.headers
        response = requests.get(url, headers=self.headers)
        return response.json()['data']
    #创建任务
    def create_task(self,title,model="六脉神剑",dubbing="逸尘",font_size="标准字幕",cover=" 复古边框封面",bgm=None,video_type=None):
        url = "https://openapi.jieshuo.cn/api/v1/task"
        payload = {
            "model": model,
            "title": title,
            "dubbing": dubbing,
            # "subtitle_style": subtitle_style,
            "font_size": font_size,
            "cover": cover,
            "bgm":bgm,
            "video_type":video_type
            }
        response=requests.post(url,headers=self.headers,json=payload)
        return response.json()
        
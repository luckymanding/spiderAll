# -*- coding: utf-8 -*-
#autor:Oliver0047
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from time import sleep
import re
from tkinter import *
import time
import pickle
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

damai_url="https://www.damai.cn/"
login_url="https://passport.damai.cn/login?ru=https%3A%2F%2Fwww.damai.cn%2F"
class Concert(object):
    def __init__(self,name,date,price,place,real_name,method=1):
        self.name=name#歌星
        self.date=date#日期序号优先级，比如，如果第二个时间可行，就选第二个，不然就选其他,最终只选一个
        self.price=price#票价序号优先级,道理同上
        self.place=place#地点
        self.status=0#状态,表示如今进行到何种程度
        self.login_method=method#{0:模拟登录,1:Cookie登录}自行选择登录方式
        with open('./user_info.txt','r') as f:#读入用户名与密码和昵称
            self.uid=f.readline().strip('\n').strip('\r\n').strip()
            self.upw=f.readline().strip('\n').strip('\r\n').strip()
            self.usr_name=f.readline().strip('\n').strip('\r\n').strip()
           
    def get_cookie(self):
       self.driver.get(damai_url)
       print("###请点击登录###")
       while self.driver.title.find('大麦网-全球演出赛事官方购票平台')!=-1:
           sleep(1)
       print("###请扫码登录###")
       while self.driver.title=='大麦登录':
           sleep(1)
       print("###扫码成功###")
       pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
       print("###Cookie保存成功###")
   
    def set_cookie(self):
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))#载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain':'.damai.cn',#必须有，不然就是假登录
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    "expires": "",
                    'path': '/',
                    'httpOnly': False,
                    'HostOnly': False,
                    'Secure': False}
                self.driver.add_cookie(cookie_dict)
            print('###载入Cookie###')
        except Exception as e:
            print(e)
           
    def login(self):
        if self.login_method==0:
            self.driver.get(login_url)#载入登录界面
            print('###开始登录###')
        elif self.login_method==1:           
            if not os.path.exists('cookies.pkl'):#如果不存在cookie.pkl,就获取一下
                self.get_cookie()
            else:
                self.driver.get(damai_url)
                self.set_cookie()
     
    def enter_concert(self):
        print('###打开浏览器，进入大麦网###')
        self.driver=webdriver.Firefox()#默认火狐浏览器
        self.driver.maximize_window()
        self.login()#先登录再说
        self.driver.refresh()   
        try:
            element = WebDriverWait(self.driver, 3).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR,".name-user"),self.usr_name))
            self.status=1
            print("###登录成功###")
        except:
            self.status=0
            print("###登录失败###")             
        if self.status==1:
            self.driver.find_element_by_class_name('input-search').send_keys(self.name)#搜索栏输入歌星
            self.driver.find_element_by_class_name('btn-search').click()#点击搜索
            try: 
                time.sleep(3) 
                element = self.driver.find_elements_by_css_selector('.factor-content')[2]
                kinds=element.find_elements_by_class_name('factor-content-item')#选择演唱会类别
                print("ok")
                print(kinds)
            except Exception as e:
                print(e)
            for k in kinds:
                print(k.text)
                if k.text=='演唱会':
                    k.click()
                    time.sleep(5)
                    break
            lists=self.driver.find_elements_by_class_name('item__box')[0].find_elements_by_class_name('items')#获取所有可能演唱会
            #注释的代码表示用图形界面手动选择演唱会，可以自行体会
    #        root = Tk()
    #        root.title("选择演唱会")
    #        v = IntVar()
    #        v.set(1)
            links=''
    #        def selection():
    #            self.choose_result=v.get()
    #            root.destroy()
            for li in lists:
                word_link=li.find_element_by_class_name('items__txt__title')
                if self.place in word_link.text:
                    temp_s=li.get_attribute('innerHTML').find('href')+6
                    temp_e=li.get_attribute('innerHTML').find('target')-2
                    links=li.get_attribute('innerHTML')[temp_s:temp_e]
                    print(links)
                    break

    #            b = Radiobutton(root,text = titles[-1],variable = v,value = len(titles),command=selection)
    #            b.pack(anchor = W)
    #        root.mainloop()
    #        while self.choose_result==0:
    #            sleep(1)
            self.url="https:"+links
            self.driver.get(self.url)#载入至购买界面
            self.status=2
            print("###选择演唱会###")


    def choose_ticket(self):
        if self.status==2:
            self.num=1#第一次尝试
            time_start=time.time()
            while self.driver.title.find('确认订单')==-1:#如果跳转到了订单结算界面就算这部成功了
                if self.num!=1:#如果前一次失败了，那就刷新界面重新开始
                    self.status=2
                    print(self.num)
                    self.driver.get(self.url)
                try:   
                    element =self.driver.find_elements_by_class_name('select_right_list')[1]
                except Exception as e:
                    print(e)       
                datelist=element.find_elements_by_class_name('select_right_list_item')
                for i in self.date:#根据优先级选择一个可行日期
                    if '无票' in datelist[i-1].text:
                        print(datelist[i-1].text)
                        print('无票')
                        continue
                    else:
                        datelist[i-1].click()
                        sleep(1)
                        print("点击")
                        break               
                pricelist=self.driver.find_elements_by_class_name('select_right_list')[2]#根据优先级选择一个可行票价
                pricelist2=element.find_elements_by_class_name('select_right_list_item')
                for i in self.price:
                    if '缺货登记' in datelist[i-1].text:
                        print(datelist[i-1].text)
                        print('缺货登记')
                        continue
                    else:
                        datelist[i-1].click()
                        sleep(1)
                        print("点击")
                        break

                try:
                    self.driver.find_element_by_class_name('cafe-c-input-number-handler-up').click()
                except:
                    print("cant click")
                print("###选择演唱会时间与票价###")
                cart=self.driver.find_element_by_class_name('buybtn')
                try:#各种按钮的点击
                    cart.click()
                    self.status=3
                except:
                    print('bugbug')
                self.num+=1
                
            time_end=time.time()
            print("###经过%d轮奋斗，共耗时%f秒，抢票成功！请确认订单信息###"%(self.num-1,round(time_end-time_start,3)))
   
    def check_order(self):
        if self.status in [3,4,5]:
            print('###开始确认订单###')
            print('###默认购票人信息###') 
            rn_button=self.driver.find_elements_by_xpath('//*[@type="checkbox"]')
            for i in rn_button[:2]:
                print(i.text)
                i.click()

            sumbit=self.driver.find_element_by_class_name('submit-wrapper')
            sumbit.find_element_by_class_name('next-btn').click()
    def finish(self):
        self.driver.quit()
               

if __name__ == '__main__':
    try:
 #       con=Concert('周杰伦',[1,2],[2],'深圳',1)#具体如果填写请查看类中的初始化函数
        con=Concert('张杰',[1,2],[1,2,3,4,5],'南宁',1)
        con.enter_concert()
        con.choose_ticket()
        con.check_order()
    except Exception as e:
        print(e)
        con.finish()

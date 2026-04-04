#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 未來參考
# https://forum.gamer.com.tw/C.php?bsn=2450&snA=1356

# 之後工作
# 新增修改按鈕 更新json (目前只有完全刪除的方法)

from logging import exception
import pyautogui
import pydirectinput
import tkinter as tk
import tkinter.messagebox
import win32api, win32con
import threading
import time
import py_win_keyboard_layout
import os
import pygetwindow as gw
import cv2
import aircv as ac
import numpy as np
import copy
import os
from PIL import Image
import math
import json

machine_tag = False
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.preprocessing import image
    physical_devices = tf.config.list_physical_devices('GPU')
    tf.config.experimental.set_memory_growth(physical_devices[0], True)
    machine_tag = True
except:
    # Invalid device or cannot modify virtual devices once initialized.
    machine_tag = False
    pass


def match(IMSRC, IMOBJ, threshold=0.8):
    # 確保圖片是彩色三通道
    if len(IMSRC.shape) == 2:  # 灰階轉BGR
        IMSRC = cv2.cvtColor(IMSRC, cv2.COLOR_GRAY2BGR)
    if len(IMOBJ.shape) == 2:  # 灰階轉BGR
        IMOBJ = cv2.cvtColor(IMOBJ, cv2.COLOR_GRAY2BGR)

    pos = ac.find_template(IMSRC, IMOBJ, threshold=threshold, rgb=False)
    if pos is not None:
        print(f"✅ 匹配成功，信心值 {pos['confidence']:.2f}，位置: {pos['result']}")
        cv2.rectangle(IMSRC, pos['rectangle'][0], pos['rectangle'][3], (0, 0, 255), 2)
        return pos
    else:
        print("❌ 未匹配到")
        return None

def position_return(screenshot, compare_object: str, x_offset: int = 10, y_offset: int = 10):
    IMSRC=np.array(screenshot)
    # 找比對
    IMOBJ=cv2.imread(compare_object)
    # print(type(IMOBJ))
    position = match(IMSRC,IMOBJ)
    if position is not None:
        x, y = position["result"]
        return int(x + x_offset), int(y + y_offset)
    else:
        return (None, None)
    
def mouseclick():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    
# === 核心：安全點擊，支援重試與信心值檢查 ===
def safe_click(img_path, retries=5, threshold=0.75, delay=0.5):
    for attempt in range(retries):
        screenshot = pyautogui.screenshot()
        IMSRC = np.array(screenshot)
        IMOBJ = cv2.imread(img_path)
        pos = match(IMSRC, IMOBJ, threshold)
        if pos is not None:
            x, y = map(int, pos['result'])
            pyautogui.moveTo(x, y)
            mouseclick()
            print(f"✅ 已點擊 {img_path}")
            time.sleep(delay)
            # 二次確認
            screenshot2 = pyautogui.screenshot()
            IMSRC2 = np.array(screenshot2)
            pos_check = match(IMSRC2, IMOBJ, threshold)
            if pos_check is None:
                print("🟢 按鈕成功消失，確認點擊有效。")
                return True
            else:
                print("⚠️ 按鈕仍存在，可能點擊未成功，重試中...")
        else:
            print(f"❌ 第 {attempt+1} 次未找到 {img_path}")
        time.sleep(1)
    print(f"❌ 多次嘗試仍未能點擊 {img_path}")
    return False

def account(account_group: str):
    account_number = 0
    account_index = 0
    if(account_group.__eq__("1")):
        account_number = 3
        account_index= 0
    elif(account_group.__eq__("2")):
        account_number = 4
        account_index = 3
    elif(account_group.__eq__("3")):
        account_number = 6
        account_index = 7
    elif(myaccountlist.curselection()):
        account_index = myaccountlist.curselection()[0]
        account_number = 1
    
    return account_number, account_index


def empty_list():
    global openlist
    global olderlist
    openlist = []
    olderlist = []
    alltitles = gw.getAllTitles()
    for t in alltitles:
        if "天使之戀Online - " in t:
            openlist.append(t)
            olderlist.append(t)
    print(openlist)
    print(olderlist)

def AutoOpen(account_group: str):   
    account_number, account_index = account(account_group)
    # pyautogui.hotkey('winleft', 'd')

    empty_list()
    if account_number == 0:
        return
    
    for i in range(account_number):
        print(f"🚀 啟動第 {i+1} 個帳號")
        os.startfile(application_path)
        time.sleep(3)

        # Step 1: 開始遊戲
        if not safe_click("image/start game.png", retries=10, threshold=0.75):
            print("⚠️ 找不到 start game.png，略過此帳號")
            continue

        # 等待登入畫面
        waited = 0
        while not safe_click("image/agree.png", retries=1) and waited < 60:
            time.sleep(3)
            waited += 3
        if waited >= 60:
            print("❌ 超時未找到 agree.png，略過此帳號")
            continue

        # Step 2: 切換輸入法
        py_win_keyboard_layout.change_foreground_window_keyboard_layout(0x04090409)

        # Step 3: 登入帳密
        pyautogui.press('backspace', presses=15, interval=0.05)
        pyautogui.write(myaccountlist.get(account_index))
        time.sleep(1)
        pydirectinput.press('tab')
        pyautogui.write(mypasswordlist.get(account_index))
        pyautogui.press("enter")
        time.sleep(3)
        pyautogui.press("enter")
        time.sleep(3)
        pyautogui.press("enter")

        # Step 4: 第二組密碼
        if data[account_index].get("second_password", ""):
            pyautogui.write(data[account_index]["second_password"])
        pyautogui.press("enter")
        pyautogui.press("enter")

        time.sleep(4)
        
        # Step 5: 新視窗偵測
        alltitles = gw.getAllTitles()
        global openlist, olderlist
        for t in alltitles:
            if "天使之戀Online - " in t:
                openlist.append(t)
        now_window_list = list(set(openlist) - set(olderlist))
        openlist = list(set(openlist))
        olderlist = copy.deepcopy(openlist)
        now_window_name = gw.getWindowsWithTitle(now_window_list[0])[0]

        # Step 6: 自動攻擊啟動
        safe_click("image/attackpage1.png", retries=8)
        safe_click("image/autoattack.png", retries=8)

        # Step 7: 視窗調整
        try:
            if account_group in ["2", "3"]:
                if i == 0:
                    now_window_name.moveTo(int(screen_width/25), int(screen_height/25))
                elif i == 1:
                    now_window_name.moveTo(int(screen_width/25 + now_window_name.width), int(screen_height/25))
                elif i == 2:
                    now_window_name.moveTo(int(screen_width/25), int(screen_height/25 + now_window_name.height))
                elif i == 3:
                    now_window_name.moveTo(int(screen_width/25 + now_window_name.width), int(screen_height/25 + now_window_name.height))
            now_window_name.minimize()
        except Exception as e:
            print(f"⚠️ 移動視窗失敗: {e}")
        time.sleep(2)
        account_index += 1

    empty_list()
  
def get_mouse_pos():
    mouse_position.config(text='滑鼠現在位置: {}, {}'.format(*root.winfo_pointerxy()))
    root.after(100, get_mouse_pos)

def exe_time(loop):    
    if loop=="2":
        count = 5
    else:
        count = 1
    clicktreasure(count)

def clicktreasure(count):
    # 取得當前視窗
    alltitles = gw.getAllTitles()
    i = 1
    while i <= count:
        for t in alltitles:
            if "天使之戀Online - " in t:
                print(f'now window = {t}')
                now_window_name = gw.getWindowsWithTitle(t[0])[0]
                now_window_name.restore()
                now_window_name.activate()
                time.sleep(1)

                shot = pyautogui.screenshot(region=[now_window_name.left, now_window_name.top, now_window_name.width, now_window_name.height]) # x,y,w,h
                open_cv_image_np = np.array(shot)
                IMSRC=open_cv_image_np
                # 找比對            
                IMOBJ=cv2.imread(os.path.join(dirname, "image/time.png"))
                position = match(IMSRC,IMOBJ)

                count_num = 0
                while position is None:
                    time.sleep(1)
                    shot = pyautogui.screenshot(region=[now_window_name.left, now_window_name.top, now_window_name.width, now_window_name.height]) # x,y,w,h
                    open_cv_image_np = np.array(shot)
                    IMSRC=open_cv_image_np
                    # 找比對
                    IMOBJ=cv2.imread(os.path.join(dirname, "image/time.png"))
                    position = match(IMSRC,IMOBJ)
                    count_num+=1

                    if count_num > 50:
                        break
                
                position_xy = str(position[0]).replace('(', '').replace(')', "").split(", ")

                # 滑鼠要移動到的位置
                x = now_window_name.left + int(position_xy[0]) + 10
                y = now_window_name.top + int(position_xy[1]) + 10

                startPosition = (x, y)
                pyautogui.moveTo(startPosition)
                mouseclick()

                now_window_name.minimize()
                i+=1
        print("done")
        if count!=1:
            time.sleep(600)

def refresh():
    print("refresh")
    alltitles = gw.getAllTitles()

    myrefreshlist.delete(0, tk.END)
    for t in alltitles:
        if "天使之戀Online - " in t:
            myrefreshlist.insert(tk.END, t)
    myrefreshlist.config(width=0)
    myrefreshlist.select_set(0)


dirname = os.path.dirname(os.path.abspath(__file__))
new_model = tf.keras.models.load_model(os.path.join(dirname, 'my_model.h5'))
labels = [',', 0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

def find_now_position(gwcontent):
    # 使用
    # crop image
    center_x = int(gwcontent.left + gwcontent.width/2) - 1
    center_y = int(gwcontent.top + gwcontent.height/2) -1 + 18

    shot = pyautogui.screenshot(region=[gwcontent.right - gwcontent.width * 1 / 6 + 60, gwcontent.top + 130, 55, 13]) # x,y,w,h
    # shotfile = os.path.join(base_path, str(uuid.uuid4()) + '.png')
    # shot.save(shotfile)
    open_cv_image = np.array(shot)
    # Convert RGB to BGR 
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    img_gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
    # apply binary thresholding
    ret, thresh = cv2.threshold(img_gray, 150, 255, cv2.THRESH_BINARY)                        
    # draw contours on the original image
    image_copy = open_cv_image.copy()
    contours, hierarchy = cv2.findContours(image=thresh, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
    print("---")

    height = 30
    width = 30

    results = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        crop_img = image_copy[y:y+h, x:x+w]
            
        top = math.ceil((height - h) / 2)
        left = math.ceil((width - w) / 2)
        bottom = top
        right = left
            
        if (top * 2) + h > height:
            top = top - 1
        if (left * 2) + w > width:
            left = left - 1
            
        a =  cv2.copyMakeBorder(crop_img, top, bottom, left, right, cv2.BORDER_CONSTANT,value=[132,121,8])

        color_coverted = cv2.cvtColor(a, cv2.COLOR_BGR2RGB)
        a=Image.fromarray(color_coverted)
        a = np.expand_dims(a, axis=0) # 轉換通道            
            
        pred = new_model.predict(a)[0]
        index = np.argmax(pred)
        prediction = labels[index]        
        results.append((x, prediction))
        
    results.sort(key = lambda s: s[0])
    my_lst_str = ''.join(str(results[i][1]) for i in range(len(results)))
    x = my_lst_str.split(",")
    
    return int(x[0]), int(x[1]), center_x, center_y
    
def go_target(target_x, target_y, now_x:int, now_y:int, center_x, center_y, now_window_name):
    count = 1
    while(abs(now_x - target_x) > 3):
        mouse_x = center_x
        mouse_y = center_y
        if now_x > target_x:
            mouse_x -= 40
            print("往左")
        elif now_x < target_x:
            mouse_x += 40
            print("往右")
        else:
            print("不用動")
            
        difference = target_x - now_x        
        count_loop = math.ceil(abs(difference / 3))
        print(f'執行次數 {count_loop}')
        j = 1
        while(j <= count_loop):            
            pyautogui.moveTo(mouse_x, mouse_y)
            mouseclick()
            time.sleep(2)
            j+=1
        now_x, now_y, center_x, center_y = find_now_position(now_window_name)
        count += 1
        
        if count > 8:
            print("break")
            break        
        
        print(mouse_x, mouse_y)
        time.sleep(3)
        
    count = 1
    while(abs(now_y - target_y) > 3):
        mouse_x = center_x
        mouse_y = center_y
                    
        if now_y > target_y:
            mouse_y += 35
            print("往下")
        elif now_y < target_y:
            mouse_y -= 35
            print("往上")
        else:
            print("不用動")
            
        difference = target_y - now_y        
        count_loop = math.ceil(abs(difference / 3))
        print(f'執行次數 {count_loop}')   
        j = 1
        while(j <= count_loop):            
            pyautogui.moveTo(mouse_x, mouse_y)
            mouseclick()
            time.sleep(2)
            j+=1
        now_x, now_y, center_x, center_y = find_now_position(now_window_name)
        count += 1
        
        if count > 8:
            print("break")
            break
        
        print(mouse_x, mouse_y)
        time.sleep(3)
        
    print("done")

def autopilot():    
    if machine_tag == True:    
        # 取得視窗名稱
        try:
            now_window_name = gw.getWindowsWithTitle(myrefreshlist.get(myrefreshlist.curselection()))[0]
            now_window_name.restore()
            now_window_name.activate()
            time.sleep(1)

            # 關閉打怪
            pydirectinput.keyDown("alt")    
            pydirectinput.press("d")
            pydirectinput.keyUp("alt")        
            time.sleep(2)

            # 查看現在位置
            x, y, center_x, center_y = find_now_position(now_window_name)

            # 走向目標
            position = mypgotargetlist.get(mypgotargetlist.curselection())
            position = position.split(", ")
            go_target(int(position[0]), int(position[1]), x, y, center_x, center_y, now_window_name)
        except:
            pass
    else:
        print("這台電腦無法進行machine learning")
        
# custom class
class AccountData:
    def __init__(self, account, password, second_password="", trade_password=""):
        self.account = account
        self.password = password
        self.second_password = second_password
        self.trade_password = trade_password
        
global AccountList
AccountList = []
def savedata():
    # 檢查帳號密碼都有輸入嗎?
    if(input_account.get()!="" and input_password.get()!=""):
        test = AccountData(input_account.get(), input_password.get(), input_second_password.get(), input_trade_password.get())
        AccountList.append(test)
    else:
        tk.messagebox.showinfo("Pop up", "帳號密碼沒有輸入喔")
    

def outputdata():
    print("output")
    global AccountList
    
    file_exists  = os.path.exists(os.path.join(dirname, "data.json"))
    if file_exists:
        result = tk.messagebox.askokcancel(title = '是否要刪除',message='目錄下已經有資料，確定要完全覆蓋嗎')
        if result:        
            # 假如有檔案會刪除 確定嘛!? 新增一下按鈕提示
            with open("data.json", "w") as outfile:
                # json.dump(AccountList, outfile)
                json.dump([z.__dict__ for z in AccountList], outfile)
                print(json.dumps([z.__dict__ for z in AccountList]))
        
def validate(P):
    print(P)
    if str.isdigit(P) or P == '':
        return True
    else:
        return False
    
def listbox_event(event):
    object = event.widget
    # print(type(object.curselection()))
    print(object.curselection())
    index = object.curselection()
    # mylabel.configure(text=object.get(index))
    
    
if __name__ == '__main__':    

    openlist = []
    olderlist = []
    alltitles = gw.getAllTitles()
    for t in alltitles:
        if "天使之戀Online - " in t:
            openlist.append(t)
            olderlist.append(t)

    print(openlist)
    print(olderlist)


    root = tk.Tk()

    root.title('my window')
    root.geometry('800x600')

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    mouse_position = tk.Label(root, text="滑鼠現在位置")
    get_mouse_pos()
    
    # selectmode=EXTENDED
    myaccountlist = tk.Listbox(root, exportselection=0)
    mypasswordlist = tk.Listbox(root, exportselection=0)
    
    f = open(os.path.join(dirname, 'data.json'), encoding="utf-8")
    # returns JSON object as 
    # a dictionary
    data = json.load(f)    
    # Iterating through the json
    # list
    for i in data:
        myaccountlist.insert(tk.END, i['account'])
        mypasswordlist.insert(tk.END, i['password'])
    
    print("---------------")    
    # Closing file
    # f.close()
    myaccountlist.bind("<<ListboxSelect>>", listbox_event)

    
    f2 = open(os.path.join(dirname, 'start_game.json'), encoding="utf-8")
    # returns JSON object as 
    # a dictionary
    data2 = json.load(f2)    
    # Iterating through the json
    # list
    for i in data2:
        application_path = i['application_path']
    # Closing file
    f2.close()
    
    #     
    myrefreshlist = tk.Listbox(root, exportselection=0)    

    mypgotargetlist = tk.Listbox(root, exportselection=0)    
    mypgotargetlist.insert(tk.END, '150, 124, 商人')
    mypgotargetlist.select_set(0)

    mybutton = tk.Button(root, text='主電腦3之帳號', command=lambda: threading.Thread(target = AutoOpen, args=("1")).start())
    mybutton2 = tk.Button(root, text='主電腦4之帳號', command=lambda: threading.Thread(target = AutoOpen, args=("2")).start())
    mybutton3 = tk.Button(root, text='副電腦', command=lambda: threading.Thread(target = AutoOpen, args=("3")).start())
    mybutton4 = tk.Button(root, text='自動領獎勵', command=lambda: threading.Thread(target = exe_time, args=("1")).start())
    mybutton5 = tk.Button(root, text='自動領獎勵(10分鐘自動領取)', command=lambda: threading.Thread(target = exe_time, args=("2")).start())
    mybutton6 = tk.Button(root, text='開啟選擇帳號', command=lambda: threading.Thread(target = AutoOpen, args=(" ")).start())
    mybutton_refresh = tk.Button(root, text='查看現有天使之戀視窗名稱', command=lambda: threading.Thread(target = refresh, args=("")).start())
    mybutton_gotarget = tk.Button(root, text='自動導航', command=lambda: threading.Thread(target = autopilot, args=("")).start())
    
    # 
    input_account_label = tk.Label(text = "帳號")
    input_password_label = tk.Label(text = "密碼")
    input_second_password_label = tk.Label(text = "第二組密碼")
    input_trade_password_label = tk.Label(text = "交易密碼")


    input_account = tk.Entry()    
    input_password = tk.Entry()
    input_second_password = tk.Entry()
    
    vcmd = (root.register(validate), '%P')
    input_trade_password = tk.Entry(validate='key', validatecommand=vcmd)
    save_btn=tk.Button(root, text="Save Data", command=lambda: threading.Thread(target = savedata, args=("")).start())
    output_btn=tk.Button(root, text="Output Data", command=lambda: threading.Thread(target = outputdata, args=("")).start())
    

    mybutton.grid(row=5, column=0)
    mybutton2.grid(row=5, column=1)
    mybutton3.grid(row=5, column=2)
    mybutton4.grid(row=5, column=3)
    mybutton5.grid(row=5, column=4)
    mybutton6.grid(row=5, column=5)
    mybutton_refresh.grid(row=7, column=0)
    mybutton_gotarget.grid(row=7, column=3)
   
    
    myaccountlist.grid(row=0, column=3)
    mypasswordlist.grid(row=0, column=4)
    myrefreshlist.grid(row=6, columnspan=3)
    mypgotargetlist.grid(row=6, columnspan=6)

    
    mouse_position.grid(row=0, columnspan=3)
    
    input_account_label.grid(row=8, column=0)
    input_password_label.grid(row=8, column=1)
    input_second_password_label.grid(row=8, column=2)
    input_trade_password_label.grid(row=8, column=3)
    input_account.grid(row=9, column=0)
    input_password.grid(row=9, column=1)
    input_second_password.grid(row=9, column=2)
    input_trade_password.grid(row=9, column=3)
    save_btn.grid(row=10, column=0)
    output_btn.grid(row=10, column=1)
    
    root.mainloop()
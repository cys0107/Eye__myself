from PyQt5.QtWidgets import QDialog  # 從 PyQt5 庫中導入 QDialog，用於創建對話框
from PyQt5.QtCore import QTimer  # 從 PyQt5 庫中導入 QTimer，用於創建定時器
from PyQt5.QtGui import QImage, QPixmap  # 從 PyQt5 庫中導入 QImage 和 QPixmap，用於處理和顯示圖像
from PyQt5.QtWidgets import (QApplication, QMessageBox)  # 從 PyQt5 庫中導入 QApplication（應用程序入口）和 QMessageBox（消息框）

import sqlite3  # 導入 sqlite3 模組，用於與 SQLite 資料庫交互
import cv2 as cv  # 導入 OpenCV（cv2）庫，並縮寫為 cv，用於圖像處理和計算機視覺操作
import mediapipe as mp  # 導入 Mediapipe 庫，用於姿勢和人臉地標檢測
import numpy as np  # 導入 NumPy 庫，用於數學運算和數據處理
import time  # 導入 time 模組，用於計時操作
from datetime import datetime  # 從 datetime 模組中導入 datetime，用於處理日期和時間
import matplotlib.pyplot as plt  # 導入 Matplotlib 庫，用於繪製圖表
import matplotlib.dates  # 導入 Matplotlib 中的日期模組，用於日期格式化
import math  # 導入 math 模組，用於數學運算
import eye_ui as ui  # 導入當前目錄中的 eye_ui 模組，並縮寫為 ui，用於處理 UI 元素和事件
import requests  # 導入 requests 庫，用於發送 HTTP 請求（例如與 LINE Notify API 交互）
import logging  # 導入 logging 模組，用於記錄日誌信息


# 配置日志输出
logging.basicConfig(filename='app.log', filemode='w', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 使用 logger
logger = logging.getLogger(__name__)


class Window(QDialog, ui.Ui_Dialog):
    def __init__(self):
        super().__init__()

        self.token = ''  # 用來儲存某種驗證或授權令牌的變數，初始為空字串
        self.camera = cv.VideoCapture(0)  # 使用 OpenCV 開啟相機，設備索引為 0
        self.setupUi(self)  # 初始化 UI，將 UI 元件與程式碼連結起來
        # 以下是一些 UI 元件的連結及事件處理函數的綁定
        self.user_list.currentTextChanged.connect(self.user_list_onchange)  # 當 user_list 的選項改變時，觸發 user_list_onchange 函數
        self.user_list_2.currentTextChanged.connect(lambda: self.user_list_onchange(2))  # 當 user_list_2 的選項改變時，觸發 user_list_onchange 函數（帶入參數2）
        self.confirm_push.clicked.connect(self.confirm_push_onchange)  # 當按下 confirm_push 按鈕時，觸發 confirm_push_onchange 函數
        self.add_push.clicked.connect(self.add_push_onchange)  # 當按下 add_push 按鈕時，觸發 add_push_onchange 函數
        # self.user_list.addItem('None')  # 可以將 'None' 添加到 user_list 中，但這行目前被註解掉了
        self.blink_threshold.valueChanged.connect(self.blink_threshold_onchange)  # 當 blink_threshold 的值改變時，觸發 blink_threshold_onchange 函數
        self.bright_threshold.valueChanged.connect(self.bright_threshold_onchange)  # 當 bright_threshold 的值改變時，觸發 bright_threshold_onchange 函數
        self.distance_threshold.valueChanged.connect(self.distance_threshold_onchange)  # 當 distance_threshold 的值改變時，觸發 distance_threshold_onchange 函數

        self.blink_bar.valueChanged.connect(self.blink_bar_onchange)  # 當 blink_bar 的值改變時，觸發 blink_bar_onchange 函數
        self.bright_bar.valueChanged.connect(self.bright_bar_onchange)  # 當 bright_bar 的值改變時，觸發 bright_bar_onchange 函數
        self.distance_bar.valueChanged.connect(self.distance_bar_onchange)  # 當 distance_bar 的值改變時，觸發 distance_bar_onchange 函數

        self.working_time.valueChanged.connect(self.working_time_onchange)  # 當 working_time 的值改變時，觸發 working_time_onchange 函數
        self.resting_time.valueChanged.connect(self.resting_time_onchange)  # 當 resting_time 的值改變時，觸發 resting_time_onchange 函數
        self.start_push.clicked.connect(self.start_push_onchange)  # 當按下 start_push 按鈕時，觸發 start_push_onchange 函數
        self.initialize_push.clicked.connect(self.initialize_push_onchange)  # 當按下 initialize_push 按鈕時，觸發 initialize_push_onchange 函數
        self.want_line.clicked.connect(self.want_line_onchange)  # 當按下 want_line 按鈕時，觸發 want_line_onchange 函數
        self.recommend_push.clicked.connect(self.recommend_push_onchange) #按下Recommend按鈕時，觸發recommend_push_onchange函數

        # 計時器
        self.timer_camera = QTimer()  # 初始化一個用於相機操作的定時器
        self.timer_warm = QTimer()  # 初始化另一個定時器，用於檢查狀態
        self.timer_camera.timeout.connect(self.update_progress_value)  # 當 timer_camera 逾時時，觸發 update_progress_value 函數
        self.timer_warm.timeout.connect(self.check_status)  # 當 timer_warm 逾時時，觸發 check_status 函數
        self.tabWidget.currentChanged.connect(self.change_index)  # 當 tabWidget 的當前索引改變時，觸發 change_index 函數
        # self.main.tabBarClicked.connect(self.pushButton_func,0)  # 註解掉的代碼，用於當 tabBar 被點擊時觸發特定功能
        # self.analyze.tabBarClicked.connect(self.pushButton_func,1)  # 同樣是註解掉的代碼
        self.work_time = self.working_time.value()  # 取得 working_time 控件的值，並賦值給 work_time
        self.rest_time = self.resting_time.value()  # 取得 resting_time 控件的值，並賦值給 rest_time
        self.blink_thres = self.blink_threshold.value()  # 取得 blink_threshold 控件的值，並賦值給 blink_thres
        self.bright_thres = self.bright_threshold.value()  # 取得 bright_threshold 控件的值，並賦值給 bright_thres
        self.distance_thres = self.distance_threshold.value()  # 取得 distance_threshold 控件的值，並賦值給 distance_thres
        self.exercise.addItem('None')  # 將 'None' 添加到 exercise 控件中
        self.exercise.addItem('close eye')  # 將 'close eye' 添加到 exercise 控件中
        self.exercise.addItem('jumping jack')  # 將 'jumping jack' 添加到 exercise 控件中
        # 變數初始化
        self.FONT_SIZE = 1  # 設定字體大小為 1
        # 日曆
        self.select_range.addItem('Every Minute')  # 將 'Every Minute' 添加到 select_range 控件中
        self.calendarWidget.selectionChanged.connect(self.calendar)  # 當日曆的選擇改變時，觸發 calendar 函數

        self.frame_counter = 0  # 初始化影格計數器為 0
        self.CEF_COUNTER = 0  # 初始化 CEF 計數器為 0
        self.total_blink = 0  # 初始化總眨眼次數為 0
        self.eye_area = 800  # 初始化眼部區域大小為 800
        self.ratio = 0  # 初始化比例為 0
        self.count = 0  # 初始化計數器為 0
        self.brightness_value = 0  # 初始化亮度值為 0
        # 常數設定
        self.eye_close_frame = 1  # 設定眼睛閉合的影格數為 1
        self.previous_time = 200  # 設定初始的先前時間為 200
        self.area_record = np.ones(self.previous_time)  # 使用 numpy 初始化區域記錄，長度為 previous_time
        self.FONTS = cv.FONT_HERSHEY_COMPLEX  # 設定字體為 OpenCV 的複雜字體
        self.EYE_STATE = 0  # 初始化眼睛狀態為 0（可能表示未閉合）
        self.ratio_thres = 4.5  # 設定比例閾值為 4.5
        self.eye_area_thres_high = 1500  # 設定眼部區域的高閾值為 1500
        self.eye_area_thres_low = 200  # 設定眼部區域的低閾值為 200
        self.eye_area_record = 800  # 初始化眼部區域記錄為 800
        self.eye_area_ratio = 0.7  # 設定眼部區域比例為 0.7
        # 面部邊界的索引
        self.FACE_OVAL = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]  # 面部輪廓的索引
        self.FACE_OVAL_SIM = [156, 383, 397]  # 簡化的面部輪廓索引
        # 嘴唇的索引
        self.LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95, 185, 40, 39, 37, 0, 267, 269, 270, 409, 415, 310, 311, 312, 13, 82, 81, 42, 183, 78]  # 嘴唇的索引
        self.LOWER_LIPS = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]  # 下嘴唇的索引
        self.UPPER_LIPS = [185, 40, 39, 37, 0, 267, 269, 270, 409, 415, 310, 311, 312, 13, 82, 81, 42, 183, 78]  # 上嘴唇的索引
        # 左眼的索引
        self.LEFT_EYE = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]  # 左眼的索引
        self.LEFT_EYEBROW = [336, 296, 334, 293, 300, 276, 283, 282, 295, 285]  # 左眉毛的索引
        # 右眼的索引
        self.RIGHT_EYE = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]  # 右眼的索引
        self.RIGHT_EYEBROW = [70, 63, 105, 66, 107, 55, 65, 52, 53, 46]  # 右眉毛的索引
        # 中心點
        self.CENTER_POINT = [9, 8, 168]  # 面部中心點的索引
        self.BODY = [22, 20, 18, 16, 14, 12, 24, 23, 11, 13, 15, 17, 19, 21]  # 身體的索引
        self.HEAD = [8, 6, 5, 4, 0, 1, 2, 3, 7]  # 頭部的索引
        self.map_face_mesh = mp.solutions.face_mesh  # 引入 mediapipe 的 face_mesh 模組
        self.status = 'run'  # 初始化狀態為 'run'
        self.blink_counter = 0  # 初始化眨眼計數器為 0
        self.area_counter = 0  # 初始化區域計數器為 0
        self.bright_counter = 0  # 初始化亮度計數器為 0
        self.frame_counter = 0  # 初始化影格計數器為 0
        self.passing_time = 0  # 初始化經過時間為 0

        # 記錄每分鐘的信息
        self.count_minute = 0  # 初始化分鐘計數器為 0
        self.previous_minute = 0  # 初始化前一分鐘記錄為 0
        self.count_bright = 0  # 初始化亮度計數為 0
        self.count_blink = 0  # 初始化眨眼計數為 0
        self.count_distance = 0  # 初始化距離計數為 0

        # 記錄時間
        self.previous_time_step = 0  # 初始化前一時間步為 0
        self.now_time_step = 0  # 初始化當前時間步為 0
        self.pass_time = 0  # 初始化經過時間為 0
        self.time_status = 'start'  # 初始化時間狀態為 'start'

        # 跳躍
        self.previous_state = -1  # 初始化前一狀態為 -1
        self.count_hand = 0  # 初始化手部計數器為 0
        self.count_jump = 0  # 初始化跳躍計數器為 0
        self.shoulder_pos = []  # 初始化肩膀位置的空列表
        self.mp_pose = mp.solutions.pose  # 引入 mediapipe 的 pose 模組
        self.mp_drawing = mp.solutions.drawing_utils  # 引入 mediapipe 的 drawing_utils 模組
        self.current_user = str(self.user_list.currentText())  # 取得當前使用者列表的文字
        self.con = sqlite3.connect('database.db')  # 連接到名為 'database.db' 的 SQLite 資料庫
        self.cursorObj = self.con.cursor()  # 創建一個游標物件來執行資料庫操作
        self.cursorObj.execute('create table if not exists None(year, month, day, hour, minute, distance, brightness, blink, state)')  # 創建一個名為 None 的資料表（如果不存在）
        self.cursorObj.execute('create table if not exists threshold(user, line_token,distance_area,distance_ratio, brightness, blink, UNIQUE(user))')  # 創建一個名為 threshold 的資料表，記錄使用者的設定，且 user 欄位需唯一
        self.cursorObj.execute("insert or ignore into threshold(user,line_token, distance_area,distance_ratio, brightness, blink) VALUES (?,?,?,?,?,?)", ('None', '', self.eye_area_record, self.eye_area_ratio, 60, 4))  # 如果沒有記錄，則插入一筆默認的使用者設定
        self.con.commit()  # 提交資料庫變更
        cursor = self.cursorObj.execute("SELECT * from threshold").fetchall()  # 查詢 threshold 資料表中的所有記錄
        for row in cursor:
            self.user_list.addItem(row[0])  # 將查詢到的使用者名稱添加到 user_list 中
            self.user_list_2.addItem(row[0])  # 同時將使用者名稱添加到 user_list_2 中
            print(row)  # 列印查詢到的記錄
        self.con.commit()  # 再次提交資料庫變更


    def __del__(self):
        self.update_database()  # 在物件被銷毀時，更新資料庫
        self.summary_report()  # 生成當天的摘要報告
        self.connection.close()  # 關閉資料庫連接

    def closeEvent(self, event):
        self.summary_report()  # 當應用程式視窗被關閉時，生成當天的摘要報告

    def lineNotifyMessage(self, msg):
        try:
            headers = {
                "Authorization": "Bearer " + self.token,  # 授權標頭，使用 Bearer Token 進行驗證
                "Content-Type" : "application/x-www-form-urlencoded"  # 設定內容類型為 x-www-form-urlencoded
            }
            
            payload = {'message': msg}  # 要發送的訊息
            r = requests.post("https://notify-api.line.me/api/notify", headers=headers, params=payload)  # 發送 HTTP POST 請求給 LINE Notify API
        except:
            pass  # 如果發生任何異常，忽略並繼續

    def summary_report(self):
        year = datetime.today().strftime("%Y")  # 取得當前年份
        month = datetime.today().strftime("%m")  # 取得當前月份
        day = datetime.today().strftime("%d")  # 取得當前日期
        today_date = datetime.today().strftime("%Y-%m-%d")  # 取得當前完整日期（格式為 YYYY-MM-DD）
        print(year, month, day)  # 在控制台打印當前日期資訊
        
        self.cursorObj = self.con.cursor()  # 獲取資料庫游標
        
        # 查詢當前使用者在當天的所有資料（年、月、日、時、分、距離、亮度、眨眼次數、狀態）
        cursor = self.cursorObj.execute(
            "SELECT year, month, day, hour, minute, distance, brightness, blink, state "
            "from %s WHERE year=%s AND month=%s AND day=%s" % (self.current_user, year, month, day)
        )
        self.con.commit()  # 提交查詢操作
        
        # 初始化用於存儲查詢結果的列表
        date = []
        dis = []
        bri = []
        blink = []
        use = []
        
        # 遍歷查詢結果並將數據添加到相應的列表中
        for i in cursor:
            use.append(i[8])  # 添加狀態資訊（如「使用中」、「缺席」、「休息」等）
            dis.append(float(i[5]))  # 添加距離數據
            bri.append(int(i[6]))  # 添加亮度數據
            blink.append(int(i[7]))  # 添加眨眼次數
        
        if len(use) != 0:  # 如果查詢結果不為空
            use_time = use.count(2)  # 計算「使用中」狀態的分鐘數
            not_time = use.count(1)  # 計算「缺席」狀態的分鐘數
            rest_time = use.count(0)  # 計算「休息」狀態的分鐘數
            avg_dis = sum(dis) / len(dis)  # 計算平均距離
            avg_bri = sum(bri) / len(bri)  # 計算平均亮度
            avg_blink = sum(blink) / len(blink)  # 計算平均眨眼次數
            
            if self.want_line.isChecked():  # 如果使用者選擇了要發送 LINE 通知
                # 發送當天的摘要報告到 LINE Notify
                self.lineNotifyMessage(
                    today_date + '\n use time : ' + str(use_time) + ' minutes \n absent time : ' + str(not_time) + ' minutes \n rest time : ' + str(rest_time) + ' minutes'
                    + '\n average distance : ' + str(avg_dis) + ' \n average brightness : ' + str(avg_bri) + ' \n average blink : ' + str(avg_blink)
                )
            
            # 在控制台打印使用時間、缺席時間、休息時間以及平均距離、亮度和眨眼次數
            print(' use time : ', str(use_time), '\n absent time', str(not_time), '\n rest time', str(rest_time))
            print(' average distance: ', avg_dis, '\n average brightness', avg_bri, '\n average blink', avg_blink)

    def want_line_onchange(self):
        if self.want_line.isChecked():  # 檢查是否勾選了 "Use Line" 選項
            self.line_token.setEnabled(True)  # 如果勾選，啟用 LINE Token 的輸入框
        else:
            self.line_token.setEnabled(True)  # 如果未勾選，禁用 LINE Token 的輸入框
                    

    def change_index(self, value):
        self.stackedWidget.setCurrentIndex(value)  # 根據傳入的索引值，改變 stackedWidget 的當前顯示頁面
        
    def user_list_onchange(self, user=1):
        self.update_database()  # 更新資料庫
        self.current_user = str(self.user_list.currentText())  # 根據 user_list 的當前選擇設定 current_user
        if user == 2:
            self.current_user = str(self.user_list_2.currentText())  # 如果 user 參數為 2，則使用 user_list_2 的當前選擇
            self.calendar()  # 更新日曆視圖
        
        # 連接到資料庫，並根據當前用戶查詢其設定
        self.con = sqlite3.connect('database.db')
        self.cursorObj = self.con.cursor()
        cursor = self.cursorObj.execute(
            "SELECT user, line_token, distance_area, distance_ratio, brightness, blink FROM threshold WHERE user = '%s'" 
            % (self.current_user,)
        )
        self.con.commit() 
        
        # 更新 UI 控件的值為查詢到的設定
        for row in cursor:
            self.blink_threshold.setValue(float(row[5]))
            self.bright_threshold.setValue(float(row[4]))
            self.distance_threshold.setValue(float(row[3]))
            self.eye_area_record = (float(row[2]))
            self.token = row[1]
        self.con.commit()  # 提交資料庫更改

    def add_user_onchange(self):
        pass  # 這個函數目前沒有實現，可能用於將新用戶添加到系統

    def confirm_push_onchange(self):
        self.initialize_push.setEnabled(True)  # 啟用 "initialize_push" 按鈕
        self.start_push.setEnabled(True)  # 啟用 "start_push" 按鈕
        self.recommend_push.setEnabled(True)  # 啟用 "recommend_push" 按鈕
        self.line_token.setText(self.token)  # 將 token 的值顯示在 line_token 的輸入框中
        self.start_time = time.time()  # 設定開始時間為當前時間
        self.status = 'run'  # 設定狀態為 'run'
        self.timer_camera.start(5)  # 啟動相機計時器，每5毫秒執行一次
        self.timer_warm.start(30)  # 啟動警告計時器，每30毫秒執行一次
        self.current_user = str(self.user_list.currentText())  # 確保設定了當前用戶
        print(f'Current user set to: {self.current_user}')  # 在控制台打印當前用戶

    def calendar(self):
        selectDay = self.calendarWidget.selectedDate()  # 獲取日曆控件中選擇的日期
        year = selectDay.toString("yyyy")  # 取得所選年份
        month = selectDay.toString("M")  # 取得所選月份
        day = selectDay.toString("d")  # 取得所選日期
        print(year, month, day)  # 在控制台打印所選日期
        
        # 查詢資料庫中該用戶在所選日期的記錄
        self.cursorObj = self.con.cursor()
        cursor = self.cursorObj.execute(
            "SELECT year, month, day, hour, minute, distance, brightness, blink, state FROM %s WHERE year=%s AND month=%s AND day=%s"
            % (self.current_user, year, month, day)
        )
        self.con.commit() 
        
        # 初始化數據列表
        date = []
        dis = []
        bri = []
        blink = []
        use = []
        
        # 將查詢結果添加到相應的列表中
        for i in cursor:
            date.append(datetime(i[0], i[1], i[2], i[3], i[4]))
            use.append(i[8])
            dis.append(float(i[5]))
            bri.append(int(i[6]))
            blink.append(int(i[7]))
        
        # 設置圖表的日期格式
        xfmt = matplotlib.dates.DateFormatter('%H:%M')
        datestime = matplotlib.dates.date2num(date)
        print((datestime, dis))  # 在控制台打印日期時間和距離的數據
        
        # 繪製使用時間的圖表
        plt.gca().xaxis.set_major_formatter(xfmt)
        plt.plot_date(datestime, use, linestyle='solid')
        plt.ylim(-0.1, 2.1)
        plt.title('Using Time')
        plt.savefig('use.png')  # 保存圖表為圖片
        plt.close()

        self.display_image(cv.imread('use.png'), (400, 270), self.use_time_graph)  # 顯示使用時間的圖表
        plt.plot_date(datestime, dis, linestyle='solid')
        plt.ylim(0, 2)
        plt.title('Distance')
        plt.savefig('dis.png')
        plt.close()

        self.display_image(cv.imread('dis.png'), (400, 270), self.distance_graph)  # 顯示距離的圖表
        plt.plot_date(datestime, bri, linestyle='solid')
        plt.ylim(0, 255)
        plt.title('Brightness')
        plt.savefig('bri.png')
        plt.close()

        self.display_image(cv.imread('bri.png'), (400, 270), self.brightness_graph)  # 顯示亮度的圖表
        plt.plot_date(datestime, blink, linestyle='solid')
        plt.ylim(0, 60)
        plt.title('Blinking')
        plt.savefig('blink.png')
        plt.close()

        self.display_image(cv.imread('blink.png'), (400, 270), self.blink_graph)  # 顯示眨眼次數的圖表


    def display_image(self, img, size, target):
        show = cv.resize(img, size)  # 將圖像調整為指定的大小
        # show = cv.cvtColor(show, cv.COLOR_BGR2RGB)  # 可選的圖像轉換，將 BGR 轉換為 RGB（目前被註解掉）
        showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)  # 將圖像轉換為 QImage 格式
        target.setPixmap(QPixmap.fromImage(showImage))  # 將轉換後的圖像設置為 target 元件的 Pixmap

    def add_push_onchange(self):
        text = str(self.add_user.text())  # 取得用戶在 add_user 輸入框中輸入的文本
        self.user_list.addItem(text)  # 將用戶輸入的文本添加到 user_list 列表
        self.user_list_2.addItem(text)  # 將用戶輸入的文本添加到 user_list_2 列表
        self.add_user.clear()  # 清空 add_user 輸入框
        if text != '':  # 如果輸入的文本不為空
            self.con = sqlite3.connect('database.db')  # 連接到 SQLite 資料庫
            self.cursorObj = self.con.cursor()  # 創建一個游標對象以執行 SQL 操作
            try:
                print(f'Creating table for user: {text}')  # 打印正在為新用戶創建表格的訊息
                # 創建一個新的表格（如果不存在），以存儲該用戶的數據
                self.cursorObj.execute(f'CREATE TABLE IF NOT EXISTS {text} (year INTEGER, month INTEGER, day INTEGER, hour INTEGER,\
                                            minute INTEGER, distance REAL, brightness INTEGER, blink INTEGER, state INTEGER)')
                # 將新用戶的初始閾值設定插入到 threshold 表中（如果尚未存在）
                self.cursorObj.execute("INSERT OR IGNORE INTO threshold (user, line_token, distance_area, distance_ratio, brightness, \
                                        blink) VALUES (?, ?, ?, ?, ?, ?)", (text, self.line_token.text(), self.eye_area_record, self.eye_area_ratio, 60, 4))
                self.con.commit()  # 提交資料庫變更
                print(f'Table created and initial data inserted for user: {text}')  # 打印表格創建成功的訊息
            except Exception as e:
                self.showDialog('Not valid name!')  # 如果出現錯誤，顯示錯誤對話框
                print(f'Error creating table or inserting data for user {text}: {e}')  # 打印錯誤訊息
        else:
            print('empty')  # 如果輸入的文本為空，打印提示訊息

    def working_time_onchange(self):
        self.work_time = self.working_time.value()  # 當工作時間控件的值改變時，更新 work_time 變數

    def resting_time_onchange(self):
        self.rest_time = self.resting_time.value()  # 當休息時間控件的值改變時，更新 rest_time 變數

    def initialize_push_onchange(self):
        br = self.ratio * 1.18  # 計算新的眨眼閾值
        bv = self.brightness_value * 0.65  # 計算新的亮度閾值
        dis = 0.7  # 設定距離閾值
        self.blink_threshold.setValue(br)  # 將眨眼閾值設置到相應控件
        self.bright_threshold.setValue(bv)  # 將亮度閾值設置到相應控件
        self.distance_threshold.setValue(dis)  # 將距離閾值設置到相應控件
        self.eye_area_record = self.eye_area  # 更新眼部區域記錄
        self.update_database()  # 將新的閾值更新到資料庫
        
    def calculate_averages(self):
            # 連接資料庫
            con = sqlite3.connect('database.db')
            cursor = con.cursor()

            # 查詢distance, brightness數據
            query = "SELECT distance, brightness FROM test"  
            cursor.execute(query)
              
            results = cursor.fetchall() # 獲取結果         
            con.close() # 關閉數據庫連接

            # 初始化變量
            sum_distance = 0
            sum_brightness = 0
            
            # 記錄行數
            num_rows = len(results)

            # 計算總和
            for row in results:
                sum_distance += row[0]
                sum_brightness += row[1]           

            # 計算平均值
            avg_distance = sum_distance / num_rows if num_rows > 0 else 0
            avg_brightness = sum_brightness / num_rows if num_rows > 0 else 0

            return avg_distance, avg_brightness

    def recommend_push_onchange(self):
        avg_distance, avg_brightness= self.calculate_averages()
        self.blink_threshold.setValue(3.3)  # 將眨眼閾值設置到相應控件
        self.bright_threshold.setValue(avg_brightness)  # 將亮度閾值設置到相應控件
        self.distance_threshold.setValue(avg_distance)  # 將距離閾值設置到相應控件


    def update_database(self):
        # 更新當前用戶的閾值設定到資料庫中
        self.cursorObj.execute("UPDATE threshold SET distance_area = %s, distance_ratio = %s ,  brightness= %s , blink=%s  WHERE user='%s'"\
                                % (self.eye_area, self.distance_threshold.value(), self.bright_threshold.value(), self.blink_threshold.value(), self.current_user))
        self.con.commit()  # 提交資料庫變更

    def start_push_onchange(self):
        self.counter = -1  # 初始化計數器
        self.pass_time = 0.01  # 初始化經過時間
        if self.want_line.isChecked():  # 如果選擇了 "Use Line"
            self.lineNotifyMessage('start')  # 發送開始訊息到 LINE
        self.status = 'start'  # 更新狀態為 'start'
        self.time_status = 'work'  # 更新時間狀態為 'work'
        self.previous_minute = 0  # 重置前一分鐘的記錄
        self.init_time = time.time()  # 記錄初始時間
        self.previous_time_step = time.time()  # 記錄前一時間步

    def blink_threshold_onchange(self):
        self.blink_thres = self.blink_threshold.value()  # 更新眨眼閾值變數
        self.blink_bar.setValue(int(self.blink_thres * 10))  # 更新眨眼進度條的值

    def blink_bar_onchange(self):
        self.blink_thres = self.blink_bar.value() / 10  # 更新眨眼閾值變數
        self.blink_threshold.setValue(self.blink_thres)  # 更新眨眼閾值控件的值

    def bright_threshold_onchange(self):
        self.bright_thres = self.bright_threshold.value()  # 更新亮度閾值變數
        self.bright_bar.setValue(int(self.bright_thres))  # 更新亮度進度條的值

    def bright_bar_onchange(self):
        self.bright_thres = self.bright_bar.value()  # 更新亮度閾值變數
        self.bright_threshold.setValue(self.bright_thres)  # 更新亮度閾值控件的值

    def distance_threshold_onchange(self):
        self.distance_thres = self.distance_threshold.value()  # 更新距離閾值變數
        self.distance_bar.setValue(int(self.distance_thres * 100))  # 更新距離進度條的值

    def distance_bar_onchange(self):
        self.distance_thres = self.distance_bar.value() / 100  # 更新距離閾值變數
        self.distance_threshold.setValue(self.distance_thres)  # 更新距離閾值控件的值

    def check_status(self):
        if self.status == 'start':  # 如果狀態為 'start'
            if self.area_counter > 2:  # 如果區域計數器超過2
                self.showDialog('Too close', line=True)  # 顯示 "Too close" 的對話框
                self.area_counter = 0  # 重置區域計數器
            if self.bright_counter > 20:  # 如果亮度計數器超過20
                self.bright_counter = 0  # 重置亮度計數器

    ''' eye detection function '''

    def PolyArea(self, x, y):
        # 計算多邊形的面積
        return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))

    # landmark detection function 
    def landmarksDetection(self, img, results, draw=False, body=False):
        img_height, img_width = img.shape[:2]  # 取得圖像的高度和寬度
        if body == False:
            # 提取面部地標座標
            mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.multi_face_landmarks[0].landmark]
        else:
            # 提取身體地標座標
            mesh_coord = [(int(point.x * img_width), int(point.y * img_height)) for point in results.pose_world_landmarks.landmark]
        if draw:
            # 如果 draw 為 True，則在圖像上繪製地標點
            [cv.circle(img, p, 2, (0,255,0), -1) for p in mesh_coord]
        return mesh_coord  # 返回地標座標列表

    # Euclidean distance 
    def euclaideanDistance(self, point, point1):
        # 計算兩個點之間的歐幾里得距離
        x, y = point
        x1, y1 = point1
        distance = math.sqrt((x1 - x)**2 + (y1 - y)**2)
        return distance

    def blinkRatio(self, img, landmarks, right_indices, left_indices):
        # 計算右眼的眨眼比率
        rh_right = landmarks[right_indices[0]]
        rh_left = landmarks[right_indices[8]]
        rv_top = landmarks[right_indices[12]]
        rv_bottom = landmarks[right_indices[4]]

        # 計算左眼的眨眼比率
        lh_right = landmarks[left_indices[0]]
        lh_left = landmarks[left_indices[8]]
        lv_top = landmarks[left_indices[12]]
        lv_bottom = landmarks[left_indices[4]]

        # 計算右眼和左眼的橫向和縱向距離
        rhDistance = self.euclaideanDistance(rh_right, rh_left)
        rvDistance = self.euclaideanDistance(rv_top, rv_bottom)
        lvDistance = self.euclaideanDistance(lv_top, lv_bottom)
        lhDistance = self.euclaideanDistance(lh_right, lh_left)

        # 計算右眼和左眼的眨眼比率
        reRatio = rhDistance / rvDistance
        leRatio = lhDistance / lvDistance

        # 計算兩眼的平均眨眼比率
        ratio = (reRatio + leRatio) / 2
        return ratio


    def get_average_brightness(self, image, mesh_coords, frame_height, frame_width):
        # 計算圖像的亮度值，使用加權的RGB值（灰度轉換公式）
        lum = image[:, :, 0] * 0.144 + image[:, :, 1] * 0.587 + image[:, :, 2] * 0.299
        # 計算整個圖像的平均亮度
        vals = np.average(lum)
        # 如果計算結果為 NaN（無效值），則返回 0
        if math.isnan(vals):
            return 0
        else:
            # 否則返回平均亮度值
            return vals

    def colorBackgroundText(self, img, text, font, fontScale, textPos, textThickness=1, textColor=(0, 255, 0), bgColor=(0, 0, 0), pad_x=3, pad_y=3):
        # 獲取文本的寬度和高度，基於字體、字體大小和字體厚度
        (t_w, t_h), _ = cv.getTextSize(text, font, fontScale, textThickness)
        x, y = textPos
        # 在文本背景上繪製一個填充的矩形，用於使文本更清晰
        cv.rectangle(img, (x - pad_x, y + pad_y), (x + t_w + pad_x, y - t_h - pad_y), bgColor, -1)
        # 繪製文本在指定位置，帶有指定的字體、大小和顏色
        cv.putText(img, text, textPos, font, fontScale, textColor, textThickness)
        return img  # 返回修改後的圖像

    def showDialog(self, text, line=True):
        # 創建一個消息框，用於顯示警告
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)  # 設置消息框的圖標為警告
        msgBox.setText(text)  # 設置消息框的文本為傳遞進來的字符串
        msgBox.setWindowTitle("Warning")  # 設置消息框的標題為 "Warning"
        msgBox.exec()  # 顯示消息框
        if line and self.want_line.isChecked():  # 如果需要發送 LINE 通知並且 Use Line 選項被選中
            self.lineNotifyMessage(text)  # 將相同的警告信息發送到 LINE

    def get_state_body(self, results):
        up_state = 1  # 定義手臂上抬的狀態值
        down_state = -1  # 定義手臂下放的狀態值
        # 獲取不同身體部位的地標位置
        left_wrist = results.pose_world_landmarks.landmark[15]  # 左手腕
        left_pinky = results.pose_world_landmarks.landmark[17]  # 左小指
        right_wrist = results.pose_world_landmarks.landmark[16]  # 右手腕
        right_pinky = results.pose_world_landmarks.landmark[18]  # 右小指
        left_hip = results.pose_world_landmarks.landmark[23]  # 左臀部
        right_hip = results.pose_world_landmarks.landmark[24]  # 右臀部
        nose = results.pose_world_landmarks.landmark[0]  # 鼻子
        # 判斷手臂位置：如果手腕位置高於鼻子位置，則為上抬狀態
        if left_wrist.y < nose.y and right_wrist.y < nose.y:
            return up_state  # 返回上抬狀態
        # 如果小指位置低於臀部位置，則為下放狀態
        elif left_pinky.y > left_hip.y and right_pinky.y > right_hip.y:
            return down_state  # 返回下放狀態
        # 如果都不符合上述條件，返回 0 表示中間狀態
        return 0

    def update_progress_value(self):
        try:
            logger.info("update_progress_value started")  # 記錄更新進度值的開始
            if self.status != 'rest':  # 如果當前狀態不是 "rest"（休息）
                logger.info("status is not rest")
                # 使用 FaceMesh 模組進行人臉地標檢測
                with self.map_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
                    self.frame_counter += 1  # 增加影格計數器
                    ret, frame = self.camera.read()  # 從相機讀取一幀畫面
                    frame_height, frame_width = frame.shape[:2]  # 獲取畫面的高度和寬度
                    rgb_frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)  # 將畫面從 BGR 轉換為 RGB 格式
                    results = face_mesh.process(rgb_frame)  # 使用 FaceMesh 模組處理 RGB 畫面
                    FONT = cv.FONT_HERSHEY_COMPLEX  # 設置字體樣式

                    if results.multi_face_landmarks:  # 如果檢測到多張人臉地標
                        logger.info("Detected face landmarks")
                        self.record_state = 2  # 設置記錄狀態為 2（表示人臉檢測到）
                        if self.time_status == 'work':  # 如果當前處於工作狀態
                            self.pass_time += (time.time() - self.previous_time_step)  # 增加經過的工作時間
                            self.previous_time_step = time.time()  # 更新前一個時間步驟
                        else:
                            self.pass_time += 0  # 如果不處於工作狀態，經過時間不變
                        if self.status == 'start':  # 如果狀態為 "start"
                            self.time_status = 'work'  # 將時間狀態設置為 "work"

                        # 檢測到人臉後提取相關地標
                        mesh_coords = self.landmarksDetection(frame, results, False)
                        # 計算右眼和左眼的區域面積
                        right_eye_area = self.PolyArea(np.array([mesh_coords[p] for p in self.RIGHT_EYE])[:, 0], np.array([mesh_coords[p] for p in self.RIGHT_EYE])[:, 1])
                        left_eye_area = self.PolyArea(np.array([mesh_coords[p] for p in self.LEFT_EYE])[:, 0], np.array([mesh_coords[p] for p in self.LEFT_EYE])[:, 1])
                        self.eye_area = (right_eye_area + left_eye_area) / 2  # 計算兩眼的平均區域面積
                        self.ratio = self.blinkRatio(frame, mesh_coords, self.RIGHT_EYE, self.LEFT_EYE)  # 計算眨眼比率
                        self.brightness_value = self.get_average_brightness(rgb_frame, mesh_coords, frame_height, frame_width)  # 計算平均亮度
                        self.eyestate = 0  # 設置眼睛狀態為 0（眨眼）

                        if self.ratio > self.blink_threshold.value():  # 如果眨眼比率超過閾值
                            self.blink_counter += 1  # 增加眨眼計數器
                            # 在畫面中顯示 "Blink" 字樣
                            self.colorBackgroundText(frame, f'Blink', FONT, self.FONT_SIZE, (int(frame_height / 2), 100), 2, (0, 255, 255), pad_x=6, pad_y=6)
                        else:  # 否則認為眼睛張開
                            if self.blink_counter >= self.eye_close_frame:  # 如果眨眼計數器達到設定的閾值
                                self.eyestate = 1  # 設置眼睛狀態為 1（表示眨眼）
                                self.total_blink += 1  # 增加總眨眼次數
                                self.blink_counter = 0  # 重置眨眼計數器

                        # 如果眼部面積比例小於距離閾值，表示太靠近攝像頭
                        if (self.eye_area_record / self.eye_area) ** 0.5 < self.distance_threshold.value():
                            self.area_counter += 1  # 增加區域計數器
                            if self.area_counter > 2:  # 如果區域計數器超過2，顯示 "Too close" 提示
                                self.colorBackgroundText(frame, f'Too close', FONT, self.FONT_SIZE, (int(frame_height / 2), 150), 2, (0, 255, 255), pad_x=6, pad_y=6)
                                if self.area_counter > 60:  # 如果區域計數器超過60，顯示對話框提示太靠近
                                    self.showDialog('Too close', line=True)
                        else:
                            self.area_counter = 0  # 如果距離正常，重置區域計數器

                        # 如果亮度低於設定的閾值，顯示 "Too dim" 提示
                        if self.brightness_value < self.bright_threshold.value():
                            self.bright_counter += 1
                            if self.bright_counter > 20:  # 如果亮度計數器超過20次，顯示 "Too dim" 提示
                                self.colorBackgroundText(frame, f'Too dim', FONT, self.FONT_SIZE, (int(frame_height / 2), 150), 2, (0, 255, 255), pad_x=6, pad_y=6)
                        else:
                            self.bright_counter = 0  # 如果亮度正常，重置亮度計數器

                        # 顯示當前的眨眼次數、眼部區域、眼部距離比例、亮度等資訊
                        self.colorBackgroundText(frame, f'Total Blinks: {self.total_blink}', FONT, self.FONT_SIZE / 2, (30, 150), 2)
                        # 在畫面中繪製左眼、右眼和臉部輪廓
                        cv.polylines(frame, [np.array([mesh_coords[p] for p in self.LEFT_EYE], dtype=np.int32)], True, (0, 255, 0), 1, cv.LINE_AA)
                        cv.polylines(frame, [np.array([mesh_coords[p] for p in self.RIGHT_EYE], dtype=np.int32)], True, (0, 255, 0), 1, cv.LINE_AA)
                        cv.polylines(frame, [np.array([mesh_coords[p] for p in self.FACE_OVAL], dtype=np.int32)], True, (0, 0, 255), 1, cv.LINE_AA)
                    else:
                        logger.info("No face landmarks detected")
                        self.previous_time_step = time.time()  # 如果沒有檢測到人臉地標，更新前一個時間步驟
                        self.record_state = 1  # 記錄狀態設置為1（表示未檢測到人）

                    # 計算並顯示畫面的FPS（每秒幀數）
                    self.fps_pass_time = time.time() - self.start_time
                    fps = self.frame_counter / self.fps_pass_time
                    # 顯示眼部區域、眼部距離比例、眨眼比率、亮度和FPS
                    self.colorBackgroundText(frame, f'Eye area : {self.eye_area}', FONT, self.FONT_SIZE / 2, (30, 90), 1)
                    self.colorBackgroundText(frame, f'Eye Distance ratio: {round((self.eye_area_record / self.eye_area) ** 0.5, 2)}', FONT, self.FONT_SIZE / 2, (30, 120), 1)
                    self.colorBackgroundText(frame, f'Eye Ratio: {round(self.ratio, 2)}', FONT, self.FONT_SIZE / 2, (30, 150), 1)
                    self.colorBackgroundText(frame, f'Brightness: {round(self.brightness_value, 1)}', FONT, self.FONT_SIZE / 2, (30, 180), 1)
                    self.colorBackgroundText(frame, f'FPS: {round(fps, 1)}', FONT, self.FONT_SIZE / 2, (30, 60), 1)
                    # 調整畫面大小並轉換為RGB格式，以便顯示在UI中
                    show = cv.resize(frame, (800, 600))
                    show = cv.cvtColor(show, cv.COLOR_BGR2RGB)
                    showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
                    self.camera_label.setPixmap(QPixmap.fromImage(showImage))  # 將處理後的畫面顯示在相機標籤上


            # 如果選擇的運動是 "jumping jack"
            elif self.exercise.currentText() == 'jumping jack':
                logger.info("Exercise is jumping jack")  # 記錄運動類型為 "jumping jack"
                FONTS = cv.FONT_HERSHEY_COMPLEX  # 設置字體樣式
                self.record_state = 1  # 記錄狀態設置為 1，表示正在進行跳躍運動
                # 使用 Mediapipe 的 Pose 模組進行姿勢檢測
                with self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=0) as pose:
                    success, image = self.camera.read()  # 從相機中讀取一幀畫面
                    image = cv.resize(image, None, fx=0.5, fy=0.5, interpolation=cv.INTER_CUBIC)  # 將畫面縮小一半以提高處理速度
                    image.flags.writeable = False  # 設置圖像為不可寫狀態，以提高處理速度
                    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)  # 將圖像從 BGR 轉換為 RGB 格式
                    results = pose.process(image)  # 使用 Pose 模組處理圖像，檢測姿勢地標
                    image = cv.cvtColor(image, cv.COLOR_RGB2BGR)  # 將圖像轉回 BGR 格式，便於顯示
                    if results.pose_world_landmarks:  # 如果檢測到姿勢地標
                        logger.info("Detected pose landmarks")  # 記錄成功檢測到姿勢地標
                        self.record_state = 0  # 記錄狀態設置為 0，表示成功檢測到姿勢
                        # 提取姿勢地標的座標，並在圖像上不進行繪製（draw=False），但包含身體地標（body=True）
                        mesh_coords = self.landmarksDetection(image, results, False, True)
                        # 如果當前的身體狀態與前一狀態相反（即手臂從下到上或從上到下），則計數
                        if self.get_state_body(results) == -self.previous_state:
                            self.previous_state = self.get_state_body(results)  # 更新之前的狀態
                            self.count_hand += 1  # 增加手臂運動次數計數
                            logger.info(f"Hand count: {self.count_hand}, Jump count: {self.count_jump}")  # 記錄手臂計數和跳躍計數

                        self.count = self.count_hand  # 更新當前的計數
                        image.flags.writeable = True  # 恢復圖像可寫狀態
                        # 在圖像上繪製檢測到的姿勢地標和連接（關節之間的線條）
                        self.mp_drawing.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
                    image = cv.flip(image, 1)  # 水平翻轉圖像，以便更自然地顯示給使用者
                    # 在圖像上顯示跳躍次數，並將文字放置在圖像的 (30, 200) 位置，字體大小為 0.7，背景為黑色，文字為綠色
                    image = self.colorBackgroundText(image, f'Total : {int(self.count / 2)}', FONTS, 0.7, (30, 200), 1)
                    show = cv.resize(image, (800, 600))  # 調整圖像大小，以適應 UI 中顯示的畫布大小
                    show = cv.cvtColor(show, cv.COLOR_BGR2RGB)  # 將圖像轉換為 RGB 格式，以便 QImage 正確處理顏色
                    showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)  # 將處理後的圖像轉換為 QImage 格式，便於在 PyQt 中顯示
                    self.camera_label.setPixmap(QPixmap.fromImage(showImage))  # 將圖像顯示在 UI 的相機標籤上


            # 如果選擇的運動是 "close eye" 或 "None"
            elif self.exercise.currentText() == 'close eye' or self.exercise.currentText() == 'None':
                logger.info(f"Exercise is {self.exercise.currentText()}")  # 記錄當前的運動類型
                # 使用 Mediapipe 的 FaceMesh 模組進行人臉地標檢測
                with self.map_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
                    self.frame_counter += 1  # 增加影格計數器
                    ret, frame = self.camera.read()  # 從相機中讀取一幀畫面
                    frame_height, frame_width = frame.shape[:2]  # 獲取畫面的高度和寬度
                    rgb_frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)  # 將畫面從 BGR 轉換為 RGB 格式
                    results = face_mesh.process(rgb_frame)  # 使用 FaceMesh 模組處理 RGB 畫面
                    FONT = cv.FONT_HERSHEY_COMPLEX  # 設置字體樣式

                    if results.multi_face_landmarks:  # 如果檢測到多張人臉地標
                        logger.info("Detected face landmarks")  # 記錄成功檢測到人臉地標
                        self.record_state = 0  # 記錄狀態設置為 0，表示成功檢測到人臉
                        # 提取面部地標座標，並不在圖像上進行繪製（draw=False）
                        mesh_coords = self.landmarksDetection(frame, results, False)
                        # 計算右眼和左眼的區域面積
                        right_eye_area = self.PolyArea(np.array([mesh_coords[p] for p in self.RIGHT_EYE])[:,0], np.array([mesh_coords[p] for p in self.RIGHT_EYE])[:,1])
                        left_eye_area = self.PolyArea(np.array([mesh_coords[p] for p in self.LEFT_EYE])[:,0], np.array([mesh_coords[p] for p in self.LEFT_EYE])[:,1])
                        self.eye_area = (right_eye_area + left_eye_area) / 2  # 計算兩眼的平均區域面積
                        self.ratio = self.blinkRatio(frame, mesh_coords, self.RIGHT_EYE, self.LEFT_EYE)  # 計算眨眼比率
                        self.brightness_value = self.get_average_brightness(rgb_frame, mesh_coords, frame_height, frame_width)  # 計算平均亮度

                        # 如果眨眼比率超過閾值，或者選擇的運動是 "None"（表示閉眼）
                        if self.ratio > self.blink_threshold.value() or self.exercise.currentText() == 'None':
                            self.eyestate = 1  # 設置眼睛狀態為 1（表示閉眼）
                            self.pass_time += (time.time() - self.previous_time_step)  # 增加經過時間
                            self.previous_time_step = time.time()  # 更新前一個時間步驟
                            # 在畫面中顯示 "Close" 字樣
                            self.colorBackgroundText(frame, f'Close', FONT, self.FONT_SIZE, (int(frame_height / 2), 100), 2, (0, 255, 255), pad_x=6, pad_y=6)
                        else:  # 否則認為眼睛張開
                            self.eyestate = 0  # 設置眼睛狀態為 0（表示張開）
                            self.pass_time += 0  # 經過時間保持不變
                            self.previous_time_step = time.time()  # 更新前一個時間步驟

                        # 在畫面中繪製左眼、右眼和臉部輪廓
                        cv.polylines(frame, [np.array([mesh_coords[p] for p in self.LEFT_EYE], dtype=np.int32)], True, (0, 255, 0), 1, cv.LINE_AA)
                        cv.polylines(frame, [np.array([mesh_coords[p] for p in self.RIGHT_EYE], dtype=np.int32)], True, (0, 255, 0), 1, cv.LINE_AA)
                        cv.polylines(frame, [np.array([mesh_coords[p] for p in self.FACE_OVAL], dtype=np.int32)], True, (0, 0, 255), 1, cv.LINE_AA)

                    # 計算並顯示畫面的FPS（每秒幀數）
                    self.fps_pass_time = time.time() - self.start_time
                    fps = self.frame_counter / self.fps_pass_time
                    # 顯示眼部區域、眼部距離比例、眨眼比率、亮度和FPS
                    self.colorBackgroundText(frame, f'Eye area : {self.eye_area}', FONT, self.FONT_SIZE / 2, (30, 90), 1)
                    self.colorBackgroundText(frame, f'Eye Distance ratio: {round((self.eye_area_record / self.eye_area) ** 0.5, 2)}', FONT, self.FONT_SIZE / 2, (30, 120), 1)
                    self.colorBackgroundText(frame, f'Eye Ratio: {round(self.ratio, 2)}', FONT, self.FONT_SIZE / 2, (30, 150), 1)
                    self.colorBackgroundText(frame, f'Brightness: {round(self.brightness_value, 1)}', FONT, self.FONT_SIZE / 2, (30, 180), 1)
                    self.colorBackgroundText(frame, f'FPS: {round(fps, 1)}', FONT, self.FONT_SIZE / 2, (30, 60), 1)
                    # 調整畫面大小並轉換為RGB格式，以便顯示在UI中
                    show = cv.resize(frame, (800, 600))
                    show = cv.cvtColor(show, cv.COLOR_BGR2RGB)
                    showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
                    self.camera_label.setPixmap(QPixmap.fromImage(showImage))  # 將圖像顯示在 UI 的相機標籤上


            # 如果選擇的運動是 "None"（無運動）
            elif self.exercise.currentText() == 'None':
                # 計算經過的時間，從上一次時間步驟到現在
                self.pass_time = (time.time() - self.previous_time_step)
                # 將時間狀態設置為 "relax"（放鬆狀態）
                self.time_status = 'relax'

            # 如果狀態是 "start" 或 "rest"
            if self.status == 'start' or self.status == 'rest':
                if self.status == 'start':  # 如果狀態是 "start"
                    # 計算剩餘的工作時間（總工作時間減去已經經過的時間）
                    remain_time = self.work_time * 60 - self.pass_time
                elif self.status == 'rest':  # 如果狀態是 "rest"
                    # 計算剩餘的休息時間（總休息時間減去已經經過的時間）
                    remain_time = self.rest_time * 60 - self.pass_time

                # 計算剩餘時間的時、分、秒
                hour = remain_time // 3600
                minute = (remain_time - (hour * 3600)) // 60
                second = (remain_time - (hour * 3600) - (minute * 60))

                # 更新進度條的值，表示經過的時間佔總時間的百分比
                self.Progress_progressBar.setValue(int(self.pass_time / (remain_time + self.pass_time) * 100))
                # 更新顯示器中的時間
                self.Time_Hour_lcdNumber.display(str(int(hour)))
                self.Time_Minute_lcdNumber.display(str(int(minute)))
                self.Time_Second_lcdNumber.display(str(int(second)))

                # 計數和累加亮度值、眨眼次數、眼部距離等數據
                self.count_minute += 1
                self.count_bright += self.brightness_value
                self.count_blink += self.eyestate
                self.count_distance += (self.eye_area_record / self.eye_area) ** 0.5

                # 計算經過的分鐘數
                pass_minute = (time.time() - self.init_time) // 60
                # 如果經過的分鐘數超過了上一分鐘
                if pass_minute > self.previous_minute:
                    logger.info('save')  # 記錄保存信息
                    self.previous_minute = pass_minute  # 更新上一分鐘的值
                    # 計算平均亮度、眨眼次數和眼部距離
                    bright_avg = int(self.count_bright / self.count_minute)
                    blink_avg = self.count_blink
                    distance_avg = round(self.count_distance / self.count_minute, 3)

                    # 重置計數器
                    self.count_bright = 0
                    self.count_blink = 0
                    self.count_distance = 0
                    self.count_minute = 0

                    # 獲取當前時間的詳細資訊
                    result = time.localtime(time.time())
                    logger.info(f"Inserting data: {int(result.tm_year)}, {int(result.tm_mon)}, {int(result.tm_mday)}, {int(result.tm_hour)}, {int(result.tm_min)}, {distance_avg}, {bright_avg}, {blink_avg}, {self.record_state}")

                    try:
                        # 如果狀態是 "start"，插入工作時間的數據
                        if self.status == 'start':
                            self.cursorObj.execute(
                                "INSERT OR IGNORE INTO %s(year, month, day, hour, minute, distance, brightness, blink, state) VALUES (?,?,?,?,?,?,?,?,?)" % self.current_user,
                                (int(result.tm_year), int(result.tm_mon), int(result.tm_mday), int(result.tm_hour), int(result.tm_min), distance_avg, bright_avg, blink_avg, self.record_state)
                            )
                        # 如果狀態是 "rest"，插入休息時間的數據，這裡距離、亮度、眨眼次數使用固定值（1, 10, 10）
                        elif self.status == 'rest':
                            self.cursorObj.execute(
                                "INSERT OR IGNORE INTO %s(year, month, day, hour, minute, distance, brightness, blink, state) VALUES (?,?,?,?,?,?,?,?,?)" % self.current_user,
                                (int(result.tm_year), int(result.tm_mon), int(result.tm_mday), int(result.tm_hour), int(result.tm_min), 1, 10, 10, self.record_state)
                            )
                        # 提交更改到資料庫
                        self.con.commit()
                        logger.info("Data inserted.")  # 記錄數據插入信息
                    except Exception as e:
                        logger.error(f"Error inserting data: {e}")  # 如果插入數據出錯，記錄錯誤信息


             # 如果剩餘時間小於 0 且當前狀態為 "start"
            if remain_time < 0 and self.status == 'start':
                logger.info('rest')  # 記錄進入休息狀態
                self.status = 'rest'  # 將狀態設置為 "rest"（休息）
                self.pass_time = 0.01  # 重置經過時間
                self.previous_time_step = time.time()  # 更新上一次時間步驟
                self.blink_counter = 0  # 重置眨眼計數器
                self.showDialog('Rest Now', line=True)  # 顯示休息提示對話框，並通過 LINE 發送通知（如果已啟用）

            # 如果剩餘時間小於 0 或已經完成預設的運動次數，且當前狀態為 "rest"
            elif (remain_time < 0 or self.count >= self.excerise_count.value()) and self.status == 'rest':
                logger.info('finish rest')  # 記錄完成休息
                self.showDialog('finish rest')  # 顯示完成休息的對話框
                self.count = 0  # 重置計數器
                self.count_hand = 0  # 重置手部計數器
                self.status = 'start'  # 將狀態設置為 "start"（開始）
                self.pass_time = 0.01  # 重置經過時間
                self.blink_counter = 0  # 重置眨眼計數器
                self.start_push_onchange()  # 調用開始按鈕的事件處理函數，進行下一輪運動

        # 捕獲並記錄任何例外情況
        except Exception as e:
            logger.error(f"Exception: {e}")
            pass


    def fetch_and_display_data():
        # Connect to the SQLite database
        con = sqlite3.connect('database.db')
        cursor = con.cursor()

        # Query to fetch all historical data (assuming it's stored in a table like 'history_data')
        query = "SELECT * FROM test"  # Replace 'history_data' with the actual table name
        cursor.execute(query)
        
        # Fetch all results
        results = cursor.fetchall()
        
        # Close the database connection
        con.close()

        # Print the results in a table-like format
        for row in results:
            print(" | ".join(map(str, row)))

    # Call the function to fetch and display the data
    fetch_and_display_data()





# 主程式入口
if __name__ == '__main__':
    app = QApplication([])  # 創建一個 QApplication 對象
    # apply_stylesheet(app, theme='dark_blue.xml')  # 可選：應用一個樣式表來改變應用程序的外觀（目前註釋掉）
    window = Window()  # 創建主視窗對象
    window.show()  # 顯示主視窗
    app.exec()  # 啟動應用程序主循環

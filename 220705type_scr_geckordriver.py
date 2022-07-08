from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

# driver = webdriver.Firefox()

#EC2でのエラー回避。220705"Expected browser binary location, but unable to find binary in default location, no 'moz:firefoxOptions.binary' capability provided, and no binary flag set on the command line.

# options = Options()
# options.binary_location = FirefoxBinary('/usr/bin/firefox')
# driver = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver', options=options)

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)


# #第一ブロック 必要なモジュール類をインポート

##ローカル、リモート切り替えパート。220404
media_name = 'type'
file_media_name = 'type'

#ローカル実施時用。220702
date = '220701'

#EC2用マスター
chrome_driver_path_ec2 = '/usr/local/bin/chromedriver'
output_path_ec2 = '/root/' + file_media_name + '_csv_files_s/'
judge_file_path_ec2 = '/root/'
#ローカル用マスター
chrome_driver_path_local = '/Users/yusukekurimoto/Dropbox/210226baklis_scr_files/chromedriver103'
output_path_local = '/Users/yusukekurimoto/Dropbox/baklis_csv_files/' + date + 'output_files/'
judge_file_path_local = '/Users/yusukekurimoto/Dropbox/210226baklis_scr_files/'

#EC2用切り替え
chrm_path = chrome_driver_path_ec2
output_path = output_path_ec2
judge_file_path = judge_file_path_ec2

#ローカル用切り替え
# chrm_path = chrome_driver_path_local
# output_path = output_path_local
# judge_file_path = judge_file_path_local



#1. 必要なモジュールをインポート
import time
t1 = time.time()

import pandas as pd
from lxml import html
from selenium import webdriver
#201122 想定される例外を3つインポート
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
#210409 新規にエラーを追加
from selenium.common.exceptions import UnexpectedAlertPresentException
#220701 新規に追加。
from selenium.common.exceptions import InvalidSessionIdException
import re
#↓追記201202
import os
import csv
import datetime
#xlsx形式で吐き出すため追記。211210
import openpyxl
from openpyxl.styles.fonts import Font
from line_profiler import LineProfiler
import pattern_text as pt
pat = pt.get_pattern_text()
#ここでptを塗り替えてしまってる、、ゆくゆく直す
import city_pattern_text as pt
city_pat = pt.get_city_pattern_text()
#栗本自作『都道府県補完』モジュール。220321
import complement_pref as cp
#メール送信のモジュールをインポート。211024
import smtplib, ssl
from email.mime.text import MIMEText
#ファイル作成のライブラリをインポート。211208
import pathlib
# import sys, codecs
# sys.stdout = codecs.getwriter("utf-16")(sys.stdout)
#半角化するモジュール。220314
import unicodedata
# #chromedriverの自動更新モジュール。220702
# # from webdriver_manager.chrome import ChromeDriverManager
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# #Seleinim4に必要なモジュール。220702
# from selenium.webdriver.chrome.service import Service as ChromeService
#Seleinum4に必要なモジュール。(geckodriverだけかも)22705
from selenium.webdriver.common.by import By

# options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#TimeOutエラー対処のため、以下オプションを追加
options.add_argument("start-maximized")
options.add_argument("enable-automation")
options.add_argument("--disable-infobars")
options.add_argument('--disable-extensions')
options.add_argument("--disable-browser-side-navigation")
options.add_argument("--disable-gpu")
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')


prefs = {"profile.default_content_setting_values.notifications" : 2}
options.add_experimental_option("prefs",prefs)
#以下はエラーが出る
# driver = new ChromeDriver(options);


#ロギングのインポート。211024
import logging
#1, ロガーの生成
logger = logging.getLogger(__name__)
#2, 出力レベルの設定
logger.setLevel(logging.INFO)

#3-1, ファイルハンドラの設定
today = datetime.datetime.today()
file_name = '{0:%y%m%d}'.format(today) + file_media_name + '_.log'
f_handler = logging.FileHandler(output_path + file_name)
logger.addHandler(f_handler)
#3-2, ストリームハンドラの設定
s_handler = logging.StreamHandler()
logger.addHandler(s_handler)
#4-1, フォーマッタの生成
fmt = logging.Formatter('%(asctime)s %(message)s _%(levelname)s')
#4-2,ハンドラにフォーマッタを登録
f_handler.setFormatter(fmt)
s_handler.setFormatter(fmt)

#Gmailの設定を書き込む
gmail_account = "bhmarketing96010@gmail.com"
#二段階認証に変更。211027
gmail_password = "krsvljvzbqwaflgl"
# メールの送信先★ --- (*2)
mail_to = "baklis@blueheats.com"

# #Chromedriverバージョンアップ2009011730
# service = ChromeService(executable_path= chrm_path)
# # driver = webdriver.Chrome(executable_path= chrm_path, options=options)
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
# driver.quit()

# driver = webdriver.Chrome(service=service, options=options)


driver.implicitly_wait(10)
#ページの読み込み最大待ち時間の指定する
driver.set_page_load_timeout(40)
#crash対策 201130
driver.set_window_size(1000, 1500)


#3-1. 空のdfを作っておく。
heading_columns = ['求人ID', '企業ID', '取得日', '媒体名', '社名', '法人名', '法人名補足', '電話番号', '電話番号ハイフンなし',
                                   '掲載期間', '掲載開始日', '情報更新日', '掲載終了日', '職種大分類', '職種中分類', '職種小分類',
                                   '掲載社名', '媒体記載職種', '事業内容', '本社住所', '業種', '従業員数', '資本金', '売上高',
                                   '設立', '勤務地', '給与', '勤務時間', '待遇・福利厚生', '休日・休暇', '仕事内容',
                                   '求めている人材', '雇用区分', 'メールアドレス',
                                   '郵便番号', 'お問合せ住所', '採用担当', '募集背景', 'お問合せ都道府県', 'お問合せ市区町村',
                                   'お問合せ町域', '広告プラン', '掲載URL', '企業HP', '従業員数レンジ', '未経験フラグ', 
                                    '転勤なしフラグ', '設立年数値', '株式公開フラグ', '資本金レンジ', '派遣会社フラグ', 
                                   '給与区分', '給与下限(万円)', '給与上限(万円)', '英語スキルフラグ', '外国籍活躍フラグ', '想定決算月', '売上高レンジ']
df_info = pd.DataFrame(columns = heading_columns)
    
    
#3-2. 要素有り、無し分岐の独自関数を定義
def check_exists_element(element):
    try:
        driver.find_element(By.CSS_SELECTOR,element)
        return True
    except NoSuchElementException:
        return False

##ここまでは定義

#=======================================================
#第二ブロック 分割ファイルを読み込み、リスト型で抽出する。

#2. 求人詳細URLを取得。次のページへ進み、全件取得する。
#2-1.サイトのベースとなるURLを変数に入れる。


#6-2, ec2起動開始のメール送信。211221
# 以下にGmailの設定を書き込む★ --- (*1)
gmail_account = "bhmarketing96010@gmail.com"
#二段階認証に変更。211027
gmail_password = "krsvljvzbqwaflgl"
# メールの送信先★ --- (*2)
mail_to = "baklis@blueheats.com"

# メールデータ(MIME)の作成 --- (*3)
# msj = logger.info(media_name + "の収集が完了しました。")
# subject = msj

#もしlogger内容でメール送信できなければ、↓に変更する。
now = datetime.datetime.now()
now_time = f"{now:%Y-%m-%d %H:%M:%S}"
subject = now_time + '【' + file_media_name  + "】のec2が起動しました。"

#本文はブランクでOK。211210
body = file_media_name + "のec2が起動しました。"

msg = MIMEText(body, "html")
msg["Subject"] = subject
msg["To"] = mail_to
msg["From"] = gmail_account

# Gmailに接続 --- (*4)
server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
    context=ssl.create_default_context())
server.login(gmail_account, gmail_password)
server.send_message(msg) # メールの送信
# print("メール送信 complete.")
logger.info("メール送信 complete.")


t1 = time.time()

# def scrape():

#2. 求人詳細URLを取得。次のページへ進み、全件取得する。
#2-1.サイトのベースとなるURLを変数に入れる。


type_base_url = 'https://type.jp/job/search.do?pathway=37&offset='

page_count = 0

#ログ用のナンバー
pre_num = 0

#合計求人数を取得するために、一度アクセス。
type_employment_list_url = type_base_url + str(page_count) 
driver.get(type_employment_list_url)

#2-2.合計求人件数を取得
total_offer_number = driver.find_element(By.CSS_SELECTOR,'.job-list .items-per-page .whole-num .num')
total_offer_number = total_offer_number.text
total_offer_number = total_offer_number.replace(',', '')
logger.info('\n' + '【typeの合計求人件数は、' + str(total_offer_number) + '件です】' + '\n')

#2-3-1.◯○件分の求人詳細URL, ベース広告プランを入れる空のリストを作っておく。
offer_employment_url_li = []
advertising_plan_li = []


#2-4-1.○○件分のURLを取得する
#切り上げ処理
#本番用
#＋２０は不要だったことに気づいた。220702
# while page_count <= int(total_offer_number) + 20:
while page_count <= int(total_offer_number):
#テスト用
# while page_count <= 600:

    #度々エラー吐くので例外処理追記。220701
    for _ in range(4):  # 最大5回実行。
        try:
            #2-4-2.求人一覧ページにアクセス
            type_employment_list_url = type_base_url + str(page_count)
            # time.sleep(1)
            #エラー回避追記。220701

#             driver.implicitly_wait(40)
#             driver.set_page_load_timeout(60)
#             #ここにも待機入れたらWebDriverExceptionエラーが収まった。220702
#             time.sleep(1.5)
            driver.get(type_employment_list_url)
            #待機を上からここに移動した。2→３。220702
            time.sleep(1)


            #2-4-3.○件分の求人詳細URLを取得し、リストに突っ込む。
            offer_employment_url_element_li = driver.find_elements(By.CSS_SELECTOR,'.mod-job-info-item .mod-job-info-footer .submit-btn')
            for offer_employment_url_element in offer_employment_url_element_li:
                offer_employment_url_element = offer_employment_url_element.find_element(By.CSS_SELECTOR,'a')
                offer_employment_url = offer_employment_url_element.get_attribute('href')   
                offer_employment_url_li.append(offer_employment_url)
        #         logger.info(offer_employment_url)


            #2-4-5. プラン判別のため、○件分の一覧画面要素を取得
            offer_employment_url_objects = driver.find_elements(By.CSS_SELECTOR,'.mod-job-info-item')

            for offer_employment_url_object in offer_employment_url_objects:
                offer_employment_url_div = offer_employment_url_object.find_element(By.CSS_SELECTOR,'.mod-job-info-item > div')
                offer_employment_url_class_1 = offer_employment_url_div.get_attribute('class')

                if not 'no-sub-img' in offer_employment_url_class_1:
                    advertising_plan = 'type-D'

                else:
                    offer_employment_url_td = offer_employment_url_div.find_element(By.CSS_SELECTOR,'td:nth-of-type(2)')
                    offer_employment_url_class_2 = offer_employment_url_td.get_attribute('class')
                    #message付きは詳細画面のタブで判断する。
                    if offer_employment_url_class_2 == 'sub-img':
                        advertising_plan = 'type-A/type-B'
                    elif offer_employment_url_class_2 == 'caption':
                        advertising_plan = 'type-C'

        #         logger.info(advertising_plan)
                advertising_plan_li.append(advertising_plan)

        except TimeoutException as e:
            logger.info("タイムアウトしました。リトライします。")
            # pass  # 失敗時はスルーする。
            continue
        #追加。220630
        except WebDriverException:
            logger.info('エラー：WebDriverException')
            time.sleep(3)
            pass
            continue
        except InvalidSessionIdException:
            logger.info('エラー：InvalidSessionIdException')
            time.sleep(3)
            pass
            # continue
        else:
            break  # 失敗しなかった時はループを抜ける
    else:
    #     raise TimeoutException("タイムアウトエラー")
        pass  # リトライが全部失敗した時はスルーする。


    pre_num += 20
    if pre_num % 40 == 0:
        logger.info('\n' + '【' + str(pre_num) + '件のデータ取得完了' + '】' + '\n')
        
    #メモリ不足対策 300→2000→(エラー出るので)500件に一度リフレッシュ 220701
    if pre_num % 5000 == 0:
        #都度driverインスタンス立ち上げに変更。220522
        #closeを削除。220616
        # driver.close()
        driver.quit()
        driver = webdriver.Chrome(executable_path= chrm_path, options=options)

       
    #次のページへ繰る。
    page_count += 20


    
#2-5. URLとベースプランを入れる辞書を作る。
url_plan_dic = {}
url_plan_dic.update(zip(offer_employment_url_li, advertising_plan_li))

dic_figs = len(url_plan_dic)
logger.info('\n' + '【typeの取得url数は、' + str(dic_figs) + '件です】' + '\n')


#2-6.エラー対策で、urlをcsvで出力。220304追記
df_type_url = pd.DataFrame(list(url_plan_dic.items()),columns=['url', 'ad_plan'])

type_url_file = 'temporary_type_url_files.csv'
df_type_url.to_csv(output_path + type_url_file)


t2 = time.time()
elapsed_time = t2-t1
logger.info(f"経過時間：{elapsed_time}")


# prof = LineProfiler()
# prof.add_function(scrape)
# prof.runcall(scrape)
# prof.logger.info_stats()

#=====================================================================
#ここから第三ブロック　データ収集、保存


now = datetime.datetime.now()
now_time = f"{now:%Y-%m-%d %H:%M:%S}"
subject = now_time + '【' + media_name  + "】の収集を開始します。"

#本文はブランクでOK。211210
body = media_name  + "の収集を開始します。"

msg = MIMEText(body, "html")
msg["Subject"] = subject
msg["To"] = mail_to
msg["From"] = gmail_account

# Gmailに接続 --- (*4)
server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
    context=ssl.create_default_context())
server.login(gmail_account, gmail_password)
server.send_message(msg) # メールの送信
# logger.info("メール送信 complete.")
logger.info("メール送信 complete.")


t3 = time.time() 

# #従業員数レンジのマスターの定義。210627
ran_1 = '(1) ～50人未満'
ran_2 = '(2) 50～100人未満'
ran_3 = '(3) 100～300人未満'
ran_4 = '(4) 300～500人未満'
ran_5 = '(5) 500～1000人未満'
ran_6 = '(6) 1000～3000人未満'
ran_7 = '(7) 3000～5000人未満'
ran_8 = '(8) 5000人以上'

#資本金レンジのマスターの定義。210830
cap_ran_1 = '(1) 750万円未満'
cap_ran_2 = '(2) 750万円以上1500万円未満'
cap_ran_3 = '(3) 1500万円以上3000万円未満'
cap_ran_4 = '(4) 3000万円以上5000万円未満'
cap_ran_5 = '(5) 5000万円以上1億円未満'
cap_ran_6 = '(6) 1億円以上5億円未満'
cap_ran_7 = '(7) 5億以上10億円未満'
cap_ran_8 = '(8) 10億円以上'

#売上高レンジのマスターの定義。220227
sales_ran_1 = '(1) 3億円未満'
sales_ran_2 = '(2) 3億円以上10億円未満'
sales_ran_3 = '(3) 10億円以上50億円未満'
sales_ran_4 = '(4) 50億円以上100万円未満'
sales_ran_5 = '(5) 100億円以上300億円未満'
sales_ran_6 = '(6) 300億円以上500億円未満'
sales_ran_7 = '(7) 500億以上1,000億円未満'
sales_ran_8 = '(8) 1,000億円以上'


#取得した件数を格納する変数を定義
num = 1


#4. 2で取得した求人詳細URLリストをforで回し、データ取得する。
for offer_employment_url, advertising_plan in url_plan_dic.items():
    for _ in range(5):  # 最大10回実行。
        try:
            logger.info(offer_employment_url)
            driver.get(offer_employment_url)  # 失敗しそうな処理
            time.sleep(1)
            
            #4. タブに"企業メッセージ"がある場合、"募集情報"をクリック。
            tabs_text = driver.find_element(By.CSS_SELECTOR, '.detail-local-nav')
            tabs_text = tabs_text.text

            if '企業メッセージ' in tabs_text:
                offer_employment_url = driver.find_element(By.CSS_SELECTOR, '.mod-link-list-mini a')
                offer_employment_url = offer_employment_url.get_attribute('href')
                driver.get(offer_employment_url)
                logger.info('『募集情報』ページへ移動します。')
                time.sleep(1)
                advertising_plan = 'type-A_message'
                
        except WebDriverException:
            logger.info('エラー：WebDriverException')
            #Chromeが予期しない理由で終了した場合の処理。220702
            driver.quit()
            time.sleep(1)
#             driver = webdriver.Chrome(service=service, options=options)
            driver = webdriver.Firefox()
            time.sleep(1)
            pass
        except InvalidSessionIdException:
            logger.info('エラー：InvalidSessionIdException')
            time.sleep(3)
            pass
        else:
            break  # 成功時はループを抜ける
        
        #pass



    #エラー例外処理のための try 
    try:

    # 4-0,前原稿の変数を全てクリア 201201
        publication_period = ''
        publication_start = ''
        information_updated = ''
        publication_end = ''
        occupation_major = ''
        occupation_medium = ''
        occupation_minor = ''
        company_name_original = ''
        occupation_type = ''
        company_name = ''
        corporate_name = ''
        corporate_sup = ''
        company_business = ''
        company_location = ''
        company_industry = ''
        company_employees = ''
        capital_stock = ''
        company_sales = ''
        company_establishment = ''
        work_location = ''
        salary = ''
        work_hours = ''
        welfare = ''
        holiday = ''
        job_description = ''
        application_conditions = ''
        employment_status = ''
        phone_number = ''
        phone_number_nonehyphen = ''
        mail_address = ''
        postal_code = ''
        street_address = ''
        charge_person = ''
        recruitment_background = ''
        contact_prefecture = ''
        contact_city  = ''
        contact_town = ''
#         advertising_plan = ''
        publication_url = ''
        applicant_id = ''
        company_id = ''
        corporate_url = ''
        company_employees_range = ''
        inexperienced_flag = ''
        #追加。210908
        public_offering = ''
        no_transfer = ''
        temp_staffing = ''
        establishment_num = ''
        stock_range = ''
        salary_class = ''
        lower_salary = ''
        upper_salary = ''
        english_skill = ''
        foreigner_activity = ''
        closing_month= ''
        sales_range = ''
        
        #4-0. today
        now = datetime.datetime.now()
        today = "{:%Y/%m/%d}".format(now)

        media_name = 'type'


        # 4-1,掲載期間・掲載開始日・掲載終了日の取得
        publication_period = driver.find_element(By.CSS_SELECTOR,'.head_udr .ico_end')
        publication_period = publication_period.text

        publication_period = re.sub(r'[亜-熙纊-黑予：（） ]','', publication_period)
        publication_period = publication_period.replace('.', '/')

        publication_start = re.search(r'([0-9/]*)(?=～)', publication_period)
        publication_start = publication_start.group()
        #以下2022/3/1→2022/03/01に修正スクリプト。（do,riku,ecr,toraのみ）220320
        publication_start = datetime.datetime.strptime(publication_start, '%Y/%m/%d')
        publication_start = f"{publication_start:%Y/%m/%d}"
        
        publication_end = re.search(r'(?<=～)([0-9/]*)', publication_period)
        publication_end = publication_end.group()
        #以下2022/3/1→2022/03/01に修正スクリプト。（do,riku,ecr,toraのみ）220320
        publication_end = datetime.datetime.strptime(publication_end, '%Y/%m/%d')
        publication_end = f"{publication_end:%Y/%m/%d}"

        #"り2"を消す処理
        publication_period = publication_start + '～' + publication_end


        # # 4-2,掲載職種大分類・中分類・小分類、業種
        #typeの職種中分類はパンくずに残らないからver1では割愛。
        occupation_total = driver.find_element(By.CSS_SELECTOR,'.breadcrumbs-inner')

        occupation_major = occupation_total.find_element(By.CSS_SELECTOR,'li:nth-of-type(2) span')
        occupation_major = occupation_major.text
        #logger.info(occupation_major)

        occupation_medium = occupation_total.find_element(By.CSS_SELECTOR,'li:nth-of-type(3) span')
        occupation_medium = occupation_medium.text
        #logger.info(occupation_medium)

        company_industry_element_li = driver.find_elements(By.CSS_SELECTOR,'.space-section .inner .index-section')
        for company_industry_element in company_industry_element_li:
            company_industry_text = company_industry_element.text
            if '業種から探す' in company_industry_text:
                company_industry = company_industry_element.find_element(By.CSS_SELECTOR,'.mod-link-list-horizontal')
                company_industry = company_industry.text
                company_industry = company_industry.replace('\n', '/')
                #logger.info(company_industry)


        # #4-3. 掲載社名
        # #4-4. 媒体記載職種
        company_name_original = driver.find_element(By.CSS_SELECTOR,'.corp-link')
        company_name_original = company_name_original.text
#         logger.info(company_name_original)
        logger.info(company_name_original)

        company_name = company_name_original


#============================================================
#ここから法人名、法人名補足のマスター

        #4-3-0.まずは、純粋な法人名を割り出す。
        
        #はたらいくは|(株)|（株）|(有)|を株式会社、有限会社に置き換える処理を入れる。201220
        company_name = company_name.replace('(株)', '株式会社').replace('（株）', '株式会社').replace('(有)', '有限会社').replace('（有）', '有限会社').replace('(医社)', '医療法人社団').replace('(医)', '医療法人').replace('(社)', '社団法人')
        
        #『株式会社〜事務所』が含まれない場合は、そのまま表記する
        legal_personality = re.search(r'^(?=.*(株式会社|有限会社|合同会社|学校法人|医療法人|社会福祉法人|事務所|独立行政法人|相互会社|生活協同組合|公益社団法人|特定非営利活動法人|企業組合|一般社団法人|社会医療法人|社会保険労務士法人|日本赤十字社|中国国際航空公司|税理士法人|NPO法人|国立大学法人|国立研究開発法人|ハイウェイ協同組合)).*$', company_name)
        if not legal_personality:
            #company_nameから装飾を削除する。
            corporate_name = re.sub(r'[ 　【】（）()/／◆「」『』※～~<>＜＞≪≫|★、]', '', company_name)
            corporate_sup = ''
        #         logger.info(corporate_name)
        else:
            #『合同募集』が含まれる場合は、そのまま表記する
            corporate_name = re.search(r'^(?=.*合同募集).*$', company_name)
            if corporate_name:
                corporate_name = company_name
                corporate_sup = ''
            #合同募集でない場合の処理
            else:
                #『会社名』から括弧の中を削除する。
                corporate_delsup_ele = re.search(r'[（(【<＜≪～~〔].+[）)】>＞≫～~〕]',  company_name)
                if corporate_delsup_ele:
                    corporate_delsup = corporate_delsup_ele.group()
                    corporate_name_1 = company_name.replace(corporate_delsup, '')
            #         logger.info(corporate_name_1)
                else:
                    corporate_name_1 = company_name

                #4-3-1.『corporate_name_1』から括弧外の補足（事業部、支社など）を削除する。
                #記号で社名をスプリット
                #[]←も入れたい。エスケープすればいいのかな。201210
                split_name_li = re.split('[ 　【】（）()/／◆「」『』※～~<>＜＞|★、◎]', corporate_name_1)
            #     logger.info(split_name_li)

                for split_name in split_name_li:
                    #法人名補足を削除するため、事業部名、店舗名などがつくワードを洗い出す。
                    #前部は含まれると除かれたくない単語、後部は含まれると除く単語。どんどん追加していく。
                    corporate_delsup_2 = re.search(r'^(?!.*株式会社|有限会社|合同会社|学校法人|医療法人|社会福祉法人|独立行政法人|相互会社|事務所|生活協同組合|公益社団法人|特定非営利活動法人|特定医療法人|企業組合|一般社団法人|社会医療法人|国立研究開発法人|NPO法人|会計事務所|三協管理センター|鍋浦のこ目立センター｜大宮商店|船橋中央自動車学校|小室商店|藤木商店|笠川工務店|伊藤工務店|広報企画センター|西商店|二村商店|サカイ引越センター|前田営工センター|岡田商店|左近商店|伊藤商店|日本衛生センター|クリエーションセンター|永岡医院|岩江クリニック|門田医院|鴨居病院|江口医院|苅安賀自動車学校|冨士喜本店|井上清助商店|ゆびすい労務センター|神田歯科医院|東京広域事務センター|大塚製薬工場|東京個別指導学院|コーディネーションセンター|キャリアデザインセンター|研究支援センター|技術研究センター|サンタックオフィス|谷田病院|JFR情報センター|木村屋|阿部長商店|がん研究センター|早田工務店|分析センター|近藤建材店|中央グループ|鈴木工務店|中央労務オフィス|臨床検査センター|法研中部|みつもりデンタル|らくだケア|サンタックス|くまの歯科|明石市立市民病院|よしだ歯科|今治繊維|九州建設|大川インテリア|丸喜工務店|太田歯科医院|かじはら歯科|五十子|神田ウィメンズ|日本建築センター|ＪＰＣＥＲＴ|椿デンタル|長澤工務店|亜細亜友の会|日本スポーツ振興|飯田商店|アエラ小児|広沢自動車学校|紛争処理|吉山塗料店|石井工務店|モリカワ会計|シルバー人材|埼玉県産業|日本会計|札幌ハート|鈴木酒造店|豊能障害|花巻病院|バウムクーヘン|広島平和|甲府昭和店|新町クリニック|欧州連合|京都ジョブパーク|新情報センター|インターオフィス|タックスオフィス|神戸海星病院|Nidec|早田工務店|熊谷環境分析センター|近藤建材店|富士学院|貝沼商店|ミニクリーン中部|法研中部|加藤工務店|明石市立市民病院|堀田工務店|今治繊維リソースセンター|九州建設マネジメントセンター|社会医療法人聖ルチア会|八幡病院|丸喜工務店|機能訓練センター|長澤工務店|亜細亜友の会外語学院|吉田クリニック|健康長寿医療センター|社会保険労務士法人|川越市シルバー|上野村きのこセンター|国民生活センター|マンション住替|儀間商店|東京紙店|木下商店|共立メンテナンスグループ|萩原商店|Ｔ.クリエーションセンター|がん研究センター).*(佐賀製作所|キッズクリニック鷺沼|直取引|ダスキン津田|オフィス迎賓館|転職エージェント|飯田橋駅前教室|グループ傘下|東京中央美容外科|西日本ユニット|HRバリュー事業|IT派遣|関東事務所|東海ブロック|関西事務所|明聖高等学校|中野キャンパス|おおしま皮膚科|お寺でおみおくり|ジャック幼児教育研究所|曙ゴルフガーデン|スイーツ新大阪|大阪南部ブロック|第一倉庫|名古屋オフィス|東中部カンパニー|経営企画本部|ナレッジバンク|モバイルユニット|住居余暇本部|友愛記念病院|ホームブリスイン野田|きらら歯科|携われる|建物管理|横浜アクア|そよかぜ|清風霊園|開設準備室|ふれあい館|ビジネススペあいの郷|ＩＴサービス室|ほけんの窓口|GS1Japan|社名変更|東急不動産|住友商事|ー東証一部上場ー|ステーション綾瀬|整備工場|ー北海道空港グループー|ズ・ジャパン|だらぼち|和食居酒屋|北関東カンパニー|遊び|学ぶ|小中部|高校部|続けています。|指導キャンパス|DEC統括|M-Shine|町CS|STLASSH|事業局|くるみの森保育園|北部ステーション|イベント事務局|播磨自動車教習所|北口教室|大宝塚ゴルフクラブ|大阪西店|土佐堀|南部ブロック|老人ホーム|東住吉|にっこり山城|名古屋商科大学|飛鳥未来高等学校|名古屋キャンパス|モバイルユニット|山内会計事務所|みなとみらい耳鼻咽喉科|観洋|出資|上場企業|グループ企業|上場|つつじ荘|のとだらぼち|生活事業|出資会社|出資企業|こうのとり|LANDooZ|個別指導キャンパス|子会社|むらた整形外科クリニック|OHARADENTALCLINIC|ハレルヤ園|地域包括ケア推進課|こども歯科|品川美容外科|通りデンタルケア|山本歯科|保谷伊藤眼科|クリニック鴨居|パートナー川口|玉成苑|野方駅内科|ウォーク尾久|田北整形外科|木場訪問看護ステーション|クリニック吉祥寺|たかの整形外科|ワダ矯正歯科|銀座･にわ歯科室|つるい整形外科|みよし歯科|銀座院|東京皮膚科･形成外科|船州会歯科診療所|宮田歯科三田診療所|瑞江整形外科|Workit!Plaza福岡|広島カンパニー|UCCグループ|CafeRestaurantBinario|アウル運輸サービス|カワイ体育教室|D-Plus|家庭教師のマナベスト|ゆかり|白鳩保育園|ダイア磯子|児童デイサービスくろーばー|CENTURY21|センチュリー21|部|課|オフィス|グループ|事業部|事業所|支社|支店|店|営業所|工場|医院|クリニック|病院|本社|車庫|学院|本部|学校|ハブセンター|センター|本舗|エリア|ダスキン津田)$', split_name)   
                    if corporate_delsup_2:
                        corporate_delsup_2 = corporate_delsup_2.group()
            #             logger.info(corporate_delsup_2)
                    else:
                        corporate_delsup_2 = ''
            #             logger.info(corporate_delsup_2)
                    #corporate_name_1から括弧外の補足（事業部、支社など）を削除する。
                    corporate_name_2 = corporate_name_1.replace(corporate_delsup_2, '')
            #         logger.info(corporate_name_2)

                #4-3-2.最後に綺麗にする。
                corporate_name = re.sub(r'[ 　【】（）()/／◆「」『』※～~<>＜＞|★、]', '', corporate_name_2)
#                 logger.info('法人名：' + corporate_name)

        # corporate_sup_ele = corporate_sup_ele + corporate_sup_ele_2
        # logger.info(corporate_sup_ele)

        #4-4-0.法人名補足を抽出する。
        #法人名補足を入れる箱を作る。
        corporate_sup = ''
        #4-4-1.括弧で分割し、事業部名などが含まれるものを抽出する。
        split_name_li = re.split('[ 　【】（）()/／◆「」『』※～~<>＜＞|★、]', company_name)
        for split_name in split_name_li:
            #事業部名、店舗名などがつくワードを検索
            corporate_sup_ele_1 = re.search(r'^(?!.*株式会社|有限会社|合同会社|学校法人|医療法人|社会福祉法人|独立行政法人|相互会社|事務所|生活協同組合|公益社団法人|特定非営利活動法人|特定医療法人|企業組合|一般社団法人|社会医療法人|国立研究開発法人|NPO法人|会計事務所|三協管理センター|鍋浦のこ目立センター｜大宮商店|船橋中央自動車学校|小室商店|藤木商店|笠川工務店|伊藤工務店|広報企画センター|西商店|二村商店|サカイ引越センター|前田営工センター|岡田商店|左近商店|伊藤商店|日本衛生センター|クリエーションセンター|永岡医院|岩江クリニック|門田医院|鴨居病院|江口医院|苅安賀自動車学校|冨士喜本店|井上清助商店|ゆびすい労務センター|神田歯科医院|東京広域事務センター|大塚製薬工場|東京個別指導学院|コーディネーションセンター|キャリアデザインセンター|研究支援センター|技術研究センター|サンタックオフィス|谷田病院|JFR情報センター|木村屋|阿部長商店|がん研究センター|早田工務店|分析センター|近藤建材店|中央グループ|鈴木工務店|中央労務オフィス|臨床検査センター|法研中部|みつもりデンタル|らくだケア|サンタックス|くまの歯科|明石市立市民病院|よしだ歯科|今治繊維|九州建設|大川インテリア|丸喜工務店|太田歯科医院|かじはら歯科|五十子|神田ウィメンズ|日本建築センター|ＪＰＣＥＲＴ|椿デンタル|長澤工務店|亜細亜友の会|日本スポーツ振興|飯田商店|アエラ小児|広沢自動車学校|紛争処理|吉山塗料店|石井工務店|モリカワ会計|シルバー人材|埼玉県産業|日本会計|札幌ハート|鈴木酒造店|豊能障害|花巻病院|バウムクーヘン|広島平和|甲府昭和店|新町クリニック|欧州連合|京都ジョブパーク|新情報センター|インターオフィス|タックスオフィス|神戸海星病院|Nidec|早田工務店|熊谷環境分析センター|近藤建材店|富士学院|貝沼商店|ミニクリーン中部|法研中部|加藤工務店|明石市立市民病院|堀田工務店|今治繊維リソースセンター|九州建設マネジメントセンター|社会医療法人聖ルチア会|八幡病院|丸喜工務店|機能訓練センター|長澤工務店|亜細亜友の会外語学院|吉田クリニック|健康長寿医療センター|社会保険労務士法人|川越市シルバー|上野村きのこセンター|国民生活センター|マンション住替|儀間商店|東京紙店|木下商店|共立メンテナンスグループ|萩原商店|Ｔ.クリエーションセンター).*(佐賀製作所|キッズクリニック鷺沼|直取引|ダスキン津田|オフィス迎賓館|転職エージェント|飯田橋駅前教室|グループ傘下|東京中央美容外科|西日本ユニット|HRバリュー事業|IT派遣|関東事務所|東海ブロック|関西事務所|明聖高等学校|中野キャンパス|おおしま皮膚科|お寺でおみおくり|ジャック幼児教育研究所|曙ゴルフガーデン|スイーツ新大阪|大阪南部ブロック|第一倉庫|名古屋オフィス|東中部カンパニー|経営企画本部|ナレッジバンク|モバイルユニット|住居余暇本部|友愛記念病院|ホームブリスイン野田|きらら歯科|携われる|建物管理|横浜アクア|そよかぜ|清風霊園|開設準備室|ふれあい館|ビジネススペあいの郷|ＩＴサービス室|ほけんの窓口|GS1Japan|社名変更|東急不動産|住友商事|ー東証一部上場ー|ステーション綾瀬|整備工場|ー北海道空港グループー|ズ・ジャパン|だらぼち|和食居酒屋|北関東カンパニー|遊び|学ぶ|小中部|高校部|続けています。|指導キャンパス|DEC統括|M-Shine|町CS|STLASSH|事業局|くるみの森保育園|北部ステーション|イベント事務局|播磨自動車教習所|北口教室|大宝塚ゴルフクラブ|大阪西店|土佐堀|南部ブロック|老人ホーム|東住吉|にっこり山城|名古屋商科大学|飛鳥未来高等学校|名古屋キャンパス|モバイルユニット|山内会計事務所|みなとみらい耳鼻咽喉科|観洋|出資|上場企業|グループ企業|上場|つつじ荘|のとだらぼち|生活事業|出資会社|出資企業|こうのとり|LANDooZ|個別指導キャンパス|子会社|むらた整形外科クリニック|OHARADENTALCLINIC|ハレルヤ園|地域包括ケア推進課|こども歯科|品川美容外科|通りデンタルケア|山本歯科|保谷伊藤眼科|クリニック鴨居|パートナー川口|玉成苑|野方駅内科|ウォーク尾久|田北整形外科|木場訪問看護ステーション|クリニック吉祥寺|たかの整形外科|ワダ矯正歯科|銀座･にわ歯科室|つるい整形外科|みよし歯科|銀座院|東京皮膚科･形成外科|船州会歯科診療所|宮田歯科三田診療所|瑞江整形外科|Workit!Plaza福岡|広島カンパニー|UCCグループ|CafeRestaurantBinario|アウル運輸サービス|カワイ体育教室|D-Plus|家庭教師のマナベスト|ゆかり|白鳩保育園|ダイア磯子|児童デイサービスくろーばー|CENTURY21|センチュリー21|部|課|オフィス|グループ|事業部|事業所|支社|支店|店|営業所|工場|医院|クリニック|病院|本社|車庫|学院|本部|学校|ハブセンター|センター|本舗|エリア|ダスキン津田)$', split_name)   
            if corporate_sup_ele_1:
                corporate_sup_ele_1 = corporate_sup_ele_1.group()
    #             logger.info(corporate_sup_ele_1)
                corporate_sup += corporate_sup_ele_1 + ','

        #4-4-2.最後の","を削除
        corporate_sup = re.sub(r',$', '', corporate_sup)
#         logger.info('法人名補足：' + corporate_sup)


        #『社会福祉法人』などの切り分けロジック。社会医療法人追記。210726
        corporate_name_jad = corporate_name
        corporate_name_jad = corporate_name_jad.replace(' ', '').replace('　', '')      
                    #『社会福祉法人』などの切り分けロジック。210722

        if '社会医療法人' in corporate_name_jad:
            corporate_name_ele = re.search(r'社会医療法人.+?会', corporate_name_jad)
            #『社会福祉法人』より後方に『会』が入っている場合の処理。
            if corporate_name_ele:
                corporate_name = corporate_name_ele.group()       
                logger.info(corporate_name)        
                corporate_sup = corporate_name_jad.replace(corporate_name, '')
#                 logger.info(corporate_sup)

        elif '一般社団法人' in corporate_name_jad or '医療法人' in corporate_name_jad:
            corporate_name_ele = re.search(r'.+会', corporate_name_jad)
            #『会』が入っている場合の処理。
            if corporate_name_ele:
                corporate_name = corporate_name_ele.group()
                logger.info(corporate_name)
                corporate_sup = corporate_name_jad.replace(corporate_name, '')
#                 logger.info(corporate_sup)

        elif '社会福祉法人' in corporate_name_jad:
            corporate_name_ele = re.search(r'社会福祉法人.+?会', corporate_name_jad)
            #『社会福祉法人』より後方に『会』が入っている場合の処理。
            if corporate_name_ele:
                corporate_name = corporate_name_ele.group()
                logger.info(corporate_name)        
                corporate_sup = corporate_name_jad.replace(corporate_name, '')
#                 logger.info(corporate_sup)

        elif '学校法人' in corporate_name_jad:
            corporate_name_ele = re.search(r'学校法人.+?園', corporate_name_jad)
            #『園』が入っている場合の処理。
            if corporate_name_ele:
                corporate_name = corporate_name_ele.group()
                logger.info(corporate_name)
                corporate_sup = corporate_name_jad.replace(corporate_name, '')
#                 logger.info(corporate_sup)


#ここまで法人名、法人名補足のマスター
#============================================================


        occupation_type = driver.find_element(By.CSS_SELECTOR,'.head_upr h1')
        occupation_type = occupation_type.text
        #logger.info(occupation_type)


        # 4-5,社名・事業内容・事業所・従業員数・業種・資本金・売上高・設立年・代表者
        company_content_li = driver.find_elements(By.CSS_SELECTOR,'.kigyogaiyo .mod-job-info dl')
        for company_content in company_content_li:
            dt_text = company_content.find_element(By.CSS_SELECTOR,'dt')
            dt_text = dt_text.text
            dd_text = company_content.find_element(By.CSS_SELECTOR,'dd')
            dd_text = dd_text.text    
            if dt_text == '事業内容':
                company_business = dd_text
                company_business = company_business.replace('\n', '')
                #logger.info(company_business)

            elif dt_text == '従業員数':
                company_employees = dd_text
                company_employees = company_employees.replace('\n', '')
                company_employees
#                 logger.info(company_employees)
                
            elif dt_text == '資本金':
                capital_stock = dd_text
                capital_stock = capital_stock.replace('\n', '')
                #logger.info(capital_stock)
            elif dt_text == '売上高':
                company_sales = dd_text
                company_sales = company_sales.replace('\n', '')
                #logger.info(company_sales)
            elif dt_text == '設立':
                company_establishment = dd_text
                company_establishment = company_establishment.replace('\n', '')
                #logger.info(company_establishment)


        #4-5-2. 業種は取得済み

        #4-6,勤務地・給与・勤務時間・待遇福利厚生・休日休暇・仕事内容・求めている人材・募集背景
        application_guideline_li = driver.find_elements(By.CSS_SELECTOR,'.bosyuarea .box')
        # logger.info(len(application_guideline_li))

        for application_guideline in application_guideline_li:
            h4_text = application_guideline.find_element(By.CSS_SELECTOR,'h4')
            h4_text = h4_text.text
            box_main_text = application_guideline.find_element(By.CSS_SELECTOR,'._box_main')
            box_main_text = box_main_text.text

            if h4_text == '勤務地':
                work_location = box_main_text
                work_location = work_location.replace('\n', '')
                #logger.info(work_location)
            elif h4_text == '想定給与':
                salary = box_main_text
                salary = salary.replace('\n', '')                    
                #logger.info(salary)
            elif h4_text == '勤務時間':
                work_hours = box_main_text
                work_hours = work_hours.replace('\n', '')                
                #logger.info(work_hours)
            elif h4_text == '待遇・福利厚生':
                welfare = box_main_text
                welfare = welfare.replace('\n', '')                    
                #logger.info(welfare)
            elif h4_text == '休日休暇':
                holiday =  box_main_text
                holiday = holiday.replace('\n', '')                                        
                #logger.info(holiday)
            elif h4_text == '雇用形態':
                employment_status =  box_main_text
                employment_status = employment_status.replace('\n', '')                                        
                #logger.info(employment_status)
            elif h4_text == '仕事内容':
                job_description =  box_main_text
                job_description = job_description.replace('\n', '')
                #logger.info(job_description)
            elif h4_text == '応募資格':
                application_conditions =  box_main_text
                application_conditions = application_conditions.replace('\n', '')
                #logger.info(application_conditions)
            elif h4_text == '募集背景':
                recruitment_background =  box_main_text
                recruitment_background = recruitment_background.replace('\n', '')
        #         logger.info(recruitment_background)

        
        
        #従業員数レンジをなどを下部に移動。210908
        if company_employees:
            com_em_ran = company_employees.replace(',', '').replace(' ', '').replace('，', '').replace('.', '')
            #『人』or『名』より前を抜き出す。『万』も含めて
#             company_employees_range = re.search(r'[\d|万]+(?=\D)',company_employees_range)
            #『万か数字』を含み、『名か人』までの判別。
            company_employees_range = re.search(r'[\d|万]+(?=[名|人])', com_em_ran)
            #『万か数字』を含み、『名か人』までが無い場合。                
            if not company_employees_range:
                #『万か数字』を含み、数字以外までの場合。
                company_employees_range = re.search(r'[\d|万]+(?!=\d)', com_em_ran)
                #『万か数字』を含み、数字以外までが無いの場合。
                if not company_employees_range:
                    company_employees_range = ''
                else:
                    #『万か数字』を含み、数字以外までがある場合。
                    company_employees_range = company_employees_range.group()
                    #『万』が含まれる場合の処理
                    if '万' in company_employees_range:
                        vcm_int = int('10000')
                    else:         
                        vcm_int = company_employees_range
                        vcm_int = int(vcm_int)
            #『万か数字』を含み、『名か人』までがある場合。
            else:
                company_employees_range = company_employees_range.group()
                #『万』が含まれる場合の処理
                if '万' in company_employees_range:
                    vcm_int = int('10000')
                else:         
                    vcm_int = company_employees_range
                    vcm_int = int(vcm_int)

            if 5000 <= vcm_int:
                company_employees_range = ran_8
            if 3000 <= vcm_int < 5000:
                company_employees_range = ran_7
            if 1000 <= vcm_int < 3000:
                company_employees_range = ran_6
            if 500 <= vcm_int < 1000:
                company_employees_range = ran_5
            if 300 <= vcm_int < 500:
                company_employees_range = ran_4
            if 100 <= vcm_int < 300:
                company_employees_range = ran_3
            if 50 <= vcm_int < 100:
                company_employees_range = ran_2
            if vcm_int < 50:
                company_employees_range = ran_1
#             logger.info(company_employees_range)


        #4-8-2. 未経験フラグ追加。210909
        #アイコンがアクティブ（on）になっているテキストを統合する変数。
        inexperienced_all_text = ''
        
        driver.implicitly_wait(0)
        if check_exists_element('.fig_pr_area.mb20 .pr_icon .on'):
            inexperienced_ele_li = driver.find_elements(By.CSS_SELECTOR,'.fig_pr_area.mb20 .pr_icon .on')
#             logger.info(len(inexperienced_ele_li))
            for inexperienced_ele in inexperienced_ele_li:
                inexperienced_text = inexperienced_ele.text
                inexperienced_all_text += inexperienced_text
        #アイコンがない場合は、全て'なし'。
        else:
            inexperienced_flag = '無'
            no_transfer = '無'
            public_offering = '無'

        if '未経験歓迎' in inexperienced_all_text:
            inexperienced_flag = '有'
        else:
            inexperienced_flag = '無'
        #転勤なしフラグの取得。210908
        if '転勤なし' in inexperienced_all_text:
            no_transfer = '有'
        else:
            no_transfer = '無'
        #株式公開フラグの取得。210908
        if '上場' in inexperienced_all_text:
            public_offering = '有'
        else:
            public_offering = '無'
        driver.implicitly_wait(10)

        
        #設立年数値、下部に追加。210908
        if company_establishment:
            company_establishment_2 = company_establishment.replace(',', '').replace('、', '')

            #西暦の場合の処理。
            establishment_range_check = re.search(r'\d{4}(?=\D)', company_establishment_2)
            if establishment_range_check:
                establishment_num = establishment_range_check.group()
                #↓これ入れ忘れてたから『文字列』になっていたぽい。220320
                establishment_num = int(establishment_num)
            else:
                #和暦の場合の処理。
                establishment_range_check = re.search(r'(\d+)|(元)(?=\D)', company_establishment_2)
                if establishment_range_check:
                    establishment_num = establishment_range_check.group()
                    establishment_num = establishment_num.replace('元', '1')
                    establishment_num = int(establishment_num)

                    # 明治 1868~1911(1912),大正1912~1925(1926),昭和1926~1988(1989),平成1989~2018,令和2019~
                    if '明治' in company_establishment_2:
                        establishment_num += 1867
                    elif '大正' in company_establishment_2:
                        establishment_num += 1911
                    elif '昭和' in company_establishment_2:
                        establishment_num += 1925
                    elif '平成' in company_establishment_2:
                        establishment_num += 1988
                    elif '令和' in company_establishment_2:
                        establishment_num += 2018
                #ブランク、もしくは変換不可能な場合の処理。
                else:
                    establishment_num = ''

            #1000年以下はエラーと判断し、ブランク処理する。220404
            if establishment_num :
                if establishment_num <= 1000:
                    establishment_num = ''

        #資本金レンジ、下部に追加。210909
        if capital_stock:
            capital_stock_2 = capital_stock.replace(',', '').replace('、', '').replace(' ', '').replace('　', '')
            #非貪欲マッチで『円』まで『円』付きで抜き取る。『1,000万円（国内グループ計8億1,200万円）』のケースに対応。210906
            capital_stock_2 = re.search('.+?円', capital_stock_2)
            if capital_stock_2:
                capital_stock_2 = capital_stock_2.group()

                #小数点以下を削除する。210906
                if '.' in capital_stock_2:
                    capital_stock_2 = re.sub(r'\.(\d+)(?=\D)','', capital_stock_2)

                #『億』が含まれる場合の処理。
                #全て『万円』単位で処理する。
                if '億' in capital_stock_2:
                    capital_stock_num = re.search(r'(\d+)(?=億)', capital_stock_2)
                    if capital_stock_num:
                        capital_stock_num = capital_stock_num.group()
                        capital_stock_num = capital_stock_num + '0000'
                        capital_stock_int = int(capital_stock_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        capital_stock_int = ''  

                elif '千万円' in capital_stock_2:
                    capital_stock_num = re.search(r'(\d+)(?=千万円)', capital_stock_2)
                    if capital_stock_num:
                        capital_stock_num = capital_stock_num.group()
                        capital_stock_num = capital_stock_num + '000'
                        capital_stock_int = int(capital_stock_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        capital_stock_int = ''

                elif '百万円' in capital_stock_2:
                    capital_stock_num = re.search(r'(\d+)(?=百万円)', capital_stock_2)
                    if capital_stock_num:
                        capital_stock_num = capital_stock_num.group()
                        capital_stock_num = capital_stock_num + '00'
                        capital_stock_int = int(capital_stock_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        capital_stock_int = ''

                elif '万' in capital_stock_2:
                    capital_stock_num = re.search(r'(\d+)(?=万)', capital_stock_2)
                    if capital_stock_num:
                        capital_stock_num = capital_stock_num.group()
                        capital_stock_int = int(capital_stock_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        capital_stock_int = '' 

                elif '千円' in capital_stock_2:
                    capital_stock_num = re.search(r'(\d+)(?=千円)', capital_stock_2)
                    if capital_stock_num:
                        capital_stock_num = capital_stock_num.group()
                        capital_stock_int = int(capital_stock_num)
                        # 切り捨て
                        capital_stock_int = capital_stock_int // 10
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        capital_stock_int = '' 

                #『億』『万』がなく、『円』のみの時。
                elif '円' in capital_stock_2:
                    capital_stock_num = re.search(r'(\d+)(?=円)', capital_stock_2)
                    if capital_stock_num:
                        capital_stock_num = capital_stock_num.group()
                        #後方4桁の数字を削除し、単位を『万』に揃える。
                        capital_stock_num = re.sub(r'\d{4}$','', capital_stock_num)
                        if capital_stock_num:
                            capital_stock_int = int(capital_stock_num)
                        #金額の数値が3桁以下の場合で取得できない場合。
                        else:
                            capital_stock_int = ''
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        capital_stock_int = ''

                #ブランク、もしくは変換不可能な場合の処理。
                else:
                    capital_stock_int = ''

                #『資本金』の表記が想定外の場合、capital_stock_intがブランクになるので、エスケープ。210830 
                if capital_stock_int:
                    if capital_stock_int < 750:
                        stock_range = cap_ran_1
                    elif 750 <= capital_stock_int < 1500:
                        stock_range = cap_ran_2
                    elif 1500 <= capital_stock_int < 3000:
                        stock_range = cap_ran_3
                    elif 3000 <= capital_stock_int < 5000:
                        stock_range = cap_ran_4
                    elif 5000 <= capital_stock_int < 10000:
                        stock_range = cap_ran_5
                    elif 10000 <= capital_stock_int < 50000:
                        stock_range = cap_ran_6
                    elif 50000 <= capital_stock_int < 100000:
                        stock_range = cap_ran_7
                    elif 100000 <= capital_stock_int:
                        stock_range = cap_ran_8
                    else:
                        stock_range = ''
        
        #派遣会社フラグ追加。210908
        if '派遣' in company_business:
            temp_staffing = '有'
        else:
            temp_staffing_check = re.search(r'\d{2}[-ー−ｰ－]\d{6}', company_business)
            if temp_staffing_check:
                temp_staffing = '有'
            else:
                temp_staffing = '無'

        #給与レンジの取得。210908
        if '想定年収' in salary:
            salary_rep = salary.replace(',', '').replace('、', '').replace(' ', '').replace('　', '')
            salary_2 = re.search(r'(?<=想定年収)\D{0,4}\d{3,4}(万円|万|)～\d{3,4}(万円|万)', salary_rep)
            #上限の記載がない場合の処理。
            if not salary_2:
                #下限のみ取得する。
                salary_2 = re.search(r'(?<=想定年収)\D{0,4}\d{3,4}(万円|万)', salary_rep)

            #上限下限、または下限のみ入っていた場合は、salary_2が存在する。
            if salary_2:
                salary_2 = salary_2.group()
        #                 logger.info(salary_2)
                salary_class = '年俸'
                lower_salary = re.search(r'\d{3,4}', salary_2)
                #念の為 ifでエスケープしとく。
                if lower_salary:
                    lower_salary = lower_salary.group()
                upper_salary = re.search(r'(?<=～)\d{3,4}', salary_2)
                #念の為 ifでエスケープしとく。
                if upper_salary:
                    upper_salary = upper_salary.group()

        if not lower_salary:
            if '年俸' in salary:
                salary_rep = salary.replace(',', '').replace('、', '')
                salary_2 = re.search(r'(?<=年俸)\D{0,4}\d{3,4}(万円|万|)～\d{3,4}(万円|万)', salary_rep)
                #上限の記載がない場合の処理。
                if not salary_2:
                    #下限のみ取得する。
                    salary_2 = re.search(r'(?<=年俸)\D{0,4}\d{3,4}(万円|万)', salary_rep)

                if salary_2:
                    salary_2 = salary_2.group()
        #                     logger.info(salary_2)
                    salary_class = '年俸'
                    lower_salary = re.search(r'\d{3,4}', salary_2)
                    #念の為 ifでエスケープしとく。
                    if lower_salary:
                        lower_salary = lower_salary.group()
                        #全角のエスケープ追記。220314
                        lower_salary = int(lower_salary)
                    upper_salary = re.search(r'(?<=～)\d{3,4}', salary_2)
                    #念の為 ifでエスケープしとく。
                    if upper_salary:
                        upper_salary = upper_salary.group()
                        #全角のエスケープ追記。220314
                        upper_salary = int(upper_salary)


        #英語スキルフラグ完成。210908
        if '英語' in job_description or '英語' in application_conditions or 'TOEIC' in application_conditions:
            english_skill = '有'
        else:
            english_skill = '無'

        #外国籍活躍フラグ完成。210908
        if '国籍' in job_description or '国籍' in application_conditions or '日本語' in application_conditions:
            foreigner_activity = '有'
        else:
            foreigner_activity = '無'


        #想定決算月の取得。220320
        if company_establishment:
            closing_month_ele = re.search(r'\d{1,2}月', company_establishment)
            if closing_month_ele:
                closing_month_p = closing_month_ele.group()
                closing_month_p = closing_month_p.replace('月', '')
                #int型に変更すれば、半角化する必要ない。220314
                closing_month = int(closing_month_p) -1
                if closing_month == 0:
                    closing_month = 12
            else:
                closing_month = ''
                
            #想定決算月が1~12以外の時、ブランク処理する。220404
            if closing_month:
                if not 1 <= closing_month <= 12:
                    closing_month = ''


        #『売上高レンジ』220314
        #前求人の値をクリア。220319
        company_sales_int = ''
        if company_sales:
            if '円' in company_sales:
                company_sales_2 = company_sales.replace(',', '').replace('、', '').replace(' ', '').replace('　', '')
                #非貪欲マッチで『円』まで『円』付きで抜き取る。『1,000万円（国内グループ計8億1,200万円）』のケースに対応。210906
                company_sales_2 = re.search('.+?円', company_sales_2)
                if company_sales_2:
                    company_sales_2 = company_sales_2.group()
                else:
                    #『売上高』が『円(2020年度実績)』などで円より前の文字列がない場合の処理。220310
                    company_sales_2 = ''
                    company_sales_int = ''

                #小数点以下を削除する。210906
                if '.' in company_sales_2:
                    company_sales_2 = re.sub(r'\.(\d+)(?=\D)','', company_sales_2)

                #『億』が含まれる場合の処理。
                #全て『万円』単位で処理する。
                if '兆' in company_sales_2:
                    company_sales_num = re.search(r'(\d+)(?=兆)', company_sales_2)
                    if company_sales_num:
                        company_sales_num = company_sales_num.group()
                        company_sales_num = company_sales_num + '00000000'
                        company_sales_int = int(company_sales_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = ''  

                elif '千億円' in company_sales_2:
                    #logger.info('b')
                    company_sales_num = re.search(r'(\d+)(?=千億円)', company_sales_2)
                    if company_sales_num:
                        #logger.info('a')
                        company_sales_num = company_sales_num.group()
                        company_sales_num = company_sales_num + '0000000'
                        company_sales_int = int(company_sales_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = ''

                elif '百億円' in company_sales_2:
                    #logger.info('b')
                    company_sales_num = re.search(r'(\d+)(?=百億円)', company_sales_2)
                    if company_sales_num:
                        #logger.info('a')
                        company_sales_num = company_sales_num.group()
                        company_sales_num = company_sales_num + '000000'
                        company_sales_int = int(company_sales_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = ''

                #誤字も織り込む。220227
                elif '億' in company_sales_2 or '憶' in company_sales_2:
                    company_sales_num = re.search(r'(\d+)(?=億|憶)', company_sales_2)
                    if company_sales_num:
                        company_sales_num = company_sales_num.group()
                        company_sales_num = company_sales_num + '0000'
                        company_sales_int = int(company_sales_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = '' 

                elif '百万円' in company_sales_2:
                    company_sales_num = re.search(r'(\d+)(?=百万円)', company_sales_2)
                    if company_sales_num:
                        company_sales_num = company_sales_num.group()
                        company_sales_num = company_sales_num + '00'
                        company_sales_int = int(company_sales_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = '' 

                elif '万円' in company_sales_2:
                    company_sales_num = re.search(r'(\d+)(?=万円)', company_sales_2)
                    if company_sales_num:
                        company_sales_num = company_sales_num.group()
                        company_sales_int = int(company_sales_num)
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = '' 

                elif '千円' in company_sales_2:
                    company_sales_num = re.search(r'(\d+)(?=千円)', company_sales_2)
                    if company_sales_num:
                        company_sales_num = company_sales_num.group()
                        company_sales_int = int(company_sales_num)
                        # 切り捨て
                        company_sales_int = company_sales_int // 10
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = '' 

                #『兆』『億』『万』がなく、『円』のみの時。
                elif '円' in company_sales_2:
                    company_sales_num = re.search(r'(\d+)(?=円)', company_sales_2)
                    if company_sales_num:
                        company_sales_num = company_sales_num.group()
                        #後方4桁の数字を削除し、単位を『万』に揃える。
                        company_sales_num = re.sub(r'\d{4}$','', company_sales_num)
                        if company_sales_num:
                            company_sales_int = int(company_sales_num)
                        #金額の数値が3桁以下の場合で取得できない場合。
                        else:
                            company_sales_int = ''
                    #漢数字の場合などのケースをエスケープしとく。210822
                    else:
                        company_sales_int = ''

                #ブランク、もしくは変換不可能な場合の処理。
                else:
                    company_sales_int = ''

            #『非上場』など円が入っていないケースはブランク処理。220227
            else:
                company_sales_int = ''

            #『売上高』の表記が想定外の場合、company_sales_intがブランクになるので、エスケープ。220227
            if company_sales_int:
                if company_sales_int < 30000:
                    sales_range = sales_ran_1
                elif 30000 <= company_sales_int < 100000:
                    sales_range = sales_ran_2
                elif 100000 <= company_sales_int < 500000:
                    sales_range = sales_ran_3
                elif 500000 <= company_sales_int < 1000000:
                    sales_range = sales_ran_4
                elif 1000000 <= company_sales_int < 3000000:
                    sales_range = sales_ran_5
                elif 3000000 <= company_sales_int < 5000000:
                    sales_range = sales_ran_6
                elif 5000000 <= company_sales_int < 10000000:
                    sales_range = sales_ran_7
                elif 10000000 <= company_sales_int:
                    sales_range = sales_ran_8
                else:
                    sales_range = ''
            
        
        #4-8. 電話番号・電話番号（ハイフンなし）・メールアドレス・郵便番号・連絡先住所・担当者
        information_detail = driver.find_element(By.CSS_SELECTOR,'.mod-choice-process .mod-job-info .uq-detail-contact')
        information_detail = information_detail.text
        #         company_name は取得済み
        postal_code = re.search(r'〒+\s?\d{3}-\d{4}', information_detail)
        if not postal_code:
            postal_code = ''
        else:
            postal_code = postal_code.group().replace('〒','').replace(' ', '')
        #logger.info(postal_code)

        street_address = re.search(pat, information_detail)
        if not street_address:
            #都道府県の記載がなく、市区町村から始まる場合の処理
            street_address = re.search(city_pat, information_detail)
            if not street_address:
                street_address = ''
            else:
                street_address = street_address.group()
        else:
            street_address = street_address.group()
        #logger.info(street_address)

        phone_number = re.search(r'0\d{1,3}-\d{2,4}-\d{3,4}', information_detail)
        if not phone_number:
            phone_number = ''
            phone_number_nonehyphen = ''
        else:
            phone_number = phone_number.group()
            phone_number_nonehyphen = phone_number.replace('-', '')
#             phone_number_nonehyphen = '=' + '\"' + phone_number_nonehyphen + '\"'        
        #logger.info(phone_number)
        #logger.info(phone_number_nonehyphen)

        mail_address  = re.search(r'(?<=E-mail：)(.+)(?!=\n)', information_detail)
        if not mail_address:
            mail_address = ''
        else:
            mail_address = mail_address.group()
        #logger.info(mail_address)

        charge_person = information_detail.replace(company_name, '').replace(postal_code, '').replace(street_address, '').replace(phone_number, '').replace(mail_address, '')        
        charge_person = charge_person.replace('連絡先', '').replace('（ホームページ）', '').replace('／', '').replace('/', '').replace('：', '').replace(':', '').replace('\n', '').replace('〒', '').replace('【', '').replace('】', '').replace(' ', '').replace('\u3000', '').replace('TEL', '').replace('E-mail', '').replace('企業に問い合わせる', '').replace('（直通）', '')
        #logger.info(charge_person)


        # 4-10,お問い合わせ先/郵便番号・都道府県・市区町村・町域・ビル名※郵便番号は↑で取得済み
        if not street_address:
            contact_prefecture = ''
            contact_city = ''
            contact_town = ''        
        else:
            #谷さんオリジナルモジュールをインポート。201031
            import pattern_text as pt
            pat = pt.get_pattern_text()
            match = re.search(pat, street_address)
            if not match:
                contact_prefecture = ''
                contact_city = ''
                contact_town = ''
            else:
                contact_prefecture = match.group(1) or ''
                contact_city = match.group(2) or ''
                contact_town = match.group(3) or ''

        #都道府県がブランク、かつ市区町村が存在する場合、都道府県補完モジュール発動。220321
        if not contact_prefecture and contact_city:
            contact_prefecture = cp.get_complement_pref(contact_city)

        # 4-11,広告プラン
        #agent判定 210130
        if '赤坂ロングビーチビル' in street_address:
            advertising_plan = advertising_plan + '_agent'

        #広告プランの先頭に媒体名の見出しつける。220404
        advertising_plan = 'typ_' + advertising_plan

        # 4-12,掲載URL
        publication_url = driver.current_url
#         logger.info(publication_url)


        # #4-13. 求人ID
        applicant_id =  re.search(r'(?<=/)\d+(?=_detail)', publication_url)
        applicant_id = applicant_id.group()
        logger.info(applicant_id)

        #4-14. 企業ID
        company_id = ''


        #4-15, 企業HP
        corporate_url_ele = driver.find_element(By.CSS_SELECTOR,'.mod-choice-process .mod-job-info > dl')
        corporate_url_ele = corporate_url_ele.get_attribute('class')
    #     logger.info(corporate_url_ele)

        if corporate_url_ele == 'uq-detail-homepage':
            corporate_url = driver.find_element(By.CSS_SELECTOR,'.mod-job-info .uq-detail-homepage a')
            corporate_url = corporate_url.get_attribute('href')
        else:
            corporate_url = ''


        #4-16, dfに取得したデータ突っ込む
        heading_columns_variable = [applicant_id, company_id, today, media_name, company_name, corporate_name, corporate_sup,
                                                            phone_number, phone_number_nonehyphen, publication_period, publication_start, information_updated,  publication_end,
                                                            occupation_major, occupation_medium, occupation_minor, company_name_original,
                                                            occupation_type, company_business, company_location, company_industry, company_employees, capital_stock, company_sales,
                                                            company_establishment, work_location, salary, work_hours, welfare, holiday, job_description, application_conditions, employment_status, 
                                                            mail_address, postal_code, street_address, charge_person,
                                                            recruitment_background, contact_prefecture, contact_city , contact_town,
                                                            advertising_plan, publication_url, corporate_url, company_employees_range, inexperienced_flag, 
                                                            no_transfer, establishment_num, public_offering, stock_range, temp_staffing, salary_class, lower_salary, 
                                                            upper_salary, english_skill, foreigner_activity, closing_month, sales_range]
        se_info = pd.Series(heading_columns_variable, heading_columns)
        df_info = df_info.append(se_info, ignore_index=True)        

    #4-15. 例外処理パターンを追記。201122
    except NoSuchElementException:
#         logger.info('エラー：NoSuchElementException')
        logger.info('エラー：NoSuchElementException')
        pass

##ボトルネックを発見するために一旦削除。220701
    #例外が発生したら、その時までに取得していたデータを書き出す処理を追記。201122
    except TimeoutException:
        logger.info('エラー：TimeoutException')
        #5. CSVに吐き出す。
        today = datetime.datetime.today()
        media_name = 'disruption_my'
        file_name = '{0:%y%m%d%H%M}'.format(today)+media_name + '.csv'
        df_info.to_csv(output_path + '{0}'.format(file_name), mode='a', header=False, encoding='utf-16', index = False) 
        pass

    except WebDriverException:
#         logger.info('エラー：WebDriverException')
        logger.info('エラー：WebDriverException')
        #5. CSVに吐き出す。
        today = datetime.datetime.today()
        media_name = 'disruption_type'
        file_name = '{0:%y%m%d%H%M}'.format(today)+media_name + '.csv'
        df_info.to_csv(output_path + '{0}'.format(file_name), mode='a', header=False, encoding='utf-16', index = False) 
        pass


    #210409 新規にエラーを追加
    except UnexpectedAlertPresentException:
#         logger.info('エラー：UnexpectedAlertPresentException')
        logger.info('エラー：UnexpectedAlertPresentException')
        today = datetime.datetime.today()
        media_name = 'disruption_type'
        file_name = '{0:%y%m%d%H%M}'.format(today)+media_name + '.csv'
        df_info.to_csv(output_path + '{0}'.format(file_name), mode='a', header=False, encoding='utf-16', index = False)

        driver.switch_to.alert.accept()
        pass

    #追記。220701
    except InvalidSessionIdException:
        logger.info('エラー：InvalidSessionIdException')
        pass


    #メモリ不足対策 500→300件に一度リフレッシュ 220624
    if num % 300 == 0:
        driver.quit()
#         driver = webdriver.Chrome(executable_path= chrm_path, options=options)
        #Selenium4.220703
        driver = webdriver.Chrome(service=service, options=options)
        time.sleep(18)


    #最初に一度吐き出す。
    if num == 1:
        #temporary_fileにdatetimeをつける。220222
        today = datetime.datetime.today()
        tem_file_name = '{0:%y%m%d%H%M}'.format(today) + file_media_name + '_temporary_file.csv'
        df_info.to_csv(output_path +  tem_file_name, encoding='utf-16', index = False)
        #dfを初期化
        df_info = pd.DataFrame(data=None, columns = heading_columns)
    #300件に一度csvに追記する。
    elif num % 100 == 0:
        df_info.to_csv(output_path +  tem_file_name, mode='a', header=False, encoding='utf-16', index = False)
        #dfを初期化
        df_info = pd.DataFrame(data=None, columns = heading_columns)


    #4-14. 1件取得ごとに変数'num'に　+1 し、20件取得ごとに出力する。
    if num % 20 == 0:
#         logger.info('\n' + '【' + str(num) + '件のデータ取得完了' + '】' + '\n')
        logger.info('\n' + '【' + str(num) + '件のデータ取得完了' + '】' + '\n')

    #追記。 220624
    if num % 200 == 0:
        now = datetime.datetime.now()
        now_time = f"{now:%Y-%m-%d %H:%M:%S}"
        subject = now_time + '【 ' + file_media_name + ' ' + str(num) + '件の収集が完了しました。】'

        #本文はブランクでOK。211210
        body = file_media_name + ' ' + str(num) + '件の収集が完了しました。】'

        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["To"] = mail_to
        msg["From"] = gmail_account

        # Gmailに接続 --- (*4)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
            context=ssl.create_default_context())
        server.login(gmail_account, gmail_password)
        server.send_message(msg) # メールの送信
        # logger.info("メール送信 complete.")
        logger.info("メール送信 complete.")
        
    #残り600件お知らせメール流す処理。220616
    remaining_num = 400
    if int(dic_figs) - num == remaining_num:
        now = datetime.datetime.now()
        now_time = f"{now:%Y-%m-%d %H:%M:%S}"
        subject = now_time + '【 ' + file_media_name + ' 残り ' + str(remaining_num) + '件 です】'

        #本文はブランクでOK。211210
        body = file_media_name + ' 残り ' + str(remaining_num) + '件 です'

        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["To"] = mail_to
        msg["From"] = gmail_account

        # Gmailに接続 --- (*4)
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
            context=ssl.create_default_context())
        server.login(gmail_account, gmail_password)
        server.send_message(msg) # メールの送信
        # logger.info("メール送信 complete.")
        logger.info("メール送信 complete.")


    num += 1
    
    
## ここからは定型         
driver.close()
driver.quit()


#5. 一旦残りのdfをCSVに吐き出す。
df_info.to_csv(output_path + tem_file_name, mode='a', header=False, encoding='utf-16', index = False)
#5-1. ファイル名を確定し、ファイル名を変更する。
today = datetime.datetime.today()
#file_media_name = 'toranet'
file_name = '{0:%y%m%d%H%M}'.format(today)+ file_media_name + '.csv'
# df_toranet.to_csv(output_path + '{0}'.format(file_name)) 
#ファイル名を変更
os.rename(output_path + tem_file_name, output_path + '{0}'.format(file_name))


#Excelファイルも吐き出すため、吐き出したCSVファイルを読み込む。
#『'取得日': object』追記。220319
df_re = pd.read_csv(output_path + file_name, low_memory=False , dtype={'取得日': object, '求人ID': object, '法人ID': object, '電話番号ハイフンなし': object}, encoding='utf-16')
# df_re = pd.read_csv(output_path + file_name, low_memory=False , dtype={'求人ID': object, '法人ID': object, '電話番号ハイフンなし': object, '設立年数値': int}, encoding='utf-16')

#3-2. 新着dfをハイパーリンクを削除し（options={'strings_to_urls':False}）xlsxで吐き出す。
file_name_new = '{0:%y%m%d%H%M}'.format(today)+ file_media_name + '.xlsx'
writer = pd.ExcelWriter(output_path + file_name_new, options={'strings_to_urls':False})
df_re.to_excel(writer, index=False)
writer.close()

## 3-3. フォントをExcelのデフォルトに変更する。210531
sheet_name = 'Sheet1'
inputfile = output_path + file_name_new

# read input xlsx
wb1 = openpyxl.load_workbook(filename=inputfile)
# シートを取得 
ws1 = wb1[sheet_name]

# set font
font = Font(name='游ゴシック Regular (本文)', size=12)

# write in sheet
# セル番地を取得
for cells in tuple(ws1.rows):
    for cell in cells:
        ws1[cell.coordinate].font = font

# # save xlsx file
wb1.save(inputfile)


#7. 片付け
# logger.info(media_name + '完了')
logger.info(media_name + '完了')

#bash判定のダミーファイルを作成する。211208
test_file = pathlib.Path(judge_file_path + 'judge.txt')
test_file.touch()


t4 = time.time()
elapsed_time = t4-t3
logger.info(f"収集時間：{elapsed_time}")

ela_time = t4-t1
logger.info(f"全体時間：{ela_time}")

complete_media_name = 'complete' + media_name
# logger.info('\n' + '【' + complete_media_name + '】' + '\n')
logger.info('\n' + '【' + complete_media_name + '】' + '\n')


#もしlogger内容でメール送信できなければ、↓に変更する。
now = datetime.datetime.now()
now_time = f"{now:%Y-%m-%d %H:%M:%S}"
subject = now_time + '【' + media_name  + "】の収集が完了しました。"

#経過時間を『分』に修正して表示
era_min = ela_time // 60
body = '収集時間は ' + str(era_min) + ' 分。\n【収集案件数は、' + str(num) + '件でした。】\n'


msg = MIMEText(body, "html")
msg["Subject"] = subject
msg["To"] = mail_to
msg["From"] = gmail_account

# Gmailに接続 --- (*4)
server = smtplib.SMTP_SSL("smtp.gmail.com", 465,
    context=ssl.create_default_context())
server.login(gmail_account, gmail_password)
server.send_message(msg) # メールの送信
# logger.info("メール送信 complete.")
logger.info("メール送信 complete.")

#ハンドラーを削除。
logger.removeHandler(s_handler)
logger.removeHandler(f_handler)


# prof = LineProfiler()
# prof.add_function(scrape)
# prof.runcall(scrape)
# prof.logger.info_stats()



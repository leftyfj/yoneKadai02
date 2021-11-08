import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

import time
import datetime
import pandas as pd
import traceback

# 使用するブラウザ
BROWSER = "Firefox"
#対象とするサイト
TARGET_SITE = 'https://tenshoku.mynavi.jp/'

LOG_FILE_PATH = "./log/log_{datetime}.log"
log_file_path = LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d'))

# Chromeを起動する関数
def set_driver(browser, headless_flg):
    if browser == "Chrome":
        options = webdriver.ChromeOptions()
    else:
        from selenium.webdriver.firefox.options import Options
        options = Options()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')
    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    if browser == "Chrome":
        driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    else:
        driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())

    return driver


#log出力関数
def make_log(txt):
    now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = '[%s:%s] %s' %('log', now, txt)
    #ファイルに出力
    with open(log_file_path, 'a', encoding='utf-8_sig') as f:
        f.write(logStr + '\n')
    print(logStr)

    # main処理
def main():
   # driverを起動
    driver = set_driver(BROWSER,False)
    make_log('ブラウザ起動')
    key_word_search = input('検索したいキーワードを入力してください。>>')  

  # Webサイトを開く
    driver.get(TARGET_SITE)
    time.sleep(4)

  # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    time.sleep(4)
  # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')

  #キーワードを検索窓に入力する
    driver.find_element_by_css_selector(
      "input.topSearch__text").send_keys(key_word_search)
    make_log(f'キーワード({key_word_search})を検索窓に入力')
  # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()

  # 検索結果 件数を取得、表示
    total_names = driver.find_element_by_css_selector(
      "span.js__searchRecruit--count").text
    print(f'キーワードに該当する企業数={total_names}社')
    make_log(f'検索結果取得成功:キーワードに該当する企業数={total_names}社')
    page = 1
    counts_companies = 1

    df = pd.DataFrame()
    while True:
        contents = driver.find_elements_by_css_selector('.cassetteRecruit')
        print(f'{page}ページ目の企業数={len(contents)}')
        make_log(f'{page}ページ目の企業数={len(contents)}')
        for content in contents:
            try:
                #企業名と企業キャッチコピーをリストに格納→それぞれを変数に取り出す
                name_catch =content.find_element_by_css_selector("h3").text
                name_catch = name_catch.strip().split('|')

                if(len(name_catch) > 1):
                    name = name_catch[0]
                    company_catch = name_catch[1]
                else:
                    name = name_catch[0]
                    company_catch=''
                #求人件名、詳細URL、更新日を取得
                title = content.find_element_by_css_selector(
                    ".cassetteRecruit__copy > a").text
                link = content.find_element_by_css_selector(
                    ".cassetteRecruit__copy > a").get_attribute("href")
                update_date = content.find_element_by_css_selector(
                    ".cassetteRecruit__updateDate > span").text
                # print(counts_companies, name,update_date,link)

                #情報をデータフレームに格納
                df = df.append({
                    'No.': counts_companies,
                    '企業名': name,
                    '募集内容': title,
                    '情報更新日': update_date,
                    '募集内容詳細': link,
                    '企業紹介': company_catch
                }, ignore_index=True)
                make_log(f'{counts_companies}社目 情報取得成功')
            except Exception as e:
                make_log(f'{counts_companies}社目 情報取得失敗')
                make_log(traceback.format_exc())
            finally:
                counts_companies += 1

        #次ページへ遷移
        element_click = driver.find_elements_by_css_selector(
            ".iconFont--arrowLeft")

        if len(element_click) >=1:
            page += 1
            driver.execute_script(
                "arguments[0].scrollIntoView(true);", element_click[0])
            element_click[0].click()
            make_log(f'{page}目へ遷移')
        else:
            print("検索結果を全て取得しました。")
            driver.close()
            break

    # 結果をcsvファイルに保存
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    file_name_path = './results/' + f'検索結果(キーワード={key_word_search})_{today}'+'.csv'
    df.to_csv(file_name_path, encoding="utf-8_sig", index=False)
    make_log(f'ファイルに保存_ファイル名「検索結果(キーワード={key_word_search}).csv」')
    
# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
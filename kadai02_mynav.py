import os
from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

import time
import pandas as pd

# 使用するブラウザ
BROWSER = "Firefox"
#対象とするサイト
TARGET_SITE = 'https://tenshoku.mynavi.jp/'

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

    # main処理
def main():
   # driverを起動
    driver = set_driver(BROWSER,False)
   
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

  # 検索ボタンクリック
    driver.find_element_by_class_name("topSearch__button").click()

  # 検索結果 件数を取得、表示
    total_names = driver.find_element_by_css_selector(
      "span.js__searchRecruit--count").text
    print(f'キーワードに該当する企業数={total_names}社')

    page = 1
    counts_companies = 1

    df = pd.DataFrame()
    while True:
        contents = driver.find_elements_by_css_selector('.cassetteRecruit')
        print(f'{page}ページ目の企業数={len(contents)}')
        for content in contents:
            name_catch =content.find_element_by_css_selector("h3").text
            name_catch = name_catch.strip().split('|')
            try:
                name = name_catch[0]
                company_catch = name_catch[1]
            except:
                name = name_catch
            title = content.find_element_by_css_selector(
                ".cassetteRecruit__copy > a").text
            link = content.find_element_by_css_selector(
                ".cassetteRecruit__copy > a").get_attribute("href")
            update_date = content.find_element_by_css_selector(
                ".cassetteRecruit__updateDate > span").text
            print(counts_companies, name,update_date,link)

            df = df.append({
                'No.': counts_companies,
                '企業名': name,
                '募集内容': title,
                '情報更新日': update_date,
                '募集内容詳細': link,
                '企業紹介': company_catch
            }, ignore_index=True)

            counts_companies += 1

        element_click = driver.find_elements_by_css_selector(
            ".iconFont--arrowLeft")

        if len(element_click) >=1:
            page += 1
            driver.execute_script(
                "arguments[0].scrollIntoView(true);", element_click[0])
            element_click[0].click()
        else:
            print("検索結果を全て取得しました。")
            driver.close()
            break
    

    # 結果をcsvファイルに保存
    file_name = f'検索結果(キーワード={key_word_search})'+'.csv'
    df.to_csv(file_name, encoding="utf-8_sig", index=False)

    
# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
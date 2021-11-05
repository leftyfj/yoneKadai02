import os
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import time
import pandas as pd

# Chromeを起動する関数


def set_driver(driver_path, headless_flg):
    if "chrome" in driver_path:
          options = ChromeOptions()
    else:
      options = Options()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    if "chrome" in driver_path:
        return Chrome(executable_path=os.getcwd() + "/" + driver_path,options=options)
    else:
        return Firefox(executable_path=os.getcwd()  + "/" + driver_path,options=options)



    # main処理
def main():
   # driverを起動
  if os.name == 'nt':  # Windows
      driver = set_driver("chromedriver.exe", False)
  elif os.name == 'posix':  # Mac
      driver = set_driver("chromedriver", False)

   #対象とするサイト
  TARGET_SITE = 'https://tenshoku.mynavi.jp/'


  key_word_search = input('検索したいキーワードを入力してください。>>')  
#   key_word_search ='松江市'
  print(key_word_search)

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

  while True:
    contents = driver.find_elements_by_css_selector('.cassetteRecruit')
    print(f'{page}ページ目の企業数={len(contents)}')
    for content in contents:
        name_catch =content.find_element_by_css_selector("h3").text
        name_catch = name_catch.strip().split('|')
        try:
            name = name_catch[0]
            catch = name_catch[1]
        except:
            name = name_catch
        title = content.find_element_by_css_selector(
            ".cassetteRecruit__copy > a").text
        print(counts_companies, name, title)
        counts_companies += 1

    try:
        page += 1
        element_click = driver.find_element_by_css_selector(
            ".iconFont--arrowLeft")
        driver.execute_script("arguments[0].scrollIntoView(true);", element_click)
        element_click.click()
    except:
        print("終わりました")
   
        break   


# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
    main()
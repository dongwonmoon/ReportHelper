import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def download_pdf(wrappers: list, processed_wrapper: set):
    """
    :wrappers: PDF 다운로드 버튼을 포함한 wrapper 리스트
    :processed_wrapper: 이미 다운로드한 wrapper 집합
    :return: 업데이트된 processed_wrapper -> set
    """
    for wrapper in wrappers:
        if wrapper not in processed_wrapper:
            time.sleep(1)
            try:
                down_btn = wrapper.find_element(By.CLASS_NAME, 'thesis__downBtn')
                down_btn.click()
                processed_wrapper.add(wrapper)
                check_recommend_thesis()
            except Exception as e:
                print(f"Error clicking download button: {e}")
        else:
            print('pass')
    return processed_wrapper


def check_recommend_thesis():
    global RECOMMEND_THESIS
    if RECOMMEND_THESIS:
        time.sleep(3)
        try:
            recommend_thesis = driver.find_element(By.CLASS_NAME, 'dpRecommendThesis')
            label = recommend_thesis.find_element(By.CLASS_NAME, 'dpRecommendThesis__label')
            check_box = label.find_element(By.TAG_NAME, 'input')
            check_box.click()
            
            button = recommend_thesis.find_element(By.CLASS_NAME, 'dpRecommendThesis__closed')
            button.click()
            
            RECOMMEND_THESIS = False
        except Exception as e:
            print(f"Error handling recommendation thesis popup: {e}")


def setup_driver(download_path):
    """
    크롬 드라이버 설정 및 초기화
    :param download_path: 파일 다운로드 경로
    :return: 설정된 크롬 드라이버 객체
    """
    chrome_options = Options()
    prefs = {
        "download.default_directory": str(download_path),
        "download.prompt_for_download": False,
        "directory_upgrade": True
    }
    
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    return driver


def croling():
    # 다운로드 경로 설정
    download_path = Path(__file__).resolve().parents[2] / 'data' / 'pdf'
    driver = setup_driver(download_path)
    
    url = 'https://www.dbpia.co.kr/search/topSearch?collectionQuery=&filter=&prefix=&subjectCategory=ND03#a'
    driver.get(url)

    time.sleep(5)

    # 이용순 클릭
    use_sort = driver.find_element(By.CSS_SELECTOR, ".thesisAll__btnWrap .thesis__useSort")
    use_sort.click()

    processed_wrapper = set()
    global RECOMMEND_THESIS
    RECOMMEND_THESIS = True

    while len(processed_wrapper) < 100:
        time.sleep(3)
        
        search_result_wrapper = driver.find_element(By.ID, 'searchResultList')
        wrappers = search_result_wrapper.find_elements(By.CLASS_NAME, 'thesisWrap')

        # 더보기 클릭
        if set(wrappers).issubset(processed_wrapper):
            try:
                view_more = driver.find_element(By.ID, 'mobileViewMore')
                view_more.click()
                time.sleep(3)
            except Exception as e:
                print(f"Error clicking 'View More': {e}")
        
        # PDF 다운로드 및 진행한 wrapper 추가
        processed_wrapper = download_pdf(wrappers, processed_wrapper)
        
        # 마지막 요소로 스크롤 이동
        if wrappers:
            action = webdriver.ActionChains(driver)
            action.move_to_element(wrappers[-1]).perform()


if __name__ == "__main__":
    croling()

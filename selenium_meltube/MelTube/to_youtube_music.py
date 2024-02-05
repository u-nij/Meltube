from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import os
import logging
from datetime import datetime

logger = logging.getLogger()


# 로그의 출력 기준 설정
logger.setLevel(logging.INFO)

# log 출력 형식
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# log를 파일에 출력
filehandler = logging.FileHandler('./log/meltube_{:%Y%m%d}.log'.format(datetime.now()))
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)


def to_youtube_music(title_of_file, num_of_file):

    logger.info(">>>>>>>>>>>>>>>>> Move the playlist to YouTube. >>>>>>>>>>>>>>>>>")
    print("Soundiiz 로그인 페이지로 이동합니다.")

    # 크롬 드라이버 다운
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    driver.maximize_window()


    logger.info("Load the Soundiiz login page.")
    # 로그인 페이지 로딩
    for i in range(3):
        try:
            driver.get("https://soundiiz.com/login")
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="btn btn-primary btn-submit-modal btn-block"]'))
            )
        except:
            logger.error("Page loading failed. Try again. (" + str(i+1) + "/ 3)")
            print("로그인 페이지 로딩을 실패했습니다. (" + str(i+1) + "/ 3)")
            print("재시도 합니다.")
        else:
            break
    logger.info("Page loading succeeded.")
    print("재생 목록을 만들고자 하는 서비스와 연결된 계정에 로그인 한 후, 엔터 키를 눌러주세요.")

    # 플레이리스트 목록 페이지 로딩
    logger.info("Load the playlists page.")
    driver.get("https://soundiiz.com/webapp/playlists")

    input()

    for i in range(3):
        try:
            WebDriverWait(driver, 120).until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="items-reload   playlists-navbar"]'))
            )
        except:
            logger.error("Page loading failed. Try again. (" + str(i+1) + "/ 3)")
            print("플레이리스트 목록 페이지 로딩을 실패했습니다. (" + str(i+1) + "/ 3)")
            print("재시도 합니다.")
        else:
            break
    logger.info("Page loading succeeded.")


    # 플레이리스트 추가 시작
    logger.info("Create a new playlist.")
    print()
    print("재생 목록을 생성합니다.")
    for cnt in range(1, num_of_file + 1):

        # Import Playlist 버튼 클릭
        import_playlist_selector = '//*[@class="btn-job-inner job-control-inner"]'
        import_playlist_element = None
        for i in range(2):
            try:
                import_playlist_element = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, import_playlist_selector))
                )
            except:
                logger.error("Import Playlist button could not be found.")
                print("Import Playlist 버튼을 찾을 수 없습니다.")
                print("로그인되었는지, 또는 계정이 Youtube와 정상 연결되었는지 다시 확인해 주세요.")
            else:
                import_playlist_element.click()
                break
        logger.info("Import Playlist button found.")

        # From File 버튼 클릭
        from_file_selector = '//*[@class="  import-step step-import-file  "]'
        from_file_element = None
        for i in range(2):
            try:
                from_file_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, from_file_selector))
                )
            except:
                logger.error("From File button could not be found.")
                print("파일 불러오기 버튼을 찾을 수 없습니다.")
                print("자동으로 재시도합니다.")
            else:
                from_file_element.click()
                break
        logger.info("From File button found.")
        

        logger.info("Adding Playlist : [" + str(cnt) + "/" + str(num_of_file) + "]")
        print("[" + str(cnt) + "/" + str(num_of_file) + " 진행 중...]")

        # Select File 버튼 클릭
        select_file_selector = '//*[@class="form-file-inner"]/*[1]'
        select_file_element = None
        try:
            select_file_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, select_file_selector))
            )
        except:
            print("파일 선택 버튼을 찾을 수 없습니다.")
            print("자동으로 재시도합니다.")
            logger.error("Select File button could not be found.")

        else:
            abspath = os.path.abspath('.').replace('\\', '/')
            select_file_element.send_keys(abspath + '/' + title_of_file + str(cnt) + '.txt')
        logger.info("Select File button found.")
        print("플레이리스트 목록 선택을 완료하였습니다. 추가할 곡들을 선택하여, 다음 단계를 진행하세요.")
        print("200곡 기준으로 약 15분 정도가 소요됩니다.")

        input("곡 불러오기(Importing)를 완료한 후, Conversion Success 표시가 나타나면 엔터 키를 눌러주세요. ")
        logger.info("The user pressed Conversion Success button.")

        # 초록색 완료 버튼
        success_btn_selector = '//*[@class="btn btn-green btn-submit-modal"]'
        try:
            WebDriverWait(driver,10).until(
                EC.presence_of_element_located((By.XPATH, success_btn_selector))
            )
        except:
            print("플레이스트 생성 과정에서 에러가 발생했습니다.")
            logger.error("Conversion Success button could not be found.")
            logger.error("; An error occurred during the creation of the plate.")
            break
        logger.info("Conversion Success button found.")

        driver.get("https://soundiiz.com/webapp/playlists")

    logger.info("======================== SUCCESS ========================")

    print("프로그램을 종료합니다.")
    logger.info("Exit the program.")


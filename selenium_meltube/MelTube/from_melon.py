from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# from openpyxl import Workbook
import csv
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


# 멜론 플레이리스트로부터 노래 목록 가져오기
def import_melon_playlist():
    logger.info(">>>>>>>>>>>>>>>>> Import Playist from Melon >>>>>>>>>>>>>>>>>")
    driver = webdriver.Chrome()
    print("플레이리스트의 링크를 입력해주세요. ")
    plylstLink = input()
    driver.get(f"{plylstLink}")


    # 페이지 셀렉터
    current_page_selector = '//*[@id="pageObjNavgation"]/div/span/strong'
    next_page_selector = '//*[@id="pageObjNavgation"]/div/span/strong/following-sibling::*[1]'
         
    # 현재 페이지 번호 추출
    current_page_element = None
    try:
        current_page_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, current_page_selector))
        )
    except:
        logger.error("Page loading failed.")
        print("페이지 로딩에 실패했습니다. 비공개 혹은 존재하는 플레이리스트인지 확인해주세요.")
    
    current_page_number = int(current_page_element.text)
    logger.info("Page loading succeeded. Current page number is [" + str(current_page_number) + "]")


       
    # 멜론 플레이리스트 가져오기
    logger.info("Extract the Melon playlist.")
    playlist_element_list = []    
    list_type = ''

    while True:
        # 현재 페이지 번호 검사
        try:
            current_page_element = WebDriverWait(driver, 30).until(
                EC.text_to_be_present_in_element((By.XPATH, current_page_selector), str(current_page_number))
            )
        except:
            logger.error("Page loading failed.")
            print(str(current_page_number) + " 페이지 로딩에 실패했습니다.")
            break

        # 플레이리스트 로딩
        logger.info('Load the playlist.')
        playlist_element = None
        try:
            playlist_selector = '#frm > div > table > tbody'
            playlist_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, playlist_selector))
            )
        except:
            logger.error("Playlist loading failed.")
            print("플레이리스트 로딩에 실패했습니다.")
            break
        logger.info("Playlist loading succeeded.")


        # 데이터 추가
        playlist_element_list.extend(playlist_element.text.split("\n"))


        # 숫자를 이용해 이동할 수 있는 마지막 페이지인지 체크
        logger.info("Extract the last page number.")
        last_page_number = int(driver.find_element(By.XPATH, '//*[@id="pageObjNavgation"]/div/span/*[last()]').text)
        print(str(current_page_number) + " 페이지 추출 중...")
        next_page_element = None
        if last_page_number == current_page_number:
            # '>' or '다음' 버튼 추출
            logger.info("Extract the next button.")
            try:
                driver.find_element(By.XPATH, '//*[@class="btn_next disabled"]')
            except:
                # 1. '>' 버튼이 활성화되어 있는 경우
                logger.info("The next button is abled.")
                # 1-1) 활성화되어 있는 '>' or '다음' 버튼 탐색
                try:
                    list_type = 'MY'
                    next_page_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@class="btn_next"]'))
                    )
                    # 버튼을 눌러 다음 페이지로 이동
                    logger.info("Go to the next page.")
                    current_page_number += 1
                    next_page_element.click()
                except:
                    list_type = 'DJ'
                    try:
                        next_page_element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, '//*[@class="next"]'))
                        )
                        # 버튼을 눌러 다음 페이지로 이동
                        logger.info("Go to the next page.")
                        current_page_number += 1
                        next_page_element.click()

                    except:
                        # 플레이리스트 추가를 종료
                        logger.info("Next page element not found. This is last page.")
                        break
            else:
                # '>' 버튼이 비활성화되어 있는 경우, 플레이리스트 추가를 종료
                list_type = 'MY'
                logger.info("Next page element not found. This is last page.")
                break
        else:
            try:
                # 숫자를 통해 다음 페이지 element 추출
                logger.info("Extract the next page's number.")
                next_page_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, next_page_selector))
                )
            except:
                logger.info("Next page element not found.")
            else:
                # 다음 페이지로 이동
                logger.info("Go to the next page.")
                current_page_number = int(next_page_element.text)
                next_page_element.click()
        

    logger.info("==========================================================")
    return list_type, playlist_element_list
    

def edit_playlist_element_list(list_type, playlist_element_list):
    logger.info(">>>>>>>>>>>>>>>>> Edit playlist element list >>>>>>>>>>>>>>>>>")

    # 데이터 편집
    playlist_element_list = [e for e in playlist_element_list if e not in ['아티스트명 더보기']]
    # 노래 추가
    logger.info("Add a song to list. (type :" + list_type + ")")
    song_list = []
    i = 0

    if list_type == 'MY':
        for i in range(0, len(playlist_element_list), 10):
            tmp_list = playlist_element_list[i:i+10]
            song_list.append([tmp_list[2], tmp_list[-6]]) # song_title, song_singger
    elif list_type == 'DJ':
        for i in range(0, len(playlist_element_list), 6):
            tmp_list = playlist_element_list[i:i+6]
            song_list.append([tmp_list[1], tmp_list[2]]) # song_title, song_singger

    print("추출 완료.")
    logger.info("==========================================================")
    return song_list


# 엑셀 파일 생성 및 노래 목록 입력
def create_excel_file(song_list):
    logger.info(">>>>>>>>>>>>>>>>> Create an Text file >>>>>>>>>>>>>>>>>")
    print("텍스트 파일이 생성되고 있습니다. 잠시만 기다려주세요.")

    # 리스트 분할
    logger.info("Perform list division.")
    list_division = []
    if len(song_list) > 200:
        list_division = [song_list[i:i+200] for i in range(0, len(song_list), 200)]
    else:
        list_division.append(song_list)

    # 텍스트 파일 생성
    logger.info("Create a text file.")

    title = 'MelTube_' + str(datetime.now().strftime('%Y%m%d%H%M')) + '_'


    for i in range(len(list_division)):
        with open('./' + title + str(i+1) + '.txt', 'w', encoding='utf8', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(list_division[i])
    
    logger.info("==========================================================")
    
    return [title, len(list_division)]
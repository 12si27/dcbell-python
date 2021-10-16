from bs4 import BeautifulSoup
import urllib.request, urllib.parse, requests, time

posturl = 'https://gall.dcinside.com/mgallery/board/lists/?id=[gid]&s_type=search_subject_memo&s_keyword=[keyword]'
cmturl = 'https://gall.dcinside.com/mgallery/board/lists/?id=[gid]&s_type=search_comment&s_keyword=[keyword]'

# 정식 갤러리
# posturl = 'https://gall.dcinside.com/board/lists?id=[gid]&s_type=search_subject_memo&s_keyword=[keyword]'
# cmturl = 'https://gall.dcinside.com/board/lists?id=[gid]&s_type=search_comment&s_keyword=[keyword]'

# 미니 갤러리
# posturl = 'https://gall.dcinside.com/mini/board/lists/?id=[gid]&s_type=search_subject_memo&s_keyword=[keyword]'
# cmturl = 'https://gall.dcinside.com/mini/board/lists/?id=[gid]&s_type=search_comment&s_keyword=[keyword]'

# (중요!!! 정식갤 또는 미니갤의 경우에는 위 URL 주석을 해제하여 알맞게 설정하세요!!!)




# 유저 에이전트 값
hdr = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3', 'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8', 'Connection': 'keep-alive'}     

# 텔레그램 봇 요청
def sendTelegramMsg(APIKey, chatID, text):
    r = requests.get("https://api.telegram.org/bot" + APIKey + "/sendMessage?chat_id="
                    + chatID + "&text=" + text + "&parse_mode=Markdown")
    return r


# ================= 사용 전 직접 설정해 주어야 하는 부분 =================

# 텔레그램 설정
TelAPI = "123456789:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" # 텔레그램 봇키
TelChan = "@channelid" # 주소

# tip. 비공개 채널에다 알림을 받고 싶은 경우
# 우선 공개 상태에서 봇을 채널에 추가 & 관리자로 설정한 뒤
# 채널에 아무 메시지나 보낸 후 해당 메시지의 링크를 복사하여
# https://t.me/c/[이 부분의 숫자]/123 를 복사하고
# 앞에 -100을 붙여 TelChan = "[여기에]" 넣으면
# 비공개 채널에서도 알림 전송이 가능합니다.

# 갤러리 설정
# (중요!!! 정식갤 또는 미니갤의 경우에는 위 URL 주석을 해제하여 알맞게 설정하세요!!!)
gallid = 'galleryid'

# 검색 키워드 채우기 (줄바꿈으로 구분합니다. 권장 키워드수는 1~10개입니다)
kw = '''관심
키워드를
여기에
입력하세요'''
keywords = {}

for k in kw.split('\n'):
    keywords[k] = [0,0]

# 무시닉네임 (본인이 쓰는 닉네임을 입력하세요)
passnick = '''본인의
닉네임을
여기에
입력하세요'''.split('\n')


updTime = 300 # 업데이트 주기 (초)

# 약 1초 간격으로 모든 키워드를 순서대로 검색한 뒤 위 주기값만큼 대기합니다.
# 검색 키워드가 10개라면 글 댓글 -> 총 2번 검색하므로 한번에 20번 요청을 보냅니다.
# 그러니 되도록이면 1분 이상 간격으로 설정해 주세요 (너무 잦으면 서버로의 접근이 잠시 막힙니다)

# ========================================================================

# 시간 표시 형식
tType = "%Y-%m-%d %H:%M:%S"
print ("========DCBELL 설정 값========")
print ("Telegram 채널ID: " + TelChan)
print ("업데이트 간격: " + str(updTime) + "초")
print ("==============================")

# 전송 기록 리스트 (중복전송 방지용)
post_hist = []
comm_hist = []


while(1):

    try:
        
        for g in keywords.items():
            
            kw = g[0] # 검색 키워드

            # 0 = 게시글 1 = 댓글
            for i in range(2):

                if (i==0):
                    print("[" + time.strftime(tType) + "] " + kw + " 글 조회 시작...")
                    link = posturl
                else:
                    print("[" + time.strftime(tType) + "] " + kw + " 댓글 조회 시작...")
                    link = cmturl

                time.sleep(0.5)

                prev_postnum = g[1][i] # 마지막 알림 게시글 번호
                link = link.replace('[gid]', gallid).replace('[keyword]', urllib.parse.quote(kw))

                req = urllib.request.Request(link, headers = hdr)
                html = urllib.request.urlopen(req).read()
                soup = BeautifulSoup(html, "html.parser")

                if (i==0): # 게시글 검색
                    link = soup.find_all("tr", { "class" : "ub-content us-post"})
                else: # 게시댓글 검색
                    link = soup.find_all("tr", { "class" : "search"})

                for m in link:

                    tmp = m.find("td", { "class" : "gall_tit ub-word"})

                    # 글(댓글) 제목
                    if "<b>" not in str(tmp):

                        if (i==0): # 게시글
                            title = tmp.a.text   
                            postnum = m.find("td", { "class" : "gall_num"}).text # 게시글 번호
                            postlink = 'https://gall.dcinside.com' + m.a['href']
                            tmp = m.find("td", { "class" : "gall_writer ub-writer"}) # 게시글 작성자 (유동은 IP)
                            name = tmp.find("em").text
                            ip = tmp.find("span", { "class" : "ip"})

                        else: # 게시댓글
                            title = m.a.text
                            tmp = m.a['href']
                            postnum = tmp[tmp.find('fcno=')+5:tmp.find('&fpno')]
                            postlink = 'https://gall.dcinside.com' + m.a['href']
                            name = m.find('span', {'class' : 'nickname'}).text
                            ip = m.find("span", { "class" : "ip"})

                        if ip is not None: ip = ip.text
                        else: ip = "(고닉)"

                        # 아래에 원하는 조건문 넣어도됨
                        if (int(postnum) > int(prev_postnum) and not name in passnick):

                            print()

                            if (i==0):
                                print ("======새 글이 있습니다!=========")
                                print ("│글번호: " + postnum)
                                print ("│글제목: " + title)
                            else:
                                print ("======새 댓글이 있습니다!=======")
                                print ("│댓글번호: " + postnum)
                                print ("│댓글내용: " + title)

                            print ("│닉네임(아이피): " + name + ip )
                            print ("│URL: " + postlink)
                            
                            # 처음에는 보내지않기 (재가동때 알림이 중복으로 가지 않도록)
                            if prev_postnum == 0:
                                print('│(최초 요청이므로 푸시를 보내지 않습니다)')

                            elif ((i==0 and postnum in post_hist) or (i==1 and postnum in comm_hist)):
                                print('│(이미 보낸 요청이므로 푸시를 보내지 않습니다)')
                                
                            else:
                                print ("│푸시 보내는 중...")

                                telmsg = "*" + gallid + " 갤러리 "
                                
                                if (i==0):
                                    telmsg += "새 '" + kw + "' 키워드 글"
                                else:
                                    telmsg += "새 '" + kw + "' 키워드 댓글"

                                telmsg += "*\n" + title.replace(kw,'_'+kw+'_') + " - " + name + ip + "\n" + "[글 링크](" + urllib.parse.quote(postlink) + ")"

                                print(sendTelegramMsg(TelAPI, TelChan, telmsg))
                                print ("│보내기 완료")
                            
                            keywords[kw][i] = postnum
                                
                            print ("===========작업 끝=============\n")
                            break

                        elif (name in passnick):
                            print("제외 닉네임이므로 무시합니다.", name)

                if keywords[kw][i] == 0:
                    print('최초 검색 결과가 없습니다. 검색되면 알림을 보냅니다.')
                    keywords[kw][i] = -1


            time.sleep(1)

    # 오류발생시 무시하고 반복 (서버가 오류가 좀 잦음)
    except Exception as ex: print("[" + time.strftime(tType) + "] 오류 발생! 무시후 다시 시도합니다.", ex)

    print("[" + time.strftime(tType) + "] 대기중... (" + str(updTime) + "초)")
    time.sleep(updTime)

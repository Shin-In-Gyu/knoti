import json
import html as html_lib
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from app.core.config import BASE, get_urls  # 전역 고정 URL 대신 get_urls 사용
from app.core.http import fetch_html
from app.utils.dedupe import dedupe_by_url
from urllib.parse import urljoin, urlparse

# 목록 페이지 HTML → 공지 제목 + 상세URL 리스트 만들기
async def get_notice_list(category: str = "univ"):
    # 1. 카테고리에 맞는 URL과 기본 Seq 가져오기 (config.py의 설정 기반)
    list_url, info_url, default_seq = get_urls(category)
    
    # 2. HTTP 요청 (해당 카테고리의 searchMenuSeq 전달)
    html_text = await fetch_html(list_url, params={"searchMenuSeq": default_seq})
    soup = BeautifulSoup(html_text, "html.parser")

    items = []
    
    # CSS 셀렉터로 공지사항 링크 추출
    for a in soup.select("a.detailLink[data-params]"):
        title = a.get_text(" ", strip=True) or a.get("title", "").strip()
        raw = html_lib.unescape(a.get("data-params", "")).strip()

        # JSON 파싱 및 보정
        try:
            params = json.loads(raw)
        except Exception:
            try:
                params = json.loads(raw.replace("'", '"'))
            except Exception:
                continue
              
        enc_menu_seq = params.get("encMenuSeq")
        enc_menu_board_seq = params.get("encMenuBoardSeq")
        scrt_wrt_yn = params.get("scrtWrtYn", False)

        if not (enc_menu_seq and enc_menu_board_seq):
            continue
        
        # ✅ 버그 수정: 전역 변수 INFO_URL 대신, 위에서 할당받은 지역 변수 info_url을 사용함
        detail_url = (
            f"{info_url}"
            f"?scrtWrtYn={'true' if scrt_wrt_yn else 'false'}"
            f"&encMenuSeq={enc_menu_seq}"
            f"&encMenuBoardSeq={enc_menu_board_seq}"
        )
        items.append({"title": title, "detailUrl": detail_url})

    # 중복 제거 및 결과 반환
    items = dedupe_by_url(items)
    return {"count": len(items), "items": items}

# 상세 페이지 HTML → 제목/본문/첨부파일 파싱
async def get_notice_detail(detail_url: str):
    html = await fetch_html(detail_url)
    soup = BeautifulSoup(html, "html.parser")
    # detail_url에서 해당 사이트의 실제 도메인을 추출 (예: https://sae.kangnam.ac.kr)
    parsed_uri = urlparse(detail_url)
    current_domain = f"{parsed_uri.scheme}://{parsed_uri.netloc}"

    # 제목 파싱
    title_el = soup.select_one("h3, h2, .view_title, .board_view_title, .title")
    title = title_el.get_text(" ", strip=True) if title_el else ""

    # 본문 파싱
    content_el = soup.select_one(".view_cont, .board_view, .contents, #contents, .content")
    content = content_el.get_text("\n", strip=True) if content_el else soup.get_text("\n", strip=True)

    # 첨부파일 파싱
    files = []
    for a in soup.select('a[href*="download"], a[href*="file"], a[href*="atch"], a[href*="FileDown"]'):
        text = a.get_text(" ", strip=True)
        href = a.get("href")
        if href:
            #  BASE 대신 현재 공지사항 사이트의 도메인을 기준으로 조인
            files.append({"name": text or "file", "url": urljoin(current_domain, href)})

    return {"title": title, "content": content, "files": files}
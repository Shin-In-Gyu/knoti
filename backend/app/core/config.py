# backend/app/core/config.py

# 기본 도메인 (기존 공지사항용)
BASE = "https://web.kangnam.ac.kr"

# 카테고리별 도메인 및 메뉴 ID 설정
NOTICE_CONFIGS = {
    # 기존 메인 공지사항 (기존 코드 호환용)
    "univ": {
        "domain": BASE,
        "menu_id": "f19069e6134f8f8aa7f689a4a675e66f",
        "seq": 0
    },
    "academic": {
        "domain": BASE,
        "menu_id": "f19069e6134f8f8aa7f689a4a675e66f",
        "seq": 116
    },
    "scholar": {
        "domain": BASE,
        "menu_id": "f19069e6134f8f8aa7f689a4a675e66f",
        "seq": 117
    },
    # --- 추가하신 학과 공지사항 ---
    "computer": {
        "domain": "https://sae.kangnam.ac.kr",
        "menu_id": "e408e5e7c9f27b8c0d5eeb9e68528b48",
        "seq": 0
    },
    "social": {
        "domain": "https://knusw.kangnam.ac.kr",
        "menu_id": "22dd7f703ec676ffdecdd6b4e4fe1b1b",
        "seq": 0
    },
    "ai": {
        "domain": "https://ace.kangnam.ac.kr",
        "menu_id": "f3a3bfbbc5715e4180657f71177d8bcf",
        "seq": 0
    }
}

def get_urls(category: str):
    """카테고리에 맞는 리스트/상세 URL 및 기본 Seq를 반환합니다."""
    conf = NOTICE_CONFIGS.get(category, NOTICE_CONFIGS["univ"])
    domain = conf["domain"]
    menu_id = conf["menu_id"]
    
    list_url = f"{domain}/menu/{menu_id}.do"
    info_url = f"{domain}/menu/board/info/{menu_id}.do"
    
    return list_url, info_url, conf["seq"]
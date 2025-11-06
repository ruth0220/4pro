# graph/specs.py
GENRES   = ["密室殺人","連続殺人","誘拐","盗難","毒殺"]
STYLES   = ["アガサクリスティ風","横溝正史風","北欧ミステリ風","倒叙形式","本格パズラー"]
TIMES    = ["冬の夜","秋の雨夜","夏の夕暮れ","嵐の夜","早朝"]
PLACES   = ["音楽ホール","山荘","列車個室","劇場楽屋","図書館","温泉旅館","高層マンション"]
CLUE_TYPES = ["key","footstep","log","weapon","fingerprint","witness","camera","document","audio","chemical"]

def parse_clue_types(s: str) -> list[str]:
    """カンマ区切り文字列を正規化し、候補にないものは落とす"""
    if not s:
        return []
    wanted = [t.strip() for t in s.split(",") if t.strip()]
    return [t for t in wanted if t in CLUE_TYPES]

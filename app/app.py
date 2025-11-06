# app/app.py  ← ファイルの先頭にそのまま貼り替え
from pathlib import Path
import sys

# 1) プロジェクトルートを import パスに追加
ROOT = Path(__file__).resolve().parents[1]  # .../multi_agent
sys.path.insert(0, str(ROOT))

# 2) .env を絶対パスで読む
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

# 3) ここからプロジェクト内モジュールをimport
from graph.build import build_app
from graph.specs import GENRES, STYLES, TIMES, PLACES, CLUE_TYPES, parse_clue_types

import chainlit as cl


DEFAULTS = {
    "genre": "密室殺人",
    "style": "アガサクリスティ風",
    "time": "冬の夜",
    "place": "音楽ホール",
    "suspects": 3,
    "clues": 3,
    "clue_types": ["key", "log", "footstep"],
    "max_rounds": 3,
}

HELP = f"""\
使い方：
- 最初のメッセージが「事件テーマ」になります（例：大学での盗難）
- オプションを付けたい場合は key=value をスペース区切りで追記
  例）genre=盗難 style=北欧ミステリ風 time=早朝 place=図書館 suspects=4 clues=5 clue_types=key,document,fingerprint

選べる値：
- genre: {", ".join(GENRES)}
- style: {", ".join(STYLES)}
- time: {", ".join(TIMES)}
- place: {", ".join(PLACES)}
- clue_types（カンマ区切り）: {", ".join(CLUE_TYPES)}
- suspects, clues, max_rounds は整数
"""

def parse_overrides(msg: str) -> tuple[str, dict]:
    """
    ユーザー入力から (テーマ, オプション辞書) を抽出。
    形式: <自由文> [key=value]...
    """
    parts = msg.strip().split()
    opts = {}
    free_tokens = []
    for p in parts:
        if "=" in p:
            k, v = p.split("=", 1)
            k = k.strip().lower()
            v = v.strip()
            opts[k] = v
        else:
            free_tokens.append(p)
    theme = " ".join(free_tokens) if free_tokens else "大学で起きた事件"
    # 型・候補の正規化
    if "suspects" in opts:
        try: opts["suspects"] = int(opts["suspects"])
        except: opts["suspects"] = DEFAULTS["suspects"]
    if "clues" in opts:
        try: opts["clues"] = int(opts["clues"])
        except: opts["clues"] = DEFAULTS["clues"]
    if "max_rounds" in opts:
        try: opts["max_rounds"] = int(opts["max_rounds"])
        except: opts["max_rounds"] = DEFAULTS["max_rounds"]

    if "genre" in opts and opts["genre"] not in GENRES:
        opts["genre"] = DEFAULTS["genre"]
    if "style" in opts and opts["style"] not in STYLES:
        opts["style"] = DEFAULTS["style"]
    if "time" in opts and opts["time"] not in TIMES:
        opts["time"] = DEFAULTS["time"]
    if "place" in opts and opts["place"] not in PLACES:
        opts["place"] = DEFAULTS["place"]

    if "clue_types" in opts:
        opts["clue_types"] = parse_clue_types(opts["clue_types"])
        if not opts["clue_types"]:
            opts["clue_types"] = DEFAULTS["clue_types"]

    return theme, opts

@cl.on_chat_start
async def on_start():
    await cl.Message(
        content=(
            "事件のテーマを入力してください。\n\n"
            + HELP +
            "\n\n例）大学での盗難 genre=盗難 style=北欧ミステリ風 time=早朝 place=図書館 suspects=4 clues=5 clue_types=key,document,fingerprint"
        )
    ).send()

@cl.on_message
async def on_message(msg: cl.Message):
    theme, overrides = parse_overrides(msg.content)

    # 初期stateを組み立て（未指定はデフォルト）
    state = {
        "request": theme,
        "genre": overrides.get("genre", DEFAULTS["genre"]),
        "style": overrides.get("style", DEFAULTS["style"]),
        "time": overrides.get("time", DEFAULTS["time"]),
        "place": overrides.get("place", DEFAULTS["place"]),
        "suspects": overrides.get("suspects", DEFAULTS["suspects"]),
        "clues": overrides.get("clues", DEFAULTS["clues"]),
        "clue_types": overrides.get("clue_types", DEFAULTS["clue_types"]),
        "history": [],
        "max_rounds": overrides.get("max_rounds", DEFAULTS["max_rounds"]),
    }

    await cl.Message(
        content=(
            f"**事件テーマ**: {state['request']}\n"
            f"- ジャンル: {state['genre']} / 作風: {state['style']}\n"
            f"- 時間: {state['time']} / 場所: {state['place']}\n"
            f"- 容疑者数: {state['suspects']} / 証拠数: {state['clues']} / 証拠タイプ: {', '.join(state['clue_types'])}\n"
            f"- ラウンド上限: {state['max_rounds']}\n\n"
            "→ 生成を開始します。"
        )
    ).send()

    app = build_app()

    # LangGraph のイベントを逐次流して表示
    async for ev in app.astream_events(state, version="v1"):
        if ev["event"] == "on_chain_end" and "output" in ev:
            out = ev["output"]
            if out.get("history"):
                last = out["history"][-1]
                role = last.get("role", "agent")
                text = last.get("text", "")
                await cl.Message(content=f"**{role}**: {text}").send()

    await cl.Message("完了。別テーマで続ける場合はメッセージを送ってください。").send()

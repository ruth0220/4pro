# scripts/run_local.py
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parents[1] / ".env")
import os
from graph.build import build_app
import argparse
from graph.specs import GENRES, STYLES, TIMES, PLACES, CLUE_TYPES, parse_clue_types

def parse_args():
    p = argparse.ArgumentParser(description="事件仕様を手動指定（未指定はデフォルト）")
    p.add_argument("--genre",  choices=GENRES,  default="密室殺人",          help="事件ジャンル")
    p.add_argument("--style",  choices=STYLES,  default="アガサクリスティ風", help="作風")
    p.add_argument("--time",   choices=TIMES,   default="冬の夜",            help="舞台の時間")
    p.add_argument("--place",  choices=PLACES,  default="音楽ホール",        help="舞台の場所")
    p.add_argument("--suspects", type=int, default=3, help="容疑者数 S1..Sn")
    p.add_argument("--clues",    type=int, default=3, help="証拠数 C1..Cm")
    p.add_argument("--clue-types", default="key,log,footstep",
                   help=f"証拠タイプをカンマで区切り。候補: {','.join(CLUE_TYPES)}")
    p.add_argument("--request", default="大学構内で起きた事件", help="自由テーマ（任意）")
    p.add_argument("--max-rounds", type=int, default=3, help="最大ラウンド数")
    p.add_argument("--show-judge", action="store_true", help="Judgeの評価HUDを逐次表示（今後拡張用）")
    p.add_argument("--log-judge", default="", help="Judge評価をJSONLで保存するパス")
    return p.parse_args()

def main():
    load_dotenv()
    args = parse_args()

    # clue-types を正規化
    clue_types = parse_clue_types(args.clue_types)

    # 初期 state を構成
    init_state = {
        "request": args.request,
        "genre": args.genre,
        "style": args.style,
        "time": args.time,
        "place": args.place,
        "suspects": args.suspects,
        "clues": args.clues,
        "clue_types": clue_types,
        "history": [],
        "max_rounds": args.max_rounds
    }

    app = build_app()
    final = app.invoke(init_state)

    for m in final["history"]:
        print(f"[{m['role']}] {m['text']}\n")
    print(f"overall_score={final.get('overall_score')}  round={final.get('round')}")

if __name__ == "__main__":
    main()

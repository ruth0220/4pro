# graph/state.py
from typing import TypedDict, List, Dict, Any

class Message(Dict[str, Any]):
    pass

class State(TypedDict, total=False):
    # 事件テーマ（自由入力も残す）
    request: str
    # ユーザーの選択（未指定はデフォルト）
    genre: str
    style: str
    time: str
    place: str
    suspects: int
    clues: int
    clue_types: List[str]

    # 実行状態
    history: List[Message]
    round: int
    max_rounds: int
    duplicate_score: float
    hard_contradiction: bool
    overall_score: float

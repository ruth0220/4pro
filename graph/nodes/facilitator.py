def _dup_score(last_text: str, prev_text: str) -> float:
    """超簡易の重複スコア（単語集合の重なり率）。後で埋め込みに差し替えOK。"""
    if not last_text or not prev_text:
        return 0.0
    a = set(last_text.split())
    b = set(prev_text.split())
    if not a:
        return 0.0
    return min(1.0, len(a & b) / max(8, len(a)))  # 分母を最低8にして過剰検出を抑制

def node_facilitator(state):
    hist = state.get("history", [])
    if len(hist) < 2:
        return {}

    last = hist[-1]["text"]
    prev = hist[-2]["text"]
    dup = _dup_score(last, prev)

    # 本格的な矛盾検出は helpers 側へ（ここではダミー False）
    hard = False

    updates = {"duplicate_score": dup, "hard_contradiction": hard}
    msg = None
    if dup >= 0.90:
        msg = "今の意見は直前の内容にとても近いようです。新しい視点や根拠を加えてください。"
    elif hard:
        msg = "これまでの証言と食い違っている点があります。根拠をもう一度確かめてください。"

    if msg:
        updates["history"] = hist + [{"role": "facilitator", "text": msg}]
    return updates

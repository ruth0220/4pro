# graph/build.py
from langgraph.graph import StateGraph, END
from .state import State
from .nodes.case_gen import node_case_gen
from .nodes.detective_a import node_detective_a
from .nodes.detective_b import node_detective_b
from .nodes.detective_c import node_detective_c
from .nodes.facilitator import node_facilitator
from .nodes.judge import node_judge

# 探偵ノードの後の分岐条件
def cond_after_detective(state: State):
    if state.get("hard_contradiction"):
        return "facilitator"          # 致命的矛盾→ファシリで整える
    if state.get("duplicate_score", 0) >= 0.90:
        return "repeat"               # 重複が大きい→同じ探偵に再発言
    return "next"                     # 通常は次の探偵へ

# ジャッジ後：早期終了 or 次ラウンド
def cond_after_judge(state: State):
    if state.get("overall_score", 0) >= 0.85:
        return END                    # 十分な確信→終了
    if state.get("round", 1) > state.get("max_rounds", 3):
        return END                    # 既定ラウンド超過→終了
    return "next_round"               # それ以外は次ラウンドへ

def build_app():
    g = StateGraph(State)

    # ノード登録
    g.add_node("case_gen", node_case_gen)
    g.add_node("A", node_detective_a)
    g.add_node("B", node_detective_b)
    g.add_node("C", node_detective_c)
    g.add_node("facilitator", node_facilitator)
    g.add_node("judge", node_judge)

    # エントリ
    g.set_entry_point("case_gen")
    g.add_edge("case_gen", "A")

    # A の後
    g.add_conditional_edges("A", cond_after_detective, {
        "repeat": "A",
        "facilitator": "facilitator",
        "next": "B",
    })
    g.add_edge("facilitator", "B")

    # B の後
    g.add_conditional_edges("B", cond_after_detective, {
        "repeat": "B",
        "facilitator": "facilitator",
        "next": "C",
    })
    g.add_edge("facilitator", "C")

    # C の後 → Judge
    g.add_conditional_edges("C", cond_after_detective, {
        "repeat": "C",
        "facilitator": "facilitator",
        "next": "judge",
    })
    g.add_edge("facilitator", "judge")

    # Judge の後 → 次ラウンド or 終了
    g.add_conditional_edges("judge", cond_after_judge, {
        "next_round": "A",
        END: END
    })

    return g.compile()

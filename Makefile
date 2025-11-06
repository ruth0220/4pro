# multi_agent/Makefile

# 変数（必要に応じて変更）
PY=python
CHAINLIT=chainlit
SCRIPT=scripts/run_graph_cli.py

# 依存インストール
install:
	$(PY) -m pip install -r requirements.txt

# CLI 実行（ARGS で引数を渡す）
run:
	$(PY) $(SCRIPT) $(ARGS)

# 例: make run ARGS="--genre 盗難 --style 北欧ミステリ風 --time 早朝 --place 図書館 --suspects 4 --clues 5 --clue-types key,document,fingerprint"

# Chainlit 起動（ブラウザUI）
ui:
	$(CHAINLIT) run app/chainlit_app.py -w

# ログ消去
clean-logs:
	rm -f data/logs/* || true

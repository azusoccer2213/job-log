import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- ページ設定 ---
st.set_page_config(page_title="就活総合管理アプリ", layout="wide")

# --- データ管理設定 ---
# ページごとに異なるCSVファイルを使用し、データを分離する
FILES = {
    "企業分析": "company_analysis.csv",
    "ES": "es_data.csv",
    "自己分析": "self_analysis.csv",
    "メモ": "recruit_memo.csv"
}

COLUMNS = {
    "企業分析": ["更新日", "企業名", "業界", "志望度", "強み・魅力", "懸念点", "選考状況"],
    "ES": ["更新日", "企業名", "設問", "文字数制限", "回答案", "現在文字数", "提出期限"],
    "自己分析": ["更新日", "項目（強み/弱み/経験など）", "具体的なエピソード", "面接でのアピール方法"],
    "メモ": ["日付", "カテゴリ", "タイトル", "内容"]
}

def load_data(key):
    filename = FILES[key]
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=COLUMNS[key])

def save_data(key, df):
    df.to_csv(FILES[key], index=False)

# --- サイドバー（ナビゲーション） ---
with st.sidebar:
    st.title("💼 就活マネジメント")
    st.markdown("---")
    menu = st.radio(
        "メニューを選択",
        ["① ホーム", "② 企業分析", "③ ESページ", "④ 自己分析", "⑤ リクルート情報メモ"]
    )

# ==========================================
# ① ホーム（ダッシュボード）
# ==========================================
if menu == "① ホーム":
    st.title("🏠 ホーム・ダッシュボード")
    st.write("各データの登録状況や、直近のタスクを確認します。")
    
    col1, col2, col3 = st.columns(3)
    
    df_company = load_data("企業分析")
    df_es = load_data("ES")
    
    with col1:
        st.metric("登録企業数", f"{len(df_company)} 社")
    with col2:
        st.metric("作成中・提出済ES数", f"{len(df_es)} 件")
    with col3:
        # ESの提出期限が近いものをピックアップするなどの拡張用
        st.metric("本日のタスク", "随時確認")

    st.markdown("---")
    st.subheader("📌 選考状況サマリー")
    if not df_company.empty:
        status_counts = df_company["選考状況"].value_counts()
        st.bar_chart(status_counts)
    else:
        st.info("企業分析ページから企業情報を登録すると、ここに選考状況のグラフが表示されます。")

# ==========================================
# ② 企業分析ページ
# ==========================================
elif menu == "② 企業分析":
    st.title("🏢 企業分析")
    df_company = load_data("企業分析")

    with st.expander("➕ 新規企業の登録・分析", expanded=True):
        with st.form("company_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                company = st.text_input("企業名*")
                industry = st.selectbox("業界", ["メーカー", "IT・通信", "商社", "金融", "コンサル", "インフラ", "その他"])
                rank = st.slider("志望度 (1:低 - 5:高)", 1, 5, 3)
            with col2:
                status = st.selectbox("選考状況", ["興味あり", "説明会待ち", "ES提出済", "面接(1次)", "面接(2次)", "最終面接", "内定", "お見送り"])
            
            pros = st.text_area("強み・魅力（なぜこの企業か）")
            cons = st.text_area("懸念点・他社との比較")
            
            if st.form_submit_button("登録する"):
                if company:
                    new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), company, industry, rank, pros, cons, status]], columns=COLUMNS["企業分析"])
                    df_company = pd.concat([df_company, new_row], ignore_index=True)
                    save_data("企業分析", df_company)
                    st.success(f"{company} の情報を登録しました。")
                    st.rerun()
                else:
                    st.error("企業名は必須入力です。")

    st.subheader("📋 登録企業一覧")
    if not df_company.empty:
        st.dataframe(df_company, use_container_width=True)
    else:
        st.info("データがありません。")

# ==========================================
# ③ ESページ（エントリーシート管理）
# ==========================================
elif menu == "③ ESページ":
    st.title("📝 ES（エントリーシート）管理")
    df_es = load_data("ES")

    with st.expander("➕ 新規ES設問の登録", expanded=True):
        with st.form("es_form", clear_on_submit=True):
            company_es = st.text_input("企業名*")
            question = st.text_area("設問内容*")
            col1, col2 = st.columns(2)
            with col1:
                limit = st.number_input("文字数制限", min_value=0, step=50, value=400)
            with col2:
                deadline = st.date_input("提出期限")
            
            answer = st.text_area("回答案", height=200)
            
            if st.form_submit_button("保存する"):
                if company_es and question:
                    current_len = len(answer.replace("\n", "").replace(" ", "").replace("　", ""))
                    new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), company_es, question, limit, answer, current_len, deadline]], columns=COLUMNS["ES"])
                    df_es = pd.concat([df_es, new_row], ignore_index=True)
                    save_data("ES", df_es)
                    st.success("ESを保存しました。")
                    st.rerun()
                else:
                    st.error("企業名と設問内容は必須です。")

    st.subheader("📋 ES一覧")
    if not df_es.empty:
        st.dataframe(df_es, use_container_width=True)
    else:
        st.info("データがありません。")

# ==========================================
# ④ 自己分析ページ
# ==========================================
elif menu == "④ 自己分析":
    st.title("🔍 自己分析")
    st.write("研究活動で培った論理的思考力やデータ分析能力など、客観的な事実に基づいたエピソードを整理しましょう。")
    df_self = load_data("自己分析")

    with st.expander("➕ 自己分析の追加", expanded=True):
        with st.form("self_form", clear_on_submit=True):
            category = st.selectbox("項目", ["強み", "弱み", "学生時代に力を入れたこと(ガクチカ)", "研究内容", "志望動機の軸"])
            episode = st.text_area("具体的なエピソード（STAR法などを意識して詳細に）", height=150)
            appeal = st.text_area("面接でのアピール方法（企業にどう貢献できるか）")
            
            if st.form_submit_button("記録する"):
                if episode:
                    new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), category, episode, appeal]], columns=COLUMNS["自己分析"])
                    df_self = pd.concat([df_self, new_row], ignore_index=True)
                    save_data("自己分析", df_self)
                    st.success("自己分析を記録しました。")
                    st.rerun()
                else:
                    st.error("エピソードを入力してください。")

    st.subheader("📋 自己分析データ")
    if not df_self.empty:
        st.dataframe(df_self, use_container_width=True)
    else:
        st.info("データがありません。")

# ==========================================
# ⑤ リクルート情報メモページ
# ==========================================
elif menu == "⑤ リクルート情報メモ":
    st.title("📓 リクルート情報・メモ")
    df_memo = load_data("メモ")

    with st.expander("➕ メモの追加", expanded=True):
        with st.form("memo_form", clear_on_submit=True):
            memo_date = st.date_input("日付", datetime.now())
            category_memo = st.selectbox("カテゴリ", ["エージェント面談", "OB/OG訪問", "イベント・合同説明会", "その他"])
            title = st.text_input("タイトル*")
            content = st.text_area("内容・議事録・To-Doなど", height=150)
            
            if st.form_submit_button("メモを保存"):
                if title:
                    new_row = pd.DataFrame([[memo_date, category_memo, title, content]], columns=COLUMNS["メモ"])
                    df_memo = pd.concat([df_memo, new_row], ignore_index=True)
                    save_data("メモ", df_memo)
                    st.success("メモを保存しました。")
                    st.rerun()
                else:
                    st.error("タイトルを入力してください。")

    st.subheader("📋 メモ一覧")
    if not df_memo.empty:
        st.dataframe(df_memo.iloc[::-1], use_container_width=True) # メモは新しい順に表示
    else:
        st.info("データがありません。")

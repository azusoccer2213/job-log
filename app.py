import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- ページ設定 ---
st.set_page_config(page_title="就活総合管理アプリ", layout="wide")

# --- データ管理設定 ---
FILES = {
    "企業分析": "company_analysis.csv",
    "ES": "es_data.csv",
    "自己分析": "self_analysis.csv",
    "メモ": "recruit_memo.csv"
}

COLUMNS = {
    "企業分析": ["更新日", "企業名", "業界", "志望度", "強み・魅力", "懸念点", "選考状況"],
    "ES": ["更新日", "企業名", "設問", "文字数制限", "回答案", "現在文字数", "提出期限"],
    "自己分析": ["更新日", "項目", "具体的なエピソード", "面接でのアピール方法"],
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
    
    col1, col2 = st.columns(2)
    df_company = load_data("企業分析")
    df_es = load_data("ES")
    
    with col1:
        st.metric("登録企業数", f"{len(df_company)} 社")
    with col2:
        st.metric("作成中・提出済ES数", f"{len(df_es)} 件")

    st.markdown("---")
    st.subheader("📌 選考状況サマリー")
    if not df_company.empty:
        status_counts = df_company["選考状況"].value_counts()
        st.bar_chart(status_counts)
    else:
        st.info("企業情報が登録されていません。")

# ==========================================
# ② 企業分析ページ（フィルター機能追加）
# ==========================================
elif menu == "② 企業分析":
    st.title("🏢 企業分析")
    df_company = load_data("企業分析")

    with st.expander("➕ 新規企業の登録・分析", expanded=False): # デフォルトは閉じておく
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
                    st.success(f"{company} を登録しました。")
                    st.rerun()

    st.subheader("📋 登録企業一覧")
    if not df_company.empty:
        # ★追加：選考状況で表示を絞り込む機能
        selected_status = st.multiselect(
            "📌 選考状況で絞り込む", 
            options=df_company["選考状況"].unique(),
            default=df_company["選考状況"].unique() # 最初はすべて表示
        )
        filtered_df = df_company[df_company["選考状況"].isin(selected_status)]
        
        # hide_index=True で左端の不要な数字を消してスッキリ見せる
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    else:
        st.info("データがありません。")

# ==========================================
# ③ ESページ（カード形式表示に変更）
# ==========================================
elif menu == "③ ESページ":
    st.title("📝 ES（エントリーシート）管理")
    df_es = load_data("ES")

    with st.expander("➕ 新規ES設問の登録", expanded=False):
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

    st.subheader("📖 保存済みのES一覧")
    if not df_es.empty:
        # ★変更：表ではなく、開閉式のカードで表示して全文を読めるようにする
        for i, row in df_es.iterrows():
            with st.expander(f"🏢 {row['企業名']} | ⏳ 期限: {row['提出期限']} | ✏️ {row['現在文字数']}/{row['文字数制限']}字"):
                st.markdown(f"**【設問】**\n{row['設問']}")
                st.markdown("---")
                # 読み取り専用のテキストエリアで表示（スクロールして全文読める）
                st.text_area("【回答案】", row['回答案'], height=150, disabled=True, key=f"es_read_{i}")
    else:
        st.info("データがありません。")

# ==========================================
# ④ 自己分析ページ（カード形式表示に変更）
# ==========================================
elif menu == "④ 自己分析":
    st.title("🔍 自己分析")
    df_self = load_data("自己分析")

    with st.expander("➕ 自己分析の追加", expanded=False):
        with st.form("self_form", clear_on_submit=True):
            category = st.selectbox("項目", ["強み", "弱み", "学生時代に力を入れたこと(ガクチカ)", "研究内容", "志望動機の軸"])
            episode = st.text_area("具体的なエピソード", height=150)
            appeal = st.text_area("面接でのアピール方法")
            
            if st.form_submit_button("記録する"):
                if episode:
                    new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), category, episode, appeal]], columns=COLUMNS["自己分析"])
                    df_self = pd.concat([df_self, new_row], ignore_index=True)
                    save_data("自己分析", df_self)
                    st.success("自己分析を記録しました。")
                    st.rerun()

    st.subheader("📖 自己分析エピソード一覧")
    if not df_self.empty:
        # ★変更：カテゴリごとに見やすいカード形式
        for i, row in df_self.iterrows():
            with st.expander(f"🏷️ {row['項目']} （更新日: {row['更新日']}）"):
                st.markdown("**【具体的なエピソード】**")
                st.write(row['具体的なエピソード'])
                st.markdown("---")
                st.markdown("**【面接でのアピール方法】**")
                st.write(row['面接でのアピール方法'])
    else:
        st.info("データがありません。")

# ==========================================
# ⑤ リクルート情報メモページ（カード形式表示に変更）
# ==========================================
elif menu == "⑤ リクルート情報メモ":
    st.title("📓 リクルート情報・メモ")
    df_memo = load_data("メモ")

    with st.expander("➕ メモの追加", expanded=False):
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

    st.subheader("📖 メモ一覧")
    if not df_memo.empty:
        # 新しい順に並び替えてから表示
        df_memo_sorted = df_memo.sort_values(by="日付", ascending=False)
        for i, row in df_memo_sorted.iterrows():
            with st.expander(f"📅 {row['日付']} | 📂 {row['カテゴリ']} | {row['タイトル']}"):
                st.write(row['内容'])
    else:
        st.info("データがありません。")

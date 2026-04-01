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
# ① ホーム（ダッシュボード・締め切り管理）
# ==========================================
if menu == "① ホーム":
    st.title("🏠 ホーム・ダッシュボード")
    
    # データの読み込み
    df_es = load_data("ES")
    df_memo = load_data("メモ")
    df_company = load_data("企業分析")
    today = datetime.now().date()

    # --- 上段：クイック統計 ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("登録企業数", f"{len(df_company)} 社")
    with col2:
        # ES提出期限が今日以降のものをカウント
        if not df_es.empty:
            df_es['提出期限'] = pd.to_datetime(df_es['提出期限']).dt.date
            active_es = len(df_es[df_es['提出期限'] >= today])
            st.metric("進行中のES", f"{active_es} 件")
        else:
            st.metric("進行中のES", "0 件")
    with col3:
        # 今後の予定（今日以降のメモ）をカウント
        if not df_memo.empty:
            df_memo['日付'] = pd.to_datetime(df_memo['日付']).dt.date
            upcoming_events = len(df_memo[df_memo['日付'] >= today])
            st.metric("今後の予定", f"{upcoming_events} 件")
        else:
            st.metric("今後の予定", "0 件")

    st.markdown("---")

    # --- 中段：締め切りとスケジュール ---
    left_col, right_col = st.columns(2)

    with left_col:
        st.subheader("⚠️ 近日の提出期限 (ES)")
        if not df_es.empty:
            # 今日以降の締め切りを近い順にソート
            upcoming_es = df_es[df_es['提出期限'] >= today].sort_values('提出期限')
            if not upcoming_es.empty:
                for _, row in upcoming_es.iterrows():
                    days_left = (row['提出期限'] - today).days
                    alert_type = "🔴" if days_left <= 3 else "🟡"
                    st.warning(f"{alert_type} **{row['提出期限']}** | {row['企業名']}\n\n {row['設問'][:30]}...")
            else:
                st.info("現在、提出期限が設定されたESはありません。")
        else:
            st.info("ESデータがありません。")

    with right_col:
        st.subheader("📅 今後のスケジュール")
        if not df_memo.empty:
            # 今日以降の予定を近い順にソート
            upcoming_sched = df_memo[df_memo['日付'] >= today].sort_values('日付')
            if not upcoming_sched.empty:
                for _, row in upcoming_sched.iterrows():
                    st.info(f"🔹 **{row['日付']}** | [{row['カテゴリ']}] {row['タイトル']}")
            else:
                st.info("今後の予定はありません。")
        else:
            st.info("メモデータがありません。")

    st.markdown("---")
    st.subheader("📌 選考状況グラフ")
    if not df_company.empty:
        status_counts = df_company["選考状況"].value_counts()
        st.bar_chart(status_counts)

# ==========================================
# ② 企業分析ページ
# ==========================================
elif menu == "② 企業分析":
    st.title("🏢 企業分析")
    df_company = load_data("企業分析")

    with st.expander("➕ 新規企業の登録・分析", expanded=False):
        with st.form("company_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                company = st.text_input("企業名*")
                industry = st.selectbox("業界", ["メーカー", "IT・通信", "商社", "金融", "コンサル", "インフラ", "その他"])
                rank = st.slider("志望度 (1:低 - 5:高)", 1, 5, 3)
            with col2:
                status = st.selectbox("選考状況", ["興味あり", "説明会待ち", "ES提出済", "面接(1次)", "面接(2次)", "最終面接", "内定", "お見送り"])
            
            pros = st.text_area("強み・魅力（生理学研究の知見がどう活かせるか等）")
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
        selected_status = st.multiselect("📌 状況で絞り込む", options=df_company["選考状況"].unique(), default=df_company["選考状況"].unique())
        filtered_df = df_company[df_company["選考状況"].isin(selected_status)]
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

# ==========================================
# ③ ESページ
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
                    st.success("ESを保存しました。ホームの締め切りリストに反映されます。")
                    st.rerun()

    st.subheader("📖 ES一覧")
    if not df_es.empty:
        for i, row in df_es.iterrows():
            with st.expander(f"🏢 {row['企業名']} | ⏳ 期限: {row['提出期限']} | ✏️ {row['現在文字数']}/{row['文字数制限']}字"):
                st.markdown(f"**【設問】**\n{row['設問']}")
                st.text_area("【回答案】", row['回答案'], height=150, disabled=True, key=f"es_read_{i}")

# ==========================================
# ④ 自己分析ページ
# ==========================================
elif menu == "④ 自己分析":
    st.title("🔍 自己分析")
    df_self = load_data("自己分析")

    with st.expander("➕ 新規エピソード追加", expanded=False):
        with st.form("self_form", clear_on_submit=True):
            category = st.selectbox("項目", ["強み", "弱み", "ガクチカ", "研究内容(生理学)", "志望動機の軸"])
            episode = st.text_area("具体的なエピソード", height=150)
            appeal = st.text_area("面接でのアピール方法")
            
            if st.form_submit_button("記録する"):
                if episode:
                    new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), category, episode, appeal]], columns=COLUMNS["自己分析"])
                    df_self = pd.concat([df_self, new_row], ignore_index=True)
                    save_data("自己分析", df_self)
                    st.success("自己分析を記録しました。")
                    st.rerun()

    st.subheader("📖 エピソード一覧")
    if not df_self.empty:
        for i, row in df_self.iterrows():
            with st.expander(f"🏷️ {row['項目']} （{row['更新日']}）"):
                st.write(row['具体的なエピソード'])
                st.caption("【アピール方法】")
                st.write(row['面接でのアピール方法'])

# ==========================================
# ⑤ リクルート情報メモページ
# ==========================================
elif menu == "⑤ リクルート情報メモ":
    st.title("📓 リクルート情報・メモ")
    df_memo = load_data("メモ")

    with st.expander("➕ 予定・メモの追加（今後の予定はホームに表示されます）", expanded=False):
        with st.form("memo_form", clear_on_submit=True):
            memo_date = st.date_input("予定日/実施日", datetime.now())
            category_memo = st.selectbox("カテゴリ", ["面接", "エージェント面談", "OB/OG訪問", "説明会", "その他"])
            title = st.text_input("タイトル*")
            content = st.text_area("内容・メモ", height=150)
            
            if st.form_submit_button("保存する"):
                if title:
                    new_row = pd.DataFrame([[memo_date, category_memo, title, content]], columns=COLUMNS["メモ"])
                    df_memo = pd.concat([df_memo, new_row], ignore_index=True)
                    save_data("メモ", df_memo)
                    st.success("保存しました。未来の日付ならホームのスケジュールに表示されます。")
                    st.rerun()

    st.subheader("📖 履歴・予定一覧")
    if not df_memo.empty:
        df_memo_sorted = df_memo.sort_values(by="日付", ascending=False)
        for i, row in df_memo_sorted.iterrows():
            with st.expander(f"📅 {row['日付']} | 📂 {row['カテゴリ']} | {row['タイトル']}"):
                st.write(row['内容'])

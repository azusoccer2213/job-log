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

# パスワードとIDを記録できるように列を追加
COLUMNS = {
    "企業分析": ["更新日", "企業名", "業界", "志望度", "強み・魅力", "懸念点", "選考状況"],
    "ES": ["更新日", "企業名", "設問", "文字数制限", "回答案", "現在文字数", "提出期限"],
    "自己分析": ["更新日", "項目", "具体的なエピソード", "面接でのアピール方法"],
    "メモ": ["日付", "カテゴリ", "タイトル", "ID_メールアドレス", "パスワード", "内容"]
}

def load_data(key):
    filename = FILES[key]
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        # 既存のCSVに新しい列が足りない場合、自動的に補完するロジック
        for col in COLUMNS[key]:
            if col not in df.columns:
                df[col] = ""
        return df[COLUMNS[key]] # 列順を整理して返す
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
# ① ホーム
# ==========================================
if menu == "① ホーム":
    st.title("🏠 ホーム・ダッシュボード")
    df_es = load_data("ES")
    df_memo = load_data("メモ")
    df_company = load_data("企業分析")
    today = datetime.now().date()

    col1, col2, col3 = st.columns(3)
    with col1: st.metric("登録企業数", f"{len(df_company)} 社")
    with col2:
        if not df_es.empty:
            df_es['提出期限'] = pd.to_datetime(df_es['提出期限']).dt.date
            active_es = len(df_es[df_es['提出期限'] >= today])
            st.metric("進行中のES", f"{active_es} 件")
        else: st.metric("進行中のES", "0 件")
    with col3:
        if not df_memo.empty:
            df_memo['日付'] = pd.to_datetime(df_memo['日付']).dt.date
            upcoming_events = len(df_memo[df_memo['日付'] >= today])
            st.metric("今後の予定", f"{upcoming_events} 件")
        else: st.metric("今後の予定", "0 件")

    st.markdown("---")
    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader("⚠️ 近日の提出期限 (ES)")
        if not df_es.empty:
            upcoming_es = df_es[df_es['提出期限'] >= today].sort_values('提出期限')
            for _, row in upcoming_es.iterrows():
                days_left = (row['提出期限'] - today).days
                alert = "🔴" if days_left <= 3 else "🟡"
                st.warning(f"{alert} **{row['提出期限']}** | {row['企業名']}")
        else: st.info("予定なし")
    with right_col:
        st.subheader("📅 今後のスケジュール")
        if not df_memo.empty:
            upcoming_sched = df_memo[df_memo['日付'] >= today].sort_values('日付')
            for _, row in upcoming_sched.iterrows():
                st.info(f"🔹 **{row['日付']}** | [{row['カテゴリ']}] {row['タイトル']}")

# ==========================================
# ② 企業分析 / ③ ES / ④ 自己分析 (変更なしのため省略不可・一括提示)
# ==========================================
elif menu == "② 企業分析":
    st.title("🏢 企業分析")
    df_company = load_data("企業分析")
    with st.expander("➕ 新規企業の登録", expanded=False):
        with st.form("company_form", clear_on_submit=True):
            company = st.text_input("企業名*")
            industry = st.selectbox("業界", ["メーカー", "IT・通信", "商社", "金融", "コンサル", "インフラ", "その他"])
            status = st.selectbox("選考状況", ["興味あり", "説明会待ち", "ES提出済", "面接(1次)", "面接(2次)", "最終面接", "内定", "お見送り"])
            if st.form_submit_button("登録"):
                new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), company, industry, 3, "", "", status]], columns=COLUMNS["企業分析"])
                df_company = pd.concat([df_company, new_row], ignore_index=True)
                save_data("企業分析", df_company)
                st.rerun()
    st.dataframe(df_company, use_container_width=True, hide_index=True)

elif menu == "③ ESページ":
    st.title("📝 ES管理")
    df_es = load_data("ES")
    with st.expander("➕ 新規ES登録", expanded=False):
        with st.form("es_form", clear_on_submit=True):
            co = st.text_input("企業名*")
            q = st.text_area("設問*")
            dl = st.date_input("期限")
            ans = st.text_area("回答案")
            if st.form_submit_button("保存"):
                new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), co, q, 400, ans, len(ans), dl]], columns=COLUMNS["ES"])
                df_es = pd.concat([df_es, new_row], ignore_index=True)
                save_data("ES", df_es)
                st.rerun()
    for i, row in df_es.iterrows():
        with st.expander(f"{row['企業名']} ({row['提出期限']})"):
            st.write(row['設問'])
            st.text_area("回答", row['回答案'], disabled=True, key=f"es_{i}")

elif menu == "④ 自己分析":
    st.title("🔍 自己分析")
    df_self = load_data("自己分析")
    with st.expander("➕ 新規追加", expanded=False):
        with st.form("self_form", clear_on_submit=True):
            cat = st.selectbox("項目", ["強み", "研究内容", "ガクチカ"])
            epi = st.text_area("エピソード")
            if st.form_submit_button("保存"):
                new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), cat, epi, ""]], columns=COLUMNS["自己分析"])
                df_self = pd.concat([df_self, new_row], ignore_index=True)
                save_data("自己分析", df_self)
                st.rerun()
    for i, row in df_self.iterrows():
        with st.expander(row['項目']): st.write(row['具体的なエピソード'])

# ==========================================
# ⑤ リクルート情報メモページ（ID・パスワード項目追加）
# ==========================================
elif menu == "⑤ リクルート情報メモ":
    st.title("📓 リクルート情報・メモ")
    st.warning("⚠️ パスワードはこのアプリ内に平文で保存されます。取り扱いには十分注意してください。")
    df_memo = load_data("メモ")

    with st.expander("➕ 予定・メモ・アカウント情報の追加", expanded=False):
        with st.form("memo_form", clear_on_submit=True):
            memo_date = st.date_input("日付", datetime.now())
            category_memo = st.selectbox("カテゴリ", ["マイページ情報", "面接", "エージェント面談", "OB訪問", "その他"])
            title = st.text_input("タイトル（企業名など）*")
            
            # --- アカウント情報入力欄 ---
            col_acc1, col_acc2 = st.columns(2)
            with col_acc1:
                login_id = st.text_input("ID / メールアドレス")
            with col_acc2:
                # type="password" にすることで入力中に伏せ字になります
                password = st.text_input("パスワード", type="password", help="保存後はカード内で確認できます")
            
            content = st.text_area("内容・メモ（URLなど）", height=150)
            
            if st.form_submit_button("保存する"):
                if title:
                    new_row = pd.DataFrame([[memo_date, category_memo, title, login_id, password, content]], columns=COLUMNS["メモ"])
                    df_memo = pd.concat([df_memo, new_row], ignore_index=True)
                    save_data("メモ", df_memo)
                    st.success("情報を保存しました。")
                    st.rerun()
                else:
                    st.error("タイトルを入力してください。")

    st.subheader("📖 履歴・アカウント情報一覧")
    if not df_memo.empty:
        df_memo_sorted = df_memo.sort_values(by="日付", ascending=False)
        for i, row in df_memo_sorted.iterrows():
            # タイトルにカテゴリを表示して見やすく
            with st.expander(f"📅 {row['日付']} | 📂 {row['カテゴリ']} | {row['タイトル']}"):
                # アカウント情報の表示
                if row['ID_メールアドレス'] or row['パスワード']:
                    st.markdown("---")
                    st.markdown("**🔐 アカウント情報**")
                    st.code(f"ID: {row['ID_メールアドレス']}\nPASS: {row['パスワード']}", language="text")
                    st.markdown("---")
                
                st.markdown("**【詳細メモ】**")
                st.write(row['内容'])
    else:
        st.info("データがありません。")

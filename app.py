import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- ページ設定 ---
st.set_page_config(page_title="就活総合管理アプリ (Cloud版)", layout="wide", page_icon="💼")

# --- スプレッドシート接続設定 ---
# .streamlit/secrets.toml または Streamlit CloudのSecretsに設定した情報を使用
conn = st.connection("gsheets", type=GSheetsConnection)

SHEET_NAMES = {
    "企業分析": "company_analysis",
    "ES": "es_data",
    "自己分析": "self_analysis",
    "メモ": "recruit_memo"
}

COLUMNS = {
    "企業分析": ["更新日", "企業名", "業界", "志望度", "強み", "弱み・課題", "機会・チャンス", "ライバル・競合", "選考状況", "ID_メールアドレス", "パスワード"],
    "ES": ["更新日", "企業名", "設問", "文字数制限", "回答案", "現在文字数", "提出期限"],
    "自己分析": ["更新日", "項目", "具体的なエピソード", "面接でのアピール方法"],
    "メモ": ["日付", "カテゴリ", "タイトル", "ID_メールアドレス", "パスワード", "内容"]
}

def load_data(key):
    """スプレッドシートからデータを読み込む"""
    try:
        # ttl=0にすることで、読み込みのたびに最新データを取得
        df = conn.read(worksheet=SHEET_NAMES[key], ttl=0)
        # スプレッドシートが空の場合やカラムが不足している場合の処理
        if df.empty:
            return pd.DataFrame(columns=COLUMNS[key])
        return df.fillna("")
    except Exception as e:
        st.error(f"データ読み込みエラー ({key}): {e}")
        return pd.DataFrame(columns=COLUMNS[key])

def save_data(key, df):
    """スプレッドシートを更新する"""
    try:
        conn.update(worksheet=SHEET_NAMES[key], data=df)
        st.cache_data.clear()  # キャッシュをクリアして反映
    except Exception as e:
        st.error(f"データ保存エラー ({key}): {e}")

# --- サイドバー ---
with st.sidebar:
    st.title("💼 就活マネジメント")
    st.markdown("---")
    menu = st.radio(
        "メニューを選択",
        ["① ホーム", "② 企業分析", "③ ESページ", "④ 自己分析", "⑤ リクルート情報メモ"],
        key="main_menu"
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
            df_es['提出期限'] = pd.to_datetime(df_es['提出期限'], errors='coerce').dt.date
            active_es = len(df_es[df_es['提出期限'] >= today])
            st.metric("進行中のES", f"{active_es} 件")
        else: st.metric("進行中のES", "0 件")
    with col3:
        if not df_memo.empty:
            df_memo['日付'] = pd.to_datetime(df_memo['日付'], errors='coerce').dt.date
            upcoming_events = len(df_memo[df_memo['日付'] >= today])
            st.metric("今後の予定", f"{upcoming_events} 件")
        else: st.metric("今後の予定", "0 件")

    st.markdown("---")
    left_col, right_col = st.columns(2)
    with left_col:
        st.subheader("⚠️ 近日の提出期限 (ES)")
        if not df_es.empty:
            df_es['提出期限'] = pd.to_datetime(df_es['提出期限'], errors='coerce').dt.date
            upcoming_es = df_es[df_es['提出期限'] >= today].sort_values('提出期限')
            for _, row in upcoming_es.iterrows():
                if pd.notnull(row['提出期限']):
                    days_left = (row['提出期限'] - today).days
                    alert = "🔴" if days_left <= 3 else "🟡"
                    st.warning(f"{alert} **{row['提出期限']}** | {row['企業名']}")
        else: st.info("予定なし")
        
    with right_col:
        st.subheader("📅 今後のスケジュール")
        if not df_memo.empty:
            df_memo['日付'] = pd.to_datetime(df_memo['日付'], errors='coerce').dt.date
            upcoming_sched = df_memo[df_memo['日付'] >= today].sort_values('日付')
            for _, row in upcoming_sched.iterrows():
                if pd.notnull(row['日付']):
                    st.info(f"🔹 **{row['日付']}** | [{row['カテゴリ']}] {row['タイトル']}")
        else: st.info("予定なし")

# ==========================================
# ② 企業分析
# ==========================================
elif menu == "② 企業分析":
    st.title("🏢 企業分析")
    df_company = load_data("企業分析")
    
    with st.expander("➕ 新規企業の登録"):
        with st.form("company_form", clear_on_submit=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                company = st.text_input("企業名*")
                industry = st.selectbox("業界", ["メーカー", "IT・通信", "商社", "金融", "コンバル", "インフラ", "サービス", "その他"])
            with col_f2:
                status = st.selectbox("選考状況", ["興味あり", "説明会待ち", "ES提出済", "面接(1次)", "面接(2次)", "最終面接", "内定", "お見送り"])
                rank = st.slider("志望度", 1, 5, 3)

            st.markdown("##### 企業分析（SWOT・競合分析）")
            col_sw1, col_sw2 = st.columns(2)
            with col_sw1:
                strength = st.text_area("会社の強み")
                opportunity = st.text_area("機会・チャンス")
            with col_sw2:
                weakness = st.text_area("弱み・課題")
                rival = st.text_area("ライバル・競合他社")

            login_id = st.text_input("マイページID")
            password = st.text_input("パスワード", type="password")

            if st.form_submit_button("登録"):
                if company:
                    new_data = [datetime.now().strftime("%Y-%m-%d"), company, industry, rank, strength, weakness, opportunity, rival, status, login_id, password]
                    new_row = pd.DataFrame([new_data], columns=COLUMNS["企業分析"])
                    df_company = pd.concat([df_company, new_row], ignore_index=True)
                    save_data("企業分析", df_company)
                    st.success(f"{company} を保存しました")
                    st.rerun()
                else:
                    st.error("企業名を入力してください。")
    
    for i, row in df_company.iterrows():
        with st.expander(f"🏢 {row['企業名']} | {row['選考状況']}"):
            st.write(f"志望度: {'⭐' * int(row['志望度'])}")
            c1, c2 = st.columns(2)
            with c1:
                st.info(f"強み: {row['強み']}")
                st.success(f"機会: {row['機会・チャンス']}")
            with c2:
                st.warning(f"弱み: {row['弱み・課題']}")
                st.error(f"競合: {row['ライバル・競合']}")
            
            if st.button("削除", key=f"del_co_{i}"):
                df_company = df_company.drop(i).reset_index(drop=True)
                save_data("企業分析", df_company)
                st.rerun()

# ==========================================
# ③ ESページ
# ==========================================
elif menu == "③ ESページ":
    st.title("📝 ES管理")
    df_es = load_data("ES")
    with st.expander("➕ 新規ES登録"):
        with st.form("es_form", clear_on_submit=True):
            co = st.text_input("企業名*")
            q = st.text_area("設問*")
            dl = st.date_input("提出期限")
            ans = st.text_area("回答案")
            if st.form_submit_button("保存"):
                if co and q:
                    new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), co, q, 400, ans, len(ans), str(dl)]], columns=COLUMNS["ES"])
                    df_es = pd.concat([df_es, new_row], ignore_index=True)
                    save_data("ES", df_es)
                    st.success("ESを保存しました")
                    st.rerun()
    
    for i, row in df_es.iterrows():
        with st.expander(f"{row['企業名']} | {row['提出期限']}"):
            st.write(f"設問: {row['設問']}")
            st.info(row['回答案'])
            if st.button("削除", key=f"del_es_{i}"):
                df_es = df_es.drop(i).reset_index(drop=True)
                save_data("ES", df_es)
                st.rerun()

# ==========================================
# ④ 自己分析
# ==========================================
elif menu == "④ 自己分析":
    st.title("🔍 自己分析")
    df_self = load_data("自己分析")
    with st.expander("➕ 新規追加"):
        with st.form("self_form", clear_on_submit=True):
            cat = st.selectbox("項目", ["強み", "研究内容", "ガクチカ", "志望動機(軸)", "自己PR"])
            epi = st.text_area("内容")
            method = st.text_area("アピール方法")
            if st.form_submit_button("保存"):
                new_row = pd.DataFrame([[datetime.now().strftime("%Y-%m-%d"), cat, epi, method]], columns=COLUMNS["自己分析"])
                df_self = pd.concat([df_self, new_row], ignore_index=True)
                save_data("自己分析", df_self)
                st.success("自己分析を保存しました")
                st.rerun()

    for i, row in df_self.iterrows():
        with st.expander(f"📌 {row['項目']}"):
            st.write(row['具体的なエピソード'])
            if st.button("削除", key=f"del_self_{i}"):
                df_self = df_self.drop(i).reset_index(drop=True)
                save_data("自己分析", df_self)
                st.rerun()

# ==========================================
# ⑤ リクルート情報メモ
# ==========================================
elif menu == "⑤ リクルート情報メモ":
    st.title("📓 メモ")
    df_memo = load_data("メモ")
    with st.expander("➕ 追加"):
        with st.form("memo_form", clear_on_submit=True):
            d = st.date_input("日付")
            c = st.selectbox("カテゴリ", ["面接", "説明会", "その他"])
            t = st.text_input("タイトル*")
            cnt = st.text_area("内容")
            if st.form_submit_button("保存"):
                new_row = pd.DataFrame([[str(d), c, t, "", "", cnt]], columns=COLUMNS["メモ"])
                df_memo = pd.concat([df_memo, new_row], ignore_index=True)
                save_data("メモ", df_memo)
                st.success("メモを保存しました")
                st.rerun()

    for i, row in df_memo.iterrows():
        with st.expander(f"{row['日付']} | {row['タイトル']}"):
            st.write(row['内容'])
            if st.button("削除", key=f"del_memo_{i}"):
                df_memo = df_memo.drop(i).reset_index(drop=True)
                save_data("メモ", df_memo)
                st.rerun()

import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- 設定 ---
filename = "job_hunting_logs.csv"

# ページ設定（スマホで見やすいようにワイドモードに）
st.set_page_config(page_title="就活記録アプリ", layout="centered")

# データ読み込み関数
def load_data():
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=["日付", "企業名", "ステータス", "内容・メモ"])

# データ保存関数
def save_data(df):
    df.to_csv(filename, index=False)

# --- メイン UI ---
st.title("💼 就活記録ログ")

# 1. 入力セクション
with st.expander("新しい記録を追加する", expanded=True):
    with st.form("input_form", clear_on_submit=True):
        date = st.date_input("日付", datetime.now())
        company = st.text_input("企業名")
        status = st.selectbox("ステータス", ["説明会", "ES提出", "面接(1次)", "面接(2次)", "最終面接", "内定", "お見送り"])
        memo = st.text_area("内容・振り返り（面接で聞かれたこと等）")
        
        submitted = st.form_submit_button("保存する")
        
        if submitted:
            if company:
                new_data = pd.DataFrame([[date, company, status, memo]], 
                                        columns=["日付", "企業名", "ステータス", "内容・メモ"])
                df = load_data()
                df = pd.concat([df, new_data], ignore_index=True)
                save_data(df)
                st.success(f"{company} の記録を保存しました！")
            else:
                st.error("企業名を入力してください。")

# --- 2. 履歴表示セクション ---
st.subheader("📊 記録一覧")
df_display = load_data()

if not df_display.empty:
    # 逆順（新しい順）に表示
    st.dataframe(df_display.iloc[::-1], use_container_width=True)
    
    # 簡易統計（スマホで見ると達成感が出ます）
    st.write("---")
    st.write(f"現在の総エントリー数: {len(df_display['企業名'].unique())} 社")
else:
    st.info("まだ記録がありません。上のフォームから入力してください。")

# --- 3. 削除機能（予備） ---
if st.checkbox("管理モード（データの全削除）"):
    if st.button("全データを削除する"):
        if os.path.exists(filename):
            os.remove(filename)
            st.warning("データを削除しました。ページをリロードしてください。")

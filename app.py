import streamlit as st
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────
#  ページ設定
# ─────────────────────────────────────────
st.set_page_config(
    page_title="AI Talent Lab｜AIエージェント実習",
    page_icon="🤖",
    layout="centered",
)

# ─────────────────────────────────────────
#  カスタムCSS
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans JP', sans-serif;
}
.lab-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    color: white;
    padding: 2rem 2rem 1.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    text-align: center;
}
.lab-header h1 { font-size: 1.6rem; font-weight: 700; margin: 0 0 0.3rem 0; }
.lab-header p  { font-size: 0.9rem; opacity: 0.75; margin: 0; }

.section-label {
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #64748b; margin-bottom: 0.5rem;
}
.case-card {
    background: #f8fafc; border-left: 4px solid #3b82f6;
    border-radius: 0 12px 12px 0; padding: 1.2rem 1.5rem; margin-bottom: 1rem;
}
.case-card h3 { font-size: 1rem; font-weight: 700; color: #1e3a5f; margin: 0 0 0.6rem 0; }
.case-card ul { margin: 0; padding-left: 1.2rem; color: #374151; font-size: 0.93rem; line-height: 1.8; }

.step-badge {
    display: inline-block; background: #1e3a5f; color: white;
    font-size: 0.78rem; font-weight: 700; padding: 0.25rem 0.75rem;
    border-radius: 999px; margin-bottom: 0.5rem;
}
.ai-output {
    background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 12px;
    padding: 1.2rem 1.5rem; font-size: 0.93rem; line-height: 1.9;
    color: #0f172a; white-space: pre-wrap; margin-top: 0.5rem;
}
.judgment-box {
    background: #fefce8; border: 1px solid #fde68a;
    border-radius: 12px; padding: 1.2rem 1.5rem; margin-top: 0.5rem;
}
.judgment-box h3 { font-size: 1rem; font-weight: 700; color: #92400e; margin: 0 0 0.4rem 0; }
.divider { border: none; border-top: 1px solid #e2e8f0; margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  OpenAI クライアント
# ─────────────────────────────────────────
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version="2024-02-01",
)

# ─────────────────────────────────────────
#  ケース情報（固定）
# ─────────────────────────────────────────
CASE = (
    "駅前にカフェを出店するかどうか検討している。\n"
    "確定している情報は以下の3点のみ：\n"
    "・駅前で人通りが多い（平日・休日ともに）\n"
    "・競合カフェが近くに2店舗ある\n"
    "・近くに大学があり、学生の利用が見込める\n"
)

SYSTEM_BASE = (
    "あなたはビジネス教育の講師AIです。\n"
    "以下のケースはすでに確定した前提条件です。\n"
    "絶対に追加情報を求めてはいけません。\n"
    "「情報が不足しています」「ケースを教えてください」などと言うことは禁止です。\n"
    "与えられた情報だけを使って、必ず具体的・肯定的に答えてください。\n\n"
    f"【確定ケース】\n{CASE}"
)

PROMPTS = {
    1: "このカフェ出店ケースについて、以下の3つの観点で状況を整理してください。\n"
       "①立地の強み　②競合の状況　③ターゲット顧客\n"
       "各項目を箇条書きで2〜3点ずつ、簡潔にまとめてください。",

    2: "このカフェ出店ケースで『出店するかどうか』を判断するときに、\n"
       "最も重要な判断ポイントを3つ挙げてください。\n"
       "①収益性　②競合対応　③顧客獲得　の観点でそれぞれ1〜2行で説明してください。",

    3: "このカフェ出店ケースで出店判断をするにあたって、\n"
       "現在わかっている情報だけでは足りない情報を5つ挙げてください。\n"
       "各項目を『・〇〇（理由：〜）』の形式で書いてください。",
}

# ─────────────────────────────────────────
#  セッション初期化
# ─────────────────────────────────────────
for key in ["step1_done", "step2_done", "step3_done", "out1", "out2", "out3"]:
    if key not in st.session_state:
        st.session_state[key] = False if key.endswith("done") else ""

# ─────────────────────────────────────────
#  ヘルパー
# ─────────────────────────────────────────
def run_step(step_num: int) -> str:
    res = client.chat.completions.create(
        model="gpt-5.2",
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_BASE},
            {"role": "user",   "content": PROMPTS[step_num]},
        ],
    )
    return res.choices[0].message.content

# ─────────────────────────────────────────
#  ヘッダー
# ─────────────────────────────────────────
st.markdown("""
<div class="lab-header">
    <h1>🤖 AI Talent Lab｜AIエージェント実習</h1>
    <p>AIに思考プロセスを担わせ、ビジネス判断の材料を整理する</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  ケース提示
# ─────────────────────────────────────────
st.markdown('<div class="section-label">📋 今日のケース</div>', unsafe_allow_html=True)
st.markdown("""
<div class="case-card">
    <h3>駅前カフェ出店の検討</h3>
    <ul>
        <li>駅前で<strong>人通りが多い</strong>立地（平日・休日ともに）</li>
        <li>近くに<strong>競合カフェが2店舗</strong>ある</li>
        <li>近くに<strong>大学があり</strong>、学生の利用が見込める</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("**テーマ**：AIを使ってビジネス判断の材料を整理する")
st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────
#  AIエージェント 3ステップ
# ─────────────────────────────────────────
st.markdown('<div class="section-label">🤖 AIエージェント（3ステップ）</div>', unsafe_allow_html=True)
st.caption("① → ② → ③ の順番にボタンを押してください。")

# ── Step 1 ───────────────────────────────
st.markdown('<div class="step-badge">① 状況を整理する</div>', unsafe_allow_html=True)

if st.button("▶ ① 状況を整理する", use_container_width=True):
    with st.spinner("AIが状況を整理しています…"):
        st.session_state.out1 = run_step(1)
        st.session_state.step1_done = True

if st.session_state.step1_done:
    st.markdown(f'<div class="ai-output">{st.session_state.out1}</div>',
                unsafe_allow_html=True)

st.markdown("")

# ── Step 2 ───────────────────────────────
st.markdown('<div class="step-badge">② 判断ポイントを出す</div>', unsafe_allow_html=True)

if not st.session_state.step1_done:
    st.caption("※ まず①を押してください")
else:
    if st.button("▶ ② 判断ポイントを出す", use_container_width=True):
        with st.spinner("AIが判断ポイントを整理しています…"):
            st.session_state.out2 = run_step(2)
            st.session_state.step2_done = True

    if st.session_state.step2_done:
        st.markdown(f'<div class="ai-output">{st.session_state.out2}</div>',
                    unsafe_allow_html=True)

st.markdown("")

# ── Step 3 ───────────────────────────────
st.markdown('<div class="step-badge">③ 足りない情報を出す</div>', unsafe_allow_html=True)

if not st.session_state.step2_done:
    st.caption("※ まず②を押してください")
else:
    if st.button("▶ ③ 足りない情報を出す", use_container_width=True):
        with st.spinner("AIが不足情報を整理しています…"):
            st.session_state.out3 = run_step(3)
            st.session_state.step3_done = True

    if st.session_state.step3_done:
        st.markdown(f'<div class="ai-output">{st.session_state.out3}</div>',
                    unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────
#  あなたの判断（最後に一箇所だけ）
# ─────────────────────────────────────────
st.markdown('<div class="section-label">✍️ あなたの判断</div>', unsafe_allow_html=True)
st.markdown("""
<div class="judgment-box">
    <h3>あなたなら出店する？しない？</h3>
    <p style="font-size:0.88rem; color:#78350f; margin:0;">
    AIの分析を見て、あなたの判断と理由を一言書いてみましょう。
    </p>
</div>
""", unsafe_allow_html=True)

user_judgment = st.text_area(
    label="あなたの判断",
    placeholder="例）出店する。大学生という安定した客層が見込めるから。",
    height=120,
    label_visibility="collapsed",
)

if st.button("📤 判断を送信する", use_container_width=True):
    if user_judgment.strip():
        st.success("✅ 送信しました！AIの分析と自分の考えを比べてみましょう。")
        st.balloons()
    else:
        st.warning("一言でいいので入力してから送信してください。")

# ─────────────────────────────────────────
#  リセット
# ─────────────────────────────────────────
st.markdown('<hr class="divider">', unsafe_allow_html=True)
if st.button("🔄 最初からやり直す", use_container_width=True):
    for key in ["step1_done", "step2_done", "step3_done", "out1", "out2", "out3"]:
        st.session_state[key] = False if key.endswith("done") else ""
    st.rerun()
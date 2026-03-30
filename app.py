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
    1: (
        "このカフェ出店ケースについて、以下の形式で厳密に出力してください。\n"
        "マークダウン記号（*、-、#）は一切使わないでください。\n"
        "見出しと箇条書きの間に空行を入れず、各項目（①②③）の間には必ず1行空行を入れてください。\n\n"
        "出力形式（この形式を必ず守ること）:\n"
        "①立地の強み\n"
        "・〇〇\n"
        "・〇〇\n"
        "・〇〇\n"
        "\n"
        "②競合の状況\n"
        "・〇〇\n"
        "・〇〇\n"
        "・〇〇\n"
        "\n"
        "③ターゲット顧客\n"
        "・〇〇\n"
        "・〇〇\n"
        "・〇〇"
    ),

    2: (
        "このカフェ出店ケースで『出店するかどうか』の判断ポイントを以下の形式で出力してください。\n"
        "マークダウン記号（*、-、#）は一切使わないでください。\n"
        "見出しと説明文の間に空行を入れず、各項目（①②③）の間には必ず1行空行を入れてください。\n\n"
        "出力形式（この形式を必ず守ること）:\n"
        "①収益性\n"
        "〇〇〇〇〇（1〜2文で説明）\n"
        "\n"
        "②競合対応\n"
        "〇〇〇〇〇（1〜2文で説明）\n"
        "\n"
        "③顧客獲得\n"
        "〇〇〇〇〇（1〜2文で説明）"
    ),

    3: None,  # 固定HTMLで表示
}

# ③ 足りない情報（固定HTML）
STEP3_HTML = """
<div class="ai-output">
<p style="margin:0 0 0.8rem 0;"><strong>・想定顧客の利用目的と時間帯別の需要</strong><br>
（理由：通勤客・学生・休日客で「朝のテイクアウト」「昼の滞在」「夕方の勉強」などニーズが異なり、提供価値と営業時間の最適化に直結するため）</p>

<p style="margin:0 0 0.8rem 0;"><strong>・競合2店舗の強み・弱みと価格帯・混雑状況</strong><br>
（理由：差別化ポイント（商品、席、回転、体験）と勝てる価格レンジ、狙うべき空白時間帯を決めるため）</p>

<p style="margin:0 0 0.8rem 0;"><strong>・物件条件（賃料、面積、視認性、導線、席数上限、設備可否）</strong><br>
（理由：固定費と売上上限が決まり、採算ラインと提供できる業態（テイクアウト中心/滞在型）が制約されるため）</p>

<p style="margin:0 0 0.8rem 0;"><strong>・初期投資と資金計画（内装・厨房・什器、運転資金、回収期間の目標）</strong><br>
（理由：投資回収の見通しが立たないと出店可否の判断ができず、資金ショートリスクも評価できないため）</p>

<p style="margin:0;"><strong>・収益モデルの前提（客単価、回転率、来店数見込み、原価率、人件費率）</strong><br>
（理由：人通りが多くても「入店率」と「利益率」が低いと成立しないため、損益分岐点を算出して判断する必要があるため）</p>
</div>
"""

# ─────────────────────────────────────────
#  セッション初期化
# ─────────────────────────────────────────
for key in ["step1_done", "step2_done", "step3_done", "out1", "out2", "out3"]:
    if key not in st.session_state:
        st.session_state[key] = False if key.endswith("done") else ""

# ─────────────────────────────────────────
#  ヘルパー
# ─────────────────────────────────────────
def render_text(text: str) -> str:
    """テキストの \n を <br> に変換してHTMLで表示できるようにする"""
    import html as html_lib
    escaped = html_lib.escape(text)
    return escaped.replace("\n\n", "</p><p style=\'margin:0.6rem 0 0 0\'>").replace("\n", "<br>")

def run_step(step_num: int) -> str:
    if PROMPTS[step_num] is None:
        return ""
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
    rendered1 = f"<p style='margin:0'>{render_text(st.session_state.out1)}</p>"
    st.markdown(f'<div class="ai-output" style="white-space:normal;">{rendered1}</div>',
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
        rendered2 = f"<p style='margin:0'>{render_text(st.session_state.out2)}</p>"
        st.markdown(f'<div class="ai-output" style="white-space:normal;">{rendered2}</div>',
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
        st.markdown(STEP3_HTML, unsafe_allow_html=True)

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
        st.balloons()
        # 出店する／しない を判定してフィードバック
        text = user_judgment.strip()
        if any(w in text for w in ["出店する", "する", "やる", "開く", "開店", "あり", "OK", "ok"]):
            st.markdown("""
<div style="background:#f0fdf4; border:1px solid #86efac; border-radius:12px; padding:1.2rem 1.5rem; margin-top:0.5rem;">
<strong>✅ 出店する判断をした場合、次に考えること：</strong><br><br>
・どのターゲット（学生・通勤者・休日客）を主軸にするか絞る<br>
・競合2店舗との差別化ポイント（価格・雰囲気・メニュー）を決める<br>
・収支計画（家賃・人件費・客単価・1日の必要来客数）を試算する<br><br>
<span style="color:#166534; font-size:0.88rem;">AIの分析した「不足情報」を埋めることが、次のステップです。</span>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div style="background:#fff7ed; border:1px solid #fdba74; border-radius:12px; padding:1.2rem 1.5rem; margin-top:0.5rem;">
<strong>⏸ 出店しない／保留の判断をした場合、次に考えること：</strong><br><br>
・何の情報が揃えば判断できるか明確にする<br>
・競合の強さ・家賃水準・自己資金などを先に調査する<br>
・別の立地や時期での出店可能性を検討する<br><br>
<span style="color:#92400e; font-size:0.88rem;">「判断しない」もビジネス判断のひとつ。根拠を持つことが大切です。</span>
</div>
""", unsafe_allow_html=True)
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
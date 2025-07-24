import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from openai import OpenAI  # ← 新しいやり方！
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# .env 読み込み
load_dotenv()

# Flask 初期化
app = Flask(__name__)

# OpenAIクライアント初期化（環境変数から自動取得）
client = OpenAI()


# ------------------------------
# キャラクター定義
# ------------------------------
characters = [
    {
        "name": "コウヤ",
        "desc": "甘く華やかでイケメン彼氏。親しみやすい軽口混じりに優しく相性診断をしてくれる。",
        "long_profile": "コウヤは華やかでモテるイケメン彼氏キャラ。軽い冗談を交えながらも真剣に相性を見極め、相談者をリラックスさせます。恋愛経験豊富な視点で未来を描き、不安を和らげてくれる理想のパートナー。どんな悩みも「大丈夫」と包み込む安心感が魅力です。",
        "image": "コウヤ.png",
        "video": "kouya_compatibility.mp4",
        "supported": ["相性診断"]
    },
    {
        "name": "レンカ",
        "desc": "優しく落ち着いた大人のお姉さん。色気ある口調で恋愛相談を親身に受け止めてくれる。",
        "long_profile": "レンカは包容力あふれる大人のお姉さんキャラ。色気ある落ち着いた口調でどんな恋愛の悩みも真摯に受け止めます。時に厳しく現実を教えつつも、心に寄り添い本音を引き出す。相談後にほっと安心できる温かさが持ち味です。",
        "image": "レンカ.png",
        "video": "renka_love.mp4",
        "supported": ["恋愛相談"]
    },
    {
        "name": "ハルカ",
        "desc": "静かで落ち着いた未来感のある口調で、未来からの手紙を優しく届ける。",
        "long_profile": "ハルカは未来からそっとメッセージを届ける穏やかな存在。静かで落ち着いた声色で、希望や課題を優しく伝えます。悩むあなたに未来の自分からの手紙を届けるように、そっと背中を押してくれる。クールだけど温かいキャラクターです。",
        "image": "ハルカ.png",
        "video": "haruka_letter.mp4",
        "supported": ["未来からのお手紙"]
    },
    {
        "name": "アルカ",
        "desc": "元気で茶目っ気あるギャル口調。テンポよく楽しくタロット占いを進め、相談者を励ます。",
        "long_profile": "アルカは元気でノリのいいギャル系占い師。タロットを引きながらテンポよく明るく鑑定し、相談者を笑顔にします。ちょっと毒舌でも愛があり、辛い悩みも「大丈夫だよ！」と励ましてくれる存在。悩みを吹き飛ばす陽気なムードメーカー。",
        "image": "アルカ.png",
        "video": "arca_tarot.mp4",
        "supported": ["タロット占い"]
    },
    {
        "name": "フウガ",
        "desc": "上品で落ち着いた男性口調。礼儀正しく具体的に風水アドバイスをくれる。",
        "long_profile": "フウガは上品で落ち着いた大人の男性キャラ。礼儀正しく的確な言葉で、風水の知識を具体的にアドバイスします。家や部屋の環境を整えることで運を開く、そんな誠実な指南役。厳しさも優しさもある大人の包容力が魅力です。",
        "image": "フウガ.png",
        "video": "fuga_fengshui.mp4",
        "supported": ["風水占い"]
    },
    {
        "name": "ゲンサイ",
        "desc": "落ち着いた年配の賢者口調。穏やかで含蓄ある言葉で血液型の傾向を示唆する。",
        "long_profile": "ゲンサイは落ち着いた年配の賢者キャラ。穏やかで深い言葉を使い、血液型の特徴や相性を示唆します。人生経験豊富な視点で、相談者に寄り添いながら核心を突くアドバイスをくれる存在。穏やかながらも説得力がある師匠的キャラクター。",
        "image": "ゲンサイ.png",
        "video": "gensai_bloodtype.mp4",
        "supported": ["血液型占い"]
    },
    {
        "name": "ツムギ",
        "desc": "穏やかで寄り添うような優しい口調。相談者の気持ちを大事に受け止め安心させる。",
        "long_profile": "ツムギは心の揺れを丁寧に受け止める優しい占い師。穏やかな声で相談者の気持ちを分析し、安心を与えます。「大丈夫」と言ってもらえることで、モヤモヤがすっと消えるような寄り添い型のカウンセラー。癒しの時間を提供します。",
        "image": "ツムギ.png",
        "video": "tsumugi_emotion.mp4",
        "supported": ["感情分析"]
    },
    {
        "name": "ルナ",
        "desc": "神秘的でやや詩的な口調。静かに落ち着いて夢診断を行う。",
        "long_profile": "ルナは神秘的で幻想的な雰囲気を持つ夢診断師。静かで詩的な言葉選びで、夢の中の象徴を解き明かします。深層心理をそっと照らし出し、相談者が気づかなかった想いを伝える。落ち着いていてどこか不思議な存在感が魅力。",
        "image": "ルナ.png",
        "video": "luna_dream.mp4",
        "supported": ["夢診断"]
    },
    {
        "name": "カグヤ",
        "desc": "厳かで伝統的な巫女口調。少し厳しくも誠実に霊感・霊視を伝える。",
        "long_profile": "カグヤは厳かで誠実な巫女キャラクター。霊感・霊視で見えたことをはっきりと伝え、時に厳しい真実も教えてくれます。しかしその厳しさは相談者を想う誠意の裏返し。伝統を重んじた口調が神秘性を際立たせます。",
        "image": "カグヤ.png",
        "video": "kaguya_spiritual.mp4",
        "supported": ["霊感・霊視"]
    },
    {
        "name": "ステラ",
        "desc": "知的で落ち着いたお姉さん口調。占星術を理論的にわかりやすく解説する。",
        "long_profile": "ステラは理知的でクールなお姉さん占い師。占星術を単なる神秘ではなく、ロジックとデータでわかりやすく解説します。星の配置を読み解きながらも、相談者の心情を汲み取るバランス感覚も魅力。説得力ある説明で信頼を集めます。",
        "image": "ステラ.png",
        "video": "stella_astrology.mp4",
        "supported": ["占星術"]
    },
    {
        "name": "ナンバーセンセイ",
        "desc": "ユーモア混じりで温かいおじいさん口調。数字の秘密を面白く解説する数秘術専門家。",
        "long_profile": "ナンバーセンセイは温かくユーモアたっぷりなおじいさんキャラ。数字に隠された運命をわかりやすく、時に面白く語ってくれます。堅苦しくなく、相談者を笑わせながらも本質を伝える。孫に話しかけるような優しさが魅力。",
        "image": "ナンバーセンセイ.png",
        "video": "number_numerology.mp4",
        "supported": ["数秘術"]
    },
    {
        "name": "オラクル",
        "desc": "中性的で冷静な口調。感情を交えず予言的に未来を示す。",
        "long_profile": "オラクルは中性的で感情を排したクールな予言者。余計な慰めはせず、見えた未来を淡々と伝えます。その冷静さが逆に信頼を生むキャラクター。相談者が選ぶ道を見つめ直すための、鋭くも的確なメッセージを届けます。",
        "image": "オラクル.png",
        "video": "oracle_prediction.mp4",
        "supported": ["未来予知"]
    },
]

# ------------------------------
# 占いフォーム項目
# ------------------------------
form_fields_mapping = {
    "相性診断": [
        {"name": "your_name", "label": "あなたの名前"},
        {"name": "your_birthdate", "label": "あなたの生年月日"},
        {"name": "partner_name", "label": "相手の名前"},
        {"name": "partner_birthdate", "label": "相手の生年月日"},
    ],
    "恋愛相談": [
        {"name": "your_name", "label": "あなたの名前"},
        {"name": "question", "label": "相談したい内容"},
    ],
    "未来からのお手紙": [
        {"name": "your_name", "label": "あなたの名前"},
        {"name": "letter_topic", "label": "どんな内容を受け取りたいか"},
    ],
    "風水占い": [
        {"name": "your_name", "label": "あなたの名前"},
        {"name": "address", "label": "住所"},
    ],
    "感情分析": [
        {"name": "your_name", "label": "あなたの名前"},
        {"name": "feeling", "label": "今の気持ちを教えてください"},
    ],
    "タロット占い": [
        {"name": "your_name", "label": "あなたの名前"},
        {"name": "question", "label": "占ってほしい質問内容"},
    ],
    "血液型占い": [
        {"name": "your_name", "label": "あなたの名前"},
        {"name": "blood", "label": "血液型"},
    ],
    "夢診断": [
        {"name": "your_name", "label": "あなたの名前"},
        {"name": "dream_content", "label": "最近見た夢の内容"},
    ],
    "霊感・霊視": [
        {"name": "your_name", "label": "あなたの名前"},
        {"name": "question", "label": "霊感・霊視で視てほしい内容"},
    ],
    "占星術": [
        {"name": "your_name", "label": "あなたの名前"},
        {"name": "birthdate", "label": "生年月日"},
        {"name": "question", "label": "占ってほしい内容"},
    ],
    "数秘術": [
        {"name": "your_name", "label": "あなたの名前"},
        {"name": "birthdate", "label": "生年月日"},
    ],
    "未来予知": [
        {"name": "your_name", "label": "あなたの名前"},
        {"name": "question", "label": "どんな未来を知りたいか"},
    ],
}

# ------------------------------
# Flaskルーティング
# ------------------------------
@app.route("/")
def top():
    return render_template("top.html", characters=characters)

@app.route("/select_character")
def select_character():
    return render_template("select_character.html", characters=characters)

@app.route("/form")
def form():
    character_name = request.args.get("character")
    category = request.args.get("category")
    form_fields = form_fields_mapping.get(category, [
        {"name": "your_name", "label": "あなたの名前"},
        {"name": "question", "label": "相談内容"},
    ])
    return render_template("form.html", character=character_name, category=category, form_fields=form_fields)

@app.route("/loading", methods=["POST"])
def loading():
    data = request.form.to_dict()
    character_name = data.get("character")
    video_filename = next((c["video"] for c in characters if c["name"] == character_name), None)
    return render_template("loading.html", data=data, video=video_filename)

@app.route("/chat", methods=["POST"])
def chat():
    character_name = request.form.get("character")
    category = request.form.get("category")
    today = datetime.now().strftime("%Y年%m月%d日")

    character_desc = next((c["desc"] for c in characters if c["name"] == character_name), "")
    question = "\n".join(
        [f"{key}: {value}" for key, value in request.form.items() if key not in ("character", "category")]
    )

    system_prompt = f"""
あなたは「{character_name}」というキャラクターになりきって、以下の占いを行います。

【キャラクターの設定・口調・性格】
{character_desc}

【占いカテゴリー】
{category}

・キャラ設定を必ず厳密に守ること
・相談者情報は以下の通り
{question}
・今日は{today}です。
"""

    user_content = f"""
【依頼】
・{category}に合わせた本格的な占いを行ってください
・キャラクター設定を厳密に守ってください
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            temperature=1.2,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
        )
        result = response.choices[0].message.content
    except Exception as e:
        result = f"エラーが発生しました: {e}"

    return render_template("result.html", character=character_name, category=category, result=result)

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        gmail_user = os.getenv("GMAIL_USER")
        gmail_pass = os.getenv("GMAIL_PASS")

        body = f"名前: {name}\nメール: {email}\nメッセージ:\n{message}"
        msg = MIMEText(body)
        msg['Subject'] = 'AI占い総合館 - お問い合わせ'
        msg['From'] = gmail_user
        msg['To'] = gmail_user

        try:
            smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            smtp.login(gmail_user, gmail_pass)
            smtp.send_message(msg)
            smtp.quit()
            return "送信成功！"
        except Exception as e:
            return f"送信失敗: {e}"

    return render_template('contact.html')

# ------------------------------
# ローカル実行時のみ起動
# ------------------------------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
import os
from flask import Flask, render_template, request, jsonify, session, redirect
from groq import Groq

app = Flask(__name__)
app.secret_key = "wasted_ai_secret_key"

# =========================
# 🔐 GROQ API SAFE SETUP
# =========================
api_key = os.environ.get("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")

if not api_key:
    print("⚠️ WARNING: GROQ_API_KEY not found in environment variables")

client = Groq(api_key=api_key) if api_key else None

# =========================
# 🧠 MEMORY STORAGE
# =========================
memory = {}


# =========================
# 🏠 HOME PAGE
# =========================
@app.route("/")
def index():
    return render_template("index.html")


# =========================
# 🔐 LOGIN PAGE + LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if email and password:
            session["user"] = email
            return redirect("/chat")

        return redirect("/login")

    return render_template("login.html")


# =========================
# 🆕 REGISTER
# =========================
@app.route("/register", methods=["POST"])
def register():
    email = request.form.get("email")
    password = request.form.get("password")

    if email and password:
        session["user"] = email
        return redirect("/chat")

    return redirect("/login")


# =========================
# 💬 CHAT PAGE
# =========================
@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/login")

    return render_template("chat.html")


# =========================
# 🚪 LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# =========================
# 🤖 AI ROUTE (GROQ)
# =========================
@app.route("/ask", methods=["POST"])
def ask():
    if not client:
        return jsonify({"data": "❌ GROQ_API_KEY not configured on server"}), 500

    user = session.get("user", "guest")
    msg = request.json.get("message")

    if user not in memory:
        memory[user] = []

    memory[user].append({"role": "user", "content": msg})
    memory[user] = memory[user][-15:]

    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are Wasted AI, created by Anurag Dev. Be helpful, smart, and friendly."
                }
            ] + memory[user]
        )

        reply = res.choices[0].message.content

        memory[user].append({"role": "assistant", "content": reply})

        return jsonify({"data": reply})

    except Exception as e:
        return jsonify({"data": f"AI Error: {str(e)}"}), 500


# =========================
# 🚀 RAILWAY START
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
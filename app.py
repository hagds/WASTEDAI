from flask import Flask, render_template, request, jsonify, session, redirect
from groq import Groq

app = Flask(__name__)
app.secret_key = "wasted_ai_secret"

client = Groq(api_key="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")

memory = {}

# 🏠 HOME
@app.route("/")
def index():
    return render_template("index.html")


# 🔐 LOGIN PAGE (GET + POST handled)
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


# 🆕 REGISTER (FIXED - NO 404)
@app.route("/register", methods=["POST"])
def register():
    email = request.form.get("email")
    password = request.form.get("password")

    if email and password:
        session["user"] = email
        return redirect("/chat")

    return redirect("/login")


# 💬 CHAT
@app.route("/chat")
def chat():
    if "user" not in session:
        return redirect("/login")

    return render_template("chat.html")


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# 🤖 AI
@app.route("/ask", methods=["POST"])
def ask():
    user = session.get("user", "guest")
    msg = request.json.get("message")

    if user not in memory:
        memory[user] = []

    memory[user].append({"role": "user", "content": msg})
    memory[user] = memory[user][-15:]

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are Wasted AI made by Anurag Dev. Be smart and helpful."
            }
        ] + memory[user]
    )

    reply = res.choices[0].message.content
    memory[user].append({"role": "assistant", "content": reply})

    return jsonify({"data": reply})


if __name__ == "__main__":
    app.run(debug=True)
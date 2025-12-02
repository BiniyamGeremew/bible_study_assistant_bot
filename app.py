from flask import Flask

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Bible Study Assistant Bot is alive on Render!", 200

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

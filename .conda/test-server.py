from flask import Flask, Response
import time

app = Flask(__name__)

@app.get("/")
def hello():
    return Response("Hello Server!", mimetype="text/plain")

if __name__ == "__main__":
    time.sleep(20)
    app.run(host="0.0.0.0", port=2993)
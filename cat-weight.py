from flask import Flask, request
import time

app = Flask(__name__)

@app.route("/push")
def hello_world():
    weight = request.args.get('weight')
    ts = time.time()
    with open("data.txt","a+") as f:
        f.write("%.3f\t%.6f\n"%(ts,weight))

    return "<p>Thank you. Enjoy your food.</p>"

if __name__ == "__main__":
    app.run()

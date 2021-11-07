from flask import Flask, request, Response
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io
from matplotlib.figure import Figure
import time
from datetime import datetime
import pytz
EST = pytz.timezone('US/Eastern')

app = Flask(__name__)

@app.route("/push")
def push_data():
    weight = float(request.args.get('weight'))
    zero = float(request.args.get('zero'))
    ts = time.time()
    with open("/home/rein/cat-weight/data.txt","a+") as f:
        f.write("%.3f\t%.6f\t%.6f\n"%(ts,weight, zero))

    return "<p>Thank you. Enjoy your food.</p>"


@app.route("/plot/circle")
def plot_circle():

    with open("/home/rein/cat-weight/data.txt","r") as f:
        lines = f.readlines()
    ts = []
    weight = []
    for l in lines:
        t, w, z = l.split("\t")
        w = float(w)
        t = float(t)
        if w>5 and w<6:
            ts.append(t)
            weight.append(w)
    bottom = 8
    max_height = 4

    N = 24
    theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
    radii = np.zeros(N)
    width = (2*np.pi) / N
    for t in ts:
        date_time = datetime.fromtimestamp(t).astimezone(EST)
        h = date_time.hour
        i = int(np.floor(h/24.*N))
        radii[i] += 1

    fig, ax = plt.subplots(1,1, subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location("S")
    ax.set_theta_direction(-1)
    ax.set_xticklabels(['midnight', '', '6am', '', 'noon', '', '6pm', ''])
    bars = ax.bar(theta, radii, width=width, bottom=0)

    max_r = np.max(radii)
# Use custom colors and opacity
    for r, bar in zip(radii, bars):
        bar.set_facecolor(plt.cm.viridis(r / max_r))
        bar.set_alpha(0.8)

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route("/list")
def show_list():
    with open("/home/rein/cat-weight/data.txt","r") as f:
        lines = f.readlines()
    ts = []
    weight = []
    for l in lines:
        t, w, z = l.split("\t")
        ts.append(float(t))
        weight.append(float(w))

    html = "<html><body><table style='padding: 9px'>"
    
    for t, w in zip(ts,weight):
        if w>5 and w<6:
            date_time = datetime.fromtimestamp(t).astimezone(EST)
            d = date_time.strftime("%Y/%m/%d %H:%M:%S")
            html += "<tr>"
            html += "<td style='padding: 3px'>"+d+"</td>"
            html += "<td style='padding: 3px'>%.3f kg</td>"%w
            html += "</tr>"
    html += "</table>"
    html += "<br /><br />"
    date_time = datetime.fromtimestamp(t).astimezone(EST)
    d = date_time.strftime("%Y/%m/%d %H:%M:%S")
    html += "Last heartbeat: "+d
    total_seconds = (datetime.now() - datetime.fromtimestamp(t)).total_seconds()
    if total_seconds > 120:
        html += "  (%.1f m ago)"%(total_seconds/60.)
    else:
        html += "  (%.0f s ago)"%(total_seconds)

    html += "</body></html>"
    
    return html

if __name__ == "__main__":
    app.run()

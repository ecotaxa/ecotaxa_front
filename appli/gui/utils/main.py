from flask import render_template
from appli import app, gvg


@app.route("/gui/badge")
def gui_badge():
    color = gvg("color", "secondblue")
    animated = gvg("animated", "")
    text = gvg("text", "")
    return render_template(
        "v2/partials/_badge.html", text=text, color=color, animated=animated
    )

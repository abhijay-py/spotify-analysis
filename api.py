from flask import render_template
import connexion

app = connexion.App(__name__, specification_dir="./")
app.add_api("swagger.yml")

@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    #Posts on http://127.0.0.1:8000/
    #Go to http://127.0.0.1:8000/api/ui for api info
    app.run(host="0.0.0.0", port=8000, debug=True)
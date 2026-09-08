from flask import Flask, request, redirect, render_template, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "resinista_secret_key_123"


# ---------------- DATABASE ----------------

def get_db():
    conn = sqlite3.connect("resinista.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ---------------- LOGIN PAGE ----------------

@app.route("/")
def index():
    return render_template("index.html")


# ---------------- HOME PAGE ----------------

@app.route("/home")
def home():

    if "customer_id" not in session:
        return redirect("/")

    return render_template(
        "home.html",
        customer_name=session["customer_name"]
    )


# ---------------- SIGNUP ----------------

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        conn = get_db()

        try:
            conn.execute(
                "INSERT INTO customers (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect("/")

        except sqlite3.IntegrityError:

            conn.close()

            return """
            <h2>Email already registered!</h2>
            <a href="/signup">Go Back</a>
            """


    return render_template("signup.html")


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template(
            "index.html",
            cart=request.args.get("cart", "")
        )

    email = request.form["email"]
    password = request.form["password"]
    cart = request.form.get("cart", "")

    conn = get_db()
    customer = conn.execute(
        "SELECT * FROM customers WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()

    if customer and check_password_hash(
        customer["password"],
        password
    ):
        session["customer_id"] = customer["id"]
        session["customer_name"] = customer["name"]

        if cart:
            return redirect("/cart?cart=" + cart)

        return redirect("/home")

    return """
    <h2>Invalid Email or Password</h2>
    <a href="/">Try Again</a>
    """


# ---------------- BILL ----------------

@app.route("/bill")
def bill():

    if "customer_id" not in session:
        return redirect("/")

    return render_template(
        "bill.html",
        customer_name=session["customer_name"]
    )


# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# ---------------- START ----------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)

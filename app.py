from flask import Flask, render_template, request, redirect
from database import get_connection

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/members")
def members():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            member_id,
            first_name,
            last_name,
            phone,
            email,
            date_joined,
            status
        FROM Members
        ORDER BY member_id;
    """)

    members = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("members.html", members=members)


@app.route("/add_member", methods=["GET", "POST"])
def add_member():

    if request.method == "POST":

        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        date_joined = request.form["date_joined"]
        status = request.form["status"]

        connection = get_connection()
        cursor = connection.cursor()

        # Find the highest existing ASKU member ID
        cursor.execute("""
            SELECT member_id
            FROM Members
            WHERE member_id LIKE 'ASKU%'
            ORDER BY member_id DESC
            LIMIT 1
        """)

        result = cursor.fetchone()

        if result:
            last_id = result[0]
            number = int(last_id.replace("ASKU/", ""))
            new_member_id = f"ASKU/{number + 1:03d}"
        else:
            new_member_id = "ASKU/001"

        cursor.execute("""
            INSERT INTO Members
            (member_id, first_name, last_name, phone, email, date_joined, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            new_member_id,
            first_name,
            last_name,
            phone,
            email,
            date_joined,
            status
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/members")

    return render_template("add_member.html")

@app.route("/add_payment", methods=["GET", "POST"])
def add_payment():

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        member_id = request.form["member_id"]
        amount = request.form["amount"]
        payment_date = request.form["payment_date"]
        payment_type = request.form["payment_type"]
        status = request.form["status"]

        # Find the highest existing payment ID
        cursor.execute("""
            SELECT payment_id
            FROM Payments
            WHERE payment_id LIKE 'PAY/%'
            ORDER BY payment_id DESC
            LIMIT 1
        """)

        result = cursor.fetchone()

        if result:
            last_id = result[0]
            number = int(last_id.replace("PAY/", ""))
            new_payment_id = f"PAY/{number + 1:03d}"
        else:
            new_payment_id = "PAY/001"

        cursor.execute("""
            INSERT INTO Payments
            (payment_id, member_id, amount, payment_date, payment_type, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            new_payment_id,
            member_id,
            amount,
            payment_date,
            payment_type,
            status
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/payments")

    # Get members for the dropdown
    cursor.execute("""
        SELECT member_id, first_name, last_name
        FROM Members
        ORDER BY member_id
    """)

    members = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("add_payment.html", members=members)

@app.route("/payments")
def payments():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT payment_id, member_id, amount, payment_date, payment_type, status
        FROM payments
        ORDER BY payment_date DESC
    """)

    payments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("payments.html", payments=payments)

@app.route("/events")
def events():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT event_id, event_name, event_date, venue, description, status
        FROM Events
        ORDER BY event_date DESC
    """)

    events = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("events.html", events=events)

@app.route("/add_event", methods=["GET", "POST"])
def add_event():

    if request.method == "POST":

        event_name = request.form["event_name"]
        event_date = request.form["event_date"]
        venue = request.form["venue"]
        description = request.form["description"]
        status = request.form["status"]

        connection = get_connection()
        cursor = connection.cursor()

        # Find the highest existing event ID
        cursor.execute("""
            SELECT event_id
            FROM Events
            WHERE event_id LIKE 'EVT/%'
            ORDER BY event_id DESC
            LIMIT 1
        """)

        result = cursor.fetchone()

        if result:
            last_id = result[0]
            number = int(last_id.replace("EVT/", ""))
            new_event_id = f"EVT/{number + 1:03d}"
        else:
            new_event_id = "EVT/001"

        cursor.execute("""
            INSERT INTO Events
            (event_id, event_name, event_date, venue, description, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            new_event_id,
            event_name,
            event_date,
            venue,
            description,
            status
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/events")

    return render_template("add_event.html")


if __name__ == "__main__":
    app.run(debug=True)
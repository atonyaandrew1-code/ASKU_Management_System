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

@app.route("/attendance")
def attendance():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            a.attendance_id,
            a.member_id,
            m.first_name,
            m.last_name,
            a.activity_id,
            ac.activity_name,
            a.attendance_date,
            a.status
        FROM Attendance a
        JOIN Members m
            ON a.member_id = m.member_id
        JOIN Activities ac
            ON a.activity_id = ac.activity_id
        ORDER BY a.attendance_date DESC
    """)

    attendance_records = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "attendance.html",
        attendance_records=attendance_records
    )

@app.route("/add_attendance", methods=["GET", "POST"])
def add_attendance():

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        member_id = request.form["member_id"]
        activity_id = request.form["activity_id"]
        attendance_date = request.form["attendance_date"]
        status = request.form["status"]

        cursor.execute("""
            SELECT MAX(attendance_id)
            FROM Attendance
        """)

        result = cursor.fetchone()

        if result[0] is not None:
            new_attendance_id = result[0] + 1
        else:
            new_attendance_id = 1

        cursor.execute("""
            INSERT INTO Attendance
            (attendance_id, member_id, activity_id, attendance_date, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            new_attendance_id,
            member_id,
            activity_id,
            attendance_date,
            status
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/attendance")

    cursor.execute("""
        SELECT member_id, first_name, last_name
        FROM Members
        ORDER BY member_id
    """)

    members = cursor.fetchall()

    cursor.execute("""
        SELECT activity_id, activity_name
        FROM Activities
        ORDER BY activity_id
    """)

    activities = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "add_attendance.html",
        members=members,
        activities=activities
    )

@app.route("/activities")
def activities():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT activity_id, activity_name, activity_date, location, created_by
        FROM Activities
        ORDER BY activity_date DESC
    """)

    activities = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("activities.html", activities=activities)

@app.route("/add_activity", methods=["GET", "POST"])
def add_activity():

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        activity_name = request.form["activity_name"]
        activity_date = request.form["activity_date"]
        location = request.form["location"]
        created_by = request.form["created_by"]

        cursor.execute("""
            SELECT MAX(activity_id)
            FROM Activities
        """)

        result = cursor.fetchone()

        if result[0] is not None:
            new_activity_id = result[0] + 1
        else:
            new_activity_id = 1

        cursor.execute("""
            INSERT INTO Activities
            (activity_id, activity_name, activity_date, location, created_by)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            new_activity_id,
            activity_name,
            activity_date,
            location,
            created_by
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/activities")

    cursor.close()
    connection.close()

    return render_template("add_activity.html")

@app.route("/reports")
def reports():

    connection = get_connection()
    cursor = connection.cursor()

    # Total members
    cursor.execute("SELECT COUNT(*) FROM Members")
    total_members = cursor.fetchone()[0]

    # Total payments
    cursor.execute("SELECT COUNT(*) FROM Payments")
    total_payments = cursor.fetchone()[0]

    # Total events
    cursor.execute("SELECT COUNT(*) FROM Events")
    total_events = cursor.fetchone()[0]

    # Total activities
    cursor.execute("SELECT COUNT(*) FROM Activities")
    total_activities = cursor.fetchone()[0]

    # Total attendance records
    cursor.execute("SELECT COUNT(*) FROM Attendance")
    total_attendance = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template(
        "reports.html",
        total_members=total_members,
        total_payments=total_payments,
        total_events=total_events,
        total_activities=total_activities,
        total_attendance=total_attendance
    )

@app.route("/transactions")
def transactions():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            transaction_id,
            member_id,
            transaction_type,
            amount,
            date,
            description,
            "reference_No",
            "Time"
        FROM Transactions
        ORDER BY date DESC, "Time" DESC
    """)

    transactions = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "transactions.html",
        transactions=transactions
    )

@app.route("/add_transaction", methods=["GET", "POST"])
def add_transaction():

    connection = get_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        member_id = request.form["member_id"]
        transaction_type = request.form["transaction_type"]
        amount = request.form["amount"]
        date = request.form["date"]
        description = request.form["description"]
        reference_no = request.form["reference_No"]
        transaction_time = request.form["time"]

        cursor.execute("""
            SELECT MAX(transaction_id)
            FROM Transactions
        """)

        result = cursor.fetchone()

        if result[0] is not None:
            new_transaction_id = result[0] + 1
        else:
            new_transaction_id = 1

        cursor.execute("""
            INSERT INTO Transactions
            (
                transaction_id,
                member_id,
                transaction_type,
                amount,
                date,
                description,
                "reference_No",
                "Time"
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            new_transaction_id,
            member_id,
            transaction_type,
            amount,
            date,
            description,
            reference_no,
            transaction_time
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/transactions")

    cursor.execute("""
        SELECT member_id, first_name, last_name
        FROM Members
        ORDER BY member_id
    """)

    members = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "add_transaction.html",
        members=members
    )
if __name__ == "__main__":
    app.run(debug=True)
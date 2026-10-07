from flask import Flask, render_template, request, redirect, session
from database import get_connection
import bcrypt

app = Flask(__name__)
app.secret_key = "asku-management-secret-key"

@app.before_request
def require_login():

    if request.endpoint not in ["login", "static"]:
        if "user_id" not in session:
            return redirect("/login")

@app.route("/")
def home():

    if "user_id" not in session:
        return redirect("/login")

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

    # Total transactions
    cursor.execute("SELECT COUNT(*) FROM Transactions")
    total_transactions = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template(
        "index.html",
        total_members=total_members,
        total_payments=total_payments,
        total_events=total_events,
        total_activities=total_activities,
        total_attendance=total_attendance,
        total_transactions=total_transactions
    )


@app.route("/members")
def members():

    connection = get_connection()
    cursor = connection.cursor()

    # Check permission:
    # manage_members OR view_members
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name IN ('manage_members', 'view_members')
    """, (session["role_id"],))

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied"

    cursor.execute("""
        SELECT
            member_id,
            first_name,
            last_name,
            phone,
            email,
            date_joined,
            status,
            created_at
        FROM Members
        ORDER BY member_id
    """)

    members = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("members.html", members=members)

@app.route("/edit_member/<path:member_id>", methods=["GET", "POST"])
def edit_member(member_id):

    connection = get_connection()
    cursor = connection.cursor()

    # Check manage_members permission
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name = 'manage_members'
    """, (session["role_id"],))

    has_permission = cursor.fetchone()

    if not has_permission:
        cursor.close()
        connection.close()
        return "Access denied", 403

    if request.method == "POST":

        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        phone = request.form["phone"]
        email = request.form["email"]
        date_joined = request.form["date_joined"]
        status = request.form["status"]

        cursor.execute("""
            UPDATE Members
            SET first_name = %s,
                last_name = %s,
                phone = %s,
                email = %s,
                date_joined = %s,
                status = %s
            WHERE member_id = %s
        """, (
            first_name,
            last_name,
            phone,
            email,
            date_joined,
            status,
            member_id
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/members")

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
        WHERE member_id = %s
    """, (member_id,))

    member = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "edit_member.html",
        member=member
    )


@app.route("/add_member", methods=["GET", "POST"])
def add_member():

    connection = get_connection()
    cursor = connection.cursor()

    # Check manage_members permission
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name = 'manage_members'
    """, (session["role_id"],))

    has_permission = cursor.fetchone()

    if not has_permission:
        cursor.close()
        connection.close()
        return "Access denied", 403

    cursor.close()
    connection.close()


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

    # Check permission
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name = 'manage_finances'
    """, (session["role_id"],))

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied"

    if request.method == "POST":

        payment_id = request.form["payment_id"]
        member_id = request.form["member_id"]
        amount = request.form["amount"]
        payment_date = request.form["payment_date"]
        payment_type = request.form["payment_type"]
        status = request.form["status"]

        cursor.execute("""
            INSERT INTO Payments
            (payment_id, member_id, amount, payment_date, payment_type, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            payment_id,
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

    return render_template(
        "add_payment.html",
        members=members
    )

@app.route("/payments")
def payments():

    connection = get_connection()
    cursor = connection.cursor()

    # Check permission:
    # manage_finances OR view_payments
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name IN ('manage_finances', 'view_payments')
    """, (session["role_id"],))

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied"

    cursor.execute("""
        SELECT
            payment_id,
            member_id,
            amount,
            payment_date,
            payment_type,
            status
        FROM Payments
        ORDER BY payment_date DESC
    """)

    payments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "payments.html",
        payments=payments
    )

@app.route("/events")
def events():

    connection = get_connection()
    cursor = connection.cursor()

    # Check permission:
    # manage_events OR view_events
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name IN ('manage_events', 'view_events')
    """, (session["role_id"],))

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied"

    cursor.execute("""
        SELECT
            event_id,
            event_name,
            event_date,
            venue,
            description,
            status
        FROM Events
        ORDER BY event_date DESC
    """)

    events = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("events.html", events=events)

@app.route("/add_event", methods=["GET", "POST"])
def add_event():

    connection = get_connection()
    cursor = connection.cursor()

    # Check permission
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name = 'manage_events'
    """, (session["role_id"],))

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied"

    if request.method == "POST":

        event_id = request.form["event_id"]
        event_name = request.form["event_name"]
        event_date = request.form["event_date"]
        venue = request.form["venue"]
        description = request.form["description"]
        status = request.form["status"]

        cursor.execute("""
            INSERT INTO Events
            (event_id, event_name, event_date, venue, description, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            event_id,
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

    cursor.close()
    connection.close()

    return render_template("add_event.html")

@app.route("/attendance")
def attendance():

    connection = get_connection()
    cursor = connection.cursor()

    # Check permission:
    # manage_activities OR view_attendance
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name IN ('manage_activities', 'view_attendance')
    """, (session["role_id"],))

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied"

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

    # Check permission
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name = 'manage_activities'
    """, (session["role_id"],))

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied"

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

    # Check permission:
    # manage_activities OR view_activities
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name IN ('manage_activities', 'view_activities')
    """, (session["role_id"],))

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied"

    cursor.execute("""
        SELECT
            activity_id,
            activity_name,
            activity_date,
            location,
            created_by
        FROM Activities
        ORDER BY activity_date DESC
    """)

    activities = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "activities.html",
        activities=activities
    )

@app.route("/add_activity", methods=["GET", "POST"])
def add_activity():

    connection = get_connection()
    cursor = connection.cursor()

    # Check permission
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name = 'manage_activities'
    """, (session["role_id"],))

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied"

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

    # Check permission:
    # manage_finances OR view_transactions
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name IN ('manage_finances', 'view_transactions')
    """, (session["role_id"],))

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied"

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
        ORDER BY date DESC
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

    # Check manage_finances permission
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name = 'manage_finances'
    """, (session["role_id"],))

    has_permission = cursor.fetchone()

    if not has_permission:
        cursor.close()
        connection.close()
        return "Access denied", 403

    if request.method == "POST":

        member_id = request.form["member_id"]
        transaction_type = request.form["transaction_type"]
        amount = request.form["amount"]
        date = request.form["date"]
        description = request.form["description"]
        reference_no = request.form["reference_no"]
        transaction_time = request.form["time"]

        # Generate transaction ID
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

    # Get members for the dropdown
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

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT user_id, username, password_hash, role_id
            FROM users
            WHERE username = %s
              AND is_active = TRUE
        """, (username,))

        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user and bcrypt.checkpw(
            password.encode("utf-8"),
            user[2].encode("utf-8")
        ):
            session["user_id"] = user[0]
            session["username"] = user[1]
            session["role_id"] = user[3]

            return redirect("/")

        return "Invalid username or password"

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

@app.route("/users")
def users():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name = 'manage_users'
    """, (session["role_id"],))

    has_permission = cursor.fetchone()

    cursor.close()
    connection.close()

    if not has_permission:
        return "Access denied", 403

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            u.user_id,
            u.username,
            m.first_name,
            m.last_name,
            r.role_name,
            u.is_active,
            u.date
        FROM users u
        LEFT JOIN members m
            ON u.member_id = m.member_id
        LEFT JOIN roles r
            ON u.role_id = r.role_id
        ORDER BY u.user_id
    """)

    users = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template("users.html", users=users)

@app.route("/add_user", methods=["GET", "POST"])
def add_user():

    connection = get_connection()
    cursor = connection.cursor()

    # Check manage_users permission
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name = 'manage_users'
    """, (session["role_id"],))

    has_permission = cursor.fetchone()

    if not has_permission:
        cursor.close()
        connection.close()
        return "Access denied", 403

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        member_id = request.form["member_id"]
        role_id = request.form["role_id"]

        # Generate user ID
        cursor.execute("""
            SELECT MAX(user_id)
            FROM users
        """)

        result = cursor.fetchone()

        if result[0] is not None:
            new_user_id = result[0] + 1
        else:
            new_user_id = 1

        # Hash password
        password_hash = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode()

        cursor.execute("""
            INSERT INTO users
            (
                user_id,
                username,
                password_hash,
                member_id,
                role_id,
                is_active,
                date
            )
            VALUES (%s, %s, %s, %s, %s, TRUE, CURRENT_DATE)
        """, (
            new_user_id,
            username,
            password_hash,
            member_id,
            role_id
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/users")

    cursor.execute("""
        SELECT member_id, first_name, last_name
        FROM members
        ORDER BY member_id
    """)

    members = cursor.fetchall()

    cursor.execute("""
        SELECT role_id, role_name
        FROM roles
        ORDER BY role_id
    """)

    roles = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "add_user.html",
        members=members,
        roles=roles
    )

@app.route("/edit_user/<int:user_id>", methods=["GET", "POST"])
def edit_user(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    # Check manage_users permission
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name = 'manage_users'
    """, (session["role_id"],))

    has_permission = cursor.fetchone()

    if not has_permission:
        cursor.close()
        connection.close()
        return "Access denied", 403

    if request.method == "POST":

        role_id = request.form["role_id"]

        cursor.execute("""
            UPDATE users
            SET role_id = %s
            WHERE user_id = %s
        """, (role_id, user_id))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/users")

    cursor.execute("""
        SELECT user_id, username, role_id
        FROM users
        WHERE user_id = %s
    """, (user_id,))

    user = cursor.fetchone()

    cursor.execute("""
        SELECT role_id, role_name
        FROM roles
        ORDER BY role_id
    """)

    roles = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "edit_user.html",
        user=user,
        roles=roles
    )

@app.route("/delete_user/<int:user_id>", methods=["POST"])
def delete_user(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    # Check permission
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name = 'manage_users'
    """, (session["role_id"],))

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied"

    # Prevent deleting the currently logged-in user
    if user_id == session["user_id"]:
        cursor.close()
        connection.close()
        return "You cannot delete the account you are currently logged in with."

    # Delete the user
    cursor.execute("""
        DELETE FROM users
        WHERE user_id = %s
    """, (user_id,))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/users")

@app.route("/contributions")
def contributions():

    connection = get_connection()
    cursor = connection.cursor()

    # Check permission:
    # manage_finances OR view_contributions
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name IN ('manage_finances', 'view_contributions')
    """, (session["role_id"],))

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied"

    cursor.execute("""
        SELECT
            c.contribution_id,
            c.member_id,
            m.first_name,
            m.last_name,
            c.amount,
            c.contribution_date,
            c.payment_method,
            c.reference_number
        FROM Contributions c
        JOIN Members m
            ON c.member_id = m.member_id
        ORDER BY c.contribution_date DESC
    """)

    contributions = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "contributions.html",
        contributions=contributions
    )

@app.route("/add_contribution", methods=["GET", "POST"])
def add_contribution():

    connection = get_connection()
    cursor = connection.cursor()

    # Check manage_finances permission
    cursor.execute("""
        SELECT 1
        FROM role_permissions rp
        JOIN permissions p
            ON rp.permission_id = p.permission_id
        WHERE rp.role_id = %s
          AND p.permission_name = 'manage_finances'
    """, (session["role_id"],))

    has_permission = cursor.fetchone()

    if not has_permission:
        cursor.close()
        connection.close()
        return "Access denied", 403

    if request.method == "POST":

        member_id = request.form["member_id"]
        amount = request.form["amount"]
        contribution_date = request.form["contribution_date"]
        payment_method = request.form["payment_method"]
        reference_number = request.form["reference_number"]

        # Generate contribution ID
        cursor.execute("""
            SELECT MAX(contribution_id)
            FROM Contributions
        """)

        result = cursor.fetchone()

        if result[0] is not None:
            new_contribution_id = result[0] + 1
        else:
            new_contribution_id = 1

        cursor.execute("""
            INSERT INTO Contributions
            (
                contribution_id,
                member_id,
                amount,
                contribution_date,
                payment_method,
                reference_number
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            new_contribution_id,
            member_id,
            amount,
            contribution_date,
            payment_method,
            reference_number
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/contributions")

    # Get members for the dropdown
    cursor.execute("""
        SELECT member_id, first_name, last_name
        FROM Members
        ORDER BY member_id
    """)

    members = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "add_contribution.html",
        members=members
    )

if __name__ == "__main__":
    app.run(debug=True)
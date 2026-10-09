from flask import Flask, render_template, request, redirect, url_for, session, Response
from database import get_connection
import bcrypt
import csv
import io
from reportlab.lib.pagesizes import landscape, letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch


app = Flask(__name__)
app.secret_key = "asku-management-secret-key"
app.config["SESSION_PERMANENT"] = False

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

    # Get search and filter values
    search = request.args.get("search", "").strip()
    status = request.args.get("status", "").strip()

    # Build the query
    query = """
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
        WHERE 1=1
    """

    parameters = []

    # Search by member ID, name, phone or email
    if search:
        query += """
            AND (
                member_id ILIKE %s
                OR first_name ILIKE %s
                OR last_name ILIKE %s
                OR phone ILIKE %s
                OR email ILIKE %s
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value,
            search_value,
            search_value
        ])

    # Filter by member status
    if status:
        query += """
            AND status = %s
        """

        parameters.append(status)

    # Sort results
    query += """
        ORDER BY member_id
    """

    cursor.execute(query, parameters)

    members = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "members.html",
        members=members,
        search=search,
        status=status
    )

@app.route("/download_members")
def download_members():

    # Require login
    if "user_id" not in session or "role_id" not in session:
        return redirect("/login")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Check permission to view or manage members
        cursor.execute("""
            SELECT 1
            FROM role_permissions rp
            JOIN permissions p
                ON rp.permission_id = p.permission_id
            WHERE rp.role_id = %s
              AND p.permission_name IN ('manage_members', 'view_members')
        """, (session["role_id"],))

        if not cursor.fetchone():
            return "Access denied", 403

        # Use the same search and status filters as the members page
        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip()

        query = """
            SELECT
                member_id,
                first_name,
                last_name,
                phone,
                email,
                date_joined,
                status
            FROM members
            WHERE 1=1
        """

        parameters = []

        if search:
            query += """
                AND (
                    member_id ILIKE %s
                    OR first_name ILIKE %s
                    OR last_name ILIKE %s
                    OR phone ILIKE %s
                    OR email ILIKE %s
                )
            """

            search_value = f"%{search}%"
            parameters.extend([search_value] * 5)

        if status:
            query += " AND status = %s"
            parameters.append(status)

        query += " ORDER BY member_id"

        cursor.execute(query, parameters)
        members = cursor.fetchall()

        # Create the CSV file in memory
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Member ID",
            "First Name",
            "Last Name",
            "Phone",
            "Email",
            "Date Joined",
            "Status"
        ])

        writer.writerows(members)

        # Return a downloadable CSV file
        csv_content = "\ufeff" + output.getvalue()

        return Response(
            csv_content,
            mimetype="text/csv; charset=utf-8",
            headers={
                "Content-Disposition":
                    "attachment; filename=ASKU_Members.csv"
            }
        )

    finally:
        cursor.close()
        connection.close()


@app.route("/download_members_pdf")
def download_members_pdf():

    # Require login
    if "user_id" not in session or "role_id" not in session:
        return redirect("/login")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Check permission to view or manage members
        cursor.execute("""
            SELECT 1
            FROM role_permissions rp
            JOIN permissions p
                ON rp.permission_id = p.permission_id
            WHERE rp.role_id = %s
              AND p.permission_name IN (
                  'manage_members',
                  'view_members'
              )
        """, (session["role_id"],))

        if not cursor.fetchone():
            return "Access denied", 403

        # Get the same filters used on the Members page
        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip()

        query = """
            SELECT
                member_id,
                first_name,
                last_name,
                phone,
                email,
                date_joined,
                status
            FROM Members
            WHERE 1=1
        """

        parameters = []

        if search:
            query += """
                AND (
                    member_id ILIKE %s
                    OR first_name ILIKE %s
                    OR last_name ILIKE %s
                    OR phone ILIKE %s
                    OR email ILIKE %s
                    OR (first_name || ' ' || last_name) ILIKE %s
                )
            """

            search_value = f"%{search}%"
            parameters.extend([search_value] * 6)

        if status:
            query += " AND status = %s"
            parameters.append(status)

        query += " ORDER BY member_id"

        cursor.execute(query, parameters)
        members = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    # Create PDF in memory
    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=25,
        leftMargin=25,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    elements = [
        Paragraph("ASKU Management System", styles["Title"]),
        Spacer(1, 8),
        Paragraph("Members Report", styles["Heading2"]),
        Spacer(1, 15)
    ]

    table_data = [[
        "Member ID",
        "First Name",
        "Last Name",
        "Phone",
        "Email",
        "Date Joined",
        "Status"
    ]]

    for member in members:
        table_data.append([
            str(value) if value is not None else ""
            for value in member
        ])

    if not members:
        table_data.append([
            "No members found", "", "", "", "", "", ""
        ])

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[85, 85, 85, 100, 165, 100, 75]
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0),
         colors.HexColor("#1f4e78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [
            colors.white,
            colors.HexColor("#f2f2f2")
        ]),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    elements.append(table)
    document.build(elements)

    buffer.seek(0)

    return Response(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=ASKU_Members.pdf"
        }
    )



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

        # Only Admin can change Member ID
        if session.get("role_name", "").lower() == "admin":

            new_member_id = request.form["new_member_id"].strip().upper()

            # Validate Member ID format
            import re

            if not re.fullmatch(r"ASKU/\d{3,}/\d{4}", new_member_id):
                cursor.close()
                connection.close()
                return "Invalid Member ID. Use the format ASKU/001.", 400

            # Check whether the new ID already exists
            if new_member_id != member_id:

                cursor.execute("""
                    SELECT 1
                    FROM Members
                    WHERE member_id = %s
                """, (new_member_id,))

                if cursor.fetchone():
                    cursor.close()
                    connection.close()
                    return "That Member ID already exists.", 400

           # Update member
           # ON UPDATE CASCADE automatically updates
           # related records in tables that reference Members,
           # such as attendance, payments, transactions, and users.
            cursor.execute("""
                UPDATE Members
                SET member_id = %s,
                    first_name = %s,
                    last_name = %s,
                    phone = %s,
                    email = %s,
                    date_joined = %s,
                    status = %s
                WHERE member_id = %s
            """, (
                new_member_id,
                first_name,
                last_name,
                phone,
                email,
                date_joined,
                status,
                member_id
            ))

        else:

            # Non-admin users cannot change Member ID
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

    # Load member
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

        # Find all existing ASKU Member IDs
        cursor.execute("""
            SELECT member_id
            FROM Members
            WHERE member_id LIKE 'ASKU/%'
        """)

        existing_ids = cursor.fetchall()

        # Find the highest member number
        highest_number = 0

        import re

        for row in existing_ids:
            existing_id = row[0]

            match = re.fullmatch(
                r"ASKU/(\d+)(?:/\d{4})?",
                existing_id
            )

            if match:
                number = int(match.group(1))

                if number > highest_number:
                    highest_number = number

        # Generate the next Member ID
        next_number = highest_number + 1

        # Get the joining year from date_joined
        joining_year = date_joined[:4]

        new_member_id = f"ASKU/{next_number}/{joining_year}"

        # Insert the new member
        cursor.execute("""
            INSERT INTO Members
            (
                member_id,
                first_name,
                last_name,
                phone,
                email,
                date_joined,
                status
            )
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

    # Get search and filter values
    search = request.args.get("search", "").strip()
    payment_date = request.args.get("payment_date", "").strip()
    payment_type = request.args.get("payment_type", "").strip()
    status = request.args.get("status", "").strip()

    # Build the query
    query = """
        SELECT
            p.payment_id,
            p.member_id,
            p.amount,
            p.payment_date,
            p.payment_type,
            p.status
        FROM Payments p
        WHERE 1=1
    """

    parameters = []

    # Search by Payment ID or Member ID
    if search:
        query += """
            AND (
                p.payment_id ILIKE %s
                OR p.member_id ILIKE %s
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value
        ])

    # Filter by payment date
    if payment_date:
        query += """
            AND p.payment_date = %s
        """

        parameters.append(payment_date)

    # Filter by payment type
    if payment_type:
        query += """
            AND p.payment_type ILIKE %s
        """

        parameters.append(f"%{payment_type}%")

    # Filter by status
    if status:
        query += """
            AND p.status = %s
        """

        parameters.append(status)

    query += """
        ORDER BY p.payment_date DESC
    """

    cursor.execute(query, parameters)

    payments = cursor.fetchall()

    # Calculate total amount of the filtered results
    total_query = """
        SELECT COALESCE(SUM(p.amount), 0)
        FROM Payments p
        WHERE 1=1
    """

    total_parameters = []

    if search:
        total_query += """
            AND (
                p.payment_id ILIKE %s
                OR p.member_id ILIKE %s
            )
        """

        total_parameters.extend([
            search_value,
            search_value
        ])

    if payment_date:
        total_query += """
            AND p.payment_date = %s
        """

        total_parameters.append(payment_date)

    if payment_type:
        total_query += """
            AND p.payment_type ILIKE %s
        """

        total_parameters.append(f"%{payment_type}%")

    if status:
        total_query += """
            AND p.status = %s
        """

        total_parameters.append(status)

    cursor.execute(total_query, total_parameters)

    total_amount = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template(
        "payments.html",
        payments=payments,
        total_amount=total_amount,
        search=search,
        payment_date=payment_date,
        payment_type=payment_type,
        status=status
    )

@app.route("/download_payments")
def download_payments():

    # Require login
    if "user_id" not in session or "role_id" not in session:
        return redirect("/login")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Check permission to view or manage payments
        cursor.execute("""
            SELECT 1
            FROM role_permissions rp
            JOIN permissions p
                ON rp.permission_id = p.permission_id
            WHERE rp.role_id = %s
              AND p.permission_name IN (
                  'manage_finances',
                  'view_payments'
              )
        """, (session["role_id"],))

        if not cursor.fetchone():
            return "Access denied", 403

        # Get the same filters used by the Payments page
        search = request.args.get("search", "").strip()
        payment_date = request.args.get("payment_date", "").strip()
        payment_type = request.args.get("payment_type", "").strip()
        status = request.args.get("status", "").strip()

        # Build the filtered query
        query = """
            SELECT
                p.payment_id,
                p.member_id,
                p.amount,
                p.payment_date,
                p.payment_type,
                p.status
            FROM Payments p
            WHERE 1=1
        """

        parameters = []

        if search:
            query += """
                AND (
                    CAST(p.payment_id AS TEXT) ILIKE %s
                    OR p.member_id ILIKE %s
                )
            """
            search_value = f"%{search}%"
            parameters.extend([search_value, search_value])

        if payment_date:
            query += " AND p.payment_date = %s"
            parameters.append(payment_date)

        if payment_type:
            query += " AND p.payment_type ILIKE %s"
            parameters.append(f"%{payment_type}%")

        if status:
            query += " AND p.status = %s"
            parameters.append(status)

        query += " ORDER BY p.payment_date DESC"

        cursor.execute(query, parameters)
        payments = cursor.fetchall()

        # Create CSV file in memory
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow([
            "Payment ID",
            "Member ID",
            "Amount",
            "Payment Date",
            "Payment Type",
            "Status"
        ])

        writer.writerows(payments)

        csv_content = "\ufeff" + output.getvalue()

        return Response(
            csv_content,
            mimetype="text/csv; charset=utf-8",
            headers={
                "Content-Disposition":
                    "attachment; filename=ASKU_Payments.csv"
            }
        )

    finally:
        cursor.close()
        connection.close()

@app.route("/download_payments_pdf")
def download_payments_pdf():

    if "user_id" not in session or "role_id" not in session:
        return redirect("/login")

    connection = get_connection()
    cursor = connection.cursor()

    try:
        # Check permissions
        cursor.execute("""
            SELECT 1
            FROM role_permissions rp
            JOIN permissions p
                ON rp.permission_id = p.permission_id
            WHERE rp.role_id = %s
              AND p.permission_name IN (
                  'manage_finances',
                  'view_payments'
              )
        """, (session["role_id"],))

        if not cursor.fetchone():
            return "Access denied", 403

        # Read the same filters as the Payments page
        search = request.args.get("search", "").strip()
        payment_date = request.args.get("payment_date", "").strip()
        payment_type = request.args.get("payment_type", "").strip()
        status = request.args.get("status", "").strip()

        query = """
            SELECT
                p.payment_id,
                p.member_id,
                p.amount,
                p.payment_date,
                p.payment_type,
                p.status
            FROM Payments p
            WHERE 1=1
        """

        parameters = []

        if search:
            query += """
                AND (
                    CAST(p.payment_id AS TEXT) ILIKE %s
                    OR p.member_id ILIKE %s
                )
            """
            value = f"%{search}%"
            parameters.extend([value, value])

        if payment_date:
            query += " AND p.payment_date = %s"
            parameters.append(payment_date)

        if payment_type:
            query += " AND p.payment_type ILIKE %s"
            parameters.append(f"%{payment_type}%")

        if status:
            query += " AND p.status = %s"
            parameters.append(status)

        query += " ORDER BY p.payment_date DESC"

        cursor.execute(query, parameters)
        payments = cursor.fetchall()

    finally:
        cursor.close()
        connection.close()

    # Create the PDF in memory
    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    elements = [
        Paragraph("ASKU Management System", styles["Title"]),
        Spacer(1, 8),
        Paragraph("Payments Report", styles["Heading2"]),
        Spacer(1, 15)
    ]

    table_data = [[
        "Payment ID",
        "Member ID",
        "Amount (KSh)",
        "Payment Date",
        "Payment Type",
        "Status"
    ]]

    for payment in payments:
        table_data.append([
            str(value) if value is not None else ""
            for value in payment
        ])

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[90, 90, 90, 100, 120, 90]
    )

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f4e78")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#f2f2f2")]),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))

    elements.append(table)

    document.build(elements)

    buffer.seek(0)

    return Response(
        buffer.getvalue(),
        mimetype="application/pdf",
        headers={
            "Content-Disposition":
                "attachment; filename=ASKU_Payments.pdf"
        }
    )

@app.route("/edit_payment/<path:payment_id>", methods=["GET", "POST"])
def edit_payment(payment_id):

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

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied", 403

    if request.method == "POST":

        member_id = request.form["member_id"]
        amount = request.form["amount"]
        payment_date = request.form["payment_date"]
        payment_type = request.form["payment_type"]
        status = request.form["status"]

        cursor.execute("""
            UPDATE Payments
            SET member_id = %s,
                amount = %s,
                payment_date = %s,
                payment_type = %s,
                status = %s
            WHERE payment_id = %s
        """, (
            member_id,
            amount,
            payment_date,
            payment_type,
            status,
            payment_id
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/payments")

    # Get the payment
    cursor.execute("""
        SELECT
            payment_id,
            member_id,
            amount,
            payment_date,
            payment_type,
            status
        FROM Payments
        WHERE payment_id = %s
    """, (payment_id,))

    payment = cursor.fetchone()

    # Get members for dropdown
    cursor.execute("""
        SELECT
            member_id,
            first_name,
            last_name
        FROM Members
        ORDER BY member_id
    """)

    members = cursor.fetchall()

    cursor.close()
    connection.close()

    if not payment:
        return "Payment not found", 404

    return render_template(
        "edit_payment.html",
        payment=payment,
        members=members
    )

@app.route("/delete_payment/<path:payment_id>", methods=["POST"])
def delete_payment(payment_id):

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

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied", 403

    # Delete the payment
    cursor.execute("""
        DELETE FROM Payments
        WHERE payment_id = %s
    """, (payment_id,))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/payments")



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

    # Get search and filter values
    search = request.args.get("search", "").strip()
    attendance_date = request.args.get("attendance_date", "").strip()
    status = request.args.get("status", "").strip()

    # Build the query
    query = """
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
        WHERE 1=1
    """

    parameters = []

    # Search by member ID, member name or activity name
    if search:
        query += """
            AND (
                a.member_id ILIKE %s
                OR m.first_name ILIKE %s
                OR m.last_name ILIKE %s
                OR ac.activity_name ILIKE %s
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value,
            search_value
        ])

    # Filter by attendance date
    if attendance_date:
        query += """
            AND a.attendance_date = %s
        """

        parameters.append(attendance_date)

    # Filter by attendance status
    if status:
        query += """
            AND a.status = %s
        """

        parameters.append(status)

    query += """
        ORDER BY a.attendance_date DESC
    """

    cursor.execute(query, parameters)

    attendance_records = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "attendance.html",
        attendance_records=attendance_records,
        search=search,
        attendance_date=attendance_date,
        status=status
    )

@app.route("/edit_attendance/<int:attendance_id>", methods=["GET", "POST"])
def edit_attendance(attendance_id):

    connection = get_connection()
    cursor = connection.cursor()

    # Check manage_activities permission
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
        return "Access denied", 403

    if request.method == "POST":

        member_id = request.form["member_id"]
        activity_id = request.form["activity_id"]
        attendance_date = request.form["attendance_date"]
        status = request.form["status"]

        cursor.execute("""
            UPDATE Attendance
            SET member_id = %s,
                activity_id = %s,
                attendance_date = %s,
                status = %s
            WHERE attendance_id = %s
        """, (
            member_id,
            activity_id,
            attendance_date,
            status,
            attendance_id
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/attendance")

    # Get the attendance record
    cursor.execute("""
        SELECT
            attendance_id,
            member_id,
            activity_id,
            attendance_date,
            status
        FROM Attendance
        WHERE attendance_id = %s
    """, (attendance_id,))

    attendance = cursor.fetchone()

    # Get members for dropdown
    cursor.execute("""
        SELECT
            member_id,
            first_name,
            last_name
        FROM Members
        ORDER BY member_id
    """)

    members = cursor.fetchall()

    # Get activities for dropdown
    cursor.execute("""
        SELECT
            activity_id,
            activity_name,
            activity_date
        FROM Activities
        ORDER BY activity_date DESC
    """)

    activities = cursor.fetchall()

    cursor.close()
    connection.close()

    if not attendance:
        return "Attendance record not found", 404

    return render_template(
        "edit_attendance.html",
        attendance=attendance,
        members=members,
        activities=activities
    )

@app.route("/delete_attendance/<int:attendance_id>", methods=["POST"])
def delete_attendance(attendance_id):

    connection = get_connection()
    cursor = connection.cursor()

    # Check manage_activities permission
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
        return "Access denied", 403

    # Delete the attendance record
    cursor.execute("""
        DELETE FROM Attendance
        WHERE attendance_id = %s
    """, (attendance_id,))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/attendance")



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

@app.route("/edit_activity/<int:activity_id>", methods=["GET", "POST"])
def edit_activity(activity_id):

    connection = get_connection()
    cursor = connection.cursor()

    # Check manage_activities permission
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
        return "Access denied", 403

    if request.method == "POST":

        activity_name = request.form["activity_name"]
        activity_date = request.form["activity_date"]
        location = request.form["location"]
        created_by = request.form["created_by"]

        cursor.execute("""
            UPDATE Activities
            SET activity_name = %s,
                activity_date = %s,
                location = %s,
                created_by = %s
            WHERE activity_id = %s
        """, (
            activity_name,
            activity_date,
            location,
            created_by,
            activity_id
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/activities")

    # Load existing activity
    cursor.execute("""
        SELECT
            activity_id,
            activity_name,
            activity_date,
            location,
            created_by
        FROM Activities
        WHERE activity_id = %s
    """, (activity_id,))

    activity = cursor.fetchone()

    cursor.close()
    connection.close()

    if not activity:
        return "Activity not found", 404

    return render_template(
        "edit_activity.html",
        activity=activity
    )

@app.route("/delete_activity/<int:activity_id>", methods=["POST"])
def delete_activity(activity_id):

    connection = get_connection()
    cursor = connection.cursor()

    # Check manage_activities permission
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
        return "Access denied", 403

    # Check whether the activity has attendance records
    cursor.execute("""
        SELECT COUNT(*)
        FROM Attendance
        WHERE activity_id = %s
    """, (activity_id,))

    attendance_count = cursor.fetchone()[0]

    if attendance_count > 0:
        cursor.close()
        connection.close()

        return (
            f"Cannot delete this activity because it has "
            f"{attendance_count} attendance record(s) attached to it. "
            f"Delete or reassign the attendance records first."
        ), 400

    # Delete the activity
    cursor.execute("""
        DELETE FROM Activities
        WHERE activity_id = %s
    """, (activity_id,))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/activities")


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
        return "Access denied", 403

    # Get search and filter values
    search = request.args.get("search", "").strip()
    transaction_date = request.args.get("transaction_date", "").strip()
    transaction_type = request.args.get("transaction_type", "").strip()

    # Build the query
    query = """
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
        WHERE 1=1
    """

    parameters = []

    # Search by Member ID, Transaction Type or Reference Number
    if search:
        query += """
            AND (
                member_id ILIKE %s
                OR transaction_type ILIKE %s
                OR "reference_No" ILIKE %s
            )
        """

        search_value = f"%{search}%"

        parameters.extend([
            search_value,
            search_value,
            search_value
        ])

    # Filter by transaction date
    if transaction_date:
        query += """
            AND date = %s
        """

        parameters.append(transaction_date)

    # Filter by transaction type
    if transaction_type:
        query += """
            AND transaction_type = %s
        """

        parameters.append(transaction_type)

    query += """
        ORDER BY date DESC
    """

    cursor.execute(query, parameters)

    transactions = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "transactions.html",
        transactions=transactions,
        search=search,
        transaction_date=transaction_date,
        transaction_type=transaction_type
    )


@app.route("/edit_transaction/<int:transaction_id>", methods=["GET", "POST"])
def edit_transaction(transaction_id):

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

    permission = cursor.fetchone()

    if not permission:
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
        time = request.form["time"]

        cursor.execute("""
            UPDATE Transactions
            SET member_id = %s,
                transaction_type = %s,
                amount = %s,
                date = %s,
                description = %s,
                "reference_No" = %s,
                "Time" = %s
            WHERE transaction_id = %s
        """, (
            member_id,
            transaction_type,
            amount,
            date,
            description,
            reference_no,
            time,
            transaction_id
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect("/transactions")

    # Load existing transaction
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
        WHERE transaction_id = %s
    """, (transaction_id,))

    transaction = cursor.fetchone()

    # Load members for the dropdown
    cursor.execute("""
        SELECT member_id, first_name, last_name
        FROM Members
        ORDER BY member_id
    """)

    members = cursor.fetchall()

    cursor.close()
    connection.close()

    if not transaction:
        return "Transaction not found", 404

    return render_template(
        "edit_transaction.html",
        transaction=transaction,
        members=members
    )

@app.route("/delete_transaction/<int:transaction_id>", methods=["POST"])
def delete_transaction(transaction_id):

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

    permission = cursor.fetchone()

    if not permission:
        cursor.close()
        connection.close()
        return "Access denied", 403

    # Delete the transaction
    cursor.execute("""
        DELETE FROM Transactions
        WHERE transaction_id = %s
    """, (transaction_id,))

    connection.commit()

    cursor.close()
    connection.close()

    return redirect("/transactions")


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
            SELECT
                u.user_id,
                u.username,
                u.password_hash,
                u.role_id,
                r.role_name
            FROM users u
            JOIN roles r
                ON u.role_id = r.role_id
            WHERE u.username = %s
              AND u.is_active = TRUE
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
            session["role_name"] = user[4]

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



if __name__ == "__main__":
    app.run(debug=True)
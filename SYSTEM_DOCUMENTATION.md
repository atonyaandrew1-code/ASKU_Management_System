# ASKU MANAGEMENT SYSTEM

## Complete System Documentation

**Project Name:** ASKU Management System
**Organization:** Actuarial Students' Association of Kenyatta University (ASKU)
**Application Type:** Web-Based Management System
**Backend:** Python and Flask
**Database:** PostgreSQL
**Interface:** HTML, CSS, and responsive web pages
**Repository:** https://github.com/atonyaandrew1-code/ASKU_Management_System

---

## Table of Contents

1. System Overview
2. Project Objectives
3. Technologies Used
4. System Architecture
5. System Modules
6. User Roles and Permissions
7. Database Design
8. Main System Features
9. Security and Access Control
10. System Workflows
11. Testing and Verification
12. Installation and Setup
13. Database Backup and Recovery
14. Maintenance and Future Improvements
15. Conclusion

---

## 1. System Overview

The ASKU Management System is a web-based application designed to support the management of members and administrative activities within the Actuarial Students' Association of Kenyatta University.

The system provides a centralized platform for storing and managing member information, recording attendance, organizing activities, tracking payments and financial transactions, managing user accounts, and accessing reports.

The application uses Python with the Flask framework for its backend logic and PostgreSQL for persistent data storage. Its web interface allows authorized users to access the system through a browser.

The system is intended to improve record accuracy, accountability, information accessibility, and continuity of operations when student leaders or administrators change.

## 2. Project Objectives

The main objectives of the ASKU Management System are:

* To maintain a centralized database of association members.
* To simplify the registration and management of members.
* To record attendance at association activities.
* To manage association activities and related information.
* To record and manage member payments.
* To maintain financial transaction records.
* To provide controlled access based on user roles and permissions.
* To support administrative reporting and review.
* To reduce dependence on scattered spreadsheets and manual records.
* To preserve organizational information for future association leaders.
* To improve accountability and the traceability of administrative operations.

## 3. Technologies Used

| Technology      | Purpose                                          |
| --------------- | ------------------------------------------------ |
| Python          | Main programming language                        |
| Flask           | Web application framework                        |
| PostgreSQL      | Relational database management system            |
| HTML            | Web page structure                               |
| CSS             | Web page styling and responsive layouts          |
| psycopg2-binary | Connection between Python and PostgreSQL         |
| python-dotenv   | Loading configuration from environment variables |
| bcrypt          | Password hashing                                 |
| Git             | Version control                                  |
| GitHub          | Remote source-code repository                    |
| Render          | Hosting and deployment, where configured         |

The project uses a `requirements.txt` file to identify the Python packages required by the application.

## 4. System Architecture

The system follows a web application architecture consisting of three main layers.

### 4.1 Presentation Layer

This layer contains the HTML templates and CSS used to display the application in a web browser.

It provides pages and forms for viewing records, entering information, searching, filtering, and performing authorized administrative operations.

### 4.2 Application Layer

This layer is implemented using Python and Flask.

It handles incoming requests, user authentication, session management, permission checks, form submissions, database operations, and page navigation.

### 4.3 Database Layer

This layer uses PostgreSQL to store application records, including members, activities, attendance, payments, transactions, users, roles, and permissions.

The database supports persistent storage and relationships between related records.

### 4.4 General Request Flow

1. A user opens the application in a browser.
2. The user logs in where authentication is required.
3. Flask receives the requested page or form submission.
4. The application checks the relevant authentication and authorization requirements.
5. Authorized database operations are performed.
6. The application returns a response to the browser.

## 5. System Modules

### 5.1 Dashboard

The dashboard serves as the main navigation page after successful login.

It provides access to the system modules available to the authenticated user, depending on the application's role and permission configuration.

The dashboard also incorporates the ASKU identity and navigation links to help users move between sections.

### 5.2 Member Management

The member management module stores and maintains information about association members.

Key functions include:

* Adding new members.
* Viewing member records.
* Editing member information.
* Searching for members.
* Filtering member records by status.
* Maintaining unique member identification numbers.
* Restricting member management operations according to permissions.

Member records may contain the member ID, first name, last name, phone number, email address, date joined, membership status, and record creation timestamp.

The current member ID format is designed to include the association prefix, a sequential number, and the joining year, for example `ASKU/001/2026`.

The exact format and numbering sequence should remain consistent with the implementation currently deployed.

### 5.3 Activities Management

The activities module supports the recording and management of association activities.

Key functions include:

* Adding activities.
* Viewing activity records.
* Editing activity details.
* Deleting activities when permitted and when database relationships allow it.
* Recording activity names, dates, locations, and creator information.

Activities provide a reference point for attendance records.

The system should prevent the deletion of an activity when associated attendance records would cause a database integrity problem.

### 5.4 Attendance Management

The attendance module records member participation in association activities.

Key functions include:

* Recording attendance.
* Viewing attendance records.
* Editing attendance information.
* Deleting attendance records when authorized.
* Associating attendance records with members and activities.

Attendance records help the association monitor participation and maintain historical records of activities.

### 5.5 Payments Management

The payments module records payments associated with members.

Depending on the fields implemented, payment records include:

* Payment ID.
* Member ID.
* Amount.
* Payment date.
* Payment type.
* Payment status.

Key functions include adding, viewing, searching, filtering, editing, and deleting payment records according to the user's permissions.

Payment records support financial administration and reporting.

### 5.6 Transactions Management

The transactions module stores financial transaction records.

Transaction information may include:

* Transaction ID.
* Member ID, where applicable.
* Transaction type.
* Amount.
* Transaction date.
* Description.
* Reference number.
* Transaction timestamp.

The module provides a record of financial movements and supports accountability by preserving relevant transaction details.

### 5.7 User Management

The user management module controls the accounts used to access the application.

Key functions include:

* Creating user accounts.
* Assigning roles.
* Managing account information.
* Activating or deactivating accounts, where supported.
* Restricting user administration to authorized personnel.

User accounts are associated with roles and, where applicable, member records.

Passwords should be stored as secure password hashes rather than plain text.

### 5.8 Authentication and Session Management

The authentication module controls access to protected areas of the system.

It supports login and logout operations and uses session management to maintain authenticated user state.

Protected routes should reject requests from unauthenticated users. Authenticated users should also be prevented from performing operations for which they lack permission.

### 5.9 Reports

The reports module provides access to supported summaries of association records.

The information available depends on the report queries and templates implemented in the application.

Reports should be accessible only to users whose assigned permissions allow them to view them.

**Note:** Contributions and Events are not included as active modules in the current documented system scope.

## 6. User Roles and Permissions

The system uses role-based access control. A user's role determines which operations the user is allowed to perform.

The configured roles are:

| Role        | General Responsibility                                                               |
| ----------- | ------------------------------------------------------------------------------------ |
| Admin       | System administration and authorized management operations                           |
| Chairperson | Association leadership and permitted member/activity management                      |
| Treasurer   | Financial administration and authorized financial reporting                          |
| Secretary   | Member administration and permitted reporting                                        |
| Member      | Viewing permitted member, activity, attendance, payment, and transaction information |

### 6.1 Permission Types

The system includes permission identifiers such as:

* `manage_members` — manage member records.
* `manage_activities` — manage activities and associated operations assigned to this permission.
* `view_reports` — access authorized reports.
* `manage_users` — manage application user accounts.
* `manage_finances` — manage authorized payment and financial transaction operations.
* `view_members` — view member records.
* `view_attendance` — view attendance records.
* `view_transactions` — view transaction records.
* `view_payments` — view payment records.
* `view_activities` — view activity records.

The permissions assigned to each role are maintained through the `roles`, `permissions`, and `role_permissions` database tables.

Actual access must be determined by the permissions configured in the running application. The role descriptions above are general summaries and do not replace the application's permission checks.

## 7. Database Design

The application uses PostgreSQL as its relational database.

The intended current database tables are listed below.

| Table              | Purpose                                          |
| ------------------ | ------------------------------------------------ |
| `members`          | Stores association member information            |
| `activities`       | Stores association activity information          |
| `attendance`       | Records member attendance at activities          |
| `payments`         | Stores payment records                           |
| `transactions`     | Stores financial transaction records             |
| `users`            | Stores application user accounts                 |
| `roles`            | Defines application roles                        |
| `permissions`      | Defines individual system permissions            |
| `role_permissions` | Associates roles with their permitted operations |

### 7.1 Relationships

The database uses relationships to connect records that belong together.

Examples include:

* Attendance records reference members and activities.
* Payment records reference members where the payment schema defines that relationship.
* User accounts may reference member records.
* User accounts reference assigned roles.
* Role-permission associations connect roles to individual permissions.

Foreign keys and other database constraints help preserve data integrity. The exact behavior when a referenced record is updated or deleted depends on the constraints configured for that relationship.

### 7.2 Member Identification

Member IDs are used to identify members across the system.

The current intended format is:

`ASKU/001/2026`

In this example:

* `ASKU` identifies the association.
* `001` represents the sequential member number.
* `2026` represents the joining year.

The application should validate member IDs and prevent duplicate identifiers.

### 7.3 Database Configuration

Database connection settings are stored in environment variables rather than being written directly into application code.

The project uses a `.env` file for local configuration. This file should remain private and should not be committed to a public repository.

The expected configuration variables are:

* `DB_HOST`
* `DB_NAME`
* `DB_USER`
* `DB_PASSWORD`
* `DB_PORT`

The actual values depend on the local or hosted PostgreSQL environment.

## 8. Main System Features

The system includes the following general features, subject to the functionality currently implemented and deployed:

### 8.1 Record Management

Authorized users can create, view, update, and, where permitted, delete records in supported modules.

### 8.2 Search and Filtering

Search and filtering features help users locate relevant records without manually reviewing the entire database.

The member and payment pages support search and filtering based on implemented fields.

### 8.3 Responsive Interface

The interface is designed to be usable on desktop and mobile screens. Responsive styling helps pages, navigation links, forms, and buttons adapt to different screen sizes.

### 8.4 Association Branding

The interface includes the ASKU logo and associated visual branding where configured.

### 8.5 Financial Record Keeping

The payments and transactions modules provide structured records for financial administration.

### 8.6 Role-Based Access

The application uses roles and permissions to limit access to protected pages and management operations.

### 8.7 Persistent Storage

Records are stored in PostgreSQL, allowing data to remain available between application sessions.

## 9. Security and Access Control

Security is an important part of the ASKU Management System because the application handles member information, account credentials, and financial records.

The following security measures should be maintained.

### 9.1 Authentication

Users should log in before accessing protected areas of the application.

### 9.2 Authorization

Routes and management operations should check the authenticated user's permissions before allowing sensitive actions.

### 9.3 Password Protection

Passwords should be hashed using the application's password-hashing implementation. Plain-text passwords should never be stored in the database.

### 9.4 Environment Variables

Database credentials and other private configuration values should be stored in environment variables.

The `.env` file must not be uploaded to a public GitHub repository.

### 9.5 Session Protection

The application should protect authenticated sessions and prevent unauthenticated access to protected routes.

### 9.6 Data Integrity

Database constraints should be used to prevent invalid references and preserve consistency between related records.

### 9.7 Production Configuration

Before public production use, the application should be configured with secure session settings, a strong secret key, HTTPS, appropriate database credentials, and debug mode disabled.

The Flask development server and `debug=True` are intended for local development, not production deployment.

## 10. System Workflows

### 10.1 User Login

1. The user opens the application.
2. The user enters login credentials.
3. The application validates the credentials.
4. If authentication succeeds, the application establishes the user's authenticated session.
5. The user is directed to the appropriate page.
6. If authentication fails, access is denied and an appropriate message is displayed.

### 10.2 Adding a Member

1. An authorized user opens the member management page.
2. The user selects the option to add a member.
3. The user enters the required member information.
4. The application validates the submitted data.
5. The application generates or validates the member ID according to the implemented rules.
6. The record is saved to PostgreSQL.
7. The updated member list is displayed.

### 10.3 Recording Attendance

1. An authorized user opens attendance management.
2. The user selects the relevant activity and member.
3. The attendance details are submitted.
4. The application validates the information.
5. The attendance record is saved.
6. The record becomes available for authorized viewing and reporting.

### 10.4 Recording a Payment

1. An authorized user opens payment management.
2. The user enters the payment information.
3. The application validates the required fields.
4. The payment record is saved to PostgreSQL.
5. The updated payment information becomes available to authorized users.

### 10.5 Recording a Transaction

1. An authorized user opens transaction management.
2. The user enters the transaction details.
3. The application validates the submitted information.
4. The transaction is saved to the database.
5. Authorized users can view the transaction record.

### 10.6 Managing User Access

1. An authorized administrator opens user management.
2. The administrator creates or updates an account.
3. A role is assigned to the account.
4. The application's permission configuration determines which operations the user may perform.
5. The user accesses only the functionality permitted by the application's authorization rules.

## 11. Testing and Verification

System testing is necessary to confirm that the application behaves as intended.

The following areas have previously been reported as tested during development. They should be retested after significant code changes or deployment updates.

| Test Area              | Purpose                                                              |
| ---------------------- | -------------------------------------------------------------------- |
| Login and logout       | Confirm authentication and session termination                       |
| Session protection     | Confirm protected pages require authentication                       |
| Role testing           | Confirm users receive access appropriate to their roles              |
| Unauthorized access    | Confirm restricted operations are denied                             |
| Member management      | Test member creation, viewing, editing, and deletion where permitted |
| Activities             | Test activity management operations                                  |
| Attendance             | Test attendance recording and management                             |
| Payments               | Test payment management and filtering                                |
| Transactions           | Test transaction management                                          |
| User management        | Test user account and role administration                            |
| Database relationships | Confirm related records remain consistent                            |
| Responsive layout      | Check usability on desktop and mobile screens                        |
| Deployment             | Confirm the hosted application connects to the correct database      |

A feature should be described as fully tested only after its current implementation has been verified.

Following changes to routes, templates, database schemas, or permissions, regression testing should be performed to identify problems introduced by the changes.

## 12. Installation and Setup

The following procedure describes the general local setup. It assumes Python and PostgreSQL are installed and accessible.

### 12.1 Project Directory

The local project directory is:

`C:\ANDREW\ASKU_Management_System`

### 12.2 Install Dependencies

Open a terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

The requirements file should contain the dependencies used by the project, including Flask, psycopg2-binary, python-dotenv, and bcrypt.

### 12.3 Configure Environment Variables

Create or update the local `.env` file with the correct database connection settings.

Example structure:

```env
DB_HOST=localhost
DB_NAME=Asku_management
DB_USER=your_database_username
DB_PASSWORD=your_database_password
DB_PORT=5432
```

Replace the example username and password with the actual PostgreSQL credentials.

Do not share real credentials in documentation, screenshots, or public repositories.

### 12.4 Prepare the Database

Ensure that the PostgreSQL database exists and that the required application tables have been created or restored from a valid backup.

The database name used during local development is `Asku_management`.

### 12.5 Start the Application

From the project directory, run:

```bash
python app.py
```

When the local Flask server starts successfully, open:

`http://127.0.0.1:5000`

The exact startup behavior depends on the current `app.py` configuration.

### 12.6 GitHub Repository

The project repository is:

https://github.com/atonyaandrew1-code/ASKU_Management_System

Before pushing changes, confirm that private configuration files, database passwords, and backup files containing sensitive data are excluded from the repository.

## 13. Database Backup and Recovery

Regular database backups help protect association records against accidental deletion, corruption, or system failure.

### 13.1 Backup

A PostgreSQL backup can be created using `pg_dump`.

Example:

```bash
pg_dump -U your_database_username -d Asku_management -F c -f backups/Asku_management_backup.dump
```

Replace the example username with the correct PostgreSQL username.

The command assumes that the `backups` directory exists and that the PostgreSQL command-line utilities are installed.

### 13.2 Recovery

A custom-format backup can be restored using `pg_restore` into an appropriate target database.

Example:

```bash
pg_restore -U your_database_username -d target_database_name backups/Asku_management_backup.dump
```

The target database must exist unless the restore procedure is specifically configured to create it.

Restoration should be tested carefully, especially when the target database already contains records.

### 13.3 Backup Recommendations

* Create backups regularly.
* Keep backup files separate from the live database.
* Restrict access to backup files.
* Store at least one backup in a secure location separate from the development computer.
* Test restoration periodically.
* Do not publish backups containing personal or financial information.

## 14. Maintenance and Future Improvements

The following improvements may be considered as the system develops.

### 14.1 Reporting Enhancements

Add more comprehensive reports and summaries for membership, attendance, payments, and transactions.

### 14.2 Audit Logs

Maintain records of important administrative actions, including changes to member information, financial records, and user permissions.

### 14.3 Data Export

Provide controlled export options for authorized users who need reports or records for administrative purposes.

### 14.4 Automated Backups

Introduce a reliable backup schedule and monitoring process.

### 14.5 Improved Validation

Strengthen form validation, error handling, and duplicate-record prevention.

### 14.6 Security Review

Review every route and sensitive operation to ensure that authentication and authorization checks are consistently applied.

### 14.7 Deployment Improvements

Use secure production configuration, HTTPS, managed environment variables, reliable database hosting, and appropriate error logging.

### 14.8 Documentation Updates

Update this document whenever major features, database tables, permissions, deployment procedures, or configuration requirements change.

## 15. Conclusion

The ASKU Management System provides a centralized platform for managing association members, activities, attendance, payments, financial transactions, user accounts, and authorized reports.

By combining a Flask application with a PostgreSQL database and role-based access control, the system is intended to improve record keeping, accountability, and continuity within ASKU.

Continued maintenance, testing, backups, and security reviews will help preserve the reliability of the application and support its future development.

---

**Document status:** Development documentation.
**Maintenance note:** Update this document whenever the actual application implementation or deployment configuration changes.

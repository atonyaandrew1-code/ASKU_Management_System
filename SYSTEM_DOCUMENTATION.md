# ASKU Management System

## 1. System Overview

The ASKU Management System is a web-based management system developed to help ASKU manage and track its members, activities, attendance, financial records and users.

The system provides controlled access based on user roles and permissions. It is designed to make organizational records easier to manage, retrieve, and maintain.

## 2. Main Objectives

The system is designed to:

- Manage ASKU member records.
- Generate and maintain member identification numbers.
- Manage activities
- Record member attendance.
- Manage payments and transactions.
- Manage system users.
- Control access according to user roles and permissions.
- Provide a centralized database for ASKU records.
- Maintain traceable records for future reference.

## 3. Technologies Used

- Python
- Flask
- PostgreSQL
- psycopg2
- HTML
- CSS
- Git
- GitHub
- Visual Studio Code

## 4. Main System Modules

### 4.1 Members

The Members module manages ASKU member records.

It supports:

- Adding members.
- Viewing members.
- Editing member information.
- Maintaining member identification numbers.
- Tracking member status.

### 4.2 Activities

The Activities module manages organizational activities.

It supports:

- Creating activities.
- Viewing activities.
- Recording activity dates.
- Recording locations.
- Tracking who created an activity.

### 4.3 Attendance

The Attendance module records member participation in activities.

It stores:

- Member.
- Activity.
- Attendance date.
- Attendance status.

### 4.4 Events

### 4.5 Payments

The Payments module records member payment information and allows authorized users to manage payment records.

### 4.6 


### 4.7 Transactions

The Transactions module records financial transactions and their related details.

### 4.8 User Management

The User Management module allows authorized administrators to:

- Add users.
- View users.
- Edit users.
- Manage user accounts.
- Control access through assigned roles.

### 4.9 Authentication

The authentication system provides:

- Login.
- Logout.
- Session management.
- Protected pages.
- Unauthorized-access protection.

## 5. User Roles and Access Control

The system uses role-based access control to determine what each user can access and manage.

### 5.1 Administrator

The Administrator has the highest level of access.

The Administrator can:

- Access the dashboard.
- Manage users.
- Manage members.
- Manage activities.
- Manage attendance.
- Manage payments.
- Manage transactions.
- Access management functions permitted by the system.

### 5.2 Treasurer

The Treasurer has access to financial management functions according to the permissions assigned to the role.

These include relevant functions for:

- Payments.
- Transactions.
- Financial records.

### 5.3 Secretary

The Secretary has access to organizational and record-management functions according to the permissions assigned to the role.

These include relevant functions for:

- Members.
- Activities.
- Attendance.
- Events.
- Other records permitted by the assigned permissions.

### 5.4 Member

The Member role provides limited access to the system.

Members can access only the functions and information permitted by their assigned permissions.

### 5.5 View-Only Access

Some permissions are restricted to viewing information without allowing the user to modify or delete records.

This helps protect important organizational records while still allowing authorized users to access information.

## 6. Database

The ASKU Management System uses PostgreSQL as its database management system.

### Database Name

```text

Main Database Tables

The system currently contains the following main tables:

members
activities
attendance
transactions
users
roles
permissions
role_permissions
6.1 Members Table

Stores information about ASKU members, including:

Member ID
First name
Last name
Phone
Email
Date joined
Status
Created date

Member IDs use the ASKU identification format, for example:

ASKU/001
ASKU/002
ASKU/003
6.2 Activities Table

Stores information about organizational activities, including:

Activity ID
Activity name
Activity date
Location
Created by
6.3 Attendance Table

Stores member attendance information, including:

Attendance ID
Member ID
Activity ID
Attendance date
Attendance status
6.4
6.5 Transactions Table

Stores financial transaction records, including:

Transaction ID
Member ID
Transaction type
Amount
Date
Description
Reference number
Time-related transaction information
6.6 Users Table

Stores system user accounts and their assigned access information.

6.7 Roles Table

Stores the roles used for controlling system access.

6.8 Permissions Table

Stores individual system permissions.

6.9 Role Permissions Table

Links roles to the permissions assigned to them.

## 7. System Features

### 7.1 User Authentication

The system provides secure user authentication through a login page.

Users must provide a valid username and password before accessing the management dashboard.

The system also provides a logout function that terminates the user's active session.

### 7.2 Role-Based Access Control

The system uses user roles and permissions to control access to different functions.

The main roles include:

- Administrator
- Chairperson
- Treasurer
- Secretary
- Member

Permissions are assigned to roles through the `role_permissions` table.

This prevents users from accessing functions that they are not authorized to use.

### 7.3 Member Management

The system allows authorized users to:

- View members
- Add new members
- Edit member information
- Manage member status
- Search and manage member records

Each member is identified using a unique Member ID.

The standard Member ID format is:

`ASKU/001`

### 7.4 Member ID Management

Administrators can change a member's Member ID when necessary.

Member IDs must follow the format:

`ASKU/###`

For example:

`ASKU/005`

can be changed to:

`ASKU/010`

The system prevents duplicate Member IDs.

When a Member ID is changed, PostgreSQL automatically updates the corresponding Member ID in related tables using `ON UPDATE CASCADE`.

The related tables include:

- Attendance
- Payments
- Transactions
- Users

This maintains database referential integrity.

### 7.5 User Management

Authorized administrators can manage system users.

User management includes:

- Adding users
- Editing users
- Deleting users
- Assigning roles
- Activating or deactivating users

User accounts are linked to members through the `member_id` field.

### 7.6 Activities Management

The system allows authorized users to manage organization activities.

Activities contain information such as:

- Activity ID
- Activity name
- Activity date
- Location
- User who created the activity

### 7.7 Attendance Management

The attendance module records member participation in activities.

Attendance records are linked to:

- Members
- Activities
- Attendance dates
- Attendance status

This allows the organization to track participation over time.

### 7.8 Payments Management

The system records payments made by members.

Payment records are associated with individual members and can be used to maintain financial records.

### 7.9 

### 7.10 Transactions Management

The transactions module records financial transactions involving members.

Transaction information includes:

- Transaction ID
- Member ID
- Transaction type
- Amount
- Date
- Description
- Reference number

### 7.11 Events Management


### 7.12 Dashboard

The dashboard provides an overview of important system information.

It displays summary information including:

- Total members
- Total payments
- Total activities
- Total attendance records
- Total transactions

The dashboard also provides navigation links to the main management modules.

### 7.13 Database Integrity

The system uses PostgreSQL foreign-key relationships to maintain consistency between related records.

Foreign-key relationships connect members with:

- Attendance
- Payments
- Transactions
- Users

The Member ID relationships use `ON UPDATE CASCADE` so that changes to a Member ID are automatically reflected in related records.

### 7.14 Security

The system includes several security controls:

- Password authentication
- Password hashing using bcrypt
- Session-based authentication
- Role-based permissions
- Protected management routes
- Admin-only Member ID modification
- Prevention of duplicate Member IDs
- Database foreign-key constraints

## 8. System Workflow

### 8.1 User Login

1. The user opens the ASKU Management System.
2. The system displays the login page if the user is not authenticated.
3. The user enters a username and password.
4. The system verifies the credentials.
5. The user's role and permissions are loaded.
6. The user is redirected to the dashboard.

### 8.2 Dashboard Access

After successful login, the user is taken to the dashboard.

The dashboard displays summary information and provides access to system modules based on the user's permissions.

### 8.3 Member Management Workflow

Authorized users can:

1. Open the Members module.
2. View existing members.
3. Add new members.
4. Edit member information.
5. Update member status.

Administrators can additionally change Member IDs.

### 8.4 User Management Workflow

Administrators can:

1. Open User Management.
2. View system users.
3. Add a new user.
4. Assign the user a role.
5. Edit user information.
6. Activate or deactivate a user.
7. Delete a user when necessary.

### 8.5 Activities and Attendance Workflow

The system allows authorized users to:

1. Create activities.
2. View activities.
3. Record member attendance.
4. View attendance records.

Attendance records are linked to both the member and the activity.

### 8.6 Financial Management Workflow

Financial information is managed through the Payments and Transactions modules.

Authorized users can record and view financial records according to their assigned permissions.

### 8.7 Member ID Change Workflow

Only an administrator can change a Member ID.

The workflow is:

1. Administrator opens the Members module.
2. Administrator selects a member.
3. Administrator opens the Edit Member page.
4. Administrator enters the new Member ID.
5. The system validates the Member ID format.
6. The system checks whether the new ID already exists.
7. If valid, the Member ID is updated.
8. PostgreSQL automatically updates related records through `ON UPDATE CASCADE`.
9. The administrator is returned to the Members list.

### 8.8 Logout Workflow

When a user selects Logout:

1. The active session is terminated.
2. The user is redirected to the login page.
3. Protected pages can no longer be accessed without logging in again.

### 8.9 Access Control Workflow

When a user attempts to access a protected function:

1. The system checks whether the user is logged in.
2. The system identifies the user's role.
3. The system checks the permissions assigned to that role.
4. If the required permission exists, access is granted.
5. If the permission does not exist, access is denied.

## 9. Testing and Verification

The ASKU Management System was tested after development to verify that the main functions operate correctly.

### 9.1 Authentication Testing

The following were tested:

- Valid user login
- Invalid username or password
- Logout
- Session protection
- Access to the dashboard after authentication

The authentication functions were successfully tested.

### 9.2 Role Testing

The following roles were tested:

- Administrator
- Chairperson
- Treasurer
- Secretary
- Member

Role-based access was tested to ensure that users can only access functions allowed by their permissions.

### 9.3 Member Management Testing

The following functions were tested:

- Viewing members
- Adding members
- Editing members
- Updating member information
- Updating member status
- Member ID validation
- Duplicate Member ID prevention

The functions operated correctly during testing.

### 9.4 Member ID Change Testing

The administrator Member ID change feature was tested by changing:

`ASKU/005`

to:

`ASKU/010`

The test confirmed that:

- The new Member ID was accepted.
- The old Member ID was removed.
- Duplicate IDs are prevented.
- The related transaction record was automatically updated.
- The related user account was automatically updated.
- Foreign-key relationships remained intact.

The test confirmed that `ON UPDATE CASCADE` is functioning correctly.

### 9.5 User Management Testing

User management functions were tested, including:

- Adding users
- Editing users
- Deleting users
- Assigning roles
- Activating and deactivating users
- Access control for user management

The functions were successfully tested.

### 9.6 Activities Testing

Activities were tested by:

- Adding activities
- Viewing activities
- Editing activities
- Managing activity information

The activities module operated correctly.

### 9.7 Attendance Testing

Attendance functionality was tested by:

- Recording attendance
- Viewing attendance records
- Linking attendance to members
- Linking attendance to activities

The attendance module operated correctly.

### 9.8 Financial Module Testing

The following modules were tested:

- Payments
- Transactions

The system successfully recorded and displayed financial information.

### 9.9 Events Testing


### 9.10 Dashboard Testing

The dashboard was tested to verify that summary figures are displayed correctly.

The following dashboard statistics were tested:

- Total members
- Total payments
- Total activities
- Total attendance records
- Total transactions

### 9.11 Database Integrity Testing

Database relationships were tested to ensure that related records remain connected to the correct member.

The Member ID cascade feature was specifically tested and confirmed to update related records automatically.

### 9.12 Overall Test Result

The major system modules and role-based access controls were tested successfully.

The system is currently functioning as expected in the local development environment.


## 10. Installation and Setup

### 10.1 Requirements

The ASKU Management System requires the following software:

- Python
- PostgreSQL
- pgAdmin
- Flask
- psycopg2
- bcrypt
- Git
- A modern web browser

### 10.2 Project Structure

The main project directory is:

`ASKU_Management_System`

The project contains the following main files and folders:

- `app.py` — Main Flask application
- `database.py` — Database connection configuration
- `requirements.txt` — Python dependencies
- `.gitignore` — Files excluded from Git
- `templates/` — HTML templates
- `static/` — Static files such as CSS and other frontend resources
- `SYSTEM_DOCUMENTATION.md` — System documentation

### 10.3 Database Setup

The system uses a PostgreSQL database named:

`Asku_management`

The database contains the tables required to manage:

- Members
- Users
- Roles
- Permissions
- Activities
- Attendance
- Payments
- Transactions
- Events

### 10.4 Python Environment

The required Python packages are listed in:

`requirements.txt`

They can be installed using:

```text
pip install -r requirements.txt

10.5 Running the Application

From the project directory, the Flask application can be started using:

python app.py

When the application starts successfully, it runs on the local development server.

The system can then be accessed through:

http://127.0.0.1:5000

10.6 Database Connection

The database connection is configured in:

database.py

The application connects to the local PostgreSQL server and the Asku_management database.

10.7 Git and Backup

The project is maintained using Git for version control.

The project has been backed up to GitHub to preserve the source code and development history.

Git is used to:

Track changes
Create commits
Maintain project history
Push backups to GitHub
Restore previous versions when necessary
10.8 Development Environment

The system was developed and tested locally using:

Windows
Visual Studio Code
Python
Flask
PostgreSQL
pgAdmin
Git

The application currently operates as a local development system.

## 11. Maintenance and Future Improvements

The ASKU Management System can be expanded and improved as the organization's needs grow.

### 11.1 Possible Future Improvements

Future versions of the system may include:

- Advanced search and filtering
- Financial reports
- Automated receipt generation
- PDF report generation
- Email notifications
- SMS notifications
- Improved dashboard charts and analytics
- Password reset functionality
- More detailed audit logs
- Automated database backups
- Improved mobile responsiveness
- Deployment to an online server
- HTTPS security
- More advanced reporting

### 11.2 Database Maintenance

Regular database maintenance should include:

- Creating regular backups
- Checking database integrity
- Reviewing unused records
- Monitoring database size
- Updating database software when necessary
- Protecting database credentials

### 11.3 User Account Maintenance

Administrators should regularly review user accounts to ensure that:

- Only authorized users have accounts.
- User roles are correctly assigned.
- Inactive users are disabled.
- Former users no longer have unnecessary access.
- Passwords are kept secure.

### 11.4 Security Maintenance

The system should be regularly reviewed for security issues.

Recommended practices include:

- Keeping Python and dependencies updated.
- Keeping PostgreSQL updated.
- Protecting the Flask secret key.
- Using strong passwords.
- Restricting database access.
- Regularly reviewing user permissions.
- Maintaining secure backups.

### 11.5 Backup Strategy

The source code should continue to be backed up using Git and GitHub.

The PostgreSQL database should also be backed up separately because a Git repository contains the application source code but does not automatically contain the live database records.

### 11.6 Deployment

Before deploying the system for production use, the following should be considered:

- Production-grade web hosting
- Secure PostgreSQL configuration
- HTTPS
- Production Flask configuration
- Secure environment variables
- Automated database backups
- Monitoring and logging
- Access control and server security

### 11.7 System Expansion

The system has been designed using separate modules so that additional functionality can be introduced without completely redesigning the existing application.

Future modules may include:

- Financial reporting
- Member communication
- Document management
- Meeting management
- Inventory management
- Advanced analytics
- Audit and compliance reporting

## 12. Conclusion

The ASKU Management System provides a centralized platform for managing members, users, activities, attendance, payments and transactions.

The system uses PostgreSQL for structured data storage and Flask for the web application.

Role-based access control ensures that users are given access according to their assigned responsibilities.

The system has been tested across its major modules and user roles. Database relationships have also been verified to maintain data integrity.

The administrator Member ID management feature uses PostgreSQL `ON UPDATE CASCADE` to ensure that changes to a Member ID are automatically reflected in related records.

The application is
 currently operational in the local development environment and can be further enhanced and deployed for production use in the future.
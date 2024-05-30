from flask import Flask, render_template, jsonify, request
import pymysql

app = Flask(__name__, static_url_path='/static')

# Configure MySQL connection
def get_db_connection():
    return pymysql.connect(
        host='nebula-db.cjiiukefoksp.us-east-1.rds.amazonaws.com',
        user='admin',
        password='master123',
        database='nebula'
    )

# Implement a basic health check endpoint
@app.route('/api/health-check')
def health_check():
    # You can add more sophisticated health checks here if needed
    return jsonify({'status': 'healthy'})

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/student-dashboard')
def student_dashboard():
    return render_template('student-dashboard.html')

@app.route('/config')
def config():
    return render_template('config.html')

@app.route('/api/students')
def get_students():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT name, email FROM Student_Details")  # Fetch name and email
                students_data = cur.fetchall()
                
                cur.execute("SELECT DISTINCT cohort_name FROM Cohort_Stats")  # Fetch unique cohort names
                cohorts_data = cur.fetchall()
                
                students = [{'name': row[0], 'email': row[1]} for row in students_data]  # Extracting student names and emails
                cohorts = [row[0] for row in cohorts_data]  # Extracting unique cohort names
                
                return jsonify({'students': students, 'cohorts': cohorts})
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/student/<email>', methods=['GET'])
def get_student_info(email):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Fetch student details including cohort and ranking
                cur.execute("SELECT attendance_average, assignment_completion, cohort_name, ranking FROM Student_Details WHERE email=%s", (email,))
                student_info = cur.fetchone()
                
                if student_info:
                    attendance_average, assignment_completion, cohort_name, ranking = student_info
                    return jsonify({'attendanceAverage': attendance_average, 'assignmentCompletion': assignment_completion, 'cohort': cohort_name, 'ranking': ranking})
                else:
                    return jsonify({'error': 'Student info not found'}), 404
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/test-db-connection', methods=['POST'])
def test_db_connection():
    data = request.form
    db_host = data.get('db_host')
    db_user = data.get('db_user')
    db_password = data.get('db_password')
    db_name = data.get('db_name')
    
    # Attempt to establish a connection
    try:
        with pymysql.connect(host=db_host, user=db_user, password=db_password, database=db_name) as test_conn:
            return jsonify({'message': 'Database connection successful'})
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to retrieve cohort statistics by cohort_name
@app.route('/api/cohort/stats/<cohort_name>', methods=['GET'])
def get_cohort_stats(cohort_name):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT total_students, average_attendance, average_assignment_completion FROM Cohort_Stats WHERE cohort_name=%s", (cohort_name,))
                cohort_stats = cur.fetchone()
                
                if cohort_stats:
                    total_students, average_attendance, average_assignment_completion = cohort_stats
                    return jsonify({
                        'cohort_name': cohort_name,
                        'total_students': total_students,
                        'average_attendance': average_attendance,
                        'average_assignment_completion': average_assignment_completion
                    })
                else:
                    return jsonify({'error': 'Cohort stats not found'}), 404
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500
    
# Endpoint to retrieve average attendance per week for a selected cohort
@app.route('/api/cohort/attendance/<cohort_name>', methods=['GET'])
def get_cohort_attendance(cohort_name):
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT week, average_attendance FROM Cohort_Stats WHERE cohort_name=%s", (cohort_name,))
                attendance_data = cur.fetchall()
                
                if attendance_data:
                    return jsonify({'attendance_data': attendance_data})
                else:
                    return jsonify({'error': 'Attendance data not found'}), 404
    except pymysql.MySQLError as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)

$(document).ready(function() {
    $('.js-example-basic-single').select2();

    // Function to update additional elements with N/A
    function updateAdditionalElements() {
        $('#attendance_average .element-value').text('N/A');
        $('#assignment_completion .element-value').text('N/A');
        $('#cohort .element-value').text('N/A');
        $('#ranking .element-value').text('N/A');
        $('#total_students .element-value').text('N/A');
    }

    // Initialize default select options and additional elements
    updateAdditionalElements();

    // Function to fetch cohort statistics based on cohort name
    function fetchCohortStats(cohortName) {
        fetch(`/api/cohort/stats/${cohortName}`)
            .then(response => response.json())
            .then(data => {
                const totalStudents = data.total_students;
                const averageAttendance = data.average_attendance;
                const averageAssignmentCompletion = data.average_assignment_completion;
                
                $('#total_students .element-value').text(totalStudents);
                $('#attendance_average .element-value').text(averageAttendance);
                $('#assignment_completion .element-value').text(averageAssignmentCompletion);
            })
            .catch(error => console.error(error));
    }

    fetch('/api/students')
        .then(response => response.json())
        .then(data => {
            const studentsSelect = $('#names');
            const cohortsSelect = $('#cohorts');

            // Populate select options for students
            studentsSelect.append($('<option>', {
                value: '',
                text: '--- Select/search a student ---'
            }));
            data.students.forEach(student => {
                const nameEmail = `${student.name} (${student.email})`;
                studentsSelect.append(new Option(nameEmail, student.email));
            });

            // Populate select options for cohorts
            cohortsSelect.append($('<option>', {
                value: '',
                text: '--- Search/select a cohort ---'
            }));
            data.cohorts.forEach(cohort => {
                cohortsSelect.append(new Option(cohort, cohort));
            });
        })
        .catch(error => console.log(error));
    
    // Event listener for changes in the input field
    $('.js-example-basic-single').on('change', function() {
        const selectedEmail = $('#names').val();
        const selectedCohort = $('#cohorts').val();
        
        if (!selectedEmail && !selectedCohort) {
            // If no student or cohort is selected, update additional elements with N/A
            updateAdditionalElements();
        } else if (selectedEmail) {
            fetch(`/api/student/${selectedEmail}`)
                .then(response => response.json())
                .then(data => {
                    // Display attendance average
                    const attendanceAverage = parseFloat(data.attendanceAverage).toFixed(2);
                    $('#attendance_average .element-value').text(attendanceAverage);
                    
                    // Display assignment completion
                    const assignmentCompletion = parseFloat(data.assignmentCompletion).toFixed(2);
                    $('#assignment_completion .element-value').text(assignmentCompletion);

                    // Display cohort and ranking
                    const cohort = data.cohort;
                    const ranking = data.ranking;
                    $('#cohort .element-value').text(cohort);
                    $('#ranking .element-value').text(ranking);
                })
                .catch(error => console.error(error));
        } else if (selectedCohort) {
            // If only a cohort is selected, fetch and display cohort statistics
            fetchCohortStats(selectedCohort);
            
            // Fetch and display the bar chart
            fetchAndDisplayChart(selectedCohort);
        }
    });
    
    // Function to fetch and display the bar chart
    function fetchAndDisplayChart(cohortName) {
        fetch(`/api/cohort/attendance/${cohortName}`)
            .then(response => response.json())
            .then(data => {
                const attendanceData = data.attendance_data;
                const weeks = attendanceData.map(item => item.week);
                const attendanceValues = attendanceData.map(item => item.average_attendance);

                // Create the bar chart
                const ctx = document.getElementById('cohort-performance-chart').getContext('2d');
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: weeks,
                        datasets: [{
                            label: 'Average Attendance',
                            data: attendanceValues,
                            backgroundColor: 'rgba(54, 162, 235, 0.5)',
                            borderColor: 'rgba(54, 162, 235, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
            })
            .catch(error => console.error(error));
    }
});

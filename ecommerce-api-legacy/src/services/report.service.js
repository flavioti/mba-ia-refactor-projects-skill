const { PAYMENT_STATUS, UNKNOWN_STUDENT } = require('../config/constants');

function createReportService({ courseModel }) {
  return {
    /** Receita e alunos por curso — uma única consulta com JOIN. */
    async financialReport() {
      const rows = await courseModel.listWithEnrollments();
      const reportByCourse = new Map();

      for (const row of rows) {
        if (!reportByCourse.has(row.course_id)) {
          reportByCourse.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
        }
        if (row.enrollment_id === null) continue;

        const courseData = reportByCourse.get(row.course_id);
        if (row.payment_status === PAYMENT_STATUS.PAID) {
          courseData.revenue += row.payment_amount;
        }
        courseData.students.push({
          student: row.student_name || UNKNOWN_STUDENT,
          paid: row.payment_amount === null ? 0 : row.payment_amount,
        });
      }

      return Array.from(reportByCourse.values());
    },
  };
}

module.exports = { createReportService };

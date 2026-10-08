import json
from io import BytesIO
import unittest

from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.database import Base, User, Job, Application, ATSResult


class AccountAndAdminApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(cls.engine)
        cls.Session = sessionmaker(bind=cls.engine, autoflush=False, autocommit=False)

    @classmethod
    def tearDownClass(cls):
        cls.engine.dispose()

    def setUp(self):
        self.db = self.Session()
        self.admin = User(name="Recruiter", email="recruiter@example.test", password_hash=main.hash_password("InitialPassword1!"), role="admin", department="People")
        self.db.add(self.admin)
        self.db.commit()

    def tearDown(self):
        if self.admin.profile_photo:
            main.delete_profile_photo(self.db, self.admin)
        self.db.query(ATSResult).delete()
        self.db.query(Application).delete()
        self.db.query(Job).delete()
        self.db.query(User).delete()
        self.db.commit()
        self.db.close()

    def test_public_registration_always_creates_student_with_profile_fields(self):
        payload = main.Registration(name="A Student", email="a.student@example.com", password="SecurePassword1!", department="ECE", register_number="ECE-1001", role="admin")
        response = main.register(payload, self.db)
        student = self.db.query(User).filter_by(email="a.student@example.com").one()
        self.assertEqual(student.role, "student")
        self.assertEqual(student.department, "ECE")
        self.assertEqual(student.register_number, "ECE-1001")
        self.assertNotIn("password", response["user"])
        self.assertNotIn("password_hash", response["user"])

    def test_student_profile_change_and_password_change(self):
        student = User(name="A Student", email="student@example.test", password_hash=main.hash_password("CurrentPassword1!"), role="student", department="CSE", register_number="CSE-001")
        self.db.add(student); self.db.commit()
        profile = main.update_profile(main.ProfileInput(name="Updated Student", department="AI/ML", register_number="AIML-002"), self.db, student)
        self.assertEqual((profile["name"], profile["department"], profile["register_number"]), ("Updated Student", "AI/ML", "AIML-002"))
        with self.assertRaises(HTTPException):
            main.change_password(main.PasswordInput(current_password="wrong", new_password="NewPassword1!", confirm_password="NewPassword1!"), self.db, student)
        main.change_password(main.PasswordInput(current_password="CurrentPassword1!", new_password="NewPassword1!", confirm_password="NewPassword1!"), self.db, student)
        self.assertTrue(main.verify_password("NewPassword1!", student.password_hash))

    def test_register_number_is_unique_and_password_confirmation_is_checked(self):
        first = User(name="One", email="one@example.test", password_hash="x", role="student", register_number="CSE-9")
        self.db.add(first); self.db.commit()
        with self.assertRaises(HTTPException) as duplicate:
            main.register(main.Registration(name="Two", email="two@example.com", password="SecurePassword1!", department="CSE", register_number="cse-9"), self.db)
        self.assertEqual(duplicate.exception.status_code, 409)
        second = User(name="Two", email="two@example.test", password_hash=main.hash_password("CurrentPassword1!"), role="student", register_number="CSE-10")
        self.db.add(second); self.db.commit()
        with self.assertRaises(HTTPException):
            main.change_password(main.PasswordInput(current_password="CurrentPassword1!", new_password="NewPassword1!", confirm_password="MismatchPassword1!"), self.db, second)

    def test_profile_image_validation_and_private_storage(self):
        payload = b"\x89PNG\r\n\x1a\n" + b"valid-test-image-content"
        upload = UploadFile(file=BytesIO(payload), filename="profile.png", headers=Headers({"content-type": "image/png"}))
        result = main.upload_profile_photo(upload, self.db, self.admin)
        self.assertTrue(result["photo_url"].startswith("/api/profile/photo"))
        self.assertTrue(self.admin.profile_photo.startswith(str(main.PROFILE_DIR)))
        with self.assertRaises(HTTPException):
            main.get_profile_photo(User(name="No Photo", email="nophoto@example.test", password_hash="x", role="student"))

    def test_admin_candidate_filters_and_analytics_use_saved_results(self):
        student = User(name="Sample Candidate", email="candidate@example.test", password_hash="x", role="student", department="CSE", register_number="CSE-200")
        job = Job(title="Software Engineer", description="Build software", minimum_score=70, required_skills="Python", optional_skills="SQL", active=True, created_by=self.admin.id)
        self.db.add_all([student, job]); self.db.commit()
        application = Application(student_id=student.id, job_id=job.id)
        self.db.add(application); self.db.commit()
        details = {"scores": {"required": 80, "optional": 60, "semantic_relevance": 70, "experience": 50, "projects": 75, "certifications": 0, "resume_quality": 60, "technical_expression": 70}}
        self.db.add(ATSResult(application_id=application.id, overall_score=74, details=json.dumps(details), qualification_status="QUALIFIED")); self.db.commit()
        rows = main.candidates(self.db, self.admin, department="CSE", register_number="200", search=None, job_id=job.id, status="QUALIFIED", min_score=70, max_score=80, date_from=None, date_to=None, limit=25, offset=0)
        self.assertEqual(rows["total"], 1)
        self.assertEqual(rows["items"][0]["register_number"], "CSE-200")
        stats = main.analytics(self.db, self.admin, department="CSE", job_id=job.id, min_score=None, max_score=None)
        self.assertEqual(stats["total_resumes_screened"], 1)
        self.assertEqual(stats["average_score"], 74)
        self.assertEqual(stats["by_job"][0]["title"], "Software Engineer")

    def test_admin_directory_includes_students_without_an_application(self):
        student = User(name="New Student", email="new.student@example.test", password_hash="x", role="student", department="Civil", register_number="CIV-401")
        self.db.add(student); self.db.commit()
        rows = main.candidates(self.db, self.admin, department="Civil", register_number=None, search=None, job_id=None, status=None, min_score=None, max_score=None, date_from=None, date_to=None, limit=25, offset=0)
        self.assertEqual(rows["total"], 1)
        self.assertEqual(rows["items"][0]["job_title"], "No application yet")
        self.assertIsNone(rows["items"][0]["score"])

    def test_student_cannot_read_another_students_application(self):
        one = User(name="One", email="one@example.test", password_hash="x", role="student", register_number="RN-1")
        two = User(name="Two", email="two@example.test", password_hash="x", role="student", register_number="RN-2")
        job = Job(title="Engineer", description="Build", minimum_score=70, required_skills="Python", created_by=self.admin.id)
        self.db.add_all([one, two, job]); self.db.commit()
        application = Application(student_id=one.id, job_id=job.id)
        self.db.add(application); self.db.commit()
        with self.assertRaises(HTTPException) as denied:
            main.owned(application, two)
        self.assertEqual(denied.exception.status_code, 403)
        with self.assertRaises(HTTPException) as admin_denied:
            main.require_admin(two)
        self.assertEqual(admin_denied.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()

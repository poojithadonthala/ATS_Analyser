from types import SimpleNamespace
import unittest

from app.services.scoring import analyze


class ProjectAwareScoringTests(unittest.TestCase):
    def score(self, resume: str, required: str):
        job = SimpleNamespace(
            title="Engineer",
            description="",
            required_skills=required,
            preferred_skills="",
            minimum_score=60,
        )
        return analyze(resume, job)

    def test_tensorflow_is_exact_when_named_in_project(self):
        _, detail = self.score(
            "Projects\nHandwritten Digit Recognition: Built a CNN classifier with TensorFlow and Python; reached 94% accuracy.",
            "TensorFlow",
        )
        match = detail["required_skills"][0]
        self.assertTrue(match["exact_match"])
        self.assertEqual(match["project_name"], "Handwritten Digit Recognition")
        self.assertEqual(match["evidence_score"], 100)

    def test_related_tensorflow_evidence_is_not_exact(self):
        _, detail = self.score(
            "Projects\nImage Classification Project: Built a CNN classifier with Python; reached 91% accuracy.",
            "TensorFlow",
        )
        match = detail["required_skills"][0]
        self.assertFalse(match["exact_match"])
        self.assertEqual(match["match_type"], "Related Match")
        self.assertEqual(match["project_name"], "Image Classification Project")

    def test_kmeans_demonstrates_machine_learning_without_claiming_exact_skill(self):
        _, detail = self.score(
            "Projects\nCustomer Segmentation: Applied K-means clustering to group retail customers and evaluated clusters.",
            "Machine Learning",
        )
        match = detail["required_skills"][0]
        self.assertFalse(match["exact_match"])
        self.assertEqual(match["match_type"], "Demonstrated Match")
        self.assertEqual(match["project_name"], "Customer Segmentation")

    def test_web_stack_is_related_to_react_but_not_exact(self):
        _, detail = self.score(
            "Projects\nStorefront: Built an e-commerce website using HTML, CSS, and JavaScript with product search and cart.",
            "React",
        )
        match = detail["required_skills"][0]
        self.assertFalse(match["exact_match"])
        self.assertEqual(match["match_type"], "Related Match")
        self.assertEqual(match["project_name"], "Storefront")

    def test_python_scripts_are_explicit_practical_evidence(self):
        _, detail = self.score(
            "Projects\nData Tool: Wrote Python scripts to clean and transform CSV datasets.",
            "Python",
        )
        match = detail["required_skills"][0]
        self.assertTrue(match["exact_match"])
        self.assertEqual(match["project_name"], "Data Tool")

    def test_visualization_fields_are_from_the_stored_analysis_payload(self):
        _, detail = self.score(
            "Summary\nData engineer using Python.\nSkills\nPython, SQL\nProjects\nCustomer Segmentation: Applied K-means clustering to group customers; improved review time by 20%.",
            "Python, Machine Learning",
        )
        self.assertEqual(detail["job_context"]["required_skills"], ["Python", "Machine Learning"])
        self.assertEqual(detail["project_analysis"]["score"], detail["scores"]["projects"])
        self.assertTrue(any(x["section"] == "Projects" and x["evidence_count"] for x in detail["resume_section_evidence"]))
        self.assertTrue(any(x["capability"] == "clustering" for x in detail["project_capability_evidence"]))
        self.assertEqual(detail["required_skills"][1]["evidence_score"], detail["related_skills"][0]["evidence_score"])


if __name__ == "__main__":
    unittest.main()

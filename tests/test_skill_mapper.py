"""Tests for category detection."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'jobhunter_crm'))

from services.skill_mapper import SkillMapper

mapper = SkillMapper()


class TestSkillMapper:
    """Tests for SkillMapper category detection."""

    def test_frontend_detection(self):
        """Frontend developer should go to 'frontend'."""
        result = mapper.detect('Frontend Developer', 'HTML CSS JavaScript React')
        assert result == 'frontend', f'Expected frontend, got {result}'

    def test_python_detection(self):
        """Python developer should go to 'python'."""
        result = mapper.detect('Backend Developer', 'Python Django FastAPI PostgreSQL Docker')
        assert result == 'python', f'Expected python, got {result}'

    def test_data_analyst_detection(self):
        """Data analyst should go to 'data_analyst'."""
        result = mapper.detect('Data Analyst', 'SQL Power BI Excel Python')
        assert result == 'data_analyst', f'Expected data_analyst, got {result}'

    def test_smm_detection(self):
        """SMM manager should go to 'smm'."""
        result = mapper.detect('SMM Manager', 'Facebook Ads Instagram Marketing')
        assert result == 'smm', f'Expected smm, got {result}'

    def test_graphic_design_detection(self):
        """Graphic designer should go to 'graphic_design'."""
        result = mapper.detect('Graphic Designer', 'Figma Photoshop Illustrator CorelDRAW')
        assert result == 'graphic_design', f'Expected graphic_design, got {result}'

    def test_no_match_returns_none(self):
        """Unrelated vacancy should return None."""
        result = mapper.detect('Driver', 'Driving license car')
        assert result is None, f'Expected None, got {result}'

    def test_senior_frontend_still_frontend(self):
        """Senior Frontend should still match frontend."""
        result = mapper.detect('Senior Frontend Developer', 'React TypeScript')
        assert result == 'frontend', f'Expected frontend, got {result}'

    def test_empty_description(self):
        """Should work with empty description."""
        result = mapper.detect('Python Developer', '')
        assert result == 'python', f'Expected python, got {result}'

    def test_case_insensitive(self):
        """Matching should be case-insensitive."""
        result = mapper.detect('DATA SCIENTIST', 'MACHINE LEARNING TENSORFLOW')
        assert result == 'data_science', f'Expected data_science, got {result}'

    def test_blender_detection(self):
        """Blender artist should go to 'blender'."""
        result = mapper.detect('3D Artist', 'Blender Cycles 3D Modeling Animation')
        assert result == 'blender', f'Expected blender, got {result}'

    def test_3d_max_detection(self):
        """3D designer using 3ds Max should go to '3d_max'."""
        result = mapper.detect('Interior Designer', '3ds Max AutoCAD V-Ray')
        assert result == '3d_max', f'Expected 3d_max, got {result}'

    def test_ms_office_detection(self):
        """Office manager should go to 'ms_office'."""
        result = mapper.detect('Office Manager', 'Microsoft Excel Word PowerPoint')
        assert result == 'ms_office', f'Expected ms_office, got {result}'

    def test_mobilograf_detection(self):
        """Mobilograf should go to 'mobilograf'."""
        result = mapper.detect('Mobilograf', 'CapCut Premiere Pro Video Editing')
        assert result == 'mobilograf', f'Expected mobilograf, got {result}'

    def test_data_science_detection(self):
        """Data scientist should go to 'data_science'."""
        result = mapper.detect('ML Engineer', 'scikit-learn TensorFlow PyTorch Deep Learning')
        assert result == 'data_science', f'Expected data_science, got {result}'

    def test_php_backend_still_frontend(self):
        """PHP backend should go to frontend (has PHP in frontend list)."""
        result = mapper.detect('PHP Developer', 'Laravel MySQL HTML CSS')
        assert result == 'frontend', f'Expected frontend, got {result}'

    def test_get_label(self):
        """get_label should return correct display name."""
        assert mapper.get_label('frontend') == 'Web Dasturlash'
        assert mapper.get_label('python') == 'Python'
        assert mapper.get_label('nonexistent') == 'Nonexistent'

    def test_get_all_categories(self):
        """get_all_categories should return all 10 categories."""
        cats = mapper.get_all_categories()
        assert len(cats) == 10
        assert 'frontend' in cats
        assert 'python' in cats
        assert 'data_analyst' in cats

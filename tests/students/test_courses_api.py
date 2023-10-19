import pytest
import random
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Student, Course
from students.serializers import CourseSerializer


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.fixture
def courses_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.mark.django_db
class TestApp:
    """Все тесты, кроме тестов фильтрации (они вне класса ниже)"""

    def test_get_one_course(self, api_client, courses_factory):
        """Проверка получения 1‑го курса (retrieve-логика)"""

        courses = courses_factory(_quantity=10, make_m2m=True)

        courses_id = [course.id for course in courses]
        response = api_client.get(f'/api/v1/courses/{random.randint(1, 10)}/')
        data = response.json()

        assert response.status_code == 200
        assert data['id'] in courses_id

    def test_get_list_courses(self, api_client, courses_factory):
        """Проверка получения списка курсов (list-логика)"""

        courses = courses_factory(_quantity=10, make_m2m=True)

        response = api_client.get('/api/v1/courses/')
        data = response.json()

        assert response.status_code == 200
        assert [course['id'] for course in data] == [course.id for course in courses]

    def test_created_course(self, api_client):
        """Тест успешного создания курса"""
        base_before = Course.objects.count()
        response = api_client.post('/api/v1/courses/',
                                   data={'name': 'Тестовый курс'})

        assert response.status_code == 201
        assert base_before + 1 == Course.objects.count()

    def test_patch_course(self, api_client, courses_factory):
        """Тест успешного создания курса"""

        course = courses_factory(make_m2m=True)
        response = api_client.patch(f'/api/v1/courses/{course.id}/', data={'name': 'Обновленный курс'})

        assert response.status_code == 200
        assert Course.objects.get(id=course.id).name == 'Обновленный курс'

    def test_delete_course(self, api_client, courses_factory):
        """Тест успешного создания курса"""

        course = courses_factory(_quantity=5, make_m2m=True)
        size_before = len(course)
        response = api_client.delete(f'/api/v1/courses/{random.choice(course).id}/')

        assert response.status_code == 204
        assert Course.objects.count() == size_before - 1


@pytest.mark.django_db
def test_filter_id(api_client, courses_factory):
    """Проверка фильтрации списка курсов по id"""

    list_large = random.randint(1, 100)
    courses = courses_factory(_quantity=list_large, make_m2m=True)
    random_course = random.choice(courses).id

    response = api_client.get(f'/api/v1/courses/', {'id': random_course})
    data = response.json()

    assert response.status_code == 200
    assert data[0]['id'] == courses[random_course - 1].id


@pytest.mark.django_db
def test_filter_name(api_client, courses_factory):
    """Проверка фильтрации списка курсов по name"""

    list_large = random.randint(10, 100)
    courses = courses_factory(_quantity=list_large, make_m2m=True)
    random_course = random.choice(courses)

    response = api_client.get(f'/api/v1/courses/', {'name': random_course.name})
    data = response.json()

    assert response.status_code == 200
    assert data[0]['name'] == courses[random_course.id - 1].name


@pytest.mark.parametrize('parameter',
                         [[x for x in range(5)], pytest.param([x for x in range(25)], marks=pytest.mark.xfail)])
def test_max_students(parameter):
    """Проверка максимального число студентов"""

    data = {"students": parameter}
    check = CourseSerializer().validate(data)

    assert data == check

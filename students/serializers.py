from rest_framework import serializers

from students.models import Course
from rest_framework.exceptions import ValidationError


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "name", "students")

    def update(self, instance, validated_data):
        """Метод для обновления"""

        return super().update(instance, validated_data)

    def validate(self, data):
        if 'students' in [data]:
            count_students_for_add = len(data['students'])
            if count_students_for_add > 20:
                raise ValidationError(
                    f'Максимально возможное количество студентов на курсе - 20, вы хотите добавить {count_students_for_add}.')
        return data

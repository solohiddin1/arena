# from typing import Required
# from rest_framework import serializers
# # from app.models.owner import Teacher
# from app.serializers_f.user_serializer import UserSerializer
# from app.models import User
# # from app.serializers_f.teacher_serializer import TeacherSerializer
# from app import serializers_f

# class TeacherSerializer(serializers.ModelSerializer):   
#     user = UserSerializer()

#     class Meta:
#         model = Teacher
#         fields = ['name','surname','age','user']
#         read_only_fields = ['created_at','updated_at']


# class TeacherAddUserSerializer(serializers.Serializer):
#     user = UserSerializer(required=True)
#     teacher = TeacherSerializer(required=True)

#     def create(self, validated_data):
#         user_data = validated_data.pop('user')
#         user_data['is_teacher'] = True
#         user_data['is_admin'] = False
#         user_data['is_student'] = False
#         user = User.objects.create(**user_data)

#         teacher_data = validated_data.pop('teacher')
#         teacher = Teacher.objects.create(user=user, **teacher_data)
#         return teacher


# class TeacherCreateSerializer(serializers.ModelSerializer):
#     user = UserSerializer(required=True)
#     # teacher = TeacherSerializer(required=True)
#     class Meta:
#         model = Teacher
#         fields = "__all__"

#     def create(self, validated_data):
#         user_data = validated_data.pop('user')
#         user_data['is_teacher'] = True
#         user_data['is_admin'] = False
#         user_data['is_student'] = False
#         user = User.objects.create_user(**user_data)

#         # teacher_data = validated_data.pop('teacher')
#         teacher = Teacher.objects.create(user=user, **validated_data)
#         return teacher

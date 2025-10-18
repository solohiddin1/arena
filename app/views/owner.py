# from django.core.mail import send_mail
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework import status
# # from ..serializers import UserSerializer
# from app.models import owner
# # from app.models.owner import Teacher
# from app.models.user import User
# # from app.serializers_f.student_serizlizer import StudentSerializer
# from app.serializers_f.owner_serializer import TeacherCreateSerializer, TeacherAddUserSerializer, TeacherSerializer
# from drf_yasg.utils import swagger_auto_schema


# # @permission_classes([IsAuthenticated])
# # class TeacherProfileView(APIView):
# #     def get(self,request):
# #         print(request.user.id)
# #         try:
# #             teacher = Teacher.objects.get(user=request.user)
# #         except Teacher.DoesNotExist:
# #             return Response({"error":"Teacher model does not exists"},status=status.HTTP_404_NOT_FOUND)
# #         except Exception as e:
# #             return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
# #         serializer = TeacherSerializer(teacher)

# #         data = serializer.data.copy()
# #         data['email'] = teacher.user.email
# #         data['phone_number'] = teacher.user.phone_number
# #         print(data)
# #         return Response(data,status=status.HTTP_200_OK)


# @permission_classes([IsAdminUser])
# class TeacherCreateView(APIView):
#     @swagger_auto_schema(request_body=TeacherCreateSerializer)
#     def post(self,request):
#         try:
#             serializer = TeacherCreateSerializer(data=request.data)
#             if serializer.is_valid():
#                 teacher = serializer.save()
#                 user = teacher.user
#                 send_mail(
#                 subject = 'Welcome to the Teacher Portal',
#                 message = f'Hello {teacher.name},\n\nYour teacher account has been created successfully.\n Your email is {user.email} and your password is [123456]\n\nThank you for joining us!',
#                 from_email = 'sirojiddinovsolohiddin961@gmail.com',
#                 recipient_list = [user.email],
#                 fail_silently = False
#                 )
#                 return Response(TeacherSerializer(teacher).data,status=status.HTTP_201_CREATED)
#             return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"error":str(e)})
    
#     def get(self,request):
#         try:
#             # teachers = Teacher.objects.all()
#             teachers = Teacher.objects.select_related('user').prefetch_related('teaching_groups').all()
#             print(teachers)
#             # for i in teachers:
#             #     print(i)
#             #     print(i.name,)
#             if teachers.exists():
#                 serializer = TeacherSerializer(teachers,many=True)
#                 return Response(serializer.data,status=200)
#             return Response({"error ": "No teachers fuond"},status=404)
#         except Exception as e:
#             return Response({"error":str(e)})


#     def put(self, request, pk=None):
#         try:
#             teacher = Teacher.objects.get(pk=pk)
#             serializer = TeacherCreateSerializer(teacher, data=request.data, partial=True)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(TeacherSerializer(teacher).data, status=200)
#             return Response(serializer.errors, status=400)
#         except Teacher.DoesNotExist:
#             return Response({"error": "Teacher not found"}, status=404)
#         except Exception as e:
#             return Response({"error": str(e)}, status=400)

#     def delete(self, request, pk=None):
#         try:
#             teacher = Teacher.objects.get(pk=pk)
#             teacher.delete()
#             return Response({"message": "Teacher deleted successfully"}, status=200)
#         except Teacher.DoesNotExist:
#             return Response({"error": "Teacher not found"}, status=404)
#         except Exception as e:
#             return Response({"error": str(e)}, status=400)
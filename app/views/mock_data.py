# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.decorators import permission_classes
# from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
# # from drf_yasg.utils import swagger_auto_schema
# from app.models.user import User
# # from django.db.models.functions import TruncMonth, TruncYear
# from django.db.models import Count
# from django.utils.dateparse import parse_date
# from django.db.models import Exists, OuterRef



# @permission_classes([AllowAny])
# class MockTwoMonth(APIView):

#     def get(self, request, date1, date2):

#         date1 = request.query_params.get('date1', date1)
#         date2 = request.query_params.get('date2', date2)


#         date1_parsed = parse_date(str(date1))
#         date2_parsed = parse_date(str(date2))

#         if not date1_parsed or not date2_parsed:
#             return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

#         students = Student.objects.annotate(
#             in_group=Exists(Group.students_set.through.objects.filter(student_id=OuterRef('pk')))
#         ).values('id', 'name', 'surname', 'user__email', 'in_group')
        
#         # .values('month').annotate(count=Count('id')).values('month', 'count')
#         in_group_students = students.filter(in_group=True).count()
#         # in_group_students = students.filter(in_group=True)
#         out_group_students = students.filter(in_group=False).count()
#         # out_group_students = students.filter(in_group=False)
#         print(students, '11111')

#         # Mock data generation logic
#         data = {
#             "message": "mock data",
#             "status": "success",
#             "in group": in_group_students,
#             "out group": out_group_students,
#             "date1": date1,
#             "date2": date2,
#         }
#         # print(data)
#         return Response(data, status=status.HTTP_200_OK)


# @permission_classes([AllowAny])
# class MockTwoCount(APIView):

#     def get(self, request, date1, date2):

#         date1 = request.query_params.get('date1', date1)
#         date2 = request.query_params.get('date2', date2)


#         date1_parsed = parse_date(str(date1))
#         date2_parsed = parse_date(str(date2))

#         if not date1_parsed or not date2_parsed:
#             return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

#         students = Student.objects.filter(user__created_at__range=(date1_parsed, date2_parsed))

#         data = {
#             "message": "mock data",
#             "status": "success",
#             "date1": date1,
#             "date2": date2,
#             "count": students.count()
#         }
#         # print(data)
#         return Response(data, status=status.HTTP_200_OK)


# class MockDataView(APIView):
#     permission_classes = ([AllowAny])
    
#     def get(self, request, year, month):
#         year = request.query_params.get('year', year)
#         month = request.query_params.get('month', month)

#         try:
#             year = int(year)
#             month = int(month)
#         except ValueError:
#             return Response({"error": "Invalid year or month"}, status=status.HTTP_400_BAD_REQUEST)
#         user = User.objects.all()
#         print(month)
#         # students = Student.objects.filter(user__created_at__year=year,user__created_at__month=month)
#         students = Student.objects.filter(user__created_at__year = year, user__created_at__month = month).values('user__created_at__year', 'user__created_at__month').annotate(total = Count('id'))
#         # students = Student.objects.values('user__created_at__year' , 'user__created_at__month').annotate(total = Count('id')).order_by('user__created_at__year')
#         # students = Student.objects.annotate(month=TruncMonth('user__created_at')).values('month').annotate(total=Count('id')).order_by('month')
        
#         print(students)
#         # students = User.objects.filter(created_at__year=year, created_at__month=month)


#         # serializer = StudentSerializer(students, many=True)
#         data = {
#             "message": "mock data",
#             "status": "success",
#             "year": year,
#             "month": month,
#             "data": students
#         }
#         return Response(data, status=status.HTTP_200_OK)


# @permission_classes([AllowAny])
# class MockDataFinished(APIView):

#     def get(self,request):
#         finished = Student.objects.filter(is_finished=1).values('id','name','surname')
#         not_finished = Student.objects.filter(is_finished=0).values('id','name','surname')
        
#         data = {
#         "count": {
#                 "finished":finished.count(),
#                 "not finished": not_finished.count(),
#             },
#         "all_students": {
#             "finished":list(finished),
#             "not finished": list(not_finished),
#         }
#         }

#         return Response(data,status=status.HTTP_200_OK)



# @permission_classes([AllowAny])
# class MockDataActiveStudents(APIView):

#     def get(self,request):
#         students = Student.objects.all()
#         groups = Group.objects.all()
#         # print(groups)
#         # print(students)
#         # for i in groups:
#         groups_students = groups.first().students_set.all()
#         student_serializer = StudentSerializer(students,many=True)
#         group_serializer = GroupSerializer(groups,many=True)
#         all_students = []
#         # data = {}

#         for g in groups:
#             students_in_group = g.students_set.all()
#             all_students.extend(students_in_group)
#             print(g.name)
        
#         # total_students_in_group = Group.objects.annotate(total_students=Count('students_set')).values('total_students')

#         # Optionally, remove the following loop if not needed
#         # for s in Student.objects.all():
#         #     students_in_group = Group.objects.filter(students_set=s.id)
#         # print(students_in_group,' students====')

#         # for s in all_students:
#         #     print(s.name)
#         groups_data = []
#         for group in groups:
#             students_in_group = group.students_set.all()
#             students_serializer = StudentSerializer(students_in_group, many=True)
#             count = group.student_count
#             # print(count)
#             groups_data.append({
#             "group_name": group.name,
#             "student_count": count,
#             "students": students_serializer.data
#             })
#         group_serializer_student = StudentSerializer(all_students, many=True)
#         # group_serializer_student = StudentSerializer(groups_students,many=True)
#         # data = {"data":all_students}
#         # print(group_serializer_student.data,'-----------group_serializer_student====')

#         return Response({"data":groups_data},status=status.HTTP_200_OK)
#         # return Response({"data":group_serializer_student.data})

#         # return Response({"data":student_serializer.data,"groups":group_serializer.data})
from django.shortcuts import render
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated


@permission_classes([IsAdminUser])
def admin_panel(request):
    return render(request,'admin_dashboard.html')


permission_classes([IsAdminUser])
def TeacherCrud(request):
    return render(request,'teacher_view.html')


@permission_classes([IsAuthenticated])
def teacher_panel(request):
    return render(request,'teacher_dashboard.html')
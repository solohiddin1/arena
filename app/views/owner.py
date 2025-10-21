from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from app.models.owner import Owner
from app.models.user import User
from rest_framework.decorators import permission_classes
from app.serializers_f.owner_serializer import OwnerSerializer


@permission_classes([IsAuthenticated])
class OwnerProfileView(APIView):
    def get(self,request):
        print(request.user.id)
        try:
            owner = Owner.objects.get(user=request.user)
        except Owner.DoesNotExist:
            return Response({"error":"Teacher model does not exists"},status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)
        serializer = OwnerSerializer(owner)

        data = serializer.data.copy()
        data['email'] = owner.user.email
        data['phone_number'] = owner.user.phone_number
        print(data)
        return Response(data,status=status.HTTP_200_OK)

class OwnerRegisterView(APIView):
    def post(self, request):
        data = request.data
        print(data)
        try:
            print(data.get('user'))
            user = User.objects.get(id=data.get('user'))
            if user.is_owner == True:
                return Response({"error":"User is already an owner"},status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OwnerSerializer(data=data)
        if serializer.is_valid():
            user.is_owner = True
            user.save()
            serializer.save(user=user)

            return Response(serializer.data)
        return Response({"error":serializer.errors},status=status.HTTP_400_BAD_REQUEST)
from rest_framework import serializers
from apps.shared.models import Region, District


class DistrictSerializer(serializers.ModelSerializer):  
    class Meta:
        model = District
        fields = ['id', 'soato_id', 'name_uz', 'name_ru', 'name_en', 'region']

class RegionSerializer(serializers.ModelSerializer):
    disctricts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Region
        fields = ['id', 'soato_id', 'name_uz', 'name_ru', 'name_en', 'disctricts']
    
    def get_disctricts(self, obj):
        districts = District.objects.filter(region=obj)
        return DistrictSerializer(districts, many=True).data
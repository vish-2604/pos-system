from rest_framework import serializers
from adminside.models import Table

class TableSerializer(serializers.ModelSerializer):
    table_id = serializers.IntegerField(read_only=True)  # Ensure auto-increment behavior

    class Meta:
        model = Table
        fields = ['table_id', 'seats', 'status']  # Include table_id, but it's read-only

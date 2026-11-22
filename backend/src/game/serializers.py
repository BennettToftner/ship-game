from rest_framework import serializers

class PointCheckRequestSerializer(serializers.Serializer):
    # Expects a list of coordinate pairs, e.g., [[34.05, -118.24], [40.71, -74.00]]
    points = serializers.ListField(
        child=serializers.ListField(
            child=serializers.FloatField(),
            min_length=2,
            max_length=2
        ),
        allow_empty=False
    )

    def validate_points(self, value):
        # Optional: Add boundary checks for latitude and longitude
        for lat, lon in value:
            if not (-90.0 <= lat <= 90.0):
                raise serializers.ValidationError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
            if not (-180.0 <= lon <= 180.0):
                raise serializers.ValidationError(f"Invalid longitude: {lon}. Must be between -180 and 180.")
        return value


class PointCheckResponseSerializer(serializers.Serializer):
    # Output schema returning boolean results
    is_water = serializers.ListField(child=serializers.BooleanField())
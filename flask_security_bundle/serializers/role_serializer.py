try:
    from flask_api_bundle import ma
except ImportError:
    from flask_unchained import OptionalClass as ma


class RoleSerializer(ma.ModelSerializer):
    class Meta:
        model = 'Role'
        fields = ('id', 'name', 'description')

from flask_api_bundle import ma


class RoleSerializer(ma.ModelSerializer):
    class Meta:
        model = 'Role'
        fields = ('id', 'name', 'description')

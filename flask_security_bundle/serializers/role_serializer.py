try:
    from flask_unchained.bundles.api import ma
except ImportError:
    from flask_unchained import OptionalClass as ma


class RoleSerializer(ma.ModelSerializer):
    class Meta:
        model = 'Role'
        fields = ('id', 'name', 'description')

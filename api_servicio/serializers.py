import re
from rest_framework import serializers
from .models import Usuario
from itertools import cycle

class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    rut = serializers.CharField()

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'first_name', 'rut', 'password']

    # ESTO ES LO QUE NO PUEDE IGNORAR:
    def validate_rut(self, value):
        # 1. Limpieza
        rut_limpio = str(value).upper().replace("-", "").replace(".", "").strip()
        
        # 2. Check de letras (Regex)
        if not re.match(r"^\d{7,8}[0-9K]$", rut_limpio):
            raise serializers.ValidationError("RUT inválido: Solo números y K final.")

        # 3. Módulo 11
        cuerpo = rut_limpio[:-1]
        dv_ingresado = rut_limpio[-1]

        reverso = map(int, reversed(cuerpo))
        factores = cycle(range(2, 8))
        suma = sum(d * f for d, f in zip(reverso, factores))
        dv_esperado = str(11 - suma % 11)
        
        if dv_esperado == "11": dv_esperado = "0"
        if dv_esperado == "10": dv_esperado = "K"

        if dv_ingresado != dv_esperado:
            raise serializers.ValidationError("Dígito verificador incorrecto.")
        
        return rut_limpio

    def create(self, validated_data):
        return Usuario.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
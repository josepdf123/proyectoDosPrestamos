import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import Usuario, Rol

print("🔄 Creando usuarios...")

# Crear rol si no existe
rol, _ = Rol.objects.get_or_create(descripcion='usuario_solicitante')

# Crear usuarios
usuarios_a_crear = [
    {'usuario': 'john', 'password': '123456', 'correo': 'john@gmail.com', 'nombre': 'John', 'apellido': 'Doe'},
]

for user_data in usuarios_a_crear:
    if not Usuario.objects.filter(usuario=user_data['usuario']).exists():
        Usuario.objects.create_user(
            usuario=user_data['usuario'],
            password=user_data['password'],
            correo=user_data['correo'],
            nombre=user_data['nombre'],
            apellido=user_data['apellido'],
            idRol=rol,
            is_active=True
        )
        print(f"✅ Usuario creado: {user_data['usuario']}")
    else:
        print(f"⚠️ Usuario ya existe: {user_data['usuario']}")

print("✅ Script finalizado")

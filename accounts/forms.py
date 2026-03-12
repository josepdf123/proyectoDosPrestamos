from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Rol, Item, CategoriaItem, Equipo, CategoriaEquipo, Ticket


class LoginForm(forms.Form):
    """HU13: Formulario de login"""
    usuario = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ingresa tu usuario',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ingresa tu contraseña',
        })
    )


class RecuperacionContraseñaForm(forms.Form):
    """HU13: Formulario para solicitar recuperación de contraseña"""
    correo = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ingresa tu correo registrado',
        })
    )


class RestablecerContraseñaForm(forms.Form):
    """HU13: Formulario para restablecer contraseña"""
    password = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Ingresa la nueva contraseña',
        }),
        min_length=8,
        help_text='Mínimo 8 caracteres'
    )
    password_confirm = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirma la contraseña',
        }),
        min_length=8
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')

        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError('Las contraseñas no coinciden.')

        return cleaned_data


class UsuarioCreationForm(UserCreationForm):
    """HU14: Formulario para crear usuario"""
    nombre = forms.CharField(
        label='Nombre',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del usuario',
        })
    )
    apellido = forms.CharField(
        label='Apellido',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido del usuario',
        })
    )
    usuario = forms.CharField(
        label='Usuario',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario único',
        })
    )
    correo = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@institucion.edu',
        })
    )
    idRol = forms.ModelChoiceField(
        label='Rol',
        queryset=Rol.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña (mín. 8 caracteres)',
        })
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma la contraseña',
        })
    )

    class Meta:
        model = Usuario
        fields = ('nombre', 'apellido', 'usuario', 'correo', 'idRol', 'password1', 'password2')

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario')
        if Usuario.objects.filter(usuario=usuario).exists():
            raise forms.ValidationError('Este usuario ya existe.')
        return usuario

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Usuario.objects.filter(correo=correo).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return correo


class UsuarioEditForm(forms.ModelForm):
    """HU14: Formulario para editar usuario"""
    nombre = forms.CharField(
        label='Nombre',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre del usuario',
        })
    )
    apellido = forms.CharField(
        label='Apellido',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido del usuario',
        })
    )
    correo = forms.EmailField(
        label='Correo Electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@institucion.edu',
        })
    )
    idRol = forms.ModelChoiceField(
        label='Rol',
        queryset=Rol.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    is_active = forms.BooleanField(
        label='Usuario Activo',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
        })
    )

    class Meta:
        model = Usuario
        fields = ('nombre', 'apellido', 'correo', 'idRol', 'is_active')

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if Usuario.objects.filter(correo=correo).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return correo


# ─── HU09: FORMULARIOS PARA ITEMS ────────────────────────────────────────────

class ItemForm(forms.ModelForm):
    """HU09: Formulario para crear/editar ítems de inventario"""
    class Meta:
        model = Item
        fields = ['nombre', 'categoria', 'descripcion', 'cantidad', 'estado']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del ítem',
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del ítem',
            }),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
            }),
        }


# ─── HU10: FORMULARIOS PARA EQUIPOS ──────────────────────────────────────────

class EquipoForm(forms.ModelForm):
    """HU10: Formulario para crear/editar equipos"""
    class Meta:
        model = Equipo
        fields = ['nombre', 'categoria', 'descripcion', 'marca', 'modelo', 'numero_serie', 'estado', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del equipo',
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-control',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción del equipo',
            }),
            'marca': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Marca',
            }),
            'modelo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Modelo',
            }),
            'numero_serie': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número de serie',
            }),
            'estado': forms.Select(attrs={
                'class': 'form-control',
            }),
            'imagen': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }


# ─── HU11: FORMULARIOS PARA TICKETS ──────────────────────────────────────────

class TicketForm(forms.ModelForm):
    """HU11: Formulario para crear tickets"""
    class Meta:
        model = Ticket
        fields = ['equipo', 'tipo', 'descripcion']
        widgets = {
            'equipo': forms.Select(attrs={
                'class': 'form-control',
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe el trabajo a realizar',
            }),
        }


class TicketEditForm(forms.ModelForm):
    """HU11: Formulario para editar tickets (cambiar estado y notas)"""
    class Meta:
        model = Ticket
        fields = ['estado', 'notas']
        widgets = {
            'estado': forms.Select(attrs={
                'class': 'form-control',
            }),
            'notas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Notas técnicas del trabajo realizado',
            }),
        }


class PrestamoForm(forms.Form):
    """HU7: Formulario para solicitar préstamo"""
    from .models import Prestamo
    
    fecha_reclamo = forms.DateField(
        label='Fecha de Reclamo',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    fecha_entrega = forms.DateField(
        label='Fecha de Entrega',
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
        })
    )
    motivo = forms.CharField(
        label='Motivo del Préstamo',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Explica por qué necesitas este equipo',
        })
    )
from django import forms
from .models import Usuario, Rol

class RegistroForm(forms.ModelForm):
    """Formulario para registro de nuevos usuarios"""
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña'
        })
    )
    password_confirm = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirma tu contraseña'
        })
    )
    
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'usuario', 'correo']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu nombre'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tu apellido'
            }),
            'usuario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de usuario (para login)'
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'tu@email.com'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden')
        
        # Validar que usuario no exista
        usuario = cleaned_data.get('usuario')
        if Usuario.objects.filter(usuario=usuario).exists():
            raise forms.ValidationError('Este usuario ya existe')
        
        # Validar que correo no exista
        correo = cleaned_data.get('correo')
        if Usuario.objects.filter(correo=correo).exists():
            raise forms.ValidationError('Este correo ya está registrado')
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        
        # Asignar rol por defecto: usuario_solicitante
        rol = Rol.objects.get(descripcion='usuario_solicitante')
        user.idRol = rol
        user.is_active = True
        
        if commit:
            user.save()
        return user

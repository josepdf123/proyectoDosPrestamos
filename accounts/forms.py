from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Rol


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

from django import forms


class LoginForm(forms.Form):
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

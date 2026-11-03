from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.forms import inlineformset_factory, BaseInlineFormSet



class UsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True)
    grupo = forms.ModelChoiceField(queryset=Group.objects.filter(name__in=['Administrador','Supervisor','Administrativo']))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'grupo']
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo.')
        return email
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            user.groups.set([self.cleaned_data['grupo']])
        return user

class PerfilForm(forms.ModelForm):
    grupo = forms.ModelChoiceField(queryset=Group.objects.filter(name__in=['Administrador','Supervisor','Administrativo']))
    class Meta:
        model = User
        fields = ['first_name','last_name','email','is_active','grupo']
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not email or User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Ingresa un correo unico.')
        return email
    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user.groups.set([self.cleaned_data['grupo']])
        return user

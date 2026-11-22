from captcha.fields import CaptchaField, CaptchaTextInput
from django import forms


class UserForm(forms.Form):
    username = forms.CharField(label="账号", max_length=16, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="密码", max_length=16, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    captcha = CaptchaField(label='验证码', widget=CaptchaTextInput(attrs={'class': 'form-control'}))


class RegisterForm(forms.Form):
    username = forms.CharField(label="账号", max_length=16, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=16, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=16, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    age = forms.CharField(label="年龄", max_length=16, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # gender = forms.ChoiceField(label="性别", choices=(('Option 1', '男'), ('Option 2', '女'), ('Option 3', '未知')), widget=forms.RadioSelect(attrs={'class': 'form-check form-check-input'}))
    gender = forms.ChoiceField(
        label="性别",
        choices=(('男', '男'), ('女', '女'), ('未知', '未知')),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )
    phone = forms.CharField(label="手机号", max_length=16, widget=forms.TextInput(attrs={'class': 'form-control'}))
    captcha = CaptchaField(label='验证码', widget=CaptchaTextInput(attrs={'class': 'form-control'}))

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User


def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            return redirect(reverse(cadastro))
            # return redirect('/usuarios/cadastro')

        user = User.objects.all()

        if user.exists():
            return redirect(reverse(cadastro))

        try:
            User.objects.create_user(
                username=username,
                password=senha
            )
            return redirect(reverse(login))
        except:
            return redirect(reverse(cadastro))

    return HttpResponse('teste')


def login(request):
    return HttpResponse('Você está no login')

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages


def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR, 'Senhas não coincidem')
            return redirect(reverse(cadastro))
            # return redirect('/usuarios/cadastro')

        user = User.objects.all()

        if user.exists():

            messages.add_message(request, constants.ERROR, 'Usuário já existe')

            return redirect(reverse(cadastro))

        try:
            User.objects.create_user(
                username=username,
                password=senha
            )
            return redirect(reverse(login))
        except:
            messages.add_message(request, constants.ERROR, 'Erro interno do servidor')
            return redirect(reverse(cadastro))

    return HttpResponse('teste')


def login(request):
    return HttpResponse('Você está no login')

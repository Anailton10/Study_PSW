from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import messages
from django.contrib import auth


def cadastro(request):
    if request.method == "GET":
        return render(request, 'cadastro.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            messages.add_message(request, constants.ERROR,
                                 'Senhas não coincidem')
            return redirect(reverse(cadastro))
            # return redirect('/usuarios/cadastro')

        user = User.objects.filter(username=username)

        if user.exists():

            messages.add_message(request, constants.ERROR, 'Usuário já existe')

            return redirect(reverse(cadastro))

        try:
            User.objects.create_user(
                username=username,
                password=senha
            )
            return redirect(reverse(logar))
        except:
            messages.add_message(request, constants.ERROR,
                                 'Erro interno do servidor')
            return redirect(reverse(cadastro))

    return HttpResponse('teste')


def logar(request):
    if request.method == "GET":
        return render(request, 'login.html')
    elif request.method == "POST":
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = auth.authenticate(request, username=username, password=senha)

        if user:
            auth.login(request, user)
            messages.add_message(request, constants.SUCCESS, "Logado")
            return redirect('/flashcard/novo_flashcard/')
        else:
            messages.add_message(request, constants.ERROR,
                                 "Username ou Senha invalidos")
            return redirect(reverse(logar))


def logout(request):
    auth.logout(request)
    return redirect(reverse(logar))

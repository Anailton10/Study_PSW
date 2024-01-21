from django.shortcuts import render, redirect
from .models import Categoria, Flashcard, Desafio, FlashcardDesafio
from django.contrib.messages import constants
from django.contrib import messages
from django.http import HttpResponse, Http404


def novo_flashcard(request):
    if not request.user.is_authenticated:
        return redirect('/usuarios/logar')

    if request.method == "GET":
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        flashcards = Flashcard.objects.filter(user=request.user)

        categoria_filtrar = request.GET.get('categoria')
        dificuldade_filtrar = request.GET.get('dificuldade')

        if categoria_filtrar:
            flashcards = flashcards.filter(categoria__id=categoria_filtrar)

        if dificuldade_filtrar:
            flashcards = flashcards.filter(dificuldade=dificuldade_filtrar)

        return render(request, 'novo_flashcard.html',
                      {'categorias': categorias,
                       'dificuldades': dificuldades,
                       'flashcards': flashcards,
                       })

    elif request.method == "POST":
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')

        if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0:
            messages.add_message(request, constants.ERROR,
                                 'Campo pergunta ou resposta vazio.')
            return redirect('/flashcard/novo_flashcard/')

        flashcard = Flashcard(
            user=request.user,
            pergunta=pergunta,
            resposta=resposta,
            categoria_id=categoria,
            dificuldade=dificuldade
        )

        flashcard.save()
        messages.add_message(request, constants.SUCCESS,
                             'Flashcard cadastrada com sucesso.')
        return redirect('/flashcard/novo_flashcard/')


def deletar_flashcard(request, id):
    flashcard = Flashcard.objects.get(id=id)
    flashcard.delete()
    messages.add_message(
        request, constants.SUCCESS, 'Flashcard deletado com sucesso!'
    )
    return redirect('/flashcard/novo_flashcard')


def iniciar_desafio(request):
    if request.method == "GET":
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        return render(request, 'iniciar_desafio.html',
                      {'categorias': categorias,
                       'dificuldades': dificuldades, })

    elif request.method == "POST":
        titulo = request.POST.get('titulo')
        # getlist pois o campo seleciona mais de uma categoria, caso contrário era um get normal
        categorias = request.POST.getlist('categoria')
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')

        desafio = Desafio(
            user=request.user,
            titulo=titulo,
            quantidade_perguntas=qtd_perguntas,
            dificuldade=dificuldade
        )
        desafio.save()
        # forma secundaria.: "desafio.categoria.add(*categorias)"
        for cat in categorias:
            desafio.categoria.add(cat)

        # na filtragem "categoria_id__in=categorias" está fazendo uma filtragem
        # com a condição de que o id (_id) esteja em (__in)categorias.
        # order_by com ? faz com que sejam de maneira aleatória
        flashcards = (
            Flashcard.objects.filter(user=request.user).filter(
                dificuldade=dificuldade).filter(categoria_id__in=categorias).
            order_by('?')
        )
        if flashcards.count() < int(qtd_perguntas):
            messages.add_message(request, constants.ERROR,
                                 'Quantidade de perguntas acima ')
            return redirect('/flashcard/iniciar_desafio/')

        # para mosdtrar a quantidade de perguntas
        flashcards = flashcards[: int(qtd_perguntas)]

        for f in flashcards:
            flashcards_desafio = FlashcardDesafio(
                flashcard=f
            )
            flashcards_desafio.save()
            desafio.flashcard.add(flashcards_desafio)

        desafio.save()

        messages.add_message(request, constants.SUCCESS,
                             'Desafio cadastrado com sucesso')
        return redirect('/flashcard/listar_desafio/')


def listar_desafio(request):
    desafios = Desafio.objects.filter(user=request.user)
    # TODO: Resolver as filtragens (dificuldade e categoria)
    return render(request, 'listar_desafio.html',
                  {'desafios': desafios})


def desafio(request, id):
    desafio = Desafio.objects.get(id=id)
    # certificando que seja o proprio usuario que acesse o desafio
    if not desafio.user == request.user:
        raise Http404()
    if request.method == "GET":

        acertos = desafio.flashcard.filter(
            respondido=True).filter(acertou=True).count()

        erros = desafio.flashcard.filter(
            respondido=True).filter(acertou=False).count()

        faltantes = desafio.flashcard.filter(respondido=False).count()

        return render(request, 'desafio.html',
                      {'desafio': desafio,
                       'acertos': acertos,
                       'erros': erros,
                       'faltantes': faltantes})


def responder_flashcard(request, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id=id)
    desafio_id = request.GET.get('desafio_id')
    acertou = request.GET.get('acertou')

    if not flashcard_desafio.flashcard.user == request.user:
        raise Http404()
    flashcard_desafio.respondido = True

    flashcard_desafio.acertou = True if acertou == '1' else False

    flashcard_desafio.save()

    return redirect(f'/flashcard/desafio/{desafio_id}')


def relatorio(request, id):
    desafio = Desafio.objects.get(id=id)

    acertos = desafio.flashcard.filter(acertou=True).count()
    erros = desafio.flashcard.filter(acertou=False).count()
    dados = [acertos, erros]

    categorias = desafio.categoria.all()

    name_categoria = [i.nome for i in categorias]

    dados2 = []

    for categoria in categorias:
        dados2.append(desafio.flashcard.filter(
            flashcard__categoria=categoria).filter(acertou=True).count())

    # TODO: fazer ranking
    return render(request, 'relatorio.html',
                  {'desafio': desafio,
                   'dados': dados,
                   'categorias': name_categoria,
                   'dados2': dados2})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse, Http404
from .models import Ebook
from books.models import Genre
from books.forms import OpinionCreateForm
import os


def elibrary(request):
    ebook_list = Ebook.objects.all().order_by('book__title')
    genres = Genre.objects.all().order_by('name')

    context = {
        'title': 'Available ebooks',
        'library_class': 'nav-selected',
        'show_extras': 'no',
        'ebook_list': ebook_list,
        'genres': genres,
    }
    return render(request, 'ebooks/elibrary.html', context)


def ebook_details(request, pk):
    ebook = get_object_or_404(Ebook, id=pk)

    def update_book_rating():
        rating = 0
        for opinion in ebook.book.opinions.all():
            rating += opinion.rating
        ebook.book.rating = round(rating / len(ebook.book.opinions.all()), 2)
        ebook.book.save()

    opinions = ebook.book.opinions.all()
    new_opinion = None

    # Opinion posted
    if request.method == 'POST':
        opinion_create_form = OpinionCreateForm(data=request.POST)
        if opinion_create_form.is_valid():
            if opinions.filter(author=request.user).exists():
                messages.warning(request, "Cannot add another review. You have already reviewed this book!")
                return redirect(f'/ebook_details/{pk}/')
            new_opinion = opinion_create_form.save(commit=False)
            new_opinion.book = ebook.book
            new_opinion.author = request.user
            opinion_create_form.save()
            update_book_rating()
            messages.success(request, "Review succesfully added!")
            return redirect(f'/ebook_details/{pk}/')
    else:
        opinion_create_form = OpinionCreateForm()

    return render(request, 'ebooks/ebook_details.html', {'title': 'Book details', 'ebook': ebook})


def is_valid_queryparam(param):
    return param != '' and param is not None


def ebook_filter_view(request):
    qs = Ebook.objects.all()
    ebook_title = request.GET.get('ebook_title')
    ebook_genre = request.GET.get('ebook_genre')
    sort_method = request.GET.get('sort')

    genres = Genre.objects.all().order_by('name')
    searched = False
    most_popular = False

    if is_valid_queryparam(ebook_title):
        qs = qs.filter(book__title__icontains=ebook_title).order_by('book__title')
        searched = True
    if is_valid_queryparam(ebook_genre):
        qs = qs.filter(book__genre__name=ebook_genre)
    if is_valid_queryparam(sort_method):
        if sort_method == 'popularity':
            qs = qs.order_by('-download_count')
            most_popular = True
        else:
            qs = qs.order_by(sort_method)

    context = {
        'ebook_list': qs,
        'genres': genres,
        'searched': searched,
        'genre': ebook_genre,
        'popularity_ranking': most_popular,
    }

    return render(request, 'ebooks/elibrary.html', context)


def download_ebook(request, pk):
    ebook = Ebook.objects.get(id=pk)
    file_type = request.GET.get('type')
    path = ''
    if file_type == "txt":
        path = ebook.txt_book.url
    if file_type == "pdf":
        path = ebook.pdf_book.url
    file_path = str(settings.BASE_DIR) + path
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            ebook.download_count += 1
            print(ebook.download_count)
            ebook.save()
            return response
    raise Http404

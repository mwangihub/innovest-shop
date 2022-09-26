from django.shortcuts import render


def custom_page_not_found(request, exception, **kwargs):
    return render(None, 'error/404.html', status=404)


def custom_server_error(request, exception):
    return render(None, 'error/500.html', status=500)

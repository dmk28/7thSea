def render_to_response(request, template, context=None):
    """
    Wrapper for render() that catches Http404 errors and renders a 404 page.
    """
    try:
        return render(request, template, context)
    except Http404:
        return render(request, '404.html', context, status=404)
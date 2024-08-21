from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import AdventuringGuild
from .forms import AdventuringGuildForm

class AdventuringGuildListView(ListView):
    model = AdventuringGuild
    template_name = 'adventuring_guild_list.html'
    context_object_name = 'guilds'

class AdventuringGuildDetailView(DetailView):
    model = AdventuringGuild
    template_name = 'adventuring_guild_detail.html'
    context_object_name = 'guild'

class AdventuringGuildCreateView(CreateView):
    model = AdventuringGuild
    form_class = AdventuringGuildForm
    template_name = 'adventuring_guild_form.html'
    success_url = reverse_lazy('guild_list')

class AdventuringGuildUpdateView(UpdateView):
    model = AdventuringGuild
    form_class = AdventuringGuildForm
    template_name = 'adventuring_guild_form.html'
    success_url = reverse_lazy('guild_list')

class AdventuringGuildDeleteView(DeleteView):
    model = AdventuringGuild
    template_name = 'adventuring_guild_confirm_delete.html'
    success_url = reverse_lazy('guild_list')
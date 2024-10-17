from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.apps import apps

Note = apps.get_model("notes", "Note")


class NotesListView(ListView):
    model = Note
    template_name = "notes/notes_list.html"
    context_object_name = "notes"

    def get_queryset(self):
        return Note.objects.filter(author=self.request.user)


class NoteDetailView(DetailView):
    model = Note
    template_name = "notes/note_detail.html"
    context_object_name = "note"

    def get_object(self, queryset=None):
        return get_object_or_404(Note, slug=self.kwargs["slug"])


class NoteCreateView(LoginRequiredMixin, CreateView):
    model = Note
    fields = ["title", "text"]
    template_name = "notes/note_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class NoteUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Note
    fields = ["title", "text"]
    template_name = "notes/note_form.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Note, slug=self.kwargs["slug"])

    def test_func(self):
        note = self.get_object()
        return self.request.user == note.author


class NoteDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Note
    template_name = "notes/note_confirm_delete.html"
    success_url = reverse_lazy("notes")

    def get_object(self, queryset=None):
        return get_object_or_404(Note, slug=self.kwargs["slug"])

    def test_func(self):
        note = self.get_object()
        return self.request.user == note.author


@login_required
def note_edit(request, slug):
    note = get_object_or_404(Note, slug=slug)
    if request.user != note.author:
        return redirect("home")
    if request.method == "POST":
        note.title = request.POST.get("title")
        note.text = request.POST.get("text")
        note.save()
        return redirect("note_detail", slug=note.slug)
    return render(request, "notes/note_form.html", {"note": note})

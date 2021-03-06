# -*- coding: utf-8 -*-
import django
if django.VERSION >= (1, 10):
    from django.urls import reverse, reverse_lazy
else:
    from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView, DeleteView
from django.http import Http404

from planet.models import Blog, Feed, Author, Post
from planet.forms import SearchForm

from tagging.models import Tag, TaggedItem
from django.contrib.messages.views import SuccessMessageMixin



def index(request):
    posts = Post.site_objects.all().order_by("-date_modified")

    return render(request, "planet/posts/list.html", {"posts": posts})


def blogs_list(request):
    blogs_list = Blog.site_objects.all()

    return render(request, "planet/blogs/list.html",{"blogs_list": blogs_list})


def blog_detail(request, blog_id, slug=None):
    blog = get_object_or_404(Blog, pk=blog_id)

    if slug is None:
        return redirect(blog, permanent=True)

    posts = Post.site_objects.filter(feed__blog=blog).order_by("-date_modified")

    return render(request, "planet/blogs/detail.html",{"blog": blog, "posts": posts})


def feeds_list(request):
    feeds_list = Feed.site_objects.all()

    return render(request, "planet/feeds/list.html",{"feeds_list": feeds_list})


def feed_detail(request, feed_id, tag=None, slug=None):
    feed = get_object_or_404(Feed, pk=feed_id)

    if not slug:
        return redirect(feed, permanent=True)

    if tag:
        tag = get_object_or_404(Tag, name=tag)

        posts = TaggedItem.objects.get_by_model(
            Post.site_objects, tag).filter(feed=feed).order_by("-date_modified")
    else:
        posts = Post.site_objects.filter(feed=feed).order_by("-date_modified")

    return render(request, "planet/feeds/detail.html",{"feed": feed, "posts": posts, "tag": tag})


def authors_list(request):
    authors = Author.site_objects.all()

    return render(request, "planet/authors/list.html",{"authors_list": authors})


def author_detail(request, author_id, tag=None, slug=None):
    author = get_object_or_404(Author, pk=author_id)

    if not slug:
        return redirect(author, permanent=True)

    if tag:
        tag = get_object_or_404(Tag, name=tag)

        posts = TaggedItem.objects.get_by_model(Post.site_objects, tag).filter(
            authors=author).order_by("-date_modified")
    else:
        posts = Post.site_objects.filter(
            authors=author).order_by("-date_modified")

    return render(request, "planet/authors/detail.html",{"author": author, "posts": posts, "tag": tag})


def posts_list(request):
    posts = Post.site_objects.all().select_related("feed", "feed__blog")\
        .prefetch_related("authors").order_by("-date_modified")

    return render(request, "planet/posts/list.html", {"posts": posts})


def post_detail(request, post_id, slug=None):
    post = get_object_or_404(
        Post.objects.select_related("feed", "feed__blog").prefetch_related("authors"),
        pk=post_id
    )

    if not slug:
        return redirect(post, permanent=True)

    return render(request, "planet/posts/detail.html", {"post": post})


def tag_detail(request, tag):
    tag = get_object_or_404(Tag, name=tag)

    posts = TaggedItem.objects.get_by_model(
        Post.site_objects, tag).order_by("-date_modified")

    return render(request, "planet/tags/detail.html", {"posts": posts,"tag": tag})


def tag_authors_list(request, tag):
    tag = get_object_or_404(Tag, name=tag)

    posts_list = TaggedItem.objects.get_by_model(Post.site_objects, tag)

    authors = set()
    for post in posts_list:
        for author in post.authors.all():
            authors.add(author)

    return render(request, "planet/authors/list_for_tag.html",
        {"authors": list(authors), "tag": tag})


def tag_feeds_list(request, tag):
    tag = get_object_or_404(Tag, name=tag)

    post_ids = TaggedItem.objects.get_by_model(Post.site_objects, tag
        ).values_list("id", flat=True)

    feeds_list = Feed.site_objects.filter(post__in=post_ids).distinct()

    return render(request, "planet/feeds/list_for_tag.html",{"feeds_list": feeds_list, "tag": tag})


def tags_cloud(request, min_posts_count=1):

    tags_cloud = Tag.objects.cloud_for_model(Post)

    return render(request, "planet/tags/cloud.html", {"tags_cloud": tags_cloud})


def foaf(request):
    # TODO: use http://code.google.com/p/django-foaf/ instead of this
    feeds = Feed.site_objects.all().select_related("blog")

    return render(request, "planet/microformats/foaf.xml", {"feeds": feeds}, content_type="text/xml")


def opml(request):
    feeds = Feed.site_objects.all().select_related("blog")

    return render(request, "planet/microformats/opml.xml", {"feeds": feeds}, content_type="text/xml")


def search(request):
    if request.method == "GET" and request.GET.get("search") == "go":
        search_form = SearchForm(request.GET)

        if search_form.is_valid():
            query = search_form.cleaned_data["q"]

            if search_form.cleaned_data["w"] == "posts":
                params_dict = {"title__icontains": query}

                posts = Post.site_objects.filter(**params_dict
                    ).distinct().order_by("-date_modified")

                return render(request, "planet/posts/list.html",
                    {"posts": posts})

            elif search_form.cleaned_data["w"] == "tags":
                params_dict = {"name__icontains": query}

                tags_list = Tag.objects.filter(**params_dict
                    ).distinct().order_by("name")

                return render(request, "planet/tags/list.html",
                    {"tags_list": tags_list})

            elif search_form.cleaned_data["w"] == "blogs":
                params_dict = {"title__icontains": query}

                blogs_list = Blog.site_objects.filter(**params_dict
                    ).order_by("title")

                return render(request, "planet/blogs/list.html",
                    {"blogs_list": blogs_list})

            elif search_form.cleaned_data["w"] == "feeds":
                params_dict = {"title__icontains": query}

                feeds_list = Feed.site_objects.filter(**params_dict
                    ).order_by("title")

                return render(request, "planet/feeds/list.html",
                    {"feeds_list": feeds_list})

            elif search_form.cleaned_data["w"] == "authors":
                params_dict = {"name__icontains": query}

                authors_list = Author.site_objects.filter(**params_dict
                    ).order_by("name")

                return render(request, "planet/authors/list.html",
                    {"authors_list": authors_list})

            else:
                return HttpResponseRedirect(reverse("planet_post_list"))

        else:
            return HttpResponseRedirect(reverse("planet_post_list"))

    else:
        return HttpResponseRedirect(reverse("planet_post_list"))


class FeedAddView(CreateView):
    model = Feed
    template_name = 'planet/feeds/add.html'
    success_message = _("Feed with url=%(url)s was created successfully")
    #success_url =

    def form_valid(self, form):
        from django.contrib import messages
        feed = form.save()
        self.object = feed
        if self.request.user.is_authenticated:
            feed.blog.owner = self.request.user
            feed.blog.save()
        success_message = self.get_success_message(form.cleaned_data)
        if success_message:
            messages.success(self.request, success_message)
        return redirect(self.get_success_url())

    def get_success_url(self):
        if self.request.user.is_authenticated:
            return reverse("planet_blog_list_by_user")
        else:
            return reverse("planet_index")


    def get_success_message(self, cleaned_data):
        return self.success_message % cleaned_data


class BlogListByUserView(ListView):
    template_name = 'planet/blogs/list_by_user.html'
    model = Blog

    def get_queryset(self):
        return Blog.objects.filter(owner=self.request.user)


class OwnedObjectMixin(SingleObjectMixin):
    """
    An object that needs to verify current user ownership
    before allowing manipulation.

    From https://github.com/PyAr/pyarweb/blob/b4095c5c1b474a207e45918683de400974f6a739/community/views.py#L43
    """

    def get_object(self, *args, **kwargs):
        obj = super(OwnedObjectMixin, self).get_object(*args, **kwargs)

        try:
            if not obj.owner == self.request.user:
                raise Http404()
        except AttributeError:
            pass

        return obj


class BlogDeleteView(DeleteView, OwnedObjectMixin):
    template_name = 'planet/blogs/confirm_delete.html'
    model = Blog
    success_url = reverse_lazy('planet_blog_list_by_user')

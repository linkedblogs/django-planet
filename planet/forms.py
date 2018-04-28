# -*- coding: utf-8 -*-
"""
"""

from django import forms
from django.utils.translation import ugettext as _
from django.forms import ModelForm
from .models import Feed
from django.forms import ValidationError, URLField

SEARCH_CHOICES = (
    ("posts", _("Posts")),
    ("tags", _("Tags")),
    ("blogs", _("Blogs")),
    ("authors", _("Authors")),
    ("feeds", _("Feeds")),
)


class SearchForm(forms.Form):
    w = forms.ChoiceField(choices=SEARCH_CHOICES, label="")
    q = forms.CharField(max_length=100, label="")


class FeedAddForm(ModelForm):
    class Meta:
        model = Feed
        fields = ["url"]

    def clean_url(self):
        url = self.cleaned_data['url']
        if Feed.objects.filter(url=url).count() > 0:
            raise ValidationError(_('A feed with this URL already exists.'))
        import feedparser as fp
        feed = fp.parse(url)
        try:
            a = feed.feed.link
        except (AttributeError, KeyError):
            raise ValidationError(_('This is not a feed address. Did you submit the blog address instead of feed location?'))
        return url

import urllib
import urllib.request
from urllib.parse import urlparse
from urllib.error import HTTPError
from planet.settings import PLANET_CONFIG


class AuthorizedFeedAddForm(FeedAddForm):
    testurl = URLField()
    class Meta:
        model = Feed
        fields = FeedAddForm.Meta.fields + ['testurl',]

    def clean_testurl(self):
        testurl = self.cleaned_data['testurl']
        if 'url' in self.cleaned_data:
            url = self.cleaned_data['url']
        else:
            raise ValidationError(_('A feed with this URL already exists.'))
        o1 = urlparse(url)
        o2 = urlparse(testurl)
        if o1.netloc != o2.netloc:
            raise ValidationError(_("The feed domain must be the same as the test url domain!"))
        try:
            urllib.request.urlopen(testurl)
        except HTTPError as error:
            if error.code == 404:
               text = _("The test url does not seem to exist!")
            else:
                text = _("An unspecified network error occurred; please try later...")
            raise ValidationError(text)
        token = PLANET_CONFIG.get("TOKEN", "django-planet")
        if not token in o2.path:
            raise ValidationError(_("The test url does not contain the token!"))

        return testurl






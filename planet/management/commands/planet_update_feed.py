#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from planet.tasks import process_feed


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('feed_url', nargs='?', type=str)

    def handle(self, *args, **options):
        feed_url = options.get('feed_url', None)
        if not feed_url:
            print("You must provide the feed url as parameter")
            exit(0)


        # process feed in create-mode
        process_feed.delay(feed_url, create=False)

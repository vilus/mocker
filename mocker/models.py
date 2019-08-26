import datetime

from django.utils import timezone
from django.db import models, transaction
from django.db.models import Q, QuerySet, Model
from django.contrib.postgres.fields import JSONField


TTL = 120
ANY = '*'
CYCLE = 'cycle'
SEQUENCE = 'sequence'


class DupError(ValueError):
    pass


class Lock(Model):
    name = models.CharField(max_length=16, primary_key=True)

    def __str__(self):
        return f'{self.name}'


class MockQuerySet(QuerySet):

    def not_expired(self):
        return self.filter(expired__gt=timezone.now())

    def overlapped(self, host, route, method):
        qs = self.not_expired()

        if host != ANY:
            qs = qs.filter(host__in=(host, ANY))

        if route != ANY:
            qs = qs.filter(route__in=(route, ANY))

        if method != ANY:
            qs = qs.filter(method__in=(method, ANY))

        return qs

    def not_by_response(self, responses, response_type):
        return self.filter(~Q(response_type=response_type, responses=responses) | Q(is_exclusive=True))

    def by_response(self, responses, response_type):
        return self.filter(response_type=response_type, responses=responses)

    def get_by(self, host, route, method):
        matched_mocks = self.not_expired().filter(
            host__in=(host, ANY), route__in=(route, ANY), method__in=(method, ANY)
        ).order_by('responses').distinct('responses')

        if matched_mocks.count() > 1:
            raise DupError('Can\'t determine mock, '
                           f'matched ones has different responses: {list(matched_mocks[:10])}')

        return matched_mocks.first()

    @transaction.atomic
    def create(self, route, method, responses, name=ANY, ttl=TTL, host=ANY, response_type=SEQUENCE, is_exclusive=False):  # TODO: hardcode
        Lock.objects.select_for_update().get_or_create(name='Mock')

        overlapped = self.overlapped(host, route, method).not_by_response(responses, response_type)
        if overlapped.exists():
            raise DupError('Can\'t to create mock, '
                           f'try again later, please (overlapped {list(overlapped[:10])})')

        overlapped = self.overlapped(host, route, method).by_response(responses, response_type)
        if overlapped.exists() and is_exclusive:
            raise DupError('Can\'t to create exclusive mock, '
                           f'try again later, please (overlapped {list(overlapped[:10])})')

        # noinspection PyArgumentList
        mock = super().create(name=name, ttl=ttl, host=host, route=route, method=method,
                              responses=responses, response_type=response_type, is_exclusive=is_exclusive)

        return mock


class Mock(Model):
    name = models.CharField(max_length=128, blank=True, default=ANY)
    created = models.DateTimeField(auto_now_add=True)
    expired = models.DateTimeField(null=True, blank=True)
    ttl = models.PositiveIntegerField(default=TTL)
    is_exclusive = models.BooleanField(default=False)
    # --
    host = models.CharField(max_length=120, default=ANY)
    route = models.CharField(max_length=120, default=ANY)
    method = models.CharField(max_length=120, default=ANY)
    # --
    responses = JSONField()
    response_type = models.CharField(max_length=20,
                                     choices=((CYCLE, CYCLE), (SEQUENCE, SEQUENCE)),
                                     default=SEQUENCE)

    objects = MockQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if not self.expired:
            self.expired = timezone.now() + datetime.timedelta(seconds=self.ttl)
        # noinspection PyArgumentList
        super().save(*args, **kwargs)

    def is_expired(self):
        return self.expired < timezone.now()

    def __str__(self):
        return f'{self.name}, id: {self.pk}, expired: {self.expired}'

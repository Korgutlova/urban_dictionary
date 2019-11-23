from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

ROLE_CHOICES = (
    (1, 'Пользователь'),
    (2, 'Модератор'),
    (3, 'Администратор'),
)
STATUSES = (
    (1, "Активный"),
    (2, "Заблокированный"),
    (3, "Неподтвержденная регистрация")
)

STATUSES_FOR_REQUESTS = (
    (1, "Новый"),
    (2, "Отклонен"),
    (3, "Опубликован"),
    (4, "Навсегда отклонен")
)

ESTIMATE = (
    (1, "Like"),
    (2, "Dislike"),
)


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="custom_user")
    description = models.TextField(verbose_name="О себе")
    email = models.CharField(max_length=50, verbose_name="Почта")
    role = models.IntegerField(choices=ROLE_CHOICES, blank=False, null=False, default=ROLE_CHOICES[0][0],
                               verbose_name="Роль")
    date_registration = models.DateTimeField(auto_now_add=True, blank=False, verbose_name="Дата регистрации")
    status = models.IntegerField(choices=STATUSES, blank=False, null=False, default=STATUSES[2][0],
                                 verbose_name="Статус")

    # link_photo

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        CustomUser.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.custom_user.save()


class Term(models.Model):
    name = models.CharField(max_length=200, verbose_name="Термин", unique=True)

    def __str__(self):
        return self.name


class Definition(models.Model):
    term = models.ForeignKey(Term, related_name='definitions', on_delete=models.CASCADE,
                             blank=False, null=False, verbose_name='Термин')
    description = models.TextField(verbose_name="Описание термина")
    examples = models.TextField(verbose_name="Примеры использования")
    date = models.DateTimeField(blank=True, verbose_name="Дата публикации", null=True)
    author = models.ForeignKey(CustomUser, related_name='definitions', on_delete=models.SET_NULL,
                               blank=True, null=True, verbose_name='Автор')
    source = models.TextField(verbose_name="Ссылка на источник/первоисточник", default=None)

    def __str__(self):
        return "Определение %s - автор %s" % (self.term, self.author)


class UploadData(models.Model):
    definition = models.ForeignKey(Definition, related_name='files', on_delete=models.CASCADE,
                                   blank=False, null=False, verbose_name='Ссылка на определение')
    header_for_file = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField()

    def __str__(self):
        return '%s - %s - %s' % (
            self.definition, self.header_for_file, self.image.url)


class RequestForPublication(models.Model):
    definition = models.ForeignKey(Definition, related_name='requests', on_delete=models.CASCADE,
                                   blank=False, null=False, verbose_name='Ссылка на определение')
    status = models.IntegerField(choices=STATUSES_FOR_REQUESTS, blank=False, null=False,
                                 default=STATUSES_FOR_REQUESTS[0][0],
                                 verbose_name="Статус публикации")
    reason = models.TextField(verbose_name="Причина отклонения", blank=False)

    old_request = models.ForeignKey("self", blank=True, null=True, verbose_name="Старый запрос на публикацию",
                                    on_delete=models.SET_NULL)

    date_creation = models.DateTimeField(auto_now_add=True, blank=False, verbose_name="Дата создания запроса")

    def __str__(self):
        return "Запрос на публикацию определения %s" % self.definition


class Comment(models.Model):
    definition = models.ForeignKey(Definition, related_name='comments', on_delete=models.CASCADE,
                                   blank=False, null=False, verbose_name='Ссылка на определение')
    other_comment = models.ForeignKey("self", blank=True, null=True, verbose_name="Корневой комментарий",
                                      on_delete=models.CASCADE)

    text = models.TextField(verbose_name="Комментарий", blank=False)

    date_creation = models.DateTimeField(auto_now_add=True, blank=False, verbose_name="Дата")

    author = models.ForeignKey(CustomUser, related_name='comments', on_delete=models.CASCADE,
                               blank=False, null=False, verbose_name='Автор комментария')

    def __str__(self):
        return "Комментарий %s от %s " % (self.text, self.author)


class Estimate(models.Model):
    definition = models.ForeignKey(Definition, related_name='estimates', on_delete=models.CASCADE,
                                   blank=False, null=False, verbose_name='Ссылка на определение')
    user = models.ForeignKey(CustomUser, related_name='estimates', on_delete=models.CASCADE,
                             blank=False, null=False, verbose_name='Пользователь')
    estimate = models.IntegerField(choices=ESTIMATE, blank=False, null=False,
                                   default=ESTIMATE[0][0],
                                   verbose_name="Оценка")

    def __str__(self):
        return "%s определения %s от %s " % (self.estimate, self.definition, self.user)


class Blocking(models.Model):
    user = models.OneToOneField(CustomUser, related_name='blocking', on_delete=models.CASCADE,
                                blank=False, null=False, verbose_name='Пользователь')
    reason = models.TextField(verbose_name="Причина блокировки", blank=False)
    date_creation = models.DateTimeField(auto_now_add=True, blank=False, verbose_name="Дата создания блокировки")
    expiration_date = models.DateTimeField(blank=True, null=True, verbose_name="Дата истекания блокировки")

    def __str__(self):
        return "Блокировка пользователя %s" % self.user


class Favorites(models.Model):
    definition = models.ForeignKey(Definition, related_name='favorites', on_delete=models.CASCADE,
                                   blank=False, null=False, verbose_name='Ссылка на определение')
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE,
                             blank=False, null=False, verbose_name='Ссылка на пользователя')

    def __str__(self):
        return "Избранное пользователя %s - %s " % (self.user, self.definition)


class Notification(models.Model):
    info = models.TextField(verbose_name="Текст уведомления", blank=False)
    date_creation = models.DateTimeField(auto_now_add=True, blank=False, verbose_name="Дата уведомления")
    action_id = models.CharField(max_length=30, verbose_name="ID события")
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE,
                             blank=False, null=False, verbose_name='Ссылка на пользователя')

    def __str__(self):
        return "Уведомление %s пользователя %s" % (self.info, self.user)

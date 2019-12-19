DEF = "DEF"
SUPPORT = "SUPPORT"
USER = "USER"

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

RATING_VALUES = (
    (0, "Dislike"),
    (1, "Like"),
)

ACTION_TYPES = (
    (0, "Dislike"),  # user_id def_id
    (1, "Like"),  # user_id def_id
    (2, "Notify update status"),
    (3, "Status has updated"),  # def_id
    (4, "Def was checked by admin"),  # def_id
    (5, "Def was rejected by admin"),  # def_id
    (6, "Def was published"),  # def_id
    (7, "Block"),
    (8, "Unblock by admin"),
    (9, "Unblock (time)"),
    (10, "Def was added in favorites by smb"),  # user_id  def_id
    (11, "Support respond on the email"),  # id on request
)

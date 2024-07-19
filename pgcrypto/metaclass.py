from django.db import models

from pgcrypto.fields import EncryptedCustomTextField


class PIIModel(models.Model):
    class Meta:
        abstract = True

    PII_FIELDS: tuple[str, ...] = tuple()

    def __init_subclass__(cls, **kwargs: dict):
        super().__init_subclass__(**kwargs)
        for field in cls.PII_FIELDS:
            setattr(
                cls,
                f"as_{field}",
                property(cls.make_getter(field), cls.make_setter(field)),
            )

    @staticmethod
    def make_getter(field: str):
        def getter(self):
            return EncryptedCustomTextField().to_python(
                getattr(self, field), self.cipher_key
            )

        return getter

    @staticmethod
    def make_setter(field):
        def setter(self, value):
            setattr(
                self,
                field,
                EncryptedCustomTextField().get_db_prep_save(
                    value, None, self.cipher_key
                ),
            )

        return setter

    @property
    def as_cipher_key(self):
        return self.cipher_key

    @as_cipher_key.setter
    def as_cipher_key(self, value):
        self.cipher_key = value

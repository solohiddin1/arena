from modeltranslation.translator import register, TranslationOptions
from apps.posts.models import Category, Amenity


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('title',)


@register(Amenity)
class AmenityTranslationOptions(TranslationOptions):
    fields = ('title',)

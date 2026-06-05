"""Category icon URL helper."""
from django.templatetags.static import static

# Only PROWEB categories that have icons
CATEGORY_ICONS = {
    'data_analyst': 'icons/Data Analyst 2.png',
    'data_science': 'icons/Data Sciense.png',
    'mobilograf': 'icons/мобилография.png',
    'smm': 'icons/pro smm.png',
    'graphic_design': 'icons/Motion design & Видеомонтаж.png',
    '3d_max': 'icons/3ds max & autocad.png',
    'blender': 'icons/blender.png',
    'python': 'icons/python.png',
    'frontend': 'icons/веб программирование.png',
    'ms_office': 'icons/mc office.png',
}


def get_category_icon_url(slug):
    """Get static URL for a category icon."""
    icon_path = CATEGORY_ICONS.get(slug)
    if icon_path:
        return static(icon_path)
    return None


def annotate_with_icons(categories):
    """Add icon_url attribute to each category in a queryset."""
    result = []
    for cat in categories:
        cat.icon_url = get_category_icon_url(cat.slug)
        result.append(cat)
    return result

from django import template

register = template.Library()

@register.filter(name="star_rating")
def star_rating(value):
    try:
        # Extract the numeric value from the string
        rating_parts = value.split()
        if len(rating_parts) >= 1:
            rating = float(rating_parts[0])
            full_stars = int(rating)
            half_stars = 1 if rating % 1 >= 0.5 else 0
            empty_stars = 5 - full_stars - half_stars

            stars = {
                "full_stars": range(full_stars),
                "half_stars": half_stars,
                "empty_stars": range(empty_stars),
            }

            return stars
    except (ValueError, IndexError):
        return None

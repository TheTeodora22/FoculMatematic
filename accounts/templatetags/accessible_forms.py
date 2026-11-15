from django import template

register = template.Library()


@register.simple_tag
def accessible_field(field, client_errors=True):
    """Render the existing widget with server-side descriptions; keep validation unchanged."""
    attrs = {}
    descriptions = field.field.widget.attrs.get("aria-describedby", "").split()
    identifier = field.id_for_label
    if identifier:
        if field.help_text:
            descriptions.append(f"{identifier}_help")
        if field.errors:
            descriptions.append(f"{identifier}_errors")
        if client_errors:
            descriptions.append(f"{identifier}_client_error")
    if descriptions:
        attrs["aria-describedby"] = " ".join(dict.fromkeys(descriptions))
    if field.errors:
        attrs["aria-invalid"] = "true"
    purposes = {
        "first_name": "given-name", "last_name": "family-name", "username": "username",
        "password": "current-password", "password1": "new-password", "password2": "new-password",
        "email": "email",
    }
    if field.name in purposes and "autocomplete" not in field.field.widget.attrs:
        attrs["autocomplete"] = purposes[field.name]
    return field.as_widget(attrs=attrs)

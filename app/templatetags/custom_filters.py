from django import template

register = template.Library()

@register.filter
def add_commas(value):
    """Định dạng số bằng cách thêm dấu phẩy làm dấu phân cách hàng nghìn."""
    try:
        # Chuyển giá trị thành float và sau đó định dạng với dấu phẩy
        return '{:,}'.format(float(value))
    except (ValueError, TypeError):
        # Trả lại giá trị gốc nếu không phải là số hợp lệ
        return value

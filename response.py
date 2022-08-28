import string


def make_response(tag, context, code=200) -> string:
    obj = {
        'tag': tag,
        'context': context,
        'code': code
    }

    response = str(obj).replace("\'", "\"")
    return response, code

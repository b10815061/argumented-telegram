import string
import json

def make_response(tag, context, code=200) -> string:
    obj = {
        'tag': tag,
        'context': context,
        'code': code
    }

    response = json.dumps(obj, ensure_ascii=False)
    return response, code

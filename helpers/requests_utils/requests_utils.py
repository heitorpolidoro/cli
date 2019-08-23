import json
# TODO usar o inspect.signature para passar o kwargs direto removendo os argumentos que não tem no post/get


class Requests(object):
    """
    Wrapper to requests to replace '${NAME}' with value in named arguments or environment variable value

    Requests.get('http://${URL}', url='bla.com')
    - request to url "http://bla.com"

    Or if there is a environment variable URL='site.com'
    Requests.get('http://${URL}')
    - request to url "http://site.com"
    """
    @staticmethod
    def post(url, *args, headers=None, files=None, **kwargs):
        import requests
        from helpers.utils import template_safe_substitute

        response = requests.post(template_safe_substitute(url, **kwargs),
                                 *template_safe_substitute(args, **kwargs),
                                 headers=template_safe_substitute(headers, **kwargs),
                                 files=template_safe_substitute(files, **kwargs),
                                 )
        response.raise_for_status()
        return response

    @staticmethod
    def get(url, *args, headers=None, **kwargs):
        import requests
        from helpers.utils import template_safe_substitute

        response = requests.get(template_safe_substitute(url, **kwargs),
                                *template_safe_substitute(args, **kwargs),
                                headers=template_safe_substitute(headers, **kwargs))
        response.raise_for_status()
        return response

    @staticmethod
    def get_content(url, *args, clazz=None, **kwargs):
        """
        Make a get request and return only the content.
        If class is not None return an instance of class with the content values
        """
        response = Requests.get(url, *args, **kwargs)
        if response.content:
            # If there is a contente, convert to JSON
            response_json = json.loads(response.content)
            if response_json:
                if isinstance(response_json, list):
                    final_response = response_json
                    if clazz is not None:
                        final_response = []
                        for j in response_json:
                            instance = clazz()
                            vars(instance).update(j)
                            final_response.append(instance)

                    if len(response_json) == 1:
                        return final_response[0]
                    else:
                        return final_response
            return response_json

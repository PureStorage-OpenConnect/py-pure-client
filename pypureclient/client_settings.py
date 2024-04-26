USER_AGENT_TEMPLATE = 'pypureclient/1.50.0/{prod}/{rest_version}/{sys}/{rel}'

def resolve_ssl_validation(verify_ssl):
    """
        Translates verify_ssl parameter of py-pure-client to verify parameter of the requests package
    """
    return verify_ssl if verify_ssl is not None else False

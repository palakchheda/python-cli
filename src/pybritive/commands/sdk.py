import click
from ..helpers.build_britive import build_britive
from ..options.britive_options import britive_options


@click.command(
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True
    )
)
@build_britive
@britive_options(names='query,output_format,tenant,token,passphrase,federation_provider')
@click.argument('method')
def sdk(ctx, query, output_format, tenant, token, passphrase, federation_provider, method):
    """Exposes the Britive Python SDK methods to the CLI.

    Documentation on each SDK method can be found inside the Python SDK itself and on Github
    (https://github.com/britive/python-sdk). The Python package `britive` is a dependency of the CLI
    already so the SDK is available without installing any extra packages.

    It is left up to the caller to provide the proper `method` and `parameters` based on the documentation
    of the API call being performed.

    The authenticated identity must have the appropriate permissions to perform the actions being requested.
    General end users of Britive will not have these permissions. This call (and the larger SDK) is generally
    meant for administrative functionality.

    Example of use:

    * pybritive sdk users.list

    * pybritive sdk tags.create --name testtag --description "test tag"

    * pybritive sdk users.list --query '[].email'

    * pybritive sdk profiles.create --application-id <id> --name testprofile

    """
    parameters = {ctx.args[i][2:]: ctx.args[i + 1] for i in range(0, len(ctx.args), 2)}
    ctx.obj.britive.sdk(
        method=method,
        parameters=parameters,
        query=query
    )

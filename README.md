# Celery Flower runner for GOV.UK PaaS

This repo can be used to run [Flower](https://flower.readthedocs.io/en/latest/) on GOV.UK PaaS (or similar environments) as a standalone app (with Redis as a broker).

The following environment variables are supported:

| Name | Required | Description |
| ---- | ------- | ----------- |
| `VCAP_SERVICES` |  | Set by GOV.UK PaaS. Redis connection details will be read from this variable if it is set. |
| `REDIS_BASE_URL` | If `VCAP_SERVICES` is not set | `redis://` or `rediss://` URL. |
| `REDIS_BROKER_DB` |  | Redis database number to use for the broker (default=0). |
| `EMAIL_WHITELIST` |  | Comma-separated list of allowed email addresses for GitHub and Google authentication. |
| `FLOWER_*` |  | [Any Flower configuration option](https://flower.readthedocs.io/en/latest/config.html). |

Authentication **must** be configured using the `FLOWER_AUTH_PROVIDER` or `FLOWER_BASIC_AUTH` environment variables (or the app won‘t start).

If using GitHub or Google authentication, you must also configure an email whitelist using the `EMAIL_WHITELIST` environment variable (and should not use `FLOWER_AUTH`).

Note that the broker tab in Flower will not work if using Redis over TLS.

"""CRDCH Integration: Refresh CCDH model functionality

This is used by a GitHub action which rebuilds ccdh-terminology-service and
follows up by initiating a refresh of the CCDH model which depends on it.
"""
import logging
import sys

import requests

from ccdh.config import get_settings


logger = logging.getLogger('ccdh.integrations.crdc_h')


def trigger_refresh():
    """Triggers refresh in the CCDH model."""
    logger.info('Requesting refresh of CCDH Model.')
    token: str = get_settings().docker_user_token_limited
    if not token:
        logger.error('Error: Attempted to trigger update in CCDH Model repository, '
            'but "DOCKER_USER_TOKEN_LIMITED" was not found in environment.',
            file=sys.stderr)
    else:
        r = requests.post(
            'https://api.github.com/repos/cancerDHC/ccdhmodel/dispatches',
            headers={
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            json={
                "event_type": "refreshModel"
            })
        if r.status_code >= 400:  # errors defined as codes 400 and above
            logger.error(
                'Error: Triggering update in CCDH Model repository failed.\n',
                'Status code: ', r.status_code, '\n'
                'Reason: ', r.reason, '\n'
                'Response text: ', r.text,
                file=sys.stderr)
        else:
            logger.info('Success.')


if __name__ == '__main__':
    trigger_refresh()

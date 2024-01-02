import argparse
import logging
import logging.config
import yaml
from nodes.utils import StravaAPIConnector, BigQueryConnector
from transformers.extract_load import StravaEL

def main():
    """
    Entry point to run the Strava EL job.
    """
    # parsing YML file
    parser = argparse.ArgumentParser(description='Run the Strava EL Job.')
    parser.add_argument('config', help='A configuration file in YAML format.')
    args = parser.parse_args()

    config = yaml.safe_load(open(args.config))

    # configure logging
    log_config = config['logging']
    logging.config.dictConfig(log_config)

    # initialize StravaAPIConnector class
    STRAVA_AUTH_URL = config['strava_api']['STRAVA_AUTH_URL']
    STRAVA_ACTIVITIES_URL = config['strava_api']['STRAVA_ACTIVITIES_URL']
    STRAVA_PAYLOAD = config['strava_api']['STRAVA_PAYLOAD']

    sac = StravaAPIConnector(STRAVA_AUTH_URL, STRAVA_ACTIVITIES_URL, STRAVA_PAYLOAD)

    # intialize StravaEL class
    sel = StravaEL(sac.strava_auth_url, sac.strava_activities_url, sac.strava_payload, 2, 200)

    # initlaize BigQueryConnector class
    SERVICE_ACCOUNT_JSON = config['bigquery']['SERVICE_ACCOUNT_JSON']
    bqc = BigQueryConnector(service_account_json=SERVICE_ACCOUNT_JSON)

    # run
    logger = logger = logging.getLogger(__name__)
    logger.info('Starting EL job.')
    sel.load(bqc, 'strava-activity.StravaActivities.raw', 200)

if __name__ == '__main__':
    main()

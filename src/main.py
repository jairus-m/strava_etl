import argparse
import logging
import logging.config
import yaml
from nodes.utils import StravaAPIConnector, BigQueryConnector

from transformers.strava_etl import StravaETL

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

     # intialize StravaETL class
    pages = config['strava_api']['pages']
    num_activities = config['strava_api']['num_activities']
    cols_to_drop = config['strava_api']['cols_to_drop']

    sel = StravaETL(sac.strava_auth_url, sac.strava_activities_url, sac.strava_payload, pages, num_activities, cols_to_drop)

    # initlaize BigQueryConnector class
    SERVICE_ACCOUNT_JSON = config['bigquery']['SERVICE_ACCOUNT_JSON']
    bqc = BigQueryConnector(service_account_json=SERVICE_ACCOUNT_JSON)

    # run
    logger = logging.getLogger(__name__)
    logger.info('Starting ETL job.')

    project_name = config['bigquery']['project']
    dataset_name = config['bigquery']['dataset']
    table_name = config['bigquery']['table']

    table_id = ".".join([project_name, dataset_name, table_name])

    sql_query = f"""
    SELECT DISTINCT id, name, start_date
    FROM {table_id}
    ORDER BY start_date DESC
    LIMIT 50;
    """
    # load updated data
    sel.load(bqc, project_name, dataset_name, table_name, num_activities, sql_query)
    logger.info('ETL job complete.')
    
if __name__ == '__main__':
    main()

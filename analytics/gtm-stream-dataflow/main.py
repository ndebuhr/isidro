import json

import apache_beam as beam

from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.trigger import AccumulationMode, AfterProcessingTime, AfterWatermark, Repeatedly
from apache_beam.transforms.window import SlidingWindows

class StreamOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_argument(
            '--table',
            help='TODO'
        )
        parser.add_argument(
            '--topic',
            help='TODO'
        )
        parser.add_argument(
            '--website_origin',
            help='TODO'
        )
        parser.add_argument(
            '--report_bucket',
            help='TODO'
        )
        parser.add_argument(
            '--report_blob',
            help='TODO'
        )


options = StreamOptions(
    runner='DataflowRunner',
    region='us-central1',
    streaming=True,
)

table_schema = {
    'fields': [
        {'name': 'container_id', 'type': 'STRING'},
        {'name': 'container_version', 'type': 'STRING'},
        {'name': 'cookie_enabled', 'type': 'BOOL'},
        {'name': 'debug_mode', 'type': 'BOOL'},
        {'name': 'environment_name', 'type': 'STRING'},
        {'name': 'event', 'type': 'STRING'},
        {'name': 'language', 'type': 'STRING'},
        {'name': 'languages', 'type': 'STRING', 'mode': 'REPEATED'},
        {'name': 'online', 'type': 'BOOL'},
        {'name': 'page_hostname', 'type': 'STRING'},
        {'name': 'page_path', 'type': 'STRING'},
        {'name': 'page_url', 'type': 'STRING'},
        {'name': 'random_number', 'type': 'INT64'},
        {'name': 'referrer', 'type': 'STRING'},
        {'name': 'scroll_x', 'type': 'FLOAT64'},
        {'name': 'scroll_y', 'type': 'FLOAT64'},
        {'name': 'timestamp', 'type': 'TIMESTAMP'},
        {'name': 'user_agent', 'type': 'STRING'}
    ]
}

class TopFivePagesFn(beam.CombineFn):
    def __init__(self, options):
        self.options = options

    def setup(self):
        from collections import Counter
        from google.cloud import storage

        self.Counter = Counter

        storage_client = storage.Client()
        bucket = storage_client.bucket(self.options.report_bucket)
        self.blob = bucket.blob(self.options.report_blob)

    def create_accumulator(self):
        return self.Counter()

    def add_input(self, counter, page):
        counter[page] += 1
        return counter

    def merge_accumulators(self, counters):
        return sum(counters, self.Counter())

    def extract_output(self, counter):
        with self.blob.open("w") as f:
            f.write(
                json.dumps([top_page for top_page, _ in counter.most_common(5)])
            )
        return None


with beam.Pipeline(options=options) as pipeline:
    hostname = options.website_origin.replace("https://", "").replace("http://", "")
    # Ingest data as JSON
    ingestion = pipeline \
        | 'StreamFromPubSub' >> beam.io.ReadFromPubSub(topic=options.topic) \
        | 'DeserializeJson' >> beam.Map(json.loads)
    # Stream data into BigQuery (10 second windowing)
    ingestion \
        | 'StreamToBigQuery' >> beam.io.WriteToBigQuery(
            options.table,
            schema=table_schema,
            method='STREAMING_INSERTS',
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
        )
    # Setup top pages JSON report with GCS (1 day windowing)
    ingestion \
        | 'FilterByHostname' >> beam.Filter(
            lambda event, hostname=hostname: event["page_hostname"] == hostname
        ) \
        | 'GetPagePath' >> beam.Map(lambda event: event["page_path"]) \
        | 'SlidingWindow24h' >> beam.WindowInto(
            SlidingWindows(24*60*60, 60*60),
            trigger=Repeatedly(AfterWatermark(late=AfterProcessingTime(0))),
            allowed_lateness=60*60,
            accumulation_mode=AccumulationMode.ACCUMULATING
        ) \
        | 'PublishTop5' >> beam.CombineGlobally(TopFivePagesFn(options)).without_defaults()

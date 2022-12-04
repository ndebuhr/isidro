import json
import logging

from collections import Counter
from dateutil.parser import parse as dp
from typing import Iterable

import apache_beam as beam

from apache_beam.transforms.window import SlidingWindows
from google.cloud import storage

from gtm_stream.options import StreamOptions
from gtm_stream.schemas import raw_stream_bq_schema


class TopFivePagesFn(beam.CombineFn):
    def create_accumulator(self):
        return Counter()

    def add_input(self, counter: Counter, page: str) -> Counter:
        counter[page] += 1
        return counter

    def merge_accumulators(self, counters: [Counter]) -> Counter:
        return sum(counters, Counter())

    def extract_output(self, counter: Counter) -> [str]:
        return [top_page for top_page, _ in counter.most_common(5)]


class WriteToGCS(beam.DoFn):
    def __init__(self, options):
        self.options = options

    def setup(self):
        storage_client = storage.Client()
        bucket = storage_client.bucket(self.options.report_bucket)
        self.blob = bucket.blob(self.options.report_blob)

    def process(self, results: [str]) -> None:
        with self.blob.open("w") as f:
            f.write(
                json.dumps(results)
            )

def run(options: StreamOptions):
    """ Main entrypoint; defines and runs the streaming pipeline. """

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
                schema=raw_stream_bq_schema,
                method='STREAMING_INSERTS',
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
            )
        # Setup top pages JSON report with GCS (1 day windowing)
        ingestion \
            | 'FilterByHostname' >> beam.Filter(
                lambda event: event["page_hostname"] == hostname
            ) \
            | 'GetPagePath' >> beam.Map(lambda event: event["page_path"]) \
            | 'SlidingWindow24h' >> beam.WindowInto(SlidingWindows(24*60*60, 60*60)) \
            | 'CompileTop5' >> beam.CombineGlobally(TopFivePagesFn()).without_defaults() \
            | 'WriteToGCS' >> beam.ParDo(WriteToGCS(options))

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    options = StreamOptions(
        runner='DataflowRunner',
        region='us-central1',
        save_main_session=True,
        streaming=True,
    )
    run(options)
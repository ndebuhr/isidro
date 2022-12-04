from apache_beam.options.pipeline_options import PipelineOptions

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
# Isidro Analytics

## Prerequisites

1. Setup Google Analytics 4
1. Establish a Google Analytics BigQuery Export
1. Setup Google Tag Manager

## Setup Cloud Resources

Provision required cloud resources in [/provisioning/analytics](/provisioning/analytics):
```bash
terraform init
terraform apply
export ANALYTICS_BUCKET="$(terraform output --raw bucket_name)"
```

Set the `GOOGLE_PROJECT` environment variable, then create a service account key:
```bash
gcloud iam service-accounts keys create isidro-analytics.json \
    --iam-account="isidro-analytics@$GOOGLE_PROJECT.iam.gserviceaccount.com"
```

Store a variable for the analytics credentials `export GOOGLE_APPLICATION_CREDENTIALS=$PWD/isidro-analytics.json`, export your website domain (with http/https scheme) in the `WEBSITE_ORIGIN` environment variable (like `export WEBSITE_ORIGIN=https://isidro.ai`), then deploy the required Cloud Function and run the Dataflow pipeline:
```bash
cd gtm-stream-functions
gcloud beta functions deploy isidro-gtm-stream \
  --gen2 \
  --runtime=python310 \
  --region=us-central1 \
  --source=. \
  --entry-point=to_pubsub \
  --trigger-http \
  --service-account isidro-analytics-functions@$GOOGLE_PROJECT.iam.gserviceaccount.com \
  --set-env-vars WEBSITE_ORIGIN="$WEBSITE_ORIGIN",GOOGLE_PROJECT="$GOOGLE_PROJECT" \
  --allow-unauthenticated
cd ..
WEBSITE_STREAM_ENDPOINT=$(gcloud beta functions describe isidro-gtm-stream --gen2 --region us-central1 --format="value(serviceConfig.uri)")
cd gtm-stream-dataflow
python3 main.py \
  --setup_file $PWD/setup.py \
  --project "$GOOGLE_PROJECT" \
  --service_account_email "isidro-analytics@$GOOGLE_PROJECT.iam.gserviceaccount.com" \
  --temp_location="gs://$ANALYTICS_BUCKET/dataflow/temp" \
  --table isidro_analytics.events \
  --topic "projects/$GOOGLE_PROJECT/topics/isidro-gtm-stream" \
  --report_bucket="$ANALYTICS_BUCKET" \
  --report_blob="top-pages.json" \
  --website_origin="$WEBSITE_ORIGIN"
cd ..
```

## Setup GTM Configuration

### GTM Trigger

Create a trigger of type timer:
* Event name is `gtm.timer`
* Interval is `1000` (ms)
* Limit is `6000`
* Condition is `Page Hostname` is `equal` to the website's hostname
* Fire on `All Timers`

### GTM Tag

Create a Custom HTML tag in Google Tag Manager.  Replace "WEBSITE_STREAM_ENDPOINT" with the Cloud Functions endpoint (`echo $WEBSITE_STREAM_ENDPOINT`).  Use the previously created trigger for this tag.
```html
<script>
  var headers = new Headers();
  headers.append("Content-Type", "application/json");
  var body = {
    "container_id": "{{Container ID}}",
    "container_version": "{{Container Version}}",
    "debug_mode": {{Debug Mode}},
    "environment_name": "{{Environment Name}}",
    "event": "{{Event}}",
    "page_hostname": "{{Page Hostname}}",
    "page_path": "{{Page Path}}",
    "page_url": "{{Page URL}}",
    "random_number": {{Random Number}},
    "referrer": "{{Referrer}}",
    "cookie_enabled": navigator.cookieEnabled,
    "language": navigator.language,
    "languages": navigator.languages,
    "online": navigator.onLine,
    "user_agent": navigator.userAgent,
    "scroll_x": window.scrollX,
    "scroll_y": window.scrollY,
    "timestamp": (new Date).toISOString()
  };
  var options = {
    method: "POST",
    headers: headers,
    body: JSON.stringify(body)
  };

  fetch("WEBSITE_STREAM_ENDPOINT", options);

</script>
```
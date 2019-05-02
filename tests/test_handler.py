import datetime
from collections import OrderedDict

from moto import mock_cloudwatch
import boto3

from handler import put_metrics, format_response


stats = {
    "downloader/request_bytes": 10055,
    "downloader/request_count": 34,
    "downloader/request_method_count/GET": 34,
    "downloader/response_bytes": 174399,
    "downloader/response_count": 34,
    "downloader/response_status_count/200": 32,
    "downloader/response_status_count/301": 2,
    "finish_reason": "finished",
    "finish_time": datetime.datetime(2019, 4, 8, 11, 49, 32, 717749),
    "item_scraped_count": 30,
    "log_count/DEBUG": 112,
    "log_count/INFO": 9,
    "log_count/WARNING": 1,
    "memusage/max": 76472320,
    "memusage/startup": 76472320,
    "postgresql/add": 30,
    "request_depth_max": 1,
    "response_received_count": 32,
    "robotstxt/request_count": 1,
    "robotstxt/response_count": 1,
    "robotstxt/response_status_count/200": 1,
    "scheduler/dequeued": 32,
    "scheduler/dequeued/memory": 32,
    "scheduler/enqueued": 32,
    "scheduler/enqueued/memory": 32,
    "start_time": datetime.datetime(2019, 4, 8, 11, 49, 22, 841506),
}


@mock_cloudwatch
def test_metrics():
    # put the data
    put_metrics(stats, function_name="mocked-spider")
    # then validate it
    client = boto3.client("cloudwatch")
    assert client.list_metrics()["Metrics"] == [
        {
            "Dimensions": [{"Name": "scraped", "Value": "items"}],
            "MetricName": "mocked-spider/item_scraped_count",
            "Namespace": "spiders",
        },
        {
            "Dimensions": [{"Name": "saved", "Value": "images"}],
            "MetricName": "mocked-spider/file_count",
            "Namespace": "spiders",
        },
        {
            "Dimensions": [{"Name": "added", "Value": "items"}],
            "MetricName": "mocked-spider/postgresql/add",
            "Namespace": "spiders",
        },
        {
            "Dimensions": [{"Name": "modified", "Value": "items"}],
            "MetricName": "mocked-spider/postgresql/modify",
            "Namespace": "spiders",
        },
        {
            "Dimensions": [{"Name": "ignored", "Value": "items"}],
            "MetricName": "mocked-spider/postgresql/ignore",
            "Namespace": "spiders",
        },
    ]
    for metric_name, value in (
        ("item_scraped_count", 30.0),
        ("postgresql/add", 30.0),
        ("postgresql/modify", 0.0),
        ("postgresql/ignore", 0.0),
    ):
        metrics = client.get_metric_statistics(
            Namespace="spiders",
            MetricName="mocked-spider/" + metric_name,
            StartTime=datetime.datetime.now() - datetime.timedelta(seconds=20),
            EndTime=datetime.datetime.now() + datetime.timedelta(seconds=20),
            Period=60,
            Statistics=["SampleCount", "Sum"],
        )
        assert len(metrics["Datapoints"]) == 1
        assert metrics["Datapoints"][0]["SampleCount"] == 1.0
        assert metrics["Datapoints"][0]["Sum"] == value
        assert metrics["Label"] == "mocked-spider/" + metric_name


def test_response_formatting():
    assert format_response(stats) == OrderedDict(
        [
            ("downloader/request_bytes", 10055),
            ("downloader/request_count", 34),
            ("downloader/request_method_count/GET", 34),
            ("downloader/response_bytes", 174399),
            ("downloader/response_count", 34),
            ("downloader/response_status_count/200", 32),
            ("downloader/response_status_count/301", 2),
            ("finish_reason", "finished"),
            ("finish_time", "2019-04-08 11:49:32.717749"),
            ("item_scraped_count", 30),
            ("log_count/DEBUG", 112),
            ("log_count/INFO", 9),
            ("log_count/WARNING", 1),
            ("memusage/max", 76472320),
            ("memusage/startup", 76472320),
            ("postgresql/add", 30),
            ("request_depth_max", 1),
            ("response_received_count", 32),
            ("robotstxt/request_count", 1),
            ("robotstxt/response_count", 1),
            ("robotstxt/response_status_count/200", 1),
            ("scheduler/dequeued", 32),
            ("scheduler/dequeued/memory", 32),
            ("scheduler/enqueued", 32),
            ("scheduler/enqueued/memory", 32),
            ("start_time", "2019-04-08 11:49:22.841506"),
        ]
    )

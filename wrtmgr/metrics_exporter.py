from .inventory import iter_machines
import asyncio
import re
from paramiko import SSHClient, AutoAddPolicy
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY


class CustomCollector(object):
    labels = ['host', 'mac_address']
    metrics_def = [
        (GaugeMetricFamily,
         'wifi_station_inactive_time_ms',
         'Time since last activity of station',
         r'inactive time:\s*(\d+)\s*ms',
         int),
        (CounterMetricFamily,
         'wifi_station_rx_bytes',
         'Bytes received by station',
         r'rx bytes:\s*(\d+)',
         int),
        (CounterMetricFamily,
         'wifi_station_tx_bytes',
         'Bytes transmitted by station',
         r'tx bytes:\s*(\d+)',
         int),
        (CounterMetricFamily,
         'wifi_station_rx_packets',
         'Packets received by station',
         r'rx packets:\s*(\d+)',
         int),
        (CounterMetricFamily,
         'wifi_station_tx_packets',
         'Packets transmitted to station',
         r'tx packets:\s*(\d+)',
         int),
        (CounterMetricFamily,
         'wifi_station_tx_packets',
         'Packets transmitted to station',
         r'tx packets:\s*(\d+)',
         int),
        (CounterMetricFamily,
         'wifi_station_tx_retries',
         'Number of times a packet was retransmitted to station',
         r'tx retries:\s*(\d+)',
         int),
        (CounterMetricFamily,
         'wifi_station_tx_failed',
         'Number of packets we gave up transmitting to station',
         r'tx failed:\s*(\d+)',
         int),
        (CounterMetricFamily,
         'wifi_station_rx_drop_misc',
         'Number of misc packets dropped on reception from station',
         r'rx drop misc:\s*(\d+)',
         int),
        (GaugeMetricFamily,
         'wifi_station_signal_dbm',
         'Intensity of signal received from station',
         r'signal:\s*([-\d]+).*?dBm',
         int),
        (GaugeMetricFamily,
         'wifi_station_signal_avg_dbm',
         'Average intensity of signal received from station',
         r'signal avg:\s*([-\d]+).*?dBm',
         int),
        (GaugeMetricFamily,
         'wifi_station_expected_throughput_mbps',
         'Expected throughput to station',
         r'expected throughput:\s*([.\d]+).*?Mbps',
         float),
        (CounterMetricFamily,
         'wifi_station_connected_time_seconds',
         'Time since station is connected',
         r'connected time:\s*(\d+)\s*seconds',
         int),
    ]

    def collect(self):
        metrics = []
        for family, name, desc, regex, typ in self.metrics_def:
            metrics.append(
                (family(name, desc, labels=self.labels), regex, typ))

        for machine, unused in iter_machines():
            ssh = SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(AutoAddPolicy())

            ssh.connect(machine, username='root')

            stdin, stdout, stderr = ssh.exec_command(
                'iw dev wlan0 station dump')

            station = None

            for line in stdout:
                m = re.search(r'^Station ([^\s]+)', line)
                if m:
                    station = m.group(1)
                    continue
                if not station:
                    continue
                label_values = [machine, station]

                for met, regex, typ in metrics:
                    m = re.search(regex, line)
                    if m:
                        met.add_metric(label_values, typ(m.group(1)))

            ssh.close()

        for met, regex, typ in metrics:
            yield met


def main(args):
    REGISTRY.register(CustomCollector())
    start_http_server(args.port)

    loop = asyncio.get_event_loop()
    try:
        loop.run_forever()
    finally:
        loop.close()

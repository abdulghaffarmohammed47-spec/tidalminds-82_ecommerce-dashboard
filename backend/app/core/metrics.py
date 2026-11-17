import time
from typing import Dict, Tuple

class PrometheusMetrics:
    def __init__(self):
        self.start_time = time.time()
        # (method, endpoint, status) -> count
        self.request_counts: Dict[Tuple[str, str, int], int] = {}
        # (method, endpoint) -> total_duration_seconds
        self.request_durations: Dict[Tuple[str, str], float] = {}
        # (status) -> count
        self.orders_total: Dict[str, int] = {}
        # (event_type) -> count
        self.inventory_locks: Dict[str, int] = {}

    def record_request(self, method: str, path: str, status_code: int, duration: float):
        # Normalize path to avoid high-cardinality route params
        normalized_path = path.split("?")[0]
        parts = normalized_path.strip("/").split("/")
        # Replace UUIDs with :id placeholder
        cleaned_parts = []
        for p in parts:
            if len(p) in (32, 36) and ("-" in p or p.isalnum()):
                cleaned_parts.append(":id")
            else:
                cleaned_parts.append(p)
        clean_path = "/" + "/".join(cleaned_parts) if cleaned_parts else "/"

        key = (method, clean_path, status_code)
        self.request_counts[key] = self.request_counts.get(key, 0) + 1
        
        dur_key = (method, clean_path)
        self.request_durations[dur_key] = self.request_durations.get(dur_key, 0.0) + duration

    def record_order(self, status: str = "CONFIRMED"):
        self.orders_total[status] = self.orders_total.get(status, 0) + 1

    def record_inventory_lock(self, result: str):
        self.inventory_locks[result] = self.inventory_locks.get(result, 0) + 1

    def generate_prometheus_text(self) -> str:
        lines = [
            "# HELP smartcommerce_uptime_seconds Total application uptime in seconds",
            "# TYPE smartcommerce_uptime_seconds gauge",
            f"smartcommerce_uptime_seconds {time.time() - self.start_time:.2f}",
            "",
            "# HELP http_requests_total Total number of HTTP requests processed",
            "# TYPE http_requests_total counter"
        ]

        for (method, path, status), count in sorted(self.request_counts.items()):
            lines.append(f'http_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}')

        lines.extend([
            "",
            "# HELP http_request_duration_seconds_total Total duration of HTTP requests in seconds",
            "# TYPE http_request_duration_seconds_total counter"
        ])

        for (method, path), total_dur in sorted(self.request_durations.items()):
            lines.append(f'http_request_duration_seconds_total{{method="{method}",path="{path}"}} {total_dur:.4f}')

        lines.extend([
            "",
            "# HELP smartcommerce_orders_total Total orders processed by status",
            "# TYPE smartcommerce_orders_total counter"
        ])
        for status, count in sorted(self.orders_total.items()):
            lines.append(f'smartcommerce_orders_total{{status="{status}"}} {count}')

        lines.extend([
            "",
            "# HELP smartcommerce_inventory_lock_events_total Inventory lock acquisition outcomes",
            "# TYPE smartcommerce_inventory_lock_events_total counter"
        ])
        for event, count in sorted(self.inventory_locks.items()):
            lines.append(f'smartcommerce_inventory_lock_events_total{{outcome="{event}"}} {count}')

        return "\n".join(lines) + "\n"

metrics = PrometheusMetrics()

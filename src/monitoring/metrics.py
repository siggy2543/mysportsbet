class MetricsHandler:
    def __init__(self):
        self.metrics = {}

    def add_metric(self, name, value):
        self.metrics[name] = value

    def get_metric(self, name):
        return self.metrics.get(name)

    def remove_metric(self, name):
        if name in self.metrics:
            del self.metrics[name]

    def get_all_metrics(self):
        return self.metrics

# Example usage:
handler = MetricsHandler()
handler.add_metric("requests", 100)
handler.add_metric("errors", 5)

print(handler.get_metric("requests"))  # Output: 100
print(handler.get_all_metrics())  # Output: {'requests': 100, 'errors': 5}

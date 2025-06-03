from locust import HttpUser, task, between
from typing import Dict
import random


class ConfigAPIUser(HttpUser):
    wait_time = between(3, 3.5)

    SERVICE_TOKENS: Dict[str, str] = {
        "web-app": "webapp_abc123",
        "api-service": "api_def456",
        "worker": "worker_ghi789"
    }

    def on_start(self):
        self.service = random.choice(["web-app", "api-service", "worker"])
        self.token = self.SERVICE_TOKENS[self.service]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task
    def get_config(self):
        """Task principal: GET config pentru dev environment"""
        self.client.get(
            f"/configs/{self.service}/dev",
            headers=self.headers,
            name="/configs/{service}/dev"
        )

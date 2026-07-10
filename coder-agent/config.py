"""
Coder Agent 配置
"""
import os

CONFIG = {
    "repo_owner": "PMA213X",
    "repo_name": "bandcode",
    "agent_username": "malingyun123",
    "poll_interval": 900,  # 15分钟 = 900秒
    "base_branch": "develop",
    "feature_prefix": "feature/",
    "max_retries": 3,
    "state_file": "coder-agent/state/processed_ids.json",
    "log_file": "coder-agent/logs/agent.log",
}

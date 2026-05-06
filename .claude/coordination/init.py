#!/usr/bin/env python3
"""
协调系统初始化脚本

首次使用前运行一次，初始化 coordination 目录结构和上下文状态。
"""

import json
import os
import sys
from datetime import datetime, timezone

COORDINATION_DIR = os.path.join(os.path.dirname(__file__))
CONTEXT_FILE = os.path.join(COORDINATION_DIR, "context", "current.json")
LOCKS_FILE = os.path.join(COORDINATION_DIR, "locks", "current.json")

DIRS = [
    "context/snapshots",
    "context/versions",
    "tasks/queue",
    "tasks/active",
    "tasks/blocked",
    "tasks/done",
    "tasks/failed",
    "locks",
    "artifacts",
    "reviews",
    "incidents",
    "audit",
]

INITIAL_CONTEXT = {
    "schema_version": "2.0",
    "context_version": "ctx_v20260506_01",
    "updated_at": datetime.now(timezone.utc).astimezone().isoformat(),
    "updated_by": "init",
    "system_state": {
        "status": "IDLE",
        "active_sprint": "Sprint-1",
        "baseline_commit": None,
        "current_branch": "main",
        "last_rollback_point": None,
        "quality_gates": {
            "unit_tests": "UNKNOWN",
            "integration_tests": "UNKNOWN",
            "e2e_tests": "UNKNOWN",
            "security_review": "UNKNOWN",
            "lint_check": "UNKNOWN"
        }
    },
    "environment": {
        "runtime": {"node_version": None, "python_version": None, "docker_available": False},
        "backend": {
            "framework": "FastAPI",
            "database_url": "postgresql://localhost:5432/zcw_rag_blog",
            "redis_url": "redis://localhost:6379/0",
            "vector_store": "pgvector",
            "embedding_model": "text-embedding-3-small"
        },
        "frontend": {
            "framework": "Nuxt 3",
            "ssr_mode": "hybrid",
            "ui_library": "Tailwind CSS",
            "api_base_url": "http://localhost:8000/api/v1"
        },
        "ai_models": {
            "reasoner": "deepseek-reasoner",
            "chat": "deepseek-chat",
            "embedding": "text-embedding-3-small"
        }
    },
    "resource_allocation": {
        "agents": {
            agent: {"status": "AVAILABLE", "active_tasks": [], "max_concurrent": mc,
                    "recent_failure_rate": 0.0, "avg_completion_minutes": 0}
            for agent, mc in [("orch", 1), ("spec", 2), ("arch", 2), ("fe", 2),
                              ("be", 2), ("db", 2), ("ai", 2), ("qa", 4),
                              ("ops", 2), ("sec", 2), ("doc", 3)]
        },
        "locks": [],
        "global_lock": None
    },
    "task_execution_context": {
        "task_queue": [], "active_tasks": [], "blocked_tasks": [],
        "dependency_graph": {"nodes": [], "edges": []},
        "recently_completed": [], "recently_failed": []
    },
    "review_context": {
        "pending_reviews": [], "in_progress_reviews": [], "completed_reviews": []
    },
    "incident_log": [],
    "audit_trail": [
        {
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
            "event": "CONTEXT_INITIALIZED",
            "actor": "init",
            "summary": "协调系统初始化完成",
            "context_version": "ctx_v20260506_01"
        }
    ]
}

INITIAL_LOCKS = {"locks": []}


def init():
    print("初始化协调系统...\n")

    for d in DIRS:
        path = os.path.join(COORDINATION_DIR, d)
        os.makedirs(path, exist_ok=True)
        print(f"  [OK] {d}/")

    save_json(CONTEXT_FILE, INITIAL_CONTEXT)
    print(f"  [OK] context/current.json (v{INITIAL_CONTEXT['context_version']})")

    save_json(LOCKS_FILE, INITIAL_LOCKS)
    print("  [OK] locks/current.json")

    print("\n初始化完成。运行 python scheduler.py --help 查看可用命令。")


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    init()

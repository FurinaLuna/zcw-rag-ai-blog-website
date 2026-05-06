#!/usr/bin/env python3
"""
Claude Code 多 Agent 协调调度器

本脚本提供自动化的任务调度、状态管理和锁管理能力，
作为 CLAUDE.md 中定义的 orch Agent 的自动化执行引擎。

使用方式：
  python .claude/coordination/scheduler.py --help

依赖：Python 3.8+，无需第三方库
"""

import json
import os
import sys
import time
import glob
from datetime import datetime, timezone
from typing import Optional

COORDINATION_DIR = os.path.join(os.path.dirname(__file__))
CONTEXT_FILE = os.path.join(COORDINATION_DIR, "context", "current.json")
LOCKS_FILE = os.path.join(COORDINATION_DIR, "locks", "current.json")
TASKS_DIR = os.path.join(COORDINATION_DIR, "tasks")


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


def bump_context_version(current_version: str) -> str:
    prefix, seq = current_version.rsplit("_", 1)
    return f"{prefix}_{int(seq) + 1:02d}"


# ─── 任务管理 ─────────────────────────────────────────────


def list_tasks(status_dir: str) -> list[dict]:
    tasks = []
    pattern = os.path.join(TASKS_DIR, status_dir, "*.json")
    for fpath in sorted(glob.glob(pattern)):
        tasks.append(load_json(fpath))
    return tasks


def move_task(task_id: str, from_dir: str, to_dir: str) -> bool:
    src = os.path.join(TASKS_DIR, from_dir, f"{task_id}.json")
    dst = os.path.join(TASKS_DIR, to_dir, f"{task_id}.json")
    if not os.path.exists(src):
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    os.rename(src, dst)
    return True


def create_task(task_def: dict) -> str:
    task_id = task_def.get("task_id")
    if not task_id:
        raise ValueError("task_id is required")
    fpath = os.path.join(TASKS_DIR, "queue", f"{task_id}.json")
    task_def["status"] = "QUEUED"
    task_def["created_at"] = now_iso()
    task_def["updated_at"] = now_iso()
    save_json(fpath, task_def)
    return task_id


def update_task_status(task_id: str, status: str, status_dir: str) -> None:
    for d in ["queue", "active", "blocked", "done", "failed"]:
        fpath = os.path.join(TASKS_DIR, d, f"{task_id}.json")
        if os.path.exists(fpath):
            task = load_json(fpath)
            task["status"] = status
            task["updated_at"] = now_iso()
            save_json(fpath, task)
            if os.path.dirname(fpath) != os.path.join(TASKS_DIR, status_dir):
                move_task(task_id, d, status_dir)
            return
    raise FileNotFoundError(f"Task {task_id} not found")


# ─── 锁管理 ───────────────────────────────────────────────


def acquire_lock(lock_id: str, level: str, path: str, holder: str,
                 task_id: str, ttl_sec: int = 1800) -> bool:
    locks = load_json(LOCKS_FILE) if os.path.exists(LOCKS_FILE) else {"locks": []}

    for lock in locks["locks"]:
        if lock["path"] == path and lock["status"] == "ACTIVE":
            age_sec = (datetime.fromisoformat(now_iso()) -
                       datetime.fromisoformat(lock["acquired_at"])).total_seconds()
            if age_sec < lock["ttl_sec"]:
                return False
            lock["status"] = "EXPIRED"

    locks["locks"].append({
        "lock_id": lock_id,
        "level": level,
        "path": path,
        "holder": holder,
        "task_id": task_id,
        "acquired_at": now_iso(),
        "ttl_sec": ttl_sec,
        "status": "ACTIVE"
    })
    save_json(LOCKS_FILE, locks)
    return True


def release_lock(lock_id: str, holder: str) -> bool:
    locks = load_json(LOCKS_FILE) if os.path.exists(LOCKS_FILE) else {"locks": []}
    for lock in locks["locks"]:
        if lock["lock_id"] == lock_id and lock["holder"] == holder:
            lock["status"] = "RELEASED"
            lock["released_at"] = now_iso()
            save_json(LOCKS_FILE, locks)
            return True
    return False


def cleanup_expired_locks() -> list[dict]:
    locks = load_json(LOCKS_FILE) if os.path.exists(LOCKS_FILE) else {"locks": []}
    expired = []
    for lock in locks["locks"]:
        if lock["status"] == "ACTIVE":
            age_sec = (datetime.fromisoformat(now_iso()) -
                       datetime.fromisoformat(lock["acquired_at"])).total_seconds()
            if age_sec >= lock["ttl_sec"]:
                lock["status"] = "EXPIRED"
                lock["expired_at"] = now_iso()
                expired.append(lock)
    if expired:
        save_json(LOCKS_FILE, locks)
    return expired


# ─── 上下文管理 ───────────────────────────────────────────


def get_context() -> dict:
    return load_json(CONTEXT_FILE)


def update_context(updates: dict) -> str:
    ctx = get_context()
    ctx.update(updates)
    ctx["updated_at"] = now_iso()
    ctx["context_version"] = bump_context_version(ctx["context_version"])
    save_json(CONTEXT_FILE, ctx)
    return ctx["context_version"]


def append_audit(event: str, actor: str, summary: str) -> None:
    ctx = get_context()
    ctx["audit_trail"].append({
        "timestamp": now_iso(),
        "event": event,
        "actor": actor,
        "summary": summary,
        "context_version": ctx["context_version"]
    })
    save_json(CONTEXT_FILE, ctx)


# ─── 调度逻辑 ─────────────────────────────────────────────


def calculate_priority(task: dict) -> int:
    scores = {"P0": 90, "P1": 75, "P2": 50, "P3": 25}
    return scores.get(task.get("priority", "P3"), 25)


def get_ready_tasks() -> list[dict]:
    queue = list_tasks("queue")
    active = list_tasks("active")
    done_ids = {t["task_id"] for t in list_tasks("done")}

    ready = []
    for task in queue:
        deps = task.get("dependencies", [])
        if all(d in done_ids for d in deps):
            ready.append(task)
    return sorted(ready, key=calculate_priority, reverse=True)


def dispatch_tasks(max_concurrent: int = 4) -> list[dict]:
    ctx = get_context()
    active = list_tasks("active")
    agent_load: dict[str, int] = {}
    for t in active:
        owner = t.get("owner", "unknown")
        agent_load[owner] = agent_load.get(owner, 0) + 1

    max_per_agent = {
        "fe": 2, "be": 2, "db": 2, "ai": 2,
        "qa": 4, "ops": 2, "doc": 3, "spec": 2, "arch": 2
    }

    ready = get_ready_tasks()
    dispatched = []

    for task in ready:
        if len(active) + len(dispatched) >= max_concurrent:
            break
        owner = task.get("owner", "unknown")
        if agent_load.get(owner, 0) >= max_per_agent.get(owner, 2):
            continue

        move_task(task["task_id"], "queue", "active")
        update_task_status(task["task_id"], "ASSIGNED", "active")
        agent_load[owner] = agent_load.get(owner, 0) + 1
        dispatched.append(task)

        append_audit(
            "TASK_ASSIGNED",
            "scheduler",
            f"任务 {task['task_id']} 已分配给 {owner}"
        )

    if dispatched:
        update_context({
            "task_execution_context": {
                "active_tasks": list_tasks("active"),
                "task_queue": list_tasks("queue")
            }
        })

    return dispatched


# ─── CLI 入口 ─────────────────────────────────────────────


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Claude Code 多 Agent 协调调度器"
    )
    sub = parser.add_subparsers(dest="command")

    # task create
    p_create = sub.add_parser("task-create", help="创建新任务")
    p_create.add_argument("--file", "-f", required=True, help="任务定义 JSON 文件路径")

    # task list
    p_list = sub.add_parser("task-list", help="列出任务")
    p_list.add_argument("status", nargs="?", default="queue",
                        choices=["queue", "active", "blocked", "done", "failed"])

    # task move
    p_move = sub.add_parser("task-move", help="移动任务状态")
    p_move.add_argument("task_id")
    p_move.add_argument("to", choices=["queue", "active", "blocked", "done", "failed"])

    # lock acquire
    p_lock = sub.add_parser("lock-acquire", help="获取文件锁")
    p_lock.add_argument("lock_id")
    p_lock.add_argument("--level", default="FILE_LOCK",
                        choices=["FILE_LOCK", "MODULE_LOCK", "GLOBAL_LOCK"])
    p_lock.add_argument("--path", required=True)
    p_lock.add_argument("--holder", required=True)
    p_lock.add_argument("--task-id", required=True)
    p_lock.add_argument("--ttl", type=int, default=1800)

    # lock release
    p_unlock = sub.add_parser("lock-release", help="释放文件锁")
    p_unlock.add_argument("lock_id")
    p_unlock.add_argument("--holder", required=True)

    # lock cleanup
    sub.add_parser("lock-cleanup", help="清理过期锁")

    # dispatch
    p_dispatch = sub.add_parser("dispatch", help="调度就绪任务")
    p_dispatch.add_argument("--max", type=int, default=4)

    # context
    p_ctx = sub.add_parser("context-show", help="显示当前上下文")
    p_ctx.add_argument("--section", choices=["system", "agents", "tasks", "audit"])

    # audit
    p_audit = sub.add_parser("audit", help="添加审计日志")
    p_audit.add_argument("--event", required=True)
    p_audit.add_argument("--actor", required=True)
    p_audit.add_argument("--summary", required=True)

    args = parser.parse_args()

    if args.command == "task-create":
        task_def = load_json(args.file)
        task_id = create_task(task_def)
        append_audit("TASK_CREATED", "cli", f"任务 {task_id} 已创建")
        print(f"任务已创建: {task_id}")

    elif args.command == "task-list":
        tasks = list_tasks(args.status)
        print(f"\n=== {args.status.upper()} 任务 ({len(tasks)}) ===\n")
        for t in tasks:
            deps = t.get("dependencies", [])
            dep_str = f" [依赖: {', '.join(deps)}]" if deps else ""
            print(f"  {t['task_id']} | {t.get('owner', '?')} | "
                  f"{t.get('priority', 'P3')} | {t.get('goal', '')[:60]}{dep_str}")

    elif args.command == "task-move":
        update_task_status(args.task_id, args.to.upper(), args.to)
        append_audit("TASK_MOVED", "cli",
                     f"任务 {args.task_id} 移至 {args.to}")
        print(f"任务 {args.task_id} 已移至 {args.to}")

    elif args.command == "lock-acquire":
        ok = acquire_lock(args.lock_id, args.level, args.path,
                          args.holder, args.task_id, args.ttl)
        if ok:
            append_audit("LOCK_ACQUIRED", args.holder,
                         f"锁 {args.lock_id} 已获取 ({args.path})")
            print(f"锁已获取: {args.lock_id}")
        else:
            print(f"锁获取失败: {args.lock_id} (已被占用)")

    elif args.command == "lock-release":
        ok = release_lock(args.lock_id, args.holder)
        if ok:
            append_audit("LOCK_RELEASED", args.holder,
                         f"锁 {args.lock_id} 已释放")
            print(f"锁已释放: {args.lock_id}")
        else:
            print(f"锁释放失败: {args.lock_id}")

    elif args.command == "lock-cleanup":
        expired = cleanup_expired_locks()
        if expired:
            for lock in expired:
                print(f"过期锁已清理: {lock['lock_id']} ({lock['path']})")
            append_audit("LOCKS_CLEANED", "scheduler",
                         f"清理了 {len(expired)} 个过期锁")
        else:
            print("无过期锁")

    elif args.command == "dispatch":
        dispatched = dispatch_tasks(args.max)
        print(f"已调度 {len(dispatched)} 个任务:")
        for t in dispatched:
            print(f"  {t['task_id']} → {t.get('owner', '?')}")

    elif args.command == "context-show":
        ctx = get_context()
        if args.section == "system":
            print(json.dumps(ctx.get("system_state", {}), ensure_ascii=False, indent=2))
        elif args.section == "agents":
            agents = ctx.get("resource_allocation", {}).get("agents", {})
            for aid, info in agents.items():
                print(f"  {aid}: {info['status']} "
                      f"(active: {len(info.get('active_tasks', []))}/{info['max_concurrent']})")
        elif args.section == "tasks":
            tec = ctx.get("task_execution_context", {})
            print(f"  队列: {len(tec.get('task_queue', []))}")
            print(f"  活跃: {len(tec.get('active_tasks', []))}")
            print(f"  阻塞: {len(tec.get('blocked_tasks', []))}")
        elif args.section == "audit":
            for entry in ctx.get("audit_trail", [])[-10:]:
                print(f"  [{entry['timestamp']}] {entry['event']} - {entry['summary']}")
        else:
            print(json.dumps(ctx, ensure_ascii=False, indent=2))

    elif args.command == "audit":
        append_audit(args.event, args.actor, args.summary)
        print("审计日志已添加")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

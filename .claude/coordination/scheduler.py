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


# ─── Git 操作 ─────────────────────────────────────────────


def git_command(*args: str) -> tuple[int, str]:
    import subprocess
    result = subprocess.run(["git"] + list(args), capture_output=True, text=True)
    return result.returncode, (result.stdout + result.stderr).strip()


def git_branch_create(branch_name: str, base_branch: str = "main") -> bool:
    code, output = git_command("checkout", base_branch)
    if code != 0:
        print(f"切换到 {base_branch} 失败: {output}")
        return False
    code, output = git_command("pull", "--ff-only")
    if code != 0:
        print(f"拉取最新代码失败: {output}")
        return False
    code, output = git_command("checkout", "-b", branch_name)
    if code != 0:
        print(f"创建分支 {branch_name} 失败: {output}")
        return False
    return True


def git_stage(paths: list[str]) -> bool:
    code, output = git_command("add", *paths)
    if code != 0:
        print(f"暂存失败: {output}")
        return False
    return True


def git_commit(message: str) -> bool:
    code, output = git_command("commit", "-m", message)
    if code != 0:
        print(f"提交失败: {output}")
        return False
    return True


def git_push(branch_name: str) -> bool:
    code, output = git_command("push", "-u", "origin", branch_name)
    if code != 0:
        print(f"推送失败: {output}")
        return False
    return True


def check_merge_conditions(task_id: str) -> dict:
    conditions = {
        "no_lock_conflicts": True,
        "unit_tests_passed": False,
        "integration_tests_passed": False,
        "docs_synced": False,
        "security_review_passed": False,
        "no_breaking_migration": True,
        "no_public_api_breaking": True
    }

    locks_file = os.path.join(COORDINATION_DIR, "locks", "current.json")
    if os.path.exists(locks_file):
        locks = load_json(locks_file)
        for lock in locks.get("locks", []):
            if lock.get("status") == "ACTIVE" and lock.get("task_id") != task_id:
                conditions["no_lock_conflicts"] = False
                break

    ctx = get_context()
    qg = ctx.get("system_state", {}).get("quality_gates", {})
    conditions["unit_tests_passed"] = qg.get("unit_tests") == "PASSED"
    conditions["integration_tests_passed"] = qg.get("integration_tests") == "PASSED"
    conditions["security_review_passed"] = qg.get("security_review") == "PASSED"

    all_pass = all(conditions.values())
    return {"conditions": conditions, "all_pass": all_pass}


def format_branch_name(task: dict) -> str:
    type_map = {"fe": "feat", "be": "feat", "ai": "feat", "db": "feat",
                "qa": "chore", "ops": "chore", "doc": "chore",
                "spec": "chore", "arch": "chore", "sec": "fix"}
    owner = task.get("owner", "chore")
    prefix = type_map.get(owner, "chore")
    task_id = task.get("task_id", "task_unknown")
    goal = task.get("goal", "update")[:30]
    slug = goal.lower().replace(" ", "-").replace("_", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")[:20]
    return f"{prefix}/{owner}/{task_id}/{slug}"


def format_commit_message(task: dict) -> str:
    prefix_map = {"fe": "feat(frontend)", "be": "feat(backend)", "ai": "feat(rag)",
                  "db": "feat(database)", "qa": "test", "ops": "chore(ops)",
                  "doc": "docs", "spec": "chore(spec)", "arch": "chore(arch)",
                  "sec": "fix(security)"}
    scope = prefix_map.get(task.get("owner", ""), "chore")
    task_id = task.get("task_id", "")
    goal = task.get("goal", "")
    return f"{scope}: {goal} ({task_id})"


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

    # quality gate
    p_qg = sub.add_parser("quality-gate", help="设置质量门禁状态")
    p_qg.add_argument("--gate", required=True,
                      choices=["unit_tests", "integration_tests", "e2e_tests",
                               "security_review", "lint_check"],
                      help="门禁名称")
    p_qg.add_argument("--status", required=True,
                      choices=["PASSED", "FAILED", "UNKNOWN"],
                      help="门禁状态")

    # git branch
    p_git_branch = sub.add_parser("git-branch", help="创建功能分支")
    p_git_branch.add_argument("task_id", help="任务 ID")
    p_git_branch.add_argument("--base", default="main", help="基于哪个分支创建")

    # git commit
    p_git_commit = sub.add_parser("git-commit", help="暂存并提交代码")
    p_git_commit.add_argument("task_id", help="任务 ID")
    p_git_commit.add_argument("--paths", "-p", nargs="+", required=True,
                              help="要暂存的文件路径")
    p_git_commit.add_argument("--message", "-m", help="自定义提交信息（可选）")

    # git push
    p_git_push = sub.add_parser("git-push", help="推送分支到远程")
    p_git_push.add_argument("task_id", help="任务 ID")
    p_git_push.add_argument("--branch", help="分支名（可选，默认从任务自动生成）")

    # merge check
    sub.add_parser("merge-check", help="检查合并条件是否满足")

    # full workflow: branch → commit → push
    p_workflow = sub.add_parser("workflow-finish", help="完成模块的完整提交流程")
    p_workflow.add_argument("task_id", help="任务 ID")
    p_workflow.add_argument("--paths", "-p", nargs="+", required=True,
                            help="要提交的文件路径")
    p_workflow.add_argument("--message", "-m", help="自定义提交信息")
    p_workflow.add_argument("--base", default="main", help="基于哪个分支")
    p_workflow.add_argument("--skip-push", action="store_true", help="跳过推送")

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

    elif args.command == "quality-gate":
        ctx = get_context()
        ctx["system_state"]["quality_gates"][args.gate] = args.status
        save_json(CONTEXT_FILE, ctx)
        append_audit("QUALITY_GATE_UPDATED", "scheduler",
                     f"门禁 {args.gate} 已设为 {args.status}")
        print(f"门禁 {args.gate} 已设为 {args.status}")

    elif args.command == "git-branch":
        task = None
        for d in ["active", "queue", "done"]:
            fpath = os.path.join(TASKS_DIR, d, f"{args.task_id}.json")
            if os.path.exists(fpath):
                task = load_json(fpath)
                break
        if not task:
            print(f"任务 {args.task_id} 不存在")
            return

        branch = format_branch_name(task)
        ok = git_branch_create(branch, args.base)
        if ok:
            ctx = get_context()
            ctx["system_state"]["current_branch"] = branch
            save_json(CONTEXT_FILE, ctx)
            append_audit("BRANCH_CREATED", "scheduler",
                         f"分支 {branch} 已创建 (基于 {args.base})")
            print(f"分支已创建: {branch}")
        else:
            print("分支创建失败")

    elif args.command == "git-commit":
        task = None
        for d in ["active", "done"]:
            fpath = os.path.join(TASKS_DIR, d, f"{args.task_id}.json")
            if os.path.exists(fpath):
                task = load_json(fpath)
                break
        if not task:
            print(f"任务 {args.task_id} 不存在或不在 active/done 中")
            return

        if not git_stage(args.paths):
            return

        message = args.message or format_commit_message(task)
        if git_commit(message):
            append_audit("COMMIT_CREATED", "scheduler",
                         f"任务 {args.task_id} 已提交: {message}")
            print(f"提交成功: {message}")
        else:
            print("提交失败")

    elif args.command == "git-push":
        task = None
        for d in ["active", "done"]:
            fpath = os.path.join(TASKS_DIR, d, f"{args.task_id}.json")
            if os.path.exists(fpath):
                task = load_json(fpath)
                break
        if not task:
            print(f"任务 {args.task_id} 不存在或不在 active/done 中")
            return

        branch = args.branch or format_branch_name(task)
        if git_push(branch):
            ctx = get_context()
            ctx["system_state"]["current_branch"] = branch
            save_json(CONTEXT_FILE, ctx)
            append_audit("BRANCH_PUSHED", "scheduler",
                         f"分支 {branch} 已推送到远程")
            print(f"推送成功: {branch}")
        else:
            print("推送失败")

    elif args.command == "merge-check":
        result = check_merge_conditions("")
        print(f"\n合并条件检查:")
        for cond, passed in result["conditions"].items():
            status = "PASS" if passed else "FAIL"
            print(f"  [{status}] {cond}")
        print(f"\n总体结果: {'通过' if result['all_pass'] else '未通过'}")

    elif args.command == "workflow-finish":
        task = None
        for d in ["active", "done"]:
            fpath = os.path.join(TASKS_DIR, d, f"{args.task_id}.json")
            if os.path.exists(fpath):
                task = load_json(fpath)
                break
        if not task:
            print(f"任务 {args.task_id} 不存在")
            return

        print(f"\n开始完整提交流程: {args.task_id}\n")

        branch = format_branch_name(task)
        print(f"[1/4] 创建分支: {branch}")
        if not git_branch_create(branch, args.base):
            return

        print(f"[2/4] 暂存文件: {len(args.paths)} 个文件")
        if not git_stage(args.paths):
            return

        message = args.message or format_commit_message(task)
        print(f"[3/4] 提交: {message}")
        if not git_commit(message):
            return

        if not args.skip_push:
            print(f"[4/4] 推送到远程: {branch}")
            if not git_push(branch):
                return

        update_task_status(args.task_id, "DONE", "done")
        ctx = get_context()
        ctx["system_state"]["current_branch"] = branch
        ctx["system_state"]["baseline_commit"] = branch
        save_json(CONTEXT_FILE, ctx)

        append_audit("WORKFLOW_COMPLETED", "scheduler",
                     f"任务 {args.task_id} 已完成提交流程，分支: {branch}")
        print(f"\n提交流程完成！分支: {branch}")
        print(f"提交信息: {message}")
        print(f"下一步: 创建 Pull Request 合并到 {args.base}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

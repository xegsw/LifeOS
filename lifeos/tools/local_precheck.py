#!/usr/bin/env python3
"""
LifeOS Local Precheck

从 Mac 本地项目读取当前状态、任务卡和交付物，调用局域网 Windows
Ollama 上的 qwen3:14b 做低风险预检，并把结果保存回 lifeos/local_prechecks/。

本脚本只生成 Local Precheck，不做 PM Review、不做独立评审、不做验收、
不更新项目账本、不冻结任何资产。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path


DEFAULT_OLLAMA_URL = "http://192.168.5.17:11434"
DEFAULT_MODEL = "qwen3:14b"
DEFAULT_NUM_CTX = 24576
DEFAULT_NUM_PREDICT = 1200
DEFAULT_TIMEOUT = 300
MIN_USEFUL_RESPONSE_CHARS = 80
MAX_CHARS_PER_FILE = 45_000
MAX_TOTAL_CHARS = 110_000


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text_limited(path: Path, max_chars: int = MAX_CHARS_PER_FILE) -> tuple[str, bool]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= max_chars:
        return text, False

    head = max_chars // 2
    tail = max_chars - head
    clipped = (
        text[:head]
        + "\n\n[... 本文件过长，local_precheck.py 已截断中间内容 ...]\n\n"
        + text[-tail:]
    )
    return clipped, True


def find_task_id(path_or_text: str) -> str | None:
    match = re.search(r"LIFEOS-P\d+-\d+", path_or_text)
    return match.group(0) if match else None


def resolve_path(root: Path, raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def find_task_card(root: Path, task_id: str) -> Path | None:
    candidates = sorted((root / "lifeos" / "tasks").glob(f"{task_id}_*.md"))
    return candidates[0] if candidates else None


def optional_file(root: Path, relative: str) -> Path | None:
    path = root / relative
    return path if path.exists() else None


def build_prompt(
    *,
    task_id: str,
    artifact_path: Path,
    source_sections: list[tuple[str, Path, str, bool]],
) -> str:
    files_block_parts = []
    total_chars = 0
    total_clipped = False

    for label, path, content, clipped in source_sections:
        if total_chars + len(content) > MAX_TOTAL_CHARS:
            remaining = max(0, MAX_TOTAL_CHARS - total_chars)
            if remaining <= 0:
                content = "[未包含：本次输入已达到 local_precheck.py 的总长度上限。]"
            else:
                content = (
                    content[:remaining]
                    + "\n\n[... 本次输入已达到 local_precheck.py 的总长度上限，后续内容已截断 ...]"
                )
            total_clipped = True
        total_chars += len(content)
        total_clipped = total_clipped or clipped
        files_block_parts.append(
            f"## {label}\n\n路径：`{path}`\n\n```markdown\n{content}\n```"
        )
        if total_chars >= MAX_TOTAL_CHARS:
            break

    clipped_note = "是" if total_clipped else "否"
    files_block = "\n\n".join(files_block_parts)

    return f"""
你是 LifeOS 项目的本地预检助手，不是 PM 主会话，不是独立评审会话，不做最终验收，不做冻结判断。

本次任务 ID：{task_id}
被预检文件：`{artifact_path}`
输入是否存在截断：{clipped_note}

请只基于下方输入材料做低风险预检，输出控制在 800-1200 字。

必须输出以下结构：

1. 100 字摘要
2. 任务卡覆盖情况
3. 明显遗漏项
4. 可能越界或高风险表述
5. 是否误写成 Frozen / Accepted / MVP 准入 / 已实现
6. 需要 PM 重点复核的问题
7. 本地预检结论：适合进入 PM 验收 / 需要人工复核 / 明显不完整

硬性限制：

- 不宣布任务 Accepted / Rework / Blocked。
- 不宣布任何资产 Frozen。
- 不宣布正式 MVP 开发准入。
- 不新增产品方向。
- 不修改项目结论。
- 不把本地预检当作 PM Review 或 Independent Review。
- 如果输入被截断，需要在“需要 PM 重点复核的问题”中提示 PM 对原文做定向复核。

以下是输入材料：

{files_block}
""".strip()


def ollama_generate(
    *,
    url: str,
    model: str,
    prompt: str,
    num_ctx: int,
    num_predict: int,
    timeout: int,
) -> tuple[str, dict]:
    endpoint = url.rstrip("/") + "/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.2,
            "top_p": 0.9,
            "num_ctx": num_ctx,
            "num_predict": num_predict,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8", errors="replace"))
    return body.get("response", "").strip(), body


def summarize_ollama_body(body: dict) -> str:
    """Return a compact debug summary without dumping huge context arrays."""
    if not isinstance(body, dict):
        return f"- 原始响应类型：`{type(body).__name__}`"

    lines = [
        f"- 响应字段：`{', '.join(sorted(body.keys()))}`",
        f"- done：`{body.get('done')}`",
        f"- done_reason：`{body.get('done_reason')}`",
        f"- response_len：`{len(body.get('response', '') or '')}`",
        f"- thinking_len：`{len(body.get('thinking', '') or '')}`",
        f"- prompt_eval_count：`{body.get('prompt_eval_count')}`",
        f"- eval_count：`{body.get('eval_count')}`",
        f"- total_duration：`{body.get('total_duration')}`",
    ]
    if body.get("error"):
        lines.append(f"- error：`{body.get('error')}`")
    if body.get("message"):
        lines.append(f"- message_type：`{type(body.get('message')).__name__}`")
    return "\n".join(lines)


def response_is_useful(response: str, body: dict, num_ctx: int) -> tuple[bool, str]:
    compact = response.strip()
    if len(compact) < MIN_USEFUL_RESPONSE_CHARS:
        return False, "输出过短，无法作为有效预检。"
    if body.get("done_reason") == "length" and body.get("prompt_eval_count") == num_ctx:
        return False, "上下文窗口被输入吃满，模型没有足够生成空间。"
    return True, ""


def ollama_health(url: str, timeout: int) -> tuple[bool, str]:
    endpoint = url.rstrip("/") + "/api/tags"
    request = urllib.request.Request(endpoint, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read().decode("utf-8", errors="replace")
        return True, body
    except Exception as exc:  # noqa: BLE001 - CLI health should report all failures.
        return False, str(exc)


def write_report(
    *,
    root: Path,
    task_id: str,
    artifact_path: Path,
    model: str,
    url: str,
    content: str,
    source_paths: list[Path],
    status: str,
) -> Path:
    out_dir = root / "lifeos" / "local_prechecks"
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact_stem = artifact_path.stem
    out_path = out_dir / f"{task_id}_{artifact_stem}_local_precheck.md"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sources = "\n".join(f"- `{path}`" for path in source_paths)
    report = f"""# {task_id} Local Precheck

- 生成时间：{now}
- 本地模型：`{model}`
- Ollama 地址：`{url}`
- 预检状态：{status}
- 被预检文件：`{artifact_path}`

## 输入文件

{sources}

## 本地预检说明

本文件由本地模型生成，只作为 `Local Precheck / 本地预检`。它不是 PM Review，不是 Independent Review，不代表 Accepted、Frozen 或 MVP 准入。

## 预检结果

{content}
"""
    out_path.write_text(report, encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Call local Ollama qwen3:14b for LifeOS low-risk precheck."
    )
    parser.add_argument(
        "artifact",
        nargs="?",
        help="交付物或评审文件路径，例如 lifeos/deliverables/LIFEOS-P2-013_xxx.md",
    )
    parser.add_argument("--task-id", help="手动指定 LIFEOS 任务 ID。")
    parser.add_argument(
        "--url",
        default=os.environ.get("LIFEOS_LOCAL_LLM_URL", DEFAULT_OLLAMA_URL),
        help=f"Ollama 地址，默认 {DEFAULT_OLLAMA_URL}",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("LIFEOS_LOCAL_LLM_MODEL", DEFAULT_MODEL),
        help=f"Ollama 模型，默认 {DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--num-ctx",
        type=int,
        default=int(os.environ.get("LIFEOS_LOCAL_LLM_NUM_CTX", DEFAULT_NUM_CTX)),
        help=f"Ollama num_ctx，默认 {DEFAULT_NUM_CTX}",
    )
    parser.add_argument(
        "--num-predict",
        type=int,
        default=int(os.environ.get("LIFEOS_LOCAL_LLM_NUM_PREDICT", DEFAULT_NUM_PREDICT)),
        help=f"Ollama num_predict，默认 {DEFAULT_NUM_PREDICT}",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"请求超时时间秒数，默认 {DEFAULT_TIMEOUT}",
    )
    parser.add_argument(
        "--health",
        action="store_true",
        help="只测试 Ollama 连接，不生成预检报告。",
    )
    args = parser.parse_args()

    root = project_root()

    if args.health:
        ok, message = ollama_health(args.url, min(args.timeout, 30))
        if ok:
            print(f"OK: Ollama reachable at {args.url}")
            print(message[:1000])
            return 0
        print(f"FAILED: Ollama not reachable at {args.url}")
        print(message)
        return 1

    if not args.artifact:
        parser.error("需要提供 artifact 路径，或使用 --health 测试连接。")

    artifact_path = resolve_path(root, args.artifact)
    if not artifact_path.exists():
        print(f"ERROR: 文件不存在：{artifact_path}", file=sys.stderr)
        return 2

    task_id = args.task_id or find_task_id(str(artifact_path))
    if not task_id:
        print("ERROR: 无法从路径识别 LIFEOS 任务 ID，请使用 --task-id。", file=sys.stderr)
        return 2

    task_card = find_task_card(root, task_id)
    source_paths: list[tuple[str, Path]] = []

    current_status = optional_file(root, "lifeos/CURRENT_STATUS.md")
    if current_status:
        source_paths.append(("CURRENT_STATUS", current_status))
    if task_card:
        source_paths.append(("TASK_CARD", task_card))
    else:
        print(f"WARNING: 未找到任务卡：lifeos/tasks/{task_id}_*.md", file=sys.stderr)
    source_paths.append(("ARTIFACT", artifact_path))

    session_template = optional_file(root, "lifeos/templates/SESSION_REPORT_TEMPLATE.md")
    if session_template:
        source_paths.append(("SESSION_REPORT_TEMPLATE", session_template))

    source_sections: list[tuple[str, Path, str, bool]] = []
    for label, path in source_paths:
        content, clipped = read_text_limited(path)
        source_sections.append((label, path, content, clipped))

    prompt = build_prompt(
        task_id=task_id,
        artifact_path=artifact_path,
        source_sections=source_sections,
    )

    try:
        response, raw_body = ollama_generate(
            url=args.url,
            model=args.model,
            prompt=prompt,
            num_ctx=args.num_ctx,
            num_predict=args.num_predict,
            timeout=args.timeout,
        )
        status = "Completed"
        useful, invalid_reason = response_is_useful(response, raw_body, args.num_ctx)
        if not useful:
            response = textwrap.dedent(
                f"""
                本地模型返回结果不可用，请 PM 按原流程直接复核原文。

                - 判定原因：{invalid_reason}

                ## 原始响应摘要

                {summarize_ollama_body(raw_body)}
                """
            ).strip()
            status = "Invalid Response"
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        response = textwrap.dedent(
            f"""
            本地预检未完成：无法调用本地模型。

            - 错误：`{exc}`
            - 处理建议：跳过本地预检，PM 按原流程读取任务卡、交付物和必要账本完成验收。
            """
        ).strip()
        status = "Skipped / Local Model Unavailable"

    out_path = write_report(
        root=root,
        task_id=task_id,
        artifact_path=artifact_path,
        model=args.model,
        url=args.url,
        content=response,
        source_paths=[path for _, path in source_paths],
        status=status,
    )
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

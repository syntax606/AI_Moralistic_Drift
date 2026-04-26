# project/src/generate.py
from __future__ import annotations
import gc, hashlib, json, time
from pathlib import Path
from typing import List, Dict

from src.config import *
from src.prompt_schema import (
    SYSTEM_MSG,
    render_rule_prompt,
    render_commitment_prompt,
    render_messages_from_history,
)
from src.models_chat import HFChatModel

def run(out_path="data/generations.jsonl"):

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)

    scripts = []
    for f in SCRIPTS_FILES:
        scripts += [json.loads(l) for l in Path(f).read_text().splitlines() if l]

    with open(out_path, "a", encoding="utf-8") as fh:

        for run_id in RUN_IDS:
            for short, model_id in MODEL_SPECS:

                model = HFChatModel(model_id)

                try:
                    for script in scripts:
                        for order in ORDERS:
                            for history_mode in HISTORY_MODES:

                                steps = FORWARD_PATH if order == "forward" else REVERSE_PATH

                                history = []

                                conv_id = f"{short}|{script['script_id']}|{order}|{history_mode}|run{run_id}"

                                for turn, step in enumerate(steps, 1):

                                    if step == "R":
                                        prompt = render_rule_prompt(DOMAIN_RULE_PROMPTS[script["domain"]], script)
                                        step_type = "rule"
                                    else:
                                        prompt = render_commitment_prompt(script, int(step[1]))
                                        step_type = "commitment"

                                    # Fix #3: use render_messages_from_history for both modes.
                                    # In no_history mode history stays [], so this correctly
                                    # sends only [system, user] each turn.
                                    messages = render_messages_from_history(
                                        history if history_mode == "history" else [],
                                        prompt
                                    )

                                    resp, in_len, out_len, hit_max = model.generate(messages, **GEN_PRIMARY)

                                    fh.write(json.dumps({
                                        "conversation_id": conv_id,
                                        "model": short,
                                        "script_id": script["script_id"],
                                        "domain": script["domain"],
                                        "order": order,
                                        "history_mode": history_mode,
                                        "run_id": run_id,
                                        "step": step,
                                        "step_type": step_type,
                                        "turn": turn,
                                        "prompt": prompt,
                                        "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                                        "response": resp,
                                        "input_len": in_len,
                                        "output_len": out_len,
                                        "hit_max_tokens": hit_max,
                                        "timestamp": time.time()
                                    }) + "\n")

                                    if history_mode == "history":
                                        history += [
                                            {"role": "user", "content": prompt},
                                            {"role": "assistant", "content": resp},
                                        ]

                finally:
                    model.unload()
                    gc.collect()

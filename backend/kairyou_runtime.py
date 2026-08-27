## Copyright 2024 Kakusui LLC (https://kakusui.org) (https://github.com/Kakusui) (https://github.com/Kakusui/kakusui.org)
## Use of this source code is governed by an GNU Affero General Public License v3.0
## license that can be found in the LICENSE file.

import asyncio
import atexit
import itertools
import json
import multiprocessing
import os
import threading
import time
from contextlib import redirect_stderr, redirect_stdout
from functools import cache
from importlib.metadata import distribution
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from filelock import FileLock, Timeout as FileLockTimeout


MAX_TEXT_LENGTH = 175_000
MAX_REPLACEMENTS_JSON_BYTES = 1_000_000
MAX_TOTAL_REPLACEMENT_ENTRIES = 5_000
MAX_TOTAL_REPLACEMENT_CHARACTERS = 500_000
MAX_REPLACEMENT_KEY_LENGTH = 512
MAX_REPLACEMENT_VALUE_LENGTH = 1_024
MAX_NAME_PARTS = 4
MAX_HONORIFICS = 32
MAX_REPLACEMENT_OPERATIONS = 100_000_000
MAX_ESTIMATED_PRIMITIVE_RULES = 250_000
MAX_WHITELIST_COMPARISONS = 250_000
MAX_NER_INPUT_CHARACTERS = 500_000
NER_CALL_OVERHEAD_CHARACTERS = 2_000
MAX_OUTPUT_LENGTH = 1_000_000
MAX_LOG_LENGTH = 250_000
KAIRYOU_QUEUE_TIMEOUT_SECONDS = 2.0
KAIRYOU_EXECUTION_TIMEOUT_SECONDS = 45.0
KAIRYOU_WORKER_MEMORY_LIMIT_MB = 3_072
KAIRYOU_PROCESS_LOCK_PATH = os.environ.get(
    "KAIRYOU_PROCESS_LOCK_PATH",
    "/tmp/kakusui-kairyou.lock",
)

KUDASAI_SECTIONS = {
    "kutouten",
    "unicode",
    "phrases",
    "single_words",
    "enhanced_check_whitelist",
    "full_names",
    "single_names",
    "name_like",
    "honorifics",
}
FUKUIN_SECTIONS = {
    "specials",
    "basic",
    "names",
    "single-names",
    "full-names",
    "name-like",
    "honorifics",
}
KUDASAI_NAME_SECTIONS = {
    "enhanced_check_whitelist",
    "full_names",
    "single_names",
    "name_like",
}
FUKUIN_ALL_NAME_SECTIONS = {"names", "full-names"}
FUKUIN_SINGLE_NAME_SECTIONS = {"single-names", "name-like"}
KUDASAI_RULE_ORDER = (
    ("kutouten", False, False, True),
    ("unicode", False, False, True),
    ("enhanced_check_whitelist", True, True, True),
    ("full_names", True, True, True),
    ("single_names", True, True, True),
    ("name_like", True, True, False),
    ("phrases", False, False, True),
    ("single_words", False, False, True),
)
FUKUIN_RULE_ORDER = (
    ("specials", False, False, True),
    ("basic", False, False, True),
    ("names", True, True, True),
    ("full-names", True, True, True),
    ("single-names", True, False, True),
    ("name-like", True, False, False),
)


class InvalidKairyouPayload(ValueError):
    pass


class KairyouBusyError(RuntimeError):
    pass


class KairyouExecutionTimeout(RuntimeError):
    pass


class KairyouWorkerError(RuntimeError):
    pass


class KairyouProcessingError(RuntimeError):
    def __init__(self, error_type: str, message: str):
        super().__init__(message)
        self.error_type = error_type


class _KairyouResourceLimit(BaseException):
    """Escape Kairyou's broad Exception handlers for bounded resource use."""

    pass


class _KairyouOutputLimit(_KairyouResourceLimit):
    """Escape Kairyou's broad Exception handlers before an unsafe allocation."""

    pass


class _KairyouNerLimit(_KairyouResourceLimit):
    pass


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InvalidKairyouPayload(f"Duplicate replacement JSON key: {key}")
        result[key] = value
    return result


def _name_parts(value: str) -> list[str]:
    parts = value.split(" ")
    if not parts or any(not part or any(character.isspace() for character in part) for part in parts):
        raise InvalidKairyouPayload("Names must use single ASCII spaces between parts")
    return parts


def _validate_string(value: Any, *, label: str, maximum: int) -> str:
    if not isinstance(value, str) or not value:
        raise InvalidKairyouPayload(f"{label} must be a non-empty string")
    if len(value) > maximum:
        raise InvalidKairyouPayload(f"{label} is too long")
    return value


def _name_variant_count(parts: int) -> int:
    # Kairyou emits all name subsets of size >= 2 with two separators, plus
    # first-name and last-name variants.
    return 2 * ((1 << parts) - parts - 1) + 2


def _iter_name_variants(
    english_name: str,
    japanese_name: str,
    all_names: bool,
):
    english_parts = _name_parts(english_name)
    japanese_parts = _name_parts(japanese_name)
    if all_names:
        indices = range(len(english_parts))
        for size in range(2, len(english_parts) + 1):
            for selected in itertools.combinations(indices, size):
                english_variant = " ".join(english_parts[index] for index in selected)
                for separator in ("\u30fb", ""):
                    yield (
                        english_variant,
                        separator.join(japanese_parts[index] for index in selected),
                    )
        yield english_parts[0], japanese_parts[0]
        yield english_parts[-1], japanese_parts[-1]
    else:
        yield english_parts[-1], japanese_parts[-1]


def _is_katakana_only(value: str) -> bool:
    return bool(value) and all("\u30a0" <= character <= "\u30fe" for character in value)


@cache
def _get_katakana_words() -> frozenset[str]:
    # Loading the public data file directly avoids importing SpaCy/Kairyou into
    # the ASGI process; model execution remains isolated in the child worker.
    words_path = Path(
        distribution("kairyou").locate_file("kairyou/words.py")
    )
    source = words_path.read_text(encoding="utf-8")
    marker = '_katakana_words = """'
    if marker not in source:
        raise RuntimeError("Kairyou Katakana dictionary format is unsupported")
    words_text = source.split(marker, 1)[1].split('"""', 1)[0]
    return frozenset(words_text.strip().splitlines())


def _validate_replacement_growth(
    text: str,
    replacements: dict[str, dict[str, str | list[str]]],
    rule_order: tuple[tuple[str, bool, bool, bool], ...],
    *,
    apply_name_bases: bool,
) -> int:
    """Simulate deterministic replacements and bound deferred Katakana work."""
    shadow_text = text
    scan_budget = 0

    def apply_exact(search: str, replacement: str) -> None:
        nonlocal scan_budget, shadow_text
        scan_budget += len(shadow_text)
        if scan_budget > MAX_REPLACEMENT_OPERATIONS:
            raise InvalidKairyouPayload("Replacement rules are too complex for this input text")
        occurrences = shadow_text.count(search)
        projected_length = len(shadow_text) + occurrences * (
            len(replacement) - len(search)
        )
        if projected_length > MAX_OUTPUT_LENGTH:
            raise InvalidKairyouPayload("Replacement rules can produce too much output")
        shadow_text = shadow_text.replace(search, replacement)

    def name_rules(
        english_name: str,
        raw_japanese_name: str | list[str],
        all_names: bool,
        replace_base: bool,
    ):
        japanese_name = (
            " ".join(raw_japanese_name)
            if isinstance(raw_japanese_name, list)
            else raw_japanese_name
        )
        for english_variant, japanese_variant in _iter_name_variants(
            english_name,
            japanese_name,
            all_names,
        ):
            for honorific, honorific_english in replacements["honorifics"].items():
                yield (
                    f"{japanese_variant}{honorific}",
                    f"{english_variant}-{honorific_english}",
                )
            if replace_base and apply_name_bases:
                yield japanese_variant, english_variant

    katakana_entries: list[tuple[int, bool, str, str | list[str], bool, bool]] = []

    # Kairyou always performs this pass. Katakana names are deferred to its
    # second pass, while non-name rules are applied here regardless of script.
    for section_name, is_name, all_names, replace_base in rule_order:
        for search, replacement in replacements[section_name].items():
            if is_name:
                japanese_name = (
                    " ".join(replacement) if isinstance(replacement, list) else replacement
                )
                if _is_katakana_only(japanese_name):
                    katakana_entries.append(
                        (
                            len(japanese_name),
                            True,
                            search,
                            replacement,
                            all_names,
                            replace_base,
                        )
                    )
                    continue
                for name_search, name_replacement in name_rules(
                    search,
                    replacement,
                    all_names,
                    replace_base,
                ):
                    apply_exact(name_search, name_replacement)
            else:
                apply_exact(search, replacement)
                if _is_katakana_only(search):
                    katakana_entries.append(
                        (len(search), False, search, replacement, False, True)
                    )

    # Match Kairyou's length-descending Katakana pass. Its bundled word list is
    # part of the pinned dependency and determines which entries are skipped.
    katakana_words = _get_katakana_words() if katakana_entries else frozenset()
    katakana_entries.sort(key=lambda entry: entry[0], reverse=True)
    for _, is_name, search, replacement, all_names, replace_base in katakana_entries:
        japanese_name = (
            " ".join(replacement)
            if is_name and isinstance(replacement, list)
            else replacement
            if is_name
            else search
        )
        if japanese_name in katakana_words:
            continue
        if is_name:
            deferred_rules = name_rules(search, replacement, all_names, replace_base)
        else:
            deferred_rules = ((search, replacement),)

        for deferred_search, deferred_replacement in deferred_rules:
            apply_exact(deferred_search, deferred_replacement)

    # Match Kudasai's final missing-space correction for supported two-part
    # full names.
    if "full_names" in replacements:
        for english_name in replacements["full_names"]:
            first_name, last_name = _name_parts(english_name)
            apply_exact(
                first_name + last_name,
                f"{first_name} {last_name}",
            )

    return len(shadow_text)


def parse_and_validate_replacements(
    replacements_json: str,
    text: str,
) -> dict[str, dict[str, str | list[str]]]:
    """Parse a Kudasai/Fukuin replacement document and bound its work."""
    if len(replacements_json.encode("utf-8")) > MAX_REPLACEMENTS_JSON_BYTES:
        raise InvalidKairyouPayload("Replacement JSON is too large")

    try:
        parsed = json.loads(replacements_json, object_pairs_hook=_reject_duplicate_keys)
    except InvalidKairyouPayload:
        raise
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        raise InvalidKairyouPayload("Replacement JSON is invalid") from error

    if not isinstance(parsed, dict):
        raise InvalidKairyouPayload("Replacement JSON must be an object")

    section_names = set(parsed)
    if section_names == KUDASAI_SECTIONS:
        is_kudasai = True
        name_sections = KUDASAI_NAME_SECTIONS
        all_name_sections = KUDASAI_NAME_SECTIONS
        rule_order = KUDASAI_RULE_ORDER
    elif section_names == FUKUIN_SECTIONS:
        is_kudasai = False
        name_sections = FUKUIN_ALL_NAME_SECTIONS | FUKUIN_SINGLE_NAME_SECTIONS
        all_name_sections = FUKUIN_ALL_NAME_SECTIONS
        rule_order = FUKUIN_RULE_ORDER
    else:
        raise InvalidKairyouPayload("Replacement JSON has missing or unknown sections")

    for section_name, section in parsed.items():
        if not isinstance(section, dict):
            raise InvalidKairyouPayload(f"Replacement section {section_name} must be an object")

    # Validate every primitive type before order-dependent cross-section work.
    for section_name, section in parsed.items():
        is_name_section = section_name in name_sections
        for raw_key, raw_value in section.items():
            _validate_string(
                raw_key,
                label=f"Replacement key in {section_name}",
                maximum=MAX_REPLACEMENT_KEY_LENGTH,
            )
            if is_name_section and isinstance(raw_value, list):
                if not raw_value or len(raw_value) > MAX_NAME_PARTS:
                    raise InvalidKairyouPayload("Name replacement has an invalid number of parts")
                for part in raw_value:
                    _validate_string(
                        part,
                        label=f"Name part in {section_name}",
                        maximum=MAX_REPLACEMENT_VALUE_LENGTH,
                    )
            else:
                _validate_string(
                    raw_value,
                    label=f"Replacement value in {section_name}",
                    maximum=MAX_REPLACEMENT_VALUE_LENGTH,
                )

    name_entry_count = sum(len(parsed[section]) for section in name_sections)
    whitelist_count = len(parsed.get("enhanced_check_whitelist", {}))
    whitelist_comparisons = (
        MAX_NAME_PARTS * name_entry_count * max(1, whitelist_count)
    )
    if whitelist_comparisons > MAX_WHITELIST_COMPARISONS:
        raise InvalidKairyouPayload("Name whitelist rules are too complex")

    honorific_count = len(parsed["honorifics"])
    if honorific_count > MAX_HONORIFICS:
        raise InvalidKairyouPayload("Too many honorific replacement rules")

    total_entries = 0
    total_characters = 0
    estimated_operations = 0
    estimated_ner_characters = 0
    text_lines = text.split("\n")

    for section_name, section in parsed.items():
        is_name_section = section_name in name_sections
        for raw_key, raw_value in section.items():
            key = _validate_string(
                raw_key,
                label=f"Replacement key in {section_name}",
                maximum=MAX_REPLACEMENT_KEY_LENGTH,
            )
            total_entries += 1
            total_characters += len(key)

            if is_name_section:
                if isinstance(raw_value, list):
                    if not raw_value or len(raw_value) > MAX_NAME_PARTS:
                        raise InvalidKairyouPayload("Name replacement has an invalid number of parts")
                    values = [
                        _validate_string(
                            part,
                            label=f"Name part in {section_name}",
                            maximum=MAX_REPLACEMENT_VALUE_LENGTH,
                        )
                        for part in raw_value
                    ]
                    if any(len(_name_parts(value)) != 1 for value in values):
                        raise InvalidKairyouPayload("Each name list item must be one name part")
                    japanese_name = " ".join(values)
                else:
                    japanese_name = _validate_string(
                        raw_value,
                        label=f"Name value in {section_name}",
                        maximum=MAX_REPLACEMENT_VALUE_LENGTH,
                    )

                english_parts = _name_parts(key)
                japanese_parts = _name_parts(japanese_name)
                if not english_parts or len(english_parts) != len(japanese_parts):
                    raise InvalidKairyouPayload("English and Japanese name part counts must match")
                if len(english_parts) > MAX_NAME_PARTS:
                    raise InvalidKairyouPayload("Names may contain at most four parts")
                if section_name == "full_names" and len(english_parts) != 2:
                    raise InvalidKairyouPayload("Kudasai full_names entries must have two parts")

                variants = (
                    _name_variant_count(len(english_parts))
                    if section_name in all_name_sections
                    else 1
                )
                estimated_operations += variants * (honorific_count + 1)
                if estimated_operations > MAX_ESTIMATED_PRIMITIVE_RULES:
                    raise InvalidKairyouPayload("Too many generated replacement rules")
                replace_base = next(
                    base_enabled
                    for rule_section, _, _, base_enabled in rule_order
                    if rule_section == section_name
                )
                if replace_base:
                    whitelist_values = parsed.get(
                        "enhanced_check_whitelist",
                        {},
                    ).values()
                    is_whitelisted = any(
                        part in whitelist_entry
                        for whitelist_entry in whitelist_values
                        for part in japanese_parts
                    )
                    conditional_variants = [
                        japanese_variant
                        for _, japanese_variant in _iter_name_variants(
                            key,
                            japanese_name,
                            section_name in all_name_sections,
                        )
                        if (
                            is_whitelisted
                            or (is_kudasai and section_name == "enhanced_check_whitelist")
                            or len(japanese_variant) == 1
                            or _is_katakana_only(japanese_name)
                        )
                    ]
                    for japanese_variant in conditional_variants:
                        # Each enhanced replacement splits/scans the full input,
                        # then invokes SpaCy once for every matching line.
                        estimated_ner_characters += len(text)
                        estimated_ner_characters += sum(
                            len(line) + NER_CALL_OVERHEAD_CHARACTERS
                            for line in text_lines
                            if japanese_variant in line
                        )
                        if estimated_ner_characters > MAX_NER_INPUT_CHARACTERS:
                            raise InvalidKairyouPayload(
                                "Name replacement rules are too complex for this input text"
                            )
                total_characters += len(japanese_name)
            else:
                value = _validate_string(
                    raw_value,
                    label=f"Replacement value in {section_name}",
                    maximum=MAX_REPLACEMENT_VALUE_LENGTH,
                )
                # Non-name Katakana entries can be visited by both replacement
                # passes, so budget for the worst case rather than classifying
                # attacker-controlled Unicode here.
                estimated_operations += 2
                if estimated_operations > MAX_ESTIMATED_PRIMITIVE_RULES:
                    raise InvalidKairyouPayload("Too many generated replacement rules")
                total_characters += len(value)

            if total_entries > MAX_TOTAL_REPLACEMENT_ENTRIES:
                raise InvalidKairyouPayload("Too many replacement rules")
            if total_characters > MAX_TOTAL_REPLACEMENT_CHARACTERS:
                raise InvalidKairyouPayload("Replacement rules contain too much text")

    operation_budget = max(1, len(text)) * estimated_operations
    if operation_budget > MAX_REPLACEMENT_OPERATIONS:
        raise InvalidKairyouPayload("Replacement rules are too complex for this input text")
    # NER-based name replacements are data-dependent. Evaluate both extremes:
    # retaining every conditional name and replacing every conditional name.
    # The child also guards every primitive replacement, which covers mixed
    # branches that cannot be represented without exponential simulation.
    retained_name_length = _validate_replacement_growth(
        text,
        parsed,
        rule_order,
        apply_name_bases=False,
    )
    replaced_name_length = _validate_replacement_growth(
        text,
        parsed,
        rule_order,
        apply_name_bases=True,
    )

    if "full_names" in parsed:
        postprocess_scans = len(parsed["full_names"]) * max(
            retained_name_length,
            replaced_name_length,
        )
        if postprocess_scans > MAX_REPLACEMENT_OPERATIONS:
            raise InvalidKairyouPayload("Full-name postprocessing is too complex")

    return parsed


def _set_worker_memory_limit() -> None:
    try:
        import resource

        memory_bytes = KAIRYOU_WORKER_MEMORY_LIMIT_MB * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
    except (ImportError, OSError, ValueError):
        # Windows development is still protected by timeout/output bounds. The
        # production Linux container enforces RLIMIT_AS here.
        return


def _install_kairyou_runtime_guards(Kairyou: Any) -> None:
    """Bound library string replacements and replace its quadratic postpass."""
    original_replace_single_word = Kairyou._replace_single_word
    original_enhanced_replace = Kairyou._perform_enhanced_replace
    ner_work_used = 0

    def reset_runtime_budgets() -> None:
        nonlocal ner_work_used
        ner_work_used = 0

    def ensure_bounded_replacement(search: str, replacement: str) -> None:
        current_text = Kairyou.text_to_preprocess
        occurrences = current_text.count(search)
        projected_length = len(current_text) + occurrences * (
            len(replacement) - len(search)
        )
        if projected_length > MAX_OUTPUT_LENGTH:
            raise _KairyouOutputLimit("Preprocessed output is too large")

    def guarded_enhanced_replace(
        japanese: str,
        replacement: str,
        tracker: Any = None,
    ) -> int:
        nonlocal ner_work_used
        # NER may select any subset of occurrences, so checking all occurrences
        # is a safe upper bound before model inference or string allocation.
        ensure_bounded_replacement(japanese, replacement)
        current_text = Kairyou.text_to_preprocess
        matching_line_work = sum(
            len(line) + NER_CALL_OVERHEAD_CHARACTERS
            for line in current_text.split("\n")
            if japanese in line
        )
        ner_work_used += len(current_text) + matching_line_work
        if ner_work_used > MAX_NER_INPUT_CHARACTERS:
            raise _KairyouNerLimit("Name replacement work exceeds the resource limit")
        return original_enhanced_replace(japanese, replacement, tracker)

    def guarded_replace_single_word(
        word: str,
        replacement: str,
        is_potential_name: bool,
        is_katakana: bool = False,
        tracker: Any = None,
        skip_honorific_tracking: bool = False,
    ) -> int:
        ensure_bounded_replacement(word, replacement)
        return original_replace_single_word(
            word,
            replacement,
            is_potential_name,
            is_katakana,
            tracker,
            skip_honorific_tracking,
        )

    def bounded_missing_space_correction() -> None:
        if Kairyou._json_type != "kudasai":
            return
        for full_name in Kairyou._replacement_json["full_names"]:
            first_name, last_name = full_name.split(" ")
            joined_name = first_name + last_name
            spaced_name = f"{first_name} {last_name}"
            ensure_bounded_replacement(joined_name, spaced_name)
            Kairyou.text_to_preprocess = Kairyou.text_to_preprocess.replace(
                joined_name,
                spaced_name,
            )

    Kairyou._perform_enhanced_replace = staticmethod(guarded_enhanced_replace)
    Kairyou._replace_single_word = staticmethod(guarded_replace_single_word)
    Kairyou._kakusui_reset_runtime_budgets = staticmethod(reset_runtime_budgets)
    Kairyou._perform_missing_space_correction = staticmethod(
        bounded_missing_space_correction
    )


def _kairyou_worker_main(connection: Any) -> None:
    _set_worker_memory_limit()

    with open(os.devnull, "w", encoding="utf-8") as output_sink:
        Kairyou = None
        while True:
            request_data = connection.recv()
            if request_data is None:
                return

            request_id, text, replacements = request_data
            try:
                if Kairyou is None:
                    from kairyou import Kairyou as KairyouClient

                    Kairyou = KairyouClient
                    _install_kairyou_runtime_guards(Kairyou)
                Kairyou._kakusui_reset_runtime_budgets()
                with redirect_stdout(output_sink), redirect_stderr(output_sink):
                    result = Kairyou.preprocess(
                        text,
                        replacements,
                        persist=False,
                        discard_ner_objects=False,
                    )

                preprocessed_text, preprocessing_log, error_log = result
                if not all(isinstance(value, str) for value in result):
                    raise TypeError("Kairyou returned an invalid response")
                if len(preprocessed_text) > MAX_OUTPUT_LENGTH:
                    raise OverflowError("Preprocessed output is too large")
                if len(preprocessing_log) > MAX_LOG_LENGTH or len(error_log) > MAX_LOG_LENGTH:
                    raise OverflowError("Preprocessing log is too large")

                connection.send((request_id, "ok", result))
            except _KairyouResourceLimit as error:
                connection.send(
                    (request_id, "error", ("ResourceLimit", str(error)))
                )
            except Exception as error:
                error_message = str(error)[:500]
                connection.send(
                    (request_id, "error", (type(error).__name__, error_message))
                )


class _KairyouWorker:
    def __init__(self) -> None:
        self._context = multiprocessing.get_context("spawn")
        self._state_lock = threading.Lock()
        self._process: multiprocessing.Process | None = None
        self._connection: Any | None = None

    def _close_connection_locked(self) -> None:
        if self._connection is not None:
            self._connection.close()
        self._connection = None

    def _stop_locked(self, graceful: bool) -> None:
        process = self._process
        if process is not None and process.is_alive():
            if graceful and self._connection is not None:
                try:
                    self._connection.send(None)
                except (BrokenPipeError, EOFError, OSError):
                    pass
                process.join(timeout=2.0)
            if process.is_alive():
                process.terminate()
                process.join(timeout=2.0)
            if process.is_alive():
                process.kill()
                process.join(timeout=2.0)
        elif process is not None:
            process.join(timeout=0)
        self._process = None
        self._close_connection_locked()

    def stop(self, graceful: bool = True) -> None:
        with self._state_lock:
            self._stop_locked(graceful)

    def _ensure_started_locked(self) -> None:
        if self._process is not None and self._process.is_alive():
            return

        self._stop_locked(graceful=False)
        parent_connection, child_connection = self._context.Pipe()
        self._connection = parent_connection
        self._process = self._context.Process(
            target=_kairyou_worker_main,
            args=(child_connection,),
            daemon=True,
            name="kairyou-worker",
        )
        self._process.start()
        child_connection.close()

    def submit(self, text: str, replacements: dict[str, Any]) -> str:
        with self._state_lock:
            self._ensure_started_locked()
            if self._connection is None:
                raise KairyouWorkerError("Kairyou worker connection is unavailable")
            request_id = uuid4().hex
            try:
                self._connection.send((request_id, text, replacements))
            except (BrokenPipeError, EOFError, OSError) as error:
                self._stop_locked(graceful=False)
                raise KairyouWorkerError("Unable to submit Kairyou request") from error
            return request_id

    def poll(self) -> tuple[str, str, Any] | None:
        with self._state_lock:
            if self._process is None or not self._process.is_alive():
                self._stop_locked(graceful=False)
                raise KairyouWorkerError("Kairyou worker exited unexpectedly")
            if self._connection is None:
                raise KairyouWorkerError("Kairyou worker connection is unavailable")
            try:
                if self._connection.poll():
                    return self._connection.recv()
                return None
            except (BrokenPipeError, EOFError, OSError) as error:
                self._stop_locked(graceful=False)
                raise KairyouWorkerError("Unable to receive Kairyou response") from error


_worker = _KairyouWorker()
_request_lock = threading.Lock()
_process_lock = FileLock(KAIRYOU_PROCESS_LOCK_PATH, timeout=0)


async def _acquire_request_lock(timeout: float | None) -> bool:
    deadline = None if timeout is None else time.monotonic() + timeout
    while True:
        if _request_lock.acquire(blocking=False):
            return True
        if deadline is not None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False
            await asyncio.sleep(min(0.05, remaining))
        else:
            await asyncio.sleep(0.05)


async def _acquire_execution_locks(timeout: float) -> bool:
    deadline = time.monotonic() + timeout
    if not await _acquire_request_lock(timeout):
        return False
    try:
        while True:
            try:
                _process_lock.acquire(timeout=0)
                return True
            except FileLockTimeout:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                await asyncio.sleep(min(0.05, remaining))
    finally:
        if not _process_lock.is_locked:
            _request_lock.release()


def _release_execution_locks() -> None:
    _process_lock.release()
    _request_lock.release()


async def preprocess_in_worker(
    text: str,
    replacements: dict[str, Any],
    *,
    recycle_worker: bool = False,
) -> tuple[str, str, str]:
    if not await _acquire_execution_locks(KAIRYOU_QUEUE_TIMEOUT_SECONDS):
        raise KairyouBusyError("Kairyou is at its concurrency limit")

    try:
        if recycle_worker:
            _worker.stop(graceful=True)

        request_id = _worker.submit(text, replacements)
        deadline = time.monotonic() + KAIRYOU_EXECUTION_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            response = _worker.poll()
            if response is None:
                await asyncio.sleep(0.05)
                continue

            response_id, status, payload = response
            if response_id != request_id:
                _worker.stop(graceful=False)
                raise KairyouWorkerError("Kairyou worker protocol error")
            if status == "ok":
                return payload

            error_type, message = payload
            if error_type != "ResourceLimit":
                _worker.stop(graceful=False)
            raise KairyouProcessingError(error_type, message)

        _worker.stop(graceful=False)
        raise KairyouExecutionTimeout("Kairyou processing timed out")
    except asyncio.CancelledError:
        _worker.stop(graceful=False)
        raise
    finally:
        _release_execution_locks()


def shutdown_kairyou_worker() -> None:
    _worker.stop(graceful=True)


async def shutdown_kairyou_worker_when_idle(
    should_stop: Callable[[], bool] | None = None,
) -> bool:
    await _acquire_request_lock(timeout=None)
    try:
        if should_stop is not None and not should_stop():
            return False
        _worker.stop(graceful=True)
        return True
    finally:
        _request_lock.release()


atexit.register(shutdown_kairyou_worker)

import sys
import types
import unittest
from unittest.mock import patch

import kairyou_runtime


def blank_kudasai():
    return {section: {} for section in kairyou_runtime.KUDASAI_SECTIONS}


class KairyouPayloadTests(unittest.TestCase):
    def test_blank_supported_schema_is_accepted(self):
        payload = kairyou_runtime.json.dumps(blank_kudasai())
        parsed = kairyou_runtime.parse_and_validate_replacements(payload, "x" * 10_000)
        self.assertEqual(parsed, blank_kudasai())

    def test_empty_search_key_is_rejected(self):
        payload = blank_kudasai()
        payload["phrases"][""] = "large expansion"
        with self.assertRaises(kairyou_runtime.InvalidKairyouPayload):
            kairyou_runtime.parse_and_validate_replacements(
                kairyou_runtime.json.dumps(payload),
                "x" * 100,
            )

    def test_names_over_four_parts_are_rejected(self):
        payload = blank_kudasai()
        payload["full_names"]["one two three four five"] = ["1", "2", "3", "4", "5"]
        with self.assertRaises(kairyou_runtime.InvalidKairyouPayload):
            kairyou_runtime.parse_and_validate_replacements(
                kairyou_runtime.json.dumps(payload),
                "x" * 100,
            )

    def test_duplicate_nested_json_keys_are_rejected(self):
        sections = [
            f'"{section}":{{}}'
            for section in sorted(kairyou_runtime.KUDASAI_SECTIONS - {"phrases"})
        ]
        sections.append('"phrases":{"same":"first","same":"second"}')
        with self.assertRaises(kairyou_runtime.InvalidKairyouPayload):
            kairyou_runtime.parse_and_validate_replacements(
                "{" + ",".join(sections) + "}",
                "x" * 100,
            )

    def test_name_honorific_operation_budget_is_enforced(self):
        payload = blank_kudasai()
        payload["full_names"]["one two three four"] = ["1", "2", "3", "4"]
        payload["honorifics"] = {
            f"h{number}": f"honorific{number}"
            for number in range(kairyou_runtime.MAX_HONORIFICS)
        }
        with self.assertRaises(kairyou_runtime.InvalidKairyouPayload):
            kairyou_runtime.parse_and_validate_replacements(
                kairyou_runtime.json.dumps(payload),
                "x" * kairyou_runtime.MAX_TEXT_LENGTH,
            )

    def test_chained_output_expansion_is_rejected_before_processing(self):
        payload = blank_kudasai()
        payload["single_words"] = {
            "a": "b" * 1024,
            "b": "c" * 1024,
        }
        with self.assertRaises(kairyou_runtime.InvalidKairyouPayload):
            kairyou_runtime.parse_and_validate_replacements(
                kairyou_runtime.json.dumps(payload),
                "a" * 100,
            )

    def test_ner_miss_cannot_hide_later_output_expansion(self):
        payload = blank_kudasai()
        payload["single_names"] = {"x": "a"}
        payload["single_words"] = {"a": "b" * 1024}
        with self.assertRaises(kairyou_runtime.InvalidKairyouPayload):
            kairyou_runtime.parse_and_validate_replacements(
                kairyou_runtime.json.dumps(payload),
                "a" * 1001,
            )

    def test_excessive_ner_work_is_rejected(self):
        payload = blank_kudasai()
        payload["single_names"] = {
            f"name{number}": chr(0x4E00 + number)
            for number in range(21)
        }
        with self.assertRaises(kairyou_runtime.InvalidKairyouPayload):
            kairyou_runtime.parse_and_validate_replacements(
                kairyou_runtime.json.dumps(payload),
                "x" * 100_000,
            )

    def test_ner_line_call_overhead_is_bounded(self):
        payload = blank_kudasai()
        payload["single_names"] = {"name": "一"}
        with self.assertRaises(kairyou_runtime.InvalidKairyouPayload):
            kairyou_runtime.parse_and_validate_replacements(
                kairyou_runtime.json.dumps(payload),
                "一\n" * 1000,
            )

    def test_kudasai_full_name_requires_exactly_two_parts(self):
        payload = blank_kudasai()
        payload["full_names"]["one two three"] = ["1", "2", "3"]
        with self.assertRaises(kairyou_runtime.InvalidKairyouPayload):
            kairyou_runtime.parse_and_validate_replacements(
                kairyou_runtime.json.dumps(payload),
                "input",
            )

    def test_generated_name_rule_count_is_bounded_independently_of_text(self):
        payload = blank_kudasai()
        payload["single_names"] = {
            f"first{number} second{number} third{number} fourth{number}": [
                f"一{number}",
                f"二{number}",
                f"三{number}",
                f"四{number}",
            ]
            for number in range(400)
        }
        payload["honorifics"] = {
            f"h{number}": f"honorific{number}"
            for number in range(kairyou_runtime.MAX_HONORIFICS)
        }
        with self.assertRaises(kairyou_runtime.InvalidKairyouPayload):
            kairyou_runtime.parse_and_validate_replacements(
                kairyou_runtime.json.dumps(payload),
                "z",
            )

    def test_malformed_later_whitelist_is_rejected_independent_of_json_order(self):
        payload = {"single_names": {"name": "一"}}
        payload.update(
            {
                section: ({"invalid": 123} if section == "enhanced_check_whitelist" else {})
                for section in kairyou_runtime.KUDASAI_SECTIONS - {"single_names"}
            }
        )
        with self.assertRaises(kairyou_runtime.InvalidKairyouPayload):
            kairyou_runtime.parse_and_validate_replacements(
                kairyou_runtime.json.dumps(payload),
                "z",
            )


class KairyouWorkerTests(unittest.TestCase):
    def test_worker_resets_kairyou_globals_between_requests(self):
        calls = []

        class FakeKairyou:
            @staticmethod
            def _kakusui_reset_runtime_budgets():
                return None

            @staticmethod
            def preprocess(text, replacements, **kwargs):
                calls.append((text, replacements, kwargs))
                return text, "log", ""

        fake_module = types.ModuleType("kairyou")
        fake_module.Kairyou = FakeKairyou
        class FakeConnection:
            def __init__(self):
                self.requests = iter([
                    ("request-id", "input", blank_kudasai()),
                    None,
                ])
                self.responses = []

            def recv(self):
                return next(self.requests)

            def send(self, response):
                self.responses.append(response)

        connection = FakeConnection()

        with patch.dict(sys.modules, {"kairyou": fake_module}):
            with (
                patch.object(kairyou_runtime, "_set_worker_memory_limit"),
                patch.object(kairyou_runtime, "_install_kairyou_runtime_guards"),
            ):
                kairyou_runtime._kairyou_worker_main(connection)

        response_id, status, result = connection.responses[0]
        self.assertEqual((response_id, status), ("request-id", "ok"))
        self.assertEqual(result, ("input", "log", ""))
        self.assertFalse(calls[0][2]["persist"])
        self.assertFalse(calls[0][2]["discard_ner_objects"])

    def test_runtime_guard_stops_mixed_branch_expansion(self):
        class FakeKairyou:
            text_to_preprocess = "a" * 1001

            @staticmethod
            def _perform_enhanced_replace(*_args, **_kwargs):
                return 0

            @staticmethod
            def _replace_single_word(
                word,
                replacement,
                _is_potential_name,
                _is_katakana=False,
                _tracker=None,
                _skip_honorific_tracking=False,
            ):
                FakeKairyou.text_to_preprocess = (
                    FakeKairyou.text_to_preprocess.replace(word, replacement)
                )
                return 1

            @staticmethod
            def _perform_missing_space_correction():
                return None

        kairyou_runtime._install_kairyou_runtime_guards(FakeKairyou)
        with self.assertRaises(kairyou_runtime._KairyouOutputLimit):
            FakeKairyou._replace_single_word("a", "b" * 1024, False)

    def test_runtime_guard_charges_ner_work_introduced_by_prior_rule(self):
        class FakeKairyou:
            text_to_preprocess = "x\n" * 50_000

            @staticmethod
            def _perform_enhanced_replace(*_args, **_kwargs):
                raise AssertionError("NER must not run after its budget is exceeded")

            @staticmethod
            def _replace_single_word(
                word,
                replacement,
                _is_potential_name,
                _is_katakana=False,
                _tracker=None,
                _skip_honorific_tracking=False,
            ):
                FakeKairyou.text_to_preprocess = (
                    FakeKairyou.text_to_preprocess.replace(word, replacement)
                )
                return 1

            @staticmethod
            def _perform_missing_space_correction():
                return None

        kairyou_runtime._install_kairyou_runtime_guards(FakeKairyou)
        FakeKairyou._kakusui_reset_runtime_budgets()
        FakeKairyou._replace_single_word("x", "一", False)

        with self.assertRaises(kairyou_runtime._KairyouNerLimit):
            FakeKairyou._perform_enhanced_replace("一", "name")


class KairyouTimeoutTests(unittest.IsolatedAsyncioTestCase):
    async def test_controlled_resource_limit_keeps_worker_warm(self):
        class ResourceLimitedWorker:
            def __init__(self):
                self.stopped = False

            def submit(self, text, replacements):
                return "request-id"

            def poll(self):
                return (
                    "request-id",
                    "error",
                    ("ResourceLimit", "resource limit"),
                )

            def stop(self, graceful=True):
                self.stopped = True

        fake_worker = ResourceLimitedWorker()
        original_worker = kairyou_runtime._worker
        kairyou_runtime._worker = fake_worker
        try:
            with self.assertRaises(kairyou_runtime.KairyouProcessingError):
                await kairyou_runtime.preprocess_in_worker("input", blank_kudasai())
            self.assertFalse(fake_worker.stopped)
        finally:
            kairyou_runtime._worker = original_worker

    async def test_timeout_terminates_the_worker(self):
        class NeverRespondingWorker:
            def __init__(self):
                self.stopped = False
                self.submitted = kairyou_runtime.asyncio.Event()

            def submit(self, text, replacements):
                self.submitted.set()
                return "request-id"

            def poll(self):
                return None

            def stop(self, graceful=True):
                self.stopped = True

        fake_worker = NeverRespondingWorker()
        original_worker = kairyou_runtime._worker
        original_timeout = kairyou_runtime.KAIRYOU_EXECUTION_TIMEOUT_SECONDS
        kairyou_runtime._worker = fake_worker
        kairyou_runtime.KAIRYOU_EXECUTION_TIMEOUT_SECONDS = 0.01
        try:
            with self.assertRaises(kairyou_runtime.KairyouExecutionTimeout):
                await kairyou_runtime.preprocess_in_worker("input", blank_kudasai())
            self.assertTrue(fake_worker.stopped)
        finally:
            kairyou_runtime._worker = original_worker
            kairyou_runtime.KAIRYOU_EXECUTION_TIMEOUT_SECONDS = original_timeout

    async def test_cancellation_terminates_the_worker(self):
        class NeverRespondingWorker:
            def __init__(self):
                self.stopped = False
                self.submitted = kairyou_runtime.asyncio.Event()

            def submit(self, text, replacements):
                self.submitted.set()
                return "request-id"

            def poll(self):
                return None

            def stop(self, graceful=True):
                self.stopped = True

        fake_worker = NeverRespondingWorker()
        original_worker = kairyou_runtime._worker
        kairyou_runtime._worker = fake_worker
        try:
            task = kairyou_runtime.asyncio.create_task(
                kairyou_runtime.preprocess_in_worker("input", blank_kudasai())
            )
            await fake_worker.submitted.wait()
            task.cancel()
            with self.assertRaises(kairyou_runtime.asyncio.CancelledError):
                await task
            self.assertTrue(fake_worker.stopped)
        finally:
            kairyou_runtime._worker = original_worker


if __name__ == "__main__":
    unittest.main()

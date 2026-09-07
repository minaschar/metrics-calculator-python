"""Focused checks on what each metric counts.

The golden snapshots pin the exact numbers per fixture; these state the
intent in isolation and cover two things a fixture snapshot can't easily
show -- the inheritance-cycle guard and the default directory excludes.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

from _paths import FIXTURES_DIR

from metrics_calculator import AnalysisConfig, ClassMetrics, analyze


def _by_class(root: Path) -> dict[str, ClassMetrics]:
    result = analyze(root, AnalysisConfig())
    return {c.class_name: c for f in result.files for c in f.classes}


def test_dit_is_ancestor_count_and_order_independent() -> None:
    classes = _by_class(FIXTURES_DIR / "deep_inheritance")
    assert {name: c.complexity.dit for name, c in classes.items()} == {
        "Animal": 0,
        "Mammal": 1,
        "Dog": 2,
        "Puppy": 3,
    }


def test_dit_survives_inheritance_cycle(tmp_path: Path) -> None:
    (tmp_path / "m.py").write_text(
        textwrap.dedent(
            """
            class A(B):
                pass

            class B(A):
                pass
            """
        ),
        encoding="utf-8",
    )
    classes = _by_class(tmp_path)  # must not raise RecursionError
    assert set(classes) == {"A", "B"}
    assert all(c.complexity.dit >= 0 for c in classes.values())


def test_mpc_counts_each_call_site_once() -> None:
    # `save` is defined in two files and `Client` has two `store.save(...)`
    # call sites: MPC is the number of call sites, not sites x definitions.
    client = _by_class(FIXTURES_DIR / "mpc_cross_file")["Client"]
    assert client.coupling.mpc == 2


def test_async_methods_are_counted() -> None:
    fetcher = _by_class(FIXTURES_DIR / "async_methods")["Fetcher"]
    assert fetcher.size.nom == 3  # two async methods + one sync


def test_lcom_does_not_leak_across_nested_functions() -> None:
    # `_step` (nested in `build`) touches `self.total`; that use belongs to
    # `_step`'s scope, not `build`'s, so `build` and `run` share no field.
    widget = _by_class(FIXTURES_DIR / "nested_functions")["Widget"]
    assert widget.cohesion.lcom == 1


def test_annotated_and_augmented_class_attributes_are_counted() -> None:
    # limit:int, name:str, seen, Config.seen (in bump), self.cache
    config = _by_class(FIXTURES_DIR / "annotated_attrs")["Config"]
    assert config.size.wac == 5


def test_dotted_base_class_is_resolved() -> None:
    classes = _by_class(FIXTURES_DIR / "dotted_base")
    assert classes["Handler"].complexity.dit == 1
    assert classes["Component"].size.nocc == 1


def test_attribute_read_is_not_a_method_call() -> None:
    # `register(scheduler.run)` and `return scheduler.run` are reads, not calls.
    app = _by_class(FIXTURES_DIR / "attr_read_not_call")["App"]
    assert app.coupling.mpc == 0


def test_default_config_excludes_vendored_and_cache_dirs(tmp_path: Path) -> None:
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "real.py").write_text("class Real: pass\n", encoding="utf-8")
    for junk in (".venv/lib", "__pycache__", "node_modules/x", "build"):
        d = tmp_path / junk
        d.mkdir(parents=True)
        (d / "junk.py").write_text("class Junk: pass\n", encoding="utf-8")

    result = analyze(tmp_path, AnalysisConfig())
    names = {c.class_name for f in result.files for c in f.classes}
    assert names == {"Real"}
    assert result.noc == 1


def test_qmood_is_not_in_the_public_api() -> None:
    import metrics_calculator

    assert not hasattr(metrics_calculator, "QmoodMetrics")
    assert "qmood" not in metrics_calculator.ClassMetrics.__dataclass_fields__

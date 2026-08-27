#!/usr/bin/env python3
"""Append Closure-3-only runtime assertions to a disposable probe copy.

This tool never reads or writes the final candidate.  It adds a single test to
the supplied temporary `runtime.rs` and records no fixture content.
"""

from __future__ import annotations

import argparse
from pathlib import Path


TEST = r'''

#[cfg(test)]
mod closure3_matrix {
    use super::*;

    #[test]
    fn today_focus_is_empty_then_stable_for_one_many_and_tied_open_actions() {
        let base = paths().unwrap().root;
        fs::create_dir_all(&base).unwrap();
        let root = base.join(format!("closure3-focus-order-{}", now().unwrap()));
        let _ = fs::remove_dir_all(&root);
        let current = mode().unwrap();
        if current == InputMode::Synthetic { fs::create_dir(&root).unwrap(); }
        let p = Paths { db: root.join(DB), root, mode: current };
        assert!(today(&p).unwrap().todays_focus.is_none());
        write(&p, |conn| {
            let time = 424242_i64;
            for (suffix, confirmed) in [("a", time), ("b", time), ("c", time + 1)] {
                let candidate = format!("{}closure3-{suffix}", p.mode.candidate_prefix());
                let action = format!("{}closure3-{suffix}", p.mode.action_prefix());
                conn.execute("INSERT INTO candidate_actions(id,capture_id,candidate_text,candidate_state,created_at_ms) VALUES(?1,?2,'fixture','accepted',?3)", params![candidate, format!("{}fixture-{suffix}", p.mode.capture_prefix()), confirmed]) .map_err(sql)?;
                conn.execute("INSERT INTO actions(id,candidate_id,action_text,confirmation_kind,action_state,created_at_ms) VALUES(?1,?2,'fixture','accept','open',?3)", params![action, candidate, confirmed]) .map_err(sql)?;
            }
            Ok(())
        }).unwrap();
        let first = today(&p).unwrap();
        assert_eq!(first.confirmed_actions.len(), 3);
        let expected = format!("{}closure3-a", p.mode.action_prefix());
        assert_eq!(first.todays_focus.as_deref(), Some(expected.as_str()));
        let reopened = today(&p).unwrap();
        assert_eq!(first.todays_focus, reopened.todays_focus);
        assert_eq!(first.confirmed_actions.iter().map(|a| &a.action_id).collect::<Vec<_>>(), reopened.confirmed_actions.iter().map(|a| &a.action_id).collect::<Vec<_>>());
        let _ = fs::remove_dir_all(&p.root);
    }
}
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", type=Path, required=True)
    args = parser.parse_args()
    runtime = args.runtime.resolve()
    text = runtime.read_text(encoding="utf-8")
    if "mod closure3_matrix" in text:
        raise SystemExit("closure3 matrix already appended")
    runtime.write_text(text + TEST, encoding="utf-8")


if __name__ == "__main__":
    main()

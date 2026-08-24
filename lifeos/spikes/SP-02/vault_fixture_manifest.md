# SP-02 Synthetic Vault Fixture Manifest

The script rebuilds a disposable Vault containing multi-directory Markdown, normal/malformed/duplicate/unclosed frontmatter, tags, headings, explicit block IDs, Markdown links, wikilinks, embeds, attachment pointers, broken links, ambiguous same-name notes, same-content distinct files, non-UTF8 bytes, hidden content, `.obsidian`, excluded and withdrawn roots, and an out-of-root directory symlink. Runtime cases add/modify/delete files, omit an event, mutate while the app is offline, rename/move 20 files, copy then delete, modify then delete, become temporarily unreachable, recover and disconnect.

All text is deterministic synthetic sentinel data. The out-of-root target is still inside `lifeos/spikes/SP-02/work/`; its sentinel must never appear in logs.

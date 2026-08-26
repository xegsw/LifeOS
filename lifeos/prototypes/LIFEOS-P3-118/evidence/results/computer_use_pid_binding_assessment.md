# P3-118 Computer Use PID / Window Binding Assessment

## Frozen question

`ABF-P3-118-v1` requires every GUI operation to be performed only after a native helper has attested one unique, onscreen, layer-0 target window for the Chrome process started by the P3-118 runner. It also forbids an app selector, because an app-level selector can bind an existing Chrome instance rather than the runner-created PID/window.

## Observed local capability surface

The installed Computer Use module was initialized without selecting or querying any app. Its exposed operation names were `click`, `drag`, `get_app_state`, `list_apps`, `paste`, `perform_secondary_action`, `press_key`, `scroll`, `select_text`, `set_value`, `target`, and `type_text`. The available call contract requires an `app` target for GUI state and input operations. No PID parameter, native window-ID parameter, or operation that accepts the attestation helper's `{ pid, window_id }` output was exposed.

No `get_app_state`, `list_apps`, click, keyboard, pointer, browser, or Chrome action was issued after this capability check. In particular, this assessment did not pass `com.google.Chrome`, a Chrome bundle path, window title, or any other selector to Computer Use.

## Conflict and fail-closed result

Giving Computer Use `com.google.Chrome` would use the explicitly prohibited app-selector route. It cannot establish that its action surface is the native-PID-filtered window attested by the helper. Continuing through that route would violate the frozen I03/I04 binding requirement and repeat the ambiguity that P3-117 was created to eliminate.

Therefore the runner was not allowed to launch the direct Chrome executable, create the temporary profile/candidate copy, take a PID-filtered capture, or execute any of the 46 GUI actions. This is a capability-boundary blocker, not a candidate failure and not a Pass. The structured counterpart is `computer_use_pid_binding_assessment.json`; the 46 required closure rows are all `NOT_IMPLEMENTED` in `dynamic_closure.json`.

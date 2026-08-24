# IPC-02 actual denial evidence

- Invoked the unregistered `unknown_p3_104_command`; the actual Tauri invoke handler denied it with no side effect. Screenshot: `screenshots/IPC-02-unknown-denied.jpeg` (`bf65e3df2452cff23722fca2474cab8f8c04e9d132a4b67ce0463175d44852e7`).
- Invoked the three registered commands with extra `path`, `sql`, and `shell` request fields. Strict deserialization rejected all three and the backend remained at one record/two audit events. Screenshot: `screenshots/IPC-02-extra-args-denied.jpeg` (`893b7975b83211aa58760cd2d67e7734909f8ea886d758df90115e3e71cb5bce`).

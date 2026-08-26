# LIFEOS-P3-122 P3-116 Actual Visual Source Positive Allowlist

- Source root: `lifeos/prototypes/LIFEOS-P3-116/`
- Purpose: the only positive visual implementation source for P3-122.
- Record count: 8
- Rule: copy these files into the new candidate as the visual source layer. P3-116 historical screenshots, AX, Evidence and any P3-121 `ui/` file are not positive visual inputs.
- Direct-inheritance rule: `index.html`、`styles.css`、`app.js`、DOM/class、visual Token and page-specific components must remain source-traceable; Runtime integration may use a separate minimal adapter but may not conceptually rewrite the visual layer.

| Relative path | Bytes | SHA-256 |
|---|---:|---|
| `index.html` | 527 | `d9283e3f0a0366ef350d8b11fe094a4f3fbebabef30511353b0b007b5de0b28b` |
| `styles.css` | 40190 | `cf9f800c8c30f75e05e0b58345807128b8a11d0c31ea11f076e8ff7a5a02d8d3` |
| `app.js` | 42702 | `c1db2926e04f83e26d787f75f922fa562070db560bc8fbac661f82492b9a451f` |
| `fixtures.js` | 2994 | `a7b01ba8e176d80ae172ddd8acd2ed3a8c9b755b046159b190a2272195af3d93` |
| `visual_contract.json` | 1825 | `c77435e281cbd9bbb447d7b081e055216afc18ff67f82b703cf9cb9acab8da49` |
| `interaction_contract.md` | 3728 | `584189e7fee5a3e3d712ae4e1e7bf2e90e90a80e17c9f3eef1a61fdc88bf6393` |
| `ia_reconciliation.md` | 3432 | `bcedecafe5b068d05e5391c7de69aff2daa11aa6716851f5d2af1277f522b467` |
| `state_machine.json` | 2660 | `2bd66cf76dff4a0289e7c5b0b6a40ced22a0a765753a79c2c98075e8aa866cdc` |

## Exclusions

- `lifeos/prototypes/LIFEOS-P3-116/evidence/` and all historical dynamic screenshot/AX assets.
- Any deleted or previously polluted P3-116 file.
- `lifeos/engineering/LIFEOS-P3-121/candidate/ui/` and all P3-121 screenshots as visual source.
- Browser chrome, current desktop state, system settings and external assets.

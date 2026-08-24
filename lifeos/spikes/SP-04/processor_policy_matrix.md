# Processor policy matrix

| Processor | Location | Policy known | Subprocessors/region | Training/eval default | Retention | Deletion | Spike eligibility |
|---|---|---|---|---|---:|---|---|
| local-runtime | local | yes | known/synthetic local | off/off | 0 days | supported | eligible within matching grant |
| lifeos-cloud-mock | LifeOS cloud mock | yes | known/CN-synthetic | off/off | 7 days | supported | eligible within matching grant |
| third-party-a-mock | named third party mock | yes | known/CN-synthetic | off/off | 7 days | supported | eligible within matching grant |
| third-party-b-mock | different named third party | yes | known/CN-synthetic | off/off | 7 days | supported | no grant in fixture; denied |

Mutation cases prove that unknown policy/subprocessors/region, policy-version change, default training/evaluation, excessive retention, insufficient deletion, and failed qualification all deny. No row is a real vendor assessment or selection.

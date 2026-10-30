# Offline review of the fixed incident evidence capture

**53 saved cases rechecked; 53 scenario expectations matched. These are not 53 security successes.**

This document presents saved synthetic observations. Evidence checks were rerun; the original upload, publication and erasure actions were not repeated. Human review was not performed. The truth of the observations and independent reproduction are not established. Conformance and legal compliance are not assessed.

## Scope and limits

| Field | Recorded value |
| --- | --- |
| actions&#95;reexecuted | false |
| conformance | &#34;NOT&#95;ASSESSED&#34; |
| dependency&#95;scope | &#34;PINNED&#95;VERSIONS&#95;NOT&#95;HERMETIC&#34; |
| human&#95;review | &#34;NOT&#95;PERFORMED&#34; |
| independent&#95;reproduction | &#34;NOT&#95;ESTABLISHED&#34; |
| legal&#95;compliance | &#34;NOT&#95;ASSESSED&#34; |
| observation&#95;truth | &#34;NOT&#95;ESTABLISHED&#34; |

## Rechecked inventory

| Pilot | Saved cases |
| --- | --- |
| upload | 17 |
| publication | 18 |
| erasure | 18 |

## Report and input bindings

| Field | Recorded value |
| --- | --- |
| Authoritative review&#46;json SHA&#45;256 | 0de419ece3f344b763122d0dfc69ec4649cf0867c3438e829f2e90031401a316 |
| Reporter version | 0&#46;1&#46;0 |
| Reporter source SHA&#45;256 | 1b6187b8d732e299de389e957601b96ad971f908f1b96cc6da11d2662e2efb3b |
| archive&#95;sha256 | 06bdb46eade7ef5c2f041797007d1f7ef3aaa55ad17d88a90b28276be17d865f |
| manifest&#95;sha256 | 808cac08a06e2f543683e4499645d1eda3860a400406efe1cbd206614490a76d |
| provenance&#95;sha256 | 986096ffcd48efeeb248dde4719c08b15eac0c80c1dd60573ce954e5ed144387 |

## Case index

These state lists are recorded case-level aggregates. Their positions do not pair operations with core assessments. The interpretation codes are explained in the full case entries; they are not grades.

| Case | Captured title | Recorded state list | Interpretation codes |
| --- | --- | --- | --- |
| UL&#45;01 (S0005) | Allowed immutable raw bytes reach the receiver (S0006) | &#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#93; (S0007) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0001, S0002); UPLOAD&#95;RECEIPT&#95;NOT&#95;PROCESSING (S0003, S0004) |
| UL&#45;02 (S0010) | Unapproved destination grant blocks before transport (S0011) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; (S0012) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0008, S0009) |
| UL&#45;03 (S0015) | Wrong tenant grant blocks before transport (S0016) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; (S0017) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0013, S0014) |
| UL&#45;04 (S0020) | Previously permitted digest cannot authorize changed bytes (S0021) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; (S0022) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0018, S0019) |
| UL&#45;05 (S0025) | Expired signed permission cannot authorize current execution (S0026) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; (S0027) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0023, S0024) |
| UL&#45;06 (S0030) | Injected journal claim failure blocks transport (S0031) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; (S0032) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0028, S0029) |
| UL&#45;07 (S0039) | Receiver commits and drops response&#59; repeat never resends (S0040) | &#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#44;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93; (S0041) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0033, S0034); UPLOAD&#95;UNKNOWN&#95;WITH&#95;RECEIVER&#95;OBSERVATION (S0035, S0036, S0037, S0038) |
| UL&#45;08 (S0048) | Authentic response for wrong payload cannot confirm receipt (S0049) | &#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#93; (S0050) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0042, S0043); UPLOAD&#95;UNKNOWN&#95;WITH&#95;RECEIVER&#95;OBSERVATION (S0044, S0045, S0046, S0047) |
| UL&#45;09 (S0055) | Caller mutation after capture cannot replace outgoing bytes (S0056) | &#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#93; (S0057) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0051, S0052); UPLOAD&#95;RECEIPT&#95;NOT&#95;PROCESSING (S0053, S0054) |
| UL&#45;10 (S0064) | Permission expires during pre&#45;send pause (S0065) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; (S0066) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0058, S0059); UPLOAD&#95;FINAL&#95;GATE&#95;DIFFERS (S0060, S0061, S0062, S0063) |
| UL&#45;11 (S0071) | Repeated confirmed request does not send twice (S0072) | &#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93; (S0073) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0067, S0068); UPLOAD&#95;RECEIPT&#95;NOT&#95;PROCESSING (S0069, S0070) |
| UL&#45;12 (S0078) | Same request identifier with newly approved other bytes is rejected (S0079) | &#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#44;&#34;REQUEST&#95;ID&#95;CONFLICT&#34;&#93; (S0080) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0074, S0075); UPLOAD&#95;RECEIPT&#95;NOT&#95;PROCESSING (S0076, S0077) |
| UL&#45;13 (S0083) | HTTP redirect is never followed (S0084) | &#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#93; (S0085) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0081, S0082) |
| UL&#45;14 (S0094) | Unauthenticated endpoint exposes the outside&#45;route bypass (S0095) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; (S0096) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0086, S0087); UPLOAD&#95;OUTSIDE&#95;ROUTE&#95;BYPASS (S0088, S0089, S0090, S0091, S0092, S0093) |
| UL&#45;15 (S0101) | Concurrent identical calls consume only one dispatch claim (S0102) | &#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93; (S0103) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0097, S0098); UPLOAD&#95;RECEIPT&#95;NOT&#95;PROCESSING (S0099, S0100) |
| UL&#45;16 (S0110) | Injected result persistence failure leaves outcome unresolved (S0111) | &#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#93; (S0112) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0104, S0105); UPLOAD&#95;UNKNOWN&#95;WITH&#95;RECEIVER&#95;OBSERVATION (S0106, S0107, S0108, S0109) |
| UL&#45;17 (S0119) | Worker killed after committed intent is not automatically resent (S0120) | &#91;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93; (S0121) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0113, S0114); UPLOAD&#95;INTENT&#95;NOT&#95;DISPATCH (S0115, S0116, S0117, S0118) |
| LP&#45;01 (S0126) | Exact approved final HTML is materialized and measured (S0127) | &#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#93; (S0128) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0122, S0123); PUBLICATION&#95;CORE&#95;REMAINS&#95;REVIEW (S0124, S0125) |
| LP&#45;02 (S0131) | Changed article cannot reuse the earlier approval (S0132) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; (S0133) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0129, S0130) |
| LP&#45;03 (S0136) | Removed disclosure cannot reuse signed preparation evidence (S0137) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; (S0138) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0134, S0135) |
| LP&#45;04 (S0141) | A valid policy package for another venue is rejected (S0142) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; (S0143) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0139, S0140) |
| LP&#45;05 (S0148) | Disclosure and reviewer approval do not override prohibited use (S0149) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; (S0150) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0144, S0145); PUBLICATION&#95;DISCLOSURE&#95;NOT&#95;OVERRIDE (S0146, S0147) |
| LP&#45;06 (S0153) | Missing explicit reviewer authorization prevents output (S0154) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; (S0155) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0151, S0152) |
| LP&#45;07 (S0158) | Untrusted reviewer signature prevents output (S0159) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; (S0160) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0156, S0157) |
| LP&#45;08 (S0166) | Approval expires during an actual pre&#45;link pause (S0167) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; (S0168) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0161, S0162); PUBLICATION&#95;FINAL&#95;AUTHORIZATION&#95;CHANGED (S0163, S0164, S0165) |
| LP&#45;09 (S0176) | Unknown imported origin remains unknown after approved local export (S0177) | &#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#93; (S0178) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0169, S0170); PUBLICATION&#95;UNKNOWN&#95;ORIGIN (S0171, S0172, S0173); PUBLICATION&#95;CORE&#95;REMAINS&#95;REVIEW (S0174, S0175) |
| LP&#45;10 (S0186) | Replaced synthetic AI operation remains history without exact final adoption (S0187) | &#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#93; (S0188) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0179, S0180); PUBLICATION&#95;UNKNOWN&#95;ORIGIN (S0181, S0182, S0183); PUBLICATION&#95;CORE&#95;REMAINS&#95;REVIEW (S0184, S0185) |
| LP&#45;11 (S0191) | Truncated signed edit history cannot become a valid candidate (S0192) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; (S0193) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0189, S0190) |
| LP&#45;12 (S0196) | Unresolved policy interpretation prevents output (S0197) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; (S0198) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0194, S0195) |
| LP&#45;13 (S0203) | Repeated identical request does not publish again (S0204) | &#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;PUBLICATION&#34;&#93; (S0205) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0199, S0200); PUBLICATION&#95;CORE&#95;REMAINS&#95;REVIEW (S0201, S0202) |
| LP&#45;14 (S0211) | Result persistence failure leaves visible output unresolved and never retries (S0212) | &#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#44;&#34;REPLAY&#95;NO&#95;PUBLICATION&#34;&#93; (S0213) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0206, S0207); PUBLICATION&#95;UNKNOWN&#95;WITH&#95;VISIBLE&#95;FILE (S0208, S0209, S0210) |
| LP&#45;15 (S0221) | Concurrent identical requests consume one publication claim (S0222) | &#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;PUBLICATION&#34;&#93; (S0223) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0214, S0215); PUBLICATION&#95;CORE&#95;REMAINS&#95;REVIEW (S0216, S0217); SORTED&#95;SUMMARY&#95;NOT&#95;RECORD&#95;ASSOCIATION (S0218, S0219, S0220) |
| LP&#45;16 (S0232) | Outside&#45;gate direct write demonstrates incomplete route control (S0233) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; (S0234) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0224, S0225); PUBLICATION&#95;OUTSIDE&#95;GATE&#95;WRITE (S0226, S0227, S0228, S0229, S0230, S0231) |
| LP&#45;17 (S0237) | Structured disclosure omitting recorded assistance prevents output (S0238) | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; (S0239) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0235, S0236) |
| LP&#45;18 (S0244) | Reusing a request ID for a newly approved different artifact conflicts (S0245) | &#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#44;&#34;REQUEST&#95;ID&#95;CONFLICT&#34;&#93; (S0246) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0240, S0241); PUBLICATION&#95;CORE&#95;REMAINS&#95;REVIEW (S0242, S0243) |
| LE&#45;01 (S0249) | Exact authorized local namespace removal (S0250) | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; (S0251) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0247, S0248) |
| LE&#45;02 (S0254) | Acknowledgement without removal leaves the object present (S0255) | &#91;&#34;ACKNOWLEDGED&#95;ONLY&#34;&#93; (S0256) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0252, S0253) |
| LE&#45;03 (S0259) | Request alone establishes no provider completion (S0260) | &#91;&#34;NO&#95;PROVIDER&#95;CALL&#34;&#93; (S0261) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0257, S0258) |
| LE&#45;04 (S0266) | Tampered receipt signature is rejected after a measured operation (S0267) | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; (S0268) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0262, S0263); ERASURE&#95;PROBE&#95;REJECTED&#95;AFTER&#95;OPERATION (S0264, S0265) |
| LE&#45;05 (S0273) | Validly signed completion for another tenant is rejected (S0274) | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; (S0275) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0269, S0270); ERASURE&#95;PROBE&#95;REJECTED&#95;AFTER&#95;OPERATION (S0271, S0272) |
| LE&#45;06 (S0278) | Authorization expires after claim and before unlink (S0279) | &#91;&#34;BLOCKED&#34;&#93; (S0280) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0276, S0277) |
| LE&#45;07 (S0283) | Changed current content is not deleted (S0284) | &#91;&#34;BLOCKED&#34;&#93; (S0285) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0281, S0282) |
| LE&#45;08 (S0290) | Pre&#45;existing absence is not attributed to this deletion request (S0291) | &#91;&#34;BLOCKED&#34;&#93; (S0292) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0286, S0287); ERASURE&#95;PREEXISTING&#95;ABSENCE (S0288, S0289) |
| LE&#45;09 (S0295) | Repeated request performs no second unlink (S0296) | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;ACTION&#34;&#93; (S0297) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0293, S0294) |
| LE&#45;10 (S0304) | Lost terminal persistence acknowledgement remains unknown and cannot retry (S0305) | &#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#44;&#34;REPLAY&#95;NO&#95;ACTION&#34;&#93; (S0306) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0298, S0299); ERASURE&#95;UNKNOWN&#95;WITH&#95;ABSENCE (S0300, S0301, S0302, S0303) |
| LE&#45;11 (S0312) | Concurrent identical requests enter at most one unlink (S0313) | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;ACTION&#34;&#93; (S0314) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0307, S0308); SORTED&#95;SUMMARY&#95;NOT&#95;RECORD&#95;ASSOCIATION (S0309, S0310, S0311) |
| LE&#45;12 (S0323) | Explicitly excluded copy stays readable after scoped removal (S0324) | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; (S0325) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0315, S0316); ERASURE&#95;READABLE&#95;RETAINED&#95;DATA (S0317, S0318, S0319, S0320, S0321, S0322) |
| LE&#45;13 (S0334) | Previously opened file stays readable after namespace removal (S0335) | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; (S0336) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0326, S0327); ERASURE&#95;READABLE&#95;RETAINED&#95;DATA (S0328, S0329, S0330, S0331, S0332, S0333) |
| LE&#45;14 (S0343) | After&#45;only absence does not prove an observed transition (S0344) | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; (S0345) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0337, S0338); ERASURE&#95;AFTER&#95;ONLY&#95;ABSENCE (S0339, S0340, S0341, S0342) |
| LE&#45;15 (S0352) | Recreated entry is observed present despite an earlier scoped receipt (S0353) | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; (S0354) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0346, S0347); ERASURE&#95;LATER&#95;PRESENCE (S0348, S0349, S0350, S0351) |
| LE&#45;16 (S0357) | Failed durable intent prevents unlink (S0358) | &#91;&#34;BLOCKED&#34;&#93; (S0359) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0355, S0356) |
| LE&#45;17 (S0362) | Same request ID with another object version conflicts (S0363) | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#44;&#34;REQUEST&#95;ID&#95;CONFLICT&#34;&#93; (S0364) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0360, S0361) |
| LE&#45;18 (S0371) | Provider attestation without observer remains a scoped provider claim (S0372) | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; (S0373) | EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS (S0365, S0366); ERASURE&#95;NO&#95;OBSERVER (S0367, S0368, S0369, S0370) |

## Original capture metadata

### upload

Original pilot source SHA-256: 0f7e7f04c45baca8bc62ea0f8778c79ef5bba22e27faf49fbad92001c617df49

Whole original summary: S0374

Original capture provenance: S0375

| Field | Recorded value | Source |
| --- | --- | --- |
| recorded&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;12&#46;019527Z&#34; | S0376 |
| network&#95;execution | &#34;ACTUAL&#95;LITERAL&#95;LOOPBACK&#95;HTTP&#34; | S0377 |
| synthetic | true | S0378 |
| independent&#95;reproduction | &#34;NOT&#95;ESTABLISHED&#34; | S0379 |
| all&#95;route&#95;prevention&#95;established | false | S0380 |

### publication

Original pilot source SHA-256: 78386924abf2ac6819f653d7c282972b86e58ac1379751c213bca1e5334c639c

Whole original summary: S0381

Original capture provenance: S0382

| Field | Recorded value | Source |
| --- | --- | --- |
| recorded&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;270998Z&#34; | S0383 |
| execution | &#34;ACTUAL&#95;LOCAL&#95;FILESYSTEM&#34; | S0384 |
| synthetic | true | S0385 |
| independent&#95;reproduction | &#34;NOT&#95;ESTABLISHED&#34; | S0386 |
| external&#95;publication | &#34;NOT&#95;PERFORMED&#34; | S0387 |
| real&#95;ai&#95;service&#95;called | false | S0388 |
| all&#95;route&#95;prevention&#95;established | false | S0389 |

### erasure

Original pilot source SHA-256: fb0dc41bde92840e06f11c9077c41743dc8c1255b4404aaa464b7455fa829191

Whole original summary: S0390

Original capture provenance: S0391

| Field | Recorded value | Source |
| --- | --- | --- |
| recorded&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;395585Z&#34; | S0392 |
| execution | &#34;ACTUAL&#95;LOCAL&#95;FILESYSTEM&#34; | S0393 |
| synthetic | true | S0394 |
| independent&#95;reproduction | &#34;NOT&#95;ESTABLISHED&#34; | S0395 |
| remote&#95;provider&#95;used | false | S0396 |
| universal&#95;erasure | &#34;NOT&#95;ESTABLISHED&#34; | S0397 |
| raw&#95;object&#95;content&#95;exported | false | S0398 |

## Case observations

### UL&#45;01 — Allowed immutable raw bytes reach the receiver

Whole-case capture: S0005

Title source: S0006

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0001 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;true&#44;&#34;states&#34;&#58;&#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#93;&#125; | S0002 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;true&#44;&#34;states&#34;&#58;&#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#93;&#125; | S0399 |
| differences | &#123;&#125; | S0400 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 1 | S0401 |
| gateway&#95;attempts | 1 | S0402 |
| handler&#95;calls | 1 | S0403 |
| received&#95;bytes&#95;match | true | S0404 |
| states | &#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#93; | S0405 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 1 | S0406 |
| accepted&#95;count | 1 | S0407 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;RECEIPT&#95;CONFIRMED&#34; | S0003 |
| attempted | true | S0408 |
| reason | &#34;PINNED&#95;RECEIVER&#95;ATTESTED&#95;MATCHING&#95;BYTES&#34; | S0409 |
| journal&#95;state | &#34;receipt&#95;confirmed&#34; | S0410 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0411 |
| byte&#95;length | 62 | S0412 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attempted | true | S0413 |
| body&#95;send&#95;completed | true | S0414 |
| attempted&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;06&#46;089313Z&#34; | S0415 |
| dispatched&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;06&#46;089561Z&#34; | S0416 |
| status | 200 | S0417 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;upload&#95;receipt&#34; | S0418 |
| request&#95;id | &#34;upload&#45;9e4227a6df0c4d6a950fe3f777e51798&#34; | S0419 |
| subject&#95;sha256 | &#34;981340e5f6352339ceb724de1bf0594a66b358358d102672d69fed3e543cde12&#34; | S0420 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0421 |
| byte&#95;length | 62 | S0422 |
| received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;06&#46;091740Z&#34; | S0423 |
| receipt&#95;id | &#34;receipt&#45;e09cc52c6c984b6ea9691b38174aad8b&#34; | S0424 |

##### receiver&#95;receipt — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| receiver&#95;rows&#91;0&#93;&#46;kind | &#34;upload&#95;receipt&#34; | S0425 |
| receiver&#95;rows&#91;0&#93;&#46;request&#95;id | &#34;upload&#45;9e4227a6df0c4d6a950fe3f777e51798&#34; | S0426 |
| receiver&#95;rows&#91;0&#93;&#46;subject&#95;sha256 | &#34;981340e5f6352339ceb724de1bf0594a66b358358d102672d69fed3e543cde12&#34; | S0427 |
| receiver&#95;rows&#91;0&#93;&#46;payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0428 |
| receiver&#95;rows&#91;0&#93;&#46;byte&#95;length | 62 | S0429 |
| receiver&#95;rows&#91;0&#93;&#46;received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;06&#46;091740Z&#34; | S0430 |
| receiver&#95;rows&#91;0&#93;&#46;receipt&#95;id | &#34;receipt&#45;e09cc52c6c984b6ea9691b38174aad8b&#34; | S0431 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0432

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0433 |

###### Recorded core dimensions

All values in the following table come from S0434

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0435

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0436

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0437 |

###### Recorded core dimensions

All values in the following table come from S0438

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0439

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase postflight

Frame or nearest existing container: S0440

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0441 |

###### Recorded core dimensions

All values in the following table come from S0442

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;ALLOW&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;DISPATCH&#95;OBSERVED&#34; |

###### Recorded core findings

All values in the following table come from S0443

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;BOUND&#95;DISPATCH&#95;OBSERVED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;de92f2f19bb84970885b2afb39415d1b&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;OBSERVED&#95;ACTION&#95;HAS&#95;APPLICABLE&#95;AUTHORIZATION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;de92f2f19bb84970885b2afb39415d1b&#34;&#44;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0001, S0002

**UPLOAD&#95;RECEIPT&#95;NOT&#95;PROCESSING** — The scoped local receiver receipt concerns matching bytes&#46; The core remote outcome remains UNKNOWN&#59; downstream processing or retention is not established&#46;

Source: S0003, S0004

### UL&#45;02 — Unapproved destination grant blocks before transport

Whole-case capture: S0010

Title source: S0011

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0008 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0009 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;received&#95;bytes&#95;match&#34;&#58;false&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0444 |
| differences | &#123;&#125; | S0445 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 0 | S0446 |
| gateway&#95;attempts | 0 | S0447 |
| handler&#95;calls | 0 | S0448 |
| received&#95;bytes&#95;match | false | S0449 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; | S0450 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 0 | S0451 |
| accepted&#95;count | 0 | S0452 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34; | S0453 |
| attempted | false | S0454 |
| reason | &#34;ASSESSOR&#95;DID&#95;NOT&#95;ALLOW&#95;MEASURED&#95;TARGET&#34; | S0455 |
| journal&#95;state | &#34;NOT&#95;CLAIMED&#34; | S0456 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0457 |
| byte&#95;length | 62 | S0458 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| transport&#95;observation | null | S0459 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0460 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0461

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0462 |

###### Recorded core dimensions

All values in the following table come from S0463

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;BLOCK&#34; |
| binding&#95;assessment | &#34;ENDPOINT&#95;NOT&#95;APPROVED&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;BLOCK&#95;CONTROLLED&#95;ROUTE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;DENY&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;DENY&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0464

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;APPROVAL&#95;REGISTRY&#95;DOES&#95;NOT&#95;AUTHORIZE&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0465

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 0 — phase postflight

Frame or nearest existing container: S0466

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0467 |

###### Recorded core dimensions

All values in the following table come from S0468

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;BLOCK&#34; |
| binding&#95;assessment | &#34;ENDPOINT&#95;NOT&#95;APPROVED&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;BLOCK&#95;CONTROLLED&#95;ROUTE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;DENY&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;DENY&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0469

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;APPROVAL&#95;REGISTRY&#95;DOES&#95;NOT&#95;AUTHORIZE&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0008, S0009

### UL&#45;03 — Wrong tenant grant blocks before transport

Whole-case capture: S0015

Title source: S0016

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0013 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0014 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;received&#95;bytes&#95;match&#34;&#58;false&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0470 |
| differences | &#123;&#125; | S0471 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 0 | S0472 |
| gateway&#95;attempts | 0 | S0473 |
| handler&#95;calls | 0 | S0474 |
| received&#95;bytes&#95;match | false | S0475 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; | S0476 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 0 | S0477 |
| accepted&#95;count | 0 | S0478 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34; | S0479 |
| attempted | false | S0480 |
| reason | &#34;ASSESSOR&#95;DID&#95;NOT&#95;ALLOW&#95;MEASURED&#95;TARGET&#34; | S0481 |
| journal&#95;state | &#34;NOT&#95;CLAIMED&#34; | S0482 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0483 |
| byte&#95;length | 62 | S0484 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| transport&#95;observation | null | S0485 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0486 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0487

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0488 |

###### Recorded core dimensions

All values in the following table come from S0489

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;BLOCK&#34; |
| binding&#95;assessment | &#34;TENANT&#95;MISMATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;BLOCK&#95;CONTROLLED&#95;ROUTE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;DENY&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;DENY&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0490

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;APPROVAL&#95;REGISTRY&#95;DOES&#95;NOT&#95;AUTHORIZE&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0491

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 0 — phase postflight

Frame or nearest existing container: S0492

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0493 |

###### Recorded core dimensions

All values in the following table come from S0494

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;BLOCK&#34; |
| binding&#95;assessment | &#34;TENANT&#95;MISMATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;BLOCK&#95;CONTROLLED&#95;ROUTE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;DENY&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;DENY&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0495

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;APPROVAL&#95;REGISTRY&#95;DOES&#95;NOT&#95;AUTHORIZE&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0013, S0014

### UL&#45;04 — Previously permitted digest cannot authorize changed bytes

Whole-case capture: S0020

Title source: S0021

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0018 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0019 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;received&#95;bytes&#95;match&#34;&#58;false&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0496 |
| differences | &#123;&#125; | S0497 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 0 | S0498 |
| gateway&#95;attempts | 0 | S0499 |
| handler&#95;calls | 0 | S0500 |
| received&#95;bytes&#95;match | false | S0501 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; | S0502 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 0 | S0503 |
| accepted&#95;count | 0 | S0504 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34; | S0505 |
| attempted | false | S0506 |
| reason | &#34;ASSESSOR&#95;DID&#95;NOT&#95;ALLOW&#95;MEASURED&#95;TARGET&#34; | S0507 |
| journal&#95;state | &#34;NOT&#95;CLAIMED&#34; | S0508 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0509 |
| byte&#95;length | 62 | S0510 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| transport&#95;observation | null | S0511 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0512 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0513

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0514 |

###### Recorded core dimensions

All values in the following table come from S0515

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;BLOCK&#34; |
| binding&#95;assessment | &#34;PAYLOAD&#95;MISMATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;BLOCK&#95;CONTROLLED&#95;ROUTE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;DENY&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;DENY&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0516

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;AUTHORIZATION&#95;NOT&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;PERMIT&#95;BINDS&#95;DIFFERENT&#95;PAYLOAD&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0517

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 0 — phase postflight

Frame or nearest existing container: S0518

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0519 |

###### Recorded core dimensions

All values in the following table come from S0520

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;BLOCK&#34; |
| binding&#95;assessment | &#34;PAYLOAD&#95;MISMATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;BLOCK&#95;CONTROLLED&#95;ROUTE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;DENY&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;DENY&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0521

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;AUTHORIZATION&#95;NOT&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;PERMIT&#95;BINDS&#95;DIFFERENT&#95;PAYLOAD&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0018, S0019

### UL&#45;05 — Expired signed permission cannot authorize current execution

Whole-case capture: S0025

Title source: S0026

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0023 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0024 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;received&#95;bytes&#95;match&#34;&#58;false&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0522 |
| differences | &#123;&#125; | S0523 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 0 | S0524 |
| gateway&#95;attempts | 0 | S0525 |
| handler&#95;calls | 0 | S0526 |
| received&#95;bytes&#95;match | false | S0527 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; | S0528 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 0 | S0529 |
| accepted&#95;count | 0 | S0530 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34; | S0531 |
| attempted | false | S0532 |
| reason | &#34;ASSESSOR&#95;DID&#95;NOT&#95;ALLOW&#95;MEASURED&#95;TARGET&#34; | S0533 |
| journal&#95;state | &#34;NOT&#95;CLAIMED&#34; | S0534 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0535 |
| byte&#95;length | 62 | S0536 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| transport&#95;observation | null | S0537 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0538 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0539

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0540 |

###### Recorded core dimensions

All values in the following table come from S0541

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;REVIEW&#34; |
| binding&#95;assessment | &#34;UNRESOLVED&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;HOLD&#95;PENDING&#95;CURRENT&#95;AUTHORIZATION&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;EXPIRED&#95;OR&#95;UNRESOLVED&#34; |
| proposed&#95;transfer&#95;authorization | &#34;REVIEW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;REVIEW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0542

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;POLICY&#95;NOT&#95;EFFECTIVE&#95;AT&#95;OPERATION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;policy&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;AUTHORIZATION&#95;NOT&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0543

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 0 — phase postflight

Frame or nearest existing container: S0544

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0545 |

###### Recorded core dimensions

All values in the following table come from S0546

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;REVIEW&#34; |
| binding&#95;assessment | &#34;UNRESOLVED&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;HOLD&#95;PENDING&#95;CURRENT&#95;AUTHORIZATION&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;EXPIRED&#95;OR&#95;UNRESOLVED&#34; |
| proposed&#95;transfer&#95;authorization | &#34;REVIEW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;REVIEW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0547

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;POLICY&#95;NOT&#95;EFFECTIVE&#95;AT&#95;OPERATION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;policy&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;AUTHORIZATION&#95;NOT&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0023, S0024

### UL&#45;06 — Injected journal claim failure blocks transport

Whole-case capture: S0030

Title source: S0031

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0028 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0029 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;received&#95;bytes&#95;match&#34;&#58;false&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0548 |
| differences | &#123;&#125; | S0549 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 0 | S0550 |
| gateway&#95;attempts | 0 | S0551 |
| handler&#95;calls | 0 | S0552 |
| received&#95;bytes&#95;match | false | S0553 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; | S0554 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 0 | S0555 |
| accepted&#95;count | 0 | S0556 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34; | S0557 |
| attempted | false | S0558 |
| reason | &#34;JOURNAL&#95;INTENT&#95;COMMIT&#95;NOT&#95;ESTABLISHED&#34; | S0559 |
| journal&#95;state | &#34;NOT&#95;CLAIMED&#34; | S0560 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0561 |
| byte&#95;length | 62 | S0562 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| transport&#95;observation | null | S0563 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0564 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0565

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0566 |

###### Recorded core dimensions

All values in the following table come from S0567

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0568

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0569

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 0 — phase postflight

Frame or nearest existing container: S0570

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0571 |

###### Recorded core dimensions

All values in the following table come from S0572

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0573

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0028, S0029

### UL&#45;07 — Receiver commits and drops response&#59; repeat never resends

Whole-case capture: S0039

Title source: S0040

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0033 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;true&#44;&#34;states&#34;&#58;&#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#44;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93;&#125; | S0034 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;true&#44;&#34;states&#34;&#58;&#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#44;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93;&#125; | S0574 |
| differences | &#123;&#125; | S0575 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 1 | S0576 |
| gateway&#95;attempts | 1 | S0577 |
| handler&#95;calls | 1 | S0578 |
| received&#95;bytes&#95;match | true | S0579 |
| states | &#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#44;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93; | S0580 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 1 | S0581 |
| accepted&#95;count | 1 | S0037 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;OUTCOME&#95;UNKNOWN&#34; | S0035 |
| attempted | true | S0582 |
| reason | &#34;RECEIVER&#95;RECEIPT&#95;NOT&#95;CONFIRMED&#34; | S0583 |
| journal&#95;state | &#34;outcome&#95;unknown&#34; | S0584 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0585 |
| byte&#95;length | 62 | S0586 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attempted | true | S0587 |
| body&#95;send&#95;completed | true | S0588 |
| attempted&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;07&#46;393766Z&#34; | S0589 |
| dispatched&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;07&#46;394015Z&#34; | S0590 |
| status | null | S0591 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0036 |

##### operation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;REPLAY&#95;NO&#95;SEND&#34; | S0592 |
| attempted | false | S0593 |
| reason | &#34;REQUEST&#95;ALREADY&#95;CLAIMED&#95;RECEIPT&#95;NOT&#95;REASSERTED&#34; | S0594 |
| journal&#95;state | &#34;outcome&#95;unknown&#34; | S0595 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0596 |
| byte&#95;length | 62 | S0597 |

##### transport — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| transport&#95;observation | null | S0598 |

##### receipt — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0599 |

##### receiver&#95;receipt — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| receiver&#95;rows&#91;0&#93;&#46;kind | &#34;upload&#95;receipt&#34; | S0600 |
| receiver&#95;rows&#91;0&#93;&#46;request&#95;id | &#34;upload&#45;a8568a2e61dd478a84faae1db770111b&#34; | S0601 |
| receiver&#95;rows&#91;0&#93;&#46;subject&#95;sha256 | &#34;3872c5aaa6036e29a0a009dc3bdbaf595e94405ce968066371b6b39bd92a84ab&#34; | S0602 |
| receiver&#95;rows&#91;0&#93;&#46;payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0603 |
| receiver&#95;rows&#91;0&#93;&#46;byte&#95;length | 62 | S0604 |
| receiver&#95;rows&#91;0&#93;&#46;received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;07&#46;396032Z&#34; | S0605 |
| receiver&#95;rows&#91;0&#93;&#46;receipt&#95;id | &#34;receipt&#45;9851763067104c30992661adadf006f0&#34; | S0606 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0607

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0608 |

###### Recorded core dimensions

All values in the following table come from S0609

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0610

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0611

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0612 |

###### Recorded core dimensions

All values in the following table come from S0613

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0614

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase postflight

Frame or nearest existing container: S0615

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0616 |

###### Recorded core dimensions

All values in the following table come from S0617

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;ALLOW&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;DISPATCH&#95;OBSERVED&#34; |

###### Recorded core findings

All values in the following table come from S0618

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;BOUND&#95;DISPATCH&#95;OBSERVED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;6672209877af4e12a0e0b326cc1399e8&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;OBSERVED&#95;ACTION&#95;HAS&#95;APPLICABLE&#95;AUTHORIZATION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;6672209877af4e12a0e0b326cc1399e8&#34;&#44;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 1 — phase preflight

Frame or nearest existing container: S0619

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0620 |

###### Recorded core dimensions

All values in the following table come from S0621

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0622

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 1 — phase final&#95;gate

Frame or nearest existing container: S0623

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 1 — phase postflight

Frame or nearest existing container: S0624

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0625 |

###### Recorded core dimensions

All values in the following table come from S0626

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0627

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0033, S0034

**UPLOAD&#95;UNKNOWN&#95;WITH&#95;RECEIVER&#95;OBSERVATION** — The gateway outcome remains unknown while the receiver has an accepted&#45;request observation&#46; The receiver observation does not retroactively confirm the gateway result&#46;

Source: S0035, S0036, S0037, S0038

### UL&#45;08 — Authentic response for wrong payload cannot confirm receipt

Whole-case capture: S0048

Title source: S0049

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0042 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;true&#44;&#34;states&#34;&#58;&#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#93;&#125; | S0043 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;true&#44;&#34;states&#34;&#58;&#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#93;&#125; | S0628 |
| differences | &#123;&#125; | S0629 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 1 | S0630 |
| gateway&#95;attempts | 1 | S0631 |
| handler&#95;calls | 1 | S0632 |
| received&#95;bytes&#95;match | true | S0633 |
| states | &#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#93; | S0634 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 1 | S0635 |
| accepted&#95;count | 1 | S0046 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;OUTCOME&#95;UNKNOWN&#34; | S0044 |
| attempted | true | S0636 |
| reason | &#34;RECEIVER&#95;RECEIPT&#95;NOT&#95;CONFIRMED&#34; | S0637 |
| journal&#95;state | &#34;outcome&#95;unknown&#34; | S0638 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0639 |
| byte&#95;length | 62 | S0640 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attempted | true | S0641 |
| body&#95;send&#95;completed | true | S0642 |
| attempted&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;07&#46;642294Z&#34; | S0643 |
| dispatched&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;07&#46;642518Z&#34; | S0644 |
| status | 200 | S0645 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0045 |

##### receiver&#95;receipt — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| receiver&#95;rows&#91;0&#93;&#46;kind | &#34;upload&#95;receipt&#34; | S0646 |
| receiver&#95;rows&#91;0&#93;&#46;request&#95;id | &#34;upload&#45;4f2e8b109dae49caadb16de42ad3f3f3&#34; | S0647 |
| receiver&#95;rows&#91;0&#93;&#46;subject&#95;sha256 | &#34;ecdcd35eaad281192428e11860acae201a4551ffbc3f61f19862a73d54ea300b&#34; | S0648 |
| receiver&#95;rows&#91;0&#93;&#46;payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0649 |
| receiver&#95;rows&#91;0&#93;&#46;byte&#95;length | 62 | S0650 |
| receiver&#95;rows&#91;0&#93;&#46;received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;07&#46;644663Z&#34; | S0651 |
| receiver&#95;rows&#91;0&#93;&#46;receipt&#95;id | &#34;receipt&#45;32ab57bd392846159c2075f13e9b8c19&#34; | S0652 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0653

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0654 |

###### Recorded core dimensions

All values in the following table come from S0655

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0656

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0657

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0658 |

###### Recorded core dimensions

All values in the following table come from S0659

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0660

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase postflight

Frame or nearest existing container: S0661

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0662 |

###### Recorded core dimensions

All values in the following table come from S0663

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;ALLOW&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;DISPATCH&#95;OBSERVED&#34; |

###### Recorded core findings

All values in the following table come from S0664

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;BOUND&#95;DISPATCH&#95;OBSERVED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;2215073add4541209cfab0dea87912a0&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;OBSERVED&#95;ACTION&#95;HAS&#95;APPLICABLE&#95;AUTHORIZATION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;2215073add4541209cfab0dea87912a0&#34;&#44;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0042, S0043

**UPLOAD&#95;UNKNOWN&#95;WITH&#95;RECEIVER&#95;OBSERVATION** — The gateway outcome remains unknown while the receiver has an accepted&#45;request observation&#46; The receiver observation does not retroactively confirm the gateway result&#46;

Source: S0044, S0045, S0046, S0047

### UL&#45;09 — Caller mutation after capture cannot replace outgoing bytes

Whole-case capture: S0055

Title source: S0056

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0051 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;true&#44;&#34;source&#95;mutated&#95;after&#95;capture&#34;&#58;true&#44;&#34;states&#34;&#58;&#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#93;&#125; | S0052 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;true&#44;&#34;source&#95;mutated&#95;after&#95;capture&#34;&#58;true&#44;&#34;states&#34;&#58;&#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#93;&#125; | S0665 |
| differences | &#123;&#125; | S0666 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 1 | S0667 |
| gateway&#95;attempts | 1 | S0668 |
| handler&#95;calls | 1 | S0669 |
| received&#95;bytes&#95;match | true | S0670 |
| source&#95;mutated&#95;after&#95;capture | true | S0671 |
| states | &#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#93; | S0672 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 1 | S0673 |
| accepted&#95;count | 1 | S0674 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;RECEIPT&#95;CONFIRMED&#34; | S0053 |
| attempted | true | S0675 |
| reason | &#34;PINNED&#95;RECEIVER&#95;ATTESTED&#95;MATCHING&#95;BYTES&#34; | S0676 |
| journal&#95;state | &#34;receipt&#95;confirmed&#34; | S0677 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0678 |
| byte&#95;length | 62 | S0679 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attempted | true | S0680 |
| body&#95;send&#95;completed | true | S0681 |
| attempted&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;07&#46;904948Z&#34; | S0682 |
| dispatched&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;07&#46;905207Z&#34; | S0683 |
| status | 200 | S0684 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;upload&#95;receipt&#34; | S0685 |
| request&#95;id | &#34;upload&#45;f93aeb3f75a64cd3b1afbb3ec4df764c&#34; | S0686 |
| subject&#95;sha256 | &#34;d2ce32319152c82269dc5a5947a88d929394673391e4ba07de66df9e796e0c29&#34; | S0687 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0688 |
| byte&#95;length | 62 | S0689 |
| received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;07&#46;909507Z&#34; | S0690 |
| receipt&#95;id | &#34;receipt&#45;ed70aee572304470ae2fd9f3ee4db911&#34; | S0691 |

##### receiver&#95;receipt — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| receiver&#95;rows&#91;0&#93;&#46;kind | &#34;upload&#95;receipt&#34; | S0692 |
| receiver&#95;rows&#91;0&#93;&#46;request&#95;id | &#34;upload&#45;f93aeb3f75a64cd3b1afbb3ec4df764c&#34; | S0693 |
| receiver&#95;rows&#91;0&#93;&#46;subject&#95;sha256 | &#34;d2ce32319152c82269dc5a5947a88d929394673391e4ba07de66df9e796e0c29&#34; | S0694 |
| receiver&#95;rows&#91;0&#93;&#46;payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0695 |
| receiver&#95;rows&#91;0&#93;&#46;byte&#95;length | 62 | S0696 |
| receiver&#95;rows&#91;0&#93;&#46;received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;07&#46;909507Z&#34; | S0697 |
| receiver&#95;rows&#91;0&#93;&#46;receipt&#95;id | &#34;receipt&#45;ed70aee572304470ae2fd9f3ee4db911&#34; | S0698 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0699

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0700 |

###### Recorded core dimensions

All values in the following table come from S0701

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0702

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0703

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0704 |

###### Recorded core dimensions

All values in the following table come from S0705

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0706

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase postflight

Frame or nearest existing container: S0707

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0708 |

###### Recorded core dimensions

All values in the following table come from S0709

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;ALLOW&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;DISPATCH&#95;OBSERVED&#34; |

###### Recorded core findings

All values in the following table come from S0710

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;BOUND&#95;DISPATCH&#95;OBSERVED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;ded884f22d644d7ca33e478a7f7497d1&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;OBSERVED&#95;ACTION&#95;HAS&#95;APPLICABLE&#95;AUTHORIZATION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;ded884f22d644d7ca33e478a7f7497d1&#34;&#44;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0051, S0052

**UPLOAD&#95;RECEIPT&#95;NOT&#95;PROCESSING** — The scoped local receiver receipt concerns matching bytes&#46; The core remote outcome remains UNKNOWN&#59; downstream processing or retention is not established&#46;

Source: S0053, S0054

### UL&#45;10 — Permission expires during pre&#45;send pause

Whole-case capture: S0064

Title source: S0065

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0058 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;admission&#95;allowed&#34;&#58;true&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0059 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;admission&#95;allowed&#34;&#58;true&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;received&#95;bytes&#95;match&#34;&#58;false&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0711 |
| differences | &#123;&#125; | S0712 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 0 | S0713 |
| admission&#95;allowed | true | S0714 |
| gateway&#95;attempts | 0 | S0715 |
| handler&#95;calls | 0 | S0716 |
| received&#95;bytes&#95;match | false | S0717 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; | S0718 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 0 | S0719 |
| accepted&#95;count | 0 | S0720 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34; | S0721 |
| attempted | false | S0063 |
| reason | &#34;FINAL&#95;ASSESSOR&#95;RECHECK&#95;DID&#95;NOT&#95;ALLOW&#34; | S0722 |
| journal&#95;state | &#34;blocked&#95;after&#95;intent&#34; | S0723 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0724 |
| byte&#95;length | 62 | S0725 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| transport&#95;observation | null | S0726 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0727 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0728

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0729 |

###### Recorded core dimensions

All values in the following table come from S0730

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0731

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0732

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0733 |

###### Recorded core dimensions

All values in the following table come from S0734

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;REVIEW&#34; |
| binding&#95;assessment | &#34;UNRESOLVED&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;HOLD&#95;PENDING&#95;CURRENT&#95;AUTHORIZATION&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;EXPIRED&#95;OR&#95;UNRESOLVED&#34; |
| proposed&#95;transfer&#95;authorization | &#34;REVIEW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;REVIEW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0735

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;POLICY&#95;NOT&#95;EFFECTIVE&#95;AT&#95;OPERATION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;policy&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;AUTHORIZATION&#95;NOT&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#93;&#125; |

##### original record index 0 — phase postflight

Frame or nearest existing container: S0736

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0737 |

###### Recorded core dimensions

All values in the following table come from S0738

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0739

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0058, S0059

**UPLOAD&#95;FINAL&#95;GATE&#95;DIFFERS** — The final gate required review and prevented an attempt&#46; Admission and postflight authorization preserve the earlier operation time and do not replace the final decision&#46;

Source: S0060, S0061, S0062, S0063

### UL&#45;11 — Repeated confirmed request does not send twice

Whole-case capture: S0071

Title source: S0072

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0067 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93;&#125; | S0068 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;true&#44;&#34;states&#34;&#58;&#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93;&#125; | S0740 |
| differences | &#123;&#125; | S0741 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 1 | S0742 |
| gateway&#95;attempts | 1 | S0743 |
| handler&#95;calls | 1 | S0744 |
| received&#95;bytes&#95;match | true | S0745 |
| states | &#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93; | S0746 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 1 | S0747 |
| accepted&#95;count | 1 | S0748 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;RECEIPT&#95;CONFIRMED&#34; | S0069 |
| attempted | true | S0749 |
| reason | &#34;PINNED&#95;RECEIVER&#95;ATTESTED&#95;MATCHING&#95;BYTES&#34; | S0750 |
| journal&#95;state | &#34;receipt&#95;confirmed&#34; | S0751 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0752 |
| byte&#95;length | 62 | S0753 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attempted | true | S0754 |
| body&#95;send&#95;completed | true | S0755 |
| attempted&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;10&#46;368944Z&#34; | S0756 |
| dispatched&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;10&#46;369156Z&#34; | S0757 |
| status | 200 | S0758 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;upload&#95;receipt&#34; | S0759 |
| request&#95;id | &#34;upload&#45;f9d90eb9b2874814acb7e094b8701139&#34; | S0760 |
| subject&#95;sha256 | &#34;ad927e1bf6e8f0e97c4dd8d28ee4f51406d2140b67c54b5ebbc5c2fa98d77288&#34; | S0761 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0762 |
| byte&#95;length | 62 | S0763 |
| received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;10&#46;371069Z&#34; | S0764 |
| receipt&#95;id | &#34;receipt&#45;d79dab552fd046e482f99a4031628528&#34; | S0765 |

##### operation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;REPLAY&#95;NO&#95;SEND&#34; | S0766 |
| attempted | false | S0767 |
| reason | &#34;REQUEST&#95;ALREADY&#95;CLAIMED&#95;RECEIPT&#95;NOT&#95;REASSERTED&#34; | S0768 |
| journal&#95;state | &#34;receipt&#95;confirmed&#34; | S0769 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0770 |
| byte&#95;length | 62 | S0771 |

##### transport — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| transport&#95;observation | null | S0772 |

##### receipt — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0773 |

##### receiver&#95;receipt — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| receiver&#95;rows&#91;0&#93;&#46;kind | &#34;upload&#95;receipt&#34; | S0774 |
| receiver&#95;rows&#91;0&#93;&#46;request&#95;id | &#34;upload&#45;f9d90eb9b2874814acb7e094b8701139&#34; | S0775 |
| receiver&#95;rows&#91;0&#93;&#46;subject&#95;sha256 | &#34;ad927e1bf6e8f0e97c4dd8d28ee4f51406d2140b67c54b5ebbc5c2fa98d77288&#34; | S0776 |
| receiver&#95;rows&#91;0&#93;&#46;payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0777 |
| receiver&#95;rows&#91;0&#93;&#46;byte&#95;length | 62 | S0778 |
| receiver&#95;rows&#91;0&#93;&#46;received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;10&#46;371069Z&#34; | S0779 |
| receiver&#95;rows&#91;0&#93;&#46;receipt&#95;id | &#34;receipt&#45;d79dab552fd046e482f99a4031628528&#34; | S0780 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0781

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0782 |

###### Recorded core dimensions

All values in the following table come from S0783

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0784

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0785

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0786 |

###### Recorded core dimensions

All values in the following table come from S0787

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0788

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase postflight

Frame or nearest existing container: S0789

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0790 |

###### Recorded core dimensions

All values in the following table come from S0791

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;ALLOW&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;DISPATCH&#95;OBSERVED&#34; |

###### Recorded core findings

All values in the following table come from S0792

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;BOUND&#95;DISPATCH&#95;OBSERVED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;ce180840fc944370bd10663135f73df5&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;OBSERVED&#95;ACTION&#95;HAS&#95;APPLICABLE&#95;AUTHORIZATION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;ce180840fc944370bd10663135f73df5&#34;&#44;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 1 — phase preflight

Frame or nearest existing container: S0793

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0794 |

###### Recorded core dimensions

All values in the following table come from S0795

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0796

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 1 — phase final&#95;gate

Frame or nearest existing container: S0797

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 1 — phase postflight

Frame or nearest existing container: S0798

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0799 |

###### Recorded core dimensions

All values in the following table come from S0800

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0801

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0067, S0068

**UPLOAD&#95;RECEIPT&#95;NOT&#95;PROCESSING** — The scoped local receiver receipt concerns matching bytes&#46; The core remote outcome remains UNKNOWN&#59; downstream processing or retention is not established&#46;

Source: S0069, S0070

### UL&#45;12 — Same request identifier with newly approved other bytes is rejected

Whole-case capture: S0078

Title source: S0079

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0074 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#44;&#34;REQUEST&#95;ID&#95;CONFLICT&#34;&#93;&#125; | S0075 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;true&#44;&#34;states&#34;&#58;&#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#44;&#34;REQUEST&#95;ID&#95;CONFLICT&#34;&#93;&#125; | S0802 |
| differences | &#123;&#125; | S0803 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 1 | S0804 |
| gateway&#95;attempts | 1 | S0805 |
| handler&#95;calls | 1 | S0806 |
| received&#95;bytes&#95;match | true | S0807 |
| states | &#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#44;&#34;REQUEST&#95;ID&#95;CONFLICT&#34;&#93; | S0808 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 1 | S0809 |
| accepted&#95;count | 1 | S0810 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;RECEIPT&#95;CONFIRMED&#34; | S0076 |
| attempted | true | S0811 |
| reason | &#34;PINNED&#95;RECEIVER&#95;ATTESTED&#95;MATCHING&#95;BYTES&#34; | S0812 |
| journal&#95;state | &#34;receipt&#95;confirmed&#34; | S0813 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0814 |
| byte&#95;length | 62 | S0815 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attempted | true | S0816 |
| body&#95;send&#95;completed | true | S0817 |
| attempted&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;10&#46;613441Z&#34; | S0818 |
| dispatched&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;10&#46;613624Z&#34; | S0819 |
| status | 200 | S0820 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;upload&#95;receipt&#34; | S0821 |
| request&#95;id | &#34;upload&#45;f47f46725126421ebdfb449e64f95958&#34; | S0822 |
| subject&#95;sha256 | &#34;6f88724c68eb9aad143e33e36398d0ab72647b36a04bdfa793eb329aecc4d822&#34; | S0823 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0824 |
| byte&#95;length | 62 | S0825 |
| received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;10&#46;615503Z&#34; | S0826 |
| receipt&#95;id | &#34;receipt&#45;0a1c68025c3747c686ed1d304bdc2472&#34; | S0827 |

##### operation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;REQUEST&#95;ID&#95;CONFLICT&#34; | S0828 |
| attempted | false | S0829 |
| reason | &#34;REQUEST&#95;ID&#95;ALREADY&#95;BOUND&#95;TO&#95;DIFFERENT&#95;ACTION&#34; | S0830 |
| journal&#95;state | &#34;receipt&#95;confirmed&#34; | S0831 |
| payload&#95;sha256 | &#34;5d4ee6c1ca3da7197ebbd81e9bc79955f8819b7b78c002f3ea9e6d0dca0ffde0&#34; | S0832 |
| byte&#95;length | 45 | S0833 |

##### transport — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| transport&#95;observation | null | S0834 |

##### receipt — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0835 |

##### receiver&#95;receipt — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| receiver&#95;rows&#91;0&#93;&#46;kind | &#34;upload&#95;receipt&#34; | S0836 |
| receiver&#95;rows&#91;0&#93;&#46;request&#95;id | &#34;upload&#45;f47f46725126421ebdfb449e64f95958&#34; | S0837 |
| receiver&#95;rows&#91;0&#93;&#46;subject&#95;sha256 | &#34;6f88724c68eb9aad143e33e36398d0ab72647b36a04bdfa793eb329aecc4d822&#34; | S0838 |
| receiver&#95;rows&#91;0&#93;&#46;payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0839 |
| receiver&#95;rows&#91;0&#93;&#46;byte&#95;length | 62 | S0840 |
| receiver&#95;rows&#91;0&#93;&#46;received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;10&#46;615503Z&#34; | S0841 |
| receiver&#95;rows&#91;0&#93;&#46;receipt&#95;id | &#34;receipt&#45;0a1c68025c3747c686ed1d304bdc2472&#34; | S0842 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0843

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0844 |

###### Recorded core dimensions

All values in the following table come from S0845

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0846

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0847

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0848 |

###### Recorded core dimensions

All values in the following table come from S0849

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0850

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase postflight

Frame or nearest existing container: S0851

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0852 |

###### Recorded core dimensions

All values in the following table come from S0853

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;ALLOW&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;DISPATCH&#95;OBSERVED&#34; |

###### Recorded core findings

All values in the following table come from S0854

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;BOUND&#95;DISPATCH&#95;OBSERVED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;4ab3acb5131a40c8969a386b5a30623c&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;OBSERVED&#95;ACTION&#95;HAS&#95;APPLICABLE&#95;AUTHORIZATION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;4ab3acb5131a40c8969a386b5a30623c&#34;&#44;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 1 — phase preflight

Frame or nearest existing container: S0855

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0856 |

###### Recorded core dimensions

All values in the following table come from S0857

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0858

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 1 — phase final&#95;gate

Frame or nearest existing container: S0859

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 1 — phase postflight

Frame or nearest existing container: S0860

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0861 |

###### Recorded core dimensions

All values in the following table come from S0862

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0863

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0074, S0075

**UPLOAD&#95;RECEIPT&#95;NOT&#95;PROCESSING** — The scoped local receiver receipt concerns matching bytes&#46; The core remote outcome remains UNKNOWN&#59; downstream processing or retention is not established&#46;

Source: S0076, S0077

### UL&#45;13 — HTTP redirect is never followed

Whole-case capture: S0083

Title source: S0084

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0081 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#93;&#125; | S0082 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;false&#44;&#34;states&#34;&#58;&#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#93;&#125; | S0864 |
| differences | &#123;&#125; | S0865 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 0 | S0866 |
| gateway&#95;attempts | 1 | S0867 |
| handler&#95;calls | 1 | S0868 |
| received&#95;bytes&#95;match | false | S0869 |
| states | &#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#93; | S0870 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 1 | S0871 |
| accepted&#95;count | 0 | S0872 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;OUTCOME&#95;UNKNOWN&#34; | S0873 |
| attempted | true | S0874 |
| reason | &#34;RECEIVER&#95;RECEIPT&#95;NOT&#95;CONFIRMED&#34; | S0875 |
| journal&#95;state | &#34;outcome&#95;unknown&#34; | S0876 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0877 |
| byte&#95;length | 62 | S0878 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attempted | true | S0879 |
| body&#95;send&#95;completed | true | S0880 |
| attempted&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;10&#46;857418Z&#34; | S0881 |
| dispatched&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;10&#46;857604Z&#34; | S0882 |
| status | 307 | S0883 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0884 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0885

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0886 |

###### Recorded core dimensions

All values in the following table come from S0887

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0888

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0889

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0890 |

###### Recorded core dimensions

All values in the following table come from S0891

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0892

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase postflight

Frame or nearest existing container: S0893

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0894 |

###### Recorded core dimensions

All values in the following table come from S0895

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;ALLOW&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;DISPATCH&#95;OBSERVED&#34; |

###### Recorded core findings

All values in the following table come from S0896

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;BOUND&#95;DISPATCH&#95;OBSERVED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;231ef6e811d7472b815ef112fae1d896&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;OBSERVED&#95;ACTION&#95;HAS&#95;APPLICABLE&#95;AUTHORIZATION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;231ef6e811d7472b815ef112fae1d896&#34;&#44;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0081, S0082

### UL&#45;14 — Unauthenticated endpoint exposes the outside&#45;route bypass

Whole-case capture: S0094

Title source: S0095

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0086 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;all&#95;route&#95;prevention&#95;established&#34;&#58;false&#44;&#34;controller&#95;direct&#95;status&#34;&#58;200&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0087 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;all&#95;route&#95;prevention&#95;established&#34;&#58;false&#44;&#34;controller&#95;direct&#95;status&#34;&#58;200&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;true&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93;&#125; | S0897 |
| differences | &#123;&#125; | S0898 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 1 | S0091 |
| all&#95;route&#95;prevention&#95;established | false | S0093 |
| controller&#95;direct&#95;status | 200 | S0092 |
| gateway&#95;attempts | 0 | S0089 |
| handler&#95;calls | 1 | S0090 |
| received&#95;bytes&#95;match | true | S0899 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34;&#93; | S0900 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 1 | S0901 |
| accepted&#95;count | 1 | S0902 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;ATTEMPT&#34; | S0088 |
| attempted | false | S0903 |
| reason | &#34;ASSESSOR&#95;DID&#95;NOT&#95;ALLOW&#95;MEASURED&#95;TARGET&#34; | S0904 |
| journal&#95;state | &#34;NOT&#95;CLAIMED&#34; | S0905 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0906 |
| byte&#95;length | 62 | S0907 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| transport&#95;observation | null | S0908 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0909 |

##### receiver&#95;receipt — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| receiver&#95;rows&#91;0&#93;&#46;kind | &#34;upload&#95;receipt&#34; | S0910 |
| receiver&#95;rows&#91;0&#93;&#46;request&#95;id | &#34;unauthenticated&#45;c57c83957a394a86b4b0b46c1629606d&#34; | S0911 |
| receiver&#95;rows&#91;0&#93;&#46;subject&#95;sha256 | &#34;8988b688bed7ecee810cbe650319a07ffeff0b02e03d284f6ad99a751846b736&#34; | S0912 |
| receiver&#95;rows&#91;0&#93;&#46;payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0913 |
| receiver&#95;rows&#91;0&#93;&#46;byte&#95;length | 62 | S0914 |
| receiver&#95;rows&#91;0&#93;&#46;received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;11&#46;089895Z&#34; | S0915 |
| receiver&#95;rows&#91;0&#93;&#46;receipt&#95;id | &#34;receipt&#45;46a8505c4d4b4eb79c628be5ac3521cc&#34; | S0916 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0917

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0918 |

###### Recorded core dimensions

All values in the following table come from S0919

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;BLOCK&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;BLOCK&#95;CONTROLLED&#95;ROUTE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;DENY&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;DENY&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0920

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;BOUND&#95;DENIAL&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0921

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 0 — phase postflight

Frame or nearest existing container: S0922

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0923 |

###### Recorded core dimensions

All values in the following table come from S0924

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;BLOCK&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;BLOCK&#95;CONTROLLED&#95;ROUTE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;DENY&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;DENY&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0925

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;BOUND&#95;DENIAL&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0086, S0087

**UPLOAD&#95;OUTSIDE&#95;ROUTE&#95;BYPASS** — The managed route recorded no attempt&#44; but the controller&#39;s direct request was accepted&#46; This negative control does not establish prevention across all routes&#46;

Source: S0088, S0089, S0090, S0091, S0092, S0093

### UL&#45;15 — Concurrent identical calls consume only one dispatch claim

Whole-case capture: S0101

Title source: S0102

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0097 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93;&#125; | S0098 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;true&#44;&#34;states&#34;&#58;&#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93;&#125; | S0926 |
| differences | &#123;&#125; | S0927 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 1 | S0928 |
| gateway&#95;attempts | 1 | S0929 |
| handler&#95;calls | 1 | S0930 |
| received&#95;bytes&#95;match | true | S0931 |
| states | &#91;&#34;RECEIPT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93; | S0932 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 1 | S0933 |
| accepted&#95;count | 1 | S0934 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;RECEIPT&#95;CONFIRMED&#34; | S0099 |
| attempted | true | S0935 |
| reason | &#34;PINNED&#95;RECEIVER&#95;ATTESTED&#95;MATCHING&#95;BYTES&#34; | S0936 |
| journal&#95;state | &#34;receipt&#95;confirmed&#34; | S0937 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0938 |
| byte&#95;length | 62 | S0939 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attempted | true | S0940 |
| body&#95;send&#95;completed | true | S0941 |
| attempted&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;11&#46;326322Z&#34; | S0942 |
| dispatched&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;11&#46;326501Z&#34; | S0943 |
| status | 200 | S0944 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;upload&#95;receipt&#34; | S0945 |
| request&#95;id | &#34;upload&#45;d5530a5560c449bd945679bbbd9cafff&#34; | S0946 |
| subject&#95;sha256 | &#34;b5f53a14a58c6fc7a6ae31996d0cf427306965c55866e53a8bc3a362cb501b32&#34; | S0947 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0948 |
| byte&#95;length | 62 | S0949 |
| received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;11&#46;328548Z&#34; | S0950 |
| receipt&#95;id | &#34;receipt&#45;2a8481ef4a094703b84f97060bb73dce&#34; | S0951 |

##### operation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;REPLAY&#95;NO&#95;SEND&#34; | S0952 |
| attempted | false | S0953 |
| reason | &#34;REQUEST&#95;ALREADY&#95;CLAIMED&#95;RECEIPT&#95;NOT&#95;REASSERTED&#34; | S0954 |
| journal&#95;state | &#34;dispatch&#95;intent&#34; | S0955 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0956 |
| byte&#95;length | 62 | S0957 |

##### transport — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| transport&#95;observation | null | S0958 |

##### receipt — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0959 |

##### receiver&#95;receipt — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| receiver&#95;rows&#91;0&#93;&#46;kind | &#34;upload&#95;receipt&#34; | S0960 |
| receiver&#95;rows&#91;0&#93;&#46;request&#95;id | &#34;upload&#45;d5530a5560c449bd945679bbbd9cafff&#34; | S0961 |
| receiver&#95;rows&#91;0&#93;&#46;subject&#95;sha256 | &#34;b5f53a14a58c6fc7a6ae31996d0cf427306965c55866e53a8bc3a362cb501b32&#34; | S0962 |
| receiver&#95;rows&#91;0&#93;&#46;payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0963 |
| receiver&#95;rows&#91;0&#93;&#46;byte&#95;length | 62 | S0964 |
| receiver&#95;rows&#91;0&#93;&#46;received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;11&#46;328548Z&#34; | S0965 |
| receiver&#95;rows&#91;0&#93;&#46;receipt&#95;id | &#34;receipt&#45;2a8481ef4a094703b84f97060bb73dce&#34; | S0966 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S0967

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0968 |

###### Recorded core dimensions

All values in the following table come from S0969

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0970

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S0971

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0972 |

###### Recorded core dimensions

All values in the following table come from S0973

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0974

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase postflight

Frame or nearest existing container: S0975

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0976 |

###### Recorded core dimensions

All values in the following table come from S0977

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;ALLOW&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;DISPATCH&#95;OBSERVED&#34; |

###### Recorded core findings

All values in the following table come from S0978

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;BOUND&#95;DISPATCH&#95;OBSERVED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;afb8c528d3fc4ca2b4d2fd447d4e2b93&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;OBSERVED&#95;ACTION&#95;HAS&#95;APPLICABLE&#95;AUTHORIZATION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;afb8c528d3fc4ca2b4d2fd447d4e2b93&#34;&#44;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 1 — phase preflight

Frame or nearest existing container: S0979

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0980 |

###### Recorded core dimensions

All values in the following table come from S0981

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0982

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 1 — phase final&#95;gate

Frame or nearest existing container: S0983

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 1 — phase postflight

Frame or nearest existing container: S0984

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S0985 |

###### Recorded core dimensions

All values in the following table come from S0986

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S0987

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0097, S0098

**UPLOAD&#95;RECEIPT&#95;NOT&#95;PROCESSING** — The scoped local receiver receipt concerns matching bytes&#46; The core remote outcome remains UNKNOWN&#59; downstream processing or retention is not established&#46;

Source: S0099, S0100

### UL&#45;16 — Injected result persistence failure leaves outcome unresolved

Whole-case capture: S0110

Title source: S0111

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0104 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#93;&#125; | S0105 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;1&#44;&#34;gateway&#95;attempts&#34;&#58;1&#44;&#34;handler&#95;calls&#34;&#58;1&#44;&#34;received&#95;bytes&#95;match&#34;&#58;true&#44;&#34;states&#34;&#58;&#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#93;&#125; | S0988 |
| differences | &#123;&#125; | S0989 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 1 | S0990 |
| gateway&#95;attempts | 1 | S0991 |
| handler&#95;calls | 1 | S0992 |
| received&#95;bytes&#95;match | true | S0993 |
| states | &#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#93; | S0994 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 1 | S0995 |
| accepted&#95;count | 1 | S0108 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;OUTCOME&#95;UNKNOWN&#34; | S0106 |
| attempted | true | S0996 |
| reason | &#34;JOURNAL&#95;RESULT&#95;PERSISTENCE&#95;FAILED&#34; | S0997 |
| journal&#95;state | &#34;dispatch&#95;intent&#34; | S0998 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S0999 |
| byte&#95;length | 62 | S1000 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attempted | true | S1001 |
| body&#95;send&#95;completed | true | S1002 |
| attempted&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;11&#46;573688Z&#34; | S1003 |
| dispatched&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;11&#46;573877Z&#34; | S1004 |
| status | 200 | S1005 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0107 |

##### receiver&#95;receipt — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| receiver&#95;rows&#91;0&#93;&#46;kind | &#34;upload&#95;receipt&#34; | S1006 |
| receiver&#95;rows&#91;0&#93;&#46;request&#95;id | &#34;upload&#45;61e12a8d3d45469ea75315c3557f1eb1&#34; | S1007 |
| receiver&#95;rows&#91;0&#93;&#46;subject&#95;sha256 | &#34;bbb4d02cdf78f2c6d6a4cf52767994d3e3f911e52478553500e51cfb2a1297a5&#34; | S1008 |
| receiver&#95;rows&#91;0&#93;&#46;payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S1009 |
| receiver&#95;rows&#91;0&#93;&#46;byte&#95;length | 62 | S1010 |
| receiver&#95;rows&#91;0&#93;&#46;received&#95;at | &#34;2026&#45;10&#45;30T01&#58;24&#58;11&#46;575782Z&#34; | S1011 |
| receiver&#95;rows&#91;0&#93;&#46;receipt&#95;id | &#34;receipt&#45;b6c28f605def4a369fba886e90a653e8&#34; | S1012 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1013

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1014 |

###### Recorded core dimensions

All values in the following table come from S1015

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S1016

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1017

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1018 |

###### Recorded core dimensions

All values in the following table come from S1019

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S1020

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase postflight

Frame or nearest existing container: S1021

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1022 |

###### Recorded core dimensions

All values in the following table come from S1023

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;ALLOW&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;DISPATCH&#95;OBSERVED&#34; |

###### Recorded core findings

All values in the following table come from S1024

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;BOUND&#95;DISPATCH&#95;OBSERVED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;7b0605b83cc442a6b5b9ed70ecbc85ef&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;OBSERVED&#95;ACTION&#95;HAS&#95;APPLICABLE&#95;AUTHORIZATION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;actual&#45;dispatch&#45;7b0605b83cc442a6b5b9ed70ecbc85ef&#34;&#44;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0104, S0105

**UPLOAD&#95;UNKNOWN&#95;WITH&#95;RECEIVER&#95;OBSERVATION** — The gateway outcome remains unknown while the receiver has an accepted&#45;request observation&#46; The receiver observation does not retroactively confirm the gateway result&#46;

Source: S0106, S0107, S0108, S0109

### UL&#45;17 — Worker killed after committed intent is not automatically resent

Whole-case capture: S0119

Title source: S0120

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0113 |
| expected | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93;&#44;&#34;worker&#95;killed&#95;after&#95;intent&#34;&#58;true&#125; | S0114 |
| actual | &#123;&#34;accepted&#95;count&#34;&#58;0&#44;&#34;gateway&#95;attempts&#34;&#58;0&#44;&#34;handler&#95;calls&#34;&#58;0&#44;&#34;received&#95;bytes&#95;match&#34;&#58;false&#44;&#34;states&#34;&#58;&#91;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93;&#44;&#34;worker&#95;exitcode&#34;&#58;&#45;9&#44;&#34;worker&#95;killed&#95;after&#95;intent&#34;&#58;true&#125; | S1025 |
| differences | &#123;&#125; | S1026 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| accepted&#95;count | 0 | S1027 |
| gateway&#95;attempts | 0 | S0118 |
| handler&#95;calls | 0 | S1028 |
| received&#95;bytes&#95;match | false | S1029 |
| states | &#91;&#34;REPLAY&#95;NO&#95;SEND&#34;&#93; | S1030 |
| worker&#95;exitcode | &#45;9 | S0116 |
| worker&#95;killed&#95;after&#95;intent | true | S0115 |

##### receiver — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| handler&#95;calls | 0 | S1031 |
| accepted&#95;count | 0 | S1032 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;REPLAY&#95;NO&#95;SEND&#34; | S1033 |
| attempted | false | S1034 |
| reason | &#34;REQUEST&#95;ALREADY&#95;CLAIMED&#95;RECEIPT&#95;NOT&#95;REASSERTED&#34; | S1035 |
| journal&#95;state | &#34;dispatch&#95;intent&#34; | S0117 |
| payload&#95;sha256 | &#34;dede6e85561971337af3f7d5e458b2457a306cd17a9de83b4ab7653fa621e201&#34; | S1036 |
| byte&#95;length | 62 | S1037 |

##### transport — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| transport&#95;observation | null | S1038 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1039 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1040

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1041 |

###### Recorded core dimensions

All values in the following table come from S1042

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S1043

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1044

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 0 — phase postflight

Frame or nearest existing container: S1045

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1046 |

###### Recorded core dimensions

All values in the following table come from S1047

| Field | Recorded value |
| --- | --- |
| application&#95;route&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| binding&#95;assessment | &#34;MATCH&#34; |
| collector&#95;health | &#34;UNKNOWN&#34; |
| control&#95;assessment | &#34;UNKNOWN&#34; |
| coverage | &#34;INCOMPLETE&#34; |
| dispatch&#95;action | &#34;PERMITTED&#95;WITHIN&#95;BOUND&#95;SCOPE&#34; |
| external&#95;activity&#95;assessment | &#34;UNKNOWN&#34; |
| observed&#95;action&#95;authorization | &#34;UNKNOWN&#34; |
| policy&#95;binding | &#34;CURRENT&#95;CONTENT&#95;BOUND&#34; |
| proposed&#95;transfer&#95;authorization | &#34;ALLOW&#34; |
| remote&#95;outcome | &#34;UNKNOWN&#34; |
| retry&#95;action | &#34;NOT&#95;ASSESSED&#34; |
| transfer&#95;authorization | &#34;ALLOW&#34; |
| transfer&#95;observation | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S1048

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;TRANSFER&#95;CURRENT&#95;POLICY&#95;AND&#95;PERMIT&#95;BIND&#95;TARGET&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;initial&#45;gateway&#34;&#44;&#34;initial&#45;policy&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0113, S0114

**UPLOAD&#95;INTENT&#95;NOT&#95;DISPATCH** — The captured worker was killed after intent and the repeated request did not resend&#46; A durable intent is not a body&#45;send observation&#46;

Source: S0115, S0116, S0117, S0118

### LP&#45;01 — Exact approved final HTML is materialized and measured

Whole-case capture: S0126

Title source: S0127

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0122 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S0123 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S1049 |
| differences | &#123;&#125; | S1050 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 1 | S1051 |
| states | &#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#93; | S1052 |
| unknown&#95;attempt&#95;observations | 0 | S1053 |
| visible&#95;bytes&#95;match&#95;candidate | true | S1054 |
| visible&#95;count | 1 | S1055 |
| sort&#95;states | false | S1056 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34; | S1057 |
| attempted | true | S1058 |
| reason | &#34;MEASURED&#95;LOCAL&#95;FILE&#95;CONFIRMED&#34; | S1059 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;563862Z&#34; | S1060 |
| publication&#46;journal&#95;state | &#34;local&#95;output&#95;confirmed&#34; | S1061 |
| publication&#46;visible&#95;name | &#34;8ef32f81e3a3e5138c186e74c92a42d52b0876802b8e6f74fe1b7e9116074284&#46;html&#34; | S1062 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1063 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1064 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;544078Z&#34; | S1065 |
| authorized&#95;local&#95;export | true | S0124 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1066 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;555170Z&#34; | S1067 |
| authorized&#95;local&#95;export | true | S1068 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1069 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;publication&#95;receipt&#34; | S1070 |
| request&#95;id | &#34;publication&#45;d132dc377b1b4815883e4fe9e58546e4&#34; | S1071 |
| fingerprint | &#34;723e827fd065227bd9bcf1b60680699deaac3d5027cfc2581510573aa3824c6f&#34; | S1072 |
| artifact&#95;sha256 | &#34;66c3dce462be32682b67aba66d9aa1a871266e3bd013193152dd93e913d47b9e&#34; | S1073 |
| disclosure&#95;sha256 | &#34;806e9855d8252a6930d98262c62dda3537d38d81932bacd1ecc6e959bae3a4b7&#34; | S1074 |
| byte&#95;length | 2856 | S1075 |
| destination&#95;id | &#34;synthetic&#45;venue&#34; | S1076 |
| visible&#95;name | &#34;8ef32f81e3a3e5138c186e74c92a42d52b0876802b8e6f74fe1b7e9116074284&#46;html&#34; | S1077 |
| observed&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;561933Z&#34; | S1078 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1079

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1080 |

###### Recorded core dimensions

All values in the following table come from S1081

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1082

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;5b2c85fce7bb4b54b627dd7760e79aa1&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;20ca38f8427440bb985183d8a5a11726&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;568065447451487d85c8b9fe74df79d9&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1083

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1084 |

###### Recorded core dimensions

All values in the following table come from S1085

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1086

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;5b2c85fce7bb4b54b627dd7760e79aa1&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;20ca38f8427440bb985183d8a5a11726&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;568065447451487d85c8b9fe74df79d9&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0122, S0123

**PUBLICATION&#95;CORE&#95;REMAINS&#95;REVIEW** — Separate authorization permitted this local export while the unchanged core remained REVIEW&#46; Local output is not external publisher delivery or acceptance&#46;

Source: S0124, S0125

### LP&#45;02 — Changed article cannot reuse the earlier approval

Whole-case capture: S0131

Title source: S0132

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0129 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S0130 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S1087 |
| differences | &#123;&#125; | S1088 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 0 | S1089 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; | S1090 |
| unknown&#95;attempt&#95;observations | 0 | S1091 |
| visible&#95;bytes&#95;match&#95;candidate | false | S1092 |
| visible&#95;count | 0 | S1093 |
| sort&#95;states | false | S1094 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34; | S1095 |
| attempted | false | S1096 |
| reason | &#34;Release authorization no longer matches candidate&#95;sha256&#34; | S1097 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;590818Z&#34; | S1098 |
| publication | null | S1099 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1100 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1101 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;590818Z&#34; | S1102 |
| authorized&#95;local&#95;export | false | S1103 |
| reason | &#34;Release authorization no longer matches candidate&#95;sha256&#34; | S1104 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1105 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1106 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1107

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1108 |

###### Recorded core dimensions

All values in the following table come from S1109

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;UNKNOWN&#34; |
| approval&#95;applicability | &#34;PRIOR&#95;REVISION&#95;ONLY&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;UNKNOWN&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1110

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;missing&#95;observation&#95;is&#95;not&#95;human&#95;only&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;abaaf0b525fa48b9b3467408c4c39c20&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;requires&#95;changed&#95;artifact&#95;reassessment&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;c91f8134be634e249a20fa1cb0a87a3e&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1105

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0129, S0130

### LP&#45;03 — Removed disclosure cannot reuse signed preparation evidence

Whole-case capture: S0136

Title source: S0137

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0134 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S0135 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S1111 |
| differences | &#123;&#125; | S1112 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 0 | S1113 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; | S1114 |
| unknown&#95;attempt&#95;observations | 0 | S1115 |
| visible&#95;bytes&#95;match&#95;candidate | false | S1116 |
| visible&#95;count | 0 | S1117 |
| sort&#95;states | false | S1118 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34; | S1119 |
| attempted | false | S1120 |
| reason | &#34;Final HTML differs from the controlled article&#47;disclosure rendering&#34; | S1121 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;613422Z&#34; | S1122 |
| publication | null | S1123 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1124 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1125 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;613422Z&#34; | S1126 |
| authorized&#95;local&#95;export | false | S1127 |
| reason | &#34;Final HTML differs from the controlled article&#47;disclosure rendering&#34; | S1128 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1129 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1130 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1131

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1129

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0134, S0135

### LP&#45;04 — A valid policy package for another venue is rejected

Whole-case capture: S0141

Title source: S0142

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0139 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S0140 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S1132 |
| differences | &#123;&#125; | S1133 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 0 | S1134 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; | S1135 |
| unknown&#95;attempt&#95;observations | 0 | S1136 |
| visible&#95;bytes&#95;match&#95;candidate | false | S1137 |
| visible&#95;count | 0 | S1138 |
| sort&#95;states | false | S1139 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34; | S1140 |
| attempted | false | S1141 |
| reason | &#34;Candidate target differs from measured bytes&#44; revision&#44; venue or policy&#34; | S1142 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;631873Z&#34; | S1143 |
| publication | null | S1144 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1145 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1146 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;631873Z&#34; | S1147 |
| authorized&#95;local&#95;export | false | S1148 |
| reason | &#34;Candidate target differs from measured bytes&#44; revision&#44; venue or policy&#34; | S1149 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1150 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1151 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1152

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1150

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0139, S0140

### LP&#45;05 — Disclosure and reviewer approval do not override prohibited use

Whole-case capture: S0148

Title source: S0149

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0144 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S0145 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S1153 |
| differences | &#123;&#125; | S1154 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 0 | S1155 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; | S1156 |
| unknown&#95;attempt&#95;observations | 0 | S1157 |
| visible&#95;bytes&#95;match&#95;candidate | false | S1158 |
| visible&#95;count | 0 | S1159 |
| sort&#95;states | false | S1160 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34; | S1161 |
| attempted | false | S1162 |
| reason | &#34;Recorded session activity is prohibited by the pinned release policy&#34; | S1163 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;648034Z&#34; | S1164 |
| publication | null | S1165 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1166 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1167 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;648034Z&#34; | S1168 |
| authorized&#95;local&#95;export | false | S1169 |
| reason | &#34;Recorded session activity is prohibited by the pinned release policy&#34; | S1170 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1171 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1172 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1173

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1174 |

###### Recorded core dimensions

All values in the following table come from S1175

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;PROHIBITED&#95;USE&#34; |
| publication&#95;action | &#34;BLOCK&#34; |

###### Recorded core findings

All values in the following table come from S1176

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;18305aec2d9e444b82aae820ee3d486a&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;d3cdc750e4324c2e83ad287c70e972fb&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;disclosure&#95;does&#95;not&#95;override&#95;prohibition&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;040c093429e5417dac45d29268d468b4&#34;&#44;&#34;record&#45;18305aec2d9e444b82aae820ee3d486a&#34;&#93;&#125; |
| 3 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;fef69c8bba28406fba42dcf7ec1cb897&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1171

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0144, S0145

**PUBLICATION&#95;DISCLOSURE&#95;NOT&#95;OVERRIDE** — Recorded disclosure and reviewer approval did not override prohibited use under the pinned policy&#46;

Source: S0146, S0147

### LP&#45;06 — Missing explicit reviewer authorization prevents output

Whole-case capture: S0153

Title source: S0154

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0151 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S0152 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S1177 |
| differences | &#123;&#125; | S1178 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 0 | S1179 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; | S1180 |
| unknown&#95;attempt&#95;observations | 0 | S1181 |
| visible&#95;bytes&#95;match&#95;candidate | false | S1182 |
| visible&#95;count | 0 | S1183 |
| sort&#95;states | false | S1184 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34; | S1185 |
| attempted | false | S1186 |
| reason | &#34;Separate explicit reviewer release authorization is required&#34; | S1187 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;670673Z&#34; | S1188 |
| publication | null | S1189 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1190 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1191 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;670673Z&#34; | S1192 |
| authorized&#95;local&#95;export | false | S1193 |
| reason | &#34;Separate explicit reviewer release authorization is required&#34; | S1194 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1195 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1196 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1197

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1198 |

###### Recorded core dimensions

All values in the following table come from S1199

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;NOT&#95;ESTABLISHED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1200

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;8d3c05736fd042b9902c30547076ac27&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;cef40cc88d444b94a226dc333e927072&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;required&#95;approval&#95;not&#95;established&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;de279bb3f821465583be5dab6ed61c1b&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1195

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0151, S0152

### LP&#45;07 — Untrusted reviewer signature prevents output

Whole-case capture: S0158

Title source: S0159

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0156 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S0157 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S1201 |
| differences | &#123;&#125; | S1202 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 0 | S1203 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; | S1204 |
| unknown&#95;attempt&#95;observations | 0 | S1205 |
| visible&#95;bytes&#95;match&#95;candidate | false | S1206 |
| visible&#95;count | 0 | S1207 |
| sort&#95;states | false | S1208 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34; | S1209 |
| attempted | false | S1210 |
| reason | &#34;Required evidence signature&#44; identity&#44; role or recording time failed&#34; | S1211 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;693791Z&#34; | S1212 |
| publication | null | S1213 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1214 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1215 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;693791Z&#34; | S1216 |
| authorized&#95;local&#95;export | false | S1217 |
| reason | &#34;Required evidence signature&#44; identity&#44; role or recording time failed&#34; | S1218 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1219 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1220 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1221

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;FAILED&#34; | S1222 |

###### Recorded core dimensions

All values in the following table come from S1223

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;NOT&#95;ESTABLISHED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1224

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;d421657b20e940f7bc0976598e7b0728&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;672a4ac1e6544d52b04bd736ac3d7dec&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;required&#95;approval&#95;not&#95;established&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;d014c29db9be4d98a64581338409e149&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1219

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0156, S0157

### LP&#45;08 — Approval expires during an actual pre&#45;link pause

Whole-case capture: S0166

Title source: S0167

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0161 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S0162 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S1225 |
| differences | &#123;&#125; | S1226 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 0 | S1227 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; | S1228 |
| unknown&#95;attempt&#95;observations | 0 | S1229 |
| visible&#95;bytes&#95;match&#95;candidate | false | S1230 |
| visible&#95;count | 0 | S1231 |
| sort&#95;states | false | S1232 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34; | S1233 |
| attempted | false | S0165 |
| reason | &#34;FINAL&#95;GATE&#95;BLOCKED&#95;PUBLICATION&#34; | S1234 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;836696Z&#34; | S1235 |
| publication&#46;journal&#95;state | &#34;blocked&#95;after&#95;intent&#34; | S1236 |
| publication&#46;visible&#95;name | &#34;e95431818f15574338e2ada96d97772ca61e2d579be9a8b1271eea366db7aa99&#46;html&#34; | S1237 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1238 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1239 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;03&#46;717380Z&#34; | S1240 |
| authorized&#95;local&#95;export | true | S0163 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1241 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;827347Z&#34; | S1242 |
| authorized&#95;local&#95;export | false | S0164 |
| reason | &#34;Reviewer authorization is premature&#44; future or expired&#34; | S1243 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1244 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1245

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1246 |

###### Recorded core dimensions

All values in the following table come from S1247

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1248

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;700e07d5dc7f4f8a8765cdab9a0ec95f&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;1381231b22e74194b94ed792788c831d&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;157a6b5d5cec4f39844d7e586d86345e&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1249

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1250 |

###### Recorded core dimensions

All values in the following table come from S1251

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;NOT&#95;ESTABLISHED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1252

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;700e07d5dc7f4f8a8765cdab9a0ec95f&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;1381231b22e74194b94ed792788c831d&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;time&#95;inapplicable&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;157a6b5d5cec4f39844d7e586d86345e&#34;&#93;&#125; |
| 3 | &#123;&#34;code&#34;&#58;&#34;publication&#95;required&#95;approval&#95;not&#95;established&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;32af45a0f9d14f86ba0ca7f170be3ac9&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0161, S0162

**PUBLICATION&#95;FINAL&#95;AUTHORIZATION&#95;CHANGED** — Initial local authorization was true&#44; but final authorization was false after expiry&#46; Preserve both decisions rather than treating initial approval as current permission&#46;

Source: S0163, S0164, S0165

### LP&#45;09 — Unknown imported origin remains unknown after approved local export

Whole-case capture: S0176

Title source: S0177

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0169 |
| expected | &#123;&#34;core&#95;activity&#95;completeness&#34;&#58;&#34;UNKNOWN&#34;&#44;&#34;core&#95;ai&#95;involvement&#34;&#58;&#34;UNKNOWN&#34;&#44;&#34;declared&#95;activities&#34;&#58;&#91;&#93;&#44;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S0170 |
| actual | &#123;&#34;core&#95;activity&#95;completeness&#34;&#58;&#34;UNKNOWN&#34;&#44;&#34;core&#95;ai&#95;involvement&#34;&#58;&#34;UNKNOWN&#34;&#44;&#34;declared&#95;activities&#34;&#58;&#91;&#93;&#44;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S1253 |
| differences | &#123;&#125; | S1254 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 1 | S1255 |
| states | &#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#93; | S1256 |
| unknown&#95;attempt&#95;observations | 0 | S1257 |
| visible&#95;bytes&#95;match&#95;candidate | true | S1258 |
| visible&#95;count | 1 | S1259 |
| sort&#95;states | false | S1260 |

##### additional&#95;observations — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;activity&#95;completeness | &#34;UNKNOWN&#34; | S0172 |
| core&#95;ai&#95;involvement | &#34;UNKNOWN&#34; | S0171 |
| declared&#95;activities | &#91;&#93; | S0173 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34; | S1261 |
| attempted | true | S1262 |
| reason | &#34;MEASURED&#95;LOCAL&#95;FILE&#95;CONFIRMED&#34; | S1263 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;877379Z&#34; | S1264 |
| publication&#46;journal&#95;state | &#34;local&#95;output&#95;confirmed&#34; | S1265 |
| publication&#46;visible&#95;name | &#34;9dbfa6f7e567b2f25c9fc83fc00266d67dfcabd8fee9238016a0a25c04d90064&#46;html&#34; | S1266 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#93; | S1267 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1268 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;860670Z&#34; | S1269 |
| authorized&#95;local&#95;export | true | S0174 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1270 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;869335Z&#34; | S1271 |
| authorized&#95;local&#95;export | true | S1272 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1273 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;publication&#95;receipt&#34; | S1274 |
| request&#95;id | &#34;publication&#45;e00550928f834d3997e7dd05b293ecb7&#34; | S1275 |
| fingerprint | &#34;566ab013a9432dcd90e65ba82565016a9c221fefde5dab01848d89e94929ef90&#34; | S1276 |
| artifact&#95;sha256 | &#34;86b6d4cf3bc68805fff731ca412a2e3f8540f4ff2164c1eeec6a6e6c9dff0136&#34; | S1277 |
| disclosure&#95;sha256 | &#34;0f8bea7e65d77736a2f294b2b74768720ef17d68440c3b1606b3bce7bd11af51&#34; | S1278 |
| byte&#95;length | 2823 | S1279 |
| destination&#95;id | &#34;synthetic&#45;venue&#34; | S1280 |
| visible&#95;name | &#34;9dbfa6f7e567b2f25c9fc83fc00266d67dfcabd8fee9238016a0a25c04d90064&#46;html&#34; | S1281 |
| observed&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;874983Z&#34; | S1282 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1283

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1284 |

###### Recorded core dimensions

All values in the following table come from S1285

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;UNKNOWN&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;UNKNOWN&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1286

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;missing&#95;observation&#95;is&#95;not&#95;human&#95;only&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;6037dd77bda24cbbaff1623a8de89d78&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;16eadb2b7ab74e289c777afd561c906b&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1287

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1288 |

###### Recorded core dimensions

All values in the following table come from S1289

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;UNKNOWN&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;UNKNOWN&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1290

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;missing&#95;observation&#95;is&#95;not&#95;human&#95;only&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;6037dd77bda24cbbaff1623a8de89d78&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;16eadb2b7ab74e289c777afd561c906b&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0169, S0170

**PUBLICATION&#95;UNKNOWN&#95;ORIGIN** — Current AI involvement and activity completeness remain UNKNOWN&#46; Disclosure of recorded activity&#44; or its absence&#44; does not establish human&#45;only origin or complete provenance&#46;

Source: S0171, S0172, S0173

**PUBLICATION&#95;CORE&#95;REMAINS&#95;REVIEW** — Separate authorization permitted this local export while the unchanged core remained REVIEW&#46; Local output is not external publisher delivery or acceptance&#46;

Source: S0174, S0175

### LP&#45;10 — Replaced synthetic AI operation remains history without exact final adoption

Whole-case capture: S0186

Title source: S0187

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0179 |
| expected | &#123;&#34;core&#95;activity&#95;completeness&#34;&#58;&#34;UNKNOWN&#34;&#44;&#34;core&#95;ai&#95;involvement&#34;&#58;&#34;UNKNOWN&#34;&#44;&#34;declared&#95;activities&#34;&#58;&#91;&#34;generation&#34;&#93;&#44;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S0180 |
| actual | &#123;&#34;core&#95;activity&#95;completeness&#34;&#58;&#34;UNKNOWN&#34;&#44;&#34;core&#95;ai&#95;involvement&#34;&#58;&#34;UNKNOWN&#34;&#44;&#34;declared&#95;activities&#34;&#58;&#91;&#34;generation&#34;&#93;&#44;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S1291 |
| differences | &#123;&#125; | S1292 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 1 | S1293 |
| states | &#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#93; | S1294 |
| unknown&#95;attempt&#95;observations | 0 | S1295 |
| visible&#95;bytes&#95;match&#95;candidate | true | S1296 |
| visible&#95;count | 1 | S1297 |
| sort&#95;states | false | S1298 |

##### additional&#95;observations — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;activity&#95;completeness | &#34;UNKNOWN&#34; | S0182 |
| core&#95;ai&#95;involvement | &#34;UNKNOWN&#34; | S0181 |
| declared&#95;activities | &#91;&#34;generation&#34;&#93; | S0183 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34; | S1299 |
| attempted | true | S1300 |
| reason | &#34;MEASURED&#95;LOCAL&#95;FILE&#95;CONFIRMED&#34; | S1301 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;919737Z&#34; | S1302 |
| publication&#46;journal&#95;state | &#34;local&#95;output&#95;confirmed&#34; | S1303 |
| publication&#46;visible&#95;name | &#34;996bc83bb84ed6d80be2dab06a353ef9082967eed5e43ee19ebf5875f881c07f&#46;html&#34; | S1304 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1305 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1306 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;901818Z&#34; | S1307 |
| authorized&#95;local&#95;export | true | S0184 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1308 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;911351Z&#34; | S1309 |
| authorized&#95;local&#95;export | true | S1310 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1311 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;publication&#95;receipt&#34; | S1312 |
| request&#95;id | &#34;publication&#45;e4315eda6eb441dcb606c91008a044cb&#34; | S1313 |
| fingerprint | &#34;b72d27e1c6a12c25f919b924005231cb633bf4548b193c6843c6cc28c9871306&#34; | S1314 |
| artifact&#95;sha256 | &#34;94e708006ac899c19a6f5c85e384b02e18d53253335225c1ee6ef3b249708bde&#34; | S1315 |
| disclosure&#95;sha256 | &#34;806e9855d8252a6930d98262c62dda3537d38d81932bacd1ecc6e959bae3a4b7&#34; | S1316 |
| byte&#95;length | 2807 | S1317 |
| destination&#95;id | &#34;synthetic&#45;venue&#34; | S1318 |
| visible&#95;name | &#34;996bc83bb84ed6d80be2dab06a353ef9082967eed5e43ee19ebf5875f881c07f&#46;html&#34; | S1319 |
| observed&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;917668Z&#34; | S1320 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1321

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1322 |

###### Recorded core dimensions

All values in the following table come from S1323

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;UNKNOWN&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;UNKNOWN&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1324

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;missing&#95;observation&#95;is&#95;not&#95;human&#95;only&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;349c6ab1eaad477a8d8a25289af38da0&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;dfd18bd20e514d96afc71425c4398091&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1325

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1326 |

###### Recorded core dimensions

All values in the following table come from S1327

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;UNKNOWN&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;UNKNOWN&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1328

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;missing&#95;observation&#95;is&#95;not&#95;human&#95;only&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;349c6ab1eaad477a8d8a25289af38da0&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;dfd18bd20e514d96afc71425c4398091&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0179, S0180

**PUBLICATION&#95;UNKNOWN&#95;ORIGIN** — Current AI involvement and activity completeness remain UNKNOWN&#46; Disclosure of recorded activity&#44; or its absence&#44; does not establish human&#45;only origin or complete provenance&#46;

Source: S0181, S0182, S0183

**PUBLICATION&#95;CORE&#95;REMAINS&#95;REVIEW** — Separate authorization permitted this local export while the unchanged core remained REVIEW&#46; Local output is not external publisher delivery or acceptance&#46;

Source: S0184, S0185

### LP&#45;11 — Truncated signed edit history cannot become a valid candidate

Whole-case capture: S0191

Title source: S0192

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0189 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S0190 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S1329 |
| differences | &#123;&#125; | S1330 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 0 | S1331 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; | S1332 |
| unknown&#95;attempt&#95;observations | 0 | S1333 |
| visible&#95;bytes&#95;match&#95;candidate | false | S1334 |
| visible&#95;count | 0 | S1335 |
| sort&#95;states | false | S1336 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34; | S1337 |
| attempted | false | S1338 |
| reason | &#34;Editor sequence or document identity mismatch&#34; | S1339 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;943327Z&#34; | S1340 |
| publication | null | S1341 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1342 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1343 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;943327Z&#34; | S1344 |
| authorized&#95;local&#95;export | false | S1345 |
| reason | &#34;Editor sequence or document identity mismatch&#34; | S1346 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1347 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1348 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1349

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1347

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0189, S0190

### LP&#45;12 — Unresolved policy interpretation prevents output

Whole-case capture: S0196

Title source: S0197

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0194 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S0195 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S1350 |
| differences | &#123;&#125; | S1351 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 0 | S1352 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; | S1353 |
| unknown&#95;attempt&#95;observations | 0 | S1354 |
| visible&#95;bytes&#95;match&#95;candidate | false | S1355 |
| visible&#95;count | 0 | S1356 |
| sort&#95;states | false | S1357 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34; | S1358 |
| attempted | false | S1359 |
| reason | &#34;Publication policy applicability or interpretation is unresolved&#34; | S1360 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;958167Z&#34; | S1361 |
| publication | null | S1362 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1363 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1364 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;958167Z&#34; | S1365 |
| authorized&#95;local&#95;export | false | S1366 |
| reason | &#34;Publication policy applicability or interpretation is unresolved&#34; | S1367 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1368 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1369 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1370

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1371 |

###### Recorded core dimensions

All values in the following table come from S1372

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;UNRESOLVED&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1373

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;84fa148f670244dc91c3be8024900a94&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;7f092617942243969a367b79a55e20a8&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;stage&#95;or&#95;interpretation&#95;unresolved&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;0398b288a86f40d28d11c9f13798311b&#34;&#93;&#125; |
| 3 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;dd31061671244e7abc2fd2bbea2e229a&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1368

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0194, S0195

### LP&#45;13 — Repeated identical request does not publish again

Whole-case capture: S0203

Title source: S0204

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0199 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S0200 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S1374 |
| differences | &#123;&#125; | S1375 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 1 | S1376 |
| states | &#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;PUBLICATION&#34;&#93; | S1377 |
| unknown&#95;attempt&#95;observations | 0 | S1378 |
| visible&#95;bytes&#95;match&#95;candidate | true | S1379 |
| visible&#95;count | 1 | S1380 |
| sort&#95;states | false | S1381 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34; | S1382 |
| attempted | true | S1383 |
| reason | &#34;MEASURED&#95;LOCAL&#95;FILE&#95;CONFIRMED&#34; | S1384 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;000975Z&#34; | S1385 |
| publication&#46;journal&#95;state | &#34;local&#95;output&#95;confirmed&#34; | S1386 |
| publication&#46;visible&#95;name | &#34;a3334b53ddf3cc1865a547175cc3950ee2fa89ae8bbcef9b38f6393bcd8acd21&#46;html&#34; | S1387 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1388 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1389 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;981897Z&#34; | S1390 |
| authorized&#95;local&#95;export | true | S0201 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1391 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;991983Z&#34; | S1392 |
| authorized&#95;local&#95;export | true | S1393 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1394 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;publication&#95;receipt&#34; | S1395 |
| request&#95;id | &#34;publication&#45;c59e3c77ce654277a1b7e75935aaa13c&#34; | S1396 |
| fingerprint | &#34;728127e9b1d001fd53eacc6aa4b1fbc682fee5e1aca34067e1bd53040b634d15&#34; | S1397 |
| artifact&#95;sha256 | &#34;66c3dce462be32682b67aba66d9aa1a871266e3bd013193152dd93e913d47b9e&#34; | S1398 |
| disclosure&#95;sha256 | &#34;806e9855d8252a6930d98262c62dda3537d38d81932bacd1ecc6e959bae3a4b7&#34; | S1399 |
| byte&#95;length | 2856 | S1400 |
| destination&#95;id | &#34;synthetic&#45;venue&#34; | S1401 |
| visible&#95;name | &#34;a3334b53ddf3cc1865a547175cc3950ee2fa89ae8bbcef9b38f6393bcd8acd21&#46;html&#34; | S1402 |
| observed&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;05&#46;998820Z&#34; | S1403 |

##### operation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;REPLAY&#95;NO&#95;PUBLICATION&#34; | S1404 |
| attempted | false | S1405 |
| reason | &#34;REQUEST&#95;ALREADY&#95;CLAIMED&#95;NO&#95;RECEIPT&#95;REASSERTED&#34; | S1406 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;009543Z&#34; | S1407 |
| publication&#46;journal&#95;state | &#34;local&#95;output&#95;confirmed&#34; | S1408 |
| publication&#46;visible&#95;name | &#34;a3334b53ddf3cc1865a547175cc3950ee2fa89ae8bbcef9b38f6393bcd8acd21&#46;html&#34; | S1409 |

##### disclosure — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1410 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1411 |

##### authorization&#95;preflight — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;001391Z&#34; | S1412 |
| authorized&#95;local&#95;export | true | S1413 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1414 |

##### authorization&#95;final&#95;gate — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1415 |

##### receipt — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1416 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1417

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1418 |

###### Recorded core dimensions

All values in the following table come from S1419

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1420

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;d8e33839dcb149f291c0ea1639799be7&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;cf9bdd9dc8d34a8796c5e50d6552e965&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;f68770ffb0ae4a5fbe4636d748e273a6&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1421

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1422 |

###### Recorded core dimensions

All values in the following table come from S1423

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1424

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;d8e33839dcb149f291c0ea1639799be7&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;cf9bdd9dc8d34a8796c5e50d6552e965&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;f68770ffb0ae4a5fbe4636d748e273a6&#34;&#93;&#125; |

##### original record index 1 — phase preflight

Frame or nearest existing container: S1425

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1426 |

###### Recorded core dimensions

All values in the following table come from S1427

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1428

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;d8e33839dcb149f291c0ea1639799be7&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;cf9bdd9dc8d34a8796c5e50d6552e965&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;f68770ffb0ae4a5fbe4636d748e273a6&#34;&#93;&#125; |

##### original record index 1 — phase final&#95;gate

Frame or nearest existing container: S1415

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0199, S0200

**PUBLICATION&#95;CORE&#95;REMAINS&#95;REVIEW** — Separate authorization permitted this local export while the unchanged core remained REVIEW&#46; Local output is not external publisher delivery or acceptance&#46;

Source: S0201, S0202

### LP&#45;14 — Result persistence failure leaves visible output unresolved and never retries

Whole-case capture: S0211

Title source: S0212

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0206 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#44;&#34;REPLAY&#95;NO&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S0207 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#44;&#34;REPLAY&#95;NO&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S1429 |
| differences | &#123;&#125; | S1430 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 1 | S1431 |
| states | &#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#44;&#34;REPLAY&#95;NO&#95;PUBLICATION&#34;&#93; | S1432 |
| unknown&#95;attempt&#95;observations | 0 | S1433 |
| visible&#95;bytes&#95;match&#95;candidate | true | S1434 |
| visible&#95;count | 1 | S1435 |
| sort&#95;states | false | S1436 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;OUTCOME&#95;UNKNOWN&#34; | S0208 |
| attempted | true | S1437 |
| reason | &#34;PUBLICATION&#95;RESULT&#95;PERSISTENCE&#95;NOT&#95;ESTABLISHED&#34; | S1438 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;062184Z&#34; | S1439 |
| publication&#46;journal&#95;state | &#34;publication&#95;intent&#34; | S1440 |
| publication&#46;visible&#95;name | &#34;da072ff55cd0337e7ccca9ae6cf70e992327758352f09ac10f3b8be4c3f7284f&#46;html&#34; | S1441 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1442 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1443 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;044059Z&#34; | S1444 |
| authorized&#95;local&#95;export | true | S1445 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1446 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;054400Z&#34; | S1447 |
| authorized&#95;local&#95;export | true | S1448 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1449 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0209 |

##### operation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;REPLAY&#95;NO&#95;PUBLICATION&#34; | S1450 |
| attempted | false | S1451 |
| reason | &#34;REQUEST&#95;ALREADY&#95;CLAIMED&#95;NO&#95;RECEIPT&#95;REASSERTED&#34; | S1452 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;070690Z&#34; | S1453 |
| publication&#46;journal&#95;state | &#34;publication&#95;intent&#34; | S1454 |
| publication&#46;visible&#95;name | &#34;da072ff55cd0337e7ccca9ae6cf70e992327758352f09ac10f3b8be4c3f7284f&#46;html&#34; | S1455 |

##### disclosure — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1456 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1457 |

##### authorization&#95;preflight — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;062469Z&#34; | S1458 |
| authorized&#95;local&#95;export | true | S1459 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1460 |

##### authorization&#95;final&#95;gate — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1461 |

##### receipt — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1462 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1463

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1464 |

###### Recorded core dimensions

All values in the following table come from S1465

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1466

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;7a8b97237ae7446c99afb3d65ad5e659&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;07a9cde59ba044ec8d70820e63535927&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;03fce430a1994144845c9bfe7652c750&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1467

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1468 |

###### Recorded core dimensions

All values in the following table come from S1469

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1470

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;7a8b97237ae7446c99afb3d65ad5e659&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;07a9cde59ba044ec8d70820e63535927&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;03fce430a1994144845c9bfe7652c750&#34;&#93;&#125; |

##### original record index 1 — phase preflight

Frame or nearest existing container: S1471

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1472 |

###### Recorded core dimensions

All values in the following table come from S1473

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1474

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;7a8b97237ae7446c99afb3d65ad5e659&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;07a9cde59ba044ec8d70820e63535927&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;03fce430a1994144845c9bfe7652c750&#34;&#93;&#125; |

##### original record index 1 — phase final&#95;gate

Frame or nearest existing container: S1461

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0206, S0207

**PUBLICATION&#95;UNKNOWN&#95;WITH&#95;VISIBLE&#95;FILE** — A visible&#45;file observation coexists with an unresolved publication result&#46; The retained file does not restore the withheld completion receipt&#46;

Source: S0208, S0209, S0210

### LP&#45;15 — Concurrent identical requests consume one publication claim

Whole-case capture: S0221

Title source: S0222

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0214 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S0215 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S1475 |
| differences | &#123;&#125; | S1476 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 1 | S1477 |
| states | &#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;PUBLICATION&#34;&#93; | S1478 |
| unknown&#95;attempt&#95;observations | 0 | S1479 |
| visible&#95;bytes&#95;match&#95;candidate | true | S1480 |
| visible&#95;count | 1 | S1481 |
| sort&#95;states | true | S0218 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;REPLAY&#95;NO&#95;PUBLICATION&#34; | S1482 |
| attempted | false | S1483 |
| reason | &#34;REQUEST&#95;ALREADY&#95;CLAIMED&#95;NO&#95;RECEIPT&#95;REASSERTED&#34; | S1484 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;128719Z&#34; | S1485 |
| publication&#46;journal&#95;state | &#34;publication&#95;intent&#34; | S1486 |
| publication&#46;visible&#95;name | &#34;197a0e9e427049bdce33ebf051acea403de54cd915d17715570e8364e1635492&#46;html&#34; | S1487 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1488 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1489 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;105951Z&#34; | S1490 |
| authorized&#95;local&#95;export | true | S1491 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1492 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1493 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1494 |

##### operation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34; | S1495 |
| attempted | true | S1496 |
| reason | &#34;MEASURED&#95;LOCAL&#95;FILE&#95;CONFIRMED&#34; | S1497 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;132974Z&#34; | S1498 |
| publication&#46;journal&#95;state | &#34;local&#95;output&#95;confirmed&#34; | S1499 |
| publication&#46;visible&#95;name | &#34;197a0e9e427049bdce33ebf051acea403de54cd915d17715570e8364e1635492&#46;html&#34; | S1500 |

##### disclosure — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1501 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1502 |

##### authorization&#95;preflight — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;109229Z&#34; | S1503 |
| authorized&#95;local&#95;export | true | S0216 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1504 |

##### authorization&#95;final&#95;gate — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;123097Z&#34; | S1505 |
| authorized&#95;local&#95;export | true | S1506 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1507 |

##### receipt — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;publication&#95;receipt&#34; | S1508 |
| request&#95;id | &#34;publication&#45;03fc267c8c5946d997598354323d5258&#34; | S1509 |
| fingerprint | &#34;976961b68b5bca3786a42ad1b3e411f2c2f48759c687dd29f42e5e5d848963c1&#34; | S1510 |
| artifact&#95;sha256 | &#34;66c3dce462be32682b67aba66d9aa1a871266e3bd013193152dd93e913d47b9e&#34; | S1511 |
| disclosure&#95;sha256 | &#34;806e9855d8252a6930d98262c62dda3537d38d81932bacd1ecc6e959bae3a4b7&#34; | S1512 |
| byte&#95;length | 2856 | S1513 |
| destination&#95;id | &#34;synthetic&#45;venue&#34; | S1514 |
| visible&#95;name | &#34;197a0e9e427049bdce33ebf051acea403de54cd915d17715570e8364e1635492&#46;html&#34; | S1515 |
| observed&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;130639Z&#34; | S1516 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1517

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1518 |

###### Recorded core dimensions

All values in the following table come from S1519

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1520

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;1ba89dd2624d46408a812ffb9ee33c34&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;0e2df2168fa546d5b069a9af2710a8b3&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;25b329f2edd94909a07cc8206966b5dd&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1493

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 1 — phase preflight

Frame or nearest existing container: S1521

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1522 |

###### Recorded core dimensions

All values in the following table come from S1523

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1524

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;1ba89dd2624d46408a812ffb9ee33c34&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;0e2df2168fa546d5b069a9af2710a8b3&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;25b329f2edd94909a07cc8206966b5dd&#34;&#93;&#125; |

##### original record index 1 — phase final&#95;gate

Frame or nearest existing container: S1525

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1526 |

###### Recorded core dimensions

All values in the following table come from S1527

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1528

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;1ba89dd2624d46408a812ffb9ee33c34&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;0e2df2168fa546d5b069a9af2710a8b3&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;25b329f2edd94909a07cc8206966b5dd&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0214, S0215

**PUBLICATION&#95;CORE&#95;REMAINS&#95;REVIEW** — Separate authorization permitted this local export while the unchanged core remained REVIEW&#46; Local output is not external publisher delivery or acceptance&#46;

Source: S0216, S0217

**SORTED&#95;SUMMARY&#95;NOT&#95;RECORD&#95;ASSOCIATION** — This concurrent case sorts aggregate state arrays&#46; Their positions are not record associations&#59; original record indices preserve each outcome and assessment pair&#46;

Source: S0218, S0219, S0220

### LP&#45;16 — Outside&#45;gate direct write demonstrates incomplete route control

Whole-case capture: S0232

Title source: S0233

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0224 |
| expected | &#123;&#34;all&#95;route&#95;prevention&#95;established&#34;&#58;false&#44;&#34;outside&#95;gate&#95;write&#95;observed&#34;&#58;true&#44;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S0225 |
| actual | &#123;&#34;all&#95;route&#95;prevention&#95;established&#34;&#58;false&#44;&#34;outside&#95;gate&#95;write&#95;observed&#34;&#58;true&#44;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S1529 |
| differences | &#123;&#125; | S1530 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| all&#95;route&#95;prevention&#95;established | false | S0231 |
| outside&#95;gate&#95;write&#95;observed | true | S1531 |
| publication&#95;attempts | 0 | S0228 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; | S1532 |
| unknown&#95;attempt&#95;observations | 0 | S1533 |
| visible&#95;bytes&#95;match&#95;candidate | true | S1534 |
| visible&#95;count | 1 | S0229 |
| sort&#95;states | false | S1535 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34; | S0226 |
| attempted | false | S1536 |
| reason | &#34;Separate explicit reviewer release authorization is required&#34; | S1537 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;168386Z&#34; | S1538 |
| publication | null | S0227 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1539 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1540 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;168386Z&#34; | S1541 |
| authorized&#95;local&#95;export | false | S1542 |
| reason | &#34;Separate explicit reviewer release authorization is required&#34; | S1543 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1544 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1545 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1546

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1547 |

###### Recorded core dimensions

All values in the following table come from S1548

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;NOT&#95;ESTABLISHED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1549

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;c68f575cc5f34d4ebf58ee85e20eba3d&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;f7d1aeb8e9244735abed65431818fdbb&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;required&#95;approval&#95;not&#95;established&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;94e2a31dcc7049ecb579c1010edf4cee&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1544

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0224, S0225

**PUBLICATION&#95;OUTSIDE&#95;GATE&#95;WRITE** — The gate blocked its publication path&#44; but a direct outside&#45;gate write produced a visible file&#46; Prevention across all routes is not established&#46;

Source: S0226, S0227, S0228, S0229, S0230, S0231

### LP&#45;17 — Structured disclosure omitting recorded assistance prevents output

Whole-case capture: S0237

Title source: S0238

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0235 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S0236 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;0&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;false&#44;&#34;visible&#95;count&#34;&#58;0&#125; | S1550 |
| differences | &#123;&#125; | S1551 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 0 | S1552 |
| states | &#91;&#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34;&#93; | S1553 |
| unknown&#95;attempt&#95;observations | 0 | S1554 |
| visible&#95;bytes&#95;match&#95;candidate | false | S1555 |
| visible&#95;count | 0 | S1556 |
| sort&#95;states | false | S1557 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#95;WITHOUT&#95;PUBLICATION&#34; | S1558 |
| attempted | false | S1559 |
| reason | &#34;Disclosure omits a recorded session activity&#34; | S1560 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;192552Z&#34; | S1561 |
| publication | null | S1562 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#93; | S1563 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1564 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;192552Z&#34; | S1565 |
| authorized&#95;local&#95;export | false | S1566 |
| reason | &#34;Disclosure omits a recorded session activity&#34; | S1567 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1568 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1569 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1570

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1568

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0235, S0236

### LP&#45;18 — Reusing a request ID for a newly approved different artifact conflicts

Whole-case capture: S0244

Title source: S0245

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0240 |
| expected | &#123;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#44;&#34;REQUEST&#95;ID&#95;CONFLICT&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S0241 |
| actual | &#123;&#34;publication&#95;attempts&#34;&#58;1&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#44;&#34;REQUEST&#95;ID&#95;CONFLICT&#34;&#93;&#44;&#34;unknown&#95;attempt&#95;observations&#34;&#58;0&#44;&#34;visible&#95;bytes&#95;match&#95;candidate&#34;&#58;true&#44;&#34;visible&#95;count&#34;&#58;1&#125; | S1571 |
| differences | &#123;&#125; | S1572 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| publication&#95;attempts | 1 | S1573 |
| states | &#91;&#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34;&#44;&#34;REQUEST&#95;ID&#95;CONFLICT&#34;&#93; | S1574 |
| unknown&#95;attempt&#95;observations | 0 | S1575 |
| visible&#95;bytes&#95;match&#95;candidate | true | S1576 |
| visible&#95;count | 1 | S1577 |
| sort&#95;states | false | S1578 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;OUTPUT&#95;CONFIRMED&#34; | S1579 |
| attempted | true | S1580 |
| reason | &#34;MEASURED&#95;LOCAL&#95;FILE&#95;CONFIRMED&#34; | S1581 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;230185Z&#34; | S1582 |
| publication&#46;journal&#95;state | &#34;local&#95;output&#95;confirmed&#34; | S1583 |
| publication&#46;visible&#95;name | &#34;9bff77d6e8a1fe343b7fa26a3a01aa1c3fada1362df048007c69e29917cde230&#46;html&#34; | S1584 |

##### disclosure — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1585 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1586 |

##### authorization&#95;preflight — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;211349Z&#34; | S1587 |
| authorized&#95;local&#95;export | true | S0242 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1588 |

##### authorization&#95;final&#95;gate — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;221391Z&#34; | S1589 |
| authorized&#95;local&#95;export | true | S1590 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1591 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;publication&#95;receipt&#34; | S1592 |
| request&#95;id | &#34;publication&#45;2f656418323a45ec95b5e4bf710f90fe&#34; | S1593 |
| fingerprint | &#34;57360e1ccd96e69173a2d36de022fae8c380b04cc202fa214647088cc2806fd8&#34; | S1594 |
| artifact&#95;sha256 | &#34;66c3dce462be32682b67aba66d9aa1a871266e3bd013193152dd93e913d47b9e&#34; | S1595 |
| disclosure&#95;sha256 | &#34;806e9855d8252a6930d98262c62dda3537d38d81932bacd1ecc6e959bae3a4b7&#34; | S1596 |
| byte&#95;length | 2856 | S1597 |
| destination&#95;id | &#34;synthetic&#45;venue&#34; | S1598 |
| visible&#95;name | &#34;9bff77d6e8a1fe343b7fa26a3a01aa1c3fada1362df048007c69e29917cde230&#46;html&#34; | S1599 |
| observed&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;228178Z&#34; | S1600 |

##### operation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;REQUEST&#95;ID&#95;CONFLICT&#34; | S1601 |
| attempted | false | S1602 |
| reason | &#34;REQUEST&#95;ID&#95;BINDS&#95;DIFFERENT&#95;ACTION&#34; | S1603 |
| post&#95;at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;241895Z&#34; | S1604 |
| publication&#46;journal&#95;state | &#34;local&#95;output&#95;confirmed&#34; | S1605 |
| publication&#46;visible&#95;name | &#34;9bff77d6e8a1fe343b7fa26a3a01aa1c3fada1362df048007c69e29917cde230&#46;html&#34; | S1606 |

##### disclosure — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| activities | &#91;&#34;generation&#34;&#93; | S1607 |
| scope | &#34;recorded&#95;local&#95;session&#95;only&#34; | S1608 |

##### authorization&#95;preflight — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| at | &#34;2026&#45;10&#45;30T02&#58;10&#58;06&#46;233239Z&#34; | S1609 |
| authorized&#95;local&#95;export | true | S1610 |
| reason | &#34;Explicit reviewer authorization for the exact local artifact&#59; core assessment remains REVIEW&#34; | S1611 |

##### authorization&#95;final&#95;gate — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| final&#95;gate | null | S1612 |

##### receipt — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1613 |

#### Core assessor frames

##### original record index 0 — phase preflight

Frame or nearest existing container: S1614

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1615 |

###### Recorded core dimensions

All values in the following table come from S1616

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1617

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;41ce995b462f42cb8bb9471cfa15e600&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;5606a3168ed2474ca93a6007bb1f8bda&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;5f2377b0d91f49a09a4867d5ec2c7361&#34;&#93;&#125; |

##### original record index 0 — phase final&#95;gate

Frame or nearest existing container: S1618

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1619 |

###### Recorded core dimensions

All values in the following table come from S1620

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1621

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;41ce995b462f42cb8bb9471cfa15e600&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;5606a3168ed2474ca93a6007bb1f8bda&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;5f2377b0d91f49a09a4867d5ec2c7361&#34;&#93;&#125; |

##### original record index 1 — phase preflight

Frame or nearest existing container: S1622

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1623 |

###### Recorded core dimensions

All values in the following table come from S1624

| Field | Recorded value |
| --- | --- |
| acceptance&#95;status | &#34;UNKNOWN&#34; |
| activity&#95;completeness | &#34;UNKNOWN&#34; |
| ai&#95;involvement | &#34;OBSERVED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| approval&#95;applicability | &#34;BOUND&#95;APPROVAL&#95;RECORDED&#34; |
| coverage | &#34;UNKNOWN&#34; |
| declarant&#95;attribution | &#34;NOT&#95;ESTABLISHED&#34; |
| delivery&#95;status | &#34;UNCONFIRMED&#34; |
| disclosure&#95;assessment | &#34;REQUIRES&#95;CONTENT&#95;REVIEW&#34; |
| disclosure&#95;preparation | &#34;RECORDED&#34; |
| dispatch&#95;observation | &#34;NOT&#95;ESTABLISHED&#34; |
| evidence&#95;basis | &#34;INSTRUMENTED&#95;OBSERVATION&#34; |
| evidence&#95;integrity | &#34;ESTABLISHED&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| evidence&#95;retention | &#34;PRESERVE&#95;PER&#95;STAGE&#95;POLICY&#95;AND&#95;REVISION&#95;BINDINGS&#34; |
| policy&#95;applicability | &#34;BOUND&#95;AND&#95;EFFECTIVE&#95;UNDER&#95;GIVEN&#95;ASSUMPTIONS&#34; |
| policy&#95;assessment | &#34;UNKNOWN&#34; |
| publication&#95;action | &#34;REVIEW&#34; |

###### Recorded core findings

All values in the following table come from S1625

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;publication&#95;activity&#95;bound&#95;to&#95;artifact&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;f31ebabd6fe944ccbe6f61efe73ff4f5&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;publication&#95;preparation&#95;is&#95;not&#95;delivery&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;19b9e37707394555a2e6455b50d87a7b&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;publication&#95;approval&#95;not&#95;publisher&#95;acceptance&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;record&#45;dc16f9f75de54b4c84c345cc6239c8f1&#34;&#93;&#125; |

##### original record index 1 — phase final&#95;gate

Frame or nearest existing container: S1612

| Field | Recorded value |
| --- | --- |
| Availability | &#34;FRAME&#95;NOT&#95;RECORDED&#34; |
| Absence reason | &#34;NULL&#95;CONTAINER&#34; |

No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0240, S0241

**PUBLICATION&#95;CORE&#95;REMAINS&#95;REVIEW** — Separate authorization permitted this local export while the unchanged core remained REVIEW&#46; Local output is not external publisher delivery or acceptance&#46;

Source: S0242, S0243

### LE&#45;01 — Exact authorized local namespace removal

Whole-case capture: S0249

Title source: S0250

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0247 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S0248 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S1626 |
| differences | &#123;&#125; | S1627 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93; | S1628 |
| local&#95;observations | &#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93; | S1629 |
| outside&#95;scope&#95;remains&#95;unknown | true | S1630 |
| rejected&#95;probes | 0 | S1631 |
| retained&#95;readable&#95;controls | &#91;&#93; | S1632 |
| states | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; | S1633 |
| unlink&#95;attempts | 1 | S1634 |
| sort&#95;states | false | S1635 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;506388Z&#34; | S1636 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S1637 |
| attempted | true | S1638 |
| reason | &#34;EXACT&#95;NAMESPACE&#95;ENTRY&#95;REMOVAL&#95;CONFIRMED&#34; | S1639 |
| journal&#95;state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S1640 |
| local&#95;observation | &#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34; | S1641 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;27a4cdd5cb2740508919aae3dffdd831&#34; | S1642 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;485135Z&#34; | S1643 |
| queue&#95;state | &#34;received&#34; | S1644 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;27a4cdd5cb2740508919aae3dffdd831&#34; | S1645 |
| completed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;488277Z&#34; | S1646 |
| locations | &#91;&#34;active&#45;object&#45;namespace&#34;&#93; | S1647 |
| exclusions | &#91;&#34;backups&#34;&#44;&#34;replicas&#34;&#44;&#34;downstream&#45;copies&#34;&#44;&#34;training&#45;derivatives&#34;&#44;&#34;open&#45;handles&#45;and&#45;memory&#34;&#44;&#34;storage&#45;media&#34;&#93; | S1648 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;unlink&#95;receipt&#34; | S1649 |
| task&#95;sha256 | &#34;da6c6c1a9660475d9f0c016db6756e9c5752675a5d8d7d13ccb945fcdd0f079e&#34; | S1650 |
| request&#95;id | &#34;request&#45;9d77c6d0959743f59babad323005bb2e&#34; | S1651 |
| manifest&#95;sha256 | &#34;ed4615a8b55a0c53aeeb49d6140d1a8f3e85a536f7f062b9742dbfb661c87367&#34; | S1652 |
| before | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#125; | S1653 |
| unlinked&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;486627Z&#34; | S1654 |
| observed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;488277Z&#34; | S1655 |
| after | &#34;ABSENT&#34; | S1656 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1657 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S1658 |
| location | &#34;active&#45;object&#45;namespace&#34; | S1659 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S1660 |
| version&#95;id | &#34;version&#45;761b938f9e9e4e09afcb9d9b0449140c&#34; | S1661 |
| phase | &#34;before&#34; | S1662 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;474782Z&#34; | S1663 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;474903Z&#34; | S1664 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S1665 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1666 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S1667 |
| location | &#34;active&#45;object&#45;namespace&#34; | S1668 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S1669 |
| version&#95;id | &#34;version&#45;761b938f9e9e4e09afcb9d9b0449140c&#34; | S1670 |
| phase | &#34;after&#34; | S1671 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;498383Z&#34; | S1672 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;498466Z&#34; | S1673 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S1674 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S1675 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S1676 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S1677 |
| replicas | &#34;UNKNOWN&#34; | S1678 |
| storage&#45;media | &#34;UNKNOWN&#34; | S1679 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S1680 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S1681

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1682 |

###### Recorded core dimensions

All values in the following table come from S1683

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S1684

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;27a4cdd5cb2740508919aae3dffdd831&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;da6c6c1a9660475d9f0c016db6756e9c5752675a5d8d7d13&#34;&#44;&#34;request&#45;record&#45;27a4cdd5cb2740508919aae3dffdd831&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;PROVIDER&#95;CLAIM&#95;REMAINS&#95;SCOPED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;completion&#45;da6c6c1a9660475d9f0c016db6756e9c5752675a5d8d7d13&#34;&#44;&#34;request&#45;record&#45;27a4cdd5cb2740508919aae3dffdd831&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0247, S0248

### LE&#45;02 — Acknowledgement without removal leaves the object present

Whole-case capture: S0254

Title source: S0255

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0252 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;ACKNOWLEDGED&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;ACKNOWLEDGED&#95;ONLY&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;0&#125; | S0253 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;ACKNOWLEDGED&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;ACKNOWLEDGED&#95;ONLY&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;0&#125; | S1685 |
| differences | &#123;&#125; | S1686 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;ACKNOWLEDGED&#34;&#93; | S1687 |
| local&#95;observations | &#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93; | S1688 |
| outside&#95;scope&#95;remains&#95;unknown | true | S1689 |
| rejected&#95;probes | 0 | S1690 |
| retained&#95;readable&#95;controls | &#91;&#93; | S1691 |
| states | &#91;&#34;ACKNOWLEDGED&#95;ONLY&#34;&#93; | S1692 |
| unlink&#95;attempts | 0 | S1693 |
| sort&#95;states | false | S1694 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;546737Z&#34; | S1695 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;ACKNOWLEDGED&#95;ONLY&#34; | S1696 |
| attempted | false | S1697 |
| reason | &#34;REQUEST&#95;RECEIVED&#95;WITHOUT&#95;DELETION&#34; | S1698 |
| journal&#95;state | &#34;ACKNOWLEDGED&#95;ONLY&#34; | S1699 |
| local&#95;observation | &#34;PRESENT&#95;AT&#95;OBSERVATION&#34; | S1700 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;8e96c46fc98249979c46a8d410a69317&#34; | S1701 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;532908Z&#34; | S1702 |
| queue&#95;state | &#34;received&#34; | S1703 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attestation | null | S1704 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1705 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1706 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S1707 |
| location | &#34;active&#45;object&#45;namespace&#34; | S1708 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S1709 |
| version&#95;id | &#34;version&#45;57b219430cd448b7a53634c604d3fda6&#34; | S1710 |
| phase | &#34;before&#34; | S1711 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;523251Z&#34; | S1712 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;523346Z&#34; | S1713 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S1714 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1715 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S1716 |
| location | &#34;active&#45;object&#45;namespace&#34; | S1717 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S1718 |
| version&#95;id | &#34;version&#45;57b219430cd448b7a53634c604d3fda6&#34; | S1719 |
| phase | &#34;after&#34; | S1720 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;541507Z&#34; | S1721 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;541603Z&#34; | S1722 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S1723 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S1724 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S1725 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S1726 |
| replicas | &#34;UNKNOWN&#34; | S1727 |
| storage&#45;media | &#34;UNKNOWN&#34; | S1728 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S1729 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S1730

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1731 |

###### Recorded core dimensions

All values in the following table come from S1732

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;ACKNOWLEDGED&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S1733

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;8e96c46fc98249979c46a8d410a69317&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;8f00f795e70e06cbcd5af0d81dbab590f5366c00ccf0ba55&#34;&#44;&#34;request&#45;record&#45;8e96c46fc98249979c46a8d410a69317&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0252, S0253

### LE&#45;03 — Request alone establishes no provider completion

Whole-case capture: S0259

Title source: S0260

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0257 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;NOT&#95;OBSERVED&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;NO&#95;PROVIDER&#95;CALL&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;0&#125; | S0258 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;NOT&#95;OBSERVED&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;NO&#95;PROVIDER&#95;CALL&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;0&#125; | S1734 |
| differences | &#123;&#125; | S1735 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;REQUEST&#95;ONLY&#34;&#93; | S1736 |
| local&#95;observations | &#91;&#34;NOT&#95;OBSERVED&#34;&#93; | S1737 |
| outside&#95;scope&#95;remains&#95;unknown | true | S1738 |
| rejected&#95;probes | 0 | S1739 |
| retained&#95;readable&#95;controls | &#91;&#93; | S1740 |
| states | &#91;&#34;NO&#95;PROVIDER&#95;CALL&#34;&#93; | S1741 |
| unlink&#95;attempts | 0 | S1742 |
| sort&#95;states | false | S1743 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;562790Z&#34; | S1744 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;result | null | S1745 |
| local&#95;observation | &#34;NOT&#95;OBSERVED&#34; | S1746 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| before | null | S1747 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| after | null | S1748 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S1749 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S1750 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S1751 |
| replicas | &#34;UNKNOWN&#34; | S1752 |
| storage&#45;media | &#34;UNKNOWN&#34; | S1753 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S1754 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S1755

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1756 |

###### Recorded core dimensions

All values in the following table come from S1757

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;REQUEST&#95;ONLY&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;NOT&#95;ESTABLISHED&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S1758

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;53a6f0c8b7764e0186fd9eaa3280abad&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0257, S0258

### LE&#45;04 — Tampered receipt signature is rejected after a measured operation

Whole-case capture: S0266

Title source: S0267

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0262 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;1&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S0263 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;1&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S1759 |
| differences | &#123;&#125; | S1760 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93; | S1761 |
| local&#95;observations | &#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93; | S1762 |
| outside&#95;scope&#95;remains&#95;unknown | true | S1763 |
| rejected&#95;probes | 1 | S1764 |
| retained&#95;readable&#95;controls | &#91;&#93; | S1765 |
| states | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; | S1766 |
| unlink&#95;attempts | 1 | S1767 |
| sort&#95;states | false | S1768 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;609119Z&#34; | S1769 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S0264 |
| attempted | true | S1770 |
| reason | &#34;EXACT&#95;NAMESPACE&#95;ENTRY&#95;REMOVAL&#95;CONFIRMED&#34; | S1771 |
| journal&#95;state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S1772 |
| local&#95;observation | &#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34; | S1773 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;a99a1b87e03e411fb39bf6a424d25e12&#34; | S1774 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;584613Z&#34; | S1775 |
| queue&#95;state | &#34;received&#34; | S1776 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;a99a1b87e03e411fb39bf6a424d25e12&#34; | S1777 |
| completed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;587856Z&#34; | S1778 |
| locations | &#91;&#34;active&#45;object&#45;namespace&#34;&#93; | S1779 |
| exclusions | &#91;&#34;backups&#34;&#44;&#34;replicas&#34;&#44;&#34;downstream&#45;copies&#34;&#44;&#34;training&#45;derivatives&#34;&#44;&#34;open&#45;handles&#45;and&#45;memory&#34;&#44;&#34;storage&#45;media&#34;&#93; | S1780 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;unlink&#95;receipt&#34; | S1781 |
| task&#95;sha256 | &#34;fd4a937be7aa1693e62928da6668c4e52533119008afff8a85ac1c8b05396c8a&#34; | S1782 |
| request&#95;id | &#34;request&#45;19b55858547047f38a416c2eeedc36c4&#34; | S1783 |
| manifest&#95;sha256 | &#34;23bcd735e080dcc651b63d4fc9a40ac0790dea32db0988531dab2e3c414095d3&#34; | S1784 |
| before | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#125; | S1785 |
| unlinked&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;586126Z&#34; | S1786 |
| observed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;587856Z&#34; | S1787 |
| after | &#34;ABSENT&#34; | S1788 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1789 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S1790 |
| location | &#34;active&#45;object&#45;namespace&#34; | S1791 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S1792 |
| version&#95;id | &#34;version&#45;d8110547f93343e0b5ee43a6ae17b69a&#34; | S1793 |
| phase | &#34;before&#34; | S1794 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;574981Z&#34; | S1795 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;575072Z&#34; | S1796 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S1797 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1798 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S1799 |
| location | &#34;active&#45;object&#45;namespace&#34; | S1800 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S1801 |
| version&#95;id | &#34;version&#45;d8110547f93343e0b5ee43a6ae17b69a&#34; | S1802 |
| phase | &#34;after&#34; | S1803 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;597486Z&#34; | S1804 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;597564Z&#34; | S1805 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S1806 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S1807 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S1808 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S1809 |
| replicas | &#34;UNKNOWN&#34; | S1810 |
| storage&#45;media | &#34;UNKNOWN&#34; | S1811 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S1812 |

##### probe — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| probes&#91;0&#93;&#46;outcome | &#34;REJECTED&#34; | S0265 |
| probes&#91;0&#93;&#46;expected&#95;task&#95;sha256 | &#34;fd4a937be7aa1693e62928da6668c4e52533119008afff8a85ac1c8b05396c8a&#34; | S1813 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S1814

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1815 |

###### Recorded core dimensions

All values in the following table come from S1816

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S1817

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;a99a1b87e03e411fb39bf6a424d25e12&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;fd4a937be7aa1693e62928da6668c4e52533119008afff8a&#34;&#44;&#34;request&#45;record&#45;a99a1b87e03e411fb39bf6a424d25e12&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;PROVIDER&#95;CLAIM&#95;REMAINS&#95;SCOPED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;completion&#45;fd4a937be7aa1693e62928da6668c4e52533119008afff8a&#34;&#44;&#34;request&#45;record&#45;a99a1b87e03e411fb39bf6a424d25e12&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0262, S0263

**ERASURE&#95;PROBE&#95;REJECTED&#95;AFTER&#95;OPERATION** — The original operation has a scoped completion record&#59; a separate altered&#45;evidence probe was rejected&#46; Probe rejection is not a blocked deletion operation&#46;

Source: S0264, S0265

### LE&#45;05 — Validly signed completion for another tenant is rejected

Whole-case capture: S0273

Title source: S0274

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0269 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;1&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S0270 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;1&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S1818 |
| differences | &#123;&#125; | S1819 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93; | S1820 |
| local&#95;observations | &#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93; | S1821 |
| outside&#95;scope&#95;remains&#95;unknown | true | S1822 |
| rejected&#95;probes | 1 | S1823 |
| retained&#95;readable&#95;controls | &#91;&#93; | S1824 |
| states | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; | S1825 |
| unlink&#95;attempts | 1 | S1826 |
| sort&#95;states | false | S1827 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;675644Z&#34; | S1828 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S0271 |
| attempted | true | S1829 |
| reason | &#34;EXACT&#95;NAMESPACE&#95;ENTRY&#95;REMOVAL&#95;CONFIRMED&#34; | S1830 |
| journal&#95;state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S1831 |
| local&#95;observation | &#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34; | S1832 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;80fb3acb618a4bc1bfffa0ed1c97c64e&#34; | S1833 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;645052Z&#34; | S1834 |
| queue&#95;state | &#34;received&#34; | S1835 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;80fb3acb618a4bc1bfffa0ed1c97c64e&#34; | S1836 |
| completed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;648216Z&#34; | S1837 |
| locations | &#91;&#34;active&#45;object&#45;namespace&#34;&#93; | S1838 |
| exclusions | &#91;&#34;backups&#34;&#44;&#34;replicas&#34;&#44;&#34;downstream&#45;copies&#34;&#44;&#34;training&#45;derivatives&#34;&#44;&#34;open&#45;handles&#45;and&#45;memory&#34;&#44;&#34;storage&#45;media&#34;&#93; | S1839 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;unlink&#95;receipt&#34; | S1840 |
| task&#95;sha256 | &#34;93ed56b411561549f96085714f93b8d8ca75fa38be889b916971117fbe504e51&#34; | S1841 |
| request&#95;id | &#34;request&#45;2b46aae6262e4d82991752b4f5807651&#34; | S1842 |
| manifest&#95;sha256 | &#34;b7aaac46fe385eb462efda6eddd01d291b0349cec196ba2a03a4b3133fc5dd2b&#34; | S1843 |
| before | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#125; | S1844 |
| unlinked&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;646557Z&#34; | S1845 |
| observed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;648216Z&#34; | S1846 |
| after | &#34;ABSENT&#34; | S1847 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1848 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S1849 |
| location | &#34;active&#45;object&#45;namespace&#34; | S1850 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S1851 |
| version&#95;id | &#34;version&#45;569de57364ff4178bac5e27c29d9beac&#34; | S1852 |
| phase | &#34;before&#34; | S1853 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;635398Z&#34; | S1854 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;635490Z&#34; | S1855 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S1856 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1857 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S1858 |
| location | &#34;active&#45;object&#45;namespace&#34; | S1859 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S1860 |
| version&#95;id | &#34;version&#45;569de57364ff4178bac5e27c29d9beac&#34; | S1861 |
| phase | &#34;after&#34; | S1862 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;657630Z&#34; | S1863 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;657706Z&#34; | S1864 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S1865 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S1866 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S1867 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S1868 |
| replicas | &#34;UNKNOWN&#34; | S1869 |
| storage&#45;media | &#34;UNKNOWN&#34; | S1870 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S1871 |

##### probe — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| probes&#91;0&#93;&#46;outcome | &#34;REJECTED&#34; | S0272 |
| probes&#91;0&#93;&#46;expected&#95;task&#95;sha256 | &#34;93ed56b411561549f96085714f93b8d8ca75fa38be889b916971117fbe504e51&#34; | S1872 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S1873

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1874 |

###### Recorded core dimensions

All values in the following table come from S1875

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S1876

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;80fb3acb618a4bc1bfffa0ed1c97c64e&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;93ed56b411561549f96085714f93b8d8ca75fa38be889b91&#34;&#44;&#34;request&#45;record&#45;80fb3acb618a4bc1bfffa0ed1c97c64e&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;PROVIDER&#95;CLAIM&#95;REMAINS&#95;SCOPED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;completion&#45;93ed56b411561549f96085714f93b8d8ca75fa38be889b91&#34;&#44;&#34;request&#45;record&#45;80fb3acb618a4bc1bfffa0ed1c97c64e&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0269, S0270

**ERASURE&#95;PROBE&#95;REJECTED&#95;AFTER&#95;OPERATION** — The original operation has a scoped completion record&#59; a separate altered&#45;evidence probe was rejected&#46; Probe rejection is not a blocked deletion operation&#46;

Source: S0271, S0272

### LE&#45;06 — Authorization expires after claim and before unlink

Whole-case capture: S0278

Title source: S0279

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0276 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;ACKNOWLEDGED&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;0&#125; | S0277 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;ACKNOWLEDGED&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;0&#125; | S1877 |
| differences | &#123;&#125; | S1878 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;ACKNOWLEDGED&#34;&#93; | S1879 |
| local&#95;observations | &#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93; | S1880 |
| outside&#95;scope&#95;remains&#95;unknown | true | S1881 |
| rejected&#95;probes | 0 | S1882 |
| retained&#95;readable&#95;controls | &#91;&#93; | S1883 |
| states | &#91;&#34;BLOCKED&#34;&#93; | S1884 |
| unlink&#95;attempts | 0 | S1885 |
| sort&#95;states | false | S1886 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;824669Z&#34; | S1887 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#34; | S1888 |
| attempted | false | S1889 |
| reason | &#34;FINAL&#95;AUTHORIZATION&#95;OR&#95;OBJECT&#95;NOT&#95;ESTABLISHED&#34; | S1890 |
| journal&#95;state | &#34;BLOCKED&#34; | S1891 |
| local&#95;observation | &#34;PRESENT&#95;AT&#95;OBSERVATION&#34; | S1892 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;f0daa4231c2644b399b05b42ebf6cb45&#34; | S1893 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;708900Z&#34; | S1894 |
| queue&#95;state | &#34;received&#34; | S1895 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attestation | null | S1896 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1897 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1898 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S1899 |
| location | &#34;active&#45;object&#45;namespace&#34; | S1900 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S1901 |
| version&#95;id | &#34;version&#45;deb04e1c73fa4b68a2eb807b7986207d&#34; | S1902 |
| phase | &#34;before&#34; | S1903 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;699437Z&#34; | S1904 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;02&#46;699528Z&#34; | S1905 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S1906 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1907 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S1908 |
| location | &#34;active&#45;object&#45;namespace&#34; | S1909 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S1910 |
| version&#95;id | &#34;version&#45;deb04e1c73fa4b68a2eb807b7986207d&#34; | S1911 |
| phase | &#34;after&#34; | S1912 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;819391Z&#34; | S1913 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;819495Z&#34; | S1914 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S1915 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S1916 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S1917 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S1918 |
| replicas | &#34;UNKNOWN&#34; | S1919 |
| storage&#45;media | &#34;UNKNOWN&#34; | S1920 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S1921 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S1922

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1923 |

###### Recorded core dimensions

All values in the following table come from S1924

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;ACKNOWLEDGED&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S1925

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;f0daa4231c2644b399b05b42ebf6cb45&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;dcf7994ab8694909d852ffb0f76d3ec31c1136c08e892404&#34;&#44;&#34;request&#45;record&#45;f0daa4231c2644b399b05b42ebf6cb45&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0276, S0277

### LE&#45;07 — Changed current content is not deleted

Whole-case capture: S0283

Title source: S0284

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0281 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;0&#125; | S0282 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;0&#125; | S1926 |
| differences | &#123;&#125; | S1927 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;REQUEST&#95;ONLY&#34;&#93; | S1928 |
| local&#95;observations | &#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93; | S1929 |
| outside&#95;scope&#95;remains&#95;unknown | true | S1930 |
| rejected&#95;probes | 0 | S1931 |
| retained&#95;readable&#95;controls | &#91;&#93; | S1932 |
| states | &#91;&#34;BLOCKED&#34;&#93; | S1933 |
| unlink&#95;attempts | 0 | S1934 |
| sort&#95;states | false | S1935 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;849497Z&#34; | S1936 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#34; | S1937 |
| attempted | false | S1938 |
| reason | &#34;REQUESTED&#95;OBJECT&#95;NOT&#95;PRESENT&#95;AS&#95;BOUND&#34; | S1939 |
| journal&#95;state | &#34;NOT&#95;CLAIMED&#34; | S1940 |
| local&#95;observation | &#34;PRESENT&#95;AT&#95;OBSERVATION&#34; | S1941 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| acknowledgement | null | S1942 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attestation | null | S1943 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1944 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1945 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S1946 |
| location | &#34;active&#45;object&#45;namespace&#34; | S1947 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S1948 |
| version&#95;id | &#34;version&#45;33f89fc0d03048c481bc08f5fd6bd940&#34; | S1949 |
| phase | &#34;before&#34; | S1950 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;839195Z&#34; | S1951 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;839289Z&#34; | S1952 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;48&#44;&#34;sha256&#34;&#58;&#34;17513c606b45413e1e1b349d04048e6bd2a00d4a1b4d45e62ccf716ea36974e6&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S1953 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1954 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S1955 |
| location | &#34;active&#45;object&#45;namespace&#34; | S1956 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S1957 |
| version&#95;id | &#34;version&#45;33f89fc0d03048c481bc08f5fd6bd940&#34; | S1958 |
| phase | &#34;after&#34; | S1959 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;845011Z&#34; | S1960 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;845126Z&#34; | S1961 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;48&#44;&#34;sha256&#34;&#58;&#34;17513c606b45413e1e1b349d04048e6bd2a00d4a1b4d45e62ccf716ea36974e6&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S1962 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S1963 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S1964 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S1965 |
| replicas | &#34;UNKNOWN&#34; | S1966 |
| storage&#45;media | &#34;UNKNOWN&#34; | S1967 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S1968 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S1969

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S1970 |

###### Recorded core dimensions

All values in the following table come from S1971

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;REQUEST&#95;ONLY&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;NOT&#95;ESTABLISHED&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S1972

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;96a9b1845c2f44e8b04a1bf351fff18f&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0281, S0282

### LE&#45;08 — Pre&#45;existing absence is not attributed to this deletion request

Whole-case capture: S0290

Title source: S0291

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0286 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;ABSENCE&#95;ONLY&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;0&#125; | S0287 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;ABSENCE&#95;ONLY&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;0&#125; | S1973 |
| differences | &#123;&#125; | S1974 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;REQUEST&#95;ONLY&#34;&#93; | S1975 |
| local&#95;observations | &#91;&#34;ABSENCE&#95;ONLY&#34;&#93; | S1976 |
| outside&#95;scope&#95;remains&#95;unknown | true | S1977 |
| rejected&#95;probes | 0 | S1978 |
| retained&#95;readable&#95;controls | &#91;&#93; | S1979 |
| states | &#91;&#34;BLOCKED&#34;&#93; | S1980 |
| unlink&#95;attempts | 0 | S1981 |
| sort&#95;states | false | S1982 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;872778Z&#34; | S1983 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#34; | S1984 |
| attempted | false | S0288 |
| reason | &#34;REQUESTED&#95;OBJECT&#95;NOT&#95;PRESENT&#95;AS&#95;BOUND&#34; | S1985 |
| journal&#95;state | &#34;NOT&#95;CLAIMED&#34; | S1986 |
| local&#95;observation | &#34;ABSENCE&#95;ONLY&#34; | S0289 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| acknowledgement | null | S1987 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attestation | null | S1988 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S1989 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1990 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S1991 |
| location | &#34;active&#45;object&#45;namespace&#34; | S1992 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S1993 |
| version&#95;id | &#34;version&#45;90c9cbb4d2f4452a9337f374c07eeccd&#34; | S1994 |
| phase | &#34;before&#34; | S1995 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;862427Z&#34; | S1996 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;862501Z&#34; | S1997 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S1998 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S1999 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2000 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2001 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2002 |
| version&#95;id | &#34;version&#45;90c9cbb4d2f4452a9337f374c07eeccd&#34; | S2003 |
| phase | &#34;after&#34; | S2004 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;868323Z&#34; | S2005 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;868401Z&#34; | S2006 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S2007 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2008 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2009 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2010 |
| replicas | &#34;UNKNOWN&#34; | S2011 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2012 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2013 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S2014

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2015 |

###### Recorded core dimensions

All values in the following table come from S2016

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;REQUEST&#95;ONLY&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;NOT&#95;ESTABLISHED&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2017

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;fdced3c3692a401b80bd918eb0ded519&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0286, S0287

**ERASURE&#95;PREEXISTING&#95;ABSENCE** — The entry was already absent and no unlink was attempted&#46; ABSENCE&#95;ONLY does not attribute a deletion operation to this request&#46;

Source: S0288, S0289

### LE&#45;09 — Repeated request performs no second unlink

Whole-case capture: S0295

Title source: S0296

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0293 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#44;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#44;&#34;ABSENCE&#95;ONLY&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;ACTION&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S0294 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#44;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#44;&#34;ABSENCE&#95;ONLY&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;ACTION&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S2018 |
| differences | &#123;&#125; | S2019 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#44;&#34;REQUEST&#95;ONLY&#34;&#93; | S2020 |
| local&#95;observations | &#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#44;&#34;ABSENCE&#95;ONLY&#34;&#93; | S2021 |
| outside&#95;scope&#95;remains&#95;unknown | true | S2022 |
| rejected&#95;probes | 0 | S2023 |
| retained&#95;readable&#95;controls | &#91;&#93; | S2024 |
| states | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;ACTION&#34;&#93; | S2025 |
| unlink&#95;attempts | 1 | S2026 |
| sort&#95;states | false | S2027 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;935406Z&#34; | S2028 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2029 |
| attempted | true | S2030 |
| reason | &#34;EXACT&#95;NAMESPACE&#95;ENTRY&#95;REMOVAL&#95;CONFIRMED&#34; | S2031 |
| journal&#95;state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2032 |
| local&#95;observation | &#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34; | S2033 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;83b85383f43f40529a8858d619bbed65&#34; | S2034 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;901218Z&#34; | S2035 |
| queue&#95;state | &#34;received&#34; | S2036 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;83b85383f43f40529a8858d619bbed65&#34; | S2037 |
| completed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;904517Z&#34; | S2038 |
| locations | &#91;&#34;active&#45;object&#45;namespace&#34;&#93; | S2039 |
| exclusions | &#91;&#34;backups&#34;&#44;&#34;replicas&#34;&#44;&#34;downstream&#45;copies&#34;&#44;&#34;training&#45;derivatives&#34;&#44;&#34;open&#45;handles&#45;and&#45;memory&#34;&#44;&#34;storage&#45;media&#34;&#93; | S2040 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;unlink&#95;receipt&#34; | S2041 |
| task&#95;sha256 | &#34;d261cf27dc6f240e905c3b69cb94c5dafc15db8b0005037c11dfb8b2f147a970&#34; | S2042 |
| request&#95;id | &#34;request&#45;34c06f06725d4b799071695ceeb90259&#34; | S2043 |
| manifest&#95;sha256 | &#34;6c818b890155e7efdcbde7d7b433fa4086a23c245087d715c6646fad7c08ae0b&#34; | S2044 |
| before | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#125; | S2045 |
| unlinked&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;902737Z&#34; | S2046 |
| observed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;904517Z&#34; | S2047 |
| after | &#34;ABSENT&#34; | S2048 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2049 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2050 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2051 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2052 |
| version&#95;id | &#34;version&#45;5c3ce7b7f37a4615ae8d2168f50264f6&#34; | S2053 |
| phase | &#34;before&#34; | S2054 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;885625Z&#34; | S2055 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;885715Z&#34; | S2056 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S2057 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2058 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2059 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2060 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2061 |
| version&#95;id | &#34;version&#45;5c3ce7b7f37a4615ae8d2168f50264f6&#34; | S2062 |
| phase | &#34;after&#34; | S2063 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;914494Z&#34; | S2064 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;914571Z&#34; | S2065 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S2066 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2067 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2068 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2069 |
| replicas | &#34;UNKNOWN&#34; | S2070 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2071 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2072 |

##### operation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;REPLAY&#95;NO&#95;ACTION&#34; | S2073 |
| attempted | false | S2074 |
| reason | &#34;REQUEST&#95;ALREADY&#95;CLAIMED&#95;NO&#95;EVIDENCE&#95;REASSERTED&#34; | S2075 |
| journal&#95;state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2076 |
| local&#95;observation | &#34;ABSENCE&#95;ONLY&#34; | S2077 |

##### acknowledgement — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| acknowledgement | null | S2078 |

##### attestation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| attestation | null | S2079 |

##### receipt — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S2080 |

##### namespace&#95;before — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2081 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2082 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2083 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2084 |
| version&#95;id | &#34;version&#45;5c3ce7b7f37a4615ae8d2168f50264f6&#34; | S2085 |
| phase | &#34;before&#34; | S2086 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;923864Z&#34; | S2087 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;923937Z&#34; | S2088 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S2089 |

##### namespace&#95;after — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2090 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2091 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2092 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2093 |
| version&#95;id | &#34;version&#45;5c3ce7b7f37a4615ae8d2168f50264f6&#34; | S2094 |
| phase | &#34;after&#34; | S2095 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;930822Z&#34; | S2096 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;930898Z&#34; | S2097 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S2098 |

##### unknown&#95;domains — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2099 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2100 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2101 |
| replicas | &#34;UNKNOWN&#34; | S2102 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2103 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2104 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S2105

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2106 |

###### Recorded core dimensions

All values in the following table come from S2107

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2108

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;83b85383f43f40529a8858d619bbed65&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;d261cf27dc6f240e905c3b69cb94c5dafc15db8b0005037c&#34;&#44;&#34;request&#45;record&#45;83b85383f43f40529a8858d619bbed65&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;PROVIDER&#95;CLAIM&#95;REMAINS&#95;SCOPED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;completion&#45;d261cf27dc6f240e905c3b69cb94c5dafc15db8b0005037c&#34;&#44;&#34;request&#45;record&#45;83b85383f43f40529a8858d619bbed65&#34;&#93;&#125; |

##### original record index 1 — phase erasure

Frame or nearest existing container: S2109

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2110 |

###### Recorded core dimensions

All values in the following table come from S2111

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;REQUEST&#95;ONLY&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;NOT&#95;ESTABLISHED&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2112

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;83b85383f43f40529a8858d619bbed65&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0293, S0294

### LE&#45;10 — Lost terminal persistence acknowledgement remains unknown and cannot retry

Whole-case capture: S0304

Title source: S0305

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0298 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;ACKNOWLEDGED&#34;&#44;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;ABSENCE&#95;ONLY&#34;&#44;&#34;ABSENCE&#95;ONLY&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#44;&#34;REPLAY&#95;NO&#95;ACTION&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S0299 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;ACKNOWLEDGED&#34;&#44;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;ABSENCE&#95;ONLY&#34;&#44;&#34;ABSENCE&#95;ONLY&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#44;&#34;REPLAY&#95;NO&#95;ACTION&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S2113 |
| differences | &#123;&#125; | S2114 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;ACKNOWLEDGED&#34;&#44;&#34;REQUEST&#95;ONLY&#34;&#93; | S2115 |
| local&#95;observations | &#91;&#34;ABSENCE&#95;ONLY&#34;&#44;&#34;ABSENCE&#95;ONLY&#34;&#93; | S2116 |
| outside&#95;scope&#95;remains&#95;unknown | true | S2117 |
| rejected&#95;probes | 0 | S2118 |
| retained&#95;readable&#95;controls | &#91;&#93; | S2119 |
| states | &#91;&#34;OUTCOME&#95;UNKNOWN&#34;&#44;&#34;REPLAY&#95;NO&#95;ACTION&#34;&#93; | S2120 |
| unlink&#95;attempts | 1 | S2121 |
| sort&#95;states | false | S2122 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;992883Z&#34; | S2123 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;OUTCOME&#95;UNKNOWN&#34; | S0300 |
| attempted | true | S2124 |
| reason | &#34;RESULT&#95;PERSISTENCE&#95;NOT&#95;ESTABLISHED&#34; | S2125 |
| journal&#95;state | &#34;deletion&#95;intent&#34; | S2126 |
| local&#95;observation | &#34;ABSENCE&#95;ONLY&#34; | S0302 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;ac90bc531e054c05a4b42f397c891784&#34; | S2127 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;967272Z&#34; | S2128 |
| queue&#95;state | &#34;received&#34; | S2129 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attestation | null | S2130 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S0301 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2131 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2132 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2133 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2134 |
| version&#95;id | &#34;version&#45;c7703d4e539446d7a7e120f3c3b25319&#34; | S2135 |
| phase | &#34;before&#34; | S2136 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;957316Z&#34; | S2137 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;957407Z&#34; | S2138 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S2139 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2140 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2141 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2142 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2143 |
| version&#95;id | &#34;version&#45;c7703d4e539446d7a7e120f3c3b25319&#34; | S2144 |
| phase | &#34;after&#34; | S2145 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;974650Z&#34; | S2146 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;974726Z&#34; | S2147 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S2148 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2149 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2150 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2151 |
| replicas | &#34;UNKNOWN&#34; | S2152 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2153 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2154 |

##### operation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;REPLAY&#95;NO&#95;ACTION&#34; | S0303 |
| attempted | false | S2155 |
| reason | &#34;REQUEST&#95;ALREADY&#95;CLAIMED&#95;NO&#95;EVIDENCE&#95;REASSERTED&#34; | S2156 |
| journal&#95;state | &#34;deletion&#95;intent&#34; | S2157 |
| local&#95;observation | &#34;ABSENCE&#95;ONLY&#34; | S2158 |

##### acknowledgement — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| acknowledgement | null | S2159 |

##### attestation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| attestation | null | S2160 |

##### receipt — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S2161 |

##### namespace&#95;before — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2162 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2163 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2164 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2165 |
| version&#95;id | &#34;version&#45;c7703d4e539446d7a7e120f3c3b25319&#34; | S2166 |
| phase | &#34;before&#34; | S2167 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;981424Z&#34; | S2168 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;981498Z&#34; | S2169 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S2170 |

##### namespace&#95;after — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2171 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2172 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2173 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2174 |
| version&#95;id | &#34;version&#45;c7703d4e539446d7a7e120f3c3b25319&#34; | S2175 |
| phase | &#34;after&#34; | S2176 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;988165Z&#34; | S2177 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;04&#46;988243Z&#34; | S2178 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S2179 |

##### unknown&#95;domains — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2180 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2181 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2182 |
| replicas | &#34;UNKNOWN&#34; | S2183 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2184 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2185 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S2186

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2187 |

###### Recorded core dimensions

All values in the following table come from S2188

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;ACKNOWLEDGED&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2189

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;ac90bc531e054c05a4b42f397c891784&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;c51f7abd4fb5e2a7689d2fd493aaa6359259eefecd3c6c52&#34;&#44;&#34;request&#45;record&#45;ac90bc531e054c05a4b42f397c891784&#34;&#93;&#125; |

##### original record index 1 — phase erasure

Frame or nearest existing container: S2190

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2191 |

###### Recorded core dimensions

All values in the following table come from S2192

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;REQUEST&#95;ONLY&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;NOT&#95;ESTABLISHED&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2193

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;ac90bc531e054c05a4b42f397c891784&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0298, S0299

**ERASURE&#95;UNKNOWN&#95;WITH&#95;ABSENCE** — Observed absence coexists with unknown completion and a replay that issued no new completion&#46; Do not promote absence into a confirmed deletion result&#46;

Source: S0300, S0301, S0302, S0303

### LE&#45;11 — Concurrent identical requests enter at most one unlink

Whole-case capture: S0312

Title source: S0313

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0307 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#44;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;ABSENCE&#95;ONLY&#34;&#44;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;ACTION&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S0308 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#44;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;ABSENCE&#95;ONLY&#34;&#44;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;ACTION&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S2194 |
| differences | &#123;&#125; | S2195 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#44;&#34;REQUEST&#95;ONLY&#34;&#93; | S2196 |
| local&#95;observations | &#91;&#34;ABSENCE&#95;ONLY&#34;&#44;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93; | S2197 |
| outside&#95;scope&#95;remains&#95;unknown | true | S2198 |
| rejected&#95;probes | 0 | S2199 |
| retained&#95;readable&#95;controls | &#91;&#93; | S2200 |
| states | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#44;&#34;REPLAY&#95;NO&#95;ACTION&#34;&#93; | S2201 |
| unlink&#95;attempts | 1 | S2202 |
| sort&#95;states | true | S0309 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;060695Z&#34; | S2203 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2204 |
| attempted | true | S2205 |
| reason | &#34;EXACT&#95;NAMESPACE&#95;ENTRY&#95;REMOVAL&#95;CONFIRMED&#34; | S2206 |
| journal&#95;state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2207 |
| local&#95;observation | &#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34; | S2208 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;0d3a9c76971f484c9593fe5e3b771139&#34; | S2209 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;032001Z&#34; | S2210 |
| queue&#95;state | &#34;received&#34; | S2211 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;0d3a9c76971f484c9593fe5e3b771139&#34; | S2212 |
| completed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;036676Z&#34; | S2213 |
| locations | &#91;&#34;active&#45;object&#45;namespace&#34;&#93; | S2214 |
| exclusions | &#91;&#34;backups&#34;&#44;&#34;replicas&#34;&#44;&#34;downstream&#45;copies&#34;&#44;&#34;training&#45;derivatives&#34;&#44;&#34;open&#45;handles&#45;and&#45;memory&#34;&#44;&#34;storage&#45;media&#34;&#93; | S2215 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;unlink&#95;receipt&#34; | S2216 |
| task&#95;sha256 | &#34;3f518fef3aec176050c3506a59c37ede58a685295e55a085d23bc796ad2fdaf8&#34; | S2217 |
| request&#95;id | &#34;request&#45;f010040cfe8948e09047b9accc4a2fbb&#34; | S2218 |
| manifest&#95;sha256 | &#34;ce1dde3f9301ae558f548b97b2a53975612b9a176b150f6f6208e54d34609588&#34; | S2219 |
| before | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#125; | S2220 |
| unlinked&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;034903Z&#34; | S2221 |
| observed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;036676Z&#34; | S2222 |
| after | &#34;ABSENT&#34; | S2223 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2224 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2225 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2226 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2227 |
| version&#95;id | &#34;version&#45;194410e74ba643beafb53ba330b88655&#34; | S2228 |
| phase | &#34;before&#34; | S2229 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;015480Z&#34; | S2230 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;015573Z&#34; | S2231 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S2232 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2233 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2234 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2235 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2236 |
| version&#95;id | &#34;version&#45;194410e74ba643beafb53ba330b88655&#34; | S2237 |
| phase | &#34;after&#34; | S2238 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;046478Z&#34; | S2239 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;046558Z&#34; | S2240 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S2241 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2242 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2243 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2244 |
| replicas | &#34;UNKNOWN&#34; | S2245 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2246 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2247 |

##### operation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;REPLAY&#95;NO&#95;ACTION&#34; | S2248 |
| attempted | false | S2249 |
| reason | &#34;REQUEST&#95;ALREADY&#95;CLAIMED&#95;NO&#95;EVIDENCE&#95;REASSERTED&#34; | S2250 |
| journal&#95;state | &#34;deletion&#95;intent&#34; | S2251 |
| local&#95;observation | &#34;ABSENCE&#95;ONLY&#34; | S2252 |

##### acknowledgement — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| acknowledgement | null | S2253 |

##### attestation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| attestation | null | S2254 |

##### receipt — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S2255 |

##### namespace&#95;before — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2256 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2257 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2258 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2259 |
| version&#95;id | &#34;version&#45;194410e74ba643beafb53ba330b88655&#34; | S2260 |
| phase | &#34;before&#34; | S2261 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;017338Z&#34; | S2262 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;017425Z&#34; | S2263 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S2264 |

##### namespace&#95;after — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2265 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2266 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2267 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2268 |
| version&#95;id | &#34;version&#45;194410e74ba643beafb53ba330b88655&#34; | S2269 |
| phase | &#34;after&#34; | S2270 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;056221Z&#34; | S2271 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;056304Z&#34; | S2272 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S2273 |

##### unknown&#95;domains — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2274 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2275 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2276 |
| replicas | &#34;UNKNOWN&#34; | S2277 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2278 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2279 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S2280

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2281 |

###### Recorded core dimensions

All values in the following table come from S2282

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2283

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;0d3a9c76971f484c9593fe5e3b771139&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;3f518fef3aec176050c3506a59c37ede58a685295e55a085&#34;&#44;&#34;request&#45;record&#45;0d3a9c76971f484c9593fe5e3b771139&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;PROVIDER&#95;CLAIM&#95;REMAINS&#95;SCOPED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;completion&#45;3f518fef3aec176050c3506a59c37ede58a685295e55a085&#34;&#44;&#34;request&#45;record&#45;0d3a9c76971f484c9593fe5e3b771139&#34;&#93;&#125; |

##### original record index 1 — phase erasure

Frame or nearest existing container: S2284

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2285 |

###### Recorded core dimensions

All values in the following table come from S2286

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;REQUEST&#95;ONLY&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;NOT&#95;ESTABLISHED&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2287

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;0d3a9c76971f484c9593fe5e3b771139&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0307, S0308

**SORTED&#95;SUMMARY&#95;NOT&#95;RECORD&#95;ASSOCIATION** — This concurrent case sorts aggregate state arrays&#46; Their positions are not record associations&#59; original record indices preserve each outcome and assessment pair&#46;

Source: S0309, S0310, S0311

### LE&#45;12 — Explicitly excluded copy stays readable after scoped removal

Whole-case capture: S0323

Title source: S0324

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0315 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#34;excluded&#45;copy&#34;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S0316 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#34;excluded&#45;copy&#34;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S2288 |
| differences | &#123;&#125; | S2289 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93; | S2290 |
| local&#95;observations | &#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93; | S2291 |
| outside&#95;scope&#95;remains&#95;unknown | true | S2292 |
| rejected&#95;probes | 0 | S2293 |
| retained&#95;readable&#95;controls | &#91;&#34;excluded&#45;copy&#34;&#93; | S2294 |
| states | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; | S2295 |
| unlink&#95;attempts | 1 | S2296 |
| sort&#95;states | false | S2297 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;114660Z&#34; | S2298 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S0317 |
| attempted | true | S2299 |
| reason | &#34;EXACT&#95;NAMESPACE&#95;ENTRY&#95;REMOVAL&#95;CONFIRMED&#34; | S2300 |
| journal&#95;state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2301 |
| local&#95;observation | &#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34; | S0318 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;7dfea6f153dd42ca88c540a55de2b6d5&#34; | S2302 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;093341Z&#34; | S2303 |
| queue&#95;state | &#34;received&#34; | S2304 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;7dfea6f153dd42ca88c540a55de2b6d5&#34; | S2305 |
| completed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;096509Z&#34; | S2306 |
| locations | &#91;&#34;active&#45;object&#45;namespace&#34;&#93; | S2307 |
| exclusions | &#91;&#34;backups&#34;&#44;&#34;replicas&#34;&#44;&#34;downstream&#45;copies&#34;&#44;&#34;training&#45;derivatives&#34;&#44;&#34;open&#45;handles&#45;and&#45;memory&#34;&#44;&#34;storage&#45;media&#34;&#93; | S2308 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;unlink&#95;receipt&#34; | S2309 |
| task&#95;sha256 | &#34;f5abbd2e78f21808b00226e9653a1cb3f2bf836984004fcacf9518d50a5a1a1b&#34; | S2310 |
| request&#95;id | &#34;request&#45;4b2b3cde69044b47a08878f11d9f43b5&#34; | S2311 |
| manifest&#95;sha256 | &#34;8398e937f305504e824f92870a70779b9e0ebaf85196ce31ad97322562cd3b81&#34; | S2312 |
| before | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#125; | S2313 |
| unlinked&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;094816Z&#34; | S2314 |
| observed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;096509Z&#34; | S2315 |
| after | &#34;ABSENT&#34; | S2316 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2317 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2318 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2319 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2320 |
| version&#95;id | &#34;version&#45;2df38b32f6c644e69717472246f20ac8&#34; | S2321 |
| phase | &#34;before&#34; | S2322 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;083305Z&#34; | S2323 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;083397Z&#34; | S2324 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S2325 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2326 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2327 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2328 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2329 |
| version&#95;id | &#34;version&#45;2df38b32f6c644e69717472246f20ac8&#34; | S2330 |
| phase | &#34;after&#34; | S2331 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;106487Z&#34; | S2332 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;106564Z&#34; | S2333 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S2334 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2335 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2336 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2337 |
| replicas | &#34;UNKNOWN&#34; | S2338 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2339 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2340 |

##### retained&#95;control — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| retained&#95;controls&#91;0&#93;&#46;kind | &#34;retained&#95;read&#95;observation&#34; | S2341 |
| retained&#95;controls&#91;0&#93;&#46;task&#95;sha256 | &#34;f5abbd2e78f21808b00226e9653a1cb3f2bf836984004fcacf9518d50a5a1a1b&#34; | S2342 |
| retained&#95;controls&#91;0&#93;&#46;manifest&#95;sha256 | &#34;8398e937f305504e824f92870a70779b9e0ebaf85196ce31ad97322562cd3b81&#34; | S2343 |
| retained&#95;controls&#91;0&#93;&#46;mechanism | &#34;excluded&#45;copy&#34; | S0319 |
| retained&#95;controls&#91;0&#93;&#46;state | &#34;READABLE&#34; | S0320 |
| retained&#95;controls&#91;0&#93;&#46;sha256 | &#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34; | S2344 |
| retained&#95;controls&#91;0&#93;&#46;byte&#95;length | 68 | S2345 |
| retained&#95;controls&#91;0&#93;&#46;observed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;114517Z&#34; | S0321 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S2346

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2347 |

###### Recorded core dimensions

All values in the following table come from S2348

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2349

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;7dfea6f153dd42ca88c540a55de2b6d5&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;f5abbd2e78f21808b00226e9653a1cb3f2bf836984004fca&#34;&#44;&#34;request&#45;record&#45;7dfea6f153dd42ca88c540a55de2b6d5&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;PROVIDER&#95;CLAIM&#95;REMAINS&#95;SCOPED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;completion&#45;f5abbd2e78f21808b00226e9653a1cb3f2bf836984004fca&#34;&#44;&#34;request&#45;record&#45;7dfea6f153dd42ca88c540a55de2b6d5&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0315, S0316

**ERASURE&#95;READABLE&#95;RETAINED&#95;DATA** — A specific retained copy or open handle remained READABLE after scoped namespace removal&#46; This is not complete erasure&#44; and broader excluded&#45;domain outcomes remain UNKNOWN&#46;

Source: S0317, S0318, S0319, S0320, S0321, S0322

### LE&#45;13 — Previously opened file stays readable after namespace removal

Whole-case capture: S0334

Title source: S0335

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0326 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#34;open&#45;handle&#34;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S0327 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#34;open&#45;handle&#34;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S2350 |
| differences | &#123;&#125; | S2351 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93; | S2352 |
| local&#95;observations | &#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#93; | S2353 |
| outside&#95;scope&#95;remains&#95;unknown | true | S2354 |
| rejected&#95;probes | 0 | S2355 |
| retained&#95;readable&#95;controls | &#91;&#34;open&#45;handle&#34;&#93; | S2356 |
| states | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; | S2357 |
| unlink&#95;attempts | 1 | S2358 |
| sort&#95;states | false | S2359 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;162413Z&#34; | S2360 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S0328 |
| attempted | true | S2361 |
| reason | &#34;EXACT&#95;NAMESPACE&#95;ENTRY&#95;REMOVAL&#95;CONFIRMED&#34; | S2362 |
| journal&#95;state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2363 |
| local&#95;observation | &#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34; | S0329 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;c513d496e4e5427b8c7f962a38d963d2&#34; | S2364 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;141551Z&#34; | S2365 |
| queue&#95;state | &#34;received&#34; | S2366 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;c513d496e4e5427b8c7f962a38d963d2&#34; | S2367 |
| completed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;144668Z&#34; | S2368 |
| locations | &#91;&#34;active&#45;object&#45;namespace&#34;&#93; | S2369 |
| exclusions | &#91;&#34;backups&#34;&#44;&#34;replicas&#34;&#44;&#34;downstream&#45;copies&#34;&#44;&#34;training&#45;derivatives&#34;&#44;&#34;open&#45;handles&#45;and&#45;memory&#34;&#44;&#34;storage&#45;media&#34;&#93; | S2370 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;unlink&#95;receipt&#34; | S2371 |
| task&#95;sha256 | &#34;7290fd909d447f6e6bdb7abb4b669e341e218d031630047e7de3a4bfaef44094&#34; | S2372 |
| request&#95;id | &#34;request&#45;48c611890b7145dba461a5ea365a980d&#34; | S2373 |
| manifest&#95;sha256 | &#34;9f19fcf09699d1ad6c559876ba3d1d123dcba2b67223708265de5e8a749d582a&#34; | S2374 |
| before | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#125; | S2375 |
| unlinked&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;143028Z&#34; | S2376 |
| observed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;144668Z&#34; | S2377 |
| after | &#34;ABSENT&#34; | S2378 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2379 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2380 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2381 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2382 |
| version&#95;id | &#34;version&#45;ac87afd8a18a48ec8b588e57076a7c0a&#34; | S2383 |
| phase | &#34;before&#34; | S2384 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;132035Z&#34; | S2385 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;132148Z&#34; | S2386 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S2387 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2388 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2389 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2390 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2391 |
| version&#95;id | &#34;version&#45;ac87afd8a18a48ec8b588e57076a7c0a&#34; | S2392 |
| phase | &#34;after&#34; | S2393 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;154215Z&#34; | S2394 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;154293Z&#34; | S2395 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S2396 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2397 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2398 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2399 |
| replicas | &#34;UNKNOWN&#34; | S2400 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2401 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2402 |

##### retained&#95;control — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| retained&#95;controls&#91;0&#93;&#46;kind | &#34;retained&#95;read&#95;observation&#34; | S2403 |
| retained&#95;controls&#91;0&#93;&#46;task&#95;sha256 | &#34;7290fd909d447f6e6bdb7abb4b669e341e218d031630047e7de3a4bfaef44094&#34; | S2404 |
| retained&#95;controls&#91;0&#93;&#46;manifest&#95;sha256 | &#34;9f19fcf09699d1ad6c559876ba3d1d123dcba2b67223708265de5e8a749d582a&#34; | S2405 |
| retained&#95;controls&#91;0&#93;&#46;mechanism | &#34;open&#45;handle&#34; | S0330 |
| retained&#95;controls&#91;0&#93;&#46;state | &#34;READABLE&#34; | S0331 |
| retained&#95;controls&#91;0&#93;&#46;sha256 | &#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34; | S2406 |
| retained&#95;controls&#91;0&#93;&#46;byte&#95;length | 68 | S2407 |
| retained&#95;controls&#91;0&#93;&#46;observed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;162159Z&#34; | S0332 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S2408

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2409 |

###### Recorded core dimensions

All values in the following table come from S2410

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2411

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;c513d496e4e5427b8c7f962a38d963d2&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;7290fd909d447f6e6bdb7abb4b669e341e218d031630047e&#34;&#44;&#34;request&#45;record&#45;c513d496e4e5427b8c7f962a38d963d2&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;PROVIDER&#95;CLAIM&#95;REMAINS&#95;SCOPED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;completion&#45;7290fd909d447f6e6bdb7abb4b669e341e218d031630047e&#34;&#44;&#34;request&#45;record&#45;c513d496e4e5427b8c7f962a38d963d2&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0326, S0327

**ERASURE&#95;READABLE&#95;RETAINED&#95;DATA** — A specific retained copy or open handle remained READABLE after scoped namespace removal&#46; This is not complete erasure&#44; and broader excluded&#45;domain outcomes remain UNKNOWN&#46;

Source: S0328, S0329, S0330, S0331, S0332, S0333

### LE&#45;14 — After&#45;only absence does not prove an observed transition

Whole-case capture: S0343

Title source: S0344

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0337 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;ABSENCE&#95;ONLY&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S0338 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;ABSENCE&#95;ONLY&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S2412 |
| differences | &#123;&#125; | S2413 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93; | S2414 |
| local&#95;observations | &#91;&#34;ABSENCE&#95;ONLY&#34;&#93; | S2415 |
| outside&#95;scope&#95;remains&#95;unknown | true | S2416 |
| rejected&#95;probes | 0 | S2417 |
| retained&#95;readable&#95;controls | &#91;&#93; | S2418 |
| states | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; | S2419 |
| unlink&#95;attempts | 1 | S2420 |
| sort&#95;states | false | S2421 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;207919Z&#34; | S2422 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S0342 |
| attempted | true | S2423 |
| reason | &#34;EXACT&#95;NAMESPACE&#95;ENTRY&#95;REMOVAL&#95;CONFIRMED&#34; | S2424 |
| journal&#95;state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2425 |
| local&#95;observation | &#34;ABSENCE&#95;ONLY&#34; | S0341 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;d38255426a174d469a2e3ddf37d827cc&#34; | S2426 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;187868Z&#34; | S2427 |
| queue&#95;state | &#34;received&#34; | S2428 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;d38255426a174d469a2e3ddf37d827cc&#34; | S2429 |
| completed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;191190Z&#34; | S2430 |
| locations | &#91;&#34;active&#45;object&#45;namespace&#34;&#93; | S2431 |
| exclusions | &#91;&#34;backups&#34;&#44;&#34;replicas&#34;&#44;&#34;downstream&#45;copies&#34;&#44;&#34;training&#45;derivatives&#34;&#44;&#34;open&#45;handles&#45;and&#45;memory&#34;&#44;&#34;storage&#45;media&#34;&#93; | S2432 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;unlink&#95;receipt&#34; | S2433 |
| task&#95;sha256 | &#34;927ae2fc97a3503e7379a762e8a464ee4283195f392d0e3df19a0fa87043ec39&#34; | S2434 |
| request&#95;id | &#34;request&#45;3e5dc6d89fc04386b9a544942445e7b8&#34; | S2435 |
| manifest&#95;sha256 | &#34;f02649441e88706b3493095f70f158315fec33ab1b8014212b728f79a7ec9594&#34; | S2436 |
| before | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#125; | S2437 |
| unlinked&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;189371Z&#34; | S2438 |
| observed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;191190Z&#34; | S2439 |
| after | &#34;ABSENT&#34; | S2440 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| before | null | S0339 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2441 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2442 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2443 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2444 |
| version&#95;id | &#34;version&#45;8e1b2eaaff1d46189983dbf720ec269f&#34; | S2445 |
| phase | &#34;after&#34; | S2446 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;200700Z&#34; | S2447 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;200777Z&#34; | S2448 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S2449 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2450 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2451 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2452 |
| replicas | &#34;UNKNOWN&#34; | S2453 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2454 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2455 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S2456

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2457 |

###### Recorded core dimensions

All values in the following table come from S2458

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2459

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;d38255426a174d469a2e3ddf37d827cc&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;927ae2fc97a3503e7379a762e8a464ee4283195f392d0e3d&#34;&#44;&#34;request&#45;record&#45;d38255426a174d469a2e3ddf37d827cc&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;PROVIDER&#95;CLAIM&#95;REMAINS&#95;SCOPED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;completion&#45;927ae2fc97a3503e7379a762e8a464ee4283195f392d0e3d&#34;&#44;&#34;request&#45;record&#45;d38255426a174d469a2e3ddf37d827cc&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0337, S0338

**ERASURE&#95;AFTER&#95;ONLY&#95;ABSENCE** — Only the after observation is available&#44; so local corroboration is ABSENCE&#95;ONLY even though an attributed provider completion claim exists&#46;

Source: S0339, S0340, S0341, S0342

### LE&#45;15 — Recreated entry is observed present despite an earlier scoped receipt

Whole-case capture: S0352

Title source: S0353

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0346 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S0347 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S2460 |
| differences | &#123;&#125; | S2461 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93; | S2462 |
| local&#95;observations | &#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93; | S2463 |
| outside&#95;scope&#95;remains&#95;unknown | true | S2464 |
| rejected&#95;probes | 0 | S2465 |
| retained&#95;readable&#95;controls | &#91;&#93; | S2466 |
| states | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; | S2467 |
| unlink&#95;attempts | 1 | S2468 |
| sort&#95;states | false | S2469 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;254931Z&#34; | S2470 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S0348 |
| attempted | true | S2471 |
| reason | &#34;EXACT&#95;NAMESPACE&#95;ENTRY&#95;REMOVAL&#95;CONFIRMED&#34; | S2472 |
| journal&#95;state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2473 |
| local&#95;observation | &#34;PRESENT&#95;AT&#95;OBSERVATION&#34; | S0351 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;5659bdeef8794f3e82af38a36b6ef795&#34; | S2474 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;233733Z&#34; | S2475 |
| queue&#95;state | &#34;received&#34; | S2476 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;5659bdeef8794f3e82af38a36b6ef795&#34; | S2477 |
| completed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;236996Z&#34; | S2478 |
| locations | &#91;&#34;active&#45;object&#45;namespace&#34;&#93; | S2479 |
| exclusions | &#91;&#34;backups&#34;&#44;&#34;replicas&#34;&#44;&#34;downstream&#45;copies&#34;&#44;&#34;training&#45;derivatives&#34;&#44;&#34;open&#45;handles&#45;and&#45;memory&#34;&#44;&#34;storage&#45;media&#34;&#93; | S2480 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;unlink&#95;receipt&#34; | S2481 |
| task&#95;sha256 | &#34;339fa3912204d03c4f74289dbbac003e8aba65c6f6c729607ad9f1416ffb76b4&#34; | S2482 |
| request&#95;id | &#34;request&#45;0317ff363f034d4d97962886cc3b24db&#34; | S2483 |
| manifest&#95;sha256 | &#34;2b61535964cf75736112bea9e6d057cb7d9ff7a18eb805e05e34b218a6e98ca1&#34; | S2484 |
| before | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#125; | S2485 |
| unlinked&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;235261Z&#34; | S2486 |
| observed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;236996Z&#34; | S0349 |
| after | &#34;ABSENT&#34; | S2487 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2488 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2489 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2490 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2491 |
| version&#95;id | &#34;version&#45;e3f6400621794ab5b03766eb6fa14789&#34; | S2492 |
| phase | &#34;before&#34; | S2493 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;224003Z&#34; | S2494 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;224113Z&#34; | S2495 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S2496 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2497 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2498 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2499 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2500 |
| version&#95;id | &#34;version&#45;e3f6400621794ab5b03766eb6fa14789&#34; | S2501 |
| phase | &#34;after&#34; | S2502 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;247232Z&#34; | S2503 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;247329Z&#34; | S2504 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S2505 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2506 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2507 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2508 |
| replicas | &#34;UNKNOWN&#34; | S2509 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2510 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2511 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S2512

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2513 |

###### Recorded core dimensions

All values in the following table come from S2514

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2515

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;5659bdeef8794f3e82af38a36b6ef795&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;339fa3912204d03c4f74289dbbac003e8aba65c6f6c72960&#34;&#44;&#34;request&#45;record&#45;5659bdeef8794f3e82af38a36b6ef795&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;PROVIDER&#95;CLAIM&#95;REMAINS&#95;SCOPED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;completion&#45;339fa3912204d03c4f74289dbbac003e8aba65c6f6c72960&#34;&#44;&#34;request&#45;record&#45;5659bdeef8794f3e82af38a36b6ef795&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0346, S0347

**ERASURE&#95;LATER&#95;PRESENCE** — A later observation found the entry present despite an earlier scoped receipt&#46; Preserve both observations&#59; do not hide the later presence or erase the earlier attributed claim&#46;

Source: S0348, S0349, S0350, S0351

### LE&#45;16 — Failed durable intent prevents unlink

Whole-case capture: S0357

Title source: S0358

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0355 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;0&#125; | S0356 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;BLOCKED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;0&#125; | S2516 |
| differences | &#123;&#125; | S2517 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;REQUEST&#95;ONLY&#34;&#93; | S2518 |
| local&#95;observations | &#91;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93; | S2519 |
| outside&#95;scope&#95;remains&#95;unknown | true | S2520 |
| rejected&#95;probes | 0 | S2521 |
| retained&#95;readable&#95;controls | &#91;&#93; | S2522 |
| states | &#91;&#34;BLOCKED&#34;&#93; | S2523 |
| unlink&#95;attempts | 0 | S2524 |
| sort&#95;states | false | S2525 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;282018Z&#34; | S2526 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;BLOCKED&#34; | S2527 |
| attempted | false | S2528 |
| reason | &#34;INTENT&#95;ACKNOWLEDGEMENT&#95;NOT&#95;ESTABLISHED&#34; | S2529 |
| journal&#95;state | &#34;NOT&#95;CLAIMED&#34; | S2530 |
| local&#95;observation | &#34;PRESENT&#95;AT&#95;OBSERVATION&#34; | S2531 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| acknowledgement | null | S2532 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| attestation | null | S2533 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S2534 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2535 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2536 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2537 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2538 |
| version&#95;id | &#34;version&#45;771a4baa11844d879502c8388c144873&#34; | S2539 |
| phase | &#34;before&#34; | S2540 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;271662Z&#34; | S2541 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;271753Z&#34; | S2542 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S2543 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2544 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2545 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2546 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2547 |
| version&#95;id | &#34;version&#45;771a4baa11844d879502c8388c144873&#34; | S2548 |
| phase | &#34;after&#34; | S2549 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;277595Z&#34; | S2550 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;277689Z&#34; | S2551 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S2552 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2553 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2554 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2555 |
| replicas | &#34;UNKNOWN&#34; | S2556 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2557 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2558 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S2559

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2560 |

###### Recorded core dimensions

All values in the following table come from S2561

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;REQUEST&#95;ONLY&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;NOT&#95;ESTABLISHED&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2562

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;a2590d2f3bd0450bb674bf38de8d0674&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0355, S0356

### LE&#45;17 — Same request ID with another object version conflicts

Whole-case capture: S0362

Title source: S0363

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0360 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#44;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#44;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#44;&#34;REQUEST&#95;ID&#95;CONFLICT&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S0361 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#44;&#34;REQUEST&#95;ONLY&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#44;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#44;&#34;REQUEST&#95;ID&#95;CONFLICT&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S2563 |
| differences | &#123;&#125; | S2564 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#44;&#34;REQUEST&#95;ONLY&#34;&#93; | S2565 |
| local&#95;observations | &#91;&#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34;&#44;&#34;PRESENT&#95;AT&#95;OBSERVATION&#34;&#93; | S2566 |
| outside&#95;scope&#95;remains&#95;unknown | true | S2567 |
| rejected&#95;probes | 0 | S2568 |
| retained&#95;readable&#95;controls | &#91;&#93; | S2569 |
| states | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#44;&#34;REQUEST&#95;ID&#95;CONFLICT&#34;&#93; | S2570 |
| unlink&#95;attempts | 1 | S2571 |
| sort&#95;states | false | S2572 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;339017Z&#34; | S2573 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2574 |
| attempted | true | S2575 |
| reason | &#34;EXACT&#95;NAMESPACE&#95;ENTRY&#95;REMOVAL&#95;CONFIRMED&#34; | S2576 |
| journal&#95;state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2577 |
| local&#95;observation | &#34;REMOVAL&#95;OBSERVED&#95;SAME&#95;CONTROLLER&#34; | S2578 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;95ced70c8c284e82a688432c9b37aa4c&#34; | S2579 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;304462Z&#34; | S2580 |
| queue&#95;state | &#34;received&#34; | S2581 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;95ced70c8c284e82a688432c9b37aa4c&#34; | S2582 |
| completed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;307639Z&#34; | S2583 |
| locations | &#91;&#34;active&#45;object&#45;namespace&#34;&#93; | S2584 |
| exclusions | &#91;&#34;backups&#34;&#44;&#34;replicas&#34;&#44;&#34;downstream&#45;copies&#34;&#44;&#34;training&#45;derivatives&#34;&#44;&#34;open&#45;handles&#45;and&#45;memory&#34;&#44;&#34;storage&#45;media&#34;&#93; | S2585 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;unlink&#95;receipt&#34; | S2586 |
| task&#95;sha256 | &#34;b2215dfbaabdefa88bdfef483ac38769b7995a060f2b7fa8ba8462bb06b6c4e5&#34; | S2587 |
| request&#95;id | &#34;request&#45;70562e1b358541908dac8cbb5a984a30&#34; | S2588 |
| manifest&#95;sha256 | &#34;0ab10a3f97f06ab5537699ef1c0a074ae70f819f1a2e3e265113e88af30db65b&#34; | S2589 |
| before | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#125; | S2590 |
| unlinked&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;305955Z&#34; | S2591 |
| observed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;307639Z&#34; | S2592 |
| after | &#34;ABSENT&#34; | S2593 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2594 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2595 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2596 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2597 |
| version&#95;id | &#34;version&#45;bea7143b579843d0aef4acc997c3505e&#34; | S2598 |
| phase | &#34;before&#34; | S2599 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;294905Z&#34; | S2600 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;294993Z&#34; | S2601 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S2602 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2603 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2604 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2605 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2606 |
| version&#95;id | &#34;version&#45;bea7143b579843d0aef4acc997c3505e&#34; | S2607 |
| phase | &#34;after&#34; | S2608 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;317039Z&#34; | S2609 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;317149Z&#34; | S2610 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;null&#44;&#34;sha256&#34;&#58;null&#44;&#34;state&#34;&#58;&#34;ABSENT&#34;&#125; | S2611 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2612 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2613 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2614 |
| replicas | &#34;UNKNOWN&#34; | S2615 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2616 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2617 |

##### operation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;REQUEST&#95;ID&#95;CONFLICT&#34; | S2618 |
| attempted | false | S2619 |
| reason | &#34;REQUEST&#95;ID&#95;BINDS&#95;DIFFERENT&#95;TASK&#34; | S2620 |
| journal&#95;state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2621 |
| local&#95;observation | &#34;PRESENT&#95;AT&#95;OBSERVATION&#34; | S2622 |

##### acknowledgement — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| acknowledgement | null | S2623 |

##### attestation — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| attestation | null | S2624 |

##### receipt — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| receipt | null | S2625 |

##### namespace&#95;before — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2626 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2627 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2628 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2629 |
| version&#95;id | &#34;version&#45;8eb87608f9684b48959a8696474cba19&#34; | S2630 |
| phase | &#34;before&#34; | S2631 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;327664Z&#34; | S2632 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;327755Z&#34; | S2633 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S2634 |

##### namespace&#95;after — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| provider&#95;id | &#34;provider&#45;local&#34; | S2635 |
| tenant&#95;id | &#34;tenant&#45;synthetic&#34; | S2636 |
| location | &#34;active&#45;object&#45;namespace&#34; | S2637 |
| object&#95;id | &#34;object&#45;synthetic&#34; | S2638 |
| version&#95;id | &#34;version&#45;8eb87608f9684b48959a8696474cba19&#34; | S2639 |
| phase | &#34;after&#34; | S2640 |
| window&#95;start | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;334612Z&#34; | S2641 |
| window&#95;end | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;334706Z&#34; | S2642 |
| measurement | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#44;&#34;state&#34;&#58;&#34;PRESENT&#34;&#125; | S2643 |

##### unknown&#95;domains — original record index 1

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2644 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2645 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2646 |
| replicas | &#34;UNKNOWN&#34; | S2647 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2648 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2649 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S2650

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2651 |

###### Recorded core dimensions

All values in the following table come from S2652

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2653

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;95ced70c8c284e82a688432c9b37aa4c&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;b2215dfbaabdefa88bdfef483ac38769b7995a060f2b7fa8&#34;&#44;&#34;request&#45;record&#45;95ced70c8c284e82a688432c9b37aa4c&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;PROVIDER&#95;CLAIM&#95;REMAINS&#95;SCOPED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;completion&#45;b2215dfbaabdefa88bdfef483ac38769b7995a060f2b7fa8&#34;&#44;&#34;request&#45;record&#45;95ced70c8c284e82a688432c9b37aa4c&#34;&#93;&#125; |

##### original record index 1 — phase erasure

Frame or nearest existing container: S2654

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2655 |

###### Recorded core dimensions

All values in the following table come from S2656

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;REQUEST&#95;ONLY&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;NOT&#95;ESTABLISHED&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2657

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;dbb4f795115648dba633244326335b17&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0360, S0361

### LE&#45;18 — Provider attestation without observer remains a scoped provider claim

Whole-case capture: S0371

Title source: S0372

#### Scenario expectation: MATCHED

| Field | Recorded value | Source |
| --- | --- | --- |
| matched | true | S0365 |
| expected | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;NOT&#95;OBSERVED&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S0366 |
| actual | &#123;&#34;core&#95;evidence&#34;&#58;&#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93;&#44;&#34;local&#95;observations&#34;&#58;&#91;&#34;NOT&#95;OBSERVED&#34;&#93;&#44;&#34;outside&#95;scope&#95;remains&#95;unknown&#34;&#58;true&#44;&#34;rejected&#95;probes&#34;&#58;0&#44;&#34;retained&#95;readable&#95;controls&#34;&#58;&#91;&#93;&#44;&#34;states&#34;&#58;&#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93;&#44;&#34;unlink&#95;attempts&#34;&#58;1&#125; | S2658 |
| differences | &#123;&#125; | S2659 |

#### Recorded sections

##### actual — case-wide

| Field | Recorded value | Source |
| --- | --- | --- |
| core&#95;evidence | &#91;&#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34;&#93; | S2660 |
| local&#95;observations | &#91;&#34;NOT&#95;OBSERVED&#34;&#93; | S2661 |
| outside&#95;scope&#95;remains&#95;unknown | true | S2662 |
| rejected&#95;probes | 0 | S2663 |
| retained&#95;readable&#95;controls | &#91;&#93; | S2664 |
| states | &#91;&#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34;&#93; | S2665 |
| unlink&#95;attempts | 1 | S2666 |
| sort&#95;states | false | S2667 |
| case&#95;as&#95;of | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;386321Z&#34; | S2668 |

##### operation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2669 |
| attempted | true | S2670 |
| reason | &#34;EXACT&#95;NAMESPACE&#95;ENTRY&#95;REMOVAL&#95;CONFIRMED&#34; | S2671 |
| journal&#95;state | &#34;LOCAL&#95;UNLINK&#95;CONFIRMED&#34; | S2672 |
| local&#95;observation | &#34;NOT&#95;OBSERVED&#34; | S0369 |

##### acknowledgement — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;58ae4d6a51c4419ba72402d5345eb9dd&#34; | S2673 |
| acknowledged&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;369125Z&#34; | S2674 |
| queue&#95;state | &#34;received&#34; | S2675 |

##### attestation — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| request&#95;record&#95;id | &#34;request&#45;record&#45;58ae4d6a51c4419ba72402d5345eb9dd&#34; | S2676 |
| completed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;372326Z&#34; | S2677 |
| locations | &#91;&#34;active&#45;object&#45;namespace&#34;&#93; | S2678 |
| exclusions | &#91;&#34;backups&#34;&#44;&#34;replicas&#34;&#44;&#34;downstream&#45;copies&#34;&#44;&#34;training&#45;derivatives&#34;&#44;&#34;open&#45;handles&#45;and&#45;memory&#34;&#44;&#34;storage&#45;media&#34;&#93; | S2679 |

##### receipt — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| kind | &#34;local&#95;unlink&#95;receipt&#34; | S2680 |
| task&#95;sha256 | &#34;937bd9fb67995134cd0b876fa4ac9b6c201cc168053a8b51bdec2f134fd5e529&#34; | S2681 |
| request&#95;id | &#34;request&#45;3248690346954627a155069bb34a64de&#34; | S2682 |
| manifest&#95;sha256 | &#34;b083cd41b39962a401182d3429e2e8f09f51994022f08b4b7f09ad62d6d84c7a&#34; | S2683 |
| before | &#123;&#34;byte&#95;length&#34;&#58;68&#44;&#34;sha256&#34;&#58;&#34;95f2f21837656da95e45aa977aa2ae52c8a64c61d0088fd6eb2ee90ded28e108&#34;&#125; | S2684 |
| unlinked&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;370608Z&#34; | S2685 |
| observed&#95;at | &#34;2026&#45;10&#45;30T03&#58;28&#58;05&#46;372326Z&#34; | S2686 |
| after | &#34;ABSENT&#34; | S2687 |

##### namespace&#95;before — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| before | null | S0367 |

##### namespace&#95;after — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| after | null | S0368 |

##### unknown&#95;domains — original record index 0

| Field | Recorded value | Source |
| --- | --- | --- |
| backups | &#34;UNKNOWN&#34; | S2688 |
| downstream&#45;copies | &#34;UNKNOWN&#34; | S2689 |
| open&#45;handles&#45;and&#45;memory | &#34;UNKNOWN&#34; | S2690 |
| replicas | &#34;UNKNOWN&#34; | S2691 |
| storage&#45;media | &#34;UNKNOWN&#34; | S2692 |
| training&#45;derivatives | &#34;UNKNOWN&#34; | S2693 |

#### Core assessor frames

##### original record index 0 — phase erasure

Frame or nearest existing container: S2694

| Field | Recorded value |
| --- | --- |
| Availability | &#34;RECORDED&#34; |
| Absence reason | null |

| Field | Recorded value | Source |
| --- | --- | --- |
| evidence&#95;integrity | &#34;VERIFIED&#95;UNDER&#95;EVALUATOR&#95;TRUST&#34; | S2695 |

###### Recorded core dimensions

All values in the following table come from S2696

| Field | Recorded value |
| --- | --- |
| binding&#95;assessment | &#34;MATCH&#34; |
| deletion&#95;evidence | &#34;PROVIDER&#95;ATTESTED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| excluded&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| independent&#95;verification | &#34;NOT&#95;ESTABLISHED&#34; |
| outside&#95;scope&#95;outcome | &#34;UNKNOWN&#34; |
| provider&#95;completion | &#34;UNKNOWN&#34; |
| receipt&#95;applicability | &#34;MATCHED&#95;WITHIN&#95;DECLARED&#95;SCOPE&#34; |
| review&#95;result | &#34;NOT&#95;ESTABLISHED&#34; |
| target&#95;completion | &#34;UNKNOWN&#34; |

###### Recorded core findings

All values in the following table come from S2697

| Finding index | Recorded value |
| --- | --- |
| 0 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;LOCAL&#95;REQUEST&#95;ESTABLISHED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;request&#45;record&#45;58ae4d6a51c4419ba72402d5345eb9dd&#34;&#93;&#125; |
| 1 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;ACKNOWLEDGEMENT&#95;IS&#95;NOT&#95;COMPLETION&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;ack&#45;937bd9fb67995134cd0b876fa4ac9b6c201cc168053a8b51&#34;&#44;&#34;request&#45;record&#45;58ae4d6a51c4419ba72402d5345eb9dd&#34;&#93;&#125; |
| 2 | &#123;&#34;code&#34;&#58;&#34;ERASURE&#95;PROVIDER&#95;CLAIM&#95;REMAINS&#95;SCOPED&#34;&#44;&#34;record&#95;ids&#34;&#58;&#91;&#34;completion&#45;937bd9fb67995134cd0b876fa4ac9b6c201cc168053a8b51&#34;&#44;&#34;request&#45;record&#45;58ae4d6a51c4419ba72402d5345eb9dd&#34;&#93;&#125; |

#### Capture interpretations

The following notes interpret this fixed capture; they are not new observations or general decisions.

**EXPECTATION&#95;IS&#95;NOT&#95;SECURITY&#95;PASS** — A matched scenario expectation is not a security&#44; conformance or legal&#45;compliance pass&#46;

Source: S0365, S0366

**ERASURE&#95;NO&#95;OBSERVER** — Observer evidence is absent&#46; The provider attestation remains a scoped provider claim&#44; not independent deletion verification&#46;

Source: S0367, S0368, S0369, S0370

## Source references

Each S-number identifies a concrete JSON Pointer and an F-number. Each F-number identifies one exact archive member and its raw-byte digest. Links point only to the fixed repository capture commit. Values remain attributable to the captured controller statements; a source link is not independent endorsement.

### Captured file inventory

| File reference | Archive member | Raw-file SHA-256 |
| --- | --- | --- |
| [F0001](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/summary.json) | evidence&#47;upload&#47;summary&#46;json | d041087291a95babd2603d7645321c8b7732a10ec2d73f5edd70d94443d7cc22 |
| [F0002](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-01.json) | evidence&#47;upload&#47;cases&#47;UL&#45;01&#46;json | b2dcfd04482bc9155623d29cc0a47a498fc481e12d736e8bee8617157dcc27df |
| [F0003](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-02.json) | evidence&#47;upload&#47;cases&#47;UL&#45;02&#46;json | 9269839f47e1fb1d10770108af3eca20c3305c006a9c3c593f93c31a0bab672a |
| [F0004](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-03.json) | evidence&#47;upload&#47;cases&#47;UL&#45;03&#46;json | ae52f9b87407dd2e2c67f1a0f3871d7b5be501f1faaf23c8d553d9767177f742 |
| [F0005](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-04.json) | evidence&#47;upload&#47;cases&#47;UL&#45;04&#46;json | db5526138e9d772e7a495777d58cf62ddbe669f6d499a0d2c7a7f8b4aea1157e |
| [F0006](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-05.json) | evidence&#47;upload&#47;cases&#47;UL&#45;05&#46;json | d0aec622abc8fbd50668b5f7a61522cbc647da487c0712c7a4fbc7efcd0335c1 |
| [F0007](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-06.json) | evidence&#47;upload&#47;cases&#47;UL&#45;06&#46;json | a0e0adfa565e4caccf985476826302c2c63e97a72d66a43c27ea6174e2b5f276 |
| [F0008](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-07.json) | evidence&#47;upload&#47;cases&#47;UL&#45;07&#46;json | 5e4248bb28da61796158676172af2243678b18454fdc8a6f9a1a34c413d37dce |
| [F0009](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-08.json) | evidence&#47;upload&#47;cases&#47;UL&#45;08&#46;json | a171c8159b7182a1a964c0b0281da09db3788b10f5cce1b218683d036827566a |
| [F0010](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-09.json) | evidence&#47;upload&#47;cases&#47;UL&#45;09&#46;json | 2fc28cf4f0de80e772b9e0f640c2ff8eda3ba56a6b2e6c009997376f8c0e3b72 |
| [F0011](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-10.json) | evidence&#47;upload&#47;cases&#47;UL&#45;10&#46;json | b70c8e6aa3fd265c8c77f21f8d8f40b9fbb6a0156a4aa57cc61e75671910c563 |
| [F0012](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-11.json) | evidence&#47;upload&#47;cases&#47;UL&#45;11&#46;json | 1bde2245d696f67e1b03f8f11ef4882812026c8ac93974b39e4d91ee0bd8ff31 |
| [F0013](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-12.json) | evidence&#47;upload&#47;cases&#47;UL&#45;12&#46;json | b48d649ef250c60fb40cf2276941664824c24e3be6cdecf1383a6237c0261d3b |
| [F0014](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-13.json) | evidence&#47;upload&#47;cases&#47;UL&#45;13&#46;json | 63415440b019487a71bdac8ea053c156f069fbf31ff4c08ae11f42e4ffcb53f2 |
| [F0015](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-14.json) | evidence&#47;upload&#47;cases&#47;UL&#45;14&#46;json | 8de2786ecce446f3c446293744e07e35ad671c94c89e2a64c7c49f1b28697197 |
| [F0016](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-15.json) | evidence&#47;upload&#47;cases&#47;UL&#45;15&#46;json | 97b43319ab4bb879c88cf142e1c62cfb832deb38778af344df82fba7876661b3 |
| [F0017](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-16.json) | evidence&#47;upload&#47;cases&#47;UL&#45;16&#46;json | 79b14d4bea0893d4de029568698a48f6d183d0c785139456d1f9b3817e339833 |
| [F0018](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/upload/cases/UL-17.json) | evidence&#47;upload&#47;cases&#47;UL&#45;17&#46;json | b07192b11f2e2d763c0eea9a5fe674f6dded9cdb9e06f8579bbff32a0ba1f550 |
| [F0019](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/summary.json) | evidence&#47;publication&#47;summary&#46;json | 9ba90113030418a5b04ad989ec5383b35ee76073b085460091b8e2ec5c715fc1 |
| [F0020](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-01.json) | evidence&#47;publication&#47;cases&#47;LP&#45;01&#46;json | df89f468ffdefaf45404839c67409165105b9db1f9dfdf8cf1c7434cad1e92e6 |
| [F0021](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-02.json) | evidence&#47;publication&#47;cases&#47;LP&#45;02&#46;json | 52656c8dd104a96a7fe5b8d03b911b92b0c0aac66e45850ec94b43db69f06dd9 |
| [F0022](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-03.json) | evidence&#47;publication&#47;cases&#47;LP&#45;03&#46;json | 0a350a110a1d7a761291c56facbb542c89370030316534837a74f2873768278d |
| [F0023](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-04.json) | evidence&#47;publication&#47;cases&#47;LP&#45;04&#46;json | 44fbdd5fa6220ffc415bab23f5dc8b821b22fb3fe117d68e8b8488a9d945f5f2 |
| [F0024](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-05.json) | evidence&#47;publication&#47;cases&#47;LP&#45;05&#46;json | 5b95e24998df2aed3a030dda60ae501cdb9290012669dc8486a4b39679fa508f |
| [F0025](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-06.json) | evidence&#47;publication&#47;cases&#47;LP&#45;06&#46;json | 2e540bc6f9f370da67697eccb497a248228e13ab6f366ef0e555d966e9fd0d4a |
| [F0026](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-07.json) | evidence&#47;publication&#47;cases&#47;LP&#45;07&#46;json | 223ceccd23d6e4cb7ea46ffba0a4e87d685fa931346269193ecc2ca212809bd9 |
| [F0027](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-08.json) | evidence&#47;publication&#47;cases&#47;LP&#45;08&#46;json | 193accfcc80cab3024655e7c562a1e8ef17de1b3efa8356e9daef5cb7db366a8 |
| [F0028](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-09.json) | evidence&#47;publication&#47;cases&#47;LP&#45;09&#46;json | 11eb326023cee09ad8789129d98152aa2090491ca30a687c5dda1f1682acc73c |
| [F0029](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-10.json) | evidence&#47;publication&#47;cases&#47;LP&#45;10&#46;json | 331fc043fca446327a397aea62521017c21f0fd1c03eb6e43dd230eac7d125d1 |
| [F0030](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-11.json) | evidence&#47;publication&#47;cases&#47;LP&#45;11&#46;json | 6da1acff6573cb3f576a0a0df8cf6965fc10b06796925c5e6bfdc3f2856e6541 |
| [F0031](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-12.json) | evidence&#47;publication&#47;cases&#47;LP&#45;12&#46;json | 609b0aeddc2f08c1303a996526c9f8f18776c6b16997a19412020ced0057ecc8 |
| [F0032](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-13.json) | evidence&#47;publication&#47;cases&#47;LP&#45;13&#46;json | d3b194272e0b04d03f3c6062278b23e9c1f3ec164f2050be63ff4fc3976e9fd2 |
| [F0033](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-14.json) | evidence&#47;publication&#47;cases&#47;LP&#45;14&#46;json | 5adbe117ce41f9eda73e769443ad95f28215ddb7c1421e289339c3ca028fbab9 |
| [F0034](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-15.json) | evidence&#47;publication&#47;cases&#47;LP&#45;15&#46;json | 4f93a498b4c4832b47335402dcd556e4d54df540854916cb02c16bc078d39806 |
| [F0035](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-16.json) | evidence&#47;publication&#47;cases&#47;LP&#45;16&#46;json | 4138b40829ceb8111ce9dcda3e3ee02e30f69bb239844db4685bab6dca58f919 |
| [F0036](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-17.json) | evidence&#47;publication&#47;cases&#47;LP&#45;17&#46;json | d97a378927ac77ac8117cd32a4db1ce2101bfdf5434266f3696c00a3030d57bd |
| [F0037](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/publication/cases/LP-18.json) | evidence&#47;publication&#47;cases&#47;LP&#45;18&#46;json | b30fccb7007c2f9ab9c56e54c761a7fc580b44ebf09acf0f3cf507b6c85af892 |
| [F0038](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/summary.json) | evidence&#47;erasure&#47;summary&#46;json | 8ca8ab03504322e293360fe98d4e16ee278e9f7eb3bb0e3b237f4f5948b3a16d |
| [F0039](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-01.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;01&#46;json | b085c5a37d0291c50eb1e13edf84da5a6fd5926336a6468a05e8dd7079421c30 |
| [F0040](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-02.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;02&#46;json | 0fdeb884e061dccf387599ea9f83cc550e8eefb344d17d4aeea4d840d29eff72 |
| [F0041](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-03.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;03&#46;json | 29fcc4461c4daeeed2bbcfd8824b1c0305324dbe03f61556a25e2a20eade7cde |
| [F0042](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-04.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;04&#46;json | 8d440bb339f7f594390b06e6c34a77c73037b4baecc98a160540bece6fd4d629 |
| [F0043](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-05.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;05&#46;json | 4ee5b6e8af17d0a5d3f4e1b9b803e73c77daf7896d687e54221308bd213a719f |
| [F0044](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-06.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;06&#46;json | cac664e14d7c12a4a11267af1d54a022d04a70ac6cd50680fb79d265e65cee3c |
| [F0045](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-07.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;07&#46;json | 23ebb972efe8793cda25efedeb09c99d4cdb337a5df6555070d460ef4c2cba4f |
| [F0046](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-08.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;08&#46;json | d92b933f6b546fb684cd3684ef3a8604551545052456083a7cf40b93c5ba1875 |
| [F0047](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-09.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;09&#46;json | 8e2908ba81397e74006ea42a4a3c55af6de18c2789b2e8c441781e1740961348 |
| [F0048](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-10.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;10&#46;json | d7b9a63bcfdf674c63baa8a866237bf3a65c09afe9ddc54a132ae9fbb9f6f596 |
| [F0049](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-11.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;11&#46;json | d09b54f59e05969bd61d7bf399518f173427a00fdf7e3ebb7bc381d66e56f19c |
| [F0050](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-12.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;12&#46;json | 4ea0f643e31cbe08d39e464e6c877e42b9036b9c07c20e31bc94905b70dbc2dc |
| [F0051](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-13.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;13&#46;json | 51ccf42ab0711205ca3a32a1728e1260e424fd7f672e58b74e50f9450baa1f99 |
| [F0052](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-14.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;14&#46;json | 23464e74e336f2a3fdf87b845bdb55f0f3ff703eb0adbd8bb4f3aa32c8724fad |
| [F0053](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-15.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;15&#46;json | a24b083e683082af77a58e939618e6694faa4d9eb9fda241e85e6d2ef769c60a |
| [F0054](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-16.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;16&#46;json | 7ae8a0c12f6d04c9613d1baadca4f178dfd76afbd6dd3ffaefe424567a7acb25 |
| [F0055](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-17.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;17&#46;json | 69e7aead108c0bd3fad7388455c74f24e29e98174c78f12ca6eac2a5899d2447 |
| [F0056](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/erasure/cases/LE-18.json) | evidence&#47;erasure&#47;cases&#47;LE&#45;18&#46;json | 9b343c13953d03dbd8dee0fce04afc7bc99a4626373647fc133e4bac1ed61401 |
| [F0057](https://github.com/veritaschain/vap-spec/blob/1553ff9729ceb30f3ff03513cead45c5b7abd1d9/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/provenance.json) | evidence&#47;provenance&#46;json | 986096ffcd48efeeb248dde4719c08b15eac0c80c1dd60573ce954e5ed144387 |

### Concrete source pointers

| Source | File reference | JSON Pointer |
| --- | --- | --- |
| S0001 | F0001 | &#47;results&#47;0&#47;matched |
| S0002 | F0001 | &#47;results&#47;0&#47;expected |
| S0003 | F0002 | &#47;reports&#47;0&#47;state |
| S0004 | F0002 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments&#47;remote&#95;outcome |
| S0005 | F0002 | document root (empty JSON Pointer) |
| S0006 | F0001 | &#47;results&#47;0&#47;title |
| S0007 | F0001 | &#47;results&#47;0&#47;actual&#47;states |
| S0008 | F0001 | &#47;results&#47;1&#47;matched |
| S0009 | F0001 | &#47;results&#47;1&#47;expected |
| S0010 | F0003 | document root (empty JSON Pointer) |
| S0011 | F0001 | &#47;results&#47;1&#47;title |
| S0012 | F0001 | &#47;results&#47;1&#47;actual&#47;states |
| S0013 | F0001 | &#47;results&#47;2&#47;matched |
| S0014 | F0001 | &#47;results&#47;2&#47;expected |
| S0015 | F0004 | document root (empty JSON Pointer) |
| S0016 | F0001 | &#47;results&#47;2&#47;title |
| S0017 | F0001 | &#47;results&#47;2&#47;actual&#47;states |
| S0018 | F0001 | &#47;results&#47;3&#47;matched |
| S0019 | F0001 | &#47;results&#47;3&#47;expected |
| S0020 | F0005 | document root (empty JSON Pointer) |
| S0021 | F0001 | &#47;results&#47;3&#47;title |
| S0022 | F0001 | &#47;results&#47;3&#47;actual&#47;states |
| S0023 | F0001 | &#47;results&#47;4&#47;matched |
| S0024 | F0001 | &#47;results&#47;4&#47;expected |
| S0025 | F0006 | document root (empty JSON Pointer) |
| S0026 | F0001 | &#47;results&#47;4&#47;title |
| S0027 | F0001 | &#47;results&#47;4&#47;actual&#47;states |
| S0028 | F0001 | &#47;results&#47;5&#47;matched |
| S0029 | F0001 | &#47;results&#47;5&#47;expected |
| S0030 | F0007 | document root (empty JSON Pointer) |
| S0031 | F0001 | &#47;results&#47;5&#47;title |
| S0032 | F0001 | &#47;results&#47;5&#47;actual&#47;states |
| S0033 | F0001 | &#47;results&#47;6&#47;matched |
| S0034 | F0001 | &#47;results&#47;6&#47;expected |
| S0035 | F0008 | &#47;reports&#47;0&#47;state |
| S0036 | F0008 | &#47;reports&#47;0&#47;receipt |
| S0037 | F0008 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0038 | F0008 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments&#47;remote&#95;outcome |
| S0039 | F0008 | document root (empty JSON Pointer) |
| S0040 | F0001 | &#47;results&#47;6&#47;title |
| S0041 | F0001 | &#47;results&#47;6&#47;actual&#47;states |
| S0042 | F0001 | &#47;results&#47;7&#47;matched |
| S0043 | F0001 | &#47;results&#47;7&#47;expected |
| S0044 | F0009 | &#47;reports&#47;0&#47;state |
| S0045 | F0009 | &#47;reports&#47;0&#47;receipt |
| S0046 | F0009 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0047 | F0009 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments&#47;remote&#95;outcome |
| S0048 | F0009 | document root (empty JSON Pointer) |
| S0049 | F0001 | &#47;results&#47;7&#47;title |
| S0050 | F0001 | &#47;results&#47;7&#47;actual&#47;states |
| S0051 | F0001 | &#47;results&#47;8&#47;matched |
| S0052 | F0001 | &#47;results&#47;8&#47;expected |
| S0053 | F0010 | &#47;reports&#47;0&#47;state |
| S0054 | F0010 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments&#47;remote&#95;outcome |
| S0055 | F0010 | document root (empty JSON Pointer) |
| S0056 | F0001 | &#47;results&#47;8&#47;title |
| S0057 | F0001 | &#47;results&#47;8&#47;actual&#47;states |
| S0058 | F0001 | &#47;results&#47;9&#47;matched |
| S0059 | F0001 | &#47;results&#47;9&#47;expected |
| S0060 | F0011 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments&#47;transfer&#95;authorization |
| S0061 | F0011 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;assessments&#47;transfer&#95;authorization |
| S0062 | F0011 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments&#47;transfer&#95;authorization |
| S0063 | F0011 | &#47;reports&#47;0&#47;attempted |
| S0064 | F0011 | document root (empty JSON Pointer) |
| S0065 | F0001 | &#47;results&#47;9&#47;title |
| S0066 | F0001 | &#47;results&#47;9&#47;actual&#47;states |
| S0067 | F0001 | &#47;results&#47;10&#47;matched |
| S0068 | F0001 | &#47;results&#47;10&#47;expected |
| S0069 | F0012 | &#47;reports&#47;0&#47;state |
| S0070 | F0012 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments&#47;remote&#95;outcome |
| S0071 | F0012 | document root (empty JSON Pointer) |
| S0072 | F0001 | &#47;results&#47;10&#47;title |
| S0073 | F0001 | &#47;results&#47;10&#47;actual&#47;states |
| S0074 | F0001 | &#47;results&#47;11&#47;matched |
| S0075 | F0001 | &#47;results&#47;11&#47;expected |
| S0076 | F0013 | &#47;reports&#47;0&#47;state |
| S0077 | F0013 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments&#47;remote&#95;outcome |
| S0078 | F0013 | document root (empty JSON Pointer) |
| S0079 | F0001 | &#47;results&#47;11&#47;title |
| S0080 | F0001 | &#47;results&#47;11&#47;actual&#47;states |
| S0081 | F0001 | &#47;results&#47;12&#47;matched |
| S0082 | F0001 | &#47;results&#47;12&#47;expected |
| S0083 | F0014 | document root (empty JSON Pointer) |
| S0084 | F0001 | &#47;results&#47;12&#47;title |
| S0085 | F0001 | &#47;results&#47;12&#47;actual&#47;states |
| S0086 | F0001 | &#47;results&#47;13&#47;matched |
| S0087 | F0001 | &#47;results&#47;13&#47;expected |
| S0088 | F0015 | &#47;reports&#47;0&#47;state |
| S0089 | F0015 | &#47;actual&#47;gateway&#95;attempts |
| S0090 | F0015 | &#47;actual&#47;handler&#95;calls |
| S0091 | F0015 | &#47;actual&#47;accepted&#95;count |
| S0092 | F0015 | &#47;actual&#47;controller&#95;direct&#95;status |
| S0093 | F0015 | &#47;actual&#47;all&#95;route&#95;prevention&#95;established |
| S0094 | F0015 | document root (empty JSON Pointer) |
| S0095 | F0001 | &#47;results&#47;13&#47;title |
| S0096 | F0001 | &#47;results&#47;13&#47;actual&#47;states |
| S0097 | F0001 | &#47;results&#47;14&#47;matched |
| S0098 | F0001 | &#47;results&#47;14&#47;expected |
| S0099 | F0016 | &#47;reports&#47;0&#47;state |
| S0100 | F0016 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments&#47;remote&#95;outcome |
| S0101 | F0016 | document root (empty JSON Pointer) |
| S0102 | F0001 | &#47;results&#47;14&#47;title |
| S0103 | F0001 | &#47;results&#47;14&#47;actual&#47;states |
| S0104 | F0001 | &#47;results&#47;15&#47;matched |
| S0105 | F0001 | &#47;results&#47;15&#47;expected |
| S0106 | F0017 | &#47;reports&#47;0&#47;state |
| S0107 | F0017 | &#47;reports&#47;0&#47;receipt |
| S0108 | F0017 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0109 | F0017 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments&#47;remote&#95;outcome |
| S0110 | F0017 | document root (empty JSON Pointer) |
| S0111 | F0001 | &#47;results&#47;15&#47;title |
| S0112 | F0001 | &#47;results&#47;15&#47;actual&#47;states |
| S0113 | F0001 | &#47;results&#47;16&#47;matched |
| S0114 | F0001 | &#47;results&#47;16&#47;expected |
| S0115 | F0018 | &#47;actual&#47;worker&#95;killed&#95;after&#95;intent |
| S0116 | F0018 | &#47;actual&#47;worker&#95;exitcode |
| S0117 | F0018 | &#47;reports&#47;0&#47;journal&#95;state |
| S0118 | F0018 | &#47;actual&#47;gateway&#95;attempts |
| S0119 | F0018 | document root (empty JSON Pointer) |
| S0120 | F0001 | &#47;results&#47;16&#47;title |
| S0121 | F0001 | &#47;results&#47;16&#47;actual&#47;states |
| S0122 | F0019 | &#47;results&#47;0&#47;matched |
| S0123 | F0019 | &#47;results&#47;0&#47;expected |
| S0124 | F0020 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S0125 | F0020 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments&#47;publication&#95;action |
| S0126 | F0020 | document root (empty JSON Pointer) |
| S0127 | F0019 | &#47;results&#47;0&#47;title |
| S0128 | F0019 | &#47;results&#47;0&#47;actual&#47;states |
| S0129 | F0019 | &#47;results&#47;1&#47;matched |
| S0130 | F0019 | &#47;results&#47;1&#47;expected |
| S0131 | F0021 | document root (empty JSON Pointer) |
| S0132 | F0019 | &#47;results&#47;1&#47;title |
| S0133 | F0019 | &#47;results&#47;1&#47;actual&#47;states |
| S0134 | F0019 | &#47;results&#47;2&#47;matched |
| S0135 | F0019 | &#47;results&#47;2&#47;expected |
| S0136 | F0022 | document root (empty JSON Pointer) |
| S0137 | F0019 | &#47;results&#47;2&#47;title |
| S0138 | F0019 | &#47;results&#47;2&#47;actual&#47;states |
| S0139 | F0019 | &#47;results&#47;3&#47;matched |
| S0140 | F0019 | &#47;results&#47;3&#47;expected |
| S0141 | F0023 | document root (empty JSON Pointer) |
| S0142 | F0019 | &#47;results&#47;3&#47;title |
| S0143 | F0019 | &#47;results&#47;3&#47;actual&#47;states |
| S0144 | F0019 | &#47;results&#47;4&#47;matched |
| S0145 | F0019 | &#47;results&#47;4&#47;expected |
| S0146 | F0024 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments&#47;publication&#95;action |
| S0147 | F0024 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments&#47;policy&#95;assessment |
| S0148 | F0024 | document root (empty JSON Pointer) |
| S0149 | F0019 | &#47;results&#47;4&#47;title |
| S0150 | F0019 | &#47;results&#47;4&#47;actual&#47;states |
| S0151 | F0019 | &#47;results&#47;5&#47;matched |
| S0152 | F0019 | &#47;results&#47;5&#47;expected |
| S0153 | F0025 | document root (empty JSON Pointer) |
| S0154 | F0019 | &#47;results&#47;5&#47;title |
| S0155 | F0019 | &#47;results&#47;5&#47;actual&#47;states |
| S0156 | F0019 | &#47;results&#47;6&#47;matched |
| S0157 | F0019 | &#47;results&#47;6&#47;expected |
| S0158 | F0026 | document root (empty JSON Pointer) |
| S0159 | F0019 | &#47;results&#47;6&#47;title |
| S0160 | F0019 | &#47;results&#47;6&#47;actual&#47;states |
| S0161 | F0019 | &#47;results&#47;7&#47;matched |
| S0162 | F0019 | &#47;results&#47;7&#47;expected |
| S0163 | F0027 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S0164 | F0027 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;authorized&#95;local&#95;export |
| S0165 | F0027 | &#47;records&#47;0&#47;report&#47;attempted |
| S0166 | F0027 | document root (empty JSON Pointer) |
| S0167 | F0019 | &#47;results&#47;7&#47;title |
| S0168 | F0019 | &#47;results&#47;7&#47;actual&#47;states |
| S0169 | F0019 | &#47;results&#47;8&#47;matched |
| S0170 | F0019 | &#47;results&#47;8&#47;expected |
| S0171 | F0028 | &#47;additional&#95;observations&#47;core&#95;ai&#95;involvement |
| S0172 | F0028 | &#47;additional&#95;observations&#47;core&#95;activity&#95;completeness |
| S0173 | F0028 | &#47;additional&#95;observations&#47;declared&#95;activities |
| S0174 | F0028 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S0175 | F0028 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments&#47;publication&#95;action |
| S0176 | F0028 | document root (empty JSON Pointer) |
| S0177 | F0019 | &#47;results&#47;8&#47;title |
| S0178 | F0019 | &#47;results&#47;8&#47;actual&#47;states |
| S0179 | F0019 | &#47;results&#47;9&#47;matched |
| S0180 | F0019 | &#47;results&#47;9&#47;expected |
| S0181 | F0029 | &#47;additional&#95;observations&#47;core&#95;ai&#95;involvement |
| S0182 | F0029 | &#47;additional&#95;observations&#47;core&#95;activity&#95;completeness |
| S0183 | F0029 | &#47;additional&#95;observations&#47;declared&#95;activities |
| S0184 | F0029 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S0185 | F0029 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments&#47;publication&#95;action |
| S0186 | F0029 | document root (empty JSON Pointer) |
| S0187 | F0019 | &#47;results&#47;9&#47;title |
| S0188 | F0019 | &#47;results&#47;9&#47;actual&#47;states |
| S0189 | F0019 | &#47;results&#47;10&#47;matched |
| S0190 | F0019 | &#47;results&#47;10&#47;expected |
| S0191 | F0030 | document root (empty JSON Pointer) |
| S0192 | F0019 | &#47;results&#47;10&#47;title |
| S0193 | F0019 | &#47;results&#47;10&#47;actual&#47;states |
| S0194 | F0019 | &#47;results&#47;11&#47;matched |
| S0195 | F0019 | &#47;results&#47;11&#47;expected |
| S0196 | F0031 | document root (empty JSON Pointer) |
| S0197 | F0019 | &#47;results&#47;11&#47;title |
| S0198 | F0019 | &#47;results&#47;11&#47;actual&#47;states |
| S0199 | F0019 | &#47;results&#47;12&#47;matched |
| S0200 | F0019 | &#47;results&#47;12&#47;expected |
| S0201 | F0032 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S0202 | F0032 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments&#47;publication&#95;action |
| S0203 | F0032 | document root (empty JSON Pointer) |
| S0204 | F0019 | &#47;results&#47;12&#47;title |
| S0205 | F0019 | &#47;results&#47;12&#47;actual&#47;states |
| S0206 | F0019 | &#47;results&#47;13&#47;matched |
| S0207 | F0019 | &#47;results&#47;13&#47;expected |
| S0208 | F0033 | &#47;records&#47;0&#47;report&#47;state |
| S0209 | F0033 | &#47;records&#47;0&#47;report&#47;receipt |
| S0210 | F0033 | &#47;visible&#47;visible&#95;count |
| S0211 | F0033 | document root (empty JSON Pointer) |
| S0212 | F0019 | &#47;results&#47;13&#47;title |
| S0213 | F0019 | &#47;results&#47;13&#47;actual&#47;states |
| S0214 | F0019 | &#47;results&#47;14&#47;matched |
| S0215 | F0019 | &#47;results&#47;14&#47;expected |
| S0216 | F0034 | &#47;records&#47;1&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S0217 | F0034 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments&#47;publication&#95;action |
| S0218 | F0034 | &#47;sort&#95;states |
| S0219 | F0034 | &#47;actual |
| S0220 | F0034 | &#47;records |
| S0221 | F0034 | document root (empty JSON Pointer) |
| S0222 | F0019 | &#47;results&#47;14&#47;title |
| S0223 | F0019 | &#47;results&#47;14&#47;actual&#47;states |
| S0224 | F0019 | &#47;results&#47;15&#47;matched |
| S0225 | F0019 | &#47;results&#47;15&#47;expected |
| S0226 | F0035 | &#47;records&#47;0&#47;report&#47;state |
| S0227 | F0035 | &#47;records&#47;0&#47;report&#47;publication |
| S0228 | F0035 | &#47;actual&#47;publication&#95;attempts |
| S0229 | F0035 | &#47;actual&#47;visible&#95;count |
| S0230 | F0035 | &#47;outside&#95;gate&#95;write&#95;observed |
| S0231 | F0035 | &#47;actual&#47;all&#95;route&#95;prevention&#95;established |
| S0232 | F0035 | document root (empty JSON Pointer) |
| S0233 | F0019 | &#47;results&#47;15&#47;title |
| S0234 | F0019 | &#47;results&#47;15&#47;actual&#47;states |
| S0235 | F0019 | &#47;results&#47;16&#47;matched |
| S0236 | F0019 | &#47;results&#47;16&#47;expected |
| S0237 | F0036 | document root (empty JSON Pointer) |
| S0238 | F0019 | &#47;results&#47;16&#47;title |
| S0239 | F0019 | &#47;results&#47;16&#47;actual&#47;states |
| S0240 | F0019 | &#47;results&#47;17&#47;matched |
| S0241 | F0019 | &#47;results&#47;17&#47;expected |
| S0242 | F0037 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S0243 | F0037 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments&#47;publication&#95;action |
| S0244 | F0037 | document root (empty JSON Pointer) |
| S0245 | F0019 | &#47;results&#47;17&#47;title |
| S0246 | F0019 | &#47;results&#47;17&#47;actual&#47;states |
| S0247 | F0038 | &#47;results&#47;0&#47;matched |
| S0248 | F0038 | &#47;results&#47;0&#47;expected |
| S0249 | F0039 | document root (empty JSON Pointer) |
| S0250 | F0038 | &#47;results&#47;0&#47;title |
| S0251 | F0038 | &#47;results&#47;0&#47;actual&#47;states |
| S0252 | F0038 | &#47;results&#47;1&#47;matched |
| S0253 | F0038 | &#47;results&#47;1&#47;expected |
| S0254 | F0040 | document root (empty JSON Pointer) |
| S0255 | F0038 | &#47;results&#47;1&#47;title |
| S0256 | F0038 | &#47;results&#47;1&#47;actual&#47;states |
| S0257 | F0038 | &#47;results&#47;2&#47;matched |
| S0258 | F0038 | &#47;results&#47;2&#47;expected |
| S0259 | F0041 | document root (empty JSON Pointer) |
| S0260 | F0038 | &#47;results&#47;2&#47;title |
| S0261 | F0038 | &#47;results&#47;2&#47;actual&#47;states |
| S0262 | F0038 | &#47;results&#47;3&#47;matched |
| S0263 | F0038 | &#47;results&#47;3&#47;expected |
| S0264 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S0265 | F0042 | &#47;probes&#47;0&#47;outcome |
| S0266 | F0042 | document root (empty JSON Pointer) |
| S0267 | F0038 | &#47;results&#47;3&#47;title |
| S0268 | F0038 | &#47;results&#47;3&#47;actual&#47;states |
| S0269 | F0038 | &#47;results&#47;4&#47;matched |
| S0270 | F0038 | &#47;results&#47;4&#47;expected |
| S0271 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S0272 | F0043 | &#47;probes&#47;0&#47;outcome |
| S0273 | F0043 | document root (empty JSON Pointer) |
| S0274 | F0038 | &#47;results&#47;4&#47;title |
| S0275 | F0038 | &#47;results&#47;4&#47;actual&#47;states |
| S0276 | F0038 | &#47;results&#47;5&#47;matched |
| S0277 | F0038 | &#47;results&#47;5&#47;expected |
| S0278 | F0044 | document root (empty JSON Pointer) |
| S0279 | F0038 | &#47;results&#47;5&#47;title |
| S0280 | F0038 | &#47;results&#47;5&#47;actual&#47;states |
| S0281 | F0038 | &#47;results&#47;6&#47;matched |
| S0282 | F0038 | &#47;results&#47;6&#47;expected |
| S0283 | F0045 | document root (empty JSON Pointer) |
| S0284 | F0038 | &#47;results&#47;6&#47;title |
| S0285 | F0038 | &#47;results&#47;6&#47;actual&#47;states |
| S0286 | F0038 | &#47;results&#47;7&#47;matched |
| S0287 | F0038 | &#47;results&#47;7&#47;expected |
| S0288 | F0046 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S0289 | F0046 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S0290 | F0046 | document root (empty JSON Pointer) |
| S0291 | F0038 | &#47;results&#47;7&#47;title |
| S0292 | F0038 | &#47;results&#47;7&#47;actual&#47;states |
| S0293 | F0038 | &#47;results&#47;8&#47;matched |
| S0294 | F0038 | &#47;results&#47;8&#47;expected |
| S0295 | F0047 | document root (empty JSON Pointer) |
| S0296 | F0038 | &#47;results&#47;8&#47;title |
| S0297 | F0038 | &#47;results&#47;8&#47;actual&#47;states |
| S0298 | F0038 | &#47;results&#47;9&#47;matched |
| S0299 | F0038 | &#47;results&#47;9&#47;expected |
| S0300 | F0048 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S0301 | F0048 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt |
| S0302 | F0048 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S0303 | F0048 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;state |
| S0304 | F0048 | document root (empty JSON Pointer) |
| S0305 | F0038 | &#47;results&#47;9&#47;title |
| S0306 | F0038 | &#47;results&#47;9&#47;actual&#47;states |
| S0307 | F0038 | &#47;results&#47;10&#47;matched |
| S0308 | F0038 | &#47;results&#47;10&#47;expected |
| S0309 | F0049 | &#47;sort&#95;states |
| S0310 | F0049 | &#47;actual |
| S0311 | F0049 | &#47;records |
| S0312 | F0049 | document root (empty JSON Pointer) |
| S0313 | F0038 | &#47;results&#47;10&#47;title |
| S0314 | F0038 | &#47;results&#47;10&#47;actual&#47;states |
| S0315 | F0038 | &#47;results&#47;11&#47;matched |
| S0316 | F0038 | &#47;results&#47;11&#47;expected |
| S0317 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S0318 | F0050 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S0319 | F0050 | &#47;retained&#95;controls&#47;0&#47;body&#47;mechanism |
| S0320 | F0050 | &#47;retained&#95;controls&#47;0&#47;body&#47;state |
| S0321 | F0050 | &#47;retained&#95;controls&#47;0&#47;body&#47;observed&#95;at |
| S0322 | F0050 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains |
| S0323 | F0050 | document root (empty JSON Pointer) |
| S0324 | F0038 | &#47;results&#47;11&#47;title |
| S0325 | F0038 | &#47;results&#47;11&#47;actual&#47;states |
| S0326 | F0038 | &#47;results&#47;12&#47;matched |
| S0327 | F0038 | &#47;results&#47;12&#47;expected |
| S0328 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S0329 | F0051 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S0330 | F0051 | &#47;retained&#95;controls&#47;0&#47;body&#47;mechanism |
| S0331 | F0051 | &#47;retained&#95;controls&#47;0&#47;body&#47;state |
| S0332 | F0051 | &#47;retained&#95;controls&#47;0&#47;body&#47;observed&#95;at |
| S0333 | F0051 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains |
| S0334 | F0051 | document root (empty JSON Pointer) |
| S0335 | F0038 | &#47;results&#47;12&#47;title |
| S0336 | F0038 | &#47;results&#47;12&#47;actual&#47;states |
| S0337 | F0038 | &#47;results&#47;13&#47;matched |
| S0338 | F0038 | &#47;results&#47;13&#47;expected |
| S0339 | F0052 | &#47;records&#47;0&#47;bundle&#47;before |
| S0340 | F0052 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement&#47;state |
| S0341 | F0052 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S0342 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S0343 | F0052 | document root (empty JSON Pointer) |
| S0344 | F0038 | &#47;results&#47;13&#47;title |
| S0345 | F0038 | &#47;results&#47;13&#47;actual&#47;states |
| S0346 | F0038 | &#47;results&#47;14&#47;matched |
| S0347 | F0038 | &#47;results&#47;14&#47;expected |
| S0348 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S0349 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;observed&#95;at |
| S0350 | F0053 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement&#47;state |
| S0351 | F0053 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S0352 | F0053 | document root (empty JSON Pointer) |
| S0353 | F0038 | &#47;results&#47;14&#47;title |
| S0354 | F0038 | &#47;results&#47;14&#47;actual&#47;states |
| S0355 | F0038 | &#47;results&#47;15&#47;matched |
| S0356 | F0038 | &#47;results&#47;15&#47;expected |
| S0357 | F0054 | document root (empty JSON Pointer) |
| S0358 | F0038 | &#47;results&#47;15&#47;title |
| S0359 | F0038 | &#47;results&#47;15&#47;actual&#47;states |
| S0360 | F0038 | &#47;results&#47;16&#47;matched |
| S0361 | F0038 | &#47;results&#47;16&#47;expected |
| S0362 | F0055 | document root (empty JSON Pointer) |
| S0363 | F0038 | &#47;results&#47;16&#47;title |
| S0364 | F0038 | &#47;results&#47;16&#47;actual&#47;states |
| S0365 | F0038 | &#47;results&#47;17&#47;matched |
| S0366 | F0038 | &#47;results&#47;17&#47;expected |
| S0367 | F0056 | &#47;records&#47;0&#47;bundle&#47;before |
| S0368 | F0056 | &#47;records&#47;0&#47;bundle&#47;after |
| S0369 | F0056 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S0370 | F0056 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments&#47;deletion&#95;evidence |
| S0371 | F0056 | document root (empty JSON Pointer) |
| S0372 | F0038 | &#47;results&#47;17&#47;title |
| S0373 | F0038 | &#47;results&#47;17&#47;actual&#47;states |
| S0374 | F0001 | document root (empty JSON Pointer) |
| S0375 | F0057 | &#47;pilots&#47;upload |
| S0376 | F0001 | &#47;recorded&#95;at |
| S0377 | F0001 | &#47;network&#95;execution |
| S0378 | F0001 | &#47;synthetic |
| S0379 | F0001 | &#47;independent&#95;reproduction |
| S0380 | F0001 | &#47;all&#95;route&#95;prevention&#95;established |
| S0381 | F0019 | document root (empty JSON Pointer) |
| S0382 | F0057 | &#47;pilots&#47;publication |
| S0383 | F0019 | &#47;recorded&#95;at |
| S0384 | F0019 | &#47;execution |
| S0385 | F0019 | &#47;synthetic |
| S0386 | F0019 | &#47;independent&#95;reproduction |
| S0387 | F0019 | &#47;external&#95;publication |
| S0388 | F0019 | &#47;real&#95;ai&#95;service&#95;called |
| S0389 | F0019 | &#47;all&#95;route&#95;prevention&#95;established |
| S0390 | F0038 | document root (empty JSON Pointer) |
| S0391 | F0057 | &#47;pilots&#47;erasure |
| S0392 | F0038 | &#47;recorded&#95;at |
| S0393 | F0038 | &#47;execution |
| S0394 | F0038 | &#47;synthetic |
| S0395 | F0038 | &#47;independent&#95;reproduction |
| S0396 | F0038 | &#47;remote&#95;provider&#95;used |
| S0397 | F0038 | &#47;universal&#95;erasure |
| S0398 | F0038 | &#47;raw&#95;object&#95;content&#95;exported |
| S0399 | F0001 | &#47;results&#47;0&#47;actual |
| S0400 | F0001 | &#47;results&#47;0&#47;differences |
| S0401 | F0002 | &#47;actual&#47;accepted&#95;count |
| S0402 | F0002 | &#47;actual&#47;gateway&#95;attempts |
| S0403 | F0002 | &#47;actual&#47;handler&#95;calls |
| S0404 | F0002 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0405 | F0002 | &#47;actual&#47;states |
| S0406 | F0002 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0407 | F0002 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0408 | F0002 | &#47;reports&#47;0&#47;attempted |
| S0409 | F0002 | &#47;reports&#47;0&#47;reason |
| S0410 | F0002 | &#47;reports&#47;0&#47;journal&#95;state |
| S0411 | F0002 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0412 | F0002 | &#47;reports&#47;0&#47;byte&#95;length |
| S0413 | F0002 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted |
| S0414 | F0002 | &#47;reports&#47;0&#47;transport&#95;observation&#47;body&#95;send&#95;completed |
| S0415 | F0002 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted&#95;at |
| S0416 | F0002 | &#47;reports&#47;0&#47;transport&#95;observation&#47;dispatched&#95;at |
| S0417 | F0002 | &#47;reports&#47;0&#47;transport&#95;observation&#47;status |
| S0418 | F0002 | &#47;reports&#47;0&#47;receipt&#47;body&#47;kind |
| S0419 | F0002 | &#47;reports&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S0420 | F0002 | &#47;reports&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S0421 | F0002 | &#47;reports&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S0422 | F0002 | &#47;reports&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S0423 | F0002 | &#47;reports&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S0424 | F0002 | &#47;reports&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S0425 | F0002 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;kind |
| S0426 | F0002 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S0427 | F0002 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S0428 | F0002 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S0429 | F0002 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S0430 | F0002 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S0431 | F0002 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S0432 | F0002 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0433 | F0002 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0434 | F0002 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0435 | F0002 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0436 | F0002 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0437 | F0002 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;evidence&#95;integrity |
| S0438 | F0002 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;assessments |
| S0439 | F0002 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;findings |
| S0440 | F0002 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0441 | F0002 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0442 | F0002 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0443 | F0002 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0444 | F0001 | &#47;results&#47;1&#47;actual |
| S0445 | F0001 | &#47;results&#47;1&#47;differences |
| S0446 | F0003 | &#47;actual&#47;accepted&#95;count |
| S0447 | F0003 | &#47;actual&#47;gateway&#95;attempts |
| S0448 | F0003 | &#47;actual&#47;handler&#95;calls |
| S0449 | F0003 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0450 | F0003 | &#47;actual&#47;states |
| S0451 | F0003 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0452 | F0003 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0453 | F0003 | &#47;reports&#47;0&#47;state |
| S0454 | F0003 | &#47;reports&#47;0&#47;attempted |
| S0455 | F0003 | &#47;reports&#47;0&#47;reason |
| S0456 | F0003 | &#47;reports&#47;0&#47;journal&#95;state |
| S0457 | F0003 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0458 | F0003 | &#47;reports&#47;0&#47;byte&#95;length |
| S0459 | F0003 | &#47;reports&#47;0&#47;transport&#95;observation |
| S0460 | F0003 | &#47;reports&#47;0&#47;receipt |
| S0461 | F0003 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0462 | F0003 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0463 | F0003 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0464 | F0003 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0465 | F0003 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0466 | F0003 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0467 | F0003 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0468 | F0003 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0469 | F0003 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0470 | F0001 | &#47;results&#47;2&#47;actual |
| S0471 | F0001 | &#47;results&#47;2&#47;differences |
| S0472 | F0004 | &#47;actual&#47;accepted&#95;count |
| S0473 | F0004 | &#47;actual&#47;gateway&#95;attempts |
| S0474 | F0004 | &#47;actual&#47;handler&#95;calls |
| S0475 | F0004 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0476 | F0004 | &#47;actual&#47;states |
| S0477 | F0004 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0478 | F0004 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0479 | F0004 | &#47;reports&#47;0&#47;state |
| S0480 | F0004 | &#47;reports&#47;0&#47;attempted |
| S0481 | F0004 | &#47;reports&#47;0&#47;reason |
| S0482 | F0004 | &#47;reports&#47;0&#47;journal&#95;state |
| S0483 | F0004 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0484 | F0004 | &#47;reports&#47;0&#47;byte&#95;length |
| S0485 | F0004 | &#47;reports&#47;0&#47;transport&#95;observation |
| S0486 | F0004 | &#47;reports&#47;0&#47;receipt |
| S0487 | F0004 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0488 | F0004 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0489 | F0004 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0490 | F0004 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0491 | F0004 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0492 | F0004 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0493 | F0004 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0494 | F0004 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0495 | F0004 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0496 | F0001 | &#47;results&#47;3&#47;actual |
| S0497 | F0001 | &#47;results&#47;3&#47;differences |
| S0498 | F0005 | &#47;actual&#47;accepted&#95;count |
| S0499 | F0005 | &#47;actual&#47;gateway&#95;attempts |
| S0500 | F0005 | &#47;actual&#47;handler&#95;calls |
| S0501 | F0005 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0502 | F0005 | &#47;actual&#47;states |
| S0503 | F0005 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0504 | F0005 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0505 | F0005 | &#47;reports&#47;0&#47;state |
| S0506 | F0005 | &#47;reports&#47;0&#47;attempted |
| S0507 | F0005 | &#47;reports&#47;0&#47;reason |
| S0508 | F0005 | &#47;reports&#47;0&#47;journal&#95;state |
| S0509 | F0005 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0510 | F0005 | &#47;reports&#47;0&#47;byte&#95;length |
| S0511 | F0005 | &#47;reports&#47;0&#47;transport&#95;observation |
| S0512 | F0005 | &#47;reports&#47;0&#47;receipt |
| S0513 | F0005 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0514 | F0005 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0515 | F0005 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0516 | F0005 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0517 | F0005 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0518 | F0005 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0519 | F0005 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0520 | F0005 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0521 | F0005 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0522 | F0001 | &#47;results&#47;4&#47;actual |
| S0523 | F0001 | &#47;results&#47;4&#47;differences |
| S0524 | F0006 | &#47;actual&#47;accepted&#95;count |
| S0525 | F0006 | &#47;actual&#47;gateway&#95;attempts |
| S0526 | F0006 | &#47;actual&#47;handler&#95;calls |
| S0527 | F0006 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0528 | F0006 | &#47;actual&#47;states |
| S0529 | F0006 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0530 | F0006 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0531 | F0006 | &#47;reports&#47;0&#47;state |
| S0532 | F0006 | &#47;reports&#47;0&#47;attempted |
| S0533 | F0006 | &#47;reports&#47;0&#47;reason |
| S0534 | F0006 | &#47;reports&#47;0&#47;journal&#95;state |
| S0535 | F0006 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0536 | F0006 | &#47;reports&#47;0&#47;byte&#95;length |
| S0537 | F0006 | &#47;reports&#47;0&#47;transport&#95;observation |
| S0538 | F0006 | &#47;reports&#47;0&#47;receipt |
| S0539 | F0006 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0540 | F0006 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0541 | F0006 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0542 | F0006 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0543 | F0006 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0544 | F0006 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0545 | F0006 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0546 | F0006 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0547 | F0006 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0548 | F0001 | &#47;results&#47;5&#47;actual |
| S0549 | F0001 | &#47;results&#47;5&#47;differences |
| S0550 | F0007 | &#47;actual&#47;accepted&#95;count |
| S0551 | F0007 | &#47;actual&#47;gateway&#95;attempts |
| S0552 | F0007 | &#47;actual&#47;handler&#95;calls |
| S0553 | F0007 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0554 | F0007 | &#47;actual&#47;states |
| S0555 | F0007 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0556 | F0007 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0557 | F0007 | &#47;reports&#47;0&#47;state |
| S0558 | F0007 | &#47;reports&#47;0&#47;attempted |
| S0559 | F0007 | &#47;reports&#47;0&#47;reason |
| S0560 | F0007 | &#47;reports&#47;0&#47;journal&#95;state |
| S0561 | F0007 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0562 | F0007 | &#47;reports&#47;0&#47;byte&#95;length |
| S0563 | F0007 | &#47;reports&#47;0&#47;transport&#95;observation |
| S0564 | F0007 | &#47;reports&#47;0&#47;receipt |
| S0565 | F0007 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0566 | F0007 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0567 | F0007 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0568 | F0007 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0569 | F0007 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0570 | F0007 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0571 | F0007 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0572 | F0007 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0573 | F0007 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0574 | F0001 | &#47;results&#47;6&#47;actual |
| S0575 | F0001 | &#47;results&#47;6&#47;differences |
| S0576 | F0008 | &#47;actual&#47;accepted&#95;count |
| S0577 | F0008 | &#47;actual&#47;gateway&#95;attempts |
| S0578 | F0008 | &#47;actual&#47;handler&#95;calls |
| S0579 | F0008 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0580 | F0008 | &#47;actual&#47;states |
| S0581 | F0008 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0582 | F0008 | &#47;reports&#47;0&#47;attempted |
| S0583 | F0008 | &#47;reports&#47;0&#47;reason |
| S0584 | F0008 | &#47;reports&#47;0&#47;journal&#95;state |
| S0585 | F0008 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0586 | F0008 | &#47;reports&#47;0&#47;byte&#95;length |
| S0587 | F0008 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted |
| S0588 | F0008 | &#47;reports&#47;0&#47;transport&#95;observation&#47;body&#95;send&#95;completed |
| S0589 | F0008 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted&#95;at |
| S0590 | F0008 | &#47;reports&#47;0&#47;transport&#95;observation&#47;dispatched&#95;at |
| S0591 | F0008 | &#47;reports&#47;0&#47;transport&#95;observation&#47;status |
| S0592 | F0008 | &#47;reports&#47;1&#47;state |
| S0593 | F0008 | &#47;reports&#47;1&#47;attempted |
| S0594 | F0008 | &#47;reports&#47;1&#47;reason |
| S0595 | F0008 | &#47;reports&#47;1&#47;journal&#95;state |
| S0596 | F0008 | &#47;reports&#47;1&#47;payload&#95;sha256 |
| S0597 | F0008 | &#47;reports&#47;1&#47;byte&#95;length |
| S0598 | F0008 | &#47;reports&#47;1&#47;transport&#95;observation |
| S0599 | F0008 | &#47;reports&#47;1&#47;receipt |
| S0600 | F0008 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;kind |
| S0601 | F0008 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S0602 | F0008 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S0603 | F0008 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S0604 | F0008 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S0605 | F0008 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S0606 | F0008 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S0607 | F0008 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0608 | F0008 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0609 | F0008 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0610 | F0008 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0611 | F0008 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0612 | F0008 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;evidence&#95;integrity |
| S0613 | F0008 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;assessments |
| S0614 | F0008 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;findings |
| S0615 | F0008 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0616 | F0008 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0617 | F0008 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0618 | F0008 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0619 | F0008 | &#47;reports&#47;1&#47;preflight&#95;assessment |
| S0620 | F0008 | &#47;reports&#47;1&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0621 | F0008 | &#47;reports&#47;1&#47;preflight&#95;assessment&#47;assessments |
| S0622 | F0008 | &#47;reports&#47;1&#47;preflight&#95;assessment&#47;findings |
| S0623 | F0008 | &#47;reports&#47;1&#47;final&#95;gate&#95;assessment |
| S0624 | F0008 | &#47;reports&#47;1&#47;postflight&#95;assessment |
| S0625 | F0008 | &#47;reports&#47;1&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0626 | F0008 | &#47;reports&#47;1&#47;postflight&#95;assessment&#47;assessments |
| S0627 | F0008 | &#47;reports&#47;1&#47;postflight&#95;assessment&#47;findings |
| S0628 | F0001 | &#47;results&#47;7&#47;actual |
| S0629 | F0001 | &#47;results&#47;7&#47;differences |
| S0630 | F0009 | &#47;actual&#47;accepted&#95;count |
| S0631 | F0009 | &#47;actual&#47;gateway&#95;attempts |
| S0632 | F0009 | &#47;actual&#47;handler&#95;calls |
| S0633 | F0009 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0634 | F0009 | &#47;actual&#47;states |
| S0635 | F0009 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0636 | F0009 | &#47;reports&#47;0&#47;attempted |
| S0637 | F0009 | &#47;reports&#47;0&#47;reason |
| S0638 | F0009 | &#47;reports&#47;0&#47;journal&#95;state |
| S0639 | F0009 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0640 | F0009 | &#47;reports&#47;0&#47;byte&#95;length |
| S0641 | F0009 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted |
| S0642 | F0009 | &#47;reports&#47;0&#47;transport&#95;observation&#47;body&#95;send&#95;completed |
| S0643 | F0009 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted&#95;at |
| S0644 | F0009 | &#47;reports&#47;0&#47;transport&#95;observation&#47;dispatched&#95;at |
| S0645 | F0009 | &#47;reports&#47;0&#47;transport&#95;observation&#47;status |
| S0646 | F0009 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;kind |
| S0647 | F0009 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S0648 | F0009 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S0649 | F0009 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S0650 | F0009 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S0651 | F0009 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S0652 | F0009 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S0653 | F0009 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0654 | F0009 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0655 | F0009 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0656 | F0009 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0657 | F0009 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0658 | F0009 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;evidence&#95;integrity |
| S0659 | F0009 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;assessments |
| S0660 | F0009 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;findings |
| S0661 | F0009 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0662 | F0009 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0663 | F0009 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0664 | F0009 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0665 | F0001 | &#47;results&#47;8&#47;actual |
| S0666 | F0001 | &#47;results&#47;8&#47;differences |
| S0667 | F0010 | &#47;actual&#47;accepted&#95;count |
| S0668 | F0010 | &#47;actual&#47;gateway&#95;attempts |
| S0669 | F0010 | &#47;actual&#47;handler&#95;calls |
| S0670 | F0010 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0671 | F0010 | &#47;actual&#47;source&#95;mutated&#95;after&#95;capture |
| S0672 | F0010 | &#47;actual&#47;states |
| S0673 | F0010 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0674 | F0010 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0675 | F0010 | &#47;reports&#47;0&#47;attempted |
| S0676 | F0010 | &#47;reports&#47;0&#47;reason |
| S0677 | F0010 | &#47;reports&#47;0&#47;journal&#95;state |
| S0678 | F0010 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0679 | F0010 | &#47;reports&#47;0&#47;byte&#95;length |
| S0680 | F0010 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted |
| S0681 | F0010 | &#47;reports&#47;0&#47;transport&#95;observation&#47;body&#95;send&#95;completed |
| S0682 | F0010 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted&#95;at |
| S0683 | F0010 | &#47;reports&#47;0&#47;transport&#95;observation&#47;dispatched&#95;at |
| S0684 | F0010 | &#47;reports&#47;0&#47;transport&#95;observation&#47;status |
| S0685 | F0010 | &#47;reports&#47;0&#47;receipt&#47;body&#47;kind |
| S0686 | F0010 | &#47;reports&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S0687 | F0010 | &#47;reports&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S0688 | F0010 | &#47;reports&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S0689 | F0010 | &#47;reports&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S0690 | F0010 | &#47;reports&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S0691 | F0010 | &#47;reports&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S0692 | F0010 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;kind |
| S0693 | F0010 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S0694 | F0010 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S0695 | F0010 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S0696 | F0010 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S0697 | F0010 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S0698 | F0010 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S0699 | F0010 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0700 | F0010 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0701 | F0010 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0702 | F0010 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0703 | F0010 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0704 | F0010 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;evidence&#95;integrity |
| S0705 | F0010 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;assessments |
| S0706 | F0010 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;findings |
| S0707 | F0010 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0708 | F0010 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0709 | F0010 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0710 | F0010 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0711 | F0001 | &#47;results&#47;9&#47;actual |
| S0712 | F0001 | &#47;results&#47;9&#47;differences |
| S0713 | F0011 | &#47;actual&#47;accepted&#95;count |
| S0714 | F0011 | &#47;actual&#47;admission&#95;allowed |
| S0715 | F0011 | &#47;actual&#47;gateway&#95;attempts |
| S0716 | F0011 | &#47;actual&#47;handler&#95;calls |
| S0717 | F0011 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0718 | F0011 | &#47;actual&#47;states |
| S0719 | F0011 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0720 | F0011 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0721 | F0011 | &#47;reports&#47;0&#47;state |
| S0722 | F0011 | &#47;reports&#47;0&#47;reason |
| S0723 | F0011 | &#47;reports&#47;0&#47;journal&#95;state |
| S0724 | F0011 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0725 | F0011 | &#47;reports&#47;0&#47;byte&#95;length |
| S0726 | F0011 | &#47;reports&#47;0&#47;transport&#95;observation |
| S0727 | F0011 | &#47;reports&#47;0&#47;receipt |
| S0728 | F0011 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0729 | F0011 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0730 | F0011 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0731 | F0011 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0732 | F0011 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0733 | F0011 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;evidence&#95;integrity |
| S0734 | F0011 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;assessments |
| S0735 | F0011 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;findings |
| S0736 | F0011 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0737 | F0011 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0738 | F0011 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0739 | F0011 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0740 | F0001 | &#47;results&#47;10&#47;actual |
| S0741 | F0001 | &#47;results&#47;10&#47;differences |
| S0742 | F0012 | &#47;actual&#47;accepted&#95;count |
| S0743 | F0012 | &#47;actual&#47;gateway&#95;attempts |
| S0744 | F0012 | &#47;actual&#47;handler&#95;calls |
| S0745 | F0012 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0746 | F0012 | &#47;actual&#47;states |
| S0747 | F0012 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0748 | F0012 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0749 | F0012 | &#47;reports&#47;0&#47;attempted |
| S0750 | F0012 | &#47;reports&#47;0&#47;reason |
| S0751 | F0012 | &#47;reports&#47;0&#47;journal&#95;state |
| S0752 | F0012 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0753 | F0012 | &#47;reports&#47;0&#47;byte&#95;length |
| S0754 | F0012 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted |
| S0755 | F0012 | &#47;reports&#47;0&#47;transport&#95;observation&#47;body&#95;send&#95;completed |
| S0756 | F0012 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted&#95;at |
| S0757 | F0012 | &#47;reports&#47;0&#47;transport&#95;observation&#47;dispatched&#95;at |
| S0758 | F0012 | &#47;reports&#47;0&#47;transport&#95;observation&#47;status |
| S0759 | F0012 | &#47;reports&#47;0&#47;receipt&#47;body&#47;kind |
| S0760 | F0012 | &#47;reports&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S0761 | F0012 | &#47;reports&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S0762 | F0012 | &#47;reports&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S0763 | F0012 | &#47;reports&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S0764 | F0012 | &#47;reports&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S0765 | F0012 | &#47;reports&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S0766 | F0012 | &#47;reports&#47;1&#47;state |
| S0767 | F0012 | &#47;reports&#47;1&#47;attempted |
| S0768 | F0012 | &#47;reports&#47;1&#47;reason |
| S0769 | F0012 | &#47;reports&#47;1&#47;journal&#95;state |
| S0770 | F0012 | &#47;reports&#47;1&#47;payload&#95;sha256 |
| S0771 | F0012 | &#47;reports&#47;1&#47;byte&#95;length |
| S0772 | F0012 | &#47;reports&#47;1&#47;transport&#95;observation |
| S0773 | F0012 | &#47;reports&#47;1&#47;receipt |
| S0774 | F0012 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;kind |
| S0775 | F0012 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S0776 | F0012 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S0777 | F0012 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S0778 | F0012 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S0779 | F0012 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S0780 | F0012 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S0781 | F0012 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0782 | F0012 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0783 | F0012 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0784 | F0012 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0785 | F0012 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0786 | F0012 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;evidence&#95;integrity |
| S0787 | F0012 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;assessments |
| S0788 | F0012 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;findings |
| S0789 | F0012 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0790 | F0012 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0791 | F0012 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0792 | F0012 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0793 | F0012 | &#47;reports&#47;1&#47;preflight&#95;assessment |
| S0794 | F0012 | &#47;reports&#47;1&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0795 | F0012 | &#47;reports&#47;1&#47;preflight&#95;assessment&#47;assessments |
| S0796 | F0012 | &#47;reports&#47;1&#47;preflight&#95;assessment&#47;findings |
| S0797 | F0012 | &#47;reports&#47;1&#47;final&#95;gate&#95;assessment |
| S0798 | F0012 | &#47;reports&#47;1&#47;postflight&#95;assessment |
| S0799 | F0012 | &#47;reports&#47;1&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0800 | F0012 | &#47;reports&#47;1&#47;postflight&#95;assessment&#47;assessments |
| S0801 | F0012 | &#47;reports&#47;1&#47;postflight&#95;assessment&#47;findings |
| S0802 | F0001 | &#47;results&#47;11&#47;actual |
| S0803 | F0001 | &#47;results&#47;11&#47;differences |
| S0804 | F0013 | &#47;actual&#47;accepted&#95;count |
| S0805 | F0013 | &#47;actual&#47;gateway&#95;attempts |
| S0806 | F0013 | &#47;actual&#47;handler&#95;calls |
| S0807 | F0013 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0808 | F0013 | &#47;actual&#47;states |
| S0809 | F0013 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0810 | F0013 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0811 | F0013 | &#47;reports&#47;0&#47;attempted |
| S0812 | F0013 | &#47;reports&#47;0&#47;reason |
| S0813 | F0013 | &#47;reports&#47;0&#47;journal&#95;state |
| S0814 | F0013 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0815 | F0013 | &#47;reports&#47;0&#47;byte&#95;length |
| S0816 | F0013 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted |
| S0817 | F0013 | &#47;reports&#47;0&#47;transport&#95;observation&#47;body&#95;send&#95;completed |
| S0818 | F0013 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted&#95;at |
| S0819 | F0013 | &#47;reports&#47;0&#47;transport&#95;observation&#47;dispatched&#95;at |
| S0820 | F0013 | &#47;reports&#47;0&#47;transport&#95;observation&#47;status |
| S0821 | F0013 | &#47;reports&#47;0&#47;receipt&#47;body&#47;kind |
| S0822 | F0013 | &#47;reports&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S0823 | F0013 | &#47;reports&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S0824 | F0013 | &#47;reports&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S0825 | F0013 | &#47;reports&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S0826 | F0013 | &#47;reports&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S0827 | F0013 | &#47;reports&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S0828 | F0013 | &#47;reports&#47;1&#47;state |
| S0829 | F0013 | &#47;reports&#47;1&#47;attempted |
| S0830 | F0013 | &#47;reports&#47;1&#47;reason |
| S0831 | F0013 | &#47;reports&#47;1&#47;journal&#95;state |
| S0832 | F0013 | &#47;reports&#47;1&#47;payload&#95;sha256 |
| S0833 | F0013 | &#47;reports&#47;1&#47;byte&#95;length |
| S0834 | F0013 | &#47;reports&#47;1&#47;transport&#95;observation |
| S0835 | F0013 | &#47;reports&#47;1&#47;receipt |
| S0836 | F0013 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;kind |
| S0837 | F0013 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S0838 | F0013 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S0839 | F0013 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S0840 | F0013 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S0841 | F0013 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S0842 | F0013 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S0843 | F0013 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0844 | F0013 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0845 | F0013 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0846 | F0013 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0847 | F0013 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0848 | F0013 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;evidence&#95;integrity |
| S0849 | F0013 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;assessments |
| S0850 | F0013 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;findings |
| S0851 | F0013 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0852 | F0013 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0853 | F0013 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0854 | F0013 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0855 | F0013 | &#47;reports&#47;1&#47;preflight&#95;assessment |
| S0856 | F0013 | &#47;reports&#47;1&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0857 | F0013 | &#47;reports&#47;1&#47;preflight&#95;assessment&#47;assessments |
| S0858 | F0013 | &#47;reports&#47;1&#47;preflight&#95;assessment&#47;findings |
| S0859 | F0013 | &#47;reports&#47;1&#47;final&#95;gate&#95;assessment |
| S0860 | F0013 | &#47;reports&#47;1&#47;postflight&#95;assessment |
| S0861 | F0013 | &#47;reports&#47;1&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0862 | F0013 | &#47;reports&#47;1&#47;postflight&#95;assessment&#47;assessments |
| S0863 | F0013 | &#47;reports&#47;1&#47;postflight&#95;assessment&#47;findings |
| S0864 | F0001 | &#47;results&#47;12&#47;actual |
| S0865 | F0001 | &#47;results&#47;12&#47;differences |
| S0866 | F0014 | &#47;actual&#47;accepted&#95;count |
| S0867 | F0014 | &#47;actual&#47;gateway&#95;attempts |
| S0868 | F0014 | &#47;actual&#47;handler&#95;calls |
| S0869 | F0014 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0870 | F0014 | &#47;actual&#47;states |
| S0871 | F0014 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0872 | F0014 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0873 | F0014 | &#47;reports&#47;0&#47;state |
| S0874 | F0014 | &#47;reports&#47;0&#47;attempted |
| S0875 | F0014 | &#47;reports&#47;0&#47;reason |
| S0876 | F0014 | &#47;reports&#47;0&#47;journal&#95;state |
| S0877 | F0014 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0878 | F0014 | &#47;reports&#47;0&#47;byte&#95;length |
| S0879 | F0014 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted |
| S0880 | F0014 | &#47;reports&#47;0&#47;transport&#95;observation&#47;body&#95;send&#95;completed |
| S0881 | F0014 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted&#95;at |
| S0882 | F0014 | &#47;reports&#47;0&#47;transport&#95;observation&#47;dispatched&#95;at |
| S0883 | F0014 | &#47;reports&#47;0&#47;transport&#95;observation&#47;status |
| S0884 | F0014 | &#47;reports&#47;0&#47;receipt |
| S0885 | F0014 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0886 | F0014 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0887 | F0014 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0888 | F0014 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0889 | F0014 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0890 | F0014 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;evidence&#95;integrity |
| S0891 | F0014 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;assessments |
| S0892 | F0014 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;findings |
| S0893 | F0014 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0894 | F0014 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0895 | F0014 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0896 | F0014 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0897 | F0001 | &#47;results&#47;13&#47;actual |
| S0898 | F0001 | &#47;results&#47;13&#47;differences |
| S0899 | F0015 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0900 | F0015 | &#47;actual&#47;states |
| S0901 | F0015 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0902 | F0015 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0903 | F0015 | &#47;reports&#47;0&#47;attempted |
| S0904 | F0015 | &#47;reports&#47;0&#47;reason |
| S0905 | F0015 | &#47;reports&#47;0&#47;journal&#95;state |
| S0906 | F0015 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0907 | F0015 | &#47;reports&#47;0&#47;byte&#95;length |
| S0908 | F0015 | &#47;reports&#47;0&#47;transport&#95;observation |
| S0909 | F0015 | &#47;reports&#47;0&#47;receipt |
| S0910 | F0015 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;kind |
| S0911 | F0015 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S0912 | F0015 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S0913 | F0015 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S0914 | F0015 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S0915 | F0015 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S0916 | F0015 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S0917 | F0015 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0918 | F0015 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0919 | F0015 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0920 | F0015 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0921 | F0015 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0922 | F0015 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0923 | F0015 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0924 | F0015 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0925 | F0015 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0926 | F0001 | &#47;results&#47;14&#47;actual |
| S0927 | F0001 | &#47;results&#47;14&#47;differences |
| S0928 | F0016 | &#47;actual&#47;accepted&#95;count |
| S0929 | F0016 | &#47;actual&#47;gateway&#95;attempts |
| S0930 | F0016 | &#47;actual&#47;handler&#95;calls |
| S0931 | F0016 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0932 | F0016 | &#47;actual&#47;states |
| S0933 | F0016 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0934 | F0016 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S0935 | F0016 | &#47;reports&#47;0&#47;attempted |
| S0936 | F0016 | &#47;reports&#47;0&#47;reason |
| S0937 | F0016 | &#47;reports&#47;0&#47;journal&#95;state |
| S0938 | F0016 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S0939 | F0016 | &#47;reports&#47;0&#47;byte&#95;length |
| S0940 | F0016 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted |
| S0941 | F0016 | &#47;reports&#47;0&#47;transport&#95;observation&#47;body&#95;send&#95;completed |
| S0942 | F0016 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted&#95;at |
| S0943 | F0016 | &#47;reports&#47;0&#47;transport&#95;observation&#47;dispatched&#95;at |
| S0944 | F0016 | &#47;reports&#47;0&#47;transport&#95;observation&#47;status |
| S0945 | F0016 | &#47;reports&#47;0&#47;receipt&#47;body&#47;kind |
| S0946 | F0016 | &#47;reports&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S0947 | F0016 | &#47;reports&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S0948 | F0016 | &#47;reports&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S0949 | F0016 | &#47;reports&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S0950 | F0016 | &#47;reports&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S0951 | F0016 | &#47;reports&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S0952 | F0016 | &#47;reports&#47;1&#47;state |
| S0953 | F0016 | &#47;reports&#47;1&#47;attempted |
| S0954 | F0016 | &#47;reports&#47;1&#47;reason |
| S0955 | F0016 | &#47;reports&#47;1&#47;journal&#95;state |
| S0956 | F0016 | &#47;reports&#47;1&#47;payload&#95;sha256 |
| S0957 | F0016 | &#47;reports&#47;1&#47;byte&#95;length |
| S0958 | F0016 | &#47;reports&#47;1&#47;transport&#95;observation |
| S0959 | F0016 | &#47;reports&#47;1&#47;receipt |
| S0960 | F0016 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;kind |
| S0961 | F0016 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S0962 | F0016 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S0963 | F0016 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S0964 | F0016 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S0965 | F0016 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S0966 | F0016 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S0967 | F0016 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S0968 | F0016 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0969 | F0016 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S0970 | F0016 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S0971 | F0016 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S0972 | F0016 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;evidence&#95;integrity |
| S0973 | F0016 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;assessments |
| S0974 | F0016 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;findings |
| S0975 | F0016 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S0976 | F0016 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0977 | F0016 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S0978 | F0016 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S0979 | F0016 | &#47;reports&#47;1&#47;preflight&#95;assessment |
| S0980 | F0016 | &#47;reports&#47;1&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S0981 | F0016 | &#47;reports&#47;1&#47;preflight&#95;assessment&#47;assessments |
| S0982 | F0016 | &#47;reports&#47;1&#47;preflight&#95;assessment&#47;findings |
| S0983 | F0016 | &#47;reports&#47;1&#47;final&#95;gate&#95;assessment |
| S0984 | F0016 | &#47;reports&#47;1&#47;postflight&#95;assessment |
| S0985 | F0016 | &#47;reports&#47;1&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S0986 | F0016 | &#47;reports&#47;1&#47;postflight&#95;assessment&#47;assessments |
| S0987 | F0016 | &#47;reports&#47;1&#47;postflight&#95;assessment&#47;findings |
| S0988 | F0001 | &#47;results&#47;15&#47;actual |
| S0989 | F0001 | &#47;results&#47;15&#47;differences |
| S0990 | F0017 | &#47;actual&#47;accepted&#95;count |
| S0991 | F0017 | &#47;actual&#47;gateway&#95;attempts |
| S0992 | F0017 | &#47;actual&#47;handler&#95;calls |
| S0993 | F0017 | &#47;actual&#47;received&#95;bytes&#95;match |
| S0994 | F0017 | &#47;actual&#47;states |
| S0995 | F0017 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S0996 | F0017 | &#47;reports&#47;0&#47;attempted |
| S0997 | F0017 | &#47;reports&#47;0&#47;reason |
| S0998 | F0017 | &#47;reports&#47;0&#47;journal&#95;state |
| S0999 | F0017 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S1000 | F0017 | &#47;reports&#47;0&#47;byte&#95;length |
| S1001 | F0017 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted |
| S1002 | F0017 | &#47;reports&#47;0&#47;transport&#95;observation&#47;body&#95;send&#95;completed |
| S1003 | F0017 | &#47;reports&#47;0&#47;transport&#95;observation&#47;attempted&#95;at |
| S1004 | F0017 | &#47;reports&#47;0&#47;transport&#95;observation&#47;dispatched&#95;at |
| S1005 | F0017 | &#47;reports&#47;0&#47;transport&#95;observation&#47;status |
| S1006 | F0017 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;kind |
| S1007 | F0017 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;request&#95;id |
| S1008 | F0017 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;subject&#95;sha256 |
| S1009 | F0017 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;payload&#95;sha256 |
| S1010 | F0017 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;byte&#95;length |
| S1011 | F0017 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;received&#95;at |
| S1012 | F0017 | &#47;receiver&#95;snapshot&#47;rows&#47;0&#47;receipt&#47;body&#47;receipt&#95;id |
| S1013 | F0017 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S1014 | F0017 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S1015 | F0017 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S1016 | F0017 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S1017 | F0017 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S1018 | F0017 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;evidence&#95;integrity |
| S1019 | F0017 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;assessments |
| S1020 | F0017 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment&#47;findings |
| S1021 | F0017 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S1022 | F0017 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S1023 | F0017 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S1024 | F0017 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S1025 | F0001 | &#47;results&#47;16&#47;actual |
| S1026 | F0001 | &#47;results&#47;16&#47;differences |
| S1027 | F0018 | &#47;actual&#47;accepted&#95;count |
| S1028 | F0018 | &#47;actual&#47;handler&#95;calls |
| S1029 | F0018 | &#47;actual&#47;received&#95;bytes&#95;match |
| S1030 | F0018 | &#47;actual&#47;states |
| S1031 | F0018 | &#47;receiver&#95;snapshot&#47;handler&#95;calls |
| S1032 | F0018 | &#47;receiver&#95;snapshot&#47;accepted&#95;count |
| S1033 | F0018 | &#47;reports&#47;0&#47;state |
| S1034 | F0018 | &#47;reports&#47;0&#47;attempted |
| S1035 | F0018 | &#47;reports&#47;0&#47;reason |
| S1036 | F0018 | &#47;reports&#47;0&#47;payload&#95;sha256 |
| S1037 | F0018 | &#47;reports&#47;0&#47;byte&#95;length |
| S1038 | F0018 | &#47;reports&#47;0&#47;transport&#95;observation |
| S1039 | F0018 | &#47;reports&#47;0&#47;receipt |
| S1040 | F0018 | &#47;reports&#47;0&#47;preflight&#95;assessment |
| S1041 | F0018 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;evidence&#95;integrity |
| S1042 | F0018 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;assessments |
| S1043 | F0018 | &#47;reports&#47;0&#47;preflight&#95;assessment&#47;findings |
| S1044 | F0018 | &#47;reports&#47;0&#47;final&#95;gate&#95;assessment |
| S1045 | F0018 | &#47;reports&#47;0&#47;postflight&#95;assessment |
| S1046 | F0018 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;evidence&#95;integrity |
| S1047 | F0018 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;assessments |
| S1048 | F0018 | &#47;reports&#47;0&#47;postflight&#95;assessment&#47;findings |
| S1049 | F0019 | &#47;results&#47;0&#47;actual |
| S1050 | F0019 | &#47;results&#47;0&#47;differences |
| S1051 | F0020 | &#47;actual&#47;publication&#95;attempts |
| S1052 | F0020 | &#47;actual&#47;states |
| S1053 | F0020 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1054 | F0020 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1055 | F0020 | &#47;actual&#47;visible&#95;count |
| S1056 | F0020 | &#47;sort&#95;states |
| S1057 | F0020 | &#47;records&#47;0&#47;report&#47;state |
| S1058 | F0020 | &#47;records&#47;0&#47;report&#47;attempted |
| S1059 | F0020 | &#47;records&#47;0&#47;report&#47;reason |
| S1060 | F0020 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1061 | F0020 | &#47;records&#47;0&#47;report&#47;publication&#47;journal&#95;state |
| S1062 | F0020 | &#47;records&#47;0&#47;report&#47;publication&#47;visible&#95;name |
| S1063 | F0020 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1064 | F0020 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1065 | F0020 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1066 | F0020 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1067 | F0020 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;at |
| S1068 | F0020 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;authorized&#95;local&#95;export |
| S1069 | F0020 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;reason |
| S1070 | F0020 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;kind |
| S1071 | F0020 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;request&#95;id |
| S1072 | F0020 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;fingerprint |
| S1073 | F0020 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;artifact&#95;sha256 |
| S1074 | F0020 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;disclosure&#95;sha256 |
| S1075 | F0020 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;byte&#95;length |
| S1076 | F0020 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;destination&#95;id |
| S1077 | F0020 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;visible&#95;name |
| S1078 | F0020 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;observed&#95;at |
| S1079 | F0020 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1080 | F0020 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1081 | F0020 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1082 | F0020 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1083 | F0020 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report |
| S1084 | F0020 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1085 | F0020 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1086 | F0020 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;findings |
| S1087 | F0019 | &#47;results&#47;1&#47;actual |
| S1088 | F0019 | &#47;results&#47;1&#47;differences |
| S1089 | F0021 | &#47;actual&#47;publication&#95;attempts |
| S1090 | F0021 | &#47;actual&#47;states |
| S1091 | F0021 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1092 | F0021 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1093 | F0021 | &#47;actual&#47;visible&#95;count |
| S1094 | F0021 | &#47;sort&#95;states |
| S1095 | F0021 | &#47;records&#47;0&#47;report&#47;state |
| S1096 | F0021 | &#47;records&#47;0&#47;report&#47;attempted |
| S1097 | F0021 | &#47;records&#47;0&#47;report&#47;reason |
| S1098 | F0021 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1099 | F0021 | &#47;records&#47;0&#47;report&#47;publication |
| S1100 | F0021 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1101 | F0021 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1102 | F0021 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1103 | F0021 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1104 | F0021 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1105 | F0021 | &#47;records&#47;0&#47;report&#47;final&#95;gate |
| S1106 | F0021 | &#47;records&#47;0&#47;report&#47;receipt |
| S1107 | F0021 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1108 | F0021 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1109 | F0021 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1110 | F0021 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1111 | F0019 | &#47;results&#47;2&#47;actual |
| S1112 | F0019 | &#47;results&#47;2&#47;differences |
| S1113 | F0022 | &#47;actual&#47;publication&#95;attempts |
| S1114 | F0022 | &#47;actual&#47;states |
| S1115 | F0022 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1116 | F0022 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1117 | F0022 | &#47;actual&#47;visible&#95;count |
| S1118 | F0022 | &#47;sort&#95;states |
| S1119 | F0022 | &#47;records&#47;0&#47;report&#47;state |
| S1120 | F0022 | &#47;records&#47;0&#47;report&#47;attempted |
| S1121 | F0022 | &#47;records&#47;0&#47;report&#47;reason |
| S1122 | F0022 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1123 | F0022 | &#47;records&#47;0&#47;report&#47;publication |
| S1124 | F0022 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1125 | F0022 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1126 | F0022 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1127 | F0022 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1128 | F0022 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1129 | F0022 | &#47;records&#47;0&#47;report&#47;final&#95;gate |
| S1130 | F0022 | &#47;records&#47;0&#47;report&#47;receipt |
| S1131 | F0022 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame |
| S1132 | F0019 | &#47;results&#47;3&#47;actual |
| S1133 | F0019 | &#47;results&#47;3&#47;differences |
| S1134 | F0023 | &#47;actual&#47;publication&#95;attempts |
| S1135 | F0023 | &#47;actual&#47;states |
| S1136 | F0023 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1137 | F0023 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1138 | F0023 | &#47;actual&#47;visible&#95;count |
| S1139 | F0023 | &#47;sort&#95;states |
| S1140 | F0023 | &#47;records&#47;0&#47;report&#47;state |
| S1141 | F0023 | &#47;records&#47;0&#47;report&#47;attempted |
| S1142 | F0023 | &#47;records&#47;0&#47;report&#47;reason |
| S1143 | F0023 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1144 | F0023 | &#47;records&#47;0&#47;report&#47;publication |
| S1145 | F0023 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1146 | F0023 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1147 | F0023 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1148 | F0023 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1149 | F0023 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1150 | F0023 | &#47;records&#47;0&#47;report&#47;final&#95;gate |
| S1151 | F0023 | &#47;records&#47;0&#47;report&#47;receipt |
| S1152 | F0023 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame |
| S1153 | F0019 | &#47;results&#47;4&#47;actual |
| S1154 | F0019 | &#47;results&#47;4&#47;differences |
| S1155 | F0024 | &#47;actual&#47;publication&#95;attempts |
| S1156 | F0024 | &#47;actual&#47;states |
| S1157 | F0024 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1158 | F0024 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1159 | F0024 | &#47;actual&#47;visible&#95;count |
| S1160 | F0024 | &#47;sort&#95;states |
| S1161 | F0024 | &#47;records&#47;0&#47;report&#47;state |
| S1162 | F0024 | &#47;records&#47;0&#47;report&#47;attempted |
| S1163 | F0024 | &#47;records&#47;0&#47;report&#47;reason |
| S1164 | F0024 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1165 | F0024 | &#47;records&#47;0&#47;report&#47;publication |
| S1166 | F0024 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1167 | F0024 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1168 | F0024 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1169 | F0024 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1170 | F0024 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1171 | F0024 | &#47;records&#47;0&#47;report&#47;final&#95;gate |
| S1172 | F0024 | &#47;records&#47;0&#47;report&#47;receipt |
| S1173 | F0024 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1174 | F0024 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1175 | F0024 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1176 | F0024 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1177 | F0019 | &#47;results&#47;5&#47;actual |
| S1178 | F0019 | &#47;results&#47;5&#47;differences |
| S1179 | F0025 | &#47;actual&#47;publication&#95;attempts |
| S1180 | F0025 | &#47;actual&#47;states |
| S1181 | F0025 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1182 | F0025 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1183 | F0025 | &#47;actual&#47;visible&#95;count |
| S1184 | F0025 | &#47;sort&#95;states |
| S1185 | F0025 | &#47;records&#47;0&#47;report&#47;state |
| S1186 | F0025 | &#47;records&#47;0&#47;report&#47;attempted |
| S1187 | F0025 | &#47;records&#47;0&#47;report&#47;reason |
| S1188 | F0025 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1189 | F0025 | &#47;records&#47;0&#47;report&#47;publication |
| S1190 | F0025 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1191 | F0025 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1192 | F0025 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1193 | F0025 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1194 | F0025 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1195 | F0025 | &#47;records&#47;0&#47;report&#47;final&#95;gate |
| S1196 | F0025 | &#47;records&#47;0&#47;report&#47;receipt |
| S1197 | F0025 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1198 | F0025 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1199 | F0025 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1200 | F0025 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1201 | F0019 | &#47;results&#47;6&#47;actual |
| S1202 | F0019 | &#47;results&#47;6&#47;differences |
| S1203 | F0026 | &#47;actual&#47;publication&#95;attempts |
| S1204 | F0026 | &#47;actual&#47;states |
| S1205 | F0026 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1206 | F0026 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1207 | F0026 | &#47;actual&#47;visible&#95;count |
| S1208 | F0026 | &#47;sort&#95;states |
| S1209 | F0026 | &#47;records&#47;0&#47;report&#47;state |
| S1210 | F0026 | &#47;records&#47;0&#47;report&#47;attempted |
| S1211 | F0026 | &#47;records&#47;0&#47;report&#47;reason |
| S1212 | F0026 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1213 | F0026 | &#47;records&#47;0&#47;report&#47;publication |
| S1214 | F0026 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1215 | F0026 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1216 | F0026 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1217 | F0026 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1218 | F0026 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1219 | F0026 | &#47;records&#47;0&#47;report&#47;final&#95;gate |
| S1220 | F0026 | &#47;records&#47;0&#47;report&#47;receipt |
| S1221 | F0026 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1222 | F0026 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1223 | F0026 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1224 | F0026 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1225 | F0019 | &#47;results&#47;7&#47;actual |
| S1226 | F0019 | &#47;results&#47;7&#47;differences |
| S1227 | F0027 | &#47;actual&#47;publication&#95;attempts |
| S1228 | F0027 | &#47;actual&#47;states |
| S1229 | F0027 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1230 | F0027 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1231 | F0027 | &#47;actual&#47;visible&#95;count |
| S1232 | F0027 | &#47;sort&#95;states |
| S1233 | F0027 | &#47;records&#47;0&#47;report&#47;state |
| S1234 | F0027 | &#47;records&#47;0&#47;report&#47;reason |
| S1235 | F0027 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1236 | F0027 | &#47;records&#47;0&#47;report&#47;publication&#47;journal&#95;state |
| S1237 | F0027 | &#47;records&#47;0&#47;report&#47;publication&#47;visible&#95;name |
| S1238 | F0027 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1239 | F0027 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1240 | F0027 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1241 | F0027 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1242 | F0027 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;at |
| S1243 | F0027 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;reason |
| S1244 | F0027 | &#47;records&#47;0&#47;report&#47;receipt |
| S1245 | F0027 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1246 | F0027 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1247 | F0027 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1248 | F0027 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1249 | F0027 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report |
| S1250 | F0027 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1251 | F0027 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1252 | F0027 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;findings |
| S1253 | F0019 | &#47;results&#47;8&#47;actual |
| S1254 | F0019 | &#47;results&#47;8&#47;differences |
| S1255 | F0028 | &#47;actual&#47;publication&#95;attempts |
| S1256 | F0028 | &#47;actual&#47;states |
| S1257 | F0028 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1258 | F0028 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1259 | F0028 | &#47;actual&#47;visible&#95;count |
| S1260 | F0028 | &#47;sort&#95;states |
| S1261 | F0028 | &#47;records&#47;0&#47;report&#47;state |
| S1262 | F0028 | &#47;records&#47;0&#47;report&#47;attempted |
| S1263 | F0028 | &#47;records&#47;0&#47;report&#47;reason |
| S1264 | F0028 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1265 | F0028 | &#47;records&#47;0&#47;report&#47;publication&#47;journal&#95;state |
| S1266 | F0028 | &#47;records&#47;0&#47;report&#47;publication&#47;visible&#95;name |
| S1267 | F0028 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1268 | F0028 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1269 | F0028 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1270 | F0028 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1271 | F0028 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;at |
| S1272 | F0028 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;authorized&#95;local&#95;export |
| S1273 | F0028 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;reason |
| S1274 | F0028 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;kind |
| S1275 | F0028 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;request&#95;id |
| S1276 | F0028 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;fingerprint |
| S1277 | F0028 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;artifact&#95;sha256 |
| S1278 | F0028 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;disclosure&#95;sha256 |
| S1279 | F0028 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;byte&#95;length |
| S1280 | F0028 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;destination&#95;id |
| S1281 | F0028 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;visible&#95;name |
| S1282 | F0028 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;observed&#95;at |
| S1283 | F0028 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1284 | F0028 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1285 | F0028 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1286 | F0028 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1287 | F0028 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report |
| S1288 | F0028 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1289 | F0028 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1290 | F0028 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;findings |
| S1291 | F0019 | &#47;results&#47;9&#47;actual |
| S1292 | F0019 | &#47;results&#47;9&#47;differences |
| S1293 | F0029 | &#47;actual&#47;publication&#95;attempts |
| S1294 | F0029 | &#47;actual&#47;states |
| S1295 | F0029 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1296 | F0029 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1297 | F0029 | &#47;actual&#47;visible&#95;count |
| S1298 | F0029 | &#47;sort&#95;states |
| S1299 | F0029 | &#47;records&#47;0&#47;report&#47;state |
| S1300 | F0029 | &#47;records&#47;0&#47;report&#47;attempted |
| S1301 | F0029 | &#47;records&#47;0&#47;report&#47;reason |
| S1302 | F0029 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1303 | F0029 | &#47;records&#47;0&#47;report&#47;publication&#47;journal&#95;state |
| S1304 | F0029 | &#47;records&#47;0&#47;report&#47;publication&#47;visible&#95;name |
| S1305 | F0029 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1306 | F0029 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1307 | F0029 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1308 | F0029 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1309 | F0029 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;at |
| S1310 | F0029 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;authorized&#95;local&#95;export |
| S1311 | F0029 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;reason |
| S1312 | F0029 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;kind |
| S1313 | F0029 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;request&#95;id |
| S1314 | F0029 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;fingerprint |
| S1315 | F0029 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;artifact&#95;sha256 |
| S1316 | F0029 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;disclosure&#95;sha256 |
| S1317 | F0029 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;byte&#95;length |
| S1318 | F0029 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;destination&#95;id |
| S1319 | F0029 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;visible&#95;name |
| S1320 | F0029 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;observed&#95;at |
| S1321 | F0029 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1322 | F0029 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1323 | F0029 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1324 | F0029 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1325 | F0029 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report |
| S1326 | F0029 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1327 | F0029 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1328 | F0029 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;findings |
| S1329 | F0019 | &#47;results&#47;10&#47;actual |
| S1330 | F0019 | &#47;results&#47;10&#47;differences |
| S1331 | F0030 | &#47;actual&#47;publication&#95;attempts |
| S1332 | F0030 | &#47;actual&#47;states |
| S1333 | F0030 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1334 | F0030 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1335 | F0030 | &#47;actual&#47;visible&#95;count |
| S1336 | F0030 | &#47;sort&#95;states |
| S1337 | F0030 | &#47;records&#47;0&#47;report&#47;state |
| S1338 | F0030 | &#47;records&#47;0&#47;report&#47;attempted |
| S1339 | F0030 | &#47;records&#47;0&#47;report&#47;reason |
| S1340 | F0030 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1341 | F0030 | &#47;records&#47;0&#47;report&#47;publication |
| S1342 | F0030 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1343 | F0030 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1344 | F0030 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1345 | F0030 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1346 | F0030 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1347 | F0030 | &#47;records&#47;0&#47;report&#47;final&#95;gate |
| S1348 | F0030 | &#47;records&#47;0&#47;report&#47;receipt |
| S1349 | F0030 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame |
| S1350 | F0019 | &#47;results&#47;11&#47;actual |
| S1351 | F0019 | &#47;results&#47;11&#47;differences |
| S1352 | F0031 | &#47;actual&#47;publication&#95;attempts |
| S1353 | F0031 | &#47;actual&#47;states |
| S1354 | F0031 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1355 | F0031 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1356 | F0031 | &#47;actual&#47;visible&#95;count |
| S1357 | F0031 | &#47;sort&#95;states |
| S1358 | F0031 | &#47;records&#47;0&#47;report&#47;state |
| S1359 | F0031 | &#47;records&#47;0&#47;report&#47;attempted |
| S1360 | F0031 | &#47;records&#47;0&#47;report&#47;reason |
| S1361 | F0031 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1362 | F0031 | &#47;records&#47;0&#47;report&#47;publication |
| S1363 | F0031 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1364 | F0031 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1365 | F0031 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1366 | F0031 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1367 | F0031 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1368 | F0031 | &#47;records&#47;0&#47;report&#47;final&#95;gate |
| S1369 | F0031 | &#47;records&#47;0&#47;report&#47;receipt |
| S1370 | F0031 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1371 | F0031 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1372 | F0031 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1373 | F0031 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1374 | F0019 | &#47;results&#47;12&#47;actual |
| S1375 | F0019 | &#47;results&#47;12&#47;differences |
| S1376 | F0032 | &#47;actual&#47;publication&#95;attempts |
| S1377 | F0032 | &#47;actual&#47;states |
| S1378 | F0032 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1379 | F0032 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1380 | F0032 | &#47;actual&#47;visible&#95;count |
| S1381 | F0032 | &#47;sort&#95;states |
| S1382 | F0032 | &#47;records&#47;0&#47;report&#47;state |
| S1383 | F0032 | &#47;records&#47;0&#47;report&#47;attempted |
| S1384 | F0032 | &#47;records&#47;0&#47;report&#47;reason |
| S1385 | F0032 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1386 | F0032 | &#47;records&#47;0&#47;report&#47;publication&#47;journal&#95;state |
| S1387 | F0032 | &#47;records&#47;0&#47;report&#47;publication&#47;visible&#95;name |
| S1388 | F0032 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1389 | F0032 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1390 | F0032 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1391 | F0032 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1392 | F0032 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;at |
| S1393 | F0032 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;authorized&#95;local&#95;export |
| S1394 | F0032 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;reason |
| S1395 | F0032 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;kind |
| S1396 | F0032 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;request&#95;id |
| S1397 | F0032 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;fingerprint |
| S1398 | F0032 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;artifact&#95;sha256 |
| S1399 | F0032 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;disclosure&#95;sha256 |
| S1400 | F0032 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;byte&#95;length |
| S1401 | F0032 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;destination&#95;id |
| S1402 | F0032 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;visible&#95;name |
| S1403 | F0032 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;observed&#95;at |
| S1404 | F0032 | &#47;records&#47;1&#47;report&#47;state |
| S1405 | F0032 | &#47;records&#47;1&#47;report&#47;attempted |
| S1406 | F0032 | &#47;records&#47;1&#47;report&#47;reason |
| S1407 | F0032 | &#47;records&#47;1&#47;report&#47;post&#95;at |
| S1408 | F0032 | &#47;records&#47;1&#47;report&#47;publication&#47;journal&#95;state |
| S1409 | F0032 | &#47;records&#47;1&#47;report&#47;publication&#47;visible&#95;name |
| S1410 | F0032 | &#47;records&#47;1&#47;candidate&#47;disclosure&#47;activities |
| S1411 | F0032 | &#47;records&#47;1&#47;candidate&#47;disclosure&#47;scope |
| S1412 | F0032 | &#47;records&#47;1&#47;report&#47;preflight&#47;at |
| S1413 | F0032 | &#47;records&#47;1&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1414 | F0032 | &#47;records&#47;1&#47;report&#47;preflight&#47;reason |
| S1415 | F0032 | &#47;records&#47;1&#47;report&#47;final&#95;gate |
| S1416 | F0032 | &#47;records&#47;1&#47;report&#47;receipt |
| S1417 | F0032 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1418 | F0032 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1419 | F0032 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1420 | F0032 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1421 | F0032 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report |
| S1422 | F0032 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1423 | F0032 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1424 | F0032 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;findings |
| S1425 | F0032 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1426 | F0032 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1427 | F0032 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1428 | F0032 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1429 | F0019 | &#47;results&#47;13&#47;actual |
| S1430 | F0019 | &#47;results&#47;13&#47;differences |
| S1431 | F0033 | &#47;actual&#47;publication&#95;attempts |
| S1432 | F0033 | &#47;actual&#47;states |
| S1433 | F0033 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1434 | F0033 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1435 | F0033 | &#47;actual&#47;visible&#95;count |
| S1436 | F0033 | &#47;sort&#95;states |
| S1437 | F0033 | &#47;records&#47;0&#47;report&#47;attempted |
| S1438 | F0033 | &#47;records&#47;0&#47;report&#47;reason |
| S1439 | F0033 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1440 | F0033 | &#47;records&#47;0&#47;report&#47;publication&#47;journal&#95;state |
| S1441 | F0033 | &#47;records&#47;0&#47;report&#47;publication&#47;visible&#95;name |
| S1442 | F0033 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1443 | F0033 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1444 | F0033 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1445 | F0033 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1446 | F0033 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1447 | F0033 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;at |
| S1448 | F0033 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;authorized&#95;local&#95;export |
| S1449 | F0033 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;reason |
| S1450 | F0033 | &#47;records&#47;1&#47;report&#47;state |
| S1451 | F0033 | &#47;records&#47;1&#47;report&#47;attempted |
| S1452 | F0033 | &#47;records&#47;1&#47;report&#47;reason |
| S1453 | F0033 | &#47;records&#47;1&#47;report&#47;post&#95;at |
| S1454 | F0033 | &#47;records&#47;1&#47;report&#47;publication&#47;journal&#95;state |
| S1455 | F0033 | &#47;records&#47;1&#47;report&#47;publication&#47;visible&#95;name |
| S1456 | F0033 | &#47;records&#47;1&#47;candidate&#47;disclosure&#47;activities |
| S1457 | F0033 | &#47;records&#47;1&#47;candidate&#47;disclosure&#47;scope |
| S1458 | F0033 | &#47;records&#47;1&#47;report&#47;preflight&#47;at |
| S1459 | F0033 | &#47;records&#47;1&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1460 | F0033 | &#47;records&#47;1&#47;report&#47;preflight&#47;reason |
| S1461 | F0033 | &#47;records&#47;1&#47;report&#47;final&#95;gate |
| S1462 | F0033 | &#47;records&#47;1&#47;report&#47;receipt |
| S1463 | F0033 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1464 | F0033 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1465 | F0033 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1466 | F0033 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1467 | F0033 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report |
| S1468 | F0033 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1469 | F0033 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1470 | F0033 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;findings |
| S1471 | F0033 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1472 | F0033 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1473 | F0033 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1474 | F0033 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1475 | F0019 | &#47;results&#47;14&#47;actual |
| S1476 | F0019 | &#47;results&#47;14&#47;differences |
| S1477 | F0034 | &#47;actual&#47;publication&#95;attempts |
| S1478 | F0034 | &#47;actual&#47;states |
| S1479 | F0034 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1480 | F0034 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1481 | F0034 | &#47;actual&#47;visible&#95;count |
| S1482 | F0034 | &#47;records&#47;0&#47;report&#47;state |
| S1483 | F0034 | &#47;records&#47;0&#47;report&#47;attempted |
| S1484 | F0034 | &#47;records&#47;0&#47;report&#47;reason |
| S1485 | F0034 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1486 | F0034 | &#47;records&#47;0&#47;report&#47;publication&#47;journal&#95;state |
| S1487 | F0034 | &#47;records&#47;0&#47;report&#47;publication&#47;visible&#95;name |
| S1488 | F0034 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1489 | F0034 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1490 | F0034 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1491 | F0034 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1492 | F0034 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1493 | F0034 | &#47;records&#47;0&#47;report&#47;final&#95;gate |
| S1494 | F0034 | &#47;records&#47;0&#47;report&#47;receipt |
| S1495 | F0034 | &#47;records&#47;1&#47;report&#47;state |
| S1496 | F0034 | &#47;records&#47;1&#47;report&#47;attempted |
| S1497 | F0034 | &#47;records&#47;1&#47;report&#47;reason |
| S1498 | F0034 | &#47;records&#47;1&#47;report&#47;post&#95;at |
| S1499 | F0034 | &#47;records&#47;1&#47;report&#47;publication&#47;journal&#95;state |
| S1500 | F0034 | &#47;records&#47;1&#47;report&#47;publication&#47;visible&#95;name |
| S1501 | F0034 | &#47;records&#47;1&#47;candidate&#47;disclosure&#47;activities |
| S1502 | F0034 | &#47;records&#47;1&#47;candidate&#47;disclosure&#47;scope |
| S1503 | F0034 | &#47;records&#47;1&#47;report&#47;preflight&#47;at |
| S1504 | F0034 | &#47;records&#47;1&#47;report&#47;preflight&#47;reason |
| S1505 | F0034 | &#47;records&#47;1&#47;report&#47;final&#95;gate&#47;at |
| S1506 | F0034 | &#47;records&#47;1&#47;report&#47;final&#95;gate&#47;authorized&#95;local&#95;export |
| S1507 | F0034 | &#47;records&#47;1&#47;report&#47;final&#95;gate&#47;reason |
| S1508 | F0034 | &#47;records&#47;1&#47;report&#47;receipt&#47;body&#47;kind |
| S1509 | F0034 | &#47;records&#47;1&#47;report&#47;receipt&#47;body&#47;request&#95;id |
| S1510 | F0034 | &#47;records&#47;1&#47;report&#47;receipt&#47;body&#47;fingerprint |
| S1511 | F0034 | &#47;records&#47;1&#47;report&#47;receipt&#47;body&#47;artifact&#95;sha256 |
| S1512 | F0034 | &#47;records&#47;1&#47;report&#47;receipt&#47;body&#47;disclosure&#95;sha256 |
| S1513 | F0034 | &#47;records&#47;1&#47;report&#47;receipt&#47;body&#47;byte&#95;length |
| S1514 | F0034 | &#47;records&#47;1&#47;report&#47;receipt&#47;body&#47;destination&#95;id |
| S1515 | F0034 | &#47;records&#47;1&#47;report&#47;receipt&#47;body&#47;visible&#95;name |
| S1516 | F0034 | &#47;records&#47;1&#47;report&#47;receipt&#47;body&#47;observed&#95;at |
| S1517 | F0034 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1518 | F0034 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1519 | F0034 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1520 | F0034 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1521 | F0034 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1522 | F0034 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1523 | F0034 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1524 | F0034 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1525 | F0034 | &#47;records&#47;1&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report |
| S1526 | F0034 | &#47;records&#47;1&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1527 | F0034 | &#47;records&#47;1&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1528 | F0034 | &#47;records&#47;1&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;findings |
| S1529 | F0019 | &#47;results&#47;15&#47;actual |
| S1530 | F0019 | &#47;results&#47;15&#47;differences |
| S1531 | F0035 | &#47;actual&#47;outside&#95;gate&#95;write&#95;observed |
| S1532 | F0035 | &#47;actual&#47;states |
| S1533 | F0035 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1534 | F0035 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1535 | F0035 | &#47;sort&#95;states |
| S1536 | F0035 | &#47;records&#47;0&#47;report&#47;attempted |
| S1537 | F0035 | &#47;records&#47;0&#47;report&#47;reason |
| S1538 | F0035 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1539 | F0035 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1540 | F0035 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1541 | F0035 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1542 | F0035 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1543 | F0035 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1544 | F0035 | &#47;records&#47;0&#47;report&#47;final&#95;gate |
| S1545 | F0035 | &#47;records&#47;0&#47;report&#47;receipt |
| S1546 | F0035 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1547 | F0035 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1548 | F0035 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1549 | F0035 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1550 | F0019 | &#47;results&#47;16&#47;actual |
| S1551 | F0019 | &#47;results&#47;16&#47;differences |
| S1552 | F0036 | &#47;actual&#47;publication&#95;attempts |
| S1553 | F0036 | &#47;actual&#47;states |
| S1554 | F0036 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1555 | F0036 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1556 | F0036 | &#47;actual&#47;visible&#95;count |
| S1557 | F0036 | &#47;sort&#95;states |
| S1558 | F0036 | &#47;records&#47;0&#47;report&#47;state |
| S1559 | F0036 | &#47;records&#47;0&#47;report&#47;attempted |
| S1560 | F0036 | &#47;records&#47;0&#47;report&#47;reason |
| S1561 | F0036 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1562 | F0036 | &#47;records&#47;0&#47;report&#47;publication |
| S1563 | F0036 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1564 | F0036 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1565 | F0036 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1566 | F0036 | &#47;records&#47;0&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1567 | F0036 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1568 | F0036 | &#47;records&#47;0&#47;report&#47;final&#95;gate |
| S1569 | F0036 | &#47;records&#47;0&#47;report&#47;receipt |
| S1570 | F0036 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame |
| S1571 | F0019 | &#47;results&#47;17&#47;actual |
| S1572 | F0019 | &#47;results&#47;17&#47;differences |
| S1573 | F0037 | &#47;actual&#47;publication&#95;attempts |
| S1574 | F0037 | &#47;actual&#47;states |
| S1575 | F0037 | &#47;actual&#47;unknown&#95;attempt&#95;observations |
| S1576 | F0037 | &#47;actual&#47;visible&#95;bytes&#95;match&#95;candidate |
| S1577 | F0037 | &#47;actual&#47;visible&#95;count |
| S1578 | F0037 | &#47;sort&#95;states |
| S1579 | F0037 | &#47;records&#47;0&#47;report&#47;state |
| S1580 | F0037 | &#47;records&#47;0&#47;report&#47;attempted |
| S1581 | F0037 | &#47;records&#47;0&#47;report&#47;reason |
| S1582 | F0037 | &#47;records&#47;0&#47;report&#47;post&#95;at |
| S1583 | F0037 | &#47;records&#47;0&#47;report&#47;publication&#47;journal&#95;state |
| S1584 | F0037 | &#47;records&#47;0&#47;report&#47;publication&#47;visible&#95;name |
| S1585 | F0037 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;activities |
| S1586 | F0037 | &#47;records&#47;0&#47;candidate&#47;disclosure&#47;scope |
| S1587 | F0037 | &#47;records&#47;0&#47;report&#47;preflight&#47;at |
| S1588 | F0037 | &#47;records&#47;0&#47;report&#47;preflight&#47;reason |
| S1589 | F0037 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;at |
| S1590 | F0037 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;authorized&#95;local&#95;export |
| S1591 | F0037 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;reason |
| S1592 | F0037 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;kind |
| S1593 | F0037 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;request&#95;id |
| S1594 | F0037 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;fingerprint |
| S1595 | F0037 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;artifact&#95;sha256 |
| S1596 | F0037 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;disclosure&#95;sha256 |
| S1597 | F0037 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;byte&#95;length |
| S1598 | F0037 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;destination&#95;id |
| S1599 | F0037 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;visible&#95;name |
| S1600 | F0037 | &#47;records&#47;0&#47;report&#47;receipt&#47;body&#47;observed&#95;at |
| S1601 | F0037 | &#47;records&#47;1&#47;report&#47;state |
| S1602 | F0037 | &#47;records&#47;1&#47;report&#47;attempted |
| S1603 | F0037 | &#47;records&#47;1&#47;report&#47;reason |
| S1604 | F0037 | &#47;records&#47;1&#47;report&#47;post&#95;at |
| S1605 | F0037 | &#47;records&#47;1&#47;report&#47;publication&#47;journal&#95;state |
| S1606 | F0037 | &#47;records&#47;1&#47;report&#47;publication&#47;visible&#95;name |
| S1607 | F0037 | &#47;records&#47;1&#47;candidate&#47;disclosure&#47;activities |
| S1608 | F0037 | &#47;records&#47;1&#47;candidate&#47;disclosure&#47;scope |
| S1609 | F0037 | &#47;records&#47;1&#47;report&#47;preflight&#47;at |
| S1610 | F0037 | &#47;records&#47;1&#47;report&#47;preflight&#47;authorized&#95;local&#95;export |
| S1611 | F0037 | &#47;records&#47;1&#47;report&#47;preflight&#47;reason |
| S1612 | F0037 | &#47;records&#47;1&#47;report&#47;final&#95;gate |
| S1613 | F0037 | &#47;records&#47;1&#47;report&#47;receipt |
| S1614 | F0037 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1615 | F0037 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1616 | F0037 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1617 | F0037 | &#47;records&#47;0&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1618 | F0037 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report |
| S1619 | F0037 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1620 | F0037 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1621 | F0037 | &#47;records&#47;0&#47;report&#47;final&#95;gate&#47;assessor&#95;frame&#47;report&#47;findings |
| S1622 | F0037 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report |
| S1623 | F0037 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;evidence&#95;integrity |
| S1624 | F0037 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;assessments |
| S1625 | F0037 | &#47;records&#47;1&#47;report&#47;preflight&#47;assessor&#95;frame&#47;report&#47;findings |
| S1626 | F0038 | &#47;results&#47;0&#47;actual |
| S1627 | F0038 | &#47;results&#47;0&#47;differences |
| S1628 | F0039 | &#47;actual&#47;core&#95;evidence |
| S1629 | F0039 | &#47;actual&#47;local&#95;observations |
| S1630 | F0039 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S1631 | F0039 | &#47;actual&#47;rejected&#95;probes |
| S1632 | F0039 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S1633 | F0039 | &#47;actual&#47;states |
| S1634 | F0039 | &#47;actual&#47;unlink&#95;attempts |
| S1635 | F0039 | &#47;sort&#95;states |
| S1636 | F0039 | &#47;case&#95;as&#95;of |
| S1637 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S1638 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S1639 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S1640 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S1641 | F0039 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S1642 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S1643 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S1644 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S1645 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;request&#95;record&#95;id |
| S1646 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;completed&#95;at |
| S1647 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;locations |
| S1648 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;exclusions |
| S1649 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;kind |
| S1650 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;task&#95;sha256 |
| S1651 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;request&#95;id |
| S1652 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;manifest&#95;sha256 |
| S1653 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;before |
| S1654 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;unlinked&#95;at |
| S1655 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;observed&#95;at |
| S1656 | F0039 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;after |
| S1657 | F0039 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S1658 | F0039 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S1659 | F0039 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S1660 | F0039 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S1661 | F0039 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S1662 | F0039 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S1663 | F0039 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S1664 | F0039 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S1665 | F0039 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S1666 | F0039 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S1667 | F0039 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S1668 | F0039 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S1669 | F0039 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S1670 | F0039 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S1671 | F0039 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S1672 | F0039 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S1673 | F0039 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S1674 | F0039 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S1675 | F0039 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S1676 | F0039 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S1677 | F0039 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S1678 | F0039 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S1679 | F0039 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S1680 | F0039 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S1681 | F0039 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S1682 | F0039 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S1683 | F0039 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S1684 | F0039 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S1685 | F0038 | &#47;results&#47;1&#47;actual |
| S1686 | F0038 | &#47;results&#47;1&#47;differences |
| S1687 | F0040 | &#47;actual&#47;core&#95;evidence |
| S1688 | F0040 | &#47;actual&#47;local&#95;observations |
| S1689 | F0040 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S1690 | F0040 | &#47;actual&#47;rejected&#95;probes |
| S1691 | F0040 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S1692 | F0040 | &#47;actual&#47;states |
| S1693 | F0040 | &#47;actual&#47;unlink&#95;attempts |
| S1694 | F0040 | &#47;sort&#95;states |
| S1695 | F0040 | &#47;case&#95;as&#95;of |
| S1696 | F0040 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S1697 | F0040 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S1698 | F0040 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S1699 | F0040 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S1700 | F0040 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S1701 | F0040 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S1702 | F0040 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S1703 | F0040 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S1704 | F0040 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation |
| S1705 | F0040 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt |
| S1706 | F0040 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S1707 | F0040 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S1708 | F0040 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S1709 | F0040 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S1710 | F0040 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S1711 | F0040 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S1712 | F0040 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S1713 | F0040 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S1714 | F0040 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S1715 | F0040 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S1716 | F0040 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S1717 | F0040 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S1718 | F0040 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S1719 | F0040 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S1720 | F0040 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S1721 | F0040 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S1722 | F0040 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S1723 | F0040 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S1724 | F0040 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S1725 | F0040 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S1726 | F0040 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S1727 | F0040 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S1728 | F0040 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S1729 | F0040 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S1730 | F0040 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S1731 | F0040 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S1732 | F0040 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S1733 | F0040 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S1734 | F0038 | &#47;results&#47;2&#47;actual |
| S1735 | F0038 | &#47;results&#47;2&#47;differences |
| S1736 | F0041 | &#47;actual&#47;core&#95;evidence |
| S1737 | F0041 | &#47;actual&#47;local&#95;observations |
| S1738 | F0041 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S1739 | F0041 | &#47;actual&#47;rejected&#95;probes |
| S1740 | F0041 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S1741 | F0041 | &#47;actual&#47;states |
| S1742 | F0041 | &#47;actual&#47;unlink&#95;attempts |
| S1743 | F0041 | &#47;sort&#95;states |
| S1744 | F0041 | &#47;case&#95;as&#95;of |
| S1745 | F0041 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result |
| S1746 | F0041 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S1747 | F0041 | &#47;records&#47;0&#47;bundle&#47;before |
| S1748 | F0041 | &#47;records&#47;0&#47;bundle&#47;after |
| S1749 | F0041 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S1750 | F0041 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S1751 | F0041 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S1752 | F0041 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S1753 | F0041 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S1754 | F0041 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S1755 | F0041 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S1756 | F0041 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S1757 | F0041 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S1758 | F0041 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S1759 | F0038 | &#47;results&#47;3&#47;actual |
| S1760 | F0038 | &#47;results&#47;3&#47;differences |
| S1761 | F0042 | &#47;actual&#47;core&#95;evidence |
| S1762 | F0042 | &#47;actual&#47;local&#95;observations |
| S1763 | F0042 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S1764 | F0042 | &#47;actual&#47;rejected&#95;probes |
| S1765 | F0042 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S1766 | F0042 | &#47;actual&#47;states |
| S1767 | F0042 | &#47;actual&#47;unlink&#95;attempts |
| S1768 | F0042 | &#47;sort&#95;states |
| S1769 | F0042 | &#47;case&#95;as&#95;of |
| S1770 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S1771 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S1772 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S1773 | F0042 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S1774 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S1775 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S1776 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S1777 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;request&#95;record&#95;id |
| S1778 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;completed&#95;at |
| S1779 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;locations |
| S1780 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;exclusions |
| S1781 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;kind |
| S1782 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;task&#95;sha256 |
| S1783 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;request&#95;id |
| S1784 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;manifest&#95;sha256 |
| S1785 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;before |
| S1786 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;unlinked&#95;at |
| S1787 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;observed&#95;at |
| S1788 | F0042 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;after |
| S1789 | F0042 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S1790 | F0042 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S1791 | F0042 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S1792 | F0042 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S1793 | F0042 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S1794 | F0042 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S1795 | F0042 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S1796 | F0042 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S1797 | F0042 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S1798 | F0042 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S1799 | F0042 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S1800 | F0042 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S1801 | F0042 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S1802 | F0042 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S1803 | F0042 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S1804 | F0042 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S1805 | F0042 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S1806 | F0042 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S1807 | F0042 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S1808 | F0042 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S1809 | F0042 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S1810 | F0042 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S1811 | F0042 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S1812 | F0042 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S1813 | F0042 | &#47;probes&#47;0&#47;expected&#95;task&#95;sha256 |
| S1814 | F0042 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S1815 | F0042 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S1816 | F0042 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S1817 | F0042 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S1818 | F0038 | &#47;results&#47;4&#47;actual |
| S1819 | F0038 | &#47;results&#47;4&#47;differences |
| S1820 | F0043 | &#47;actual&#47;core&#95;evidence |
| S1821 | F0043 | &#47;actual&#47;local&#95;observations |
| S1822 | F0043 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S1823 | F0043 | &#47;actual&#47;rejected&#95;probes |
| S1824 | F0043 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S1825 | F0043 | &#47;actual&#47;states |
| S1826 | F0043 | &#47;actual&#47;unlink&#95;attempts |
| S1827 | F0043 | &#47;sort&#95;states |
| S1828 | F0043 | &#47;case&#95;as&#95;of |
| S1829 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S1830 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S1831 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S1832 | F0043 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S1833 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S1834 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S1835 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S1836 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;request&#95;record&#95;id |
| S1837 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;completed&#95;at |
| S1838 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;locations |
| S1839 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;exclusions |
| S1840 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;kind |
| S1841 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;task&#95;sha256 |
| S1842 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;request&#95;id |
| S1843 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;manifest&#95;sha256 |
| S1844 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;before |
| S1845 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;unlinked&#95;at |
| S1846 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;observed&#95;at |
| S1847 | F0043 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;after |
| S1848 | F0043 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S1849 | F0043 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S1850 | F0043 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S1851 | F0043 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S1852 | F0043 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S1853 | F0043 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S1854 | F0043 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S1855 | F0043 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S1856 | F0043 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S1857 | F0043 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S1858 | F0043 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S1859 | F0043 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S1860 | F0043 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S1861 | F0043 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S1862 | F0043 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S1863 | F0043 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S1864 | F0043 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S1865 | F0043 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S1866 | F0043 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S1867 | F0043 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S1868 | F0043 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S1869 | F0043 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S1870 | F0043 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S1871 | F0043 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S1872 | F0043 | &#47;probes&#47;0&#47;expected&#95;task&#95;sha256 |
| S1873 | F0043 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S1874 | F0043 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S1875 | F0043 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S1876 | F0043 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S1877 | F0038 | &#47;results&#47;5&#47;actual |
| S1878 | F0038 | &#47;results&#47;5&#47;differences |
| S1879 | F0044 | &#47;actual&#47;core&#95;evidence |
| S1880 | F0044 | &#47;actual&#47;local&#95;observations |
| S1881 | F0044 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S1882 | F0044 | &#47;actual&#47;rejected&#95;probes |
| S1883 | F0044 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S1884 | F0044 | &#47;actual&#47;states |
| S1885 | F0044 | &#47;actual&#47;unlink&#95;attempts |
| S1886 | F0044 | &#47;sort&#95;states |
| S1887 | F0044 | &#47;case&#95;as&#95;of |
| S1888 | F0044 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S1889 | F0044 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S1890 | F0044 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S1891 | F0044 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S1892 | F0044 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S1893 | F0044 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S1894 | F0044 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S1895 | F0044 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S1896 | F0044 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation |
| S1897 | F0044 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt |
| S1898 | F0044 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S1899 | F0044 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S1900 | F0044 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S1901 | F0044 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S1902 | F0044 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S1903 | F0044 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S1904 | F0044 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S1905 | F0044 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S1906 | F0044 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S1907 | F0044 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S1908 | F0044 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S1909 | F0044 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S1910 | F0044 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S1911 | F0044 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S1912 | F0044 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S1913 | F0044 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S1914 | F0044 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S1915 | F0044 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S1916 | F0044 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S1917 | F0044 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S1918 | F0044 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S1919 | F0044 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S1920 | F0044 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S1921 | F0044 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S1922 | F0044 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S1923 | F0044 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S1924 | F0044 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S1925 | F0044 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S1926 | F0038 | &#47;results&#47;6&#47;actual |
| S1927 | F0038 | &#47;results&#47;6&#47;differences |
| S1928 | F0045 | &#47;actual&#47;core&#95;evidence |
| S1929 | F0045 | &#47;actual&#47;local&#95;observations |
| S1930 | F0045 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S1931 | F0045 | &#47;actual&#47;rejected&#95;probes |
| S1932 | F0045 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S1933 | F0045 | &#47;actual&#47;states |
| S1934 | F0045 | &#47;actual&#47;unlink&#95;attempts |
| S1935 | F0045 | &#47;sort&#95;states |
| S1936 | F0045 | &#47;case&#95;as&#95;of |
| S1937 | F0045 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S1938 | F0045 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S1939 | F0045 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S1940 | F0045 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S1941 | F0045 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S1942 | F0045 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement |
| S1943 | F0045 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation |
| S1944 | F0045 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt |
| S1945 | F0045 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S1946 | F0045 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S1947 | F0045 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S1948 | F0045 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S1949 | F0045 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S1950 | F0045 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S1951 | F0045 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S1952 | F0045 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S1953 | F0045 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S1954 | F0045 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S1955 | F0045 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S1956 | F0045 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S1957 | F0045 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S1958 | F0045 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S1959 | F0045 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S1960 | F0045 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S1961 | F0045 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S1962 | F0045 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S1963 | F0045 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S1964 | F0045 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S1965 | F0045 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S1966 | F0045 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S1967 | F0045 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S1968 | F0045 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S1969 | F0045 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S1970 | F0045 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S1971 | F0045 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S1972 | F0045 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S1973 | F0038 | &#47;results&#47;7&#47;actual |
| S1974 | F0038 | &#47;results&#47;7&#47;differences |
| S1975 | F0046 | &#47;actual&#47;core&#95;evidence |
| S1976 | F0046 | &#47;actual&#47;local&#95;observations |
| S1977 | F0046 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S1978 | F0046 | &#47;actual&#47;rejected&#95;probes |
| S1979 | F0046 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S1980 | F0046 | &#47;actual&#47;states |
| S1981 | F0046 | &#47;actual&#47;unlink&#95;attempts |
| S1982 | F0046 | &#47;sort&#95;states |
| S1983 | F0046 | &#47;case&#95;as&#95;of |
| S1984 | F0046 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S1985 | F0046 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S1986 | F0046 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S1987 | F0046 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement |
| S1988 | F0046 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation |
| S1989 | F0046 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt |
| S1990 | F0046 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S1991 | F0046 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S1992 | F0046 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S1993 | F0046 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S1994 | F0046 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S1995 | F0046 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S1996 | F0046 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S1997 | F0046 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S1998 | F0046 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S1999 | F0046 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2000 | F0046 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2001 | F0046 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S2002 | F0046 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2003 | F0046 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2004 | F0046 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S2005 | F0046 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2006 | F0046 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2007 | F0046 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S2008 | F0046 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2009 | F0046 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2010 | F0046 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2011 | F0046 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2012 | F0046 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2013 | F0046 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2014 | F0046 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S2015 | F0046 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2016 | F0046 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2017 | F0046 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2018 | F0038 | &#47;results&#47;8&#47;actual |
| S2019 | F0038 | &#47;results&#47;8&#47;differences |
| S2020 | F0047 | &#47;actual&#47;core&#95;evidence |
| S2021 | F0047 | &#47;actual&#47;local&#95;observations |
| S2022 | F0047 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S2023 | F0047 | &#47;actual&#47;rejected&#95;probes |
| S2024 | F0047 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S2025 | F0047 | &#47;actual&#47;states |
| S2026 | F0047 | &#47;actual&#47;unlink&#95;attempts |
| S2027 | F0047 | &#47;sort&#95;states |
| S2028 | F0047 | &#47;case&#95;as&#95;of |
| S2029 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S2030 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2031 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S2032 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2033 | F0047 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S2034 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2035 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S2036 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S2037 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2038 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;completed&#95;at |
| S2039 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;locations |
| S2040 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;exclusions |
| S2041 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;kind |
| S2042 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;task&#95;sha256 |
| S2043 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;request&#95;id |
| S2044 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;manifest&#95;sha256 |
| S2045 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;before |
| S2046 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;unlinked&#95;at |
| S2047 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;observed&#95;at |
| S2048 | F0047 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;after |
| S2049 | F0047 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S2050 | F0047 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S2051 | F0047 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S2052 | F0047 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S2053 | F0047 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S2054 | F0047 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S2055 | F0047 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S2056 | F0047 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S2057 | F0047 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S2058 | F0047 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2059 | F0047 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2060 | F0047 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S2061 | F0047 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2062 | F0047 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2063 | F0047 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S2064 | F0047 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2065 | F0047 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2066 | F0047 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S2067 | F0047 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2068 | F0047 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2069 | F0047 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2070 | F0047 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2071 | F0047 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2072 | F0047 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2073 | F0047 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;state |
| S2074 | F0047 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2075 | F0047 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;reason |
| S2076 | F0047 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2077 | F0047 | &#47;records&#47;1&#47;assessment&#47;local&#95;observation |
| S2078 | F0047 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;acknowledgement |
| S2079 | F0047 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;attestation |
| S2080 | F0047 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;receipt |
| S2081 | F0047 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S2082 | F0047 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S2083 | F0047 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;location |
| S2084 | F0047 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S2085 | F0047 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S2086 | F0047 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;phase |
| S2087 | F0047 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S2088 | F0047 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S2089 | F0047 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;measurement |
| S2090 | F0047 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2091 | F0047 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2092 | F0047 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;location |
| S2093 | F0047 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2094 | F0047 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2095 | F0047 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;phase |
| S2096 | F0047 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2097 | F0047 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2098 | F0047 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;measurement |
| S2099 | F0047 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2100 | F0047 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2101 | F0047 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2102 | F0047 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2103 | F0047 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2104 | F0047 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2105 | F0047 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S2106 | F0047 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2107 | F0047 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2108 | F0047 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2109 | F0047 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report |
| S2110 | F0047 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2111 | F0047 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2112 | F0047 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2113 | F0038 | &#47;results&#47;9&#47;actual |
| S2114 | F0038 | &#47;results&#47;9&#47;differences |
| S2115 | F0048 | &#47;actual&#47;core&#95;evidence |
| S2116 | F0048 | &#47;actual&#47;local&#95;observations |
| S2117 | F0048 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S2118 | F0048 | &#47;actual&#47;rejected&#95;probes |
| S2119 | F0048 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S2120 | F0048 | &#47;actual&#47;states |
| S2121 | F0048 | &#47;actual&#47;unlink&#95;attempts |
| S2122 | F0048 | &#47;sort&#95;states |
| S2123 | F0048 | &#47;case&#95;as&#95;of |
| S2124 | F0048 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2125 | F0048 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S2126 | F0048 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2127 | F0048 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2128 | F0048 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S2129 | F0048 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S2130 | F0048 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation |
| S2131 | F0048 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S2132 | F0048 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S2133 | F0048 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S2134 | F0048 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S2135 | F0048 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S2136 | F0048 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S2137 | F0048 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S2138 | F0048 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S2139 | F0048 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S2140 | F0048 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2141 | F0048 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2142 | F0048 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S2143 | F0048 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2144 | F0048 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2145 | F0048 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S2146 | F0048 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2147 | F0048 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2148 | F0048 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S2149 | F0048 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2150 | F0048 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2151 | F0048 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2152 | F0048 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2153 | F0048 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2154 | F0048 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2155 | F0048 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2156 | F0048 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;reason |
| S2157 | F0048 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2158 | F0048 | &#47;records&#47;1&#47;assessment&#47;local&#95;observation |
| S2159 | F0048 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;acknowledgement |
| S2160 | F0048 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;attestation |
| S2161 | F0048 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;receipt |
| S2162 | F0048 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S2163 | F0048 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S2164 | F0048 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;location |
| S2165 | F0048 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S2166 | F0048 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S2167 | F0048 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;phase |
| S2168 | F0048 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S2169 | F0048 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S2170 | F0048 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;measurement |
| S2171 | F0048 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2172 | F0048 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2173 | F0048 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;location |
| S2174 | F0048 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2175 | F0048 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2176 | F0048 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;phase |
| S2177 | F0048 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2178 | F0048 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2179 | F0048 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;measurement |
| S2180 | F0048 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2181 | F0048 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2182 | F0048 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2183 | F0048 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2184 | F0048 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2185 | F0048 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2186 | F0048 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S2187 | F0048 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2188 | F0048 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2189 | F0048 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2190 | F0048 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report |
| S2191 | F0048 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2192 | F0048 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2193 | F0048 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2194 | F0038 | &#47;results&#47;10&#47;actual |
| S2195 | F0038 | &#47;results&#47;10&#47;differences |
| S2196 | F0049 | &#47;actual&#47;core&#95;evidence |
| S2197 | F0049 | &#47;actual&#47;local&#95;observations |
| S2198 | F0049 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S2199 | F0049 | &#47;actual&#47;rejected&#95;probes |
| S2200 | F0049 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S2201 | F0049 | &#47;actual&#47;states |
| S2202 | F0049 | &#47;actual&#47;unlink&#95;attempts |
| S2203 | F0049 | &#47;case&#95;as&#95;of |
| S2204 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S2205 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2206 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S2207 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2208 | F0049 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S2209 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2210 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S2211 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S2212 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2213 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;completed&#95;at |
| S2214 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;locations |
| S2215 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;exclusions |
| S2216 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;kind |
| S2217 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;task&#95;sha256 |
| S2218 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;request&#95;id |
| S2219 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;manifest&#95;sha256 |
| S2220 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;before |
| S2221 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;unlinked&#95;at |
| S2222 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;observed&#95;at |
| S2223 | F0049 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;after |
| S2224 | F0049 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S2225 | F0049 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S2226 | F0049 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S2227 | F0049 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S2228 | F0049 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S2229 | F0049 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S2230 | F0049 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S2231 | F0049 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S2232 | F0049 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S2233 | F0049 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2234 | F0049 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2235 | F0049 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S2236 | F0049 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2237 | F0049 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2238 | F0049 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S2239 | F0049 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2240 | F0049 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2241 | F0049 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S2242 | F0049 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2243 | F0049 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2244 | F0049 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2245 | F0049 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2246 | F0049 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2247 | F0049 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2248 | F0049 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;state |
| S2249 | F0049 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2250 | F0049 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;reason |
| S2251 | F0049 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2252 | F0049 | &#47;records&#47;1&#47;assessment&#47;local&#95;observation |
| S2253 | F0049 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;acknowledgement |
| S2254 | F0049 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;attestation |
| S2255 | F0049 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;receipt |
| S2256 | F0049 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S2257 | F0049 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S2258 | F0049 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;location |
| S2259 | F0049 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S2260 | F0049 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S2261 | F0049 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;phase |
| S2262 | F0049 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S2263 | F0049 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S2264 | F0049 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;measurement |
| S2265 | F0049 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2266 | F0049 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2267 | F0049 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;location |
| S2268 | F0049 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2269 | F0049 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2270 | F0049 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;phase |
| S2271 | F0049 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2272 | F0049 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2273 | F0049 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;measurement |
| S2274 | F0049 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2275 | F0049 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2276 | F0049 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2277 | F0049 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2278 | F0049 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2279 | F0049 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2280 | F0049 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S2281 | F0049 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2282 | F0049 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2283 | F0049 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2284 | F0049 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report |
| S2285 | F0049 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2286 | F0049 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2287 | F0049 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2288 | F0038 | &#47;results&#47;11&#47;actual |
| S2289 | F0038 | &#47;results&#47;11&#47;differences |
| S2290 | F0050 | &#47;actual&#47;core&#95;evidence |
| S2291 | F0050 | &#47;actual&#47;local&#95;observations |
| S2292 | F0050 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S2293 | F0050 | &#47;actual&#47;rejected&#95;probes |
| S2294 | F0050 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S2295 | F0050 | &#47;actual&#47;states |
| S2296 | F0050 | &#47;actual&#47;unlink&#95;attempts |
| S2297 | F0050 | &#47;sort&#95;states |
| S2298 | F0050 | &#47;case&#95;as&#95;of |
| S2299 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2300 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S2301 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2302 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2303 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S2304 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S2305 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2306 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;completed&#95;at |
| S2307 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;locations |
| S2308 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;exclusions |
| S2309 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;kind |
| S2310 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;task&#95;sha256 |
| S2311 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;request&#95;id |
| S2312 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;manifest&#95;sha256 |
| S2313 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;before |
| S2314 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;unlinked&#95;at |
| S2315 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;observed&#95;at |
| S2316 | F0050 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;after |
| S2317 | F0050 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S2318 | F0050 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S2319 | F0050 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S2320 | F0050 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S2321 | F0050 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S2322 | F0050 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S2323 | F0050 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S2324 | F0050 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S2325 | F0050 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S2326 | F0050 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2327 | F0050 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2328 | F0050 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S2329 | F0050 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2330 | F0050 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2331 | F0050 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S2332 | F0050 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2333 | F0050 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2334 | F0050 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S2335 | F0050 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2336 | F0050 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2337 | F0050 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2338 | F0050 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2339 | F0050 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2340 | F0050 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2341 | F0050 | &#47;retained&#95;controls&#47;0&#47;body&#47;kind |
| S2342 | F0050 | &#47;retained&#95;controls&#47;0&#47;body&#47;task&#95;sha256 |
| S2343 | F0050 | &#47;retained&#95;controls&#47;0&#47;body&#47;manifest&#95;sha256 |
| S2344 | F0050 | &#47;retained&#95;controls&#47;0&#47;body&#47;sha256 |
| S2345 | F0050 | &#47;retained&#95;controls&#47;0&#47;body&#47;byte&#95;length |
| S2346 | F0050 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S2347 | F0050 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2348 | F0050 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2349 | F0050 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2350 | F0038 | &#47;results&#47;12&#47;actual |
| S2351 | F0038 | &#47;results&#47;12&#47;differences |
| S2352 | F0051 | &#47;actual&#47;core&#95;evidence |
| S2353 | F0051 | &#47;actual&#47;local&#95;observations |
| S2354 | F0051 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S2355 | F0051 | &#47;actual&#47;rejected&#95;probes |
| S2356 | F0051 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S2357 | F0051 | &#47;actual&#47;states |
| S2358 | F0051 | &#47;actual&#47;unlink&#95;attempts |
| S2359 | F0051 | &#47;sort&#95;states |
| S2360 | F0051 | &#47;case&#95;as&#95;of |
| S2361 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2362 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S2363 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2364 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2365 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S2366 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S2367 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2368 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;completed&#95;at |
| S2369 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;locations |
| S2370 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;exclusions |
| S2371 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;kind |
| S2372 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;task&#95;sha256 |
| S2373 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;request&#95;id |
| S2374 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;manifest&#95;sha256 |
| S2375 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;before |
| S2376 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;unlinked&#95;at |
| S2377 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;observed&#95;at |
| S2378 | F0051 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;after |
| S2379 | F0051 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S2380 | F0051 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S2381 | F0051 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S2382 | F0051 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S2383 | F0051 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S2384 | F0051 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S2385 | F0051 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S2386 | F0051 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S2387 | F0051 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S2388 | F0051 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2389 | F0051 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2390 | F0051 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S2391 | F0051 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2392 | F0051 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2393 | F0051 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S2394 | F0051 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2395 | F0051 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2396 | F0051 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S2397 | F0051 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2398 | F0051 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2399 | F0051 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2400 | F0051 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2401 | F0051 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2402 | F0051 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2403 | F0051 | &#47;retained&#95;controls&#47;0&#47;body&#47;kind |
| S2404 | F0051 | &#47;retained&#95;controls&#47;0&#47;body&#47;task&#95;sha256 |
| S2405 | F0051 | &#47;retained&#95;controls&#47;0&#47;body&#47;manifest&#95;sha256 |
| S2406 | F0051 | &#47;retained&#95;controls&#47;0&#47;body&#47;sha256 |
| S2407 | F0051 | &#47;retained&#95;controls&#47;0&#47;body&#47;byte&#95;length |
| S2408 | F0051 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S2409 | F0051 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2410 | F0051 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2411 | F0051 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2412 | F0038 | &#47;results&#47;13&#47;actual |
| S2413 | F0038 | &#47;results&#47;13&#47;differences |
| S2414 | F0052 | &#47;actual&#47;core&#95;evidence |
| S2415 | F0052 | &#47;actual&#47;local&#95;observations |
| S2416 | F0052 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S2417 | F0052 | &#47;actual&#47;rejected&#95;probes |
| S2418 | F0052 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S2419 | F0052 | &#47;actual&#47;states |
| S2420 | F0052 | &#47;actual&#47;unlink&#95;attempts |
| S2421 | F0052 | &#47;sort&#95;states |
| S2422 | F0052 | &#47;case&#95;as&#95;of |
| S2423 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2424 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S2425 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2426 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2427 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S2428 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S2429 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2430 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;completed&#95;at |
| S2431 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;locations |
| S2432 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;exclusions |
| S2433 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;kind |
| S2434 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;task&#95;sha256 |
| S2435 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;request&#95;id |
| S2436 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;manifest&#95;sha256 |
| S2437 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;before |
| S2438 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;unlinked&#95;at |
| S2439 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;observed&#95;at |
| S2440 | F0052 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;after |
| S2441 | F0052 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2442 | F0052 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2443 | F0052 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S2444 | F0052 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2445 | F0052 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2446 | F0052 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S2447 | F0052 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2448 | F0052 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2449 | F0052 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S2450 | F0052 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2451 | F0052 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2452 | F0052 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2453 | F0052 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2454 | F0052 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2455 | F0052 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2456 | F0052 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S2457 | F0052 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2458 | F0052 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2459 | F0052 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2460 | F0038 | &#47;results&#47;14&#47;actual |
| S2461 | F0038 | &#47;results&#47;14&#47;differences |
| S2462 | F0053 | &#47;actual&#47;core&#95;evidence |
| S2463 | F0053 | &#47;actual&#47;local&#95;observations |
| S2464 | F0053 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S2465 | F0053 | &#47;actual&#47;rejected&#95;probes |
| S2466 | F0053 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S2467 | F0053 | &#47;actual&#47;states |
| S2468 | F0053 | &#47;actual&#47;unlink&#95;attempts |
| S2469 | F0053 | &#47;sort&#95;states |
| S2470 | F0053 | &#47;case&#95;as&#95;of |
| S2471 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2472 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S2473 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2474 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2475 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S2476 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S2477 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2478 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;completed&#95;at |
| S2479 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;locations |
| S2480 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;exclusions |
| S2481 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;kind |
| S2482 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;task&#95;sha256 |
| S2483 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;request&#95;id |
| S2484 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;manifest&#95;sha256 |
| S2485 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;before |
| S2486 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;unlinked&#95;at |
| S2487 | F0053 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;after |
| S2488 | F0053 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S2489 | F0053 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S2490 | F0053 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S2491 | F0053 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S2492 | F0053 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S2493 | F0053 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S2494 | F0053 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S2495 | F0053 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S2496 | F0053 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S2497 | F0053 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2498 | F0053 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2499 | F0053 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S2500 | F0053 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2501 | F0053 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2502 | F0053 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S2503 | F0053 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2504 | F0053 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2505 | F0053 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S2506 | F0053 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2507 | F0053 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2508 | F0053 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2509 | F0053 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2510 | F0053 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2511 | F0053 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2512 | F0053 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S2513 | F0053 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2514 | F0053 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2515 | F0053 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2516 | F0038 | &#47;results&#47;15&#47;actual |
| S2517 | F0038 | &#47;results&#47;15&#47;differences |
| S2518 | F0054 | &#47;actual&#47;core&#95;evidence |
| S2519 | F0054 | &#47;actual&#47;local&#95;observations |
| S2520 | F0054 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S2521 | F0054 | &#47;actual&#47;rejected&#95;probes |
| S2522 | F0054 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S2523 | F0054 | &#47;actual&#47;states |
| S2524 | F0054 | &#47;actual&#47;unlink&#95;attempts |
| S2525 | F0054 | &#47;sort&#95;states |
| S2526 | F0054 | &#47;case&#95;as&#95;of |
| S2527 | F0054 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S2528 | F0054 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2529 | F0054 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S2530 | F0054 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2531 | F0054 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S2532 | F0054 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement |
| S2533 | F0054 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation |
| S2534 | F0054 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt |
| S2535 | F0054 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S2536 | F0054 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S2537 | F0054 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S2538 | F0054 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S2539 | F0054 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S2540 | F0054 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S2541 | F0054 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S2542 | F0054 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S2543 | F0054 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S2544 | F0054 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2545 | F0054 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2546 | F0054 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S2547 | F0054 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2548 | F0054 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2549 | F0054 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S2550 | F0054 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2551 | F0054 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2552 | F0054 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S2553 | F0054 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2554 | F0054 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2555 | F0054 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2556 | F0054 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2557 | F0054 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2558 | F0054 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2559 | F0054 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S2560 | F0054 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2561 | F0054 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2562 | F0054 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2563 | F0038 | &#47;results&#47;16&#47;actual |
| S2564 | F0038 | &#47;results&#47;16&#47;differences |
| S2565 | F0055 | &#47;actual&#47;core&#95;evidence |
| S2566 | F0055 | &#47;actual&#47;local&#95;observations |
| S2567 | F0055 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S2568 | F0055 | &#47;actual&#47;rejected&#95;probes |
| S2569 | F0055 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S2570 | F0055 | &#47;actual&#47;states |
| S2571 | F0055 | &#47;actual&#47;unlink&#95;attempts |
| S2572 | F0055 | &#47;sort&#95;states |
| S2573 | F0055 | &#47;case&#95;as&#95;of |
| S2574 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S2575 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2576 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S2577 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2578 | F0055 | &#47;records&#47;0&#47;assessment&#47;local&#95;observation |
| S2579 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2580 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S2581 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S2582 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2583 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;completed&#95;at |
| S2584 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;locations |
| S2585 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;exclusions |
| S2586 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;kind |
| S2587 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;task&#95;sha256 |
| S2588 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;request&#95;id |
| S2589 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;manifest&#95;sha256 |
| S2590 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;before |
| S2591 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;unlinked&#95;at |
| S2592 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;observed&#95;at |
| S2593 | F0055 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;after |
| S2594 | F0055 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S2595 | F0055 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S2596 | F0055 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;location |
| S2597 | F0055 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S2598 | F0055 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S2599 | F0055 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;phase |
| S2600 | F0055 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S2601 | F0055 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S2602 | F0055 | &#47;records&#47;0&#47;bundle&#47;before&#47;body&#47;measurement |
| S2603 | F0055 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2604 | F0055 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2605 | F0055 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;location |
| S2606 | F0055 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2607 | F0055 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2608 | F0055 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;phase |
| S2609 | F0055 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2610 | F0055 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2611 | F0055 | &#47;records&#47;0&#47;bundle&#47;after&#47;body&#47;measurement |
| S2612 | F0055 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2613 | F0055 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2614 | F0055 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2615 | F0055 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2616 | F0055 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2617 | F0055 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2618 | F0055 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;state |
| S2619 | F0055 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2620 | F0055 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;reason |
| S2621 | F0055 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2622 | F0055 | &#47;records&#47;1&#47;assessment&#47;local&#95;observation |
| S2623 | F0055 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;acknowledgement |
| S2624 | F0055 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;attestation |
| S2625 | F0055 | &#47;records&#47;1&#47;bundle&#47;provider&#95;result&#47;receipt |
| S2626 | F0055 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;provider&#95;id |
| S2627 | F0055 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;tenant&#95;id |
| S2628 | F0055 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;location |
| S2629 | F0055 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;object&#95;id |
| S2630 | F0055 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;version&#95;id |
| S2631 | F0055 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;phase |
| S2632 | F0055 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;window&#95;start |
| S2633 | F0055 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;window&#95;end |
| S2634 | F0055 | &#47;records&#47;1&#47;bundle&#47;before&#47;body&#47;measurement |
| S2635 | F0055 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;provider&#95;id |
| S2636 | F0055 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;tenant&#95;id |
| S2637 | F0055 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;location |
| S2638 | F0055 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;object&#95;id |
| S2639 | F0055 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;version&#95;id |
| S2640 | F0055 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;phase |
| S2641 | F0055 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;window&#95;start |
| S2642 | F0055 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;window&#95;end |
| S2643 | F0055 | &#47;records&#47;1&#47;bundle&#47;after&#47;body&#47;measurement |
| S2644 | F0055 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2645 | F0055 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2646 | F0055 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2647 | F0055 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2648 | F0055 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2649 | F0055 | &#47;records&#47;1&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2650 | F0055 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S2651 | F0055 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2652 | F0055 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2653 | F0055 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2654 | F0055 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report |
| S2655 | F0055 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2656 | F0055 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2657 | F0055 | &#47;records&#47;1&#47;assessment&#47;assessor&#95;report&#47;findings |
| S2658 | F0038 | &#47;results&#47;17&#47;actual |
| S2659 | F0038 | &#47;results&#47;17&#47;differences |
| S2660 | F0056 | &#47;actual&#47;core&#95;evidence |
| S2661 | F0056 | &#47;actual&#47;local&#95;observations |
| S2662 | F0056 | &#47;actual&#47;outside&#95;scope&#95;remains&#95;unknown |
| S2663 | F0056 | &#47;actual&#47;rejected&#95;probes |
| S2664 | F0056 | &#47;actual&#47;retained&#95;readable&#95;controls |
| S2665 | F0056 | &#47;actual&#47;states |
| S2666 | F0056 | &#47;actual&#47;unlink&#95;attempts |
| S2667 | F0056 | &#47;sort&#95;states |
| S2668 | F0056 | &#47;case&#95;as&#95;of |
| S2669 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;state |
| S2670 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attempted |
| S2671 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;reason |
| S2672 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;journal&#95;state |
| S2673 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2674 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;acknowledged&#95;at |
| S2675 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;acknowledgement&#47;body&#47;data&#47;queue&#95;state |
| S2676 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;request&#95;record&#95;id |
| S2677 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;completed&#95;at |
| S2678 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;locations |
| S2679 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;attestation&#47;body&#47;data&#47;exclusions |
| S2680 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;kind |
| S2681 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;task&#95;sha256 |
| S2682 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;request&#95;id |
| S2683 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;manifest&#95;sha256 |
| S2684 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;before |
| S2685 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;unlinked&#95;at |
| S2686 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;observed&#95;at |
| S2687 | F0056 | &#47;records&#47;0&#47;bundle&#47;provider&#95;result&#47;receipt&#47;body&#47;after |
| S2688 | F0056 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;backups |
| S2689 | F0056 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;downstream&#45;copies |
| S2690 | F0056 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;open&#45;handles&#45;and&#45;memory |
| S2691 | F0056 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;replicas |
| S2692 | F0056 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;storage&#45;media |
| S2693 | F0056 | &#47;records&#47;0&#47;assessment&#47;unknown&#95;domains&#47;training&#45;derivatives |
| S2694 | F0056 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report |
| S2695 | F0056 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;evidence&#95;integrity |
| S2696 | F0056 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;assessments |
| S2697 | F0056 | &#47;records&#47;0&#47;assessment&#47;assessor&#95;report&#47;findings |

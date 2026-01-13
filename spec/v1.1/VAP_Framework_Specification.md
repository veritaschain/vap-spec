# Verifiable AI Provenance Framework (VAP)

## Framework Specification v1.1

**Document ID:** VSO-VAP-SPEC-001  
**Status:** Draft Specification  
**Version:** 1.1.0  
**Date:** 2025-12-11  
**Maintainer:** VeritasChain Standards Organization (VSO)  
**License:** CC BY 4.0 International  
**Website:** https://veritaschain.org

---

## Executive Summary

**VAP（Verifiable AI Provenance Framework）** は、あらゆる高リスクAIシステムに共通する「暗号学的に検証可能な判断証跡（Provenance）」の構成要件を規定する、**分野横断の上位フレームワーク**である。

VAPは「AIの利用を制限する規制」ではなく、**「AIを安全に継続運用するための証跡インフラ」** を標準化することを目的とする。

**VAPの適用対象は明確である：システム障害が人命・社会基盤・民主的制度に不可逆的な損害をもたらしうる領域。**

金融・医療・交通・エネルギー・公共政策の5領域において、AI判断の透明性と追跡可能性は任意の付加機能ではなく、社会インフラとしての必須要件である。

---

## Normative Position Statement

### The VAP/VSO/VCP Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│     VAP (Verifiable AI Provenance Framework)                    │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                    │
│     AI判断証跡の「概念・上位フレームワーク」                      │
│     全ドメイン共通の最低要件・抽象レイヤーを定義                   │
│                                                                 │
│                          ▲                                      │
│                          │ defines & maintains                  │
│                          │                                      │
│     VSO (VeritasChain Standards Organization)                   │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                   │
│     VAPを策定・維持・認証する「標準化団体」                        │
│     プロファイル間の整合性を保証                                  │
│                                                                 │
│                          │                                      │
│                          │ publishes profiles                   │
│                          ▼                                      │
│                                                                 │
│     ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│     │   VCP   │ │   DVP   │ │   MAP   │ │   PAP   │  ...      │
│     │Finance  │ │Automotive│ │Medical │ │Public  │           │
│     │Profile  │ │ Profile │ │Profile │ │Profile │           │
│     └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│                                                                 │
│     ドメイン固有の「具体プロトコル実装」                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Analogous Standards Bodies

| Standards Body | Domain | Framework/Protocol |
|----------------|--------|-------------------|
| **W3C** | Web | HTML, CSS, DOM |
| **IETF** | Network | TCP/IP, HTTP, TLS |
| **IEEE** | Electronics/Communications | 802.11 (WiFi), 1588 (PTP) |
| **FIX Trading Community** | Financial Trading | FIX Protocol |
| **VSO** | **AI Decision Provenance** | **VAP Framework, VCP, DVP, MAP...** |

**VSOは「AI判断の証跡と安全性の基盤」を定義する国際標準化団体として位置づけられる。**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [High-Risk AI Domains](#2-high-risk-ai-domains)
3. [Framework Architecture](#3-framework-architecture)
4. [Core Layers](#4-core-layers)
5. [Domain Profiles](#5-domain-profiles)
6. [Cryptographic Requirements](#6-cryptographic-requirements)
7. [Data Model](#7-data-model)
8. [Conformance Levels](#8-conformance-levels)
9. [Implementation Guidelines](#9-implementation-guidelines)
10. [Governance and Standardization](#10-governance-and-standardization)
11. [Relation to International Standards (Non-Normative)](#11-relation-to-international-standards)
12. [References](#12-references)

---

## 1. Introduction

### 1.1 Purpose

VAP（Verifiable AI Provenance Framework）は、以下の構造的課題を解消するために設計された上位フレームワークである：

| 課題 | 説明 | VAPによる解決 |
|--------|------|---------------|
| **再現不可能性** | AIの判断プロセスが再現できない | Provenance Layerによる判断由来の記録 |
| **記録欠如** | 意思決定の過程が記録されていない | Integrity Layerによる自動ロギング |
| **改ざん可能性** | 監査記録が事後的に書き換え可能 | Hash Chain + Merkle Tree による暗号的保証 |
| **責任曖昧性** | 事故時の責任主体が特定不能 | Accountability Layerによる責任境界の可視化 |

### 1.2 Design Philosophy

VAPは以下の基本理念に基づく：

> **「AIの利用を制限する規制」ではなく、「AIを安全に継続運用するための共通証跡基盤」**

AI技術の進歩を阻害することなく、その判断プロセスの透明性と追跡可能性を確保することで、社会的信頼を維持しながらAI活用を継続可能にする。

### 1.3 Scope Definition

VAPは**「システム障害が人命・社会基盤・民主的制度に重大かつ不可逆的な損害をもたらしうる領域」**を対象とする。

この定義は意図的に厳格である。VAPは汎用的なログ収集フレームワークではなく、**社会インフラとしてのAIシステムに必須となる証跡基盤**である。

### 1.4 Conformance Language

本仕様書において、以下のキーワードは RFC 2119 に準拠して解釈される：

- **MUST** / **REQUIRED** / **SHALL**: 絶対的な要件
- **MUST NOT** / **SHALL NOT**: 絶対的な禁止
- **SHOULD** / **RECOMMENDED**: 推奨事項（正当な理由がある場合は逸脱可能）
- **MAY** / **OPTIONAL**: 任意事項

### 1.5 Terminology

| Term | Definition |
|------|------------|
| **VAP** | Verifiable AI Provenance Framework - 分野横断の上位フレームワーク |
| **VSO** | VeritasChain Standards Organization - VAPを策定・維持する標準化団体 |
| **Profile** | VAPの特定ドメイン実装（VCP, DVP, MAP等） |
| **Provenance** | データの出所・由来・履歴の暗号学的に検証可能な記録 |
| **High-Risk AI** | EU AI Act Article 6に定義される高リスクAIシステム |

---

## 2. High-Risk AI Domains

### 2.1 Normative Scope Statement

**VAP（Verifiable AI Provenance Framework）は、「システム障害が人命・社会基盤・民主的制度に重大かつ不可逆的な損害をもたらしうる領域」におけるAI判断の監査基盤として設計される。**

以下の5領域は、VAPの**必須適用対象（Mandatory Application Domains）**として定義される。

### 2.2 Domain Definitions

#### 2.2.1 Financial Infrastructure（金融インフラ）

| Attribute | Value |
|-----------|-------|
| **Profile ID** | VCP (VeritasChain Protocol) |
| **Status** | v1.0 Released |
| **Risk Category** | Systemic Risk / Market Integrity |

**Scope:**
- 高頻度取引（HFT）システム
- AI/アルゴリズム駆動の取引戦略
- 取引所・清算機関・プライムブローカー
- リスク管理システム
- 与信スコアリングAI

**Failure Impact:**
- AI/HFTの異常動作による市場の急激な変動
- 年金基金・企業財務・国家財政への連鎖的影響
- システミックリスクの顕在化（2010年Flash Crash：1兆ドルが数分で蒸発）

**Regulatory Drivers:**
- EU AI Act Article 6(2) - 信用スコアリングは高リスクAI
- MiFID II Article 17 - アルゴリズム取引の監査要件
- CAT Rule 613 - 統合監査証跡

**VAP Requirements:**
- 取引イベントの暗号学的連鎖記録
- AI判断根拠（DecisionFactors）の保存
- ナノ秒精度のタイムスタンプ同期

---

#### 2.2.2 Medical and Healthcare AI（医療・ヘルスケアAI）

| Attribute | Value |
|-----------|-------|
| **Profile ID** | MAP (Medical AI Protocol) |
| **Status** | Planned |
| **Risk Category** | Patient Safety / Life-Critical |

**Scope:**
- AI診断支援システム
- 画像診断AI（放射線、病理）
- トリアージ・優先度判定AI
- 投薬推奨・薬物相互作用チェック
- 手術支援ロボットの判断ロジック

**Failure Impact:**
- 診断の誤りによる患者への直接的な健康被害
- 投薬ミスによる重篤な副作用
- トリアージ誤判定による適切な医療提供の遅延

**Regulatory Drivers:**
- EU AI Act Annex III - 医療機器AIは高リスク
- FDA AI/ML-Based SaMD Guidance
- MDR (Medical Device Regulation) 2017/745

**VAP Requirements:**
- 診断根拠の完全な記録と再構成能力
- 判断に使用したデータ・モデルバージョンの特定
- 医療事故調査・訴訟対応への証跡提供能力

---

#### 2.2.3 Transportation and Autonomous Systems（交通・自動運転）

| Attribute | Value |
|-----------|-------|
| **Profile ID** | DVP (Driving Vehicle Protocol) / AAP (Aviation AI Protocol) |
| **Status** | Planned |
| **Risk Category** | Physical Safety / Mass Casualty Prevention |

**Scope:**
- 自動運転車両（Level 3-5）
- ADAS（先進運転支援システム）
- 航空機自動操縦・航空管制AI
- 鉄道運行管理システム
- ドローン自律制御

**Failure Impact:**
- 自動運転の誤判断による交通事故
- 航空管制AIの異常動作による航空機事故リスク
- 鉄道制御の誤動作による運行障害

**Regulatory Drivers:**
- EU AI Act Annex III - 交通安全AIは高リスク
- UNECE WP.29 - 自動運転システム規則
- FAA Advisory Circular 23.1309-1E

**VAP Requirements:**
- 物理的フライトレコーダーとAI判断レコーダーの統合
- センサー入力→判断→制御出力の完全な因果連鎖記録
- リアルタイム記録とオフライン検証の両立

**Unique Characteristic:**
> **物理的フライトレコーダーに加え、AI判断レベルの証跡記録が最終形態となる領域。**

---

#### 2.2.4 Energy and Critical Infrastructure（エネルギー・社会インフラ）

| Attribute | Value |
|-----------|-------|
| **Profile ID** | EIP (Energy Infrastructure Protocol) |
| **Status** | Planned |
| **Risk Category** | Societal Continuity / Critical Infrastructure |

**Scope:**
- 電力網管理・需給バランシングAI
- 水道網監視・制御システム
- 通信インフラ管理AI
- ガスパイプライン制御
- 原子力発電所監視システム

**Failure Impact:**
- 電力網AI異常動作による大規模停電（医療機器・冷暖房への影響）
- 水道システム誤動作による水質・供給への影響
- 通信インフラ障害による緊急通報・金融システムへの波及

**Regulatory Drivers:**
- EU NIS2 Directive - 重要インフラのセキュリティ
- NERC CIP Standards - 電力系統サイバーセキュリティ
- EU AI Act - エネルギー管理AIは高リスク

**VAP Requirements:**
- AIの異常判断の原因追跡能力
- 障害復旧のための状態再構成
- カスケード障害の根本原因分析

**Unique Characteristic:**
> **社会基盤の継続性に直結するインフラ。復旧のためには判断履歴の追跡が不可欠。**

---

#### 2.2.5 Public Policy, Law Enforcement, and Justice（公共政策・治安・司法）

| Attribute | Value |
|-----------|-------|
| **Profile ID** | PAP (Public Administration Protocol) |
| **Status** | Planned |
| **Risk Category** | Democratic Integrity / Civil Rights |

**Scope:**
- 与信スコアリング・ローン審査AI
- 福祉給付判定システム
- 入国管理・ビザ審査AI
- 再犯リスク評価（recidivism prediction）
- 採用・人事評価AI

**Failure Impact:**
- 判断理由が追跡不能な場合、不服申立・司法審査が困難
- バイアスのあるAIによる不公正な判定の固定化
- 民主的統制を欠いたアルゴリズムによる意思決定

**Regulatory Drivers:**
- EU AI Act Article 6(2) - 基本的権利に影響するAIは高リスク
- GDPR Article 22 - 自動化された意思決定への異議申立権
- US Executive Order 14110 - AI安全性に関する大統領令

**VAP Requirements:**
- 個人に影響する判定の完全な説明可能性
- 事後的な監査と異議申立への対応能力
- 民主的監視のための透明性確保

**Unique Characteristic:**
> **判断理由の追跡が不可能なAIは、民主的説明責任の基盤を損なう。**

---

### 2.3 Domain Classification Matrix

| Domain | Profile | Failure Mode | Time to Impact | Reversibility |
|--------|---------|--------------|----------------|---------------|
| Financial | VCP | Systemic Instability | Milliseconds | Partial |
| Medical | MAP | Patient Harm | Minutes-Hours | Irreversible |
| Transportation | DVP/AAP | Physical Harm | Seconds | Irreversible |
| Energy | EIP | Infrastructure Disruption | Minutes-Days | Slow Recovery |
| Public Policy | PAP | Institutional Erosion | Months-Years | Difficult |

### 2.4 Common Requirements Across Domains

すべてのHigh-Risk Domainに共通する要件：

| Requirement ID | Requirement | Rationale |
|----------------|-------------|-----------|
| **HR-001** | 暗号学的完全性（Hash Chain） | 改ざん検出 |
| **HR-002** | 判断由来の記録（Provenance） | 再構成能力 |
| **HR-003** | 因果連鎖の追跡（Traceability） | 根本原因分析 |
| **HR-004** | 責任境界の明確化（Accountability） | 法的責任特定 |
| **HR-005** | 説明可能性（Explainability） | 規制・訴訟対応 |
| **HR-006** | プライバシー保護（Privacy） | GDPR対応 |

### 2.5 Domain Selection Criteria

#### 2.5.1 Selection Criteria

VAPの必須適用対象は、以下の基準に基づいて選定された：

1. **不可逆性（Irreversibility）**: 判断ミスの結果が回復困難または不可能
2. **規模（Scale）**: 個人ではなく社会全体に影響が波及
3. **速度（Velocity）**: 人間の介入が間に合わない速度で影響が拡大
4. **規制要件（Regulatory Mandate）**: 既存または計画中の規制が透明性を要求

#### 2.5.2 Strategic Implications

この5領域の明確な定義により：

| Implication | Description |
|-------------|-------------|
| **VAPの普遍性** | 金融領域に限定されない汎用フレームワークであることを明示 |
| **VAPの必然性** | AI社会基盤全体の上位レイヤーとしての位置づけを確立 |
| **参入障壁の低下** | 他分野の事業者がVAP準拠を選択する合理的理由を提供 |
| **標準乱立の防止** | 各分野での個別プロトコル乱立を防ぎ、相互運用性を確保 |
| **国際標準化の促進** | ISO等の国際標準化プロセスへの移行を円滑化 |

---

## 3. Framework Architecture

### 3.1 Layered Architecture

VAP は以下の5つの必須レイヤーから構成される：

```
┌─────────────────────────────────────────────────────────────┐
│                   Domain Profiles Layer                      │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│   │   VCP   │ │   DVP   │ │   MAP   │ │   PAP   │   ...    │
│   │(Finance)│ │ (Auto)  │ │(Medical)│ │(Public) │          │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
├─────────────────────────────────────────────────────────────┤
│                  Accountability Layer                        │
│         責任主体の識別・責任境界の定義・監査証跡              │
├─────────────────────────────────────────────────────────────┤
│                  Traceability Layer                          │
│         因果構造の再構成・時系列追跡・インシデント分析         │
├─────────────────────────────────────────────────────────────┤
│                   Provenance Layer                           │
│         Actor/Input/Context/Action/Outcome の記録            │
├─────────────────────────────────────────────────────────────┤
│                    Integrity Layer                           │
│         Hash Chain・Merkle Tree・Digital Signatures          │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Layer Dependency

各レイヤーは下位レイヤーに依存する：

```
Domain Profiles ──depends on──▶ Accountability Layer
                                       │
                               depends on
                                       ▼
                              Traceability Layer
                                       │
                               depends on
                                       ▼
                               Provenance Layer
                                       │
                               depends on
                                       ▼
                               Integrity Layer
```

### 3.3 Cross-Cutting Concerns

以下は全レイヤーに共通する横断的関心事である：

| 関心事 | 説明 | 実装要件 |
|--------|------|----------|
| **Privacy** | 個人データの保護 | Crypto-shredding, 匿名化 |
| **Security** | 暗号的安全性 | Ed25519/Dilithium, SHA-256/SHA3 |
| **Performance** | 低遅延・高スループット | Tier別の性能要件 |
| **Interoperability** | システム間連携 | JSON/SBE, 標準API |

---

## 4. Core Layers

### 4.1 Integrity Layer（暗号的完全性レイヤー）

#### 4.1.1 Purpose

すべてのAI判断イベントの改ざん不可能性を暗号学的に保証する。

#### 4.1.2 Requirements

| 要件ID | 要件 | 必須レベル |
|--------|------|------------|
| INT-001 | すべてのイベントは正規化（Canonicalization）されなければならない | MUST |
| INT-002 | 各イベントには一意識別子（UUID v7推奨）を付与しなければならない | MUST |
| INT-003 | イベントは暗号学的ハッシュ（SHA-256以上）でリンクされなければならない | MUST |
| INT-004 | ハッシュチェーンは連続性を維持しなければならない | MUST |
| INT-005 | デジタル署名またはTEE署名により否認防止を実現すべきである | SHOULD |
| INT-006 | 定期的なMerkle Tree アンカリングを行うべきである | SHOULD |

#### 4.1.3 Hash Chain Construction

```
Event_n = {
    Header,
    Payload,
    Security: {
        event_hash: H(canonical(Header) || canonical(Payload) || prev_hash),
        prev_hash: Event_(n-1).event_hash,
        signature: Sign(event_hash, private_key)
    }
}
```

**Hash Chain Validation Algorithm:**

```
Algorithm: VAP Hash Chain Validation
Input: Sequence of events E₁, E₂, ..., Eₙ
Output: VALID or INVALID with error location

1: h ← GENESIS_HASH
2: for i = 1 to n do
3:     if Eᵢ.prev_hash ≠ h then
4:         return INVALID: Chain break at event i
5:     end if
6:     h' ← H(canonical(Eᵢ.Header) || canonical(Eᵢ.Payload) || h)
7:     if h' ≠ Eᵢ.event_hash then
8:         return INVALID: Hash mismatch at event i
9:     end if
10:    h ← h'
11: end for
12: return VALID
```

#### 4.1.4 Merkle Tree Anchoring

RFC 6962（Certificate Transparency）準拠のMerkle Tree構築を**必須**とする：

```
Leaf(D) = H(0x00 || D)        // リーフノード
Node(L, R) = H(0x01 || L || R) // 内部ノード
```

**Domain Separation（0x00/0x01 prefix）は第二原像攻撃を防止するために必須である。**

#### 4.1.5 Cryptographic Algorithm Support

| Algorithm | Type | Status | Post-Quantum Safe |
|-----------|------|--------|-------------------|
| **SHA-256** | Hash | DEFAULT | Partial (128-bit effective) |
| SHA3-256 | Hash | SUPPORTED | Partial |
| BLAKE3 | Hash | SUPPORTED | Partial |
| **Ed25519** | Signature | DEFAULT | No |
| ECDSA secp256k1 | Signature | SUPPORTED | No |
| **DILITHIUM2** | Signature | FUTURE | Yes |
| FALCON-512 | Signature | FUTURE | Yes |

**Crypto Agility要件:** すべてのVAP準拠実装は、署名アルゴリズムを識別するフィールドを含み、将来のアルゴリズム移行を可能にしなければならない（MUST）。

---

### 4.2 Provenance Layer（判断由来レイヤー）

#### 4.2.1 Purpose

AIの判断由来（誰が・何を・どの環境で・何を参照して・何を出したか）を構造化して記録する。

#### 4.2.2 Abstract Data Model

VAPはドメイン非依存の抽象モデルを定義する：

```json
{
  "provenance": {
    "actor": {
      "type": "enum",           // AI_MODEL, HUMAN, EXTERNAL_AGENT, HYBRID
      "identifier": "string",   // 一意識別子
      "version": "string",      // バージョン情報（AI_MODELの場合）
      "hash": "string"          // モデルパラメータのハッシュ（AI_MODELの場合）
    },
    "input": {
      "sources": ["array"],     // 入力データソースのリスト
      "timestamp": "int64",     // 入力取得時刻
      "hash": "string"          // 入力データのハッシュ
    },
    "context": {
      "parameters": "object",   // アクティブなパラメータ
      "constraints": "object",  // 適用された制約条件
      "environment": "object"   // 実行環境情報
    },
    "action": {
      "type": "string",         // 判断/提案/推奨の種類
      "decision": "object",     // AIの判断内容
      "confidence": "string",   // 信頼度スコア（0.0-1.0）
      "explainability": {
        "method": "enum",       // SHAP, LIME, GRADCAM, RULE_TRACE, NONE
        "factors": ["array"]    // 判断に寄与した要因
      }
    },
    "outcome": {
      "result": "object",       // 実行結果
      "timestamp": "int64",     // 結果確定時刻
      "status": "enum"          // SUCCESS, FAILURE, PARTIAL, PENDING
    }
  }
}
```

#### 4.2.3 Domain Profile Mapping

| VAP Abstract | VCP (Finance) | DVP (Automotive) | MAP (Medical) | PAP (Public) |
|--------------|---------------|------------------|---------------|--------------|
| actor | Algorithm/Trader | AutonomousSystem/Driver | DiagnosticAI/Physician | ScoringAI/Officer |
| input | MarketData/Signals | SensorData/LIDAR/Camera | PatientData/Imaging | ApplicationData/Records |
| context | RiskParameters/Limits | EnvironmentConditions/Route | ClinicalProtocol/History | PolicyRules/Guidelines |
| action | TradeSignal/Order | PathPlanning/Control | Diagnosis/TreatmentPlan | Decision/Recommendation |
| outcome | Execution/Fill | VehicleState/Maneuver | PatientOutcome/Response | Determination/Appeal |

---

### 4.3 Traceability Layer（追跡可能性レイヤー）

#### 4.3.1 Purpose

判断チェーンを時系列および因果構造で再構成可能にする。

#### 4.3.2 Requirements

| 要件ID | 要件 | 必須レベル |
|--------|------|------------|
| TRC-001 | イベント間の因果関係を表現できなければならない | MUST |
| TRC-002 | trace_id により関連イベントをグループ化できなければならない | MUST |
| TRC-003 | 任意の時点でのシステム状態を再構成できるべきである | SHOULD |
| TRC-004 | 根本原因分析（RCA）を支援するクエリ機能を提供すべきである | SHOULD |

#### 4.3.3 Causal Chain Model

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Input   │────▶│ Action  │────▶│ Outcome │────▶│ Impact  │
│ Event   │     │ Event   │     │ Event   │     │ Event   │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     └───────────────┴───────────────┴───────────────┘
                          │
                    [trace_id: common]
```

#### 4.3.4 Domain-Specific Causal Chains

**Finance (VCP):**
```
Signal Generated (SIG) → Order Sent (ORD) → Acknowledged (ACK) → Executed (EXE) → Position Closed (CLS)
```

**Automotive (DVP):**
```
Sensor Input → Perception → Path Planning → Control Command → Vehicle State
```

**Medical (MAP):**
```
Patient Data → Analysis → Diagnosis → Treatment Plan → Outcome
```

**Public (PAP):**
```
Application → Evaluation → Scoring → Decision → Notification → Appeal
```

---

### 4.4 Accountability Layer（責任境界レイヤー）

#### 4.4.1 Purpose

AI関与の判断において、責任主体を特定可能にする。

#### 4.4.2 Actor Types

| Actor Type | 説明 | 例 |
|------------|------|-----|
| **MODEL_DEVELOPER** | AIモデルの開発者 | 機械学習エンジニア |
| **AI_PROVIDER** | AIシステムの提供者 | SaaSベンダー |
| **OPERATOR** | 運用者・オペレーター | トレーダー、ドライバー、医師 |
| **DATA_VENDOR** | データ提供者 | マーケットデータベンダー |
| **FINAL_DECISION_MAKER** | 最終意思決定者 | リスクマネージャー |

#### 4.4.3 Responsibility Schema

```json
{
  "accountability": {
    "operator_id": "string",           // 運用者識別子
    "last_approval_by": "string",      // 最終承認者
    "approval_timestamp": "int64",     // 承認時刻
    "delegation_chain": [              // 委任チェーン
      {
        "delegator": "string",
        "delegatee": "string",
        "scope": "string",
        "valid_from": "int64",
        "valid_until": "int64"
      }
    ],
    "override_history": [              // 上書き履歴
      {
        "original_action": "object",
        "override_action": "object",
        "override_by": "string",
        "reason": "string",
        "timestamp": "int64"
      }
    ]
  }
}
```

#### 4.4.4 Human Oversight Requirements

EU AI Act Article 14（Human Oversight）への対応：

| 要件 | VAP実装 |
|------|---------|
| 人間による監視の有効化 | operator_id フィールド |
| 介入能力 | HALT/OVERRIDE イベントタイプ |
| オーバーライド機能 | override_history 記録 |

---

### 4.5 Domain Profiles Layer（領域プロファイルレイヤー）

#### 4.5.1 Purpose

VAP共通レイヤーの上に、ドメイン固有の拡張を定義する。

#### 4.5.2 Profile Registry

| Profile ID | Domain | Status | Specification |
|------------|--------|--------|---------------|
| **VCP** | Finance / Algorithmic Trading | **v1.0 Released** | VSO-VCP-SPEC-001 |
| DVP | Automotive / Autonomous Driving | Planned | - |
| AAP | Aviation / Air Traffic Control | Planned | - |
| MAP | Medical / Healthcare AI | Planned | - |
| EIP | Energy / Critical Infrastructure | Planned | - |
| PAP | Public Sector / Government AI | Planned | - |

#### 4.5.3 Profile Extension Mechanism

各プロファイルは以下の拡張ポイントを定義できる：

```json
{
  "profile_extension": {
    "profile_id": "string",
    "profile_version": "string",
    "domain_specific_modules": ["array"],
    "domain_specific_events": ["array"],
    "domain_specific_constraints": {
      "timestamp_precision": "enum",
      "clock_sync_requirement": "enum"
    }
  }
}
```

---

## 5. Domain Profiles

### 5.1 VCP: Finance Profile

**Status:** v1.0 Released  
**Document:** VSO-VCP-SPEC-001

#### 5.1.1 Overview

VCP（VeritasChain Protocol）は、VAP の金融ドメインプロファイルであり、アルゴリズム取引・AI駆動取引システムの監査証跡を標準化する。

**VCPはVAPファミリーの最初の実装プロファイルであり、金融・アルゴリズム取引ドメインにおける証跡標準として位置づけられる。**

#### 5.1.2 Domain-Specific Modules

| Module | Purpose | VAP Layer Mapping |
|--------|---------|-------------------|
| **VCP-CORE** | 標準ヘッダー・セキュリティ | Integrity Layer |
| **VCP-TRADE** | 取引ペイロード | Provenance Layer (action/outcome) |
| **VCP-GOV** | アルゴリズムガバナンス | Provenance Layer (actor/context) |
| **VCP-RISK** | リスクパラメータ記録 | Provenance Layer (context) |
| **VCP-PRIVACY** | Crypto-shredding | Cross-cutting (Privacy) |
| **VCP-RECOVERY** | チェーン復旧 | Integrity Layer |

#### 5.1.3 Compliance Tiers

| Tier | Target | Clock Sync | Signature | Anchor Frequency |
|------|--------|------------|-----------|------------------|
| **Platinum** | HFT/Exchange | PTPv2 (<1µs) | Ed25519 (Hardware) | 10 minutes |
| **Gold** | Institutional | NTP (<1ms) | Ed25519 (Client) | 1 hour |
| **Silver** | Retail/MT4/5 | Best-effort | Ed25519 (Delegated) | 24 hours |

#### 5.1.4 Regulatory Compliance

| Regulation | VCP Module | Implementation |
|------------|------------|----------------|
| EU AI Act Art. 12 | VCP-CORE | 自動イベントロギング |
| EU AI Act Art. 13 | VCP-GOV | DecisionFactors |
| EU AI Act Art. 14 | VCP-GOV | OperatorID, LastApprovalBy |
| MiFID II Art. 17 | VCP-GOV | AlgoID, TestingRecordLink |
| MiFID II RTS 25 | VCP-CORE | ClockSyncStatus |
| GDPR Art. 17 | VCP-PRIVACY | Crypto-shredding |

---

### 5.2 Future Profiles (Planned)

#### 5.2.1 DVP: Automotive Profile

**Scope:** 自動運転車両、ADAS、ドローン

**Key Events:**
- SENSOR_INPUT, PERCEPTION, PATH_PLANNING, CONTROL_COMMAND
- TAKEOVER_REQUEST, EMERGENCY_STOP, COLLISION_WARNING

#### 5.2.2 MAP: Medical Profile

**Scope:** AI診断、画像解析、投薬支援、手術ロボット

**Key Events:**
- IMAGING_ACQUIRED, ANALYSIS_COMPLETED, DIAGNOSIS_SUGGESTED
- PHYSICIAN_REVIEWED, TREATMENT_PROPOSED, PATIENT_CONSENTED

#### 5.2.3 PAP: Public Administration Profile

**Scope:** 与信スコア、福祉判定、入国管理、採用AI

**Key Events:**
- APPLICATION_RECEIVED, EVALUATION_STARTED, SCORING_COMPLETED
- DECISION_MADE, NOTIFICATION_SENT, APPEAL_FILED

---

## 6. Cryptographic Requirements

### 6.1 Algorithm Requirements

#### 6.1.1 Hash Functions

| Requirement | Specification |
|-------------|---------------|
| Minimum Security | 128-bit effective security |
| Default Algorithm | SHA-256 |
| Alternative Algorithms | SHA3-256, BLAKE3 |
| Collision Resistance | MUST resist birthday attacks |

#### 6.1.2 Digital Signatures

| Requirement | Specification |
|-------------|---------------|
| Default Algorithm | Ed25519 |
| Key Size | 256-bit (Ed25519) |
| Signature Size | 64 bytes (Ed25519) |
| Future Migration | DILITHIUM2, FALCON-512 |

### 6.2 Quantum Resistance

#### 6.2.1 Threat Analysis

```
Current Ed25519 Security:
- Classical Attack: O(2^128) operations
- Quantum Attack (Shor): O((log n)³) with ~2,000-4,000 logical qubits

Hash Function (SHA-256):
- Classical Preimage: O(2^256)
- Quantum Preimage (Grover): O(2^128) — Still secure
```

**Key Insight:** VAPのハッシュチェーン完全性は量子攻撃後も維持される。

#### 6.2.2 Migration Path

```
Phase 1 (Current): Ed25519 + SHA-256
Phase 2 (Hybrid):  Ed25519 || Dilithium (dual signature)
Phase 3 (PQC):     Dilithium2 + SHA3-256
```

### 6.3 Crypto-Shredding for Privacy

#### 6.3.1 Mechanism

```
Before Key Destruction:
  Encrypted Data + Encryption Key → Original Data

After Key Destruction:
  Encrypted Data + [KEY DESTROYED] → Mathematically Unrecoverable
```

#### 6.3.2 Hash Chain Preservation

| Component | After Crypto-Shredding |
|-----------|------------------------|
| Hash Chain Structure | ✅ Intact |
| Merkle Tree | ✅ Intact |
| Cryptographic Proofs | ✅ Verifiable |
| Original Data | ❌ Permanently unrecoverable |

---

## 7. Data Model

### 7.1 Common Event Structure

すべてのVAP準拠イベントは以下の構造を持つ：

```json
{
  "vap_version": "1.1",
  "profile": {
    "id": "string",
    "version": "string"
  },
  "header": {
    "event_id": "uuid_v7",
    "trace_id": "uuid_v7",
    "timestamp_int": "int64",
    "timestamp_iso": "string",
    "timestamp_precision": "enum",
    "event_type": "string",
    "event_type_code": "uint8"
  },
  "provenance": {
    "actor": { },
    "input": { },
    "context": { },
    "action": { },
    "outcome": { }
  },
  "accountability": {
    "operator_id": "string",
    "last_approval_by": "string",
    "approval_timestamp": "int64"
  },
  "domain_payload": { },
  "security": {
    "event_hash": "string",
    "prev_hash": "string",
    "hash_algo": "enum",
    "signature": "string",
    "sign_algo": "enum",
    "signer_id": "string"
  }
}
```

### 7.2 Numeric Precision

**すべての数値はstring型でエンコードしなければならない（MUST）。**

```json
// ✅ Correct
{ "price": "123.456789", "quantity": "1000.00" }

// ❌ Wrong
{ "price": 123.456789, "quantity": 1000 }
```

### 7.3 Canonicalization

JSON の正規化は RFC 8785（JSON Canonicalization Scheme）に従わなければならない（MUST）。

---

## 8. Conformance Levels

### 8.1 Level Definitions

| Level | Description | Requirements |
|-------|-------------|--------------|
| **VAP-Core** | 最小準拠 | Integrity Layer必須要件のみ |
| **VAP-Standard** | 標準準拠 | Core + Provenance + Traceability |
| **VAP-Full** | 完全準拠 | Standard + Accountability + Profile Extensions |

### 8.2 Certification Program

| Certification | Level | Requirements |
|---------------|-------|--------------|
| **VAP-Ready** | Core | 基本テスト合格 |
| **VAP-Compliant** | Standard | 標準テスト合格 + 監査 |
| **VAP-Certified** | Full | 完全テスト合格 + 第三者監査 |

---

## 9. Implementation Guidelines

### 9.1 Sidecar Pattern

既存システムへの非侵入的統合を推奨する：

```
┌─────────────────────────────────────────────────┐
│                Existing System                   │
│                                                  │
└──────────────────────┬───────────────────────────┘
                       │ Events
                       ▼
┌──────────────────────────────────────────────────┐
│              VAP Sidecar Process                  │
│  Event Capture → Chain Builder → Merkle Anchor   │
└──────────────────────────────────────────────────┘
```

### 9.2 Integration Patterns

| Pattern | Use Case | Complexity |
|---------|----------|------------|
| **Sidecar** | Legacy system integration | Low |
| **SDK** | New application development | Medium |
| **Middleware** | Enterprise gateway | High |
| **Native** | Ground-up implementation | Very High |

---

## 10. Governance and Standardization

### 10.1 VSO Structure

```
VeritasChain Standards Organization (VSO)
├── Technical Committee
│   ├── Core Working Group (VAP Framework)
│   ├── Finance Working Group (VCP)
│   ├── Automotive Working Group (DVP)
│   ├── Medical Working Group (MAP)
│   └── Public Sector Working Group (PAP)
├── Certification Authority
│   └── Conformance Testing
└── Advisory Board
    ├── Industry Representatives
    └── Regulatory Liaisons
```

### 10.2 Standardization Roadmap

| Phase | Timeline | Activities |
|-------|----------|------------|
| **Phase 1** | 2025 Q1-Q2 | VCP v1.0 Release, VAP Framework Draft |
| **Phase 2** | 2025 Q3-Q4 | VAP v1.0 Formalization, IETF Internet-Draft |
| **Phase 3** | 2026 | ISO TC 68 Submission, DVP/MAP Development |
| **Phase 4** | 2027+ | International Standard, PQC Migration |

### 10.3 Change Management

仕様変更は以下のプロセスに従う：

1. **RFC（Request for Comments）** 提出
2. **Public Review** 期間（30日）
3. **Technical Committee** 審議
4. **Vote**（2/3多数で承認）
5. **Release**

---

## 11. Relation to International Standards (Non-Normative)

### 11.1 Broader AI Provenance Framework Context

VCPは、将来的に他分野でも使えるVerifiable AI Provenance（VAP）の**金融プロファイル版**として設計されている。

### 11.2 Standards Landscape

| Domain | Existing Standards | VAP Profile Role |
|--------|-------------------|------------------|
| Financial Trading | FIX, ISO 20022 | VCP complements existing formats with provenance |
| Automotive | ISO 26262, UNECE WP.29 | DVP adds AI decision provenance to safety standards |
| Medical Devices | IEC 62304, FDA SaMD | MAP adds AI explainability to device logging |
| Critical Infrastructure | IEC 62443, NERC CIP | EIP adds AI provenance to SCADA/ICS logging |

### 11.3 Future Standardization

VSOは以下の標準化活動を計画している：

| Target | Timeline | Status |
|--------|----------|--------|
| IETF Internet-Draft | 2025 Q3 | Planned |
| ISO/TC 68 (Financial Services) | 2026 | Planned |
| ISO/IEC JTC 1/SC 42 (AI) | 2026-2027 | Planned |
| IEEE Standards Association | 2027+ | Under consideration |

---

## 12. References

### 12.1 Standards

| Standard | Description |
|----------|-------------|
| RFC 9562 | UUID v7 |
| RFC 8785 | JSON Canonicalization Scheme |
| RFC 6962 | Certificate Transparency |
| RFC 8032 | Ed25519 Digital Signature |
| IEEE 1588-2019 | Precision Time Protocol |

### 12.2 Regulations

| Regulation | Jurisdiction | Relevance |
|------------|--------------|-----------|
| EU AI Act | European Union | High-Risk AI Classification |
| MiFID II | European Union | Financial Trading |
| GDPR | European Union | Data Privacy |
| CAT Rule 613 | United States | Consolidated Audit Trail |
| NIS2 Directive | European Union | Critical Infrastructure |

### 12.3 Related VSO Documents

| Document ID | Title |
|-------------|-------|
| VSO-VCP-SPEC-001 | VeritasChain Protocol Specification v1.0 |
| VSO-SDK-SPEC-001 | VCP SDK Specification v1.0 |
| VSO-TEST-001 | VCP Conformance Test Guide v1.0 |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **VAP** | Verifiable AI Provenance Framework - 分野横断の上位フレームワーク |
| **VSO** | VeritasChain Standards Organization - VAPを策定・維持する標準化団体 |
| **VCP** | VeritasChain Protocol - VAP Finance Profile |
| **DVP** | Driving Vehicle Protocol - VAP Automotive Profile |
| **MAP** | Medical AI Protocol - VAP Medical Profile |
| **PAP** | Public Administration Protocol - VAP Public Sector Profile |
| **EIP** | Energy Infrastructure Protocol - VAP Energy Profile |
| **AAP** | Aviation AI Protocol - VAP Aviation Profile |
| **Provenance** | データの出所・由来・履歴の暗号学的に検証可能な記録 |
| **High-Risk AI** | EU AI Act Article 6に定義される高リスクAIシステム |

---

## Appendix B: Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-12-11 | Initial Release | VSO Technical Committee |
| 1.1.0 | 2025-12-11 | Added High-Risk AI Domains, VSO/VAP/VCP hierarchy clarification | VSO Technical Committee |

---

## Appendix C: License

This specification is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

---

## Contact Information

**VeritasChain Standards Organization (VSO)**  
Website: https://veritaschain.org  
Email: standards@veritaschain.org  
Technical: technical@veritaschain.org  
GitHub: https://github.com/veritaschain

---

## Declaration

> **VAP（Verifiable AI Provenance Framework）は、AI社会基盤の最上位概念として、
> 「システム障害が人命・社会基盤・民主的制度に重大かつ不可逆的な損害をもたらしうる領域」における
> AI判断の証跡と安全性の基盤を定義する。**
>
> VSOは、W3C（Web）、IETF（Network）、IEEE（Communications）、FIX（Financial Trading）と並ぶ、
> **AI判断証跡の国際標準化団体**として、このフレームワークを策定・維持する。
>
> VCPは、VAPファミリーの最初の実装プロファイルであり、
> 金融・アルゴリズム取引ドメインにおける証跡標準として運用されている。

---

*"Encoding Trust in the AI Age"*

*End of Verifiable AI Provenance Framework (VAP) Specification v1.1*

---
title: "Claude Code API 키 설정, 가장 먼저 조심해야 할 것"
date: 2026-05-07 09:30:00 +0900
categories: [AI]
tags: [claude-code, api-key, security]
excerpt: "Claude Code API 키를 발급하고 안전하게 설정하는 방법을 정리한다."
---

이 글은 Claude Code 정리 시리즈의 3번째 글입니다. 앞선 글에서 Claude Code가 단순 자동완성 도구가 아니라 개발 에이전트에 가깝다는 이야기를 했다면, 여기서는 실제로 쓰기 위해 알아야 할 한 가지 주제를 조금 더 구체적으로 정리합니다.

Claude Code는 강력하지만, 처음부터 모든 기능을 한꺼번에 익힐 필요는 없습니다. 설치, 권한, 메모리, Git, Hooks처럼 자주 부딪히는 부분을 하나씩 나눠 이해하면 훨씬 덜 부담스럽습니다.

## 먼저 이해할 것

Claude Code API 키를 발급하고 안전하게 설정하는 방법을 정리한다.

---

> 💡 **이 챕터에서 배우는 것**: API 키 발급, 안전한 설정 방법, 요금제 선택 가이드

전제 지식

[설치 가이드](https://claude-code-playbook-nu.vercel.app/docs/level-1/installation)를 먼저 완료해야 합니다.

---

## API 키란?

API 키는 Claude AI 서비스에 접근하기 위한 **인증 암호**입니다. Claude Code가 Anthropic 서버와 통신할 때 사용합니다.

중요

API 키는 절대 공개 저장소(GitHub 등)에 올리지 마세요. 유출 시 요금이 청구될 수 있습니다.

---

## API 키 발급 방법

### 1단계: Anthropic Console 접속

[console.anthropic.com](https://console.anthropic.com/) 접속 → 계정 생성 또는 로그인

### 2단계: API Keys 메뉴 이동

좌측 사이드바 → **API Keys** 클릭

### 3단계: 새 API 키 생성

**Create Key** 버튼 클릭 → 키 이름 입력 (예: `claude-code-personal`) → **Create Key**

### 4단계: API 키 복사

생성된 키(`sk-ant-api03-...`)를 복사합니다. **이 화면을 벗어나면 다시 볼 수 없으니** 안전한 곳에 보관하세요.

---

## API 키 설정 방법

### 방법 1: Claude Code 대화형 설정 (권장)

처음 실행 시 API 키 입력 프롬프트가 나타납니다.

```
claude# 복사한 키를 붙여넣고 Enter
```

### 방법 2: 환경변수로 설정

```
export ANTHROPIC_API_KEY="sk-ant-api03-..."claude
```

### 방법 3: 셸 설정 파일에 영구 저장

**macOS (zsh 사용 시, 기본 셸):**

```
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-..."' >> ~/.zshrcsource ~/.zshrc
```

**macOS/Linux (bash 사용 시):**

```
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-..."' >> ~/.bashrcsource ~/.bashrc
```

**Windows PowerShell:**

```
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-api03-...", "User")
```

---

## 요금제 이해하기

Claude Code는 Anthropic API를 사용하므로 사용량에 따라 비용이 발생합니다.

### 가격 구조 (2026년 기준)

|모델|가격|특징|
|---|---|---|
|Claude Haiku|저렴|빠름, 간단한 작업|
|Claude Sonnet|중간|균형, **기본값**|
|Claude Opus|고가|최고 성능|

> 정확한 가격은 [Anthropic 공식 요금 페이지](https://www.anthropic.com/pricing)를 확인하세요.

### 실제 사용량 예시

일반적인 개발 세션(30분):

- 소규모 버그 수정: **$0.01 ~ $0.05**
- 새 기능 구현: **$0.10 ~ $0.50**
- 대규모 리팩토링: **$0.50 ~ $2.00**

### 비용 관리 팁

1. **크레딧 한도 설정**: Console → Settings → Limits에서 월별 사용 한도 설정
2. **Haiku 모델 사용**: 간단한 작업은 Haiku로 (`/model claude-haiku-4-5-20251001`)
3. **캐싱 활용**: 동일 컨텍스트 반복 시 프롬프트 캐싱으로 최대 90% 절감

---

## 무료로 시작하는 방법

### Claude.ai 구독자 (Max 플랜)

Claude.ai Max 구독자는 Claude Code를 추가 비용 없이 사용할 수 있습니다.

```
claude# "Login with Claude.ai" 옵션 선택
```

### API 크레딧 방식

Anthropic Console에서 카드를 등록하고, 최소 $5부터 충전해서 시작할 수 있습니다.

---

## 보안 모범 사례

`.gitignore`에 반드시 추가:

```
.env*.env
```

**절대 하지 말아야 할 것:**

- API 키를 코드에 하드코딩
- GitHub, GitLab 등 공개 저장소에 키 업로드

**만약 키가 유출됐다면:**

1. 즉시 Console → API Keys → 해당 키 비활성화
2. 새 키 발급
3. 모든 환경에서 키 교체

---

## 핵심 정리

- API 키는 [console.anthropic.com](https://console.anthropic.com/)에서 발급
- 환경변수 `ANTHROPIC_API_KEY`로 설정하는 것이 안전
- 사용량에 따라 비용 발생 → 월 한도 설정 권장
- Claude.ai Max 플랜 구독자는 추가 비용 없음

---

## whalelake Note

Claude Code를 잘 쓰는 핵심은 기능을 많이 아는 것보다 작업의 경계를 분명히 주는 데 있습니다. 어떤 파일을 고쳐도 되는지, 어떤 명령을 실행해도 되는지, 어떤 기준으로 완료를 판단할지 알려줄수록 에이전트는 더 안정적으로 움직입니다.

이 글에서 다룬 내용도 결국 같은 방향을 가리킵니다. Claude Code에게 모든 것을 맡기는 것이 아니라, 반복되는 설명과 확인 과정을 구조화해서 개발자가 더 중요한 판단에 집중하도록 만드는 것입니다.

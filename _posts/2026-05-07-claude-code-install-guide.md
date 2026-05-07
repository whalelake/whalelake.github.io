---
title: "Claude Code 설치, 시작 전에 막히지 않으려면"
date: 2026-05-07 09:20:00 +0900
categories: [AI]
tags: [claude-code, installation, developer-tools]
excerpt: "Claude Code를 설치하기 전에 필요한 준비물과 설치 확인 흐름을 정리한다."
faqs:
  - question: "Claude Code 설치, 시작 전에 막히지 않으려면를 다룰 때 가장 먼저 확인할 점은 무엇인가요?"
    answer: "먼저 Claude Code 설치, 시작 전에 막히지 않으려면의 핵심 개념과 실제 작업 환경에서 필요한 전제 조건을 확인하는 것이 좋습니다."
  - question: "Claude Code를 쓸 때 SEO/AEO 관점에서 중요한 점은 무엇인가요?"
    answer: "단순 기능 소개보다 사용자가 바로 따라 할 수 있는 절차, 주의점, 자주 묻는 질문을 함께 정리하는 것이 좋습니다."
  - question: "이 글을 읽고 바로 해볼 수 있는 다음 행동은 무엇인가요?"
    answer: "본문의 체크 포인트를 기준으로 내 프로젝트에 적용할 설정 하나를 고르고, 작은 예제로 먼저 검증해보면 됩니다."
---

## 핵심 요약

- Claude Code를 설치하기 전에 필요한 준비물과 설치 확인 흐름을 정리한다.
- AI 도구와 워크플로 관점에서 먼저 알아야 할 개념과 실제 적용할 때의 판단 기준을 나눠 봅니다.
- 검색으로 들어온 독자와 AI 답변 엔진이 핵심을 바로 이해할 수 있도록 질문과 답 형태로 정리합니다.

이 글은 Claude Code 정리 시리즈의 2번째 글입니다. 앞선 글에서 Claude Code가 단순 자동완성 도구가 아니라 개발 에이전트에 가깝다는 이야기를 했다면, 여기서는 실제로 쓰기 위해 알아야 할 한 가지 주제를 조금 더 구체적으로 정리합니다.

Claude Code는 강력하지만, 처음부터 모든 기능을 한꺼번에 익힐 필요는 없습니다. 설치, 권한, 메모리, Git, Hooks처럼 자주 부딪히는 부분을 하나씩 나눠 이해하면 훨씬 덜 부담스럽습니다.

## 먼저 이해할 것

Claude Code를 설치하기 전에 필요한 준비물과 설치 확인 흐름을 정리한다.

---

> 💡 **이 챕터에서 배우는 것**: Claude Code 설치 전 준비물, OS별 설치 방법, 설치 확인

전제 지식

이 챕터를 시작하기 전에 필요한 것:

- 인터넷 연결
- 터미널(명령 프롬프트/PowerShell/Terminal) 기본 사용법

---

## 설치 전 준비물

|항목|버전|확인 방법|
|---|---|---|
|Node.js|**18 이상** (LTS 권장)|`node --version`|
|npm|Node.js와 함께 설치됨|`npm --version`|
|Anthropic API 키|—|[다음 챕터](https://claude-code-playbook-nu.vercel.app/docs/level-1/api-key-setup)에서 설명|

### Node.js 설치 (아직 없다면)

**공식 다운로드**: [nodejs.org](https://nodejs.org/) → LTS 버전 선택

Windows에서 Node.js 설치macOS에서 Node.js 설치Linux(Ubuntu/Debian)에서 Node.js 설치

---

## Claude Code 설치

준비가 됐다면 이 명령 하나로 설치합니다:

```
npm install -g @anthropic-ai/claude-code
```

> `-g` 옵션: 전역(global) 설치. 어느 디렉토리에서든 `claude` 명령을 사용할 수 있습니다.

### Windows 사용자 주의사항

Windows PowerShell에서 권한 오류가 날 경우:

```
# PowerShell을 관리자 권한으로 열고 실행Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

또는 **PowerShell 대신 Git Bash** 사용을 권장합니다.

---

## 설치 확인

```
claude --version
```

정상 출력 예 (버전 번호는 설치 시점에 따라 다릅니다):

```
1.x.x (Claude Code)
```

---

## 첫 실행 및 API 키 설정

```
claude
```

처음 실행하면 API 키를 입력하라는 안내가 나옵니다:

```
Welcome to Claude Code!Please enter your Anthropic API key to get started.You can find your API key at https://console.anthropic.com/API key: sk-ant-...
```

API 키 발급 방법은 [다음 챕터](https://claude-code-playbook-nu.vercel.app/docs/level-1/api-key-setup)에서 자세히 설명합니다.

---

## 자주 겪는 설치 문제

### 문제 1: `npm: command not found`

Node.js가 설치되지 않은 상태. 위의 Node.js 설치 과정을 먼저 진행하세요.

### 문제 2: `EACCES: permission denied` (macOS/Linux)

```
# npm 전역 디렉토리 권한 문제# 해결 방법: npm 전역 디렉토리 변경mkdir ~/.npm-globalnpm config set prefix ~/.npm-globalecho 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrcsource ~/.bashrcnpm install -g @anthropic-ai/claude-code
```

### 문제 3: 설치 후 `claude` 명령이 없다고 나올 때

터미널을 완전히 닫고 다시 열어보세요. PATH 환경변수가 새로 적용됩니다.

### 문제 4: 회사 네트워크에서 설치 실패

프록시 설정이 필요할 수 있습니다:

```
npm config set proxy http://프록시주소:포트npm config set https-proxy http://프록시주소:포트npm install -g @anthropic-ai/claude-code
```

---

## 핵심 정리

- Claude Code는 **Node.js 18+** 필요
- `npm install -g @anthropic-ai/claude-code` 명령으로 설치
- 설치 후 `claude --version`으로 확인
- API 키는 다음 챕터에서 발급

---

## whalelake Note

Claude Code를 잘 쓰는 핵심은 기능을 많이 아는 것보다 작업의 경계를 분명히 주는 데 있습니다. 어떤 파일을 고쳐도 되는지, 어떤 명령을 실행해도 되는지, 어떤 기준으로 완료를 판단할지 알려줄수록 에이전트는 더 안정적으로 움직입니다.

이 글에서 다룬 내용도 결국 같은 방향을 가리킵니다. Claude Code에게 모든 것을 맡기는 것이 아니라, 반복되는 설명과 확인 과정을 구조화해서 개발자가 더 중요한 판단에 집중하도록 만드는 것입니다.

## 자주 묻는 질문

### Claude Code 설치, 시작 전에 막히지 않으려면를 다룰 때 가장 먼저 확인할 점은 무엇인가요?

먼저 Claude Code 설치, 시작 전에 막히지 않으려면의 핵심 개념과 실제 작업 환경에서 필요한 전제 조건을 확인하는 것이 좋습니다.

### Claude Code를 쓸 때 SEO/AEO 관점에서 중요한 점은 무엇인가요?

단순 기능 소개보다 사용자가 바로 따라 할 수 있는 절차, 주의점, 자주 묻는 질문을 함께 정리하는 것이 좋습니다.

### 이 글을 읽고 바로 해볼 수 있는 다음 행동은 무엇인가요?

본문의 체크 포인트를 기준으로 내 프로젝트에 적용할 설정 하나를 고르고, 작은 예제로 먼저 검증해보면 됩니다.

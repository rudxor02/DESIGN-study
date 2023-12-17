# DESIGN-study

# Week 1

event emitter 구현

## 패키지 설치

```bash
pip3 install pydantic pytest pynput pytest-asyncio 
```

## execute

```bash
PYTHONPATH=. python3 week1/main.py
```

## test

```bash
pytest week1/test/
```

# Week2

nestpy 구현 (base dir은 `week2/` 입니다)

대략적인 동작 원리는 다음과 같습니다.

1. decorator에서 class에 token을 달아줍니다.
2. root module을 register하면 해당 module에 의존성이 있는 module, controller, provider 등을 재귀적으로 register하고, instantiate합니다.
3. controller는 method decorator에서 method (function) 객체에 api에 관한 정보들을 달아줍니다.
4. handler builder가 이 정보들을 모아서 handler를 생성합니다.

## 패키지 설치

```bash
poetry install
```

## cats 서버 실행

```bash
poetry run main.py
```

## cats 서버 test (create, list, retrieve)

매 테스트 전 서버를 켜고 진행해 주세요

```bash
poetry run pytest tests/ -m cats
```

## token (DI) test

```bash
poetry run pytest tests/ -m token
```

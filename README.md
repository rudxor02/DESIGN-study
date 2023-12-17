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

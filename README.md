# slack_databot
----

slack 에 여러 기능을 붙혀 사용하기 위해 만들었습니다.

## python 3.10 이용 (3.10)

## 실행 방법

### clone, .env 생성

```shell
git clone git@github.com:J-TKim/slack_bot.git
cp .env_example .env
```

### .env 설정
.env 파일에 필요한 환경변수를 설정합니다.

### run with docker

```shell
docker build -t ${TAG_NAME} . 
docker run --rm -p 30100:30100 ${TAG_NAME}
```

### run in local
```shell
uvicorn --host=0.0.0.0 --port ${PORT} main:app --reload
```
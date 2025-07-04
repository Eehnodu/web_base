# 🧱 Base Project (FastAPI + SQLAlchemy + Alembic)

이 프로젝트는 FastAPI 기반 백엔드 시스템을 개발하기 위한 **기본 골격(base structure)**을 제공합니다.  
API 개발, 데이터베이스 연동, 계층 분리, 마이그레이션 관리까지 모두 포함되어 있어 실무 프로젝트에 바로 활용할 수 있습니다.

---

## 🗂 프로젝트 구조

```
back/
├── app/
│   ├── config/           # 전역 설정 (환경변수, 서비스 구분 등)
│   ├── middlewares/      # 미들웨어 설정 (예: CORS)
│   ├── models/           # SQLAlchemy 모델 정의
│   ├── schemas/          # 요청/응답 Pydantic 스키마 정의
│   ├── repository/       # DB 접근 계층 (CRUD 분리)
│   ├── services/         # 비즈니스 로직 처리 계층
│   ├── routers/          # API 라우팅 정의
│   ├── database.py       # DB 연결 및 세션/엔진 설정
│   └── main.py           # 앱 초기화, 미들웨어, 라우터 등록
├── alembic/              # Alembic 마이그레이션 디렉토리
├── alembic.ini           # Alembic 설정 파일
├── migrations.sh         # 마이그레이션 자동 스크립트
├── run.sh                # 로컬 서버 실행 스크립트
├── .env                  # 환경변수 파일
└── requirements.txt      # 의존성 목록

front/
├── public/                    # 정적 파일 (favicon 등)
├── src/
│   ├── pages/                 # 페이지 단위 구성 (ex: Home, Login)
│   │   └── Home/
│   │       ├── index.tsx      # 페이지 컴포넌트
│   │       ├── hooks.ts       # 해당 페이지용 훅
│   │       └── style.css      # Tailwind 기반 커스텀 스타일
│   ├── components/           # 공통 컴포넌트
│   ├── hooks/                # 전역 커스텀 훅
│   ├── styles/               # 전역 스타일 설정
│   ├── App.tsx               # 라우팅 및 전체 구조
│   ├── main.tsx              # 앱 엔트리 포인트
│   └── router.tsx            # React Router 설정
├── index.html                # Vite 루트 HTML
├── tailwind.config.js        # Tailwind 설정
├── postcss.config.js         # PostCSS 설정
├── package.json              # 프론트엔드 의존성 및 스크립트
└── tsconfig.json             # TypeScript 설정
```

---

## ⚙️ 주요 구성 요소 설명

### ✅ FastAPI

- Python 기반 비동기 웹 프레임워크
- Swagger 자동 문서화 (`/docs`), ReDoc (`/redoc`)

### ✅ SQLAlchemy (ORM)

- 객체 지향적으로 DB 테이블 모델링
- DB 스키마 변경 시 Alembic과 함께 자동 반영 가능

### ✅ Alembic

- 마이그레이션 도구 (스키마 버전 관리)
- `models.py`를 기준으로 실제 DB에 변경사항을 적용

### ✅ Pydantic

- 입력/출력 유효성 검사
- `schemas/`에서 정의하여 라우터와 분리된 검증 처리

---

## 🚀 실행 방법

### 1. 환경 설정

`.env` 파일 생성:

<pre><code># 로컬 환경 DB
local_mysql_user=root
local_mysql_password=1234
local_mysql_host=localhost
local_mysql_db=example_local

# 운영 환경 DB
prod_mysql_user=admin
prod_mysql_password=securepass
prod_mysql_host=db.prod.host
prod_mysql_db=example_prod
</code></pre>

> `settings.py`는 hostname을 기준으로 자동으로 local/prod 환경을 감지합니다.

---

### 2. 패키지 설치

```bash
cd back
pip install -r requirements.txt
```

---

### 3. DB 마이그레이션 (초기 테이블 생성)

```bash
sh migrations.sh
```

> 내부 명령:
>
> ```bash
> alembic revision --autogenerate -m "init"
> alembic upgrade head
> ```

---

### 4. 서버 실행

```bash
sh run.sh
```

> 실행 결과: [http://127.0.0.1:8000](http://127.0.0.1:8000) 에서 앱 실행

---

### 5. 프론트엔드 실행

```bash
cd front
npm install
npm run dev
```

> Vite 개발 서버: [http://localhost:3000](http://localhost:3000)

---

## 🧠 개발 흐름 예시

1. `models/` 에 DB 테이블 정의
2. `schemas/` 에 요청/응답 모델 정의
3. `repository/` 에 CRUD 로직 작성
4. `services/` 에 조건/업무 로직 구현
5. `routers/` 에 API 연결
6. `migrations.sh` 로 DB 스키마 반영

---

## ✅ 프론트엔드 주요 기술 스택

- React + TypeScript + Vite
- TailwindCSS 기반 디자인 시스템
- React Router 기반 페이지 구조

---

## 📌 기타 유틸

- `run.sh` : FastAPI 앱 실행 (개발 서버)
- `migrations.sh` : alembic 마이그레이션 자동 실행
- `Base.metadata.create_all()` : 로컬에서는 테이블 자동 생성

---

## ✅ 의존성 목록

`requirements.txt` 예시 (백엔드):

```txt
fastapi
uvicorn
sqlalchemy
pydantic
alembic
python-dotenv
pymysql
```

`package.json` 예시 (프론트엔드):

```json
{
  "dependencies": {
    "react": "^18.x",
    "react-dom": "^18.x",
    "react-router-dom": "^6.x"
  },
  "devDependencies": {
    "tailwindcss": "^3.x",
    "vite": "^5.x",
    "typescript": "^5.x",
    "postcss": "^8.x",
    "autoprefixer": "^10.x"
  }
}
```

---

## 📎 기타 참고

- `/docs` : Swagger UI
- `/redoc` : ReDoc 문서화
- Alembic 변경사항 추적: `alembic/history`
- Tailwind 설정: `tailwind.config.js`, `global.css`

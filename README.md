# kotlin spring boot test project



## sequence

- github repository 생성
- archetecture 설계
- tech 결정
- 결정된 tech를 기반으로 gitignore 제작
    - [gitignore.io](https://www.toptal.com/developers/gitignore)


- backend tool 추가
    - api document
        - swagger
        - apidoc

- `docker-compose.yml` 제작
    - container
        - nginx
        - frontend (null)
        - backend (spring boot)
        - mariadb
    - network
    - volumn
    - dependency
    - health-check
    - env

- `Makefile` 제작
    - CI CD를 위한 도구에 익숙하지 않아 단순히 환경변수와 명령어를 통일시키려는 목적

- `init.py`와 `.env.example`을 통한 `.env` 파일 생성
    - 최소한도의 기능과 보안을 가진 최소한도의 정책
    - default값을 채워주는 형태이지 


### mariadb
- docker compose를 통해 실행 및 관리
- init.sql을 통해 데이터베이스, 테이블 생성 및 초기화

### spring boot (kotlin)
- [Spring Initializr](https://start.spring.io/)를 활용한 프로젝트 생성
    - dependencies
        - spring web
        - spring security
            - default로 서버 접근시 로그인 페이지로 링크, user와 실행시 나오는 비밀번호로 로그인 가능
            - 최신 버전에서는 WebSecurityConfigurerAdapter를 상속받지 않음
            - SecurityConfig (이름은 중요하지 않음) class 제작
                - @Configuration
                - @EnableWebSecurity
                - SecurityFilterChain 메서드를 @Bean으로 등록하여 URL별 권한 제어 및 보안 설정
        - spring data jpa
            - dbms와의 연동 필요. H2를 사용하다가 mariadb를 사용하도록 변경 가능
            - 이니셜라이저를 통해 `build.gradle.kts`에 작성되어있음
            - application.yml에서 dbms 정보를 설정
        - mariadb driver
    - build
        - gradle kotlin

- swagger 연동

#### user service 구현
- user table 구현
    - UUID와 auto increase를 모두 사용
    - 어떤 값이 PK가 되어야하는가?
    - 어떤 정보를 가져야하나
        - login, signin page에서 받을 정보
            - 개인정보 정책과 연동되는 부분
            - 비밀번호는 반드시 암호화되어야한다



- login page
    - 진입 : get
    - 로그인 시도 : post
- singup page
    - 진입 : get
    - 로그인 시도 : post
- profile page
    - profile update page

--- 

# 기준점

## status

### 42서울 수료

- inception, 트센 기반의 웹 아키텍쳐 이해도가 있음

- flutter로 모바일 앱 제작 실습은 해봄. (api 연동 로그인, 정보 받아오기 정도)

### spring framework experience

- java 기반의 spring 경험 있음
    - CURD 가능한 mariadb와 연동된 jpa 사이트 제작 경험
- kotlim 기반의 spring boot api 서버 경험 있음
    - 단, 실무적으로 개조되어 스웨거도 있는 세팅 위에서 CRUD api를 추가해 본 경험 수준임
        - .env 직접 세팅
        - swagger를 통해 crud api test해봄

## 실습 기준

- 도메인 영역을 위해 필요한 동작에 대하여 어떤 방식으로 구현할 수 있을지 고민하며 벡엔드 서버 구조를 학습한다

- 어떻게 제작할 수 있는지 모르는 상태이기 때문에 먼저 웹 프로젝트 기반으로 백엔드 서버를 만들어보며 이 환경에서 가능한 동작이 무엇인지 배워야한다

- 문서단위 서비스를 기반으로 하기 때문에 nosql의 도입이 필요하지만 user service는 rdbms 기반으로 해야하니 일단 동작을 확인하는 단계인 지금 시점의 실습에서는 mariadb만 사용한다

- 대부분의 서비스는 지금 단계에서 제작하려고 집중할 수 없다. 당장의 목표는 내가 기본적인 벡엔드 서버 구성을 할 수 있는 것을 증명할 저수준의 포폴이다.

- TDD 기반으로 의사코드 - 테스트코드 - 개발 순서

---

## Domain

- 옵시디언과 유사한 문서 관리 프로그램
    - 기존 옵시디언의 그래프에 가중치가 없어 완전히 만족스럽지 못했음
    - local저장소를 기반으로 작동하지만 결국 모든 플랫폼에서 개별적으로 관리해야함
    - 웹을 통해 접근 가능한 로컬 기반으로 저장되는 지식 저장소를 만들고싶다
    - 내가 원하는 문서만 외부에서 접근 가능하도록 하고싶다
    - 각 문서에 대한 여러가지 정보가 문서를 외부에 공개하는 시점에서 내가 원하지 않는 정보를 숨길 수 있게 하고싶다

#### 개요
- 제텔카스텐 기법을 적용할 수 있어야한다
- 각 문서는 view 모드와 write모드를 가진다
- 문서는 제목, 내용, 메타데이터를 가진다
    - 제목과 내용은 마크다운 형식을 따른다
    - 메타데이터는 view 모드에서 표기되지 않아야한다
    - 내용과 메타데이터는 명백히 구분지어진 UIUX를 가져야한다
    - markdown file로 출력할 수 있어야 한다
        - 메타데이터를 포함할지 여부를 선택할 수 있어야 한다
- 각 문서의 메타데이터에 작성자를 기록할 수 있어야 한다
    - 유저 서비스가 존재해야한다
    - 권한이 어떻게 될지 모르겠지만 최소 해당 문서의 주인만 열람 가능 기능은 있어야한다

#### 주의
- 해당 서비스가 obsidian vault의 정보에 접근해 바로 사용하는지, 읽고 정리하여 db에 저장 후 동작하며 웹에서의 기록을 저장할 때 vault에 문서화 할지, 출력을 요청받지 않는 상황이라면 db에 정보를 저장만 하고 있을지 결정된 부분 없음. 세 가지 동작 이외의 경우도 있을 수 있음




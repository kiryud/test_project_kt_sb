# kotlin spring boot test project

## sequence

- github repository 생성
- architecture 설계
- tech 결정
- 결정된 tech를 기반으로 gitignore 제작
    - [gitignore.io](https://www.toptal.com/developers/gitignore)
- convention.md 정리

- backend tool 추가
    - 활용 가능한 api document service
        - swagger
        - apidoc

- `docker-compose.yml` 제작
    - container
        - nginx
            - config (*.conf)
        - frontend (null)
        - backend (spring boot)
        - dbms
            - mariadb
    - network
    - volume
    - dependency
    - health-check
    - env

- `Makefile` 제작
    - CI CD를 위한 도구에 익숙하지 않아 단순히 환경변수와 명령어를 통일시키려는 목적

- `init.py`와 `.env.example`을 통한 `.env` 파일 생성
    - 최소한도의 기능과 보안을 가진 최소한도의 정책
    - default값을 채워주는 형태이지 난수 생성은 없다

- deployment
    - 미정

#### 인증서 관리
- ca_certificate
    - 내 프로젝트와 별개로 시스템에 설치된 root ca public key 목록
- letsencrypt
    - 90일 무료 인증서 발급 기관
- certbot
    - 만료 30일 전 갱신 봇

### DBMS

#### H2
- 메모리 상의 가상 dbms

#### redis
- in memory, nosql db

#### postgres
- 기본적인 사용은 RDBMS의 공통적인 사용법과 같다
- 부가 기능이 굉장히 많은데 아직 학습하진 못했다

#### supabase
- postgres 기반의 Backend as a Service


#### mariadb

> docker 이미지 있으니 걍 쓰는중

- docker compose를 통해 실행 및 관리
    - 환경변수 없이 임시 값 넣어둔 상태
    - 다른 환경변수까지 정리된 후 .env를 사용하도록 수정 예정
- init.sql을 통해 데이터베이스, 테이블 생성 및 초기화

### spring boot (kotlin)

> 버전은 설계 완성 후 프로젝트 시작시 제대로 고정할 예정
> 당장은 특정 버전을 사용해야하는 이유에 대한 고민이 존재하지 않는 상태이다

- [Spring Initializr](https://start.spring.io/)를 활용한 프로젝트 생성
    - dependencies
        - spring web
            - servlet 기반
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
        - spring boot 4.x.x 이상의 release
        - JAVA 21 이상
        - gradle kotlin

- `swagger` 연동

```build.gradle.kts
dependencies{
	// Swagger (OpenAPI) 버전은 프로젝트의 환경에 맞추면 된다
	implementation("org.springdoc:springdoc-openapi-starter-webmvc-ui:2.8.0")
}
```

- 테스트
    - `WebMvcTest`
        - 기본적으로 포함된 `spring-boot-starter-webmvc-test`를 통해 테스트 가능

- 레이어드 아키텍처
    - controller - service - repository
    - 이 경우 spring boot라서 adapter를 작성할 필요는 없다

- 헥사고날 아키텍처
    - port와 adapter를 기반으로 결합도를 낮춰 더 유연한 개발이 가능해짐

```md
controller
service
repository
```

- controller의 역할과 책임
    - request body
    - query parameter
    - path variable
    - response body

- service의 역할과 책임
    - user의 권한에 따라 요청된 비즈니스 로직을 실행


- repository의 역할과 책임
    - JPA(ORM)을 통해 어떻게 DBMS와 소통할지 선언
    - ORM에서 최종적으로 어떤 SQL을 만드는지 확인해 N+1같은 널리 알려진 문제는 미리 잡아야 한다

```md
dto
entity
```

- dto의 역할과 책임
    - data 전송 객체로서 필요한 범위의 data를 저장 가능해야한다
    - 불필요한 정보는 빈 공간으로 둘 수 있어야한다

- request dto의 역할과 책임
    - 요청을 받을 때 오는 정보를 관리할 수 있어야한다
    - 정보를 관리하면서 생기는 다른 정보도 관리 가능해야한다

- response dto의 역할과 책임
    - 반환을 위한 정보를 다룰 수 있어야한다
    - 비즈니스 로직의 동작에 따른 data의 반환이 가능해야한다
    - api의 반환값을 더 쉽게 만들 수 있도록 잘 설계되어있어야한다

- entity의 역할과 책임
    - 일단 지금 수준에선 db의 table과 일치해야한다
    - ORM에서 가져오는게 전용 dto로 갈 예정이라 사실상 Create나 Update를 요청할 때 사용하게 될 듯 하다

#### service 구현
- service에서 제공하는 기능 정리
- table(entity) 정의 및 구현
- dto, repository 정의 및 구현
- controller, service 정의 및 구현

#### user service 구현
- user service의 기능 정리
- user table 구현
    - [UUID](#uuid)란?
    - UUID와 auto increment를 모두 사용해야하나?
        - 내부적으로는 indexing하기 좋은 auto increment인 정수를 사용하는것이 좋고 외부에 공개하는 유저 식별자는 UUID로 하는것이 좋다
            - UUID를 저장할 땐 문자열이 아닌 BINARY(16)을 사용해야한다
        - RESTful api를 지향한다면 UUID를 resource-id로 사용하게 된다
            - UUIDv7는 첫 영역이 timestamp라서 등록 순서대로 정렬된다
                - B+Tree기반의 index에 굉장히 좋다
                - 해당 UUID의 생성 일시가 그대로 노출된다
                - UUID만으로 indexing이 되어 auto increment가 불필요해 보이지만 이 때에도 sequence의 역할을 해줄 수 있다
                    - timestamp는 발급 당시 기기의 설정에 종속되어있다
            - UUIDv4는 임의의 난수로서 예측이 불가능하다 (굉장히 낮은 확률로 겹칠 수는 있다)
                - 이 때 내부 index로 auto increment인 정수를 사용하면 좋다 
    - 어떤 값이 PK가 되어야하는가
        - 어차피 키를 하나만 쓸것도 아니라 제 3의 값도 테이블 구성에 따라 키가 될 수 있는거라 유저서비스를 위한 정보가 어떻게 구성될지가 중요할 듯 하다
        - 중복 안되는 정보가 한두개가 아니다
    - 어떤 정보를 가져야하나
        - login(signin), signup page에서 받을 정보
            - 개인정보 정책과 연동되는 부분
            - 비밀번호는 반드시 해시로 저장되어야 한다 (`BCryptPasswordEncoder` 사용하도록 제어해야함)

#### auth service 구현
- [`Cookie`](#cookie)란?
    - browser에서 refresh(F5)로는 사라지지 않는다
        - 필요시 `HttpOnly ; SameSite=<Strict|Lax> ; __Host-[name]=[host] ; Secure ; Path=/` attributes와 함께 사용하여 보안을 강화해 사용하면 새로고침시에도 access token을 유지시킬 수 있다
- [`JWT`](#json-web-token) 기반의 인증 시스템 구현
    - 로그인 성공시 access token과 refresh token 발급
        - 일단 access token은 웹의 스토리지가 아닌 램에서 다룬다
            - 새로고침시 로그인이 유지되어야할 이유가 아직 없다
        - refresh token을 서버에서도 관리하는 것이 권장된다
            - 서버에서 통제권을 가질 필요가 없는 서비스는 일반적으로 존재하지 않는다고 봐도 과언이 아니다
        - DPoP, RTR을 통해 보안성을 강화하면 클라이언트를 신뢰하기 어려운 환경에서도 refresh token을 안전하게 제공할 수 있다
            - DPoP : 로그인, 발급시 `Bearer`대신 `DPoP`를 사용하자고 요청을 보내면 클라이언트가 비대칭키 쌍을 만들어 공개키가 포함된 `DPoP Proof JWT`를 비밀키로 서명해서 보내고 인증 서버에서 access token의 cnf.jkt 클레임에 해당 공개키의 지문을 바인딩
                - 정말 도입할 생각이 있으면 이것보다 더 자세하게 조사해야할 것 같다
                1. Client : POST
                2. Server : 400 or 401 `WWW-Authenticate: DPoP`
                3. Client : POST JWT(alg typ jwk(kty crv x y) . jti htm htu iat :ath :nonce)
                4. Server : 200 OK JWT(access token)
            - RTR : refresh token 사용시 재발급하는 방식
                - 단, 멱등성 키를 통해 검증한 동일한 요청이 일정 시간 안에 오는 경우 재발급이 아닌 재전송을 해줘야한다
    - spring security의 http security를 통해 토큰 검증 후 인가 정보 관리
    - 해당 토큰은 header fields 중 Authorization을 통해 주고받게 된다
        - 기본적으로는 `Authorization: Bearer [JWT]`의 형태로 `Bearer `뒤에 JWT를 이어붙인다
        - DPoP을 사용한다면 `Authorization: DPoP [JWT]`의 형태로 `DPoP `뒤에 JWT를 이어붙이고 `DPoP: [비밀키로 서명된 JWT]`를 헤더에 추가해야한다

- 만약 서버가 확장된다면 user service에서 분리되어 api를 통해 접근 가능한 하나의 서비스로 작동해야만 함
    - user service 이외의 서비스가 존재한다면 이미 인증만을 담당하고 각 서비스에서 인가할 수 있게 비대칭 키 형태로 서명하여 공개키를 각 서비스에서 가지고 있을 것이다
    - 공개키를 인증 서버에서 관리하고 `GET /.well-known/openid-configuration/[PATH]`형태로 엔드포인트를 열어 다른 서버가 접속할 수 있게 하고 이 때 키가 있는 uri(`jwks_uri`)가 담긴 JSON을 반환한다
        - [RFC 8414](https://www.rfc-editor.org/rfc/rfc8414#section-5)
        1. Resource server : GET /.well-known/openid-configuration/[PATH]
        2. Auth server : {"issuer": [DOMAIN], "jwks_uri": [DOMAIN]/jwks.json}
        3. Resource server : GET /jwks.json


---

## frontend knowledge? experience?

### web

#### vanilla javascript

- (html/css/js)
    - SPA를 위한 router 구조 이해

#### library & framework

- vite
- typescript
- react
- nextjs

### app

- android native
    - kotlin

- ios
    - swift

- cross platform
    - flutter


--- 

# 기준점

## status

### 42서울 수료

- inception, 트센 기반의 웹 아키텍처 이해도가 있음

- 42에서 peer-evaluation 준비하듯 내가 할 수 있는 선에서 최대한 상세한 설명을 할 수 있는 기반을 만들어버리는 중...
    - well known standard만 사용할거면 신입을 왜 씀? 검증할 수 있는 사람이 필요한거지

### ??

- flutter로 모바일 앱 제작 실습은 해봄. (api 연동 로그인, 정보 받아오기 정도)

### spring framework experience

- java 기반의 spring 경험 있음
    - CRUD 가능한 mariadb와 연동된 jsp 사이트 제작 경험
    - jdbc, jpa(ORM) 의 단순 사용 경험 있음
- kotlin 기반의 spring boot api 서버 경험 있음
    - 단, 실무적으로 개조되어 스웨거도 있는 세팅 위에서 CRUD api를 추가해 본 경험 수준임
        - .env 직접 세팅
        - swagger를 통해 crud api test해봄

## 실습 기준

- 도메인 영역을 위해 필요한 동작에 대하여 어떤 방식으로 구현할 수 있을지 고민하며 백엔드 서버 구조를 학습한다

- 어떻게 제작할 수 있는지 모르는 상태이기 때문에 먼저 웹 프로젝트 기반으로 백엔드 서버를 만들어보며 이 환경에서 가능한 동작이 무엇인지 배워야한다

- 문서단위 서비스를 기반으로 하기 때문에 nosql의 도입이 필요하지만 user service는 rdbms 기반으로 해야하니 일단 동작을 확인하는 단계인 지금 시점의 실습에서는 mariadb만 사용한다

- 대부분의 서비스는 지금 단계에서 제작하려고 집중할 수 없다. 당장의 목표는 내가 기본적인 백엔드 서버 구성을 할 수 있는 것을 증명할 저수준의 포폴이다.

- TDD 기반으로 의사코드 - 테스트코드 - 개발 순서

- 과정 검증을 위한 지식 정리 이후 컨벤션 및 제약 정의 후 llm을 통한 개발 예정
    - 이 때 최대한 적은 횟수의 지시를 하되 내가 적은 문서의 설계가 잘 전달되는지 (내가 맥락을 부족하게 적은게 없는지) 검증할 예정
- 하네스 엔지니어링 적용을 위한 추가 학습 예정
    - CICD 자동화가 된 상태에서 지속적으로 업데이트 - 즉시배포가 가능한지 확인할 예정
        - 지인분의 llm기반 모바일 대상 웹 게임이 미니게임을 잔뜩 추가중인데 변경점, 추가시 자동으로 업데이트 알림이 나오고 새로고침 유도하는거 보고 관련된 내용을 나도 사용 가능하게 재가공 해볼 예정

---

## Domain

- 옵시디언과 유사한 문서 관리 프로그램
    - 기존 옵시디언의 그래프에 가중치가 없어 완전히 만족스럽지 못했음
    - local 저장소를 기반으로 작동하지만 결국 모든 플랫폼에서 개별적으로 관리해야함
    - 웹을 통해 접근 가능한 로컬 기반으로 저장되는 지식 저장소를 만들고 싶다
    - 내가 원하는 문서만 외부에서 접근 가능하도록 하고 싶다
    - 각 문서에 대한 여러가지 정보가 문서를 외부에 공개하는 시점에서 내가 원하지 않는 정보를 숨길 수 있게 하고 싶다
    - 각 문서의 내용을 합쳐 배치한 새 문서를 만들거나 구성할 수 있어야한다
        - 이 때 각 문서와 통합 문서의 동기화 여부는 아직 결정되지 않았다 (모르겠다)

#### 개요
- markdown 기반의 문서를 해석할 수 있어야한다
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

